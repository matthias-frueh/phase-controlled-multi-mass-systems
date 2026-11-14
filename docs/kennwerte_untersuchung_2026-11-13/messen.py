"""Untersuchung der Kennwerte (13.11.2026), Schritt 1: Rohwerte unter der Umgebung dieses Prozesses ablegen.

Aufruf aus dem Wurzelverzeichnis des Repositorys, je Umgebung einmal:

    OPENBLAS_CORETYPE=HASWELL OPENBLAS_NUM_THREADS=1 python3 docs/kennwerte_untersuchung_2026-11-13/messen.py \\
        /tmp/kennwerte/HASWELL_1.pkl [Threads zur Laufzeit]

Abgelegt werden (pickle, nicht im Repository; je Umgebung rund 90 MB):
- die Felder der drei Prüfsätze (Laufzusammenfassungen und P0-Messung der sieben Prüfkampagnen, Tabellen der zehn
  Ablauf-Prüfkampagnen), ihre Prüfsummen und die exakten Teile (Köpfe, Entscheidungen, Ziehungen, Inhalt);
- die Kurzbefunde dreier Kampagnen wie in tests/test_ap13_harness.py::test_kampagnen_unabhaengig_von_der_prozesszahl,
  im eigenen Prozess gerechnet;
- die Umgebung (harness.pruefsatz.umgebung; mit threadpoolctl auch Rechenkern und Thread-Zahl).

Das optionale zweite Argument setzt die Zahl der BLAS-Threads zur Laufzeit (threadpoolctl). So lassen sich mehr
Threads einstellen, als der Rechner Kerne hat; über die Umgebungsvariable begrenzt OpenBLAS auf die Kernzahl.
"""
import pickle
import sys

sys.path.insert(0, 'code')
import numpy as np                                                       # noqa: E402

from pcmms_auswertung import formate, regeln, zufall                     # noqa: E402
from pcmms_auswertung.generator import kalibrierdaten, kampagne as kp, szenarien    # noqa: E402
from pcmms_auswertung.harness import ablauf_pruefsatz as ap, kampagnen, kette, pruefsatz as ps    # noqa: E402


def pruefsaetze():
    out = dict(testdaten={}, ablauf={}, katalog=ps.katalog_hash())
    plan = kp.plan_aus_dict(ps.PRUEFPLAN)
    for sid, stufe, seed in ps.PRUEFKAMPAGNEN:
        m, laeufe, tab = kette.kampagne_erzeugen(sid, stufe, plan, seed)
        kw = {a: b for a, b in szenarien.KATALOG[sid].kalibrierung}
        mes, _ = kalibrierdaten.p0_messungen(m.system, zufall.strom(seed, 'p0'), p01=kw.get('p01'), p04=kw.get('p04'),
                                             p05=kw.get('p05'))
        sk, felder = formate.zerlege(mes)
        out['testdaten'][f'{sid}/{stufe}/{seed}'] = dict(
            daten={k: np.array(v) for k, v in tab.daten.items()}, p0_felder={k: np.array(v) for k, v in felder.items()},
            exakt=dict(koepfe=formate.sha256_json(tab.koepfe), p0_skelett=formate.sha256_json(sk)),
            hashes=ps.testdaten_hash(sid, stufe, seed))
    for fassung in ap.STAENDE:
        for sid, st, sd, art in ap.FAELLE:
            f, r = ap.fall(sid, st, sd, art, fassung)
            a = r['ablauf']
            t1 = a.tabelle()
            out['ablauf'][f'{fassung}:{sid}/{st}/{sd}/{art}'] = dict(
                daten={k: np.array(v) for k, v in t1.daten.items()}, hashes=f['hashes'],
                exakt=dict(inhalt=formate.sha256_json(f['inhalt']), koepfe=formate.sha256_json(t1.koepfe),
                           entscheidungen=formate.sha256_json(a.z['entscheidungen']),
                           ziehungen=formate.sha256_json(a.z['ziehungen']),
                           gegenprobe=formate.sha256_json(ap._gegenprobe(sid, st, sd, art, r, fassung))))
    return out


def befunde():
    profil = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=1000)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=24)
    return kampagnen.ausfuehren('A04-R4', 'L1', profil, 3, 11, 'test', plan, 18, prozesse=1)['befunde']


if __name__ == '__main__':
    ziel = sys.argv[1]
    if len(sys.argv) > 2:
        import importlib
        from threadpoolctl import threadpool_limits
        importlib.import_module('scipy.linalg')                          # lädt die BLAS von SciPy vor dem Setzen
        threadpool_limits(limits=int(sys.argv[2]), user_api='blas')
    umg = ps.umgebung()
    from numpy._core._multiarray_umath import __cpu_features__ as merkmale
    umg['numpy_avx512'] = bool(merkmale.get('X86_V4', merkmale.get('AVX512F')))
    out = dict(umgebung=umg, pruefsaetze=pruefsaetze(), befunde=befunde())
    with open(ziel, 'wb') as f:
        pickle.dump(out, f)
    print(ziel, umg)
