"""Diagnose E3b und G4 mit Pilotreserve (Auftrag vom 17.10.2026): kleine G4-Ergänzungsläufe auf Ebene H und ein Auszug
der E3-Prüfgrößen aus den Neuläufen von PR #21. Die produktive Auswertung bleibt unverändert; Varianten der G4-Schwelle
und der Reserve wertet nur der Berichtsteil (harness.diagnose_e3b_g4_bericht) aus den hier erzeugten Größen aus.

Je Kampagne (Rolle diagnose_g4, Seed zufall.unterseed(20261017, 'diagnose_g4', System, 'L1', i), i = 0 … 39):
Generator (Ebene H), Kalibrierung, Pilotanalyse und Teil B wie kette.kette, dann die Gültigkeitsprüfung der Phase 1
mit den Schwellen aus Teil B (auswertung._schwellen, gueltigkeit.pruefe), ohne Bootstrap und Stufe 2. Für die ersten
vier Kampagnen je System (vorab festgelegt, Startsatz) läuft die volle Kette; ihre Gültigkeit muss mit der schlanken
übereinstimmen. Zusätzlich, nur für die Diagnose und mit eigenen Zufallsströmen derselben Kampagne:
- 20 Läufe eines gezielten Phase-0-Piloten an der steilsten Flanke in der Umgebung des Schnitts, die die
  Mindestabstände der registrierten Piloten einhält (zyklische Abstände mindestens 10° von 120°, §5.4, A7), gewählt am
  rauschfreien Modell vor Phase 0 nach der vorhergesagten Jitterstreuung von D_F;
- ein Wiederholungsvorrat von zwei Läufen je Konfigurationsplatz der Phase 1 (A9.12: höchstens zwei Wiederholungen
  je Konfiguration und Block; der Generator bildet sie nicht ab), am Platz des ursprünglichen Laufs; welche
  Wiederholung gemessen würde, entscheidet erst die Auswertung je Variante;
- je Lauf D_N, D_F (k ≤ k_max und k ≤ k der Pilotgrößen) und F_min − ⟨N⟩ des letzten Fünftels, je Konfiguration die
  aus Phase 0 vorhergesagte Jitterstreuung von D_F (Vorhersage ŷ⁰ wie Teil B nr4, Jitter der Piloten, n_f Zyklen je
  Fünftel) und der Jitter der Piloten.

Checkpoint je Auftrag wie harness.neulauf (Rechencode ohne Berichtsteil, Auftrag, gemeinsame Einstellungen, Profil,
Werkzeug 8, Seeds, Lage des Zielpiloten, Bibliotheken); gerechnet wird nur aus einem sauberen Git-Stand.
vorbereiten() erzeugt einmalig die Auftragsliste, Werkzeug 8 V1-G60h (wiederverwendet aus dem Altlauf) und den
E3-Auszug.
"""
import csv
import json
import os
import shutil
import sys
import time

import numpy as np

from .. import auswertung, formate, gueltigkeit, konventionen as kv, regeln, teil_b, verfahren as vf, vorhersage as vh
from .. import zufall
from .. import zusammenfassung as zf
from ..generator import ebene_h, kampagne as kp, szenarien, wahrheit
from . import kampagnen, kette, neulauf, pruefstand

DOKU_REL = 'docs/e3b_g4_diagnose_2026-10-17'
AUFTRAG = os.path.join(neulauf.WURZEL, DOKU_REL, 'auftrag.json')
AUSGABE = '/tmp/pcmms-diagnose-e3b-g4-20261017'
KENNUNG = 'DIAGNOSE-E3B-G4-20261017'
NICHT_RECHENCODE = neulauf.NICHT_RECHENCODE + ('harness/diagnose_e3b_g4_bericht.py',)
AUSGANGSSTAND = '0a8eb1b3812733b799e5134ddd9c4acf1a5398d2'

SEED_BASIS = 20261017
ROLLE = 'diagnose_g4'
STUFE = 'L1'
SYSTEME = (('N01-A4', 'A4'), ('N01-V1G0', 'V1-G0'), ('N01-V1G60h', 'V1-G60h'))     # Szenario, Werkzeug 8
N_KAMPAGNEN = 40
N_START = 4                     # Startsatz je System: Laufzeitmessung und volle Ketten (vorab festgelegt)
N_ZIELPILOT = 20                # Läufe des gezielten Piloten (wie n_pilot)
WIEDERHOLUNGEN = 2              # Vorrat je Konfigurationsplatz (A9.12)
ABSTAND_MIN_GRAD = 10.0         # Mindestabstand der zyklischen Phasenabstände von 120° (registrierte Piloten: 10°)
H_FLANKE = 0.05                 # Schritt der einseitigen Differenzen [°] (nur beschreibend)
N_JITTER_MC = 256               # feste Ziehungen (antithetisch verdoppelt) der vorhergesagten Jitterstreuung
SEED_JITTER_MC = 20261017
JITTER_NENN_GRAD = 0.2          # Nennjitter je Zyklus für die Wahl des Zielpiloten vor Phase 0 (Rauschmodell L1)
SUCHRASTER = (np.arange(90.0, 150.0 + 1e-9, 2.0), np.arange(200.0, 280.0 + 1e-9, 2.0))    # Umgebung des Schnitts
REGELN = gueltigkeit.REGELN_G
VERFAHREN = vf.HISTORISCH       # Diagnose des produktiven Stands vom 17.10.2026 (σ_Δ bei k der Pilotgrößen)

# Werkzeug 8: A4 und V1-G0 aus PR #21 (unverändert), V1-G60h aus dem Altlauf (vorbereiten)
W8_DATEIEN = {'A4': 'docs/ap13_neulaeufe_2026-10-17/werkzeug8_A4',
              'V1-G0': 'docs/ap13_neulaeufe_2026-10-17/werkzeug8_V1G0',
              'V1-G60h': f'{DOKU_REL}/werkzeug8_V1G60h'}
NEULAUF_AUFTRAG_REL = 'docs/ap13_neulaeufe_2026-10-17/auftrag.json'
NEULAUF_GIT = '020e1313b1d8e39bd7f77ba0e5295cbf4f132865'       # Rechenstand der Neuläufe (PR #21)

Fehler = neulauf.AuftragFehler


def kampagnen_seeds(sid, n=N_KAMPAGNEN, basis=SEED_BASIS):
    return [kampagnen.kampagnen_seed(basis, ROLLE, sid, STUFE, i) for i in range(n)]


def profil_und_plan(g):
    """Profil ENTW-2026-10 mit der Reduktion des Prüfstands (wie PR #21) und Entwicklungsplan; prüft beide."""
    st = pruefstand.STANDARD
    soll = dict(profil_reduktion=st['profil_reduktion'], plan=st['plan'], n_min=st['n_min'], stufe=st['stufe'])
    ab = [k for k, v in soll.items() if not neulauf._gleich(g[k], v)]
    if ab:
        raise Fehler(f'gemeinsame Einstellungen weichen von pruefstand.STANDARD ab: {ab}')
    prof = regeln.profil(g['profil']).mit_reduktion(**g['profil_reduktion'])
    if prof.sha256() != g['profil_sha256'] or prof.sha256() != neulauf.ALT_PROFIL_SHA256:
        raise Fehler(f'Profil-Hash {prof.sha256()} ≠ {g["profil_sha256"]}')
    if prof.wert('g4.faktor') != g['g4_faktor']:
        raise Fehler('G4-Faktor des Profils ≠ Auftragsliste')
    return prof, kp.Plan(**g['plan'])


# ── Flanke, Zielpilot ─────────────────────────────────────────────────────────────────────────────────────
def abstaende(p2, p3):
    """Zyklische Phasenabstände (φ₂, φ₃ − φ₂, 360° − φ₃) einer Konfiguration (0, φ₂, φ₃)."""
    return np.array([p2, p3 - p2, 360.0 - p3])


def zulaessig(p2, p3, abstand=ABSTAND_MIN_GRAD):
    """Pilotkonfiguration mit allen zyklischen Abständen mindestens `abstand` von 120° (A7: keine Äquivalenz zu einem
    Schnittpunkt, mit dem Mindestabstand der registrierten Piloten)."""
    a = abstaende(p2, p3)
    return bool((a > 0).all() and np.abs(a - 120.0).min() >= abstand - 1e-9)


def steigung(F, p2, p3, h=H_FLANKE):
    """Einseitige RMS-Steigungen (s₂, s₃) einer Funktion F(φ₂, φ₃): √((d₊² + d₋²)/2) je Richtung; am Knick des Zelts
    (zwei gleiche Minima) gibt das die Streuung einer kleinen symmetrischen Phasenstörung wieder."""
    f0 = F(p2, p3)
    s = []
    for d2, d3 in ((h, 0.0), (0.0, h)):
        dp = (F(p2 + d2, p3 + d3) - f0) / h
        dm = (f0 - F(p2 - d2, p3 - d3)) / h
        s.append(float(np.sqrt(0.5 * (dp * dp + dm * dm))))
    return s


def _ziehungen(n=N_JITTER_MC, seed=SEED_JITTER_MC):
    """Feste Standardnormalziehungen (n, 2), antithetisch verdoppelt."""
    z = np.random.default_rng(seed).standard_normal((n, 2))
    return np.concatenate([z, -z])


def jitter_streuung(F_viele, phis, s, z=None):
    """Vorhergesagte Streuung der Fünftel-Differenz D_F aus dem Jitter der Indexphasen: √(2·Var_e F(φ + e)) mit
    e = (0, s₂·z₁, s₃·z₂) und festen Ziehungen z; s = (s₂, s₃) Streuung der Fünftelmittel der Indexphase [°] (σⱼ/√n_f).
    Erfasst auch den Knick des Zelts (zwei gleiche Minima), an dem die örtliche Steigung nicht bestimmt ist."""
    z = _ziehungen() if z is None else z
    out = []
    for p2, p3 in phis:
        P = np.column_stack([np.zeros(len(z)), p2 + s[0] * z[:, 0], p3 + s[1] * z[:, 1]])
        out.append(float(np.sqrt(2.0 * np.var(F_viele(P), ddof=1))))
    return np.array(out)


def fmin_modell(sid, plan):
    """F_min − ⟨N⟩ (k ≤ k_max) der rauschfreien Superposition für viele Profilphasen (n, 3) (Auslegungsmodell)."""
    m = szenarien.modell(sid, STUFE, plan=plan)
    kmax = m.system.k_max
    specs, tab = wahrheit.rauschfreie_laeufe(m, kp.schnitt_konfigurationen(m.plan))
    k = np.arange(1, tab.k_voll + 1)
    E = np.stack([next(tab.daten['Nk_summe'][i] for i, sp in enumerate(specs) if sp['laufart'] == 'L'
                       and sp['phase'] == 0 and sp['einstellung'] == 1 and sp['modul'] == j) for j in (1, 2, 3)])

    def F_viele(P):
        Z = kv.zeigerfaktor(m.index_soll_grad(np.asarray(P, float)), k)
        return vh.fmin_rel_viele(np.einsum('njk,jk->nk', Z, E)[:, :kmax])
    return F_viele, kmax, m


def fmin_phase0(tb, kmax):
    """F_min − ⟨N⟩ (k ≤ k_max) der Phase-0-Vorhersage aus Teil B wie nr4 (Einzelmodulmittel P0.8 der gültigen Läufe,
    Δδⱼ aus P0.5, Jitterfaktor der Piloten) für viele Profilphasen (n, 3)."""
    Nbar0 = np.stack([np.asarray(e['Nk_zellen']).mean(0) for e in tb['nr3']['einzel0']]).sum(1)      # (Modul, K)
    dd = np.asarray(tb['nr2']['delta_delta_grad'], float)
    sig = np.asarray(tb['nr4']['jitter_grad'], float)
    k = np.arange(1, Nbar0.shape[-1] + 1)
    daempfung = np.exp(-0.5 * np.outer(np.radians(sig), k) ** 2)

    def F_viele(P):
        rho = kv.zeigerfaktor(np.asarray(P, float) - dd, k) * daempfung                            # wie rho_soll
        return vh.fmin_rel_viele(np.einsum('njk,jk->nk', rho, Nbar0)[:, :kmax])
    return F_viele


def ziel_pilot(sid, plan):
    """Zulässige Pilotkonfiguration in der Umgebung des Schnitts mit der größten vorhergesagten Jitterstreuung von
    D_F (Auslegungsmodell, Nennjitter); dazu dieselbe Größe und die einseitige Steigung an Schnitt und Piloten."""
    F_viele, kmax, m = fmin_modell(sid, plan)
    nf = m.plan.n_zyklen // 5
    s = (JITTER_NENN_GRAD / np.sqrt(nf),) * 2
    kand = [(float(p2), float(p3)) for p2 in SUCHRASTER[0] for p3 in SUCHRASTER[1]
            if zulaessig(p2, p3) and (float(p2), float(p3)) not in kv.PILOTEN]
    sj = jitter_streuung(F_viele, kand, s)
    i = int(np.argmax(sj))
    F1 = lambda p2, p3: float(F_viele([[0.0, p2, p3]])[0])                                        # noqa: E731
    schnitt = [(float(p2), kv.SCHNITT_PHI3) for p2 in kv.SCHNITT_PHI2]
    return dict(phi=list(kand[i]), jitter_streuung_N=float(sj[i]), k_max=kmax, n_fuenftel=nf,
                jitter_nenn_grad=JITTER_NENN_GRAD, kandidaten=len(kand),
                jitter_streuung_schnitt_N=jitter_streuung(F_viele, schnitt, s).tolist(),
                jitter_streuung_piloten_N=jitter_streuung(F_viele, kv.PILOTEN, s).tolist(),
                steigung_schnitt=[float(np.hypot(*steigung(F1, *p))) for p in schnitt],
                steigung_piloten=[float(np.hypot(*steigung(F1, *p))) for p in kv.PILOTEN],
                steigung_ziel=float(np.hypot(*steigung(F1, *kand[i]))),
                raster=[[float(SUCHRASTER[0][0]), float(SUCHRASTER[0][-1]), 2.0],
                        [float(SUCHRASTER[1][0]), float(SUCHRASTER[1][-1]), 2.0]])


# ── eine Kampagne ─────────────────────────────────────────────────────────────────────────────────────────
def _flags(pr, n):
    """Regelergebnisse je Lauf als int8 (−1 nicht anwendbar/prüfbar, 0 eingehalten, 1 verletzt), Spalten REGELN."""
    out = np.full((n, len(REGELN)), -1, np.int8)
    for j, g in enumerate(REGELN):
        v = pr['regeln'][g]
        out[:, j] = [-1 if x is None else int(bool(x)) for x in v]
    return out


def _differenzen(tab, kmax, kval):
    DN, DF = gueltigkeit.fuenftel_differenzen(tab, kmax)
    DFv = DF if kval == kmax else gueltigkeit.fuenftel_differenzen(tab, kval)[1]
    Fl = kv.fmin_rel(tab.daten['fuenftel_Nk'][:, 1, :kmax])
    return DN, DF, DFv, Fl


def _koepfe_neu(koepfe, suffix):
    keys = ('laufart', 'modul', 'einstellung', 'konfiguration', 'phase', 'block', 'messtag', 'position',
            'kontrollsatz', 't_start', 't_ende')
    return [dict({k: h[k] for k in keys}, lauf_id=f'{h["lauf_id"]}-{suffix}') for h in koepfe]


def _verbinde(a, b):
    return zf.LaufTabelle(a.koepfe + b.koepfe, {n: np.concatenate([a.daten[n], b.daten[n]]) for n in a.daten}, a.meta)


def kampagne(auftrag):
    """Eine Kampagne der G4-Diagnose (Arbeitsprozess). auftrag = (Szenario, Index, Seed, Profil, Plan, n_min,
    Werkzeug 8, voll, Zielpilot (φ₂, φ₃)). Rückgabe dict mit Skalaren und Feldern je Lauf."""
    sid, idx, seed, prof, plan, n_min, w8, voll, ziel = auftrag
    t0 = time.perf_counter()
    kurz = info = None
    if voll:
        r = kette.kette(sid, STUFE, prof, plan=plan, seed=seed, werkzeug8=w8, n_min=n_min, mit_wahrheit=False,
                        verfahren=VERFAHREN)
        m, laeufe, tab, tb, pe, erg = r['modell'], r['laeufe'], r['tabelle'], r['teil_b'], r['pilot'], r['ergebnis']
        kurz = kampagnen.kurzbefund(erg, tb, seed)
        kurz = {k: v for k, v in kurz.items() if k not in ('felder', 'teil_b')}
        info = erg['konfigurationen']
    else:
        m, laeufe, tab = kette.kampagne_erzeugen(sid, STUFE, plan, seed)
        _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
        tb, pe = kette.teil_b_erzeugen(tab, kal, m, prof, w8, seed, n_min,
                                       kennung=formate.synth_kennung('KETTE', sid, STUFE, seed), verfahren=VERFAHREN)
    t_kette = time.perf_counter() - t0
    kmax, kval = int(tb['nr2']['k_max']), int(pe['k_pilotgroessen'])
    sw = auswertung._schwellen(tb, prof)
    t1 = tab.auswahl(tab.spalte('phase', int) == 1).sortiert()
    pr = gueltigkeit.pruefe(t1, sw)
    ab = gueltigkeit.abbruchregeln(t1, pr)
    if voll:
        g = erg['gueltigkeit']['gruende']
        lean = {t1.koepfe[i]['lauf_id']: pr['gruende'][i] for i in np.flatnonzero(~pr['gueltig'])}
        if not neulauf._gleich(lean, g):
            raise Fehler(f'{sid}/{idx}: schlanke Gültigkeitsprüfung ≠ volle Kette')
    # Phase 0: registrierte Piloten (produktive Gültigkeit) und der gezielte Pilot (nur Diagnose)
    tab0 = tab.auswahl(tab.spalte('phase', int) == 0).sortiert()
    gr0 = np.array([k['konfiguration']['gruppe'] for k in tab0.koepfe])
    pil = (tab0.spalte('laufart', object) == 'K') & (gr0 == 'pilot')
    p0 = tab0.auswahl(pil)
    if not neulauf._gleich(gueltigkeit.sigma_delta(tab0, kval)['K'], sw.sigma_delta['K']):
        raise Fehler(f'{sid}/{idx}: σ_Δ der Kombinationsläufe in Teil B ≠ Piloten bei k = {kval}')
    ung0 = set(pe['gueltigkeit']['gruende'])
    pil_konf = np.array([kv.PILOTEN.index(tuple(k['konfiguration']['phi_soll_grad'][1:])) for k in p0.koepfe])
    pil_regeln = np.array([[int(g in pe['gueltigkeit']['gruende'].get(k['lauf_id'], [])) for g in REGELN]
                           for k in p0.koepfe], np.int8).reshape(-1, len(REGELN))
    zk = kp._konf('K', 'pilot', (0.0, float(ziel[0]), float(ziel[1])))
    T_lauf, t_end = m.plan.T_lauf, max(k['t_ende'] for k in tab0.koepfe)
    zl = [dict(zk, phase=0, block=None, messtag=1, position=100000 + j, kontrollsatz=None,
               lauf_id=f'0-Z{j:02d}-{zk["konfiguration"]["id"]}', t_start=t_end + j * T_lauf,
               t_ende=t_end + (j + 1) * T_lauf) for j in range(N_ZIELPILOT)]
    zt = ebene_h.erzeuge(m, zl, zufall.strom(seed, 'diagnose_zielpilot'))
    # Phase 1: Konfigurationsplätze des Schnitts und Wiederholungsvorrat
    schnitt = [c['konfiguration']['id'] for c in kp.schnitt_konfigurationen(m.plan)
               if c['konfiguration']['gruppe'] == 'schnitt']
    ids = np.array(t1.konfig_ids())
    art1 = t1.spalte('laufart', object)
    plaetze = np.flatnonzero((art1 == 'K') & np.isin(ids, schnitt))
    t1p = t1.auswahl(plaetze)
    wl = []
    for w in range(1, WIEDERHOLUNGEN + 1):
        wl += _koepfe_neu(t1p.koepfe, f'W{w}')
    wt = ebene_h.erzeuge(m, wl, zufall.strom(seed, 'diagnose_wiederholung'))
    t1x = _verbinde(t1, wt)
    prx = gueltigkeit.pruefe(t1x, sw)
    n1 = len(t1)
    for gname in REGELN:
        if not neulauf._gleich([x for x in prx['regeln'][gname][:n1]], [x for x in pr['regeln'][gname]]):
            raise Fehler(f'{sid}/{idx}: Wiederholungsvorrat verändert {gname} der ursprünglichen Läufe')
    fl1 = _flags(prx, len(t1x))
    DN, DF, DFv, Fl = _differenzen(t1x, kmax, kval)
    DN0, DF0, DFv0, _ = _differenzen(p0, kmax, kval)
    DNz, DFz, DFvz, _ = _differenzen(zt, kmax, kval)
    # Gesamtzählung der Plätze: Original, W1, W2 (Reihenfolge wie wl)
    sel = np.r_[plaetze, n1 + np.arange(len(wl))]
    konf = np.array([schnitt.index(c) for c in ids[plaetze]], np.int8)
    rolle = np.repeat(np.arange(WIEDERHOLUNGEN + 1, dtype=np.int8), len(plaetze))
    block = np.tile(t1p.spalte('block', int), WIEDERHOLUNGEN + 1).astype(np.int8)
    # vorhergesagte Jitterstreuung von D_F aus Phase 0 an Schnitt, Piloten und Zielpilot (Jitter der Piloten, n_f)
    phis = [(p2, kv.SCHNITT_PHI3) for p2 in kv.SCHNITT_PHI2] + list(kv.PILOTEN) + [tuple(ziel)]
    nf = int(t1.koepfe[0]['n_fuenftel'])
    s_f = np.asarray(tb['nr4']['jitter_grad'], float)[1:] / np.sqrt(nf)
    sj0 = jitter_streuung(fmin_phase0(tb, kmax), phis, s_f)
    sig_r = tab0.daten['sigma_grad'][pil][:, 1:]
    felder = dict(
        laeufe_konf=np.tile(konf, WIEDERHOLUNGEN + 1), laeufe_rolle=rolle, laeufe_block=block,
        laeufe_DN=DN[sel], laeufe_DF=DF[sel], laeufe_DF_kpilot=DFv[sel], laeufe_Fletzt=Fl[sel],
        laeufe_regeln=fl1[sel], laeufe_gueltig=prx['gueltig'][sel], laeufe_Nmittel=t1x.daten['N_mittel'][sel],
        pilot_konf=pil_konf.astype(np.int8), pilot_DN=DN0, pilot_DF=DF0, pilot_DF_kpilot=DFv0,
        pilot_gueltig=np.array([k['lauf_id'] not in ung0 for k in p0.koepfe]), pilot_regeln=pil_regeln,
        pilot_Nmittel=p0.daten['N_mittel'], pilot_sigma_grad=sig_r,
        ziel_DN=DNz, ziel_DF=DFz, ziel_DF_kpilot=DFvz, ziel_sigma_grad=zt.daten['sigma_grad'][:, 1:],
        ziel_Nmittel=zt.daten['N_mittel'],
        jitter_phase0=sj0)
    sonst = np.flatnonzero(art1 != 'K')
    out = dict(
        szenario=sid, index=int(idx), seed=int(seed), voll=bool(voll), k_max=kmax, k_pilotgroessen=kval,
        k_b=int(pe['k_b']), n_fuenftel=int(t1.koepfe[0]['n_fuenftel']), n_zyklen=int(t1.koepfe[0]['n_zyklen']),
        p_hat=float(pe['p_hat']), p_hat_hinweis=pe['p_hat_hinweis'], n_pilot=int(pil.sum()),
        sigma_delta={g: dict(v) for g, v in sw.sigma_delta.items()}, g4_faktor=float(sw.g4_faktor),
        rundung_rel=gueltigkeit.RUNDUNG_REL, jitter_grad=np.asarray(tb['nr4']['jitter_grad'], float).tolist(),
        zielpilot=[float(ziel[0]), float(ziel[1])], schnitt=schnitt,
        teil_b=dict(n_min=int(tb['nr2']['n_min']), r=tb['nr2'].get('r'), n=int(tb['nr2']['n']),
                    pilot_suche=tb['nr2'].get('pilot_suche')),
        phase1=dict(n_laeufe=int(n1), n_ungueltig=int((~pr['gueltig']).sum()),
                    sonstige_ungueltig={g: int(sum(1 for i in sonst if pr['regeln'][g][i] is True)) for g in REGELN},
                    sonstige_n=int(sonst.size), S2=len(ab['S2']), S2_phase_beendet=bool(ab['S2_phase_beendet']),
                    S4=len(ab['S4']), nicht_pruefbar={g: len(v) for g, v in pr['nicht_pruefbar'].items()}),
        voll_kette=None if not voll else dict(
            H1=kurz['H1']['ausgang'], H1_grund=kurz['H1']['grund'], H1Z=kurz['H1Z']['ausgang'],
            H2=kurz['H2']['ausgang'], H2_grund=kurz['H2']['grund'], H3=kurz['H3']['ausgang'], H4=kurz['H4']['ausgang'],
            E3=(kurz['E3'] or {}).get('bewertung'), n_auswertbar=kurz['n_auswertbar'], yhat1_gueltig=kurz['yhat1_gueltig'],
            konfigurationen={c: dict(n_gueltig=info[c]['n_gueltig'], kontaktast=info[c]['kontaktast'],
                                     auswertbar=info[c]['auswertbar']) for c in schnitt},
            gueltigkeit_gleich_schlank=True),
        laufzeit_s=dict(kette=round(t_kette, 3), gesamt=round(time.perf_counter() - t0, 3)),
        felder=felder)
    return out


# ── Auftragsliste, Ausführung ─────────────────────────────────────────────────────────────────────────────
def lies_auftrag(pfad=AUFTRAG):
    with open(pfad, encoding='utf-8') as f:
        return json.load(f)


def werkzeug8(a, name):
    """Werkzeug-8-Werte und Inhaltsprüfsumme nach der Auftragsliste (vollständig, keine Testvorgabe)."""
    return neulauf.werkzeug8_laden(a, name)


def schluessel(a, job, prof, w8_sha):
    """Herkunftsschlüssel eines Auftrags. Die Lage des Zielpiloten steht je System (nicht im Auftrag) und geht in die
    Rechnung ein; ohne sie würde ein Checkpoint zu einer anderen Lage übernommen."""
    return dict(rechencode=neulauf.rechencode_sha256(NICHT_RECHENCODE), auftrag=formate.sha256_json(job),
                gemeinsam=formate.sha256_json(a['gemeinsam']), profil_sha256=prof.sha256(), werkzeug8=w8_sha,
                seeds=formate.sha256_json(job['seeds']),
                zielpilot=[float(x) for x in a['systeme'][job['szenario']]['zielpilot']['phi']],
                umgebung=neulauf.umgebung())


def _rechne(job, a, prof, plan, w8, ziel, prozesse):
    g = a['gemeinsam']
    auftraege = [(job['szenario'], i, s, prof, plan, g['n_min'], w8, job['voll'], ziel)
                 for i, s in zip(job['indizes'], job['seeds'])]
    if prozesse > 1:
        return kampagnen._parallel(auftraege, prozesse, fn=kampagne)
    return [kampagne(x) for x in auftraege]


def ausfuehren(pfad=AUFTRAG, nur=None, prozesse=None, ausgabe=None, protokoll=print, streng=True):
    """Aufträge der Liste der Reihe nach (je Auftrag bis zu `prozesse` Arbeitsprozesse mit einem BLAS-Thread);
    passende Checkpoints werden übernommen. Rückgabe {id: Status}."""
    a = lies_auftrag(pfad)
    prof, plan = profil_und_plan(a['gemeinsam'])
    git = formate.git_stand()
    if streng and (git is None or git.endswith('+geändert')):
        raise Fehler(f'Arbeitsbaum nicht sauber ({git}): Diagnosetreiber und Auftragsliste vor den Rechnungen committen')
    P = int(prozesse or a['gemeinsam']['prozesse'])
    status = {}
    for job in a['auftraege']:
        if nur and job['id'] not in nur:
            continue
        if job['seeds'] != [kampagnen.kampagnen_seed(SEED_BASIS, ROLLE, job['szenario'], STUFE, i)
                            for i in job['indizes']]:
            raise Fehler(f'{job["id"]}: Seed-Ableitung ergibt andere Seeds als die Auftragsliste')
        sysd = a['systeme'][job['szenario']]
        w8, w8_sha = werkzeug8(a, sysd['werkzeug8'])
        key = schluessel(a, job, prof, w8_sha)
        ziel = os.path.join(ausgabe or a['gemeinsam']['ausgabe'], job['id'])
        s = neulauf.checkpoint(ziel, key)
        if s:
            protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]}: Checkpoint passt (Code {s["git"]}, '
                      f'{s["laufzeit_s"]} s) – übernommen')
            status[job['id']] = 'übernommen'
            continue
        if os.path.exists(ziel):
            beiseite = f'{ziel}.verworfen-{time.strftime("%Y%m%dT%H%M%S")}'
            shutil.move(ziel, beiseite)
            protokoll(f'{job["id"]}: Checkpoint fehlt, ist unvollständig oder passt nicht – beiseitegelegt: {beiseite}')
        os.makedirs(ziel)
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]}: {len(job["seeds"])} Kampagnen …')
        t0, start = time.perf_counter(), formate.zeitstempel()
        befunde = _rechne(job, a, prof, plan, w8, sysd['zielpilot']['phi'], P)
        git_ende = formate.git_stand()
        if streng and git_ende != git:
            raise Fehler(f'{job["id"]}: Code während der Rechnung geändert ({git} → {git_ende})')
        meta = dict(auftrag=job['id'], szenario=job['szenario'], stufe=STUFE, rolle=ROLLE, seed_basis=SEED_BASIS,
                    indizes=job['indizes'], seeds=job['seeds'], voll=job['voll'], profil=prof.id,
                    profil_sha256=prof.sha256(), werkzeug8=sysd['werkzeug8'], werkzeug8_sha256=w8_sha,
                    plan=a['gemeinsam']['plan'], n_min=a['gemeinsam']['n_min'], code_version=formate.code_version())
        name = f'g4_{job["id"]}'
        formate.schreibe_objekt(os.path.join(ziel, name), formate.kopf('bewertung', formate.synth_kennung(
            KENNUNG, job['id'])), dict(meta=meta, befunde=befunde))
        dateien = [name + x for x in ('.json', '.npz') if os.path.exists(os.path.join(ziel, name + x))]
        s = dict(auftrag=job['id'], schluessel=key, dateien={d: formate.sha256_datei(os.path.join(ziel, d))
                                                             for d in dateien},
                 git=git, git_ende=git_ende, start=start, ende=formate.zeitstempel(),
                 laufzeit_s=round(time.perf_counter() - t0, 1), prozesse=P,
                 kernsekunden=round(sum(b['laufzeit_s']['gesamt'] for b in befunde), 1))
        with open(os.path.join(ziel, 'schluessel.json'), 'w', encoding='utf-8') as f:
            f.write(formate.json_text(s))
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]} fertig ({s["laufzeit_s"]} s, {s["kernsekunden"]} '
                  'Kernsekunden)')
        status[job['id']] = 'gerechnet'
    return status


def lies_ergebnisse(a, ausgabe=None):
    """Befunde aller Aufträge aus passenden Checkpoints: {Szenario: [Befund je Kampagne nach Index]} und die
    Checkpoint-Angaben; bricht ab, wenn ein Checkpoint fehlt oder nicht zum aktuellen Stand passt."""
    prof, _ = profil_und_plan(a['gemeinsam'])
    out, cp = {}, {}
    for job in a['auftraege']:
        sysd = a['systeme'][job['szenario']]
        _, w8_sha = werkzeug8(a, sysd['werkzeug8'])
        ziel = os.path.join(ausgabe or a['gemeinsam']['ausgabe'], job['id'])
        s = neulauf.checkpoint(ziel, schluessel(a, job, prof, w8_sha))
        if not s:
            raise Fehler(f'{job["id"]}: kein passender Checkpoint in {ziel} (zuerst harness diagnose-e3b-g4 rechnen)')
        _, v = formate.lies_objekt(os.path.join(ziel, f'g4_{job["id"]}'), 'bewertung')
        out.setdefault(job['szenario'], []).extend(v['befunde'])
        cp[job['id']] = {k: s[k] for k in ('git', 'start', 'ende', 'laufzeit_s', 'prozesse', 'kernsekunden', 'dateien')}
    for sid in out:
        out[sid].sort(key=lambda b: b['index'])
    return out, cp


# ── einmalige Vorbereitung ────────────────────────────────────────────────────────────────────────────────
def _w8_v1g60h(voll, doku):
    """Werkzeug 8 V1-G60h aus der vollständigen Ausgabe des Altlaufs, unverändert (wie harness.neulauf.vorbereiten)."""
    kopf, v = formate.lies_objekt(voll, 'bewertung')
    with open(os.path.join(neulauf.WURZEL, neulauf.HISTORISCH_REL), encoding='utf-8') as f:
        hist = json.load(f)
    if not neulauf._gleich(pruefstand.kompakt(v), hist['inhalt']):
        raise Fehler('vollständige Ausgabe ergibt nicht die historische kompakte Datei')
    if kopf['code_version']['git'] != neulauf.ALT_CODE or v['profil_sha256'] != neulauf.ALT_PROFIL_SHA256:
        raise Fehler('Code oder Profil der vollständigen Ausgabe ≠ Altlauf')
    if neulauf.git_blob(os.path.join(neulauf.WURZEL, neulauf.HISTORISCH_REL)) != neulauf.ALT_BLOB:
        raise Fehler('historische kompakte Datei verändert')
    kal = v['schritte']['kalibrierung_v1']['V1-G60h']
    m = kal['meta']
    st = pruefstand.STANDARD
    if (m['szenario'], m['stufe'], m['seed_basis'], m['profil_sha256']) != ('N01-V1G60h', 'L1', st['seed'],
                                                                            neulauf.ALT_PROFIL_SHA256):
        raise Fehler('Kalibrierung V1-G60h: Szenario, Stufe, Seed oder Profil ≠ Altlauf')
    w8 = dict(kal['werkzeug8'])
    fehlt = [f for f in neulauf.W8_FELDER if w8.get(f) is None]
    if fehlt:
        raise Fehler(f'Werkzeug 8 V1-G60h im Altlauf unvollständig: {fehlt}')
    for f in neulauf.W8_ARRAYS:
        w8[f] = np.asarray(w8[f], float)
    quelle = dict(datei='pruefstand.json (+ pruefstand.npz), vollständige Ausgabe des Entwicklungsprüfstands vom '
                        '16.10.2026; nicht im Repository, im Arbeitsbereich der Sitzung erhalten',
                  sha256=formate.sha256_datei(voll + '.json'), npz_sha256=formate.sha256_datei(voll + '.npz'),
                  kennung=kopf['kennung'], code_version=kopf['code_version'], profil=v['profil'],
                  profil_sha256=v['profil_sha256'],
                  historisch=dict(datei=neulauf.HISTORISCH_REL, git_blob=neulauf.ALT_BLOB, gleich_kompakt_der_quelle=True))
    ort = 'schritte.kalibrierung_v1.V1-G60h.werkzeug8'
    herkunft = dict(art='wiederverwendet (nicht rekonstruiert)', quelle=quelle, ort=ort,
                    kalibrierung=dict(szenario='N01-V1G60h', stufe='L1', seed_basis=m['seed_basis'],
                                      rollen=['kalibrierung_c', 'pruefung_c'], n_kalibrierung=m['n_kalibrierung'],
                                      n_pruefung=m['n_pruefung'], profil=m['profil'], profil_sha256=m['profil_sha256'],
                                      code_version=m['code_version'], plan=st['plan'], n_min=st['n_min'],
                                      gepoolt=kal['gepoolt']))
    datei = 'werkzeug8_V1G60h'
    formate.schreibe_objekt(os.path.join(doku, datei), formate.kopf(
        'werkzeug8', formate.synth_kennung('W8', 'N01-V1G60h', 'L1', st['seed']), herkunft=herkunft), w8)
    _, zurueck = formate.lies_objekt(os.path.join(doku, datei), 'werkzeug8')
    if not neulauf._gleich(zurueck, kal['werkzeug8']):
        raise Fehler('Werkzeug 8 V1-G60h: Datei gibt die Werte des Altlaufs nicht unverändert zurück')
    return dict(datei=f'{DOKU_REL}/{datei}', inhalt_sha256=formate.sha256_json(zurueck), art='wiederverwendet',
                ort_im_altlauf=ort, quelle_sha256=quelle['sha256'], c_H1=w8['c_H1'], c_H1Z=w8['c_H1Z'],
                h2_intervall=dict(typ=w8['h2_intervall']['typ'], niveau=w8['h2_intervall']['niveau']),
                gepoolt=kal['gepoolt'])


E3_SPALTEN = ('punkt', 'kampagne', 'seed', 'bewertung', 'status', 'z_B', 'm', 'n_e3a', 'e3a_auffaellig',
              'e3a_ueber_schwelle', 'e3a_max_ober_grad', 'e3a_max_unter_grad', 'e3a_max_ober_ohne_T_grad', 'q_Z',
              'u_q_Z', 'u_q_Z_ohne_T', 'E3_grund')


def _e3_zeilen(punkt, lauf, sw):
    """Je Kampagne die Prüfgrößen von E3a (zusammengefasst) und E3b in voller Genauigkeit."""
    out = []
    for i, b in enumerate(lauf['befunde']):
        e = b['E3']
        if not e:
            out.append(dict(punkt=punkt, kampagne=i, seed=b['seed'], E3_grund=b['E3_grund']))
            continue
        a = np.asarray(e['e3a'], float).reshape(-1, 3)
        zB = e['z_B']
        q = np.asarray(e['e3b'], float) if e['e3b'] is not None else np.full(3, np.nan)
        z = dict(punkt=punkt, kampagne=i, seed=b['seed'], bewertung=e['bewertung'], z_B=zB, m=e['m'],
                 status=None if e['bewertung'] else e['status'], status_voll=e['status'], n_e3a=int(a.shape[0]),
                 q_Z=float(q[0]), u_q_Z=float(q[1]), u_q_Z_ohne_T=float(q[2]))
        if zB is not None and a.shape[0]:
            ober = a[:, 0] + 1.645 * a[:, 1]
            z.update(e3a_auffaellig=int((a[:, 0] - zB * a[:, 1] > sw['phase_grad']).sum()),
                     e3a_ueber_schwelle=int((ober > sw['phase_grad']).sum()), e3a_max_ober_grad=float(ober.max()),
                     e3a_max_unter_grad=float((a[:, 0] - zB * a[:, 1]).max()),
                     e3a_max_ober_ohne_T_grad=float((a[:, 0] + 1.645 * a[:, 2]).max()))
        out.append(z)
    return out


def _e3_auszug(doku, e3_quelle):
    """E3-Prüfgrößen aller 570 Kampagnen aus den Checkpoints von PR #21 (Herkunft je Punkt geprüft) und Abgleich mit
    der versionierten, gerundeten kampagnen_e3.csv."""
    nl = neulauf.lies_auftrag(os.path.join(neulauf.WURZEL, NEULAUF_AUFTRAG_REL))
    sw = regeln.profil(nl['gemeinsam']['profil']).wert('e3.schwellen')
    with open(os.path.join(neulauf.WURZEL, 'docs/ap13_neulaeufe_2026-10-17/kampagnen_e3.csv'), encoding='utf-8') as f:
        alt = {(r['punkt'], int(r['kampagne'])): r for r in csv.DictReader(f)}
    zeilen, herkunft = [], {}
    for job in nl['auftraege']:
        if job['art'] != 'kampagnen':
            continue
        ziel = os.path.join(e3_quelle, job.get('verzeichnis', job['id']))
        s = neulauf.checkpoint(ziel)
        if not s:
            raise Fehler(f'{job["id"]}: Checkpoint der Neuläufe fehlt oder ist unvollständig ({ziel})')
        if s['schluessel']['auftrag'] != formate.sha256_json(job) or s['git'] != NEULAUF_GIT:
            raise Fehler(f'{job["id"]}: Checkpoint passt nicht zur Auftragsliste der Neuläufe bzw. zu {NEULAUF_GIT}')
        name = next(d for d in s['dateien'] if d.endswith('.json'))[:-5]
        _, lauf = formate.lies_objekt(os.path.join(ziel, name), 'bewertung')
        if lauf['meta']['seeds'] != job['seeds']:
            raise Fehler(f'{job["id"]}: Seeds im Checkpoint ≠ Auftragsliste')
        punkt = f'{job["szenario"]}/{job["stufe"]}'
        z = _e3_zeilen(punkt, lauf, sw)
        for x in z:
            r = alt[(punkt, x['kampagne'])]
            if str(r['seed']) != str(x['seed']) or (r['E3_bewertung'] or None) != x.get('bewertung'):
                raise Fehler(f'{punkt}/{x["kampagne"]}: Bewertung oder Seed ≠ kampagnen_e3.csv')
            for spalte in ('q_Z', 'u_q_Z', 'u_q_Z_ohne_T'):
                if r[spalte] and not np.isclose(float(r[spalte]), x[spalte], rtol=1e-5, atol=0):
                    raise Fehler(f'{punkt}/{x["kampagne"]}: {spalte} ≠ kampagnen_e3.csv')
        zeilen += z
        herkunft[punkt] = dict(auftrag=job['id'], verzeichnis=os.path.relpath(ziel, e3_quelle), git=s['git'],
                               schluessel=s['schluessel'], dateien=s['dateien'], n=len(z), rolle=job['rolle'],
                               werkzeug8=job['werkzeug8'])
    pfad = os.path.join(doku, 'e3_pruefgroessen.csv')
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=E3_SPALTEN, lineterminator='\n')
        w.writeheader()
        for x in zeilen:
            w.writerow({k: (repr(v) if isinstance(v, float) else ('' if v is None else v))
                        for k, v in ((k, x.get(k)) for k in E3_SPALTEN)})
    return dict(datei=f'{DOKU_REL}/e3_pruefgroessen.csv', sha256=formate.sha256_datei(pfad), n=len(zeilen),
                status_mit_bewertung=sorted({z['status_voll'] for z in zeilen if z.get('bewertung')}),
                quelle=dict(verzeichnis=e3_quelle, auftragsliste=NEULAUF_AUFTRAG_REL,
                            auftragsliste_git_blob=neulauf.git_blob(os.path.join(neulauf.WURZEL, NEULAUF_AUFTRAG_REL)),
                            git=NEULAUF_GIT, abgleich='Bewertung, Seed und q_Z, u(q_Z), u ohne T gleich '
                                                      'kampagnen_e3.csv (6 signifikante Stellen)'),
                schwellen=sw, punkte=herkunft)


def vorbereiten(voll, e3_quelle=None, doku=None):
    """Auftragsliste, Werkzeug 8 V1-G60h und E3-Auszug (einmalig, vor den Rechnungen)."""
    doku = doku or os.path.join(neulauf.WURZEL, DOKU_REL)
    e3_quelle = e3_quelle or neulauf.AUSGABE
    os.makedirs(doku, exist_ok=True)
    st = pruefstand.STANDARD
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(**st['profil_reduktion'])
    plan = kp.Plan(**st['plan'])
    w8 = {}
    nl = neulauf.lies_auftrag(os.path.join(neulauf.WURZEL, NEULAUF_AUFTRAG_REL))
    for name in ('A4', 'V1-G0'):
        e = dict(nl['werkzeug8'][name])
        if e['datei'] != W8_DATEIEN[name]:
            raise Fehler(f'Werkzeug 8 {name}: Datei der Neuläufe ≠ {W8_DATEIEN[name]}')
        w8[name] = dict(e, herkunft='PR #21 (unverändert)')
    w8['V1-G60h'] = _w8_v1g60h(voll, doku)
    systeme = {}
    for sid, w in SYSTEME:
        systeme[sid] = dict(werkzeug8=w, zielpilot=ziel_pilot(sid, plan))
    e3 = _e3_auszug(doku, e3_quelle)
    auftr = []
    for sid, _ in SYSTEME:
        for teil, ind, voll_k in (('start', list(range(N_START)), True),
                                  ('rest', list(range(N_START, N_KAMPAGNEN)), False)):
            s = kampagnen_seeds(sid)
            auftr.append(dict(id=f'G4-{sid}-{teil}', szenario=sid, stufe=STUFE, rolle=ROLLE, indizes=ind,
                              seeds=[s[i] for i in ind], voll=voll_k))
    a = dict(kennung=KENNUNG, anweisung='ANWEISUNG_Claude_Code_E3b_G4_Diagnose_2026-10-17',
             ausgangsstand=AUSGANGSSTAND,
             gemeinsam=dict(profil='ENTW-2026-10', profil_reduktion=st['profil_reduktion'], profil_sha256=prof.sha256(),
                            g4_faktor=prof.wert('g4.faktor'), plan=st['plan'], n_min=st['n_min'], stufe=st['stufe'],
                            harmonische='k_max des Systems (A4: 9, V1: 12); σ_Δ der Piloten bei k = k_b (A4: 30), '
                                        'wie die produktive Pilotanalyse ohne Suche',
                            seed_basis=SEED_BASIS, rolle=ROLLE,
                            seed_ableitung="zufall.unterseed(20261017, 'diagnose_g4', Szenario, 'L1', i)",
                            zufallsstroeme=dict(generator="zufall.strom(seed, 'generator')",
                                                zielpilot="zufall.strom(seed, 'diagnose_zielpilot')",
                                                wiederholung="zufall.strom(seed, 'diagnose_wiederholung')"),
                            prozesse=4, blas_threads_je_prozess=1, ausgabe=AUSGABE),
             werkzeug8=w8, systeme=systeme, auftraege=auftr,
             diagnose=dict(zielpilot=f'steilste nach A7 zulässige Konfiguration (Abstände ≥ {ABSTAND_MIN_GRAD:g}° von '
                                     f'120°), {N_ZIELPILOT} Läufe, nur Diagnose',
                           wiederholung=f'{WIEDERHOLUNGEN} Läufe je Konfigurationsplatz am Platz des ursprünglichen '
                                        'Laufs (A9.12), nur Diagnose', flanke_schritt_grad=H_FLANKE,
                           volle_ketten='Startsatz: Kampagnen 0–3 je System'),
             e3=e3,
             umfang=dict(neue_kampagnen=N_KAMPAGNEN * len(SYSTEME), volle_ketten=N_START * len(SYSTEME),
                         kalibrierkampagnen=0, e3_kampagnen_ausgewertet=e3['n'],
                         e3_kampagnen_neu_gerechnet=0))
    with open(os.path.join(doku, 'auftrag.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text(a))
    return a


if __name__ == '__main__':                         # PYTHONPATH=code python3 -m pcmms_auswertung.harness.diagnose_e3b_g4
    from ..cli import main
    sys.exit(main(['harness', 'diagnose-e3b-g4'] + sys.argv[1:]))
