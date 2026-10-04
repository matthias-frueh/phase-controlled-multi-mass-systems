"""Plausibilitätsprüfung zu ap13_zeit.py: max|z| bei exakter Superposition und Zeitreihenlauf gegen Harmonische."""
import numpy as np
src = open('ap13_zeit.py', encoding='utf-8').read().split('# (d)')[0]
exec(src)
mz = np.array([kampagne(200) for _ in range(200)])
print('max|z| (exakt, 200 Kampagnen, B = 200): Median %.2f, q95 %.2f' % (np.median(mz), np.quantile(mz, 0.95)))
print('c_B(nu=37) = %.3f' % tdist.ppf(1 - 0.05 / 294, 37))
mk = lauf_zeitreihe(sig=0.0, jit=0.0)
soll = (Fzk * np.exp(-1j * np.radians(np.array([0, 120, 240]))[:, None, None] * kz)).sum(0) * 2   # (Zelle, K)
print('Zeitreihe ohne Rauschen/Jitter gegen Harmonische: max|Δ| Zellen = %.2e N, Summe = %.2e N'
      % (np.abs(mk[:3] - soll).max(), np.abs(mk[3] - soll.sum(0)).max()))
