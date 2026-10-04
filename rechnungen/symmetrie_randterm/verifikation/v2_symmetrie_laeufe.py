"""
v2_symmetrie_laeufe.py - eigene RK4-Engine (v_engine), 600 Perioden (60 s), Fenster 40-50 s und 50-60 s.
Aufruf: python3 v2_symmetrie_laeufe.py std|shift frame|com
 std  : alle Bilder mit Standardstart t0 = 0 (statisches Gleichgewicht, Ruhe) -> Startabhaengigkeit
 shift: S3-Bilder mit Startzeit t0 = -tau_ref (aequivalenter Start)
Punkte: K1 (110,234), L1 (157.3,264), L4 (330.6,242.9), L5 (98.1,333.7), L6 (307.5,279.9) je 6 S3-Bilder;
im Modus std zusaetzlich Spiegelbilder (-phi) von K1, L1 und 120-Grad-Bilder von K1, L1, L5.
"""
import sys, time, numpy as np
import v_engine as ve

mode, form = sys.argv[1], sys.argv[2]
BASIS = {'K1': (110.0, 234.0), 'L1': (157.3, 264.0), 'L4': (330.6, 242.9), 'L5': (98.1, 333.7),
         'L6': (307.5, 279.9)}


def s3_bilder(p2, p3):
    """eigene Herleitung: Referenzmodul r aus {0,p2,p3}; neue Phasen = alte - r (mod 360)."""
    res = []
    for r, rest in [(0.0, (p2, p3)), (p2, (0.0, p3)), (p3, (0.0, p2))]:
        a, b = (rest[0] - r) % 360, (rest[1] - r) % 360
        res.append((a, b, r, 'ref%g' % r))
        res.append((b, a, r, 'ref%g*' % r))
    return res


pts = []   # (name, phi2, phi3, t0)
basen = ['K1', 'L1', 'L4'] if mode == 'shift' else list(BASIS)
for nm in basen:
    p2, p3 = BASIS[nm]
    for i, (a, b, r, lab) in enumerate(s3_bilder(p2, p3)):
        t0 = -(r / 360.0) * ve.T if mode == 'shift' else 0.0
        pts.append((f'{nm}:g{i}', a, b, t0))
if mode == 'std':
    for nm in ('K1', 'L1'):
        p2, p3 = BASIS[nm]
        pts.append((f'{nm}:mirror', (-p2) % 360, (-p3) % 360, 0.0))
    for nm in ('K1', 'L1', 'L5'):
        p2, p3 = BASIS[nm]
        pts.append((f'{nm}:+120', (p2 + 120) % 360, (p3 + 120) % 360, 0.0))
names = [p[0] for p in pts]
P2 = np.array([p[1] for p in pts]); P3 = np.array([p[2] for p in pts]); T0 = np.array([p[3] for p in pts])
t1 = time.time()
o = ve.run(P2, P3, 600, form=form, t0=T0)
print(f'{len(pts)} Punkte, 600 Perioden, {form}, {mode}: {time.time() - t1:.1f} s')
np.savez(f'v2_laeufe_{mode}_{form}.npz', names=np.array(names), P2=P2, P3=P3, T0=T0,
         **{k: o[k] for k in ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS', 'DFT')}, L=o['L'],
         vSend=o['vSend'])
