"""Reproduktion des adaptiven Burn-in (Nachrechnung 13.09.) an ausgewählten Punkten durch Import des
abgelegten Skripts (nur lesend; schreibt nichts, da main() nicht aufgerufen wird)."""
import os
import importlib.util, sys, numpy as np
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../docs/arbeitspapier/nachrechnung_2026-09-13/pcmms_sweep_burnin_2026-09-13.py')
spec = importlib.util.spec_from_file_location('burnin', P)
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
phis = np.linspace(0.0, 360.0, 19, endpoint=False)
pts = [(0, 11), (11, 0), (8, 8)] if len(sys.argv) < 2 else [tuple(map(int, a.split(','))) for a in sys.argv[1:]]
for i2, i3 in pts:
    r = b.run_point(i2, i3, float(phis[i2]), float(phis[i3]))
    print(f'({i2},{i3}) phi=({phis[i2]!r},{phis[i3]!r}) t_burn={r["t_burn_s"]:.1f} s k={r["period_k"]} '
          f'delta={r["delta_ppm"]:.1f} R={r["R_ppm"]:.1f} Q={r["Q_ppm"]:.1f} ppm lam={r["liftoff_pct"]:.4f} '
          f'skew={r["skew"]:.4f} Nmax={r["N_max_N"]:.3f}')
