#!/usr/bin/env python3
"""Gegenprüfung LB-10/LB-11: konsistente Vergleichsskalen. u_c nach Präreg-Anhang A4/A8 (PB1, nu -> inf):
u_c <= 0,25*DeltaF_Zelt / z(1 - 0,05/294), je Szenario mit dem DeltaF_Zelt DESSELBEN Szenarios (A4-Tabelle:
starr mu=0,4: 0,4693 N; Referenz K=1e4, mu=1: 4,5627 N). Dazu f_n-Verschiebung durch Zusatzmassen und die
Mindeststeifigkeit aus Präreg §5.3(b) (3f <= f1/2 -> f1 >= 60 Hz bei f = 10 Hz)."""
import numpy as np
from scipy.stats import norm
z = norm.ppf(1 - 0.05 / 294)
for name, dz in [('starr mu=0,4', 0.4693), ('K=1e4 mu=1', 4.5627)]:
    print(name, 'Delta=', round(0.25 * dz, 4), 'u_c<=', round(0.25 * dz / z, 4))
M = 0.65
for m in (1.94e-3, 4.6e-3, 8.0e-3, 29.25e-3):
    print('m=%.2f g: f_n-Verschiebung %.3f %%' % (m * 1e3, (1 / np.sqrt(1 + m / M) - 1) * 100))
print('K fuer f1>=60 Hz:', M * (2 * np.pi * 60) ** 2)
