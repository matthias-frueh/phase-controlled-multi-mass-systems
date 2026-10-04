"""AP-08: Zahlen für den Entwurf der Entscheidungsregeln (A4-Beispiel, starr, mu = 0,4, 10 Hz)."""
import numpy as np
from scipy.stats import norm, t, chi2
from scipy import integrate, optimize
import linear_solver as L

# 1) Auslegungsgrenzen
p = 0.8 ** (1 / 147)
R_new_inf = norm.ppf(0.95) + norm.ppf((1 + p) / 2)
c_inf = norm.ppf(1 - 0.05 / 294)
R_old_inf = c_inf + norm.ppf((1 + p) / 2)


def p_test(R, nu, rule):
    """P(Bedingung erfüllt | exakt) je Test; r ~ N(0,1), u_hat^2 ~ chi2_nu/nu; Delta = R (in Einheiten u)."""
    if rule == 'new':
        te = t.ppf(0.95, nu)
        f = lambda s: (2 * norm.cdf(R - te * s) - 1) * (R - te * s > 0)
    else:
        c = t.ppf(1 - 0.05 / 294, nu)
        f = lambda s: (2 * norm.cdf(np.minimum(R - c * s, c * s)) - 1) * (np.minimum(R - c * s, c * s) > 0)
    # Dichte von s = u_hat/u
    dens = lambda s: chi2.pdf(nu * s * s, nu) * 2 * nu * s
    v, _ = integrate.quad(lambda s: f(s) * dens(s), 0, 5, limit=400, points=[R / (t.ppf(0.95, nu) if rule=='new' else 2*t.ppf(1-0.05/294,nu))])
    return v


def R_for(nu, rule):
    return optimize.brentq(lambda R: p_test(R, nu, rule) - p, 2, 20)


print('p je Test', p)
print('neu   nu=inf R =', round(R_new_inf, 3), ' nu=19 R =', round(R_for(19, 'new'), 3), ' nu=37 R =', round(R_for(37, 'new'), 3))
print('alt   nu=inf R =', round(R_old_inf, 3), ' nu=19 R =', round(R_for(19, 'old'), 3))
print('t_eq inf/19/37', round(norm.ppf(0.95), 3), round(t.ppf(0.95, 19), 3), round(t.ppf(0.95, 37), 3))
print('Fehlbestätigung PB1 alt je Test am Rand: Phi(-c) =', '%.2g' % norm.sf(c_inf))

# 2) A4-Beispiel bandbegrenzt
P, n = L.profile_spectrum()
mu, M = 0.4, L.M
KM = 9
Pb = P.copy(); Pb[KM + 1:] = 0
phi2 = np.arange(100, 140.1, 2.0)
k = np.arange(P.size)
comb = (1 + np.exp(-1j * np.outer(np.radians(phi2), k)) + np.exp(-1j * k * np.radians(240.0))) / 3
F = L.MG + mu * M * np.fft.irfft(Pb * comb, n, axis=1)
Fmin = F.min(1) - L.MG
D_F = Fmin.max() - Fmin.min()
print('k_max=9: D_F =', round(D_F, 4), 'Delta_F =', round(0.25 * D_F, 4))
Nk = 2 * mu * M * Pb[None, :] * comb / n      # komplexe Amplituden N_k (Konvention |N_k| wie --section)
for kk in (1, 2, 3):
    z = Nk[:, kk]
    A = np.abs(z).max()
    sre = z.real.max() - z.real.min(); sim = z.imag.max() - z.imag.min()
    print(f'k={kk}: max|N_k| = {A:.4f}  Delta_A = {0.25*A:.4f};  Spannweite Re = {sre:.4f}, Im = {sim:.4f} -> Delta_B Re {0.25*sre:.4f}, Im {0.25*sim:.4f}; Einzelmodul |N_k| = {np.abs(2*mu*M*P[kk]/3/n):.4f}; Kammfaktor max = {np.abs(comb[:,kk]).max():.4f}')
D = 0.25 * D_F
for nu, Rn in ((np.inf, R_new_inf), (19, R_for(19, 'new'))):
    te = norm.ppf(0.95) if nu == np.inf else t.ppf(0.95, nu)
    print(f'nu={nu}: notwendig u < Delta/t_eq = {1e3*D/te:.1f} mN; Auslegung u <= Delta/R = {1e3*D/Rn:.1f} mN; N1 (A): {1e3*0.25*np.abs(Nk[:,1]).max()/Rn:.1f} mN')
print('Überdeckungsschwelle 0,95 - 2 SE(1000):', round(0.95 - 2 * (0.95 * 0.05 / 1000) ** 0.5, 3))
