"""P3 bewertung_b, Kandidat 42 (B10): Auswahlregel der Harmonischen fuer N Module.
(a) Summenkanal: (1/N) sum_j exp(-i k phi_j) mit gleichverteilten Phasen -> nur k = 0 mod N.
(b) Paarweise Gegenphase (N gerade) -> ungerade k geloescht.
(c) [E, eigene Verallgemeinerung von KM-03] N Module auf einem Ring an theta_j = 2 pi j/N,
    Phasen phi_j = 2 pi j/N: die azimutale Lastmode m der Zellkraefte enthaelt nur
    Harmonische k = m (mod N) (bzw. k = -m fuer die konjugierte Mode).
Reine Phasenfaktoren (linearer Dauerkontakt, identische Module); keine Dynamik.
"""
import numpy as np

def P_sum(k, phis):
    return np.mean(np.exp(-1j * k * phis))

def P_mode(k, m, phis, thetas):
    return np.mean(np.exp(-1j * k * phis) * np.exp(1j * m * thetas))

for N in (3, 4, 6, 8):
    phis = 2 * np.pi * np.arange(N) / N
    ks = [k for k in range(1, 13) if abs(P_sum(k, phis)) > 1e-9]
    print(f"N={N}: gleichverteilt, Summe enthaelt k = {ks}")
    if N % 2 == 0:
        anti = np.array([0.0, np.pi] * (N // 2)) + np.repeat(np.linspace(0, np.pi / 2, N // 2), 2)
        ka = [k for k in range(1, 13) if abs(P_sum(k, anti)) > 1e-9]
        print(f"      paarweise Gegenphase (Paarlagen beliebig), Summe enthaelt k = {ka}")
    thetas = phis.copy()
    for mm in range(0, N // 2 + 1):
        km = [k for k in range(1, 13) if abs(P_mode(k, mm, phis, thetas)) > 1e-9]
        print(f"      azimutale Mode m={mm}: k = {km}")
