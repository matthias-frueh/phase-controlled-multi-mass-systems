"""AP-12: synthetisches Teil B nach Präreg A9.3 aus Phase-0-Daten, Kalibrierung (AP-11), Pilotanalyse (AP-11) und den
Ergebnissen von Werkzeug 8 (AP-13). Teil B wird nicht mit Messwerten gefüllt; synthetische Kennungen beginnen mit
„SYNTH-“ und behaupten keine Registrierung.

Gliederung (A9.3): nr1 Herkunft; nr2 Platzhalterwerte; nr3 Einzelmodul-Harmonische der Phase 0 je Lauf (Zellen,
ungebändert) mit den festen Indexmatrizen B⁰ⱼ; nr4 Vorhersage an den Sollphasen mit dem Jitter der Pilotläufe
(ρⱼₖ = e^{−ikφⱼ,soll}·e^{−k²σⱼ²/2}, A2.4), D_q (Fassung B, dazu Fassung A), Δ_q = Faktor·D_q, Δ_rel,q, Sensitivität
0,1·D_q, Rauschbias b̂⁰, b̂¹ mit u(b̂) (Werkzeug 8), u_c,erw, H1Z-Grenzen, ŷ⁰′ an den Punkten I; nr5 T(kω) für E3;
nr6 H2-Fenster, φ̂₂*, SNR und erwartete Halbbreite; nr5 trägt dazu die Unsicherheitsbeschreibung von T
(kontrollen.t_beschreibung, A9.3 Nr. 5); nr7 H3-Vorhersage (nur zum Vergleich); nr8 Prüfmenge V;
nr9 Laufreihenfolge; nr10 Ergebnisse von Werkzeug 8 (c von H1 und H1Z mit Prüfrate und Herkunft, kritischer Wert für
ε_ctrl, Intervalltyp von H2 mit Überdeckung). Fehlende Werte stehen als None mit Vermerk; Stufe 2 meldet die
betroffenen Ausgänge dann als nicht entscheidbar mit Grund.

Phase-0-Größen (ab teil_b-0.3): σ_Δ, σ̂_ref, ε_ctrl mit kritischem Wert, p̂, die Streuungen (u_c,erw, V, SNR) und die
Auswahl der gültigen Phase-0-Läufe (ŷ⁰, N_s) stammen aus einem Satz, der an k_max und N_z des tatsächlich verwendeten
Plans gebunden ist (phase0_satz, nr2.phase0_bindung). Ein passender Satz der Pilotausgabe wird übernommen, sonst mit
dem Code des Pilotskripts neu berechnet; Pilotausgaben anderer Daten oder ohne Seed werden zurückgewiesen. Bis
teil_b-0.2 stammten diese Größen aus dem vorläufigen Satz bei k der Pilotgrößen (bei A4 k = 30 gegen k_max = 9); diese
Bindung ist als „historisch“ nur ausdrücklich und gekennzeichnet wählbar. nr2.arbeitspunkt prüft den Plan mit dem
gebundenen p̂ erneut (Reserve, n_max, Herkunft aus der Suche) und gibt einen nicht mehr abgesicherten Plan als solchen aus;
nachoptimiert wird nicht.

Laufgrößen (ab teil_b-0.4, nur Regelstand 2026-11): nr2.laufgroessen enthält die Komponentenschätzer des gebundenen
Satzes (laufgroessen.schaetzen bei k_max und N_z; aus der Pilotausgabe übernommen oder hier aus den gültigen Läufen
des Satzes berechnet), nr2.sigma_a_j, nr2.sigma_delta_j und nr2.sigma_off_j je Modul mit ν und marginaler oberer
80-%-Grenze (A9.3 Nr. 2, Entwurf). nr10.werte_regel nennt die Regel planung.teil_b_werte (Teil-B-Werte aus
Punktschätzern nach der Planung) und die Modellquelle der Werkzeug-8-Werte. Unter den historischen Profilen bleibt
Teil B unverändert (teil_b-0.3).
"""
import math

import numpy as np
from scipy import stats

from . import bootstrap as bs, formate, g4, h2, kontrollen, konventionen as kv, laufgroessen, pilot, regeln
from . import vorhersage as vh, zeltfit as zfit
from . import zusammenfassung as zf
from .regeln import RegelOffen

VERSION = 'teil_b-0.4'          # 0.2: nr5.unsicherheit (Korrektur E), nr1.phase0_verarbeitung (Korrektur B);
                                # 0.3: Phase-0-Satz an k_max und N_z des Plans gebunden, nr2.arbeitspunkt;
                                # 0.4: Laufgrößen in nr2 (nur Regelstand 2026-11)
VERSION_HISTORISCH = 'teil_b-0.3'


def version(profil):
    """Version von Teil B unter dem Profil: historische Profile bilden Teil B wie teil_b-0.3."""
    return VERSION_HISTORISCH if regeln.ist_historisch(profil) else VERSION


BINDUNGEN = ('plan', 'historisch')
# Felder einer Bindung, die den Satz bestimmen (Phase-0-Daten, k, Fenster, Code und Seed); die Quellangabe zählt nicht
BINDUNG_IDENTITAET = ('k', 'N_z', 'n_fuenftel', 'T_a_s', 'phase0_sha256', 'n_laeufe', 'n_pilot', 'seed_eps_ctrl',
                      'n_sim_eps_ctrl', 'version')


def gleich_gebunden(a, b):
    """Bezeichnen zwei Bindungen denselben Satz (BINDUNG_IDENTITAET)? Fehlt eine Bindung, nein."""
    return isinstance(a, dict) and isinstance(b, dict) and all(a.get(x) == b.get(x) for x in BINDUNG_IDENTITAET)


def konfigurationen(zusatz=False, punkte_I=None):
    """Konfigurationsliste in der Reihenfolge von §6 (Schnitt aufsteigend, Zusatz, Punkte I bei Einstellung 2)."""
    out = [dict(id=zf.konfig_id('K', (0.0, p, kv.SCHNITT_PHI3), gruppe='schnitt'), gruppe='schnitt',
                phi=[0.0, float(p), kv.SCHNITT_PHI3], einstellung=1) for p in kv.SCHNITT_PHI2]
    if zusatz:
        out += [dict(id=zf.konfig_id('K', (0.0, 0.0, b), gruppe='zusatz'), gruppe='zusatz', phi=[0.0, 0.0, b],
                     einstellung=1) for b in (0.0, 180.0)]
    for p in (punkte_I or []):
        out.append(dict(id=zf.konfig_id('K', (0.0, p, kv.SCHNITT_PHI3), einstellung=2, gruppe='identifizierbarkeit'),
                        gruppe='identifizierbarkeit', phi=[0.0, float(p), kv.SCHNITT_PHI3], einstellung=2))
    return out


def _einzel(tab, modul, einstellung, ausschluss):
    sel = [i for i, k in enumerate(tab.koepfe) if k['laufart'] == 'L' and k['modul'] == modul
           and k['einstellung'] == einstellung and k['phase'] == 0 and k['lauf_id'] not in ausschluss]
    sel = sorted(sel, key=lambda i: tab.koepfe[i]['position'])
    return dict(Nk_zellen=tab.daten['Nk_zellen'][sel], lauf_ids=[tab.koepfe[i]['lauf_id'] for i in sel],
                positionen=[tab.koepfe[i]['position'] for i in sel])


def rho_soll(phi_profil, dd, sigma, kmax):
    """ρⱼₖ an den Sollphasen: Indexphase φ^P − Δδⱼ, Jitterfaktor e^{−k²σⱼ²/2} (σ in Grad)."""
    k = np.arange(1, kmax + 1)
    idx = np.asarray(phi_profil, float) - np.asarray(dd, float)
    return kv.zeigerfaktor(idx, k) * np.exp(-0.5 * np.outer(np.radians(np.asarray(sigma, float)), k) ** 2)


def d_grenzen(Y, kmax):
    """D_q über den Schnitt aus Vorhersagen Y (21, ≥ kmax) nach §8.5: F_min-Spannweite, Fassung B (Durchmesser),
    Fassung A (größter Betrag) für Re und Im N_k."""
    F = vh.fmin_rel_viele(Y[:, :kmax])
    DB, DA = [F.max() - F.min()], [F.max() - F.min()]
    for k in range(3):
        z = Y[:, k]
        dB = float(np.abs(z[:, None] - z[None, :]).max())
        dA = float(np.abs(z).max())
        DB += [dB, dB]
        DA += [dA, dA]
    return np.array(DB), np.array(DA)


def phase0_satz(tab0, kal, pilot_erg, profil, plan, bindung='plan', seed_pilot=None):
    """Der für Phase 1 maßgebliche Satz der Phase-0-Größen und seine Einordnung (nr2.phase0_bindung).

    bindung='plan': Satz bei k_max des Plans und dem Fenster der übergebenen Phase-0-Läufe; ihre Zyklenzahl muss N_z des
    Plans gleichen (sonst: Läufe zuerst auf die ersten N_z Zyklen kürzen). Ein Satz der Pilotausgabe mit gleichem k, N_z
    und gleichen Phase-0-Daten wird übernommen, bei einem festgelegten Paar der Suche deren Satz vor dem vorläufigen
    Satz auf oberster Ebene (beide haben gleiches k und N_z, wenn die Suche beim k der Pilotgrößen festlegt); gleiches k
    und N_z bei anderen Daten ist unvereinbar. Sonst wird der Satz mit dem Code und Seed des Pilotskripts neu berechnet
    (seed_pilot, falls die Pilotausgabe keinen Seed nennt). bindung='historisch': der vorläufige Satz auf oberster Ebene
    wie bis teil_b-0.2, gekennzeichnet und nicht qualifizierend."""
    if bindung not in BINDUNGEN:
        raise ValueError(f'Bindung {bindung!r} unbekannt ({", ".join(BINDUNGEN)})')
    t = tab0.auswahl(tab0.spalte('phase', int) == 0).sortiert()
    k = int(plan['k_max'])
    N_z, _ = pilot.fenster(t)
    if plan.get('N_z') is not None and int(plan['N_z']) != N_z:
        raise ValueError(f'Teil B: Phase-0-Läufe mit N_z = {N_z} Zyklen passen nicht zum Plan (N_z = {plan["N_z"]}); '
                         'die Läufe zuerst auf die ersten N_z Zyklen kürzen')
    einordnung = pilot.einordnen(pilot_erg)
    info = dict(modus=bindung, k_plan=k, N_z_plan=plan.get('N_z'), N_z=N_z, pilot_version=pilot_erg.get('version'),
                pilot_einordnung=einordnung['bedeutung'], k_pilotgroessen=pilot_erg.get('k_pilotgroessen'))
    if bindung == 'historisch':
        s = pilot.satz_oberste_ebene(pilot_erg)
        info.update(quelle='historisch: vorläufiger Satz bei k der Pilotgrößen (bis teil_b-0.2)', k=info['k_pilotgroessen'],
                    qualifiziert=False, neu_berechnet=False, bindung=s.get('bindung'),
                    grund='nicht an k_max des Plans gebunden' if info['k_pilotgroessen'] != k else
                    'Bindung an k_max zufällig gleich, aber nicht geprüft')
        if pilot.mit_laufgroessen(profil) and 'laufgroessen' not in s and info['k_pilotgroessen'] is not None:
            return _mit_laufgroessen(s, t, profil, int(info['k_pilotgroessen']), info)
        return s, info
    h = pilot.daten_sha256(t)
    such = pilot_erg.get('suche') or {}
    kandidaten = [('Pilotskript, oberste Ebene', pilot.satz_oberste_ebene(pilot_erg))]
    if such.get('satz'):
        kandidaten.insert(0 if such.get('ergebnis') == 'festgelegt' else 1, ('Pilotskript, Suche', such['satz']))
    passend = [(name, s) for name, s in kandidaten
               if s.get('bindung') and s['bindung']['k'] == k and s['bindung']['N_z'] == N_z]
    for name, s in passend:
        if s['bindung']['phase0_sha256'] != h:
            raise ValueError(f'Teil B: Satz „{name}“ (k = {k}, N_z = {N_z}) stammt aus anderen Phase-0-Daten als den '
                             'übergebenen Läufen')
    if passend:
        name, s = passend[0]
        info.update(quelle=name, k=k, qualifiziert=True, neu_berechnet=False, bindung=s['bindung'])
        return _mit_laufgroessen(s, t, profil, k, info)
    seed = pilot_erg.get('seed', seed_pilot)
    if seed is None:
        raise ValueError(f'Teil B: Pilotgrößen nicht an k_max = {k}, N_z = {N_z} gebunden ({einordnung["bedeutung"]}) '
                         'und ohne Seed der ε_ctrl-Simulation nicht neu berechenbar')
    s = pilot.satz_fuer_plan(t, kal, profil, plan['f'], k, int(seed),
                             quelle=f'in Teil B neu berechnet: k_max des Plans = {k}, k der Pilotgrößen = '
                                    f'{pilot_erg.get("k_pilotgroessen")}')
    info.update(quelle='neu berechnet (Code des Pilotskripts)', k=k, qualifiziert=True, neu_berechnet=True,
                bindung=s['bindung'])
    return _mit_laufgroessen(s, t, profil, k, info)


def _mit_laufgroessen(s, t, profil, k, info):
    """Regelstand 2026-11: Laufgrößen des Satzes; fehlen sie (Pilotausgabe eines historischen Profils), werden sie aus
    den gültigen Läufen des Satzes bei dessen k berechnet und so gekennzeichnet."""
    if not pilot.mit_laufgroessen(profil):
        return s, info
    if 'laufgroessen' in s:
        info['laufgroessen_quelle'] = ('mit dem Satz neu berechnet (Code des Pilotskripts)' if info.get('neu_berechnet')
                                       else 'Satz der Pilotausgabe')
        return s, info
    ungueltig = set(s['gueltigkeit']['gruende'])
    maske = np.array([kk['lauf_id'] not in ungueltig for kk in t.koepfe])
    s = dict(s, laufgroessen=laufgroessen.schaetzen(t, maske, k))
    info['laufgroessen_quelle'] = 'in Teil B aus den gültigen Läufen des gebundenen Satzes berechnet'
    return s, info


def arbeitspunkt(plan, satz, info, pilot_erg, profil):
    """Erneute Prüfung des verwendeten Plans mit dem gebundenen Satz (keine Nachoptimierung): Reserve
    r(p̂) = ⌈n_min·p̂/(1 − p̂)⌉ + Reserve, n ≤ n_max(p̂) bei Zeitangaben, p̂ des Plans, Herkunft aus der Suche (Quelle und
    Bindung gleich der des Satzes beim festgelegten Paar, gleich_gebunden).
    Status „abgesichert“ nur für einen Plan aus der Suche mit demselben Satz und bestandenen Prüfungen; „nicht
    abgesichert“, wenn eine Prüfung scheitert; sonst „nicht geprüft“ (externer Plan: gemeinsame Bedingung hier nicht
    geprüft)."""
    p = float(satz['p_hat'])
    n_min, n = int(plan['n_min']), int(plan['n'])
    res = profil.wert('planung.reserve')
    pr, fehl = [], []
    r_soll = math.ceil(n_min * p / (1 - p)) + res if p < 1 else None
    if r_soll is None:
        fehl.append('p̂ = 1: Reserve nicht bestimmbar')
    elif n < n_min + r_soll:
        fehl.append(f'n = {n} < n_min + r(p̂) = {n_min} + {r_soll} (p̂ = {p:.4f})')
    else:
        pr.append(f'n = {n} ≥ n_min + r(p̂) = {n_min + r_soll} (p̂ = {p:.4f})')
    zeit, T_lauf = plan.get('zeit'), plan.get('T_lauf')
    n_max_neu = None
    if zeit and T_lauf is not None and p < 1:
        n_max_neu = pilot.n_max(float(T_lauf), p, zeit)
        (pr if n <= n_max_neu else fehl).append(f'n = {n} {"≤" if n <= n_max_neu else ">"} n_max(p̂) = {n_max_neu}')
    else:
        pr.append('n ≤ n_max nicht prüfbar (Zeitangaben des Plans fehlen)')
    if plan.get('p_hat') is not None and abs(float(plan['p_hat']) - p) > 1e-12:
        fehl.append(f'p̂ des Plans {float(plan["p_hat"]):.4f} ≠ p̂ des gebundenen Satzes {p:.4f}')
    s = pilot_erg.get('suche') or {}
    aus_suche = s.get('ergebnis') == 'festgelegt'
    if aus_suche:
        ab = [x for x in ('k_max', 'N_z', 'n_min', 'n0', 'n') if plan.get(x) is not None and plan.get(x) != s.get(x)]
        if ab:
            fehl.append(f'Plan weicht vom Ergebnis der Suche ab: {ab}')
        if info.get('quelle') != 'Pilotskript, Suche':
            fehl.append(f'Satz nicht der des festgelegten Paars der Suche ({info.get("quelle")})')
        elif not gleich_gebunden(info.get('bindung'), (s.get('satz') or {}).get('bindung')):
            fehl.append('Bindung des Satzes ≠ Bindung des Satzes beim festgelegten Paar der Suche (Daten, k, Fenster, '
                        'Code oder Seed)')
    if info['modus'] == 'historisch':
        fehl.append('historische Bindung: Phase-0-Größen bei k der Pilotgrößen, nicht beim k_max des Plans')
    status = 'nicht abgesichert' if fehl else ('abgesichert' if aus_suche else 'nicht geprüft')
    return dict(status=status, aus_suche=aus_suche, p_hat=p, r_soll=r_soll, r_plan=plan.get('r'), n=n, n_min=n_min,
                n_max_neu=n_max_neu, bestanden=pr, verfehlt=fehl,
                hinweis=None if aus_suche else 'externer Plan: P(H1 und H2 bestätigt | exakt) ≥ 0,8 hier nicht geprüft')


def einordnen(tb):
    """Bedeutung eines Teil B, auch älterer Fassungen (ohne nr2.phase0_bindung)."""
    n2 = tb['nr2']
    b = n2.get('phase0_bindung')
    if b is None:
        return dict(version=tb.get('version') or 'unbekannt', modus='historisch', qualifiziert=False,
                    bedeutung=('Phase-0-Größen (σ_Δ, σ̂_ref, ε_ctrl, p̂, Streuungen, Auswahl gültiger Phase-0-Läufe) aus '
                               'dem vorläufigen Satz bei k der Pilotgrößen, nicht an k_max = '
                               f'{n2.get("k_max")} gebunden (Fassung bis teil_b-0.2)'))
    ap = n2.get('arbeitspunkt') or {}
    return dict(version=tb.get('version'), modus=b['modus'], qualifiziert=bool(b.get('qualifiziert')),
                arbeitspunkt=ap.get('status'),
                bedeutung=f'Phase-0-Größen bei k = {b.get("k")}, N_z = {b.get("N_z")} ({b.get("quelle")})')


def erstellen(tab0, kal, pilot_erg, profil, plan, werkzeug8=None, kennung=None, seed_b0=None, B=None, bindung='plan',
              seed_pilot=None):
    """Teil B (Inhalt als verschachteltes dict). tab0: Phase-0-Läufe (LaufTabelle); kal: Kalibrierung; pilot_erg:
    Ergebnis von pilot.pilot_auswerten; plan: dict(f, k_max, N_z (optional), n_min, n0, r, n, d, n_max, zusatz,
    einstellung2 (art, s, punkte_I) oder None, seed_reihenfolge, laufreihenfolge, seed_bootstrap, gegebenenfalls zeit,
    T_lauf, p_hat); werkzeug8: dict (c_H1, c_H1Z, bias0, bias1, u_bias0, u_bias1 (je (21,) Summe; *_zellen (21, 3)),
    h2_intervall, eps_kritisch, …) oder None; bindung: Phase-0-Satz an den Plan ('plan') oder historisch (phase0_satz)."""
    w8 = dict(werkzeug8 or {})
    if str(w8.get('kennzeichnung', '')).startswith('Demonstration') and not str(kennung or '').startswith(
            formate.PRAEFIX_SYNTH):
        raise ValueError('Teil B: Werkzeug-8-Werte des Demonstrationsmodus („Demonstration, synthetisch, nicht '
                         'kalibriert“) nur für synthetische Kennungen, nie für ein Teil B zu Messdaten')
    kmax = int(plan['k_max'])
    K = int(tab0.k_voll)
    B = profil.zahl('bootstrap_B') if B is None else int(B)
    p05 = kal['p0_5']
    dd = np.asarray(p05['delta_delta_grad'], float)
    satz, bindung_info = phase0_satz(tab0, kal, pilot_erg, profil, plan, bindung, seed_pilot)
    ungueltig = set(satz['gueltigkeit']['gruende'])
    e2 = plan.get('einstellung2')
    # nr3: Einzelmodulläufe der Phase 0 und feste Indexmatrizen B⁰ⱼ
    nr3 = dict(einzel0=[_einzel(tab0, j, 1, ungueltig) for j in (1, 2, 3)],
               einzel0_strich=[_einzel(tab0, j, 2, ungueltig) for j in (1, 2, 3)] if e2 else None,
               B=B, seed_b0=seed_b0)
    ss = np.random.SeedSequence(seed_b0).spawn(6)
    idx = {}
    for j in range(3):
        n0j = len(nr3['einzel0'][j]['lauf_ids'])
        idx[f'B0/modul{j + 1}'] = np.random.Generator(np.random.PCG64(ss[j])).integers(0, n0j, size=(B, n0j))
        if e2:
            n0s = len(nr3['einzel0_strich'][j]['lauf_ids'])
            idx[f"B0′/modul{j + 1}"] = np.random.Generator(np.random.PCG64(ss[3 + j])).integers(0, n0s,
                                                                                                size=(B, n0s))
    nr3['indizes'] = idx
    for j, e in enumerate(nr3['einzel0']):
        if len(e['lauf_ids']) < 2:
            raise ValueError(f'Teil B nicht bildbar: Modul {j + 1} hat {len(e["lauf_ids"])} gültige Einzelmodulläufe '
                             'der Phase 0 (Pilotanalyse: Gültigkeit)')
    Nbar0 = np.stack([e['Nk_zellen'].mean(0) for e in nr3['einzel0']])          # (Modul, Zelle, K)
    # Referenzläufe der Phase 0: N_s je Zelle
    ref = [i for i, k in enumerate(tab0.koepfe) if k['laufart'] == 'R' and k['lauf_id'] not in ungueltig]
    N_s_z = tab0.daten['N_mittel_zellen'][ref].mean(0)
    # nr4: Vorhersage an den Sollphasen mit dem Jitter der Pilotläufe
    pil = [i for i, k in enumerate(tab0.koepfe) if k['konfiguration']['gruppe'] == 'pilot']
    sig = np.r_[0.0, np.nanmedian(tab0.daten['sigma_grad'][pil][:, 1:], 0)]
    konf = konfigurationen(plan.get('zusatz', False), e2['punkte_I'] if e2 else None)
    vor = {}
    for c in konf:
        if c['einstellung'] == 2:
            continue
        rho = rho_soll(c['phi'], dd, sig, K)
        Yz = vh.vorhersage(Nbar0, rho, zellen=True)
        vor[c['id']] = dict(Nk_zellen=Yz, Nk_summe=Yz.sum(0))
    schnitt = [c['id'] for c in konf if c['gruppe'] == 'schnitt']
    Y = np.array([vor[q]['Nk_summe'] for q in schnitt])
    DB, DA = d_grenzen(Y, kmax)
    fak = profil.wert('h1.faktor')
    Delta = fak * DB
    nr4 = dict(konfigurationen={q: dict(F_min_rel=float(vh.fmin_rel_viele(v['Nk_summe'][:kmax])),
                                        N_k=v['Nk_summe'][:3], gamma1=float(kv.schiefe(v['Nk_summe'][:kmax])),
                                        Nk_summe=v['Nk_summe'], Nk_zellen=v['Nk_zellen']) for q, v in vor.items()},
               D_B=DB, D_A=DA, Delta=Delta, Delta_rel=Delta.copy(), Delta_sens_0_1=0.1 * DB, Delta_sens_A=fak * DA,
               faktor=fak, d_fassung=profil.wert('h1.d_fassung'), jitter_grad=sig, N_s_zellen=N_s_z)
    # H1Z-Grenzen (Regel h1z.grenzen offen; Entwicklungsprüffall (a): Δ_q/3)
    try:
        regel = profil.wert('h1z.grenzen')
        nr4['h1z'] = dict(regel=regel, Delta_c=Delta / 3 if regel == 'a' else None,
                          Delta_c_rel=Delta / 3 if regel == 'a' else None)
    except RegelOffen as e:
        nr4['h1z'] = dict(regel=None, grund=e.grund, Delta_c=None, Delta_c_rel=None)
    for name in ('bias0', 'bias1', 'u_bias0', 'u_bias1', 'bias0_zellen', 'bias1_zellen', 'u_bias0_zellen',
                 'u_bias1_zellen'):
        nr4[name] = None if w8.get(name) is None else np.asarray(w8[name], float)
    nr4['bias_herkunft'] = w8.get('bias_herkunft', 'fehlt (Werkzeug 8)')
    # u_c,erw aus s_q (Pilot, gebundener Satz) und u(ŷ) (Bootstrap der Vorhersage an den Sollphasen)
    st = satz['streuungen']
    s_q = np.array([st['s_q'][g] for g in kv.GROESSEN_H1]) if st.get('s_q') else None
    u_yhat = np.zeros((len(schnitt), 7))
    u_gam = np.zeros(len(schnitt))
    Bv = min(B, 2000)                                                   # u(ŷ) für u_c,erw und V (Schätzung)
    Nb = np.stack([(bs.zaehlmatrix(idx[f'B0/modul{j + 1}'][:Bv], e['Nk_zellen'].shape[0]) @
                    e['Nk_zellen'].sum(1)) / e['Nk_zellen'].shape[0] for j, e in enumerate(nr3['einzel0'])], 1)
    for i, q in enumerate(schnitt):
        c = next(x for x in konf if x['id'] == q)
        rho = rho_soll(c['phi'], dd, sig, K)
        reps = np.einsum('bjk,jk->bk', Nb, rho)[:, :kmax]
        u_yhat[i] = vh.groessen(reps, kmax).std(0, ddof=1)
        u_gam[i] = kv.schiefe(reps).std(ddof=1)
    n_min = int(plan['n_min'])
    nr4['u_yhat'] = u_yhat
    nr4['u_yhat_replikate'] = int(Bv)
    nr4['u_c_erw'] = None if s_q is None else np.sqrt(s_q[None, :] ** 2 / n_min + u_yhat ** 2)
    # nr8: Prüfmenge V
    c4 = float(stats.t.ppf(1 - 0.05 / profil.wert('h4.m'), n_min - 1))
    s_g = st.get('s_gamma1')
    V = []
    if s_g is not None:
        for i, q in enumerate(schnitt):
            g = nr4['konfigurationen'][q]['gamma1']
            ue = np.sqrt(s_g ** 2 / n_min + u_gam[i] ** 2)
            if abs(g) >= (c4 + profil.wert('h4.aufnahme')) * ue:
                V.append(dict(id=q, gamma_vorhersage=g, u_c_erw=float(ue)))
    nr8 = dict(V=V, c4=c4, zusatz=bool(plan.get('zusatz', False)))
    # nr6: H2-Fenster und Spitzenlage an der Vorhersage
    F_vor = np.array([nr4['konfigurationen'][q]['F_min_rel'] for q in schnitt])
    try:
        W = h2.fenster(F_vor, kv.SCHNITT_PHI2, profil)
        phiW = np.array([kv.SCHNITT_PHI2[i] for i in W['W']])
        fit = zfit.zeltfit(phiW[None], F_vor[W['W']][None])
        phis = float(fit['phi_stern'][0])
        lin = phiW <= phis
        sL = np.polyfit(phiW[lin], F_vor[W['W']][lin], 1)[0] if lin.sum() >= 2 else np.nan
        sR = -np.polyfit(phiW[~lin], F_vor[W['W']][~lin], 1)[0] if (~lin).sum() >= 2 else np.nan
        sF = st['s_q']['F_min_rel'] if st.get('s_q') else None
        snr = None if not sF else float(np.nanmean([abs(sL), abs(sR)]) * 1.0 / sF)
        nr6 = dict(W=W, W_ids=[schnitt[i] for i in W['W']], phi_hat_stern=phis, flanken=[float(sL), float(sR)],
                   SNR=snr, halbbreite_erwartet=None if snr is None else float(3 / (snr * np.sqrt(plan['n']))))
    except RegelOffen as e:
        nr6 = dict(W=None, grund=e.grund)
    # nr5: T(kω) für E3
    T = kontrollen.uebertragung(kal, plan['f'])
    nr5 = dict(T=T, hinweis='T aus P0.1 (Statik, Lagen, Verstärkungen), Kette und 1 FG; Kippmoden vernachlässigt',
               unsicherheit=kontrollen.t_beschreibung(kal, plan['f']))
    if nr5['unsicherheit'] is not None:
        nr5['unsicherheit']['herkunft'] = dict(quelle='Kalibrierung (AP-11): P0.1 Laststellen und Brücke, P0.4 '
                                                     'Einfreiheitsgrad', kalibrierung_sha256=formate.sha256_json(kal),
                                               teil_b_version=version(profil))
    nr2 = dict(f=float(plan['f']), k_max=kmax, k_voll=K, delta_delta_grad=dd,
               u_delta_delta_grad=np.asarray(p05['u_delta_delta_grad'], float),
               sigma_tol_grad=pilot_erg['sigma_tol_grad'], delta_f_tol=plan.get('delta_f_tol'),
               sigma_ref=satz['sigma_ref']['sigma_ref'], sigma_ref_zellen=satz['sigma_ref']['sigma_ref_zellen'],
               eps_ctrl=satz['eps_ctrl'].get('eps_ctrl'), eps_ctrl_test=satz['eps_ctrl'],
               sigma_c=pilot_erg['sigma_c'], F_LO_zellen=pilot_erg['F_LO_zellen'],
               sigma_delta=satz['sigma_delta'], T_P0=plan.get('T_P0'), Delta_T=plan.get('Delta_T'),
               n_min=n_min, n0=int(plan['n0']), r=plan.get('r'), n=int(plan['n']), n_max=plan.get('n_max'),
               d=int(plan['d']), p_hat=satz['p_hat'], einstellung2=e2,
               F_c_stat=np.asarray(kal['p0_2']['F_c_stat_N'], float), N_s_zellen=N_s_z,
               konfigurationen=konf, f_takt=plan.get('f_takt', 1e6),
               pilot_suche={x: pilot_erg.get('suche', {}).get(x) for x in ('ergebnis', 'grund')},
               phase0_bindung=bindung_info, arbeitspunkt=arbeitspunkt(plan, satz, bindung_info, pilot_erg, profil),
               N_z=bindung_info['N_z'])
    if 'laufgroessen' in satz:                                          # Regelstand 2026-11 (A9.3 Nr. 2, Entwurf)
        nr2.update(laufgroessen_felder(satz['laufgroessen']))
    if 'g4.verfahren' in profil.regeln and profil.hat('g4.verfahren'):     # Regelstand 2026-11: G4 B+, D, Lⱼ (g4.py)
        nr2['g4'] = g4.teil_b_block(tab0, ungueltig, Nbar0.sum(1), dd, np.asarray(p05['u_delta_delta_grad'], float),
                                    sig, kmax, konf, satz.get('laufgroessen'), profil)   # σ_Δ aus den gültigen Läufen
    nr10 = dict(c_H1=w8.get('c_H1'), c_H1_herkunft=w8.get('c_H1_herkunft', 'fehlt (Werkzeug 8)'),
                c_H1Z=w8.get('c_H1Z'), c_H1Z_herkunft=w8.get('c_H1Z_herkunft', 'fehlt (Werkzeug 8)'),
                pruefrate=w8.get('pruefrate'), h2_intervall=w8.get('h2_intervall'),
                eps_kritisch=satz['eps_ctrl'].get('kritisch'), raten=w8.get('raten'))
    if not regeln.ist_historisch(profil) and w8.get('e3_kriterien') is not None:
        nr10['e3_kriterien'] = w8['e3_kriterien']                      # Rückfall je Prüfgröße (E3, A9.11)
    if not regeln.ist_historisch(profil):
        nr10['werte_regel'] = dict(planung_teil_b_werte=profil.wert_oder_none('planung.teil_b_werte'),
                                   modellquelle=w8.get('modellquelle', 'nicht angegeben (Werkzeug 8)'),
                                   hinweis='Planung an der oberen Grenze mit c_B; Teil-B-Werte aus Punktschätzern '
                                           'der Kalibrierung nach der Planung')
    nr1_neu = {} if regeln.ist_historisch(profil) else dict(phase0_optionale_sha256={
        k: formate.sha256_bytes(formate.npz_bytes({k: v})) for k, v in tab0.daten.items() if k in zf.OPTIONALE_FELDER})
    return dict(version=version(profil), kennung=kennung,
                nr1=dict(kalibrierung_sha256=formate.sha256_json(kal), **nr1_neu,
                         phase0_sha256=formate.sha256_bytes(formate.npz_bytes(zf.pflichtfelder(tab0.daten))),
                         phase0_verarbeitung=zf.verarbeitungsstand(tab0.koepfe),
                         pilot_sha256=formate.sha256_json(pilot_erg), code_version=formate.code_version()),
                nr2=nr2, nr3=nr3, nr4=nr4, nr5=nr5, nr6=nr6, nr7=dict(hinweis='H3-Vorhersage rechnet Stufe 2 aus der '
                                                                               'Kalibrierung (nur zum Vergleich)'),
                nr8=nr8, nr9=dict(seed=plan.get('seed_reihenfolge'), laufreihenfolge=plan.get('laufreihenfolge')),
                nr10=nr10, seed_bootstrap=plan.get('seed_bootstrap'), profil=profil.kurz())


def laufgroessen_felder(lg):
    """Felder von nr2 aus den Laufgrößen: σ_a,j, σ_δ,j, σ_off,j je Modul mit ν und oberer 80-%-Grenze (marginal)."""
    f = lg['komponenten']
    out = dict(laufgroessen=lg)
    for name, quelle, einheit in (('sigma_a_j', 'sigma_a', '1 (relativ)'),
                                  ('sigma_delta_j', 'sigma_delta_grad', '°'),
                                  ('sigma_off_j', 'sigma_off_grad', '°')):
        out[name] = dict(wert=f[quelle], nu=f[quelle + '_nu'], oben80=f[quelle + '_oben80'], einheit=einheit,
                         bindung=dict(k=lg['bindung']['k'], N_z=lg['bindung']['N_z']),
                         hinweis='marginale obere 80-%-Grenze je Komponente, keine gemeinsame Garantie')
    return out


def schreiben(pfad, inhalt, kennung):
    return formate.schreibe_objekt(pfad, formate.kopf('teil_b', kennung, version=inhalt.get('version', VERSION)),
                                   inhalt)


def lesen(pfad):
    return formate.lies_objekt(pfad, 'teil_b')
