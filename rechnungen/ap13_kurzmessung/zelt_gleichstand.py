"""Abweichungen Kandidatenverfahren ↔ Prüferfassung: RSS an beiden φ* mit explizitem lstsq (unabhängig)."""
import numpy as np
from zelt_schnell import zelt_kand, testsatz
src = open('m_zelt2.py', encoding='utf-8').read().split('for w in (6, 8, 20):')[0]
ns = {}; exec(src, ns); zp = ns['zelt_seg']


def rss_lstsq(x, y, p):
    A = np.c_[np.ones_like(x), -np.maximum(p - x, 0), -np.maximum(x - p, 0)]
    r = y - A @ np.linalg.lstsq(A, y, rcond=None)[0]
    return r @ r


rng = np.random.default_rng(613)
worst = 0.0; nmis = 0; besser_p = 0
for w in (6, 8, 20):
    for art in ('asym', 'sym', 'sym_fein', 'rauschen', 'gerade', 'knick_flach'):
        R = 300 if w < 20 else 100
        X, Y = testsatz(rng, R, w, art)
        a, c = zelt_kand(X, Y), zp(X, Y)
        for i in np.flatnonzero(np.abs(a - c) > 1e-6):
            ra, rc = rss_lstsq(X[i], Y[i], a[i]), rss_lstsq(X[i], Y[i], c[i])
            rel = (ra - rc) / max(ra, rc, 1e-300)
            nmis += 1; besser_p += rel > 1e-9
            worst = max(worst, rel)
            if rel > 1e-9 or art in ('sym',):
                print(f'w={w} {art} i={i}: φ*_kand={a[i]:.3f} RSS={ra:.6e}, φ*_prüf={c[i]:.3f} RSS={rc:.6e}, rel={rel:.2e}')
print(f'{nmis} Abweichungen; Prüferfassung mit relativ kleinerer RSS (> 1e-9) in {besser_p}; größtes (RSS_kand − RSS_prüf)/RSS = {worst:.2e}')
