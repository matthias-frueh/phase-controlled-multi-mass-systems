"""Prüfung zu den Skripten dieses Ordners und zum Herkunftshinweis der 2400-s-Tabellen (16.11.2026).

Aufruf (aus beliebigem Verzeichnis):
    python3 pruefung_2026-11-16.py            # etwa 1 min
    python3 pruefung_2026-11-16.py --voll     # dazu alle 245 Punkte der Steifigkeitsreihe, etwa 6 min

A  Sinusamplitude: Rechnung aus a_sin.py gegen A_sin.txt.
B  Sinus-Sweep: alle 49 Punkte mit sinsweep.py gegen data/sweep_7x7_sinus.csv; dazu die Punkte ohne Liftoff
   mit der früher aus den Daten rekonstruierten Amplitude (RTOP + RBOT)/2.
C  Steifigkeitsreihe: Kennzahlen der fünf sens_k-Dateien gegen die Tabelle des Arbeitspapiers v2.5
   (Abschnitt 9.8, Label tab:sens-k, aus dem Quelltext gelesen); Punkte mit sens.py neu gerechnet gegen die
   Dateien (ohne --voll zwei je Steifigkeit); Punkt (0°, 0°) mit C = 16 N·s/m gegen data/sweep_19x19.csv.
D  2400-s-Tabellen (data/regime_2400s*.csv): fünf Übereinstimmungen mit dem Burn-in-Sweep vom 13.09.2026
   (Skript und Tabelle in ../nachrechnung_2026-09-13/). Ein Indiz für die Herkunft, kein Nachweis.

Die Skripte werden unverändert geladen. Keine Datei des Repositorys wird überschrieben; neu geschriebene
Tabellen liegen in einem temporären Verzeichnis.

Bestanden heißt: A stimmt exakt; in B und C liegen alle Punkte ohne Liftoff innerhalb von TOL, und die
Kennzahlen der Tabelle stimmen; D trifft zu. Punkte mit Liftoff gehen nicht in das Urteil ein: Dort kann ein
Unterschied in der letzten Stelle (andere Mathematikbibliothek) über die Laufzeit anwachsen. Ob die Dateien
bytegleich wiederkehren, wird berichtet, aber nicht verlangt; das hängt an den Versionen von numpy und scipy.

Nur Simulation, keine Messdaten. Die Prüfung gehört nicht zur Testsuite in tests/.
"""
import contextlib
import csv
import hashlib
import io
import math
import os
import platform
import re
import struct
import sys
import tempfile
import time

import numpy as np
import pandas as pd
import scipy

HIER = os.path.dirname(os.path.abspath(__file__))
os.chdir(HIER)                      # die Skripte laden Engine und A_sin.txt relativ zum Arbeitsordner
WURZEL = os.path.join('..', '..', '..')
DATA = os.path.join(WURZEL, 'data')
ENGINE = os.path.join(WURZEL, 'code', 'pcmms_v3a_phasen_sweep.py')
BURNIN = os.path.join('..', 'nachrechnung_2026-09-13', 'pcmms_sweep_burnin_2026-09-13.py')
BURNIN_CSV = os.path.join('..', 'nachrechnung_2026-09-13', 'sweep_19x19_burnin_2026-09-13.csv')
ARBEITSPAPIER = os.path.join('..', 'PCMMS_Arbeitspapier_v2_5.tex')
TOL = 1e-9                          # N bzw. dimensionslos, für Punkte ohne Liftoff
VOLL = '--voll' in sys.argv[1:]
BAHN = ('F_mean', 'liftoff', 'F_max', 'F_min')


def lade(datei, bis):
    """Definitionsteil eines Skripts ausführen (alles vor der Zeichenfolge `bis`); dessen Ausgabe entfällt."""
    quelle = open(datei, encoding='utf-8').read()
    assert quelle.count(bis) == 1, (datei, bis)
    ns = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(quelle.split(bis)[0], datei, 'exec'), ns)
    return ns


def sha(pfad):
    return hashlib.sha256(open(pfad, 'rb').read()).hexdigest()


def lies(pfad):
    with open(pfad, newline='', encoding='utf-8') as fh:
        zeilen = list(csv.reader(fh))
    return zeilen[0], zeilen[1:]


def wert(text):
    return float(text) if text != '' else float('nan')


def gleich_bits(a, b):
    return (math.isnan(a) and math.isnan(b)) or struct.pack('<d', a) == struct.pack('<d', b)


def vergleich(kopf, neu, alt):
    """Zellenweiser Vergleich zweier Tabellen mit gleichem Kopf; `alt` bestimmt, welche Zeilen Liftoff haben."""
    il = kopf.index('liftoff')
    erg = dict(zellen=0, bitgleich=0, spalten={}, frei=0, frei_max=0.0, lift=0, lift_bahn_gleich=0, lift_max=0.0)
    for zn, za in zip(neu, alt):
        frei = wert(za[il]) == 0.0
        erg['frei' if frei else 'lift'] += 1
        bahn_gleich = True
        for name, tn, ta in zip(kopf, zn, za):
            a, b = wert(tn), wert(ta)
            erg['zellen'] += 1
            if gleich_bits(a, b):
                erg['bitgleich'] += 1
                continue
            d = abs(a - b)
            n, m = erg['spalten'].get(name, (0, 0.0))
            erg['spalten'][name] = (n + 1, max(m, d))
            if frei:
                erg['frei_max'] = max(erg['frei_max'], d)
            else:
                erg['lift_max'] = max(erg['lift_max'], d)
                bahn_gleich = bahn_gleich and name not in BAHN
        if not frei and bahn_gleich:
            erg['lift_bahn_gleich'] += 1
    return erg


def bericht(erg):
    print(f"   Zellen: {erg['zellen']}, davon bitgleich: {erg['bitgleich']}")
    for name, (n, m) in erg['spalten'].items():
        print(f"   abweichend in {name}: {n} Zellen, größte Abweichung {m:.2e}")
    if erg['frei']:
        print(f"   Zeilen ohne Liftoff: {erg['frei']}, größte Abweichung dort {erg['frei_max']:.2e} (TOL {TOL:.0e})")
    if erg['lift']:
        print(f"   Zeilen mit Liftoff: {erg['lift']}, davon in F_mean, liftoff, F_max und F_min bitgleich: "
              f"{erg['lift_bahn_gleich']}; größte Abweichung dort {erg['lift_max']:.2e} (nicht im Urteil)")


def tabelle_arbeitspapier():
    """Tabelle tab:sens-k aus dem Quelltext des Arbeitspapiers v2.5: fünf Zeilen mit je acht Kennzahlen."""
    text = open(ARBEITSPAPIER, encoding='utf-8').read()
    teil = text[text.index(r'\label{sec:sens-k}'):text.index(r'\label{tab:sens-k}')]

    def zahl(s):
        return float(s.replace('$', '').replace('{,}', '.').strip())

    tab = {}
    for zeile in teil.split('\n'):
        m = re.match(r'\s*\$(?:(\d)\\cdot)?10\^\{(\d)\}\$\s*&(.*)', zeile)
        if not m:
            continue
        k = float(m.group(1) or 1) * 10 ** int(m.group(2))
        c = [x.strip() for x in m.group(3).rstrip().rstrip('\\').split('&')]
        paar, gesamt = re.match(r'(\d+) von (\d+)', c[6]).groups()
        tab[k] = (zahl(c[0]), zahl(c[1]), int(c[2]), zahl(c[3]), zahl(c[4]), zahl(c[5]), int(paar), int(gesamt))
    assert len(tab) == 5, len(tab)
    return tab


ok = {}
print('Prüfung vom 16.11.2026 zu docs/arbeitspapier/sinus_sensitivitaet_2026-09-05/')
print('Aufruf: python3 pruefung_2026-11-16.py' + (' --voll' if VOLL else ''))
print(f'Umgebung: Python {platform.python_version()}, numpy {np.__version__}, scipy {scipy.__version__}, '
      f'pandas {pd.__version__}, {platform.platform()}')
print(f'Engine: code/pcmms_v3a_phasen_sweep.py, SHA-256 {sha(ENGINE)}')
print()

# ── A  Sinusamplitude ────────────────────────────────────────────────────────────────────────────────────────
a = lade('a_sin.py', "open('A_sin.txt','w')")
A_neu, A_datei = str(a['A']), open('A_sin.txt', encoding='ascii').read()
A_rek = (a['ns']['RTOP'] + a['ns']['RBOT']) / 2
ok['A'] = A_neu == A_datei
print('A  Sinusamplitude')
print(f'   a_sin.py: Hub des Egg-Profils {a["hub"] * 1e3:.6f} mm, A = {A_neu} m')
print(f'   A_sin.txt:                                A = {A_datei} m   gleich: {"ja" if ok["A"] else "nein"}')
print(f'   (RTOP + RBOT)/2 = {A_rek!r} m; A liegt {(float(A_datei) - A_rek) * 1e9:.2f} nm darüber '
      f'(relativ {(float(A_datei) - A_rek) / A_rek:.2e})')
print()

# ── B  Sinus-Sweep ───────────────────────────────────────────────────────────────────────────────────────────
s = lade('sinsweep.py', "if __name__=='__main__'")
raster = np.linspace(0, 360, 7, endpoint=False)
t0 = time.time()
zeilen = [s['point'](p2, p3) for p2 in raster for p3 in raster]
dauer = time.time() - t0
ref = os.path.join(DATA, 'sweep_7x7_sinus.csv')
with tempfile.TemporaryDirectory() as tmp:
    ziel = os.path.join(tmp, 'sweep_7x7_sinus.csv')
    pd.DataFrame(zeilen).to_csv(ziel, index=False)          # wie in sinsweep.py
    h_neu, (kopf_neu, neu) = sha(ziel), lies(ziel)
h_alt, (kopf, alt) = sha(ref), lies(ref)
erg = vergleich(kopf, neu, alt)
ok['B'] = kopf_neu == kopf and len(neu) == len(alt) == 49 and erg['frei_max'] <= TOL
print(f'B  Sinus-Sweep, 49 Punkte mit sinsweep.py ({dauer:.0f} s) gegen data/sweep_7x7_sinus.csv')
print(f'   SHA-256 im Repository: {h_alt}')
print(f'   SHA-256 neu gerechnet: {h_neu}   bytegleich: {"ja" if h_neu == h_alt else "nein"}')
bericht(erg)
i_max, i_min, i_lift = kopf.index('F_max'), kopf.index('F_min'), kopf.index('liftoff')
A_original, s['A'] = s['A'], A_rek
abw = [max(abs(r['F_max'] - wert(z[i_max])), abs(r['F_min'] - wert(z[i_min])))
       for z in alt if wert(z[i_lift]) == 0.0
       for r in [s['point'](wert(z[0]), wert(z[1]))]]
s['A'] = A_original
print(f'   mit (RTOP + RBOT)/2 statt A_sin.txt, {len(abw)} Punkte ohne Liftoff: Abweichung in F_max und F_min '
      f'{min(abw):.2e} bis {max(abw):.2e} N')
print()

# ── C  Steifigkeitsreihe ─────────────────────────────────────────────────────────────────────────────────────
e = lade('sens.py', 'grid=np.linspace')
M, MG, F_HZ = e['M'], e['MG'], e['F_HZ']
zeta0 = 16 / (2 * math.sqrt(1e4 * M))                        # wie in sens.py
tab = tabelle_arbeitspapier()
auswahl = [(i, j) for i in range(7) for j in range(7)] if VOLL else [(0, 3), (2, 4)]
print('C  Steifigkeitsreihe')
print('   Kennzahlen je Datei gegen Arbeitspapier v2.5, Tabelle tab:sens-k; Reihenfolge: f_n, 3f/f_n, liftoff-frei,')
print('   max λ, min γ₁, max N_max/Mg, γ₁ < 0 mit gleichphasigem Paar, γ₁ < 0 gesamt')
treffer, ok['C'] = 0, True
neu_gerechnet = []
for K in (1e3, 3e3, 1e4, 3e4, 1e5):
    name = f'sens_k_{K:.0e}_{zeta0:.2f}.csv'
    kopf_k, alt_k = lies(name)
    sp = {n: [wert(z[i]) for z in alt_k] for i, n in enumerate(kopf_k)}
    fn = math.sqrt(K / M) / (2 * math.pi)
    neg = [i for i in range(len(alt_k)) if sp['F_skew'][i] < -1e-3]
    kenn = (round(fn, 1), round(3 * F_HZ / fn, 2), sum(1 for x in sp['liftoff'] if x < 1e-9),
            round(max(sp['liftoff']), 1), round(min(sp['F_skew']), 3), round(max(sp['F_max']) / MG, 2),
            sum(1 for i in neg if sp['dmin'][i] < 1e-6), len(neg))
    n_gleich = sum(1 for x, y in zip(kenn, tab[K]) if x == y)
    treffer += n_gleich
    print(f'   {name}: {kenn}  Arbeitspapier: {tab[K]}  {n_gleich}/8')
    C = 2 * zeta0 * math.sqrt(K * M)
    t0 = time.time()
    punkte = [e['point'](raster[i], raster[j], K, C) for i, j in auswahl]
    neu_gerechnet.append((name, kopf_k, alt_k, punkte, C, time.time() - t0))
ok['C'] = ok['C'] and treffer == 40
print(f'   Kennzahlen: {treffer} von 40 stimmen')
print(f'   Punkte mit sens.py neu gerechnet ({"alle 49" if VOLL else "zwei"} je Steifigkeit) gegen die Dateien')
for name, kopf_k, alt_k, punkte, C, dauer in neu_gerechnet:
    d = pd.DataFrame(punkte)
    d['dmin'] = [e['mind'](p2, p3) for p2, p3 in zip(d.phi2, d.phi3)]          # wie in sens.py
    with tempfile.TemporaryDirectory() as tmp:
        ziel = os.path.join(tmp, name)
        d.to_csv(ziel, index=False)
        h_neu, (kopf_neu, neu_k) = sha(ziel), lies(ziel)
    erg = vergleich(kopf_k, neu_k, [alt_k[7 * i + j] for i, j in auswahl])
    ok['C'] = ok['C'] and kopf_neu == kopf_k and erg['frei_max'] <= TOL
    zusatz = f', bytegleich: {"ja" if h_neu == sha(name) else "nein"}' if VOLL else ''
    print(f'   {name} (C = {C!r} N·s/m, {dauer:.0f} s{zusatz})')
    bericht(erg)
p00 = e['point'](0.0, 0.0, 1e4, 16.0)
kopf_19, alt_19 = lies(os.path.join(DATA, 'sweep_19x19.csv'))
z00 = [z for z in alt_19 if wert(z[0]) == 0.0 and wert(z[1]) == 0.0][0]
stellen = {'F_mean': 6, 'F_skew': 6, 'liftoff': 4, 'F_max': 6, 'F_min': 6}
gleich = all(f'{p00[n]:.{st}f}' == z00[kopf_19.index(n)] for n, st in stellen.items())
print(f'   Punkt (0°, 0°) mit K = 1e4 N/m und C = 16.0 N·s/m: '
      + ', '.join(f'{n} {p00[n]:.{st}f}' for n, st in stellen.items()))
print(f'   gleich der Zeile in data/sweep_19x19.csv auf die dort abgelegten Nachkommastellen: '
      f'{"ja" if gleich else "nein"} (Punkt mit Liftoff, nicht im Urteil)')
print()

# ── D  2400-s-Tabellen ───────────────────────────────────────────────────────────────────────────────────────
quelle = open(BURNIN, encoding='utf-8').read()
k_list = [int(x) for x in re.search(r'^K_LIST\s*=\s*\[([^\]]*)\]', quelle, re.M).group(1).split(',')]
tol_v, tol_z = (float(x) for x in re.search(r'^TOL_V,\s*TOL_Z,\s*N_LAST\s*=\s*([^,]+),\s*([^,]+),', quelle, re.M).groups())
jv_jz = bool(re.search(r'\bjv\b', quelle)) and bool(re.search(r'\bjz\b', quelle))
kopf_b, alt_b = lies(BURNIN_CSV)
ohne = [(z[kopf_b.index('i2')], z[kopf_b.index('i3')]) for z in alt_b if z[kopf_b.index('period_k')] == '-1']
print('D  2400-s-Tabellen gegen den Burn-in-Sweep vom 13.09.2026 (Indiz für die Herkunft, kein Nachweis)')
print(f'   pcmms_sweep_burnin_2026-09-13.py: K_LIST = {k_list}, TOL_V = {tol_v:g} m/s, TOL_Z = {tol_z:g} m, '
      f'Variablen jv und jz: {"ja" if jv_jz else "nein"}')
print(f'   sweep_19x19_burnin_2026-09-13.csv: {len(alt_b)} Zeilen, Spalten i2 und i3: '
      f'{"ja" if kopf_b[:2] == ["i2", "i3"] else "nein"}, ohne erkannte Periode (period_k = -1): {len(ohne)}')
ok['D'] = jv_jz and kopf_b[:2] == ['i2', 'i3']
for name in ('regime_2400s.csv', 'regime_2400s_dt2.csv'):
    kopf_r, alt_r = lies(os.path.join(DATA, name))
    spalten = all(n in kopf_r for n in ('i2', 'i3', 'passk', 'bestk', 'bestjv', 'bestjz'))
    sp = {n: [z[kopf_r.index(n)] for z in alt_r] for n in kopf_r}
    bestk, passk = sorted({int(x) for x in sp['bestk']}), sorted({int(x) for x in sp['passk']})
    enthalten = set(bestk) <= set(k_list) and set(passk) - {0} <= set(k_list)
    punkte = list(zip(sp['i2'], sp['i3'])) == ohne
    erfuellt = [int(p) != 0 for p in sp['passk']]
    unter = [float(v) < tol_v and float(z) < tol_z for v, z in zip(sp['bestjv'], sp['bestjz'])]
    mit = [float(v) for v, e in zip(sp['bestjv'], erfuellt) if e]
    rest = [float(v) for v, e in zip(sp['bestjv'], erfuellt) if not e]
    ok['D'] = ok['D'] and spalten and enthalten and punkte and erfuellt == unter
    print(f'   {name}: {len(alt_r)} Zeilen')
    print(f'      1. bestk {bestk}, passk {passk} (0 laut data/README.md: Kriterium nicht erfüllt); '
          f'alle Werte in K_LIST: {"ja" if enthalten else "nein"}')
    print(f'      2. Spalten bestjv und bestjz (im Skript jv und jz), 3. Spalten i2 und i3: {"ja" if spalten else "nein"}')
    print(f'      4. Punkte und Reihenfolge gleich den {len(ohne)} Punkten ohne erkannte Periode: {"ja" if punkte else "nein"}')
    print(f'      5. passk > 0 genau dort, wo bestjv < TOL_V und bestjz < TOL_Z: {"ja" if erfuellt == unter else "nein"} '
          f'(bestjv mit passk > 0: {", ".join(f"{v:.3e}" for v in mit)}; kleinster bestjv mit passk = 0: {min(rest):.3e})')
print()

bestanden = all(ok.values())
print('Urteil: ' + ', '.join(f'{k} {"ja" if v else "nein"}' for k, v in ok.items()))
print('Ergebnis: ' + ('bestanden' if bestanden else 'NICHT bestanden'))
sys.exit(0 if bestanden else 1)
