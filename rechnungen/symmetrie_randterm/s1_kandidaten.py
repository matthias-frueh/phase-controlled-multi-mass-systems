"""s1_kandidaten.py - Auswahl generischer Punkte (keine zwei gleichen zyklischen Abstaende, kein
Abstand nahe 0 oder 120 Grad) fuer die numerische Symmetriepruefung. Standardstart, 15 s,
Fenster 5-15 s. Ausgabe: lambda, F_min, Schiefe je Kandidat."""
import numpy as np
import sr_engine as se

rng = np.random.default_rng(20261002)
cand = []
while len(cand) < 20:
    a, b = np.round(rng.uniform(0, 360, 2), 1)
    g = se.gaps(a, b)
    d = [abs(g[0] - g[1]), abs(g[1] - g[2]), abs(g[0] - g[2])]
    if min(g) > 20 and min(d) > 10 and min(abs(x - 120) for x in g) > 8:
        cand.append((float(a), float(b)))
p2 = [c[0] for c in cand]; p3 = [c[1] for c in cand]
o = se.run(p2, p3, 150)
w = se.window(o, 50, 150)
print(' phi2    phi3   Abstaende            lambda/%   F_min/N   Schiefe   F_max/N  dv(5-15s)/(m/s)')
for j, (a, b) in enumerate(cand):
    g = se.gaps(a, b)
    print(f'{a:6.1f} {b:6.1f}  ({g[0]:5.1f},{g[1]:5.1f},{g[2]:5.1f})  {w["liftoff"][j]:8.3f}  {w["F_min"][j]:8.4f}'
          f'  {w["skew"][j]:8.4f}  {w["F_max"][j]:8.3f}  {w["dv"][j]:+.2e}')
