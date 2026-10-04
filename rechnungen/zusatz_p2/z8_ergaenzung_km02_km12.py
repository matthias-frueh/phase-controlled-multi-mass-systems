"""z8_ergaenzung_km02_km12.py - Ergaenzungen:
 (A) KM-02/KM-07: Entkopplung bei mu = 1, G0 auch mit einseitigem Kontakt je Zelle. Eigene 3-FG-RK4 (q-Koordinaten,
     einseitig je Zelle) ueber 0,1 s gegen eine 1-FG-Schleife mit der unveraenderten Engine-rechten-Seite
     (finesweep.rhs) bei (0, 0): Zelle 1 = Engine/3.
 (B) KM-12/KM-04: Betrag |M(t)| (quasistatisch, Egg) und Netto-Umlaufzahl mit Kippdynamik (REF, mu = 1, G0).
"""
import numpy as np
import zm
import finesweep as fs

# (A)
geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=1.0)
K, C = zm.K_REF, zm.C_REF
Minv = np.linalg.inv(geo.Mq)
mvec = geo.Bm @ geo.m
tau = np.radians([0.0, 120.0, 240.0]) / zm.OMEGA


def f3(q, v, t):
    w, wd = geo.Bc.T @ q, geo.Bc.T @ v
    Fs = -(K / 3) * w - (C / 3) * wd
    Fc = np.where((w < 0) & (Fs > 0), Fs, 0.0)
    acc = Minv @ (-zm.G * mvec + geo.Bc @ Fc - geo.Bm @ (geo.m * zm.accel(t - tau)))
    return v, acc, Fc


q = np.linalg.solve(geo.Kq(K), -zm.G * mvec); v = np.zeros(3)
z, zd = np.array([-zm.MG / K]), np.zeros(1)
DT = 5e-5
dmax = []
null1 = 0
for i in range(int(round(1.0 / DT))):
    t = i * DT
    a1, b1, F3 = f3(q, v, t)
    a2, b2, _ = f3(q + 0.5 * DT * a1, v + 0.5 * DT * b1, t + 0.5 * DT)
    a3, b3, _ = f3(q + 0.5 * DT * a2, v + 0.5 * DT * b2, t + 0.5 * DT)
    a4, b4, _ = f3(q + DT * a3, v + DT * b3, t + DT)
    k1z, k1d, F1 = fs.rhs(z, zd, t, np.zeros(1), np.zeros(1))
    k2z, k2d, _ = fs.rhs(z + 0.5 * DT * k1z, zd + 0.5 * DT * k1d, t + 0.5 * DT, np.zeros(1), np.zeros(1))
    k3z, k3d, _ = fs.rhs(z + 0.5 * DT * k2z, zd + 0.5 * DT * k2d, t + 0.5 * DT, np.zeros(1), np.zeros(1))
    k4z, k4d, _ = fs.rhs(z + DT * k3z, zd + DT * k3d, t + DT, np.zeros(1), np.zeros(1))
    dmax.append(abs(F3[0] - F1[0] / 3))
    null1 += F3[0] == 0.0
    q = q + DT * (a1 + 2 * a2 + 2 * a3 + a4) / 6; v = v + DT * (b1 + 2 * b2 + 2 * b3 + b4) / 6
    z = z + DT * (k1z + 2 * k2z + 2 * k3z + k4z) / 6; zd = zd + DT * (k1d + 2 * k2d + 2 * k3d + k4d) / 6
dmax = np.array(dmax)
print('(A) mu=1, G0, einseitig je Zelle, Triphasik-Phasen: |F_Zelle1 - F_Engine(0,0)/3|')
for tt in (0.1, 0.5, 1.0):
    n = int(round(tt / DT))
    print(f'   bis {tt:.1f} s: max {dmax[:n].max():.2e} N')
print(f'   Anteil Stichproben ohne Kontakt in Zelle 1 (1. s): {null1/len(dmax):.3f}')

# (B)
print('\n(B) |M(t)| am Triphasik-Punkt, Egg, G0')
t = np.arange(8000) * zm.T_CYC / 8000
for lab, K_, C_, mu in (('STARR', None, None, 0.462), ('STEIF', zm.K_ST, zm.C_ST, 0.462), ('REF', zm.K_REF, zm.C_REF, 1.0)):
    geo = zm.Geo(Rm=zm.R_C, psi0=0.0, mu=mu)
    g = zm.module_phasors(geo, (0, 120, 240), 300)
    F = zm.cell_phasors(geo, g, K_, C_)
    Mx, My = zm.moments(geo, zm.synth(F, t))
    A = np.hypot(Mx, My)
    ang = np.unwrap(np.arctan2(My, Mx))
    print(f'   {lab:5s} mu={mu}: |M| min {A.min():.4f}, max {A.max():.4f} N m, max/min {A.max()/A.min():.2f}; '
          f'Netto-Umlaeufe je Periode {(ang[-1]-ang[0])/(2*np.pi) + (ang[1]-ang[0])/(2*np.pi):+.2f}; '
          f'Mittel Mx, My {Mx.mean():.1e}, {My.mean():.1e}')
