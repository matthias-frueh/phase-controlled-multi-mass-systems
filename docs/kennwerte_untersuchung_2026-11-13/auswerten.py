"""Untersuchung der Kennwerte (13.11.2026), Schritt 2: Streuung zwischen den Umgebungen.

Aufruf aus dem Wurzelverzeichnis des Repositorys:

    python3 docs/kennwerte_untersuchung_2026-11-13/auswerten.py <Verzeichnis mit den .pkl aus messen.py> <Bezug>

Schreibt streuung.json neben dieses Skript. Je Umgebung gegen die Bezugsumgebung:
- exakte Teile (Katalog, Köpfe, Skelett, Inhalt, Entscheidungen, Ziehungen, Gegenprobe): gleich oder nicht;
- Prüfsummen der berechneten Felder (wie in den Prüfsätzen): Zahl der abweichenden;
- Felder Eintrag für Eintrag: größte Abweichung bezogen auf den größten Betrag des Feldes (δ/M), dasselbe nur für die
  Laufzusammenfassungen und Ablauf-Tabellen (ohne P0-Messung), und bezogen auf den Eintrag selbst (δ/|x|);
- Kennwerte (kennwerte.py): innerhalb der Toleranz? größte Auslastung der Toleranz, zum Vergleich auch mit der
  engeren Toleranz rtol = 1e-12;
- Kurzbefunde: exakte Inhalte gleich? größte Abweichung der Zahlenfelder bezogen auf M und Auslastung.
Dazu die Größe der vollen Bezugsfelder der Bezugsumgebung (roh und als komprimierte NPZ).
"""
import glob
import io
import json
import os
import pickle
import sys

sys.path.insert(0, 'code')
import numpy as np                                                       # noqa: E402

from pcmms_auswertung import formate, kennwerte as kw                    # noqa: E402
from pcmms_auswertung.harness.pruefsatz import _einzeilig                # noqa: E402  (kompakter JSON-Text)

HIER = os.path.dirname(os.path.abspath(__file__))


def reell(a):
    a = np.asarray(a)
    return np.stack([a.real, a.imag], -1).ravel() if np.iscomplexobj(a) else a.astype(float).ravel()


def felder_vergleich(fa, fb):
    """Größte δ/M, größte δ/|x| und das Feld mit der größten δ/M über alle Gleitkommafelder; exakte Felder gleich?"""
    dm, dx, wo, exakt = 0.0, 0.0, None, True
    for k in fa:
        a, b = np.asarray(fa[k]), np.asarray(fb[k])
        if a.dtype.kind in 'biu':
            exakt = exakt and bool(np.array_equal(a, b))
            continue
        x, y = reell(a), reell(b)
        e = np.isfinite(x) & np.isfinite(y)
        exakt = exakt and bool(np.array_equal(np.isfinite(x), np.isfinite(y)))
        if not e.any():
            continue
        d, M = np.abs(x[e] - y[e]), float(np.abs(x[e]).max())
        if M > 0 and d.max() / M > dm:
            dm, wo = float(d.max() / M), k
        nz = np.abs(x[e]) > 0
        if nz.any():
            dx = max(dx, float((d[nz] / np.abs(x[e][nz])).max()))
    return dm, dx, wo, exakt


def pruefsaetze(ref, d):
    out = dict(exakte_teile_abweichend=[], pruefsummen_abweichend=0, pruefsummen_gesamt=0, delta_M=0.0, delta_x=0.0,
               feld_delta_M=None, delta_M_ohne_p0=0.0, kennwerte_gleich=True, kennwerte_innerhalb=True, auslastung=0.0,
               feld_auslastung=None, auslastung_rtol_1e_12=0.0)
    if ref['katalog'] != d['katalog']:
        out['exakte_teile_abweichend'].append('katalog')
    for teil in ('testdaten', 'ablauf'):
        for key, x in ref[teil].items():
            y = d[teil][key]
            out['exakte_teile_abweichend'] += [f'{key}: {z}' for z in x['exakt'] if x['exakt'][z] != y['exakt'][z]]
            for h, w in x['hashes'].items():
                if h in ('zusammenfassungen', 'p0_messung', 'daten'):
                    out['pruefsummen_gesamt'] += 1
                    out['pruefsummen_abweichend'] += int(w != y['hashes'][h])
                elif w != y['hashes'][h]:
                    out['exakte_teile_abweichend'].append(f'{key}: Prüfsumme {h}')
            for fk in ('daten', 'p0_felder'):
                if fk not in x:
                    continue
                dm, dx, wo, exakt = felder_vergleich(x[fk], y[fk])
                if not exakt:
                    out['exakte_teile_abweichend'].append(f'{key}: {fk}: exaktes Feld oder NaN-Muster')
                if dm > out['delta_M']:
                    out.update(delta_M=dm, feld_delta_M=f'{key}: {fk}: {wo}')
                out['delta_x'] = max(out['delta_x'], dx)
                if fk == 'daten':
                    out['delta_M_ohne_p0'] = max(out['delta_M_ohne_p0'], dm)
                ka, kb = kw.felder(x[fk]), kw.felder(y[fk])
                v = kw.vergleich_felder(ka, kb)
                out['auslastung_rtol_1e_12'] = max(out['auslastung_rtol_1e_12'],
                                                   kw.vergleich_felder(ka, kb, rtol=1e-12)['auslastung'])
                out['kennwerte_gleich'] = out['kennwerte_gleich'] and v['kennwerte_gleich']
                out['kennwerte_innerhalb'] = out['kennwerte_innerhalb'] and v['gleich']
                if v['auslastung'] > out['auslastung']:
                    out.update(auslastung=v['auslastung'], feld_auslastung=f'{key}: {fk}: {v["feld_auslastung"]}')
    return out


def groesse(ref):
    """Größe der vollen Bezugsfelder in Byte: roh und als komprimierte NPZ, je Teil."""
    out = {}
    for name, teil, fk in (('laufzusammenfassungen', 'testdaten', 'daten'), ('p0_messungen', 'testdaten', 'p0_felder'),
                           ('ablauf_tabellen', 'ablauf', 'daten')):
        roh = npz = 0
        for x in ref[teil].values():
            roh += sum(np.asarray(v).nbytes for v in x[fk].values())
            b = io.BytesIO()
            np.savez_compressed(b, **{f'f{i}': np.asarray(v) for i, v in enumerate(x[fk].values())})
            npz += len(b.getvalue())
        out[name] = dict(roh=roh, npz=npz)
    out['summe'] = dict(roh=sum(v['roh'] for v in out.values()), npz=sum(v['npz'] for v in out.values()))
    return out


def befunde(ref, d):
    ohne = ('laufzeit_s',)
    v = kw.vergleich_objekt(ref, d, ohne=ohne)
    grob = kw.vergleich_objekt(ref, d, rtol=10.0, atol=1.0, ohne=ohne)         # nur exakte Inhalte zählen
    eng = kw.vergleich_objekt(ref, d, rtol=1e-15, atol=0.0, ohne=ohne)          # Auslastung = δ/(1e-15·M)
    h = lambda b: formate.sha256_json({k: w for k, w in b.items() if k != 'laufzeit_s'})    # noqa: E731
    return dict(pruefsummen_gleich=[h(a) == h(b) for a, b in zip(ref, d)], exakte_inhalte_gleich=grob['gleich'],
                innerhalb_der_toleranz=v['gleich'], auslastung=v['auslastung'],
                stelle_auslastung=v['stelle_auslastung'],
                delta_M=eng['auslastung'] * 1e-15 if np.isfinite(eng['auslastung']) else None)


if __name__ == '__main__':
    verzeichnis, bezug = sys.argv[1], sys.argv[2]
    D = {os.path.basename(p)[:-4]: pickle.load(open(p, 'rb'))
         for p in sorted(glob.glob(os.path.join(verzeichnis, '*.pkl')))}
    ref = D[bezug]
    out = dict(beschreibung='Streuung der Prüfsatz-Felder und der Kurzbefunde zwischen Rechenumgebungen (messen.py, '
                            'auswerten.py); Toleranz der Kennwerte ' + json.dumps(kw.toleranz(), ensure_ascii=False),
               bezug=bezug, umgebungen={n: d['umgebung'] for n, d in D.items()}, pruefsaetze={}, befunde={},
               groesse_bezugsfelder_byte=groesse(ref['pruefsaetze']))
    for n, d in D.items():
        if n == bezug:
            continue
        out['pruefsaetze'][n] = pruefsaetze(ref['pruefsaetze'], d['pruefsaetze'])
        out['befunde'][n] = befunde(ref['befunde'], d['befunde'])
    kerne = {n: {x['rechenkern'] for x in d['umgebung']['blas'] or []} for n, d in D.items()}
    paare = [(a, b) for a in D for b in D if a < b and kerne[a] and kerne[a] == kerne[b]
             and D[a]['umgebung'].get('numpy_avx512') == D[b]['umgebung'].get('numpy_avx512')]
    out['befunde_gleicher_kern_andere_threadzahl'] = {f'{a} gegen {b}': befunde(D[a]['befunde'], D[b]['befunde'])
                                                      for a, b in paare}
    with open(os.path.join(HIER, 'streuung.json'), 'w', encoding='utf-8') as f:
        f.write(_einzeilig(out) + '\n')
    for n, r in out['pruefsaetze'].items():
        print(f'{n:22s} exakt abw. {len(r["exakte_teile_abweichend"])}  Prüfsummen abw. {r["pruefsummen_abweichend"]}/'
              f'{r["pruefsummen_gesamt"]}  δ/M {r["delta_M"]:.2e} (ohne P0 {r["delta_M_ohne_p0"]:.2e})  δ/|x| '
              f'{r["delta_x"]:.2e}  Auslastung {r["auslastung"]:.2e} (rtol 1e-12: {r["auslastung_rtol_1e_12"]:.2e})'
              f'  | Befunde: exakt gleich {out["befunde"][n]["exakte_inhalte_gleich"]}, δ/M '
              f'{out["befunde"][n]["delta_M"] or 0:.2e}, Auslastung {out["befunde"][n]["auslastung"]:.2e}')
    print('Bezugsfelder:', out['groesse_bezugsfelder_byte'])
    for n, r in out['befunde_gleicher_kern_andere_threadzahl'].items():
        print(f'{n:40s} Prüfsummen gleich {r["pruefsummen_gleich"]}, exakt gleich {r["exakte_inhalte_gleich"]}, δ/M '
              f'{r["delta_M"] or 0:.2e}, Auslastung {r["auslastung"]:.2e}')
