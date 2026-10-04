"""s3_h2_zeltfit_mc.py – H2 (Präreg v2 §3, §8.6, A9.6): Halbbreite des Intervalls für Δφ* = φ₂*(Messung) − φ̂₂*
(Vorhersage) aus dem Zwei-Geraden-Zeltfit, nötige Laufzahl je Punkt für Halbbreite ≤ 1°, Bias des Fits bei
gekrümmtem Zelt.

Prüfgruppe statistik, P2. Nur lesend auf Repo-Code und data/finesweep_2deg_120_240.csv.

Modell (eigene Annahmen):
- Formen: 'ref' = Referenz-Engine im Kontaktast (K = 10⁴ N/m, C = 16 N·s/m, μ = 1; 2°-Sekanten 0,212/0,195 N/°;
  identisch mit finesweep_2deg_120_240.csv auf φ₃ = 240°, s. Ausgabe), skaliert mit s ∈ {1; 0,5; 0,25; 0,1}
  (reduzierter Hub bzw. μ < 1: alle Modulharmonischen × s); 'A4' = starre Auflage, μ = 0,4, 10 Hz (Sekante 0,047).
  Superposition exakt (Typ-I-Lage), identische Module, Phasen = Sollphasen.
- Rauschen: weißes Restrauschen der Lauf-Mittelkurve, sd(Re N_k) = sd(Im N_k) = σ_h je Lauf, k ≤ k_max = 9;
  daraus sd(F_min − ⟨N⟩) eines Laufs σ_run ≈ σ_h·√k_max. Messseite: n Läufe je Punkt, unabhängig zwischen den
  Punkten. Vorhersage: n₀ = n Einzelmodulläufe je Modul, dieselben für alle Punkte (korreliert über Punkte).
- SNR := s̄·1°/σ_run mit s̄ = Mittel der beiden 2°-Sekanten an der Spitze.
- Fitfenster W nach A9.6 mit der rauschfreien Vorhersage und u_c,erw = σ_run·√(1/n + 3/n₀).
- Zeltfit wie A9.6: φ* auf 0,02°-Raster, dann 0,001° fein; je φ* lineare KQ für (F*, s_L, s_R).
- Erwartete Halbbreite = (q97,5 − q2,5)/2 der Monte-Carlo-Verteilung von Δφ* (R Kampagnen); Stichprobe mit
  Bootstrap je Kampagne (A9.6, B Replikate) zur Kontrolle.
Ausgaben: s3_h2_zeltfit_mc.csv, s3_h2_bias.csv, Text nach stdout.
"""
import os
import sys
import numpy as np
import pandas as pd
import linear_solver as L

rng = np.random.default_rng(7)
KMAX, NTH = 9, 2000
M = L.M
P, NF = L.profile_spectrum()
k = np.arange(1, KMAX + 1)
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))
PHI2 = np.arange(100, 140.1, 2.0)


def module_harm(shape):
    if shape == 'ref':
        H, _ = L.transfer(1e4, 16.0, P.size)
        return 2 * 1.0 * M * (P * H)[1:KMAX + 1] / 3 / NF
    if shape == 'A4':
        return 2 * 0.4 * M * P[1:KMAX + 1] / 3 / NF
    raise ValueError


def E_of(phi2):
    PH = np.radians(np.stack([np.zeros_like(phi2), phi2, np.full_like(phi2, 240.0)], 1))
    return np.exp(-1j * PH[:, :, None] * k[None, None, :])             # npt × 3 × K


def fmin_curves(Nc, mask):
    return (Nc.real @ COS[:, mask] - Nc.imag @ SIN[:, mask]).min(-1)


# ---------- Zeltfit ----------
def tent_design(x, ps):
    X = np.stack([np.ones((ps.size, x.size)), -np.clip(ps[:, None] - x[None, :], 0, None),
                  -np.clip(x[None, :] - ps[:, None], 0, None)], -1)  # G × n × 3
    return X


def tent_fit(x, Y, step1=0.02):
    """φ* je Zeile von Y (R × n) nach A9.6 (Raster über [min x, max x], kleinste RSS, bei Gleichstand das kleinste)."""
    Y = np.atleast_2d(Y)
    ps = np.arange(x.min(), x.max() + 1e-9, step1)

    def best(ps_rows):
        # ps_rows: R × G (eigenes Raster je Zeile) oder G (gemeinsam)
        if ps_rows.ndim == 1:
            X = tent_design(x, ps_rows)
            Pm = np.einsum('gnp,gpq,gmq->gnm', X, np.linalg.pinv(np.einsum('gnp,gnq->gpq', X, X)), X)
            out = np.empty(Y.shape[0])
            for c0 in range(0, Y.shape[0], 100):
                Yc = Y[c0:c0 + 100]
                fit = np.einsum('gnm,rm->rgn', Pm, Yc)
                rss = ((Yc[:, None, :] - fit) ** 2).sum(-1)
                out[c0:c0 + 100] = ps_rows[np.argmin(rss, 1)]
            return out
        out = np.empty(Y.shape[0])
        for i in range(Y.shape[0]):
            X = tent_design(x, ps_rows[i])
            Pm = np.einsum('gnp,gpq,gmq->gnm', X, np.linalg.pinv(np.einsum('gnp,gnq->gpq', X, X)), X)
            fit = Pm @ Y[i]
            rss = ((Y[i][None, :] - fit) ** 2).sum(-1)
            out[i] = ps_rows[i][np.argmin(rss)]
        return out

    c = best(ps)
    # Feinsuche ±step1 mit 0,001°: gemeinsames relatives Raster, je Zeile verschoben
    rel = np.arange(-step1, step1 + 1e-9, 0.001)
    fine = np.clip(c[:, None] + rel[None, :], x.min(), x.max())
    # vektorisiert über Zeilen: Design je (Zeile, Rasterpunkt)
    R, G = fine.shape
    Xd = np.stack([np.ones((R, G, x.size)), -np.clip(fine[:, :, None] - x[None, None, :], 0, None),
                   -np.clip(x[None, None, :] - fine[:, :, None], 0, None)], -1)
    XtX = np.einsum('rgnp,rgnq->rgpq', Xd, Xd)
    Xty = np.einsum('rgnp,rn->rgp', Xd, Y)
    beta = np.einsum('rgpq,rgq->rgp', np.linalg.pinv(XtX), Xty)
    rss = ((Y[:, None, :] - np.einsum('rgnp,rgp->rgn', Xd, beta)) ** 2).sum(-1)
    return fine[np.arange(R), np.argmin(rss, 1)]


def tent_dev(x, y):
    """größte Abweichung der Punkte von der eigenen Zeltanpassung"""
    ps = tent_fit(x, y[None, :])[0]
    X = tent_design(x, np.array([ps]))[0]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return np.abs(y - X @ b).max(), ps


def window(Fpred, uce, center=120.0):
    """A9.6: größtes w aus {4, …, 20}, ≥ 2 Punkte je Seite, Abweichung ≤ 0,25·u_c,erw."""
    best = None
    for w in range(4, 21, 2):
        sel = (PHI2 >= center - w - 1e-9) & (PHI2 <= center + w + 1e-9)
        if (PHI2[sel] < center).sum() < 2 or (PHI2[sel] > center).sum() < 2:
            continue
        dev, _ = tent_dev(PHI2[sel], Fpred[sel])
        if dev <= 0.25 * uce:
            best = w
    return best


# ---------- 1. Bias des Zwei-Geraden-Fits am rauschfreien, gekrümmten Zelt ----------
print('=== 1. Rauschfreier Zeltfit: φ* gegen die wahre Spitze 120° ===')
fs = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/finesweep_2deg_120_240.csv'))
fs = fs[np.isclose(fs.phi3_deg, 240)].sort_values('phi2_deg')
rows_b = []
for shape in ('ref', 'A4', 'csv'):
    if shape == 'csv':
        F = fs.F_min.values
    else:
        Nm = module_harm(shape)
        Nc = (Nm[None, None, :] * E_of(PHI2)).sum(1)
        F = (Nc.real @ COS - Nc.imag @ SIN).min(1)
    for w in range(4, 21, 2):
        sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
        dev, ps = tent_dev(PHI2[sel], F[sel])
        rows_b.append(dict(form=shape, w=w, phi_stern=ps, bias_deg=ps - 120.0, max_abw_mN=1e3 * dev))
    print(shape, ' '.join(f'w={r["w"]}: {r["bias_deg"]:+.3f}° ({r["max_abw_mN"]:.1f} mN)'
                          for r in rows_b if r['form'] == shape))
pd.DataFrame(rows_b).to_csv('s3_h2_bias.csv', index=False)
# Sekanten
for shape in ('ref', 'A4'):
    Nm = module_harm(shape)
    Nc = (Nm[None, None, :] * E_of(np.array([118.0, 120.0, 122.0]))).sum(1)
    F = (Nc.real @ COS - Nc.imag @ SIN).min(1)
    print(f'{shape}: 2°-Sekanten {(F[1] - F[0]) / 2:.4f} / {(F[1] - F[2]) / 2:.4f} N/°  (bandbegrenzt k ≤ {KMAX})')

# ---------- 2. Monte Carlo der Halbbreite ----------
print('\n=== 2. Halbbreite von Δφ* (Messung − Vorhersage), exakte Superposition ===')
R = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
cases = [('ref', 1.0), ('ref', 0.5), ('ref', 0.25), ('ref', 0.1), ('A4', 1.0)]
snrs = [0.5, 1.0, 2.0, 4.0, 8.0]
ns = [5, 10, 20, 40]
rows = []
for shape, sc in cases:
    Nm = module_harm(shape) * sc
    E = E_of(PHI2)
    Ntrue = (Nm[None, None, :] * E).sum(1)                             # 21 × K
    cv = Ntrue.real @ COS - Ntrue.imag @ SIN
    Ftrue = cv.min(1)
    sbar = ((Ftrue[10] - Ftrue[9]) + (Ftrue[10] - Ftrue[11])) / 4      # Mittel der 2°-Sekanten
    for snr in snrs:
        s_run = sbar * 1.0 / snr
        sig_h = s_run / np.sqrt(KMAX)
        for n in ns:
            n0 = n
            uce = s_run * np.sqrt(1 / n + 3 / n0)
            w = window(Ftrue, uce)
            if w is None:
                rows.append(dict(form=shape, skala=sc, sbar=sbar, snr=snr, s_run_mN=1e3 * s_run, n=n, w=np.nan))
                continue
            sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
            x = PHI2[sel]
            masks = [cv[i] < cv[i].min() + max(0.3 * sc, 8 * s_run) for i in np.where(sel)[0]]
            # Messung
            noise = sig_h / np.sqrt(n) * (rng.standard_normal((R, sel.sum(), KMAX))
                                          + 1j * rng.standard_normal((R, sel.sum(), KMAX)))
            Ym = Ntrue[sel][None] + noise
            # Vorhersage: gemeinsame Einzelmodul-Mittel (3 Module), je Punkt mit den Phasen kombiniert
            mods = Nm[None, None, :] + sig_h / np.sqrt(n0) * (rng.standard_normal((R, 3, KMAX))
                                                                + 1j * rng.standard_normal((R, 3, KMAX)))
            Yp = np.einsum('rjk,ijk->rik', mods, E[sel])
            Fm = np.stack([fmin_curves(Ym[:, i], masks[i]) for i in range(sel.sum())], 1)
            Fp = np.stack([fmin_curves(Yp[:, i], masks[i]) for i in range(sel.sum())], 1)
            pm, pp = tent_fit(x, Fm), tent_fit(x, Fp)
            d = pm - pp
            q = np.quantile(d, [0.025, 0.975])
            rows.append(dict(form=shape, skala=sc, sbar=sbar, snr=snr, s_run_mN=1e3 * s_run, n=n, w=w,
                             npunkte=sel.sum(), halbbreite_deg=(q[1] - q[0]) / 2, sd_deg=d.std(),
                             bias_deg=d.mean(), median_deg=np.median(d),
                             bias_Messung_deg=pm.mean() - 120, bias_Vorhersage_deg=pp.mean() - 120,
                             P_abs_gt_1=np.mean(np.abs(d) > 1.0)))
            print(f'{shape} s={sc:4.2f} sbar={sbar:.4f} SNR={snr:4.1f} s_run={1e3*s_run:7.2f} mN n={n:3d} w={w:2d}: '
                  f'HB={(q[1]-q[0])/2:.3f}° sd={d.std():.3f}° bias={d.mean():+.3f}° '
                  f'(Mess {pm.mean()-120:+.3f}°, Vorh {pp.mean()-120:+.3f}°)', flush=True)
df = pd.DataFrame(rows)
df.to_csv('s3_h2_zeltfit_mc.csv', index=False)

# ---------- 3. Skalierung: HB ≈ κ/(SNR·√n) ----------
print('\n=== 3. Skalierungsgesetz HB ≈ κ/(SNR·√n) und nötiges n für HB ≤ 1° ===')
d = df.dropna(subset=['halbbreite_deg']).copy()
d['kappa'] = d.halbbreite_deg * d.snr * np.sqrt(d.n)
for (shape, sc), g in d.groupby(['form', 'skala']):
    lin = g[g.halbbreite_deg < 1.5]
    kap = lin.kappa.median() if len(lin) else np.nan
    print(f'{shape} s={sc}: κ (Median, HB < 1,5°) = {kap:.2f}; Spannweite {g.kappa.min():.2f}–{g.kappa.max():.2f}; '
          f'n_nötig ≈ (κ/SNR)²: ' + ', '.join(f'SNR {s}: {int(np.ceil((kap / s) ** 2))}' for s in (0.5, 1, 2, 4, 8)))
