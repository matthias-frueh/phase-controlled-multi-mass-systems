"""
finesweep.py – vektorisierte Reproduktion der Referenz-Engine pcmms_v3a_phasen_sweep.py
(identische Parameter, identisches RK4-Schema, identische Observablen).
Abgleich gegen sweep_19x19.csv mit --validate: liftoff-arme Punkte stimmen auf sechs
Nachkommastellen; am Punkt (0,0) mit 75,8 % Liftoff weicht F_mean um 1,7e-4 N ab
(Auswertungsreihenfolge skalar vs. vektorisiert). Der Referenzdatensatz stammt aus
pcmms_v3a_phasen_sweep.py, nicht aus diesem Skript.

Erzeugt:
  finesweep_2deg_120_240.csv   441 Punkte, phi2 in [100,140], phi3 in [220,260], 2°-Raster
  series_regime.npz            Zeitreihen N(t) für (0,0), (151.579,265.263), (120,240), 0.3 s ab Burn-in

Aufruf:  python3 finesweep.py [--validate] [--chunk N]
Rechenzeit: ca. 55 s je 111 Punkte (Chunking, weil F_eval für 441 Punkte ~750 MB belegt).

Matthias Früh · PCMMS · September 2026
"""
import sys, os
import numpy as np
from scipy.stats import skew

# ── Parameter exakt wie in pcmms_v3a_phasen_sweep.py ────────────────────────
M, G = 0.650, 9.81
MG = M * G
F_HZ = 10.0;            T_CYC = 1.0 / F_HZ
RTOP = 0.005;           THOLD = 0.65;   TFAST = 1.0 - THOLD
RBOT = RTOP * TFAST / THOLD
K, C_DAMP = 10000.0, 16.0
DT, T_SIM, T_BURN = 5e-5, 15.0, 5.0
N_STEPS, N_BURN = int(T_SIM / DT), int(T_BURN / DT)
_A_HOLD = -RTOP * (np.pi / (THOLD * T_CYC))**2
_A_FAST =  RBOT * (np.pi / (TFAST * T_CYC))**2


def z_egg_zdd(t):
    phi = np.mod(t, T_CYC) / T_CYC
    return np.where(phi < THOLD, _A_HOLD * np.sin(np.pi * phi / THOLD),
                    _A_FAST * np.sin(np.pi * (phi - THOLD) / TFAST))


def rhs(z, zd, t, tau2, tau3):
    F = -K * z - C_DAMP * zd
    Fc = np.where((z >= 0.0) | (F <= 0.0), 0.0, F)
    zdd_egg = (z_egg_zdd(t) + z_egg_zdd(t - tau2) + z_egg_zdd(t - tau3)) / 3.0
    return zd, -G + Fc / M - zdd_egg, Fc


def run(phi2_deg, phi3_deg, store_series=False, series_len=0):
    phi2 = np.radians(np.asarray(phi2_deg, float)); phi3 = np.radians(np.asarray(phi3_deg, float))
    tau2 = phi2 / (2 * np.pi * F_HZ); tau3 = phi3 / (2 * np.pi * F_HZ)
    n = phi2.size
    z, zd = np.full(n, -MG / K), np.zeros(n)
    F_eval = np.empty((N_STEPS - N_BURN, n))
    series = np.empty((series_len, n)) if store_series else None
    for i in range(N_STEPS):
        t = i * DT
        k1z, k1d, Fc = rhs(z, zd, t, tau2, tau3)
        k2z, k2d, _ = rhs(z + 0.5*DT*k1z, zd + 0.5*DT*k1d, t + 0.5*DT, tau2, tau3)
        k3z, k3d, _ = rhs(z + 0.5*DT*k2z, zd + 0.5*DT*k2d, t + 0.5*DT, tau2, tau3)
        k4z, k4d, _ = rhs(z + DT*k3z, zd + DT*k3d, t + DT, tau2, tau3)
        z = z + DT * (k1z + 2*k2z + 2*k3z + k4z) / 6.0
        zd = zd + DT * (k1d + 2*k2d + 2*k3d + k4d) / 6.0
        if i >= N_BURN:
            F_eval[i - N_BURN] = Fc
            if store_series and i - N_BURN < series_len:
                series[i - N_BURN] = Fc
    F_min, F_max = F_eval.min(0), F_eval.max(0)
    denom = MG - F_min
    out = dict(phi2_deg=np.degrees(phi2), phi3_deg=np.degrees(phi3), F_mean=F_eval.mean(0),
               F_skew=skew(F_eval, axis=0), liftoff=(F_eval < 1e-9).mean(0) * 100.0,
               F_max=F_max, F_min=F_min,
               peak_ratio=np.where(denom > 1e-6, (F_max - MG) / np.where(denom > 1e-6, denom, 1.0), np.nan))
    return out, series


if __name__ == '__main__':
    import pandas as pd
    if '--validate' in sys.argv:
        ref = pd.read_csv('sweep_19x19.csv')
        pts = [(0.0, 0.0), (113.684, 227.368), (151.579, 265.263)]
        out, _ = run([p[0] for p in pts], [p[1] for p in pts])
        for j, (a, b) in enumerate(pts):
            r = ref[(ref.phi2_deg == a) & (ref.phi3_deg == b)].iloc[0]
            print(f'({a},{b}) F_mean {out["F_mean"][j]:.6f}/{r.F_mean:.6f}  F_min {out["F_min"][j]:.6f}/{r.F_min:.6f}  '
                  f'skew {out["F_skew"][j]:.6f}/{r.F_skew:.6f}  liftoff {out["liftoff"][j]:.4f}/{r.liftoff:.4f}')
        sys.exit()
    p2, p3 = np.arange(100, 141, 2), np.arange(220, 261, 2)
    P2, P3 = np.meshgrid(p2, p3, indexing='ij')
    phi2_all, phi3_all = P2.ravel().astype(float), P3.ravel().astype(float)
    CH = 111; nch = int(np.ceil(phi2_all.size / CH))
    single = '--chunk' in sys.argv
    chunks = [int(sys.argv[sys.argv.index('--chunk') + 1])] if single else range(nch)
    # Die Chunks schreiben im Anhaengemodus (ein voller Lauf besteht aus nch Teillaeufen).
    # Ein vorhandener Datensatz wuerde dadurch verlaengert statt ersetzt -> vorher abbrechen.
    if not single and os.path.exists('finesweep_2deg_120_240.csv'):
        sys.exit('finesweep_2deg_120_240.csv existiert bereits. Zum Neuerzeugen die Datei '
                 'entfernen oder umbenennen; einzelne Teillaeufe mit --chunk N anhaengen.')
    for i in chunks:
        sl = slice(i * CH, (i + 1) * CH)
        out, _ = run(phi2_all[sl], phi3_all[sl])
        df = pd.DataFrame(out)
        df.to_csv('finesweep_2deg_120_240.csv', mode='a', index=False, float_format='%.6f',
                  header=not os.path.exists('finesweep_2deg_120_240.csv'))
        print(f'chunk {i}: {len(df)} Punkte, F_min max {df.F_min.max():.4f}')
    pts = [(0.0, 0.0), (151.579, 265.263), (120.0, 240.0)]
    out, series = run([p[0] for p in pts], [p[1] for p in pts], store_series=True, series_len=int(0.3 / DT))
    np.savez('series_regime.npz', t=np.arange(series.shape[0]) * DT, F=series,
             phi2=[p[0] for p in pts], phi3=[p[1] for p in pts])
    print('fertig')
