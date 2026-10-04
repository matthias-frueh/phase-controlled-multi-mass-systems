"""
a5b_kontaktanteil_mu.py – Gegenprobe Präreg A3 („48,6 % bei K = 10⁴ N/m und μ = 0,5“): Anteil des
1°-Phasenrasters mit Kontaktast bei der Referenzsteifigkeit für μ = 1; 0,5; 0,4 mit code/linear_solver.py
(contact_map, nur gelesen/importiert). Ausgabe: a5_kontaktanteil_mu_ausgabe.txt. Laufzeit < 30 s.
"""
import os
import linear_solver as ls

HERE = os.path.dirname(os.path.abspath(__file__))
lines = []
for mu in (1.0, 0.5, 0.4):
    _, F, z, v = ls.contact_map(1.0, mu=mu)
    lines.append(f'K=1e4, mu={mu:.1f}: Kontaktast {100 * v.mean():.2f} % (F_min>0 und z<0), F_min>0 allein '
                 f'{100 * (F > 0).mean():.2f} %, Reserve>=25% {100 * (F >= 0.25 * ls.MG).mean():.2f} %')
print('\n'.join(lines))
with open(os.path.join(HERE, 'a5_kontaktanteil_mu_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
