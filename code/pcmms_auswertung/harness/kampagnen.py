"""Gezielte Kampagnen eines Szenariopunkts (Plan AP-13, Abschnitte 2.5 und 4.3): je Kampagne die Kette auf Ebene H
mit eigenem Seed, ein kompakter Befund und daraus Raten mit Monte-Carlo-Fehler gegen die getrennt berechnete Wahrheit.

Seeds: Kampagne i des Szenarios s auf Stufe L mit Rolle ρ (kalibrierung_c, pruefung_c, pruefung, planung …) erhält
den Seed zufall.unterseed(Basis, ρ, s, L, i). Das Ergebnis hängt nicht von der Zahl der Prozesse ab.
Die Wahrheit liest nur dieser Harness; AP-12 erhält sie nicht.
"""
import concurrent.futures as cf
import csv
import multiprocessing as mp
import os
import time
import warnings

import numpy as np

from .. import ablauf as abl, formate, regeln, verfahren as vf, zufall
from ..generator import kampagne as kp, szenarien, wahrheit
from . import kette, metriken

HYPOTHESEN = ('H1', 'H1Z', 'H2', 'H3', 'H4')
AUSGAENGE = ('bestätigt', 'falsifiziert', 'nicht entscheidbar')


def kampagnen_seed(basis, rolle, sid, stufe, i):
    return zufall.unterseed(basis, rolle, sid, stufe, int(i))


def _roh(T, bias, achse=None):
    """Rohresiduum vor der Biaskorrektur und Varianz ohne u²(b̂) aus den gespeicherten Tests (r ist korrigiert)."""
    r = np.array(T['r'], float)
    r[..., 0] = r[..., 0] + np.asarray(bias, float)
    return r, np.asarray(T['varA'], float) + np.asarray(T['varB'], float)


def _e3_kurz(e3):
    """Kompakter E3-Befund: Bewertung, Status, Prüfgrößen je Konfiguration und Modul (|Δφ_Z|, u, u ohne T-Anteil) und
    für E3b (q_Z, u, u ohne T-Anteil), z_B, m sowie die Diagnose der T-Ziehungen (Teil B nr5.unsicherheit)."""
    a = [[abs(v['delta_phi_Z_grad']), v['u_grad'], v.get('u_ohne_T_grad', np.nan)]
         for e in e3.get('e3a') or [] for v in e['e3a'].values()]
    b = e3.get('e3b')
    return dict(bewertung=e3.get('bewertung'), status=e3.get('status'), z_B=e3.get('z_B'), m=e3.get('m'),
                e3a=np.asarray(a, float).reshape(-1, 3),
                e3b=None if not b else np.array([b['q_Z'], b['u_q_Z'], b.get('u_q_Z_ohne_T', np.nan)], float),
                t=e3.get('t_unsicherheit'))


def _e3_fehlt(tb):
    """Grund, aus dem AP-12 keine E3-Auswertung liefert (statt eines stillen Fehlens im Befund)."""
    n5 = tb.get('nr5') or {}
    if n5.get('T') is None:
        return 'keine E3-Auswertung: T(kω) fehlt in Teil B nr5 (Zellanteile aus P0.1 nicht bestimmbar)'
    if n5.get('unsicherheit') is None:
        return ('keine E3-Auswertung: Laststellen aus P0.1 nicht bestimmbar oder keine auswertbare '
                'Schnittkonfiguration')
    return 'keine E3-Auswertung: keine auswertbare Schnittkonfiguration'


def kurzbefund(erg, tb, seed, ablauf=None):
    """Kompakter, wahrheitsfreier Befund einer Kampagne (nur aus dem Ergebnis von AP-12 und Teil B; ablauf: Bericht des
    zustandsbehafteten Ablaufs, kompakt übernommen)."""
    H1, H1Z, H2, H3, H4 = (erg[k] for k in HYPOTHESEN)
    b = H1['bias']
    r0, v0 = _roh(H1['tests0'], b['b0'])
    r1, v1 = _roh(H1['tests1'], b['b1'])
    n4 = tb['nr4']
    bz0 = np.zeros((r0.shape[0], 3)) if n4.get('bias0_zellen') is None else np.asarray(n4['bias0_zellen'], float)
    bz1 = np.zeros((r0.shape[0], 3)) if n4.get('bias1_zellen') is None else np.asarray(n4['bias1_zellen'], float)
    rz0, vz0 = _roh(H1Z['tests0'], bz0)
    rz1, vz1 = _roh(H1Z['tests1'], bz1)
    iv = {k: (v['yhat0'], v['yhat1']) for k, v in (H2.get('intervalle') or {}).items()}
    g = erg['gueltigkeit']
    regelzahl = {}
    for gr in g['gruende'].values():
        for x in (gr if isinstance(gr, list) else [gr]):
            regelzahl[x] = regelzahl.get(x, 0) + 1
    zu = erg.get('zuordnung') or {}
    e3 = erg.get('E3') or {}
    return dict(
        seed=int(seed), seed_bootstrap=erg['herkunft']['seed'], profil=erg['herkunft']['profil']['profil_id'],
        laufzeit_s=erg['herkunft'].get('laufzeit_s'),
        H1=dict(ausgang=H1['ausgang'], grund=H1['grund'], zusaetze=list(H1['zusaetze']),
                abweichung=H1['abweichung_nachgewiesen'], drift=bool(H1['drift']), vollstaendig=H1['vollstaendig'],
                c=H1['c'], max_abs_z0=H1['max_abs_z0'], max_abs_z1=H1['max_abs_z1']),
        H1_sens={k: v['ausgang'] for k, v in erg['H1_sensitivitaet'].items()},
        H1Z=dict(ausgang=H1Z['ausgang'], grund=H1Z['grund'], c=H1Z['c'], max_abs_z0=H1Z['max_abs_z0']),
        H2=dict(ausgang=H2['ausgang'], grund=H2.get('grund'), zusaetze=list(H2.get('zusaetze', [])),
                delta_phi0=H2.get('delta_phi0'), delta_phi1=H2.get('delta_phi1'), intervalle=iv,
                gewaehlt=H2.get('intervall_gewaehlt'), W_ids=list((H2.get('W') or {}).get('W_ids') or []),
                punktmasse0=H2.get('punktmasse0'), punktmasse1=H2.get('punktmasse1')),
        H3=dict(ausgang=H3['ausgang'], grund=H3.get('grund'), zusaetze=list(H3.get('zusaetze', [])),
                kennzeichnung=H3.get('kennzeichnung')),
        H4=dict(ausgang=H4['ausgang'], grund=H4.get('grund'), V=H4.get('V')),
        H0=dict(aussage=erg['H0'].get('aussage'), lage=erg['H0'].get('lage'),
                g1=len(erg['H0'].get('g1_verletzt', []))),
        zuordnung=dict(ergebnis=zu.get('ergebnis'), klasse=zu.get('klasse'), status=zu.get('status')) if zu else None,
        E3=_e3_kurz(e3) if e3 else None, E3_grund=None if e3 else _e3_fehlt(tb),
        gueltigkeit=dict(n_laeufe=g['n_laeufe'], n_ungueltig=g['n_ungueltig'], regeln=regelzahl,
                         S2=len(g['abbruch']['S2']), S4=len(g['abbruch']['S4']),
                         S1_kandidaten=len(g['abbruch']['S1_kandidaten'])),
        n_auswertbar=erg['n_auswertbar'], yhat1_gueltig=erg['yhat1_gueltig'],
        ablauf=None if ablauf is None else abl.kurz(ablauf),
        teil_b=dict(Delta=np.asarray(n4['Delta'], float), Delta_rel=np.asarray(n4['Delta_rel'], float),
                    D=np.asarray(n4['D'], float) if n4.get('D') is not None else None,
                    bindung=(tb['nr2'].get('phase0_bindung') or {}).get('modus', 'historisch'),
                    k_bindung=(tb['nr2'].get('phase0_bindung') or {}).get('k'),
                    arbeitspunkt=(tb['nr2'].get('arbeitspunkt') or {}).get('status')),
        felder=dict(r0=r0, v0=v0, r1=r1, v1=v1, rz0=rz0, vz0=vz0, rz1=rz1, vz1=vz1,
                    u0=np.asarray(H1['tests0']['u'], float), nu0=np.asarray(H1['tests0']['nu'], float),
                    z0=np.asarray(H1['tests0']['z'], float), z1=np.asarray(H1['tests1']['z'], float),
                    zz0=np.asarray(H1Z['tests0']['z'], float)))


def _eine(auftrag):
    sid, stufe, prof, plan, seed, w8, n_min, rausch, staerke, k_max, verfahren = auftrag
    r = kette.kette(sid, stufe, prof, plan=plan, seed=seed, werkzeug8=w8, n_min=n_min, mit_wahrheit=False,
                    rausch=rausch, staerke=staerke, k_max=k_max, verfahren=verfahren)
    return kurzbefund(r['ergebnis'], r['teil_b'], seed, r.get('ablauf'))


THREAD_VARIABLEN = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')


def _parallel(auftraege, prozesse, fn=None):
    """Arbeitsprozesse mit je einem BLAS-Thread (spawn; die Umgebung gilt beim Import von NumPy im Kind). fn: Funktion
    je Auftrag auf Modulebene (Vorgabe: eine Kampagne der Kette mit Kurzbefund)."""
    alt = {v: os.environ.get(v) for v in THREAD_VARIABLEN}
    os.environ.update({v: '1' for v in THREAD_VARIABLEN})
    try:
        with cf.ProcessPoolExecutor(prozesse, mp_context=mp.get_context('spawn')) as ex:
            return list(ex.map(fn or _eine, auftraege, chunksize=1))
    finally:
        for v, w in alt.items():
            if w is None:
                os.environ.pop(v, None)
            else:
                os.environ[v] = w


def wahrheit_kurz(sid, stufe, plan, staerke=None, k_max=None):
    """Wahrheit des Szenariopunkts (rauschfrei, unabhängig von der Kampagne) für die Bewertung."""
    m = szenarien.modell(sid, stufe, plan=plan, staerke=staerke, k_max=k_max)
    w, felder = wahrheit.berechne(m, kp.schnitt_konfigurationen(m.plan))
    out = {k: w.get(k) for k in ('klasse', 'r_max_rel_beide', 'r_max_rel_yhat0', 'r_max_rel_yhat1',
                                 'klasse_sens_faktor_0_1', 'klasse_sens_fassung_A', 'r_max_rel_je_groesse',
                                 'zellminimum_min_N', 'schnitt', 'Delta_B')}
    out['F'] = {k: np.asarray(felder[k], float) for k in ('F_mess', 'F_yhat0', 'F_yhat1') if k in felder}
    out['staerke'] = m.staerke
    return out


def ausfuehren(sid, stufe, profil, n, seed_basis, rolle='pruefung', plan=None, n_min=None, werkzeug8=None, rausch=None,
               staerke=None, prozesse=1, fortschritt=None, k_max=None, verfahren=None):
    """n Kampagnen des Szenariopunkts; Rückgabe dict(meta, befunde, wahrheit). verfahren: Bindung der Phase-0-Größen
    und Ablauf der Phase 1 (Vorgabe verfahren.STANDARD), in der Herkunft vermerkt."""
    plan = kp.Plan() if plan is None else plan
    verfahren = vf.oder_standard(verfahren)
    seeds = [kampagnen_seed(seed_basis, rolle, sid, stufe, i) for i in range(n)]
    auftraege = [(sid, stufe, profil, plan, s, werkzeug8, n_min, rausch, staerke, k_max, verfahren) for s in seeds]
    t = time.perf_counter()
    if prozesse > 1:
        befunde = _parallel(auftraege, prozesse)
    else:
        befunde = []
        for i, a in enumerate(auftraege):
            befunde.append(_eine(a))
            if fortschritt:
                fortschritt(i + 1, n)
    dauer = time.perf_counter() - t
    meta = dict(szenario=sid, stufe=stufe, profil=profil.id, profil_sha256=profil.sha256(), n=n,
                seed_basis=int(seed_basis), rolle=rolle, seeds=seeds, plan=_plan_dict(plan), n_min=n_min,
                werkzeug8_herkunft=None if werkzeug8 is None else werkzeug8.get('c_H1_herkunft'),
                werkzeug8=('TESTVORGABE' if werkzeug8 is None else 'übergeben'),
                normative_kampagnenzahl=regeln.NORMATIVE_ZAHLEN['kampagnen_pruefung'],
                reduziert=bool(n < regeln.NORMATIVE_ZAHLEN['kampagnen_pruefung']) or profil.reduziert,
                laufzeit_s=round(dauer, 2), prozesse=prozesse, code_version=formate.code_version())
    meta.update(k_max=k_max, rauschmodell=None if rausch is None else rausch.name, staerke=staerke,
                verfahren=verfahren.kennung())
    return dict(meta=meta, befunde=befunde, wahrheit=wahrheit_kurz(sid, stufe, plan, staerke, k_max))


def _plan_dict(plan):
    from dataclasses import asdict
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in kp.plan_dict(plan).items()}


# ── Raten ────────────────────────────────────────────────────────────────────────────────────────────
def _etikett(wert, status):
    """Zählbezeichnung einer Kontrolle: Bewertung bzw. Ergebnis, sonst der Status ohne Begründung (z. B. „nicht
    auswertbar“, „nur beschreibend“, „nur numerisch“)."""
    if wert is not None:
        return str(wert)
    return (status or 'ohne Bewertung').split(':', 1)[0]


def raten(lauf):
    """Raten der Ausgänge, Gründe und Zusätze je Hypothese, Gültigkeit und Kontrollen (Zähler, Nenner, MC-Fehler)."""
    m = lauf['meta']
    bf = lauf['befunde']
    kw = dict(szenario=m['szenario'], stufe=m['stufe'], profil=m['profil'])
    out = dict(meta=m, wahrheit=dict(klasse=lauf['wahrheit']['klasse'],
                                     r_max_rel=lauf['wahrheit']['r_max_rel_beide']), raten={})
    R = out['raten']
    n = len(bf)
    for h in HYPOTHESEN:
        for a in AUSGAENGE:
            R[f'{h}: {a}'] = metriken.rate(sum(b[h]['ausgang'] == a for b in bf), n, f'P({h} {a})', **kw)
        gr = sorted({b[h].get('grund') for b in bf if b[h].get('grund')})
        for g in gr:
            R[f'{h}: nicht entscheidbar, Grund {g}'] = metriken.rate(
                sum(b[h].get('grund') == g for b in bf), n, f'P({h} nicht entscheidbar, Grund {g})', **kw)
    for h in ('H1', 'H2', 'H3'):
        zs = sorted({z for b in bf for z in b[h].get('zusaetze', [])})
        for z in zs:
            R[f'{h}: Zusatz {z}'] = metriken.rate(sum(z in b[h]['zusaetze'] for b in bf), n, f'P({h} Zusatz „{z}“)',
                                                  **kw)
    for s in sorted({k for b in bf for k in b['H1_sens']}):
        for a in AUSGAENGE:
            R[f'H1 Sensitivität {s}: {a}'] = metriken.rate(sum(b['H1_sens'][s] == a for b in bf), n,
                                                            f'P(H1 {a} | Sensitivität {s})', **kw)
    R['H1 und H2 bestätigt'] = metriken.rate(sum(b['H1']['ausgang'] == 'bestätigt' and b['H2']['ausgang'] ==
                                                 'bestätigt' for b in bf), n, 'P(H1 und H2 bestätigt)', **kw)
    R['mindestens ein |z⁰| > c (H1)'] = metriken.rate(
        sum(b['H1']['max_abs_z0'] is not None and b['H1']['c'] is not None and b['H1']['max_abs_z0'] > b['H1']['c']
            for b in bf), n, 'Anteil mit max|z⁰| > c (H1)', **kw)
    zus = [_etikett(b['zuordnung']['ergebnis'], b['zuordnung'].get('status')) for b in bf if b['zuordnung']]
    for e in sorted(set(zus)):
        R[f'Zuordnung: {e}'] = metriken.rate(zus.count(e), len(zus), f'P(Zuordnung „{e}“)', **kw)
    e3 = [_etikett(b['E3']['bewertung'], b['E3'].get('status')) for b in bf if b['E3']]
    for e in sorted(set(e3)):
        R[f'E3: {e}'] = metriken.rate(e3.count(e), len(e3), f'P(E3 „{e}“)', **kw)
    nl = sum(b['gueltigkeit']['n_laeufe'] for b in bf)
    regeln_alle = sorted({g for b in bf for g in b['gueltigkeit']['regeln']})
    out['gueltigkeit'] = {g: metriken.rate(sum(b['gueltigkeit']['regeln'].get(g, 0) for b in bf), nl,
                                           f'Anteil der Phase-1-Läufe ungültig durch {g}', **kw) for g in regeln_alle}
    out['abbruch'] = {s: metriken.rate(sum(b['gueltigkeit'][s] > 0 for b in bf), n, f'Anteil der Kampagnen mit {s}',
                                       **kw) for s in ('S2', 'S4', 'S1_kandidaten')}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)                  # Szenarien ohne auswertbare Tests
        out['u_c_median'] = dict(zip(['F_min', 'Re N1', 'Im N1', 'Re N2', 'Im N2', 'Re N3', 'Im N3'],
                                     [float(x) for x in np.nanmedian(np.stack([b['felder']['u0'] for b in bf]),
                                                                     axis=(0, 1))])) if bf else None
    out['laufzeit_je_kampagne_s'] = metriken.mittel([b['laufzeit_s'] for b in bf if b['laufzeit_s'] is not None])
    ab = [b['ablauf'] for b in bf if b.get('ablauf')]
    if ab:
        out['ablauf'] = ablauf_raten(ab, **kw)
    return out


def ablauf_raten(ab, **kw):
    """Ablauf über die Kampagnen: angehaltene/abgebrochene Kampagnen (nicht abgeschlossen), zusätzliche Läufe und
    realisierte gegen geplante Messzeit (Laufzahl × T_Lauf), ausgeschöpfte Grenzen."""
    n = len(ab)
    zus = [a['laufzahl']['zusaetzlich'] for a in ab]
    real = [a['messzeit_s']['realisiert_laeufe'] for a in ab]
    return dict(n=n, nicht_abgeschlossen=metriken.rate(sum(a['status'] != 'abgeschlossen' for a in ab), n,
                                                       'Anteil nicht abgeschlossener Kampagnen (Halt/Abbruch)', **kw),
                halt_regeln={r: sum(a['halt'] == r for a in ab) for r in sorted({a['halt'] for a in ab if a['halt']})},
                zusaetzliche_laeufe=dict(mittel=float(np.mean(zus)), max=int(np.max(zus))),
                messzeit_s=dict(geplant=float(ab[0]['messzeit_s']['geplant_laeufe']), realisiert_mittel=float(np.mean(real)),
                                realisiert_max=float(np.max(real))),
                grenzen=sum(a['grenzen'] for a in ab))


# ── Ausgabe ──────────────────────────────────────────────────────────────────────────────────────────
def schreibe(verzeichnis, lauf, kennung=None):
    """JSON+NPZ des Laufs (Befunde mit Feldern) und eine CSV-Tabelle je Kampagne; Rückgabe der Pfade."""
    os.makedirs(verzeichnis, exist_ok=True)
    m = lauf['meta']
    kennung = kennung or formate.synth_kennung('HARNESS', m['szenario'], m['stufe'], m['rolle'], m['seed_basis'])
    p = os.path.join(verzeichnis, f'kampagnen_{m["szenario"]}_{m["stufe"]}_{m["rolle"]}')
    formate.schreibe_objekt(p, formate.kopf('bewertung', kennung), lauf)
    with open(p + '.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['kampagne', 'seed', 'H1', 'H1_grund', 'H1_zusaetze', 'max_abs_z0', 'c', 'H1Z', 'H2', 'H2_grund',
                    'delta_phi0', 'delta_phi1', 'H3', 'H4', 'E3', 'Zuordnung', 'ungueltig', 'auswertbar'])
        for i, b in enumerate(lauf['befunde']):
            w.writerow([i, b['seed'], b['H1']['ausgang'], b['H1']['grund'] or '', '; '.join(b['H1']['zusaetze']),
                        b['H1']['max_abs_z0'], b['H1']['c'], b['H1Z']['ausgang'], b['H2']['ausgang'],
                        b['H2']['grund'] or '', b['H2']['delta_phi0'], b['H2']['delta_phi1'], b['H3']['ausgang'],
                        b['H4']['ausgang'], (b['E3'] or {}).get('bewertung', ''),
                        (b['zuordnung'] or {}).get('ergebnis', ''), b['gueltigkeit']['n_ungueltig'],
                        b['n_auswertbar']])
    return dict(objekt=p, csv=p + '.csv')
