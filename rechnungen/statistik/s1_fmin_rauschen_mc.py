"""s1_fmin_rauschen_mc.py – Monte Carlo eines einzelnen Laufs auf Zeitreihenebene: Wie streut und wie verzerrt
ist F_min − ⟨N⟩ bei weißem Sensorrauschen, Abtastrate, Zyklenzahl, Phasenjitter und Bandbegrenzung, je nach
Schätzverfahren?

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code (linear_solver.py, finesweep.py).

Modell (Annahmen, eigene Festlegung):
- Beispiel A4: starre Auflage, μ = 0,4, f = 10 Hz, Egg-Profil der Engine, identische Module;
  Modul j trägt h(t − τ_j − δ_{j,c}) bei, h = (μM/3)·a(t) (A2.1, A2.5), τ_j = φ_j/(2πf).
- Phasenjitter: Modul 2 und 3 je Zyklus c um δ_{j,c} ~ N(0, σ_t²) verschoben (gegen Modul 1, das die
  Zyklusphase definiert); σ_t = 0 oder 56 µs (Budget Anforderungsprofil F5, = 0,2° bei 10 Hz).
- Sensorrauschen: weiß, normalverteilt, σ je Abtastwert des Summenkanals N, σ ∈ {1, 5, 20} mN
  (Bestand: Werkzeug_PCMMFM_PreValidation §6 nennt elektrisch 1–5 mN, mechanisch 5–30 mN, Umgebung
  3–20 mN; Anforderungsprofil F1 verlangt Auflösung ≤ 0,005·Mg ≈ 32 mN).
- Abtastrate f_s ∈ {2000, 6400, 10000} Hz (f_s/f ganzzahlig), zufälliger Sub-Sample-Versatz je Lauf.
- Zyklenzahl N_z ∈ {10, 100} (T_a = 1 s bzw. 10 s).
Verfahren:
- A (Präreg §4/A9.4): je Zyklus lineare Interpolation auf N_θ = 2000, phasensynchrones Mittel,
  DFT, Koeffizienten über k_max null (k_max = 3, 6, 9 oder ohne), F_min − ⟨N⟩ der Mittelkurve.
- B (E4-artig): Minimum der Rohabtastwerte je Zyklus, über Zyklen gemittelt, minus ⟨N⟩.
Wahrheit: rauschfreie, jittergedämpfte Erwartungskurve (Harmonische · e^{−k²σ_φ²/2} für Modul 2, 3),
gleich bandbegrenzt; das ist, was die Superpositionsvorhersage mit gemessenen Zeigern ρ liefert.
Ausgabe: s1_fmin_rauschen_mc.csv, Text nach stdout.
"""
import itertools
import numpy as np
import pandas as pd
import linear_solver as L

MG, M, F = L.MG, L.M, 10.0
T = 1.0 / F
MU = 0.4
NTH = 2000
rng = np.random.default_rng(42)

# Modulbeitrag h(t) auf feinem Raster (16000 je Periode)
P, NF = L.profile_spectrum()
h_spec = MU * M * P / 3                      # starr: H = 1
h_fine = np.fft.irfft(h_spec, NF)
t_fine = np.arange(NF) * T / NF


def h_at(t):
    return np.interp(np.mod(t, T), t_fine, h_fine, period=T)


def truth_curve(phi2, phi3, sig_phi, kmax):
    k = np.arange(h_spec.size)
    damp = np.exp(-0.5 * (k * sig_phi) ** 2)
    A = h_spec * (1 + damp * np.exp(-1j * k * np.radians(phi2)) + damp * np.exp(-1j * k * np.radians(phi3)))
    if kmax is not None:
        A[kmax + 1:] = 0
    x = np.fft.irfft(A, NF)[::NF // NTH]
    return x                                  # N − Mg auf 2000 Stützstellen, Mittel exakt 0


def truth_raw_min(phi2, phi3):
    k = np.arange(h_spec.size)
    A = h_spec * (1 + np.exp(-1j * k * np.radians(phi2)) + np.exp(-1j * k * np.radians(phi3)))
    return np.fft.irfft(A, NF).min()


def simulate(phi2, phi3, fs, sigma, sig_t, nz, R, kmaxs):
    nc = int(round(fs / F))
    ns = nc * nz
    out = {('A', km): np.empty(R) for km in kmaxs}
    out[('B', None)] = np.empty(R)
    harm = np.empty((R, 3), complex)
    tau2, tau3 = np.radians(phi2) / (2 * np.pi * F), np.radians(phi3) / (2 * np.pi * F)
    batch = max(1, int(1e7 // ns))
    th = np.arange(NTH) / NTH                 # Zyklusphase in Bruchteilen
    for b0 in range(0, R, batch):
        bR = min(batch, R - b0)
        off = rng.uniform(0, 1.0 / fs, size=(bR, 1))           # Sub-Sample-Versatz
        ts = off + np.arange(ns)[None, :] / fs                  # Abtastzeiten (Index von Modul 1 bei t = 0)
        cyc = np.floor(ts / T).astype(int)
        cyc = np.clip(cyc, 0, nz - 1)
        d2 = rng.normal(0, sig_t, size=(bR, nz + 2))
        d3 = rng.normal(0, sig_t, size=(bR, nz + 2))
        c2 = np.clip(np.floor((ts - tau2) / T).astype(int) + 1, 0, nz + 1)
        c3 = np.clip(np.floor((ts - tau3) / T).astype(int) + 1, 0, nz + 1)
        x = (h_at(ts) + h_at(ts - tau2 - np.take_along_axis(d2, c2, 1))
             + h_at(ts - tau3 - np.take_along_axis(d3, c3, 1)))
        x = x + sigma * rng.standard_normal(x.shape)
        mean_N = x.mean(1)                                       # ⟨N⟩ − Mg über ganze Zyklen (≈)
        # Verfahren B: Rohminimum je Zyklus (f_s/f ganzzahlig, Versatz < 1/f_s: Zyklus c = Abtastwerte c·n_c … (c+1)·n_c − 1)
        xr = x.reshape(bR, nz, nc)
        out[('B', None)][b0:b0 + bR] = xr.min(2).mean(1) - mean_N
        # Verfahren A: lineare Interpolation je Zyklus auf 2000 Punkte und Mittel über Zyklen. Weil alle Zyklen
        # dasselbe Abtastmuster haben (f_s/f ganzzahlig), ist das gleich der Interpolation des über Zyklen
        # gemittelten Abtastzyklus (periodisch fortgesetzt; am Zyklusende Randfehler vernachlässigbar).
        xm = xr.mean(1)                                          # bR × n_c
        pos = (th[None, :] * T - off) * fs                       # Bruchindex der Zielpunkte, bR × 2000
        i0 = np.floor(pos).astype(int)
        w = pos - i0
        i0m = np.mod(i0, nc)
        i1m = np.mod(i0 + 1, nc)
        curve = (1 - w) * np.take_along_axis(xm, i0m, 1) + w * np.take_along_axis(xm, i1m, 1)
        Ck = np.fft.rfft(curve, axis=1)
        harm[b0:b0 + bR] = 2 * Ck[:, 1:4] / NTH
        for km in kmaxs:
            Cc = Ck.copy()
            if km is not None:
                Cc[:, km + 1:] = 0
            cv = np.fft.irfft(Cc, NTH, axis=1)
            out[('A', km)][b0:b0 + bR] = cv.min(1) - cv.mean(1)
    return out, harm


rows = []
configs = [(120.0, 240.0), (116.0, 240.0), (100.0, 240.0)]
kmaxs = [3, 6, 9, None]
grid = list(itertools.product(configs, [2000, 6400, 10000], [0.001, 0.005, 0.020], [0.0, 56e-6], [10, 100]))
import os
import sys
if os.environ.get('QUICK'):
    grid = grid[-4:]
CFG = int(sys.argv[1]) if len(sys.argv) > 1 else None      # Teillauf je Konfiguration (Wandzeitbudget)
if CFG is not None:
    grid = [g for g in grid if g[0] == configs[CFG]]
for (phi2, phi3), fs, sigma, sig_t, nz in grid:
    R = 300
    sig_phi = 2 * np.pi * F * sig_t
    out, harm = simulate(phi2, phi3, fs, sigma, sig_t, nz, R, kmaxs)
    for (proc, km), v in out.items():
        if proc == 'A':
            tr = truth_curve(phi2, phi3, sig_phi, km).min()
            tr0 = truth_curve(phi2, phi3, 0.0, km).min()
        else:
            tr = tr0 = truth_raw_min(phi2, phi3)
        rows.append(dict(phi2=phi2, fs=fs, sigma_mN=1e3 * sigma, jitter_us=1e6 * sig_t, nz=nz, verfahren=proc,
                         kmax=-1 if km is None else km, wahr_mN=1e3 * tr, wahr_ohne_jitter_mN=1e3 * tr0,
                         bias_mN=1e3 * (v.mean() - tr), sd_mN=1e3 * v.std(ddof=1),
                         bias_se_mN=1e3 * v.std(ddof=1) / np.sqrt(R),
                         sd_ReN1_mN=1e3 * harm[:, 0].real.std(ddof=1), sd_ReN2_mN=1e3 * harm[:, 1].real.std(ddof=1),
                         sd_ReN3_mN=1e3 * harm[:, 2].real.std(ddof=1)))
    print(f'{phi2:5.0f} fs={fs:5d} sig={1e3*sigma:4.0f} mN jit={1e6*sig_t:3.0f} us nz={nz:3d} | ' +
          ' '.join(f'{p}{"" if k is None else k}: b={1e3*(v.mean()-(truth_curve(phi2,phi3,sig_phi,k).min() if p=="A" else truth_raw_min(phi2,phi3))):+.2f} s={1e3*v.std(ddof=1):.2f}'
                   for (p, k), v in out.items()), flush=True)

df = pd.DataFrame(rows)
df.to_csv('s1_quick.csv' if os.environ.get('QUICK') else (f's1_fmin_rauschen_mc_cfg{CFG}.csv' if CFG is not None else 's1_fmin_rauschen_mc.csv'), index=False)
# Theoretische Streuung (weißes Rauschen, Bandbegrenzung): Var(N(θ) − ⟨N⟩) = 2·k_max·σ²/(f_s·T_a)
print('\nTheorie weißes Rauschen: sd(N(θ) − ⟨N⟩) der bandbegrenzten Mittelkurve = σ·sqrt(2 k_max/(f_s T_a)); '
      'sd(Re N_k) = σ·sqrt(2/(f_s T_a))')
for fs, sigma, nz, km in [(6400, 0.020, 100, 9), (2000, 0.020, 10, 9), (10000, 0.001, 100, 3)]:
    Ta = nz / F
    print(f'  fs={fs}, sigma={1e3*sigma} mN, T_a={Ta} s, k_max={km}: '
          f'{1e3*sigma*np.sqrt(2*km/(fs*Ta)):.3f} mN; Re N_k: {1e3*sigma*np.sqrt(2/(fs*Ta)):.3f} mN')
