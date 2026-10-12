"""
v1_zeitbereich.py – Gegenprüfung NR-04/NR-08: Nadelkräfte der Belegung B im Zeitbereich.

Eigener Rechenweg, unabhängig von nr_modell.py (das nur als Vergleichsziel importiert wird):
- Geometrie als ausgeschriebene Tabelle (Fixierstellen, Druckrichtungen), nicht aus Versatzregeln erzeugt.
- Massenmatrix als Summe räumlicher Trägheiten von Punktmassen, M_i = m·[[I, −[r]×], [[r]×, −[r]×[r]×]], plus
  Trägerträgheit; Steifigkeit Σ k·g·gᵀ.
- Modulbeschleunigung direkt aus der Egg-Formel (Halte- und Schnellphase als Sinusbögen), keine FFT.
- Integration der vollen Bewegungsgleichung M6·ẍ + β·K·ẋ + K·x = w_g − w_mod(t) mit DOP853 (rtol 1e-11) aus der
  statischen Ruhelage über 30 Perioden; Vergleich der letzten Periode (400 Zeitpunkte) mit der stationären
  Frequenzbereichslösung von nr_modell.antwort. Dazu der starre Grenzfall λ(t) = G⁻¹·(−w_g + w_mod(t)).
  Das Vergleichsziel wird mit n = 4000, 16 000 und 64 000 Stützstellen je Periode gebildet, um den Abbruch der
  Profilreihe vom Modellfehler zu trennen.

Parameter wie nr_modell (V1-Kandidat, Lage G0, ρ0 = 80 mm isotrop, k_a = 10⁶ N/m, ζ = 0,02 an der tiefsten Mode).
Laufzeit gut 1 min; schreibt keine Dateien.
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import nr_modell as ziel            # noqa: E402  (nur Vergleichsziel)

g0 = 9.81
f, hub, thold = 10.0, 8e-3, 0.65
m_mod, m0, rho0 = 0.1, 0.35, 0.08
k_a, zeta = 1e6, 0.02
T = 1.0 / f

# Belegung B als Tabelle: (Name, Fixierstelle [m], Druckrichtung auf den Körper)
NADELN = [('Nord', (0.0, 0.15, 0.04), (0, -1, 0)), ('Süd', (0.0, -0.15, -0.04), (0, 1, 0)),
          ('Ost', (0.15, 0.04, 0.0), (-1, 0, 0)), ('West', (-0.15, -0.04, 0.0), (1, 0, 0)),
          ('oben', (0.04, 0.0, 0.15), (0, 0, -1)), ('unten', (-0.04, 0.0, -0.15), (0, 0, 1))]
Gm = np.array([np.r_[n, np.cross(r, n)] for _, r, n in NADELN], float).T
K = k_a * Gm @ Gm.T

R_mod = np.array([[0.1 * np.cos(p), 0.1 * np.sin(p), 0.0] for p in np.radians([0.0, 120.0, 240.0])])


def x_(r):
    return np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])


def raeumlich(m, r):
    X = x_(r)
    return m * np.block([[np.eye(3), -X], [X, -X @ X]])


M6 = raeumlich(m0, np.zeros(3)) + sum(raeumlich(m_mod, r) for r in R_mod)
M6[3:, 3:] += m0 * rho0 ** 2 * np.eye(3)
M_ges = m0 + 3 * m_mod
w_g = np.r_[0.0, 0.0, -M_ges * g0, np.zeros(3)]             # Schwerpunkt in O (symmetrische Lage G0)

w2, _ = eigh(K, M6)
beta = 2 * zeta / np.sqrt(w2[0])
print(f'Eigenfrequenzen [Hz]: {np.round(np.sqrt(w2) / (2 * np.pi), 2).tolist()};  β = {beta:.4e} s')


def a_egg(t, phi_deg):
    s = np.mod(f * t - phi_deg / 360.0, 1.0)
    tf = 1.0 - thold
    a = np.where(s < thold, -np.pi ** 2 / thold * np.sin(np.pi * s / thold),
                 np.pi ** 2 / tf * np.sin(np.pi * (s - thold) / tf))
    return hub * f ** 2 * a


def w_mod(t, phis):
    a = np.array([a_egg(t, p) for p in phis])                  # (3, …)
    F = np.zeros((6,) + np.shape(t))
    F[2] = m_mod * a.sum(0)
    mom = np.cross(R_mod, np.array([0.0, 0.0, 1.0]))           # R_i × e_z
    F[3:] = m_mod * np.einsum('ic,i...->c...', mom, a)
    return F


Minv = np.linalg.inv(M6)
x0 = np.linalg.solve(K, w_g)


def rhs(t, y, phis):
    x, v = y[:6], y[6:]
    return np.r_[v, Minv @ (w_g - w_mod(t, phis) - K @ (x + beta * v))]


zeiten = 29 * T + np.arange(400) * T / 400
th = 2 * np.pi * f * (zeiten - 29 * T)
RB = ziel.rahmen('B')
N_ZIEL = (4000, 16000, 64000)
ziele = {n: ziel.Koerper(n=n) for n in N_ZIEL}


def reihe(lam):
    """Fourier-Reihe an den Vergleichszeitpunkten; ohne den Nyquist-Term (k = n/2)."""
    kk = np.arange(lam.shape[1] - 1)
    return lam[:, :1].real + 2 * np.real(lam[:, 1:-1] @ np.exp(1j * np.outer(kk[1:], th)))


print('Vergleich mit nr_modell bei n Stützstellen je Periode (Profilreihe bis k = n/2), max|Δλ| über Nadeln und Zeit [N]')
print('Konfig.  Lösung        ' + '  '.join(f'n = {n:<7d}' for n in N_ZIEL))
ergebnis = {}
for name, phis in (('T', (0.0, 120.0, 240.0)), ('Z', (0.0, 110.0, 240.0)), ('S', (0.0, 0.0, 0.0))):
    sol = solve_ivp(rhs, (0.0, 30 * T), np.r_[x0, np.zeros(6)], method='DOP853', rtol=1e-11, atol=1e-15,
                    max_step=T / 400, t_eval=zeiten, args=(phis,))
    x, v = sol.y[:6], sol.y[6:]
    lam_zeit = -k_a * Gm.T @ (x + beta * v)                    # Rahmendynamik, Zeitbereich
    starr_zeit = np.linalg.solve(Gm, -w_g[:, None] + w_mod(zeiten, phis))   # starrer Grenzfall, analytisch
    d_dyn = [np.abs(lam_zeit - reihe(ziel.antwort(ziele[n], RB, phis))).max() for n in N_ZIEL]
    d_st = [np.abs(starr_zeit - reihe(ziel.antwort(ziele[n], RB, phis, starr=True))).max() for n in N_ZIEL]
    ergebnis[name] = (d_dyn, d_st)
    print(f'{name:7s}  dynamisch     ' + '  '.join(f'{d:.2e}   ' for d in d_dyn) + f'(nfev {sol.nfev})')
    print(f'{"":7s}  starr         ' + '  '.join(f'{d:.2e}   ' for d in d_st))
    print(f'{"":7s}  Spanne λ_unten (Zeitbereich) {lam_zeit[5].min():+.4f} … {lam_zeit[5].max():+.4f} N')
fein = max(max(v[0][-1], v[1][-1]) for v in ergebnis.values())
abnahme = min(v[i][0] / v[i][-1] for v in ergebnis.values() for i in (0, 1) if v[i][-1] > 1e-12)
print(f'größte Abweichung bei n = {N_ZIEL[-1]}: {fein:.2e} N; kleinste Abnahme von n = {N_ZIEL[0]} auf {N_ZIEL[-1]}: '
      f'Faktor {abnahme:.1f}')
print('Die Restabweichung ist der Abbruch der Fourier-Reihe des Profils (die Ableitung der Beschleunigung springt an den')
print('Phasennähten); sie fällt hier etwa wie 1/n² (Faktor 16 je vierfacher Stützstellenzahl). Bei S liegen die')
print('Vergleichszeitpunkte ohne Phasenverschiebung auf dem Stützstellenraster; dort ist die starre Reihe fast exakt.')
print(f'Urteil: {"bestätigt" if fein < 1e-5 and abnahme > 8 else "NICHT bestätigt"} (Schwelle 1e-5 N bei n = {N_ZIEL[-1]}, '
      f'Abnahme > 8)')
