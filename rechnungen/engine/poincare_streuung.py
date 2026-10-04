"""P2/engine – Streuung des Poincaré-Schnitts (ż zu Zyklusbeginn, 50–100 s) je Lauf und Wiederkehrabstand für
p = 1, 2, 3, 6, 30: Festschritt-Rauschen der Hüpfzustände (skaliert mit Δt) gegenüber exakter Periodizität.
Aufruf: python3 poincare_streuung.py SPEC.json RUNDIR"""
import sys
import numpy as np
import run_seg
r, L = run_seg.load(sys.argv[1], sys.argv[2])
for k, l in enumerate(L):
    v = r['PV'][500:, k]; z = r['PZ'][500:, k]
    out = [f'p{p}: {np.abs(v[p:] - v[:-p]).max():.1e}/{np.abs(z[p:] - z[:-p]).max():.1e}' for p in (1, 2, 3, 6, 30)]
    print(f'{l["name"]:12s} ż-Spanne {np.ptp(v):.3e}  ' + '  '.join(out))
