"""
k2c_phasen.py – Befund KM-04 (Phasen): komplexe Zeiger der links (P+) und rechts (P−) umlaufenden
Momentkomponenten am Triphasik-Punkt, G0, R_c = 100 mm. arg = Winkel des Teilvektors bei t = 0
(Zelle 1 auf der x-Achse). Analytisch (quasistatisch): arg P+_1 = arg c_1 − 90°, arg P−_2 = −arg c_2 − 90°.
"""
import numpy as np
from km_modell import Geo, linear, M
K_ST = 369518.0
C_ST = 2 * 0.02 * np.sqrt(K_ST * M)
for lab, K, C, mu, st in (('STARR', 1, 0, 0.462, True), ('STEIF', K_ST, C_ST, 0.462, False), ('REF', 1e4, 16.0, 1.0, False)):
    geo = Geo(R_c=0.1, mu=mu)
    r = linear(geo, (0, 120, 240), K=K, C=C, starr=st)
    X, Y = r['Mxk'], r['Myk']
    for k in range(1, 7):
        Pp = X[k] + 1j * Y[k]
        Pm = np.conj(X[k]) + 1j * np.conj(Y[k])
        print(f'{lab} μ={mu} k={k}: links |P+|={abs(Pp):.5f} N·m arg={np.degrees(np.angle(Pp)):8.2f}°   '
              f'rechts |P−|={abs(Pm):.5f} arg={np.degrees(np.angle(Pm)):8.2f}°')
print('(arg bei Betrag ≈ 0 ohne Bedeutung)')
