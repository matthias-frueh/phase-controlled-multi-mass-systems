"""Untersuchung der Kennwerte (13.11.2026), Zusatzmessungen: kleine Testkampagne, Ebene Z, Strukturgenerator.

Aufruf aus dem Wurzelverzeichnis des Repositorys:

    OPENBLAS_CORETYPE=HASWELL OPENBLAS_NUM_THREADS=1 \\
        python3 docs/kennwerte_untersuchung_2026-11-13/zusatz.py messen /tmp/zusatz/Haswell_1.json
    python3 docs/kennwerte_untersuchung_2026-11-13/zusatz.py vergleichen /tmp/zusatz SkylakeX_1

messen legt für die Umgebung dieses Prozesses ab (JSON, nicht im Repository):
- kleine Kampagne der Ebene H wie in tests/test_herkunft.py (N01-V1G0, Seed 7): Prüfsumme des Herkunftsnachweises,
  Prüfsumme der Datenfelder (alte Bindung), Kennwerte der Phase-0-Läufe;
- Kampagne der Ebene Z wie in tests/test_herkunft.py (N01-A4, Seed 13, 56 Rohdateien → Stufe 1): dasselbe;
- Strukturgenerator wie in tests/test_d_planung_phase0.py (Struktur aus P0.8 der Kampagne N01-A4, Seed 5):
  Prüfsummen von Modellquelle, Modellbeschreibung, Struktur, Rauschparametern und Kalibrierobjekt, Kennwerte der
  Struktur; dazu, ob die Prüfsummen eine Prozessgrenze (pickle) überstehen.
vergleichen schreibt zusatz.json neben dieses Skript: je Umgebung gegen die Bezugsumgebung, ob die Prüfsummen gleich
sind und wie weit die Kennwerte die Toleranz auslasten.
"""
import glob
import json
import os
import pickle
import sys
import tempfile

sys.path.insert(0, 'code')
import numpy as np                                                       # noqa: E402

from pcmms_auswertung import formate, herkunft, kennwerte as kw, pilot, regeln, zufall    # noqa: E402
from pcmms_auswertung.generator import kampagne as kp, szenarien          # noqa: E402
from pcmms_auswertung.harness import kette, planung, pruefsatz as ps      # noqa: E402

HIER = os.path.dirname(os.path.abspath(__file__))
ZEIT = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)


def _phase0(t0):
    return dict(n=len(t0), nachweis=herkunft.sha256(herkunft.nachweis(t0)), datenfelder=pilot.daten_sha256(t0),
                kennwerte=pilot.phase0_kennwerte(t0)['felder'])


def ebene_h():
    tab = kette.kampagne_erzeugen('N01-V1G0', 'L1', kp.Plan(n0=20, n_pilot=20, n_bloecke=2), 7)[2]
    return _phase0(tab.auswahl(tab.spalte('phase', int) == 0))


def ebene_z():
    sid, seed = 'N01-A4', 13
    m = szenarien.modell(sid, 'L1', plan=kp.Plan(n0=10, n_pilot=6, n_bloecke=2, ref_min_p0=8, n_zyklen=40))
    laeufe = kp.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    _, kwahr, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
    kwz = dict(nullpunkt_adc=kwahr['p01']['nullpunkt_adc'],
               empfindlichkeit_N_je_adc=kwahr['p01']['empfindlichkeit_N_je_adc'])
    with tempfile.TemporaryDirectory() as d:
        messung = kette.MessungZ(m, laeufe, seed, d, kwz, kal, formate.synth_kennung('PROBE', 'Z'))
        return _phase0(messung.phase0(laeufe))


def strukturgenerator():
    profil = regeln.profil('ENTW-2026-11').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=200)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=24)
    m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', 'L1', plan, 5)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m, 5)
    t0 = tab.auswahl(tab.spalte('phase', int) == 0).sortiert()
    s = pilot.satz_fuer_plan(t0, kal, profil, m.system.f, 9, 5)
    ung = set(s['gueltigkeit']['gruende'])
    T_lauf = 2.0 + 2.0 + 3.0 + 10.0 + 1.0
    aufruf = dict(k=9, N_z=100, T_a=10.0, T_e=3.0, T_lauf=T_lauf, zeit=dict(ZEIT), s_q=s['streuungen'],
                  kovarianzen=s['kovarianzen'], p_hat=s['p_hat'], n_max=pilot.n_max(T_lauf, s['p_hat'], ZEIT),
                  tabelle=t0, gueltig=np.array([x['lauf_id'] not in ung for x in t0.koepfe]), kal=kal, f=m.system.f,
                  laufgroessen=s['laufgroessen'], bindung=s['bindung'])
    q, _ = planung.quelle_aus_aufruf(aufruf, 'punkt', profil=profil)
    b = q.modell(plan).beschreibung()
    q2 = pickle.loads(pickle.dumps(q))
    return dict(modellquelle=q.kennung()['sha256'], modell=formate.sha256_json(b), struktur=b['struktur']['sha256'],
                rauschen=formate.sha256_json(b['rauschen']), kalibrierung=formate.sha256_json(kal),
                ueber_prozessgrenze_gleich=bool(q2.kennung()['sha256'] == q.kennung()['sha256']
                                                and formate.sha256_json(q2.modell(plan).beschreibung())
                                                == formate.sha256_json(b)),
                kennwerte=kw.felder(dict(Nz=q.struktur.Nz, F0=q.struktur.F0)))


def messen(ziel):
    umg = ps.umgebung()
    from numpy._core._multiarray_umath import __cpu_features__ as merkmale
    umg['numpy_avx512'] = bool(merkmale.get('X86_V4', merkmale.get('AVX512F')))
    out = dict(umgebung=umg, ebene_h=ebene_h(), ebene_z=ebene_z(), strukturgenerator=strukturgenerator())
    with open(ziel, 'w', encoding='utf-8') as f:
        f.write(formate.json_text(out))
    print(ziel, umg['blas'], umg['numpy_avx512'])


def vergleichen(verzeichnis, bezug):
    D = {os.path.basename(p)[:-5]: json.load(open(p, encoding='utf-8'))
         for p in sorted(glob.glob(os.path.join(verzeichnis, '*.json')))}
    ref = D[bezug]
    out = dict(beschreibung='Zusatzmessungen (zusatz.py): Prüfsummen und Kennwerte je Umgebung gegen die '
                            'Bezugsumgebung; Toleranz der Kennwerte ' + json.dumps(kw.toleranz(), ensure_ascii=False),
               bezug=bezug, umgebungen={n: d['umgebung'] for n, d in D.items()}, pruefsummen={}, vergleich={})
    for n, d in D.items():
        out['pruefsummen'][n] = dict(
            ebene_h={x: d['ebene_h'][x][:12] for x in ('nachweis', 'datenfelder')},
            ebene_z={x: d['ebene_z'][x][:12] for x in ('nachweis', 'datenfelder')},
            strukturgenerator={x: d['strukturgenerator'][x][:12] for x in ('modellquelle', 'modell', 'struktur',
                                                                            'rauschen', 'kalibrierung')},
            ueber_prozessgrenze_gleich=d['strukturgenerator']['ueber_prozessgrenze_gleich'])
        if n == bezug:
            continue
        zeile = {}
        for teil in ('ebene_h', 'ebene_z', 'strukturgenerator'):
            v = kw.vergleich_felder(ref[teil]['kennwerte'], d[teil]['kennwerte'])
            zeile[teil] = dict(innerhalb_der_toleranz=v['gleich'], kennwerte_gleich=v['kennwerte_gleich'],
                               auslastung=v['auslastung'], feld_auslastung=v['feld_auslastung'])
            if teil != 'strukturgenerator':
                zeile[teil].update(nachweis_gleich=ref[teil]['nachweis'] == d[teil]['nachweis'],
                                   datenfelder_gleich=ref[teil]['datenfelder'] == d[teil]['datenfelder'])
            else:
                zeile[teil].update(modell_gleich=ref[teil]['modell'] == d[teil]['modell'])
        out['vergleich'][n] = zeile
        print(n, json.dumps(zeile, ensure_ascii=False))
    with open(os.path.join(HIER, 'zusatz.json'), 'w', encoding='utf-8') as f:
        f.write(ps._einzeilig(out) + '\n')                               # kompakter JSON-Text


if __name__ == '__main__':
    if sys.argv[1] == 'messen':
        messen(sys.argv[2])
    else:
        vergleichen(sys.argv[2], sys.argv[3])
