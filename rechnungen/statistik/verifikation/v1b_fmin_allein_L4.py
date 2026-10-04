"""v1b_fmin_allein_L4.py – Zusatz zu v1: P(PB1 ∧ kein |z| > c) nur über die 21 F_min-Tests auf Stufe L3/L4 (analytisch, ν = 37)."""
import sys, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import v1_pb1_bindung_analytisch as V          # führt v1 aus (Ausgabe unterdrückt)
import numpy as np
for L in (3, 4, 5):
    lab, sh, sa, sp = V.LEVELS[L]
    U = V.u_all(sh, sa, sp, V.n0)
    pF = np.prod([V.p1_test(r, 37, V.c37) for r in V.DELTA9[0] / U[:, 0]])
    pN1 = np.prod([V.p1_test(r, 37, V.c37) for r in (V.DELTA9[1] / U[:, 1:3]).ravel()])
    print(f'{lab}: nur F_min (21 Tests): P = {pF:.3f}; nur Re/Im N1 (42 Tests): P = {pN1:.3f}')
