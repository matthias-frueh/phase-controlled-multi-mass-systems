"""v2_fmin_zeitreihe_mc.py – Gegenprüfung STA-02 (F_min-Schätzer, Extremwert-Bias) mit eigener Implementierung.

Unterschiede zur Gruppe (s1): eigene Zeitreihen-Erzeugung mit zufälligem Sub-Sample-Versatz, Jitter als
zyklusweise Verschiebung von Modul 2 und 3, eigene Segmentierung + lineare Interpolation auf N_θ = 2000
(A9.4 Schritt 3–4), DFT-Abschneiden (Schritt 5). Wahrheit zweifach:
  (i)  Soll-Kurve mit Jitterdämpfung e^{−k²σ²/2} (Erwartungswert) – das ist die Wahrheit der Gruppe;
  (ii) Kurve mit den im Lauf GEMESSENEN Zeigern ρ_jk = ⟨e^{−ik(φ_j+ε_jc)}⟩_c – das ist die Größe, gegen die die
       registrierte Vorhersage (§8.2, A9.5) tatsächlich verglichen wird.
Verfahren A: Mittelkurve, k ≤ k_max (9 oder ohne Begrenzung = 1000), Minimum − Mittel.
Verfahren B: Rohminimum der Abtastwerte je Zyklus, über Zyklen gemittelt, minus Laufmittel.
Aufruf: python3 v2_fmin_zeitreihe_mc.py [R]
"""
import os
import sys
import numpy as np

M, G = 0.650, 9.81
MG = M * G
F = 10.0
T = 1 / F
RTOP, THOLD = 0.005, 0.65
TFAST = 1 - THOLD
RBOT = RTOP * TFAST / THOLD
MU = 0.4
A_HOLD = -RTOP * (np.pi / (THOLD * T)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T)) ** 2


def accel(t):
    p = np.mod(t, T) / T
    return np.where(p < THOLD, A_HOLD * np.sin(np.pi * p / THOLD), A_FAST * np.sin(np.pi * (p - THOLD) / TFAST))


NTH = 2000
th = np.arange(NTH) / NTH * T
NFINE = 16000
tf = np.arange(NFINE) / NFINE * T
Cmod = np.fft.rfft(MU * M / 3 * accel(tf)) / NFINE        # Fourierkoeffizienten (x = Σ C_k e^{ikωt}, rfft-Konv.)


def curve_from_rho(rho, kmax):
    """N(θ) − ⟨N⟩ auf NTH Punkten aus Zeigern rho (3 × K_all) für Module j; Bandbegrenzung kmax."""
    K = Cmod.size
    X = (Cmod[None, :] * rho).sum(0)
    X[0] = 0
    if kmax is not None:
        X[kmax + 1:] = 0
    x = np.fft.irfft(X * NFINE, NFINE)
    return x[:: NFINE // NTH]


R = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = np.random.default_rng(424242)
FS, NZ = 6400, 100
NS = int(FS * T)
kall = np.arange(Cmod.size)
res = []
lines = []
for phi2 in (100.0, 116.0, 120.0):
    phis = np.radians([0.0, phi2, 240.0])
    tau = phis / (2 * np.pi * F)
    for sig_t in (0.0, 56e-6):
        sj = 2 * np.pi * F * sig_t                                  # Jitter in rad
        rho_soll = np.exp(-1j * np.outer(phis, kall)) * np.exp(-0.5 * (kall * sj) ** 2)[None, :]
        rho_soll[0] = np.exp(-1j * phis[0] * kall)                  # Modul 1 ohne Jitter (definiert θ)
        truth = {km: curve_from_rho(rho_soll, km).min() for km in (9, None)}
        for sig in (0.005, 0.020):
            acc = {key: [] for key in ('A9_soll', 'A9_rho', 'Aoff_soll', 'Aoff_rho', 'B_soll')}
            for r in range(R):
                t0 = rng.uniform(0, 1 / FS)
                ts = t0 + np.arange(NZ * NS + 2) / FS - 1 / FS            # Abtastzeitpunkte (Index von Modul 1 bei cT)
                eps = rng.normal(0, sig_t, (3, NZ + 2))
                eps[0] = 0.0
                # Jitter je eigenem Zyklus von Modul j (Zyklusgrenze bei t = cT + τ_j)
                cyc_j = [np.floor((ts - tau[j]) / T).astype(int).clip(-1, NZ) + 1 for j in range(3)]
                x = MG + sum(MU * M / 3 * accel(ts - tau[j] - eps[j, cyc_j[j]]) for j in range(3))
                x = x + rng.normal(0, sig, ts.size)
                # Segmentierung + lineare Interpolation auf NTH Stützstellen je Zyklus
                tq = (np.arange(NZ)[:, None] * T + th[None, :]).ravel()
                y = np.interp(tq, ts, x).reshape(NZ, NTH)
                mc = y.mean(0)
                Xm = np.fft.rfft(mc)
                mean = Xm[0].real / NTH
                rho_run = np.exp(-1j * np.outer(phis, kall))[:, :] * 1.0
                for j in (1, 2):
                    rho_run[j] = np.exp(-1j * kall * phis[j]) * np.exp(-1j * np.outer(kall, 2 * np.pi * F * eps[j, 1:NZ + 1])).mean(1)
                for km, tag in ((9, 'A9'), (None, 'Aoff')):
                    X = Xm.copy()
                    if km is not None:
                        X[km + 1:] = 0
                    fm = np.fft.irfft(X, NTH).min() - mean
                    acc[tag + '_soll'].append(fm - truth[km])
                    acc[tag + '_rho'].append(fm - curve_from_rho(rho_run, km).min())
                # Verfahren B: Rohminimum je Zyklus (Abtastwerte im Zyklus)
                xin = x[1:1 + NZ * NS]                                   # ts[1] = t0 ≥ 0: genau NS Abtastwerte je Zyklus
                assert ts[1] >= 0 and ts[NZ * NS] < NZ * T
                cm = xin.reshape(NZ, NS).min(1)
                acc['B_soll'].append(cm.mean() - xin.mean() - truth[None])
            row = dict(phi2=phi2, jitter_us=sig_t * 1e6, sigma_mN=sig * 1e3)
            for key, v in acc.items():
                v = np.array(v) * 1e3
                row[key + '_bias'] = v.mean()
                row[key + '_sd'] = v.std(ddof=1)
            res.append(row)
            ln = (f'φ₂={phi2:5.1f}° Jitter={sig_t*1e6:3.0f} µs σ={sig*1e3:4.0f} mN | '
                  + ' | '.join(f'{k}: {row[k+"_bias"]:+7.3f} ± {row[k+"_sd"]/np.sqrt(R):.3f} (sd {row[k+"_sd"]:.3f})'
                               for k in acc))
            print(ln, flush=True)
            lines.append(ln)
# Rauschfreier Interpolationsanteil bei 6,4 kHz
ln2 = []
for phi2 in (100.0, 116.0, 120.0):
    phis = np.radians([0.0, phi2, 240.0])
    tau = phis / (2 * np.pi * F)
    rho = np.exp(-1j * np.outer(phis, kall))
    tr = curve_from_rho(rho, 9).min()
    vals = []
    for t0 in np.linspace(0, 1 / FS, 8, endpoint=False):
        ts = t0 + np.arange(NS + 4) / FS - 2 / FS
        x = MG + sum(MU * M / 3 * accel(ts - tau[j]) for j in range(3))
        y = np.interp(th, ts, x)
        X = np.fft.rfft(y)
        X[10:] = 0
        vals.append(np.fft.irfft(X, NTH).min() - X[0].real / NTH - tr)
    ln2.append(f'rauschfrei, f_s = 6,4 kHz, k_max = 9, φ₂ = {phi2:.0f}°: Interpolationsanteil {1e3*np.mean(vals):+.3f} mN '
               f'(Spanne {1e3*min(vals):+.3f} … {1e3*max(vals):+.3f})')
    print(ln2[-1])
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_fmin_zeitreihe_mc_ausgabe.txt'), 'w').write(
    f'R = {R} Läufe je Zelle, f_s = {FS} Hz, N_z = {NZ}; Werte in mN: Bias ± MC-Standardfehler (sd je Lauf)\n'
    + '\n'.join(lines + ln2) + '\n')
import csv
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v2_fmin_zeitreihe_mc.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
    w.writeheader()
    w.writerows(res)
