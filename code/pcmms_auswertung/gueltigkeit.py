"""Gültigkeit der Läufe und Abbruchregeln offline (Präreg §9.1, §9.2, §8.8, A9.2 „Reihenfolge der Schwellen“, A9.8).

Geprüft wird an Laufzusammenfassungen, also nach der Aufnahme; das ist keine Echtzeit-Sicherheitsfunktion (AP-10).
Je Lauf und Regel steht True (verletzt), False (eingehalten) oder None (nicht anwendbar oder nicht prüfbar, mit
Grund). Schwellen erhalten einen Rundungsboden (10⁻⁵° bzw. 10⁻¹²·⟨N⟩), damit rauschfreie Prüffälle mit Schwelle null
nicht an Rundungsfehlern scheitern (technisch). Ein Lauf ist gültig, wenn keine geprüfte Regel verletzt ist; nicht prüfbare Regeln werden getrennt gezählt
und berichtet, nie stillschweigend als eingehalten gewertet.

G1   |Δ⟨N⟩| > ε_ctrl, Δ⟨N⟩ = ⟨N⟩ − N_s,int (lineare Interpolation zwischen den einschließenden gültigen
     Referenzläufen, A1); Referenzläufe: Nullpunktalarm 3·√(4/3)·σ̂_ref (Summe) bzw. σ̂_ref,c (Zelle) gegen den
     vorangehenden gültigen Referenzlauf.
G2   Kombinationsläufe: |φ̄ⱼ^P − φⱼ,soll^P| > δφ_tol (j = 2, 3) mit φ̄ⱼ^P = −arg ρⱼ₁ + Δδⱼ, σⱼ > σ_tol; alle Läufe mit
     bewegten Modulen: fehlende oder überzählige Indeximpulse. Einstellung 2: offen (Regel g.einstellung2).
G3   |f̄ − f| > δf_tol (δf_tol aus Teil B; ohne Angabe nicht prüfbar).
G4   |X(erstes Fünftel) − X(letztes Fünftel)| > 3·σ_Δ,X, X = ⟨N⟩ und F_min − ⟨N⟩ (k ≤ k_max), σ_Δ = 1,4826·MAD
     je Laufart über die Phase-0-Läufe (Pilotläufe gepoolt, Einzelmodulläufe je Modul, Referenzläufe nur ⟨N⟩).
G5   Übersteuerung einer Zelle; G6 Einzelzell-Liftoff min N_c < F_LO,c (ganzer Lauf); G7 Zelltemperatur außerhalb
     T_P0 ± ΔT (Form offen, Regel g7.form; ohne T_P0, ΔT nicht prüfbar); G8 Störung; G9 Parkposition;
     G10 unvollständige Aufzeichnung oder fehlender Kanal.
S1–S4 (§9.2): S2 Einzelzell-Liftoff in einem Lauf mit bewegten Modulen (ohne G5/G8/G10-ungültige), zweites S2
     beendet Phase 1; S4 G2 in zwei aufeinanderfolgenden Läufen; S3 Drift der Einzelmodulreferenz in einem
     Kontrolllauf; S1 reproduzierter H0-Verstoß. Im statischen Laufplan gibt es keine Wiederholungsläufe: Für S1 und S3
     werden Auslösekandidaten (erste Überschreitung) berichtet, die Reproduktion bleibt „nicht prüfbar“. Im
     zustandsbehafteten Ablauf (ablauf.py; Köpfe mit „versuch“) entscheidet der Ablauf über S1–S4 mit denselben
     Funktionen (interpolation, g1_verletzt, alarm_kanaele); die Offline-Prüfung muss seine Entscheidungen bestätigen.
"""
from dataclasses import dataclass, field

import numpy as np
from scipy import stats

from . import konventionen as kv

REGELN_G = ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10')
RUNDUNG_GRAD = 1e-5                     # Rundungsboden der Jittertoleranz: σ = √(−2 ln R) rauscht bei R ≈ 1 um √(2ε) ≈ 10⁻⁶°
RUNDUNG_REL = 1e-12                     # Rundungsboden relativ zu ⟨N⟩ für G1, G4 und den Nullpunktalarm


@dataclass
class Schwellen:
    """Parameter der Gültigkeitsregeln (Phase 0: aus der Pilotanalyse; Phase 1: aus Teil B)."""
    f_soll: float
    kmax: int
    delta_phi_tol_grad: float = 0.5
    sigma_tol_grad: dict = None               # {2: …, 3: …}
    sigma_delta: dict = None                  # {Gruppe: {'N': …, 'F': …}}
    F_LO_zellen: object = None                # (3) [N]
    delta_delta_grad: object = None           # (3) Δδⱼ aus P0.5
    delta_f_tol: float = None
    eps_ctrl: float = None
    sigma_ref: float = None                   # σ̂_ref (Summe)
    sigma_ref_zellen: object = None           # σ̂_ref,c
    alarm_faktor: float = 3.0 * (4.0 / 3.0) ** 0.5
    g4_faktor: float = 3.0
    T_P0: object = None
    Delta_T: float = None
    einstellung2_g2_g4: bool = False          # Regel g.einstellung2 offen: G2–G4 für Einstellung 2 nicht prüfbar
    herkunft: dict = field(default_factory=dict)


def g4_gruppe(kopf):
    if kopf['laufart'] == 'R':
        return 'R'
    if kopf['laufart'] == 'L':
        return f'L{kopf["modul"]}' + ("′" if kopf['einstellung'] == 2 else '')
    return 'K' if kopf['einstellung'] == 1 else "K′"


def fuenftel_differenzen(tab, kmax):
    """D_N = ⟨N⟩(letztes) − ⟨N⟩(erstes Fünftel), D_F für F_min − ⟨N⟩ der bandbegrenzten Fünftelkurven."""
    d = tab.daten
    DN = d['fuenftel_N_mittel'][:, 1] - d['fuenftel_N_mittel'][:, 0]
    Fk = d['fuenftel_Nk'][:, :, :kmax]
    DF = kv.fmin_rel(Fk[:, 1]) - kv.fmin_rel(Fk[:, 0])
    return DN, DF


def sigma_delta(tab, kmax):
    """σ_Δ,X = 1,4826·MAD je Laufart über die übergebenen (Phase-0-)Läufe."""
    DN, DF = fuenftel_differenzen(tab, kmax)
    gr = np.array([g4_gruppe(k) for k in tab.koepfe])
    out = {}
    for g in sorted(set(gr)):
        m = gr == g
        def mad(x):
            x = x[np.isfinite(x)]
            return float(1.4826 * np.median(np.abs(x - np.median(x)))) if x.size else float('nan')
        out[g] = dict(N=mad(DN[m]), F=None if g == 'R' else mad(DF[m]), n=int(m.sum()))
    return out


def interpolation(N, t, Na, ta, Nb, tb):
    """Abweichung N − N_s,int von der linearen Interpolation zwischen den Referenzläufen a und b (A1) zur Laufmitte t,
    für die Summe oder die Zellen; Rückgabe (Abweichung, β). Dieselbe Rechnung offline und im Ablauf (ablauf.py)."""
    be = (t - ta) / (tb - ta)
    return N - ((1 - be) * Na + be * Nb), be


def g1_verletzt(dN, N, eps_ctrl):
    """G1: |Δ⟨N⟩| > ε_ctrl (mit Rundungsboden)."""
    return bool(abs(dN) > eps_ctrl + RUNDUNG_REL * abs(N))


def alarm_kanaele(sw, N, Nz, N_vor, Nz_vor):
    """Kanäle eines Nullpunktalarms (§8.8) eines Referenzlaufs (⟨N⟩, ⟨N_c⟩) gegen den vorangehenden gültigen."""
    dS = abs(N - N_vor)
    dZ = np.abs(Nz - Nz_vor)
    zs = (np.asarray(sw.sigma_ref_zellen) if sw.sigma_ref_zellen is not None else np.full(3, np.inf))
    bS = RUNDUNG_REL * abs(N)
    bZ = RUNDUNG_REL * np.abs(Nz)
    return (['Summe'] if dS > sw.alarm_faktor * sw.sigma_ref + bS else []) + \
        [f'Zelle {c + 1}' for c in range(3) if dZ[c] > sw.alarm_faktor * zs[c] + bZ[c]]


def rolle(kopf):
    """Rolle eines Laufs im zustandsbehafteten Ablauf (Kopf „versuch“), sonst None (statischer Laufplan)."""
    v = kopf.get('versuch')
    return v.get('rolle') if isinstance(v, dict) else None


def klammer_indizes(tab, gueltig_ref=None):
    """Je Lauf mit bewegten Modulen die Indizes (a, b) der einschließenden gültigen Referenzläufe derselben Phase
    (nach Position); −1, wenn ein Nachbar fehlt, und für Referenzläufe."""
    n = len(tab)
    pos = tab.spalte('position', int)
    art = tab.spalte('laufart', object)
    ref = np.flatnonzero((art == 'R') & (np.ones(n, bool) if gueltig_ref is None else gueltig_ref))
    ref = ref[np.argsort(pos[ref])]
    ka, kb = np.full(n, -1), np.full(n, -1)
    for i in range(n):
        if art[i] == 'R':
            continue
        vor = ref[pos[ref] < pos[i]]
        nach = ref[pos[ref] > pos[i]]
        if not vor.size or not nach.size:
            continue
        a, b = vor[-1], nach[0]
        if tab.koepfe[a]['phase'] != tab.koepfe[i]['phase'] or tab.koepfe[b]['phase'] != tab.koepfe[i]['phase']:
            continue
        ka[i], kb[i] = a, b
    return ka, kb


def _interpolieren(tab, ka, kb):
    n = len(tab)
    t = 0.5 * (tab.spalte('t_start', float) + tab.spalte('t_ende', float))
    Nm, Nz = tab.daten['N_mittel'], tab.daten['N_mittel_zellen']
    dN, dZ, beta = np.full(n, np.nan), np.full((n, 3), np.nan), np.full(n, np.nan)
    for i in np.flatnonzero(ka >= 0):
        a, b = ka[i], kb[i]
        dN[i], beta[i] = interpolation(Nm[i], t[i], Nm[a], t[a], Nm[b], t[b])
        dZ[i] = interpolation(Nz[i], t[i], Nz[a], t[a], Nz[b], t[b])[0]
    return dN, dZ, beta


def referenz_interpolation(tab, gueltig_ref=None):
    """Δ⟨N⟩ (Summe und Zellen) und β jedes Laufs gegen die einschließenden gültigen Referenzläufe (nach Position).
    Rückgabe (dN (n), dN_zellen (n, 3), beta (n)); nan, wenn ein Nachbar fehlt."""
    return _interpolieren(tab, *klammer_indizes(tab, gueltig_ref))


def x_strich_klammer(koepfe, i, a, b):
    """Offline-Gegenprobe zur Klammer von X′ (Index i) im zustandsbehafteten Ablauf, nur aus den Köpfen: Sind die
    einschließenden gültigen Referenzläufe a, b das R₂ und R₃ desselben G1-Falls? Eine nicht reproduzierte
    Alarmwiederholung wird auf den alarmierten Lauf zurückgeführt, den sie ersetzt (§8.8)."""
    if a < 0 or b < 0:
        return False
    ids = {k['versuch']['id']: j for j, k in enumerate(koepfe) if isinstance(k.get('versuch'), dict)}

    def wurzel(j):
        v = koepfe[j].get('versuch') or {}
        while v.get('rolle') == 'alarmwiederholung' and v.get('bezug_versuch') in ids:
            v = koepfe[ids[v['bezug_versuch']]]['versuch']
        return v
    x = (koepfe[i].get('versuch') or {}).get('bezug_versuch')
    ra, rb = wurzel(a), wurzel(b)
    return bool(x) and ra.get('rolle') == 'R2' and ra.get('bezug_versuch') == x and rb.get('rolle') == 'R3' \
        and rb.get('bezug_versuch') == x


def sigma_ref(tab, phase=0):
    """σ̂_ref und σ̂_ref,c: Leave-one-out der Referenzläufe gegen die Interpolation ihrer Nachbarn (A1)."""
    art = tab.spalte('laufart', object)
    ph = tab.spalte('phase', int)
    pos = tab.spalte('position', int)
    t = 0.5 * (tab.spalte('t_start', float) + tab.spalte('t_ende', float))
    r = np.flatnonzero((art == 'R') & (ph == phase))
    r = r[np.argsort(pos[r])]
    if r.size < 3:
        return dict(sigma_ref=None, sigma_ref_zellen=None, n=int(r.size), werte=0)
    Nm, Nz = tab.daten['N_mittel'], tab.daten['N_mittel_zellen']
    d, dz = [], []
    for a, i, b in zip(r[:-2], r[1:-1], r[2:]):
        be = (t[i] - t[a]) / (t[b] - t[a])
        d.append(Nm[i] - ((1 - be) * Nm[a] + be * Nm[b]))
        dz.append(Nz[i] - ((1 - be) * Nz[a] + be * Nz[b]))
    d, dz = np.array(d), np.array(dz)
    return dict(sigma_ref=float(d.std(ddof=1)), sigma_ref_zellen=dz.std(0, ddof=1).tolist(), n=int(r.size),
                werte=int(d.size), loo=d)


def pruefe(tab, sw, regeln=('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G1'), gueltig_ref=None):
    """Prüft die Läufe; Rückgabe dict mit je Regel (n,) object-Arrays (True/False/None), Gründen und Gültigkeit."""
    n = len(tab)
    d = tab.daten
    K = tab.koepfe
    erg = {g: np.full(n, None, object) for g in REGELN_G}
    nicht = {g: [] for g in REGELN_G}
    art = tab.spalte('laufart', object)
    e2 = tab.spalte('einstellung', int) == 2
    bew = art != 'R'
    DN, DF = fuenftel_differenzen(tab, sw.kmax)
    for i in range(n):
        k = K[i]
        e2g = e2[i] and not sw.einstellung2_g2_g4
        # G2
        if 'G2' in regeln and bew[i]:
            if e2g:
                nicht['G2'].append((i, 'Einstellung 2: G2 nicht gefasst (Regel g.einstellung2 offen)'))
            else:
                v = bool(d['index_fehler'][i].sum() > 0)
                if art[i] == 'K' and not v:
                    if sw.delta_delta_grad is None or sw.sigma_tol_grad is None:
                        nicht['G2'].append((i, 'Δδⱼ oder σ_tol fehlt'))
                        v = None
                    else:
                        soll = np.asarray(k['konfiguration']['phi_soll_grad'], float)
                        rho = d['zeiger'][i, :, 0] / k['n_zyklen']
                        phiP = -np.degrees(np.angle(rho)) + np.asarray(sw.delta_delta_grad, float)
                        ab = np.abs(kv.wickel_grad(phiP[1:] - soll[1:]))
                        sig = d['sigma_grad'][i, 1:]
                        tol = np.maximum(np.array([sw.sigma_tol_grad[2], sw.sigma_tol_grad[3]]), RUNDUNG_GRAD)
                        v = bool((ab > sw.delta_phi_tol_grad).any() or (sig > tol).any())
                erg['G2'][i] = v
        # G3
        if 'G3' in regeln and art[i] != 'R':
            if e2g:
                nicht['G3'].append((i, 'Einstellung 2: G3 nicht gefasst'))
            elif sw.delta_f_tol is None:
                nicht['G3'].append((i, 'δf_tol fehlt (Teil B)'))
            else:
                erg['G3'][i] = bool(abs(k['f_mittel'] - sw.f_soll) > sw.delta_f_tol)
        # G4
        if 'G4' in regeln:
            g = g4_gruppe(k)
            if e2g:
                nicht['G4'].append((i, 'Einstellung 2: G4 nicht gefasst'))
            elif sw.sigma_delta is None or g not in sw.sigma_delta:
                nicht['G4'].append((i, f'σ_Δ der Laufart {g} fehlt'))
            else:
                s = sw.sigma_delta[g]
                boden = RUNDUNG_REL * abs(d['N_mittel'][i])
                v = bool(abs(DN[i]) > sw.g4_faktor * s['N'] + boden)
                if art[i] != 'R' and s.get('F') is not None:
                    v = v or bool(abs(DF[i]) > sw.g4_faktor * s['F'] + boden)
                erg['G4'][i] = v
        # G5, G6, G8, G9, G10
        if 'G5' in regeln:
            erg['G5'][i] = bool(d['uebersteuert_zellen'][i].any())
        if 'G6' in regeln:
            if sw.F_LO_zellen is None:
                nicht['G6'].append((i, 'F_LO,c fehlt (P0.7)'))
            else:
                erg['G6'][i] = bool((d['min_roh_zellen'][i] < np.asarray(sw.F_LO_zellen)).any())
        if 'G7' in regeln:
            if sw.T_P0 is None or sw.Delta_T is None:
                nicht['G7'].append((i, 'T_P0 oder ΔT fehlt (Form des Fensters offen, Regel g7.form)'))
            else:
                T0 = np.asarray(sw.T_P0, float)
                erg['G7'][i] = bool((d['temperatur_min_zellen'][i] < T0 - sw.Delta_T).any()
                                    or (d['temperatur_max_zellen'][i] > T0 + sw.Delta_T).any())
        if 'G8' in regeln:
            erg['G8'][i] = bool(k['stoerung'])
        if 'G9' in regeln:
            erg['G9'][i] = None if k['park_ok'] is None else (not k['park_ok'])
        if 'G10' in regeln:
            erg['G10'][i] = bool((not k['aufzeichnung_ok']) or len(k['fehlende_kanaele']) > 0)
    # G1 bzw. Nullpunktalarm nach G2–G10. Stützstellen der Interpolation: Referenzläufe ohne Verstoß gegen G2–G10;
    # im zustandsbehafteten Ablauf (Köpfe mit „versuch“) zusätzlich ohne Nullpunktalarm, weil dort die sofortige
    # Wiederholung den alarmierten Lauf ersetzt (§8.8); der statische Laufplan behält die bisherige Rechnung.
    ungueltig_vor_g1 = np.array([any(erg[g][i] is True for g in REGELN_G if g != 'G1') for i in range(n)])
    if 'G1' in regeln:
        alarm = nullpunktalarm(tab, sw, ~ungueltig_vor_g1)
        gref = (art == 'R') & ~ungueltig_vor_g1 if gueltig_ref is None else gueltig_ref
        if gueltig_ref is None and any('versuch' in k for k in K):
            gref = gref & ~np.isin(np.arange(n), [i for i, a in alarm.items() if a['alarm']])
        klammer = klammer_indizes(tab, gref)
        dN, dZ, beta = _interpolieren(tab, *klammer)
        for i in range(n):
            if art[i] == 'R':
                continue
            if sw.eps_ctrl is None:
                nicht['G1'].append((i, 'ε_ctrl fehlt'))
            elif not np.isfinite(dN[i]):
                nicht['G1'].append((i, 'kein einschließendes Paar gültiger Referenzläufe'))
            else:
                erg['G1'][i] = g1_verletzt(dN[i], d['N_mittel'][i], sw.eps_ctrl)
        for i, a in alarm.items():
            erg['G1'][i] = a['alarm']
    else:
        dN = dZ = beta = klammer = None
    gueltig = np.array([not any(erg[g][i] is True for g in REGELN_G) for i in range(n)])
    gruende = [[g for g in REGELN_G if erg[g][i] is True] for i in range(n)]
    return dict(regeln=erg, gueltig=gueltig, gruende=gruende, nicht_pruefbar={g: v for g, v in nicht.items() if v},
                delta_N=dN, delta_N_zellen=dZ, beta=beta, g1_klammer=klammer)


def nullpunktalarm(tab, sw, kandidat):
    """Nullpunktalarm je Referenzlauf gegen den vorangehenden gültigen Referenzlauf derselben Phase. Aufwärm-
    Referenzläufe des zustandsbehafteten Ablaufs (Rolle „aufwaermen“) lösen keinen Alarm aus und sind Bezug (A9.12)."""
    out = {}
    if sw.sigma_ref is None:
        return out
    art = tab.spalte('laufart', object)
    pos = tab.spalte('position', int)
    r = np.flatnonzero(art == 'R')
    r = r[np.argsort(pos[r])]
    vor = None
    for i in r:
        if not kandidat[i]:
            continue
        if (vor is not None and tab.koepfe[vor]['phase'] == tab.koepfe[i]['phase']
                and rolle(tab.koepfe[i]) != 'aufwaermen'):
            kanal = alarm_kanaele(sw, tab.daten['N_mittel'][i], tab.daten['N_mittel_zellen'][i],
                                  tab.daten['N_mittel'][vor], tab.daten['N_mittel_zellen'][vor])
            out[i] = dict(alarm=bool(kanal), kanaele=kanal)
            if kanal:
                continue                                                # alarmierter Lauf ist nicht Bezug
        vor = i
    return out


def abbruchregeln(tab, pr, phase=1):
    """S2 und S4 aus den Gültigkeitsergebnissen; Kandidaten für S1 (reproduzierbar erst mit Wiederholung). Im
    zustandsbehafteten Ablauf (Köpfe mit „versuch“) gelten S2 und S4 nicht für L₁′–L₃′ (offen, §12, wie im Ablauf), und
    S1/S3 stehen aus dem Ablaufprotokoll in den Köpfen (Halt mit Regel)."""
    d = tab.daten
    art = tab.spalte('laufart', object)
    ph = tab.spalte('phase', int)
    pos = tab.spalte('position', int)
    ordn = np.argsort(pos)
    reg = pr['regeln']
    zustand = any('versuch' in k for k in tab.koepfe)
    strich = np.array([zustand and k['laufart'] == 'L' and k['einstellung'] == 2 for k in tab.koepfe])
    s2 = [int(i) for i in ordn if ph[i] == phase and art[i] != 'R' and reg['G6'][i] is True
          and not any(reg[g][i] is True for g in ('G5', 'G8', 'G10')) and not strich[i]]
    s4 = []
    vor = None
    for i in ordn:
        if ph[i] != phase or art[i] == 'R':
            continue
        if reg['G2'][i] is True and vor is not None and reg['G2'][vor] is True and not strich[i]:
            s4.append(int(i))
        vor = i
    s1_kand = [int(i) for i in ordn if ph[i] == phase and reg['G1'][i] is True]
    out = dict(S2=s2, S2_phase_beendet=len(s2) >= 2, S2_erster=s2[0] if s2 else None, S4=s4,
               S1_kandidaten=s1_kand, S1='nicht prüfbar ohne Wiederholungsläufe (Generator ohne Wiederholung)',
               S3='siehe s3_pruefung (Kandidaten ohne Wiederholung)',
               hinweis='offline aus Laufzusammenfassungen; keine Echtzeit-Abschaltung (AP-10)')
    if zustand:
        halt = {g: [tab.koepfe[i]['lauf_id'] for i in ordn if (tab.koepfe[i].get('versuch') or {}).get('halt') == g]
                for g in ('S1', 'S3')}
        out.update(S1=halt['S1'], S3=halt['S3'], L_strich_offen=[int(i) for i in ordn if strich[i]],
                   hinweis='Ablaufprotokoll (zustandsbehafteter Ablauf); S2 und S4 für L′ offen (§12)')
    return out


def s3_pruefung(tab, gueltig, kmax, n_tests=42):
    """S3: Größen F_min⁽ʲ⁾ − ⟨N⁽ʲ⁾⟩ (k ≤ k_max), Re/Im N_k⁽ʲ⁾ (k ≤ 3) der Kontrollläufe Lⱼ gegen das Phase-0-Mittel,
    Schwelle c_S·s·√(1 + 1/n₀ⱼ), c_S = t(1 − 0,05/42; n₀ⱼ − 1). Rückgabe Kandidaten (erste Überschreitung)."""
    art = tab.spalte('laufart', object)
    ph = tab.spalte('phase', int)
    mod = tab.koepfe
    e = tab.spalte('einstellung', int)
    out = []
    for j in (1, 2, 3):
        m0 = np.flatnonzero((art == 'L') & (ph == 0) & (e == 1) & gueltig & np.array([k['modul'] == j for k in mod]))
        m1 = np.flatnonzero((art == 'L') & (ph == 1) & (e == 1) & np.array([k['modul'] == j for k in mod]))
        if m0.size < 2:
            continue
        X0 = kv.h1_vektor(tab.daten['Nk_summe'][m0, :kmax])
        mu, s = X0.mean(0), X0.std(0, ddof=1)
        n0 = m0.size
        cS = stats.t.ppf(1 - 0.05 / n_tests, n0 - 1)
        X1 = kv.h1_vektor(tab.daten['Nk_summe'][m1, :kmax])
        for ii, i in enumerate(m1):
            ueber = np.abs(X1[ii] - mu) > cS * s * np.sqrt(1 + 1 / n0)
            if ueber.any():
                out.append(dict(lauf=int(i), modul=j, groessen=[kv.GROESSEN_H1[q] for q in np.flatnonzero(ueber)]))
    return dict(kandidaten=out, reproduktion='nicht prüfbar ohne sofortige Wiederholung')
