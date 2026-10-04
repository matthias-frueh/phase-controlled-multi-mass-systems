"""Gegenprüfung ENG-08: Langläufe der aperiodischen 'niedrigen' Zustände mit SA (P13B 43,7 %, P45 ~35 %,
Bahn 44 ~36 %) über 100 s ab RK4-S-Endzustand (40 s) bzw. ab Standardstart; Floquet der P33-Zustände.
Aufruf: python3 vk_langlauf.py lang | floquet33
"""
import os
import sys
import numpy as np
import pandas as pd
import vk_model as m
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
D = 360.0 / 19


def lang():
    L = []
    cases = [('P13B std ab t=0', 13, 0, None), ('P45B ramp2 ab 40 s', 14, 2, 'ramp2'), ('P45A std ab 40 s', 12, 17, 'std'),
             ('Bahn44 (6,8) std ab 40 s', 6, 8, 'std')]
    for nm, i, j, st in cases:
        s = sa.SA(i * D, j * D)
        if st is None:
            R = s.run(-m.MG / m.K, 0.0, 0.0, 1000); t0 = 0.0
        else:
            g = pd.read_csv(OUT + f'vk_grid_{st}.csv')
            row = g[(g.i2 == i) & (g.i3 == j)].iloc[0]
            R = s.run(row.z_end, row.zd_end, 40.0, 1000); t0 = 40.0
        blocks = [sa.stats(R, c, c + 100)['lam'] for c in range(0, 1000, 100)]
        per = sa.period(R, n_last=100, pmax=60, tol_v=1e-8, tol_z=1e-10)
        L.append(f'{nm}: lambda je 10 s ab {t0:.0f} s: ' + ' '.join(f'{b:.2f}' for b in blocks)
                 + f'; Periode (Tol 1e-8) {per[0]}; touchdowns/Zyklus {sa.stats(R, 900, 1000)["td"]:.2f}')
        print(L[-1], flush=True)
    open(OUT + 'vk_langlauf_ausgabe.txt', 'w').write('\n'.join(L) + '\n')


def floquet33():
    L = []
    for nm, (i, j), v0f, p in (('P33A std (P3)', (1, 16), 'std', 3), ('P33A imp (P1)', (1, 16), 'imp', 1),
                               ('P13B imp (P1)', (13, 0), 'imp', 1), ('P6B std (P1)', (13, 13), 'std', 1)):
        s = sa.SA(i * D, j * D)
        v0 = 0.0 if v0f == 'std' else -float(m.ebar_v(0.0, s.taus))
        R = s.run(-m.MG / m.K, v0, 0.0, 300)
        x, mu, rr = sa.floquet(s, [R['PZ'][-1], R['PV'][-1]], 30.0, p=p)
        R2 = s.run(x[0], x[1], 0.0, 3 * p)
        st = sa.stats(R2, 0, 3 * p)
        L.append(f'{nm}: |mu| = {", ".join(f"{abs(v):.4f}" for v in mu)}; Residuen {rr[0]:.0e} -> {rr[-1]:.0e}; '
                 f'Orbit lam {st["lam"]:.4f} %, gamma1 {st["skew"]:.4f}, F_max {st["Fmax"]:.2f} N')
        print(L[-1], flush=True)
    open(OUT + 'vk_floquet_paare_ausgabe.txt', 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    {'lang': lang, 'floquet33': floquet33}[sys.argv[1]]()
