"""v7_kartenband.py - Datenpruefung: Anteil des gesaettigten Huepfbands in data/sweep_19x19.csv (SYM-03) und
mittlere Differenz der Vertauschung (23) ueber 171 Paare i<j (SYM-05)."""
import os
import pandas as pd, numpy as np
d = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/sweep_19x19.csv'))
b = d[(d.liftoff >= 74) & (d.liftoff <= 77)]
print(f'Band lambda 74-77 %: {len(b)} von {len(d)} Punkten ({len(b) / len(d) * 100:.1f} %), Schiefe {b.F_skew.min():.5f} .. {b.F_skew.max():.5f}')
print('lambda == 0:', (d.liftoff == 0).sum(), ' F_min > 0:', (d.F_min > 1e-9).sum())
p = np.sort(d.phi2_deg.unique())
A = d.pivot(index='phi2_deg', columns='phi3_deg', values='F_mean').loc[p, p].values
iu = np.triu_indices(len(p), 1)
diff = A[iu] - A.T[iu]
print(f'Vertauschung (23): {diff.size} Paare i<j, mittlere Differenz {diff.mean():+.2e} N, max |Diff| {np.abs(diff).max() * 1e3:.2f} mN')
