"""s2_symmetrie_laeufe.py - Laeufe fuer die numerische Symmetriepruefung (Teil A, Aufgaben 2-3).

Basispunkte: 3 liftoff-frei (Kontaktast), 6 mit Liftoff (generisch, aus s1_kandidaten), dazu
2 Punkte, an denen die 120-Grad-Verschiebung zufaellig eine Aequivalenz ist (40,200), (80,160).
Je Basispunkt: sechs S3-Bilder, Spiegelbild (-phi2,-phi3), 120-Grad-Bild (phi2+120, phi3+120).

Modus 'std'  : alle Laeufe mit Standardstart z=-Mg/K, zd=0, t0=0 (wie Engine), 600 Perioden (60 s).
Modus 'shift': S3-Bilder mit Standardzustand, aber Startzeit t0 = -tau_ref (tau_ref = phi_ref/(360 f));
               damit ist abar_B(t) = abar_A(t + tau_ref) und der Lauf B die zeitverschobene Kopie von A.
Ausgabe: s2_laeufe_<modus>.npz (zyklusweise Akkumulatoren, siehe sr_engine.run)."""
import sys
import time
import numpy as np
import sr_engine as se

BASIS = [('K1', 110.0, 234.0), ('K2', 128.0, 246.0), ('K3', 114.0, 252.0),
         ('L1', 157.3, 264.0), ('L2', 198.2, 267.4), ('L3', 204.4, 250.8),
         ('L4', 330.6, 242.9), ('L5', 98.1, 333.7), ('L6', 307.5, 279.9),
         ('Z1', 40.0, 200.0), ('Z2', 80.0, 160.0)]
N_CYC = 600


def liste(mode):
    rows = []
    for name, a, b in BASIS:
        for g, p2, p3, pref in se.s3_images(a, b):
            t0 = 0.0 if mode == 'std' else -pref / (360.0 * se.F_HZ)
            rows.append((name, g, p2, p3, pref, t0))
        if mode == 'std':
            rows.append((name, 'mirror', float(np.mod(-a, 360)), float(np.mod(-b, 360)), np.nan, 0.0))
            rows.append((name, 'plus120', float(np.mod(a + 120, 360)), float(np.mod(b + 120, 360)), np.nan, 0.0))
    return rows


if __name__ == '__main__':
    mode = sys.argv[1]
    rows = liste(mode)
    p2 = np.array([r[2] for r in rows]); p3 = np.array([r[3] for r in rows])
    t0 = np.array([r[5] for r in rows])
    tic = time.time()
    o = se.run(p2, p3, N_CYC, t0=t0)
    print(f'{mode}: {len(rows)} Laeufe, {N_CYC} Perioden, {time.time() - tic:.0f} s')
    keep = {k: v for k, v in o.items() if isinstance(v, np.ndarray)}
    np.savez(f's2_laeufe_{mode}.npz', names=np.array([r[0] for r in rows]),
             elems=np.array([r[1] for r in rows]), pref=np.array([r[4] for r in rows]),
             L=o['L'], dt=o['dt'], **keep)
