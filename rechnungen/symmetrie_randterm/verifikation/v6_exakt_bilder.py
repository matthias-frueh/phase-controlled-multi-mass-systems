"""
v6_exakt_bilder.py - unabhaengige Numerik (ereignisgesteuert, v_exakt) fuer SYM-02/SYM-03:
L1 (157.3, 264), Spiegelbild L1* (202.7, 96), 120-Grad-Bild K1+120 (230, 354), Standardstart, 20 s.
Auswertung 15-20 s auf einem 5-us-Raster der exakten Kraft: lambda, gamma1, F_min, F_max, <N> (Impulsintegral).
"""
import sys, time, numpy as np
import v_engine as ve, v_exakt as vx

PTS = [('L1', 157.3, 264.0), ('L1*', 202.7, 96.0), ('K1+120', 230.0, 354.0)]
sel = sys.argv[1:] or [p[0] for p in PTS]
for nm, p2, p3 in PTS:
    if nm not in sel:
        continue
    t1 = time.time()
    b = vx.Bahn(p2, p3)
    b.integriere(0.0, -ve.MG / ve.K0, 0.0, 20.0)
    tg = 15.0 + np.arange(1000000) * 5e-6
    F = b.kraft(tg)
    m = F.mean(); s = F.std()
    gam = np.mean((F - m) ** 3) / s ** 3
    I = b.impuls(15.0, 20.0) / 5.0
    z, v = b.zustand(np.array([15.0, 17.5, 19.9]))
    print(f'{nm:7s} ({p2},{p3}) exakt [{time.time() - t1:.0f} s]: lambda {np.mean(F < 1e-9) * 100:.3f} %  gamma1 {gam:+.4f}  '
          f'F_min {F.min():.4f}  F_max {F.max():.3f} N  <N> = {I:.6f} N (Mg {ve.MG:.4f})  Segmente {len(b.seg)}; '
          f'v_f bei 15/17,5/19,9 s: {np.round(v, 5)}', flush=True)
