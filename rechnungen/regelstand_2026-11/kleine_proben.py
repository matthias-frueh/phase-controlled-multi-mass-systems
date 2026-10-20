"""Kleine Proben des Regelstands 2026-11 (Auftrag vom 20.10.2026, Abschnitte 1 und 10.2).

Teile (python3 rechnungen/regelstand_2026-11/kleine_proben.py <teil> [--ausgabe DIR]):
  g4   gepaarte G4-Diagnose auf denselben Läufen: Regel je Laufart (historisch), B+ (Standard) und D (Diagnosemodus)
       an N01-A4, N01-V1G0, N01-V1G60h; Ausschlüsse je Konfiguration (flache Punkte S100/S140, steile und Knickpunkte
       S118–S122), Pilotmischung (s_P, s̄_P, σ_W) und Trendfälle (Amplitudentrend 0,5 % und 1 % im letzten Fünftel,
       exakt über F_min − ⟨N⟩ ∝ Amplitude). Statischer Laufplan der Phase 1 (G4 hängt nicht vom Ablauf ab).
  e2e  End-to-End-Auswahl mit Ablauf ablauf-4: Nullkampagnen A4 und V1-G0, Kopplungsfall A04-R4, Halt mit
       erfolgreicher Wiederaufnahme und mit endgültigem Ende, Weg über Ebene Z/Stufe 1.
Feste Seeds, kleine Zahlen, Laufzeit je Teil im Ergebnis. Die Zahlen sind Funktionsnachweise und Beispiele, keine
Raten: Sie bestätigen weder eine Fehlausschlussrate noch eine Power oder Vollständigkeit.
"""
import argparse
import json
import os
import sys
import time

THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')
for _v in THREADS:                                  # ein BLAS-Thread je Prozess; wirkt nur vor dem Import von NumPy
    os.environ.setdefault(_v, '1')

import numpy as np  # noqa: E402

WURZEL = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(WURZEL, 'code'))

from pcmms_auswertung import auswertung, formate, gueltigkeit, konventionen as kv, regeln, verfahren as vf  # noqa
from pcmms_auswertung import zusammenfassung as zf  # noqa: E402
from pcmms_auswertung.generator import kampagne as kp, szenarien  # noqa: E402
from pcmms_auswertung.harness import kette  # noqa: E402

RED = dict(bootstrap_B=100, h3_mc=100, eps_ctrl_datensaetze=200)
PROFIL = regeln.profil('ENTW-2026-11').mit_reduktion(**RED)
SYSTEME = ('N01-A4', 'N01-V1G0', 'N01-V1G60h')
SEEDS_G4 = (101, 102, 103)
PLAN_G4 = dict(n0=20, n_pilot=20, n_bloecke=8)
FLACH, STEIL = ('S100', 'S140'), ('S118', 'S120', 'S122')
TRENDS = (0.005, 0.01)


def _schwellen(tb, modus):
    p = PROFIL if modus == 'b_plus' else PROFIL.mit_diagnose(g4__verfahren=modus)
    sw = auswertung._schwellen(tb, p)
    if modus == 'je_laufart':
        sw.g4_lj = None
    return sw


def g4_probe():
    t0 = time.perf_counter()
    out = dict(profil=PROFIL.id, plan=PLAN_G4, seeds=list(SEEDS_G4), systeme={})
    for sid in SYSTEME:
        zaehl = {m: {} for m in ('je_laufart', 'b_plus', 'd')}
        trend = {m: {e: {'flach': [0, 0], 'steil': [0, 0]} for e in TRENDS} for m in zaehl}
        n_k = {}
        pil = []
        for seed in SEEDS_G4:
            plan = kp.plan_aus_dict(dict(PLAN_G4, p0_anordnung='p07'))
            m, laeufe, tab = kette.kampagne_erzeugen(sid, 'L1', plan, seed)
            _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
            t0k = tab.auswahl(tab.spalte('phase', int) == 0)
            tb, _ = kette.teil_b_erzeugen(t0k, kal, m, PROFIL, kette.testvorgabe_werkzeug8(), seed, 6)
            g = tb['nr2']['g4']
            pil.append(dict(seed=seed, s_P=g['b_plus']['s_P'], sbar_P=g['b_plus']['sbar_P'],
                            sigma_W=g['b_plus']['sigma_W'], sigma_P_F=g['b_plus']['sigma_P_F'],
                            sigma_D=(g['d'] or {}).get('sigma_D'),
                            T_F={c: g['b_plus']['schwellen_F'][c] for c in FLACH + STEIL},
                            s={c: g['b_plus']['s'][c] for c in FLACH + STEIL}))
            t1 = tab.auswahl((tab.spalte('phase', int) == 1) & (tab.spalte('laufart', object) == 'K')
                             & (tab.spalte('einstellung', int) == 1))
            DN, DF = gueltigkeit.fuenftel_differenzen(t1, tb['nr2']['k_max'])
            F_letzt = kv.fmin_rel(t1.daten['fuenftel_Nk'][:, 1, :tb['nr2']['k_max']])
            ids = t1.konfig_ids()
            for c in ids:
                n_k[c] = n_k.get(c, 0) + 1
            for modus in zaehl:
                sw = _schwellen(tb, modus)
                pr = gueltigkeit.pruefe(t1, sw, regeln=('G4',))
                for c, v in zip(ids, pr['regeln']['G4']):
                    zaehl[modus][c] = zaehl[modus].get(c, 0) + int(v is True)
                for e in TRENDS:                              # Amplitudentrend ε im letzten Fünftel
                    t2 = zf.LaufTabelle(t1.koepfe, dict(t1.daten))
                    t2.daten['fuenftel_Nk'] = t1.daten['fuenftel_Nk'].copy()
                    t2.daten['fuenftel_Nk'][:, 1] *= (1 + e)
                    t2.daten['fuenftel_N_mittel'] = t1.daten['fuenftel_N_mittel'].copy()
                    pt = gueltigkeit.pruefe(t2, sw, regeln=('G4',))
                    for c, v in zip(ids, pt['regeln']['G4']):
                        art = 'flach' if c in FLACH else ('steil' if c in STEIL else None)
                        if art:
                            trend[modus][e][art][0] += int(v is True)
                            trend[modus][e][art][1] += 1
        out['systeme'][sid] = dict(
            laeufe_je_konfiguration=n_k, g4_ausschluesse=zaehl, piloten=pil,
            flach_steil={m: dict(flach=sum(zaehl[m].get(c, 0) for c in FLACH),
                                 steil=sum(zaehl[m].get(c, 0) for c in STEIL),
                                 alle=sum(zaehl[m].values()), n=sum(n_k.values())) for m in zaehl},
            trend={m: {str(e): v for e, v in trend[m].items()} for m in trend})
    out['laufzeit_s'] = round(time.perf_counter() - t0, 1)
    out['lesart'] = ('Funktionsnachweis an 3 Kampagnen je System mit 8 Blöcken; Zähler je Konfiguration, keine Raten. '
                     'Trend: Anteil erkannter Läufe (Zähler, Nenner) bei ε im letzten Fünftel.')
    return out


def _kurz(r):
    e = r['ergebnis']
    a = r.get('ablauf') or {}
    w = a.get('harness_wiederaufnahme') or {}
    g = e['gueltigkeit']
    return dict(H1=e['H1']['ausgang'], H1_grund=e['H1'].get('grund'), H2=e['H2']['ausgang'], H3=e['H3']['ausgang'],
                H4=e['H4']['ausgang'], E3=(e.get('E3') or {}).get('bewertung'),
                E3_stufen={k: v.get('stufe') for k, v in ((e.get('E3') or {}).get('pruefgroessen') or {}).items()},
                g4_ungueltig=sum('G4' in (x if isinstance(x, list) else [x]) for x in g['gruende'].values()),
                ablauf_status=a.get('status'), halte=[h['regel'] for h in a.get('halte', [])],
                wiederaufnahmen=w.get('wiederaufnahmen'), endgueltig=w.get('grund'),
                bezugswechsel=len(a.get('bezugswechsel') or []), zusatzlaeufe=a.get('zusatzlaeufe'),
                laufzeit_s=r['laufzeit_s'])


def e2e_probe(ausgabe):
    t0 = time.perf_counter()
    plan = kp.plan_aus_dict(dict(n0=20, n_pilot=20, n_bloecke=8, p0_anordnung='p07'))
    faelle = [('N01-A4', 201), ('N01-V1G0', 202), ('A04-R4', 203), ('S02-kontrolllauf', 204), ('S01a-liftoff', 205)]
    out = dict(profil=PROFIL.id, plan=kp.plan_dict(plan), faelle={})
    for sid, seed in faelle:
        r = kette.kette(sid, 'L1', PROFIL, plan=plan, seed=seed, n_min=6, mit_wahrheit=False, verfahren=vf.ZUSTAND)
        out['faelle'][f'{sid}/{seed}'] = _kurz(r)
    # Weg über Ebene Z/Stufe 1 (Rohdaten in eine frische Struktur, Stufe 1, gleicher Ablauf)
    vz = os.path.join(ausgabe, 'ebene_z')
    os.makedirs(vz, exist_ok=True)
    rz = kette.kampagne_ablauf('N01-A4', 'L1', kp.plan_aus_dict(dict(n0=20, n_pilot=20, n_bloecke=3,
                                                                     p0_anordnung='p07')),
                               206, PROFIL, n_min=2, ebene='Z', verzeichnis=vz)
    tab = kette.ablauf_tabelle(rz)
    auswertung.datenlage(tab, rz['teil_b'], PROFIL)
    out['ebene_z'] = dict(status=rz['ablauf'].status, versuche=len(rz['ablauf'].z['versuche']),
                          fuenftelzeiger=zf.hat_fuenftelzeiger(tab.daten),
                          verarbeitung=zf.verarbeitungsstand(tab.koepfe)['versionen'])
    out['laufzeit_s'] = round(time.perf_counter() - t0, 1)
    out['lesart'] = 'je Fall eine Kampagne; Ausgänge sind Beispiele, keine Raten'
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('teil', choices=('g4', 'e2e'))
    ap.add_argument('--ausgabe', default=os.path.join(WURZEL, 'rechnungen', 'regelstand_2026-11'))
    a = ap.parse_args(argv)
    r = g4_probe() if a.teil == 'g4' else e2e_probe(a.ausgabe)
    r.update(code_version=formate.code_version(), umgebung=dict(python=sys.version.split()[0], numpy=np.__version__,
                                                                threads={v: os.environ.get(v) for v in THREADS}))
    pfad = os.path.join(a.ausgabe, f'probe_{a.teil}.json')
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(formate._json_wert(r), f, ensure_ascii=False, indent=1)
    print(pfad, r['laufzeit_s'], 's')


if __name__ == '__main__':
    main()
