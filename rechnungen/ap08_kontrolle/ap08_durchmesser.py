import numpy as np, linear_solver as L
P, n = L.profile_spectrum(); mu, M = 0.4, L.M
phi2 = np.arange(100, 140.1, 2.0)
for kk in (1, 2, 3):
    c = (1 + np.exp(-1j*kk*np.radians(phi2)) + np.exp(-1j*kk*np.radians(240.0)))/3
    z = 2*mu*M*P[kk]*c/n
    d = np.abs(z[:, None] - z[None, :]).max()
    print(kk, 'max|N|', round(np.abs(z).max(), 4), 'Durchmesser', round(d, 4), 'Delta_B', round(0.25*d, 4), 'Kamm min/max', round(np.abs(c).min(),4), round(np.abs(c).max(),4), 'Verhältnis Durchmesser/max', round(d/np.abs(z).max(),3))
