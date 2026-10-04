"""v4_h2_fenster_halbbreite.py – Gegenprüfung STA-05, STA-06 (H2: Fensterregel A9.6 und Halbbreite von Δφ*).

Eigene Implementierung (Kurven im Zeitbereich bzw. mit eigener Übertragungsfunktion, eigener Zeltfit über
Projektionsmatrizen je Kandidat φ*, 0,01°-Raster + 0,001°-Verfeinerung).
 1) Rauschfrei: größte Abweichung der Vorhersage F̂_min von ihrer Zeltanpassung je Halbbreite w (A4 k ≤ 9,
    Referenz K = 10⁴ N/m, C = 16 N·s/m, μ = 1, k ≤ 9; dazu die nichtlineare Engine-CSV auf φ₃ = 240°).
 2) NEU gegenüber der Gruppe: Fensterwahl mit der VERRAUSCHTEN Phase-0-Vorhersage (wie in Teil B tatsächlich):
    P(zulässiges W existiert) als Funktion des SNR, n = n₀ = 20, weißes Rauschen.
 3) Stichproben der Halbbreite (q97,5 − q2,5)/2 von Δφ* = φ*_Mess − φ̂* bei exakter Superposition.
Aufruf: python3 v4_h2_fenster_halbbreite.py [R_fenster] [R_halbbreite]
"""
import os
import sys
import numpy as np
import csv

M, G = 0.650, 9.81
F = 10.0
T = 1 / F
RTOP, THOLD = 0.005, 0.65
TFAST = 1 - THOLD
RBOT = RTOP * TFAST / THOLD
A_HOLD = -RTOP * (np.pi / (THOLD * T)) ** 2
A_FAST = RBOT * (np.pi / (TFAST * T)) ** 2


def accel(t):
    p = np.mod(t, T) / T
    return np.where(p < THOLD, A_HOLD * np.sin(np.pi * p / THOLD), A_FAST * np.sin(np.pi * (p - THOLD) / TFAST))


KMAX, NF, NTH = 9, 16000, 2000
k = np.arange(1, KMAX + 1)
Pk = 2 * np.fft.rfft(accel(np.arange(NF) / NF * T))[1:KMAX + 1] / NF       # Profilbeschleunigung, N_k-Konvention
w0 = 2 * np.pi * F


def mod_harm(form):
    if form == 'A4':
        return 0.4 * M / 3 * Pk
    Kc, Cc = 1e4, 16.0                                                      # Referenz: H(kω) = (K + iωC)/(K − Mω² + iωC)
    om = k * w0
    H = (Kc + 1j * om * Cc) / (Kc - M * om ** 2 + 1j * om * Cc)
    return 1.0 * M / 3 * Pk * H


PHI2 = np.arange(100, 140.1, 2.0)
E = np.exp(-1j * np.radians(np.stack([np.zeros(21), PHI2, np.full(21, 240.0)], 1))[:, :, None] * k)   # 21×3×K
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))


def fmin(Nc):
    return (Nc.real @ COS - Nc.imag @ SIN).min(-1)


# ---------------- eigener Zeltfit ----------------
_cache = {}


def tent_proj(x):
    key = tuple(x)
    if key in _cache:
        return _cache[key]
    cand = np.round(np.arange(x.min(), x.max() + 1e-9, 0.01), 6)
    X = np.stack([np.ones((cand.size, x.size)), np.minimum(x[None, :] - cand[:, None], 0),
                  np.maximum(x[None, :] - cand[:, None], 0)], -1)              # G × n × 3
    Q = np.einsum('gnp,gpq,gmq->gnm', X, np.linalg.pinv(np.einsum('gnp,gnq->gpq', X, X)), X)
    _cache[key] = (cand, Q)
    return cand, Q


def tent_fit(x, Y):
    """φ* (kleinste Residuenquadratsumme; Gleichstand → kleinstes) und max. Abweichung, je Zeile von Y."""
    Y = np.atleast_2d(Y)
    cand, Q = tent_proj(x)
    best = np.empty(Y.shape[0])
    for c0 in range(0, Y.shape[0], 200):
        Yc = Y[c0:c0 + 200]
        fitq = np.einsum('rn,gnm,rm->rg', Yc, Q, Yc)                         # yᵀQy; RSS = yᵀy − yᵀQy
        best[c0:c0 + 200] = cand[np.argmax(fitq, 1)]
    # Verfeinerung 0,001° in ±0,01°
    rel = np.arange(-0.01, 0.01 + 1e-12, 0.001)
    fine = np.clip(best[:, None] + rel[None, :], x.min(), x.max())
    X = np.stack([np.ones(fine.shape + (x.size,)), np.minimum(x[None, None, :] - fine[:, :, None], 0),
                  np.maximum(x[None, None, :] - fine[:, :, None], 0)], -1)    # R × g × n × 3
    beta = np.einsum('rgpq,rgq->rgp', np.linalg.pinv(np.einsum('rgnp,rgnq->rgpq', X, X)),
                     np.einsum('rgnp,rn->rgp', X, Y))
    res = Y[:, None, :] - np.einsum('rgnp,rgp->rgn', X, beta)
    rss = (res ** 2).sum(-1)
    j = np.argmin(rss, 1)
    ii = np.arange(Y.shape[0])
    return fine[ii, j], np.abs(res[ii, j]).max(-1)


def window_from(Fpred_rows, uce, center=120.0):
    """A9.6: größtes w ∈ {4,…,20} mit ≥ 2 Punkten je Seite und max. Abweichung ≤ 0,25·u_c,erw; je Zeile."""
    R = Fpred_rows.shape[0]
    best = np.full(R, np.nan)
    devs = {}
    for w in range(4, 21, 2):
        sel = (PHI2 >= center - w - 1e-9) & (PHI2 <= center + w + 1e-9)
        if (PHI2[sel] < center).sum() < 2 or (PHI2[sel] > center).sum() < 2:
            continue
        _, dev = tent_fit(PHI2[sel], Fpred_rows[:, sel])
        devs[w] = dev
        best = np.where(dev <= 0.25 * uce, w, best)
    return best, devs


out = []
pr = out.append
# ---------------- 1) rauschfrei ----------------
pr('=== 1) Rauschfrei: max. Abweichung der Vorhersage von der eigenen Zeltanpassung [mN] und φ* − 120° ===')
TRUE = {}
for form in ('A4', 'ref'):
    Nc = (mod_harm(form)[None, None, :] * E).sum(1)
    Ft = fmin(Nc)
    TRUE[form] = (Nc, Ft)
    sec = ((Ft[10] - Ft[9]) / 2, (Ft[10] - Ft[11]) / 2)
    row = []
    for w in range(4, 21, 2):
        sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
        ps, dev = tent_fit(PHI2[sel], Ft[sel][None, :])
        row.append(f'w={w}: {1e3*dev[0]:.2f} ({ps[0]-120:+.3f}°)')
    pr(f'{form}: 2°-Sekanten {sec[0]:.4f}/{sec[1]:.4f} N/° | ' + '; '.join(row))
fs = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../data/finesweep_2deg_120_240.csv'))))
fcsv = np.array([float(r['F_min']) for r in sorted(fs, key=lambda r: float(r['phi2_deg'])) if abs(float(r['phi3_deg']) - 240) < 1e-6])
row = []
for w in range(4, 21, 2):
    sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
    ps, dev = tent_fit(PHI2[sel], fcsv[sel][None, :])
    row.append(f'w={w}: {1e3*dev[0]:.2f} ({ps[0]-120:+.3f}°)')
pr('CSV (Engine, volles Spektrum): ' + '; '.join(row))
for form in ('A4', 'ref'):
    Ft = TRUE[form][1]
    sel = (PHI2 >= 116) & (PHI2 <= 124)
    _, dev = tent_fit(PHI2[sel], Ft[sel][None, :])
    n = 20
    uce_min = 4 * dev[0]
    pr(f'{form}: Fenster (rauschfrei) nur bei u_c,erw ≥ 4·{1e3*dev[0]:.2f} = {1e3*uce_min:.2f} mN; '
       f'bei n = n₀ = 20 (u_c,erw = σ_run·√(4/20)): σ_run ≥ {1e3*uce_min/np.sqrt(4/20):.1f} mN')

# ---------------- 2) Fensterwahl mit verrauschter Vorhersage ----------------
RW = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
RH = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
rng = np.random.default_rng(99)
pr(f'\n=== 2) Fensterwahl mit verrauschter Phase-0-Vorhersage (n = n₀ = 20, weiß; {RW} Ziehungen) ===')
rows = []
for form in ('A4', 'ref'):
    Nm = mod_harm(form)
    Nc, Ft = TRUE[form]
    sbar = ((Ft[10] - Ft[9]) + (Ft[10] - Ft[11])) / 4
    for snr in (0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 8.0, 16.0, 32.0, 100.0):
        s_run = sbar / snr
        sh = s_run / np.sqrt(KMAX)
        n = n0 = 20
        uce = s_run * np.sqrt(1 / n + 3 / n0)
        mods = Nm[None, None, :] + sh / np.sqrt(n0) * (rng.standard_normal((RW, 3, KMAX)) + 1j * rng.standard_normal((RW, 3, KMAX)))
        Yp = np.einsum('rjk,ijk->rik', mods, E)
        Fp = np.stack([fmin(Yp[:, i]) for i in range(21)], 1)
        wbest, devs = window_from(Fp, uce)
        wfree, _ = window_from(Ft[None, :], uce)
        p_exist = np.mean(~np.isnan(wbest))
        hist = {w: np.mean(wbest == w) for w in range(4, 21, 2)}
        p4 = np.mean(devs[4] <= 0.25 * uce)
        rows.append(dict(form=form, snr=snr, s_run_mN=1e3 * s_run, uce_mN=1e3 * uce, w_rauschfrei=wfree[0],
                         P_fenster=p_exist, P_w4_zulaessig=p4, median_dev4_durch_uce=np.median(devs[4]) / uce,
                         **{f'P_w{w}': v for w, v in hist.items()}))
        pr(f'{form} SNR={snr:4.2f} σ_run={1e3*s_run:8.2f} mN u_c,erw={1e3*uce:7.2f} mN | w(rauschfrei)={wfree[0]} | '
           f'P(Fenster existiert)={p_exist:.3f}, P(w=4 zulässig)={p4:.3f}, Median Abw(w=4)/u_c,erw={np.median(devs[4])/uce:.3f} | '
           + ' '.join(f'w{w}:{v:.2f}' for w, v in hist.items() if v > 0.005))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v4_h2_fenster.csv'), 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)

# ---------------- 3) Halbbreite (exakte Superposition) ----------------
pr(f'\n=== 3) Halbbreite von Δφ* (q97,5 − q2,5)/2, n₀ = n, weiß, Fenster w fest wie angegeben; {RH} Kampagnen ===')
for form, snr, n, w in (('A4', 1.0, 20, 6), ('A4', 1.0, 20, 20), ('A4', 2.0, 10, 20), ('ref', 1.0, 20, 16),
                        ('ref', 0.5, 20, 20), ('ref', 2.0, 5, 16), ('A4', 4.0, 20, 4)):
    Nm = mod_harm(form)
    Nc, Ft = TRUE[form]
    sbar = ((Ft[10] - Ft[9]) + (Ft[10] - Ft[11])) / 4
    s_run = sbar / snr
    sh = s_run / np.sqrt(KMAX)
    sel = (PHI2 >= 120 - w) & (PHI2 <= 120 + w)
    x = PHI2[sel]
    Ym = Nc[sel][None] + sh / np.sqrt(n) * (rng.standard_normal((RH, sel.sum(), KMAX)) + 1j * rng.standard_normal((RH, sel.sum(), KMAX)))
    mods = Nm[None, None, :] + sh / np.sqrt(n) * (rng.standard_normal((RH, 3, KMAX)) + 1j * rng.standard_normal((RH, 3, KMAX)))
    Yp = np.einsum('rjk,ijk->rik', mods, E[sel])
    Fm = np.stack([fmin(Ym[:, i]) for i in range(sel.sum())], 1)
    Fp = np.stack([fmin(Yp[:, i]) for i in range(sel.sum())], 1)
    pm, _ = tent_fit(x, Fm)
    pp, _ = tent_fit(x, Fp)
    dd = pm - pp
    q = np.quantile(dd, [0.025, 0.975])
    hb = (q[1] - q[0]) / 2
    # nur Messseite
    qm = np.quantile(pm - 120, [0.025, 0.975])
    pr(f'{form} SNR={snr} n={n} w={w}: HB = {hb:.3f}° → κ = HB·SNR·√n = {hb*snr*np.sqrt(n):.2f}; '
       f'E[Δφ*] = {dd.mean():+.3f}°; P(Δφ* = 0 exakt) = {np.mean(np.abs(dd) < 5e-4):.2f}; nur Messseite HB = {(qm[1]-qm[0])/2:.3f}°, '
       f'P(φ*_Mess = 120° exakt) = {np.mean(np.abs(pm - 120) < 5e-4):.2f}')
txt = '\n'.join(out)
print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v4_h2_fenster_halbbreite_ausgabe.txt'), 'w').write(txt + '\n')
