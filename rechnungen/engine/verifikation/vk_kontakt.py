"""Gegenprüfung ENG-02: Kontaktast – stationäre Lösung analytisch, Floquet, Startunabhängigkeit, Stöße.

(a) Harmonische Balance mit ANALYTISCHEN Fourier-Koeffizienten des Profils (geschlossene Integrale, nicht FFT
    wie linear_solver.py), k = 1..KMAX; N(t) an den Engine-Stichproben t_i = i*50 µs und auf 1-µs-Raster.
(b) |mu| = exp(-C T / 2M) analytisch (lineare ODE im Dauerkontakt).
(c) Halbanalytischer Löser SA: Starts std / imp / Orbit, Einschwingzeit; Stöße dz' an zwei Zyklusphasen.
"""
import os
import sys, json
import numpy as np
from scipy.stats import skew
import vk_model as m
import vk_sa as sa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
KMAX = 20000
W = 2 * np.pi * m.F_HZ


def Pk(k):
    """(1/T) int_0^T a(u) exp(-i k W u) du, geschlossen."""
    k = np.asarray(k, float)
    TH, TF = m.THOLD * m.T, m.TFAST * m.T

    def I_sin(A, w, L, shift):
        # int_0^L A sin(w s) exp(-i k W (s + shift)) ds
        out = 0
        for sgn in (+1, -1):
            q = sgn * w - k * W
            out = out + sgn * (np.exp(1j * q * L) - 1) / (1j * q)
        return A / (2j) * out * np.exp(-1j * k * W * shift)
    return (I_sin(m.AH, m.WH, TH, 0.0) + I_sin(m.AF, m.WF, TF, TH)) / m.T


def N_series(phi2, phi3, t, nfine=100000):
    """Stationäre Kontaktlösung (abgeschnitten bei KMAX). Auswertung exakt an t = j*T/nfine per irfft,
    beliebige t (wenige) per direkter Summe."""
    k = np.arange(1, KMAX + 1)
    P = Pk(k)
    comb = (1 + np.exp(-1j * k * np.radians(phi2)) + np.exp(-1j * k * np.radians(phi3))) / 3
    Ab = P * comb
    H = (m.K + 1j * m.C * k * W) / (m.K - m.M * (k * W)**2 + 1j * m.C * k * W)
    Nk = m.M * H * Ab
    Yk = -Ab / (m.K / m.M - (k * W)**2 + 2j * m.ALPHA * k * W)     # z_k
    t = np.asarray(t, float)
    if t.size <= 10:
        E = np.exp(1j * np.outer(t, k * W))
        return (m.MG + 2 * np.real(E @ Nk), -m.MG / m.K + 2 * np.real(E @ Yk),
                2 * np.real(E @ (1j * k * W * Yk)))
    # Raster j*T/nfine
    def irf(c):
        arr = np.zeros(nfine // 2 + 1, complex)
        arr[1:KMAX + 1] = c
        return np.fft.irfft(arr, nfine) * nfine
    Nf = m.MG + irf(Nk); zf = -m.MG / m.K + irf(Yk); vf = irf(1j * k * W * Yk)
    idx = np.rint(np.mod(t, m.T) / m.T * nfine).astype(int) % nfine
    assert np.allclose(idx * m.T / nfine, np.mod(t, m.T), atol=1e-12)
    return Nf[idx], zf[idx], vf[idx]


def main():
    res = {}
    lines = []
    P = lines.append
    P(f'Kontrolle P_0 = {Pk(0.0):.2e} (analytisch 0), |P_1| = {abs(Pk(1.0)):.6f}, |P_2| = {abs(Pk(2.0)):.6f} m/s^2')
    mu = np.exp(-m.C * m.T / (2 * m.M))
    P(f'(b) |mu| = exp(-C T/2M) = exp(-{m.C*m.T/(2*m.M):.4f}) = {mu:.4f}; tau = 2M/C = {2*m.M/m.C:.5f} s; 10 tau = {20*m.M/m.C:.4f} s; '
      f'zeta = {m.C/(2*np.sqrt(m.K*m.M)):.5f}, f_n = {m.W0/2/np.pi:.3f} Hz, 1/(2 pi zeta f_n) = {1/(m.C/(2*np.sqrt(m.K*m.M))*m.W0):.5f} s')
    pts = [(120, 240), (113.684, 227.368), (100, 240), (110, 250), (130, 230), (110, 252)]
    ts = np.arange(2000) * 5e-5
    tf = np.arange(100000) * 1e-6
    mode = sys.argv[1] if len(sys.argv) > 1 else 'base'
    i0, i1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, len(pts))
    for p2, p3 in (pts if mode == 'base' else []):
        N, z, zd = N_series(p2, p3, ts)
        Nf, zf, _ = N_series(p2, p3, tf)
        d = dict(skew_s=float(skew(N)), Fmin_s=float(N.min()), Fmax_s=float(N.max()),
                 Fmin_f=float(Nf.min()), Fmax_f=float(Nf.max()), zmax=float(zf.max()), mean=float(N.mean()))
        res[f'{p2},{p3}'] = d
        P(f'(a) ({p2},{p3}): Stichproben 50 µs: gamma1 {d["skew_s"]:.6f}, F_min {d["Fmin_s"]:.5f}, F_max {d["Fmax_s"]:.5f} N; '
          f'1 µs: F_min {d["Fmin_f"]:.5f}, F_max {d["Fmax_f"]:.5f}; max z {d["zmax"]*1e3:.4f} mm; <N>-Mg {d["mean"]-m.MG:.1e}')
        # (c) SA: Starts
        s = sa.SA(p2, p3)
        z0o, v0o = z[0], zd[0]
        starts = {'std': (-m.MG / m.K, 0.0), 'imp': (-m.MG / m.K, -float(m.ebar_v(0.0, s.taus))), 'orb': (z0o, v0o)}
        for nm, (a, b) in starts.items():
            R = s.run(a, b, 0.0, 40)
            st = sa.stats(R, 20, 40)
            dv = np.abs(R['PV'] - v0o)
            ok = np.where(dv >= 1e-6)[0]
            tset = (ok[-1] + 1) * m.T if ok.size else 0.0
            ok8 = np.where(dv >= 1e-8)[0]
            tset8 = (ok8[-1] + 1) * m.T if ok8.size else 0.0
            P(f'    SA {nm}: lam {st["lam"]:.4f}, gamma1 {st["skew"]:.6f}, F_min {st["Fmin"]:.5f}, F_max {st["Fmax"]:.5f}, '
              f'|z\'-z\'_orb| am Ende {dv[-1]:.1e}, Einschwingen <1e-6: {tset:.1f} s, <1e-8: {tset8:.1f} s')
            res[f'{p2},{p3}'][f'sa_{nm}'] = dict(st, tset6=tset, tset8=tset8)
    # Stöße
    kicks = [3.0, -3.0, 1.0, -1.0, 0.3, -0.3]
    for p2, p3 in (pts[i0:i1] if mode == 'kicks' else []):
        res[f'{p2},{p3}'] = {}
        s = sa.SA(p2, p3)
        kres = []
        for t0c in (0, 0.5):     # Zyklusphase 0 und 0.5: Startzustand exakt auf dem Orbit (Fourierlösung)
            t0 = 3.0 + t0c * m.T
            _, zq, zdq = N_series(p2, p3, np.array([t0c * m.T]))
            zz, vv = float(zq[0]), float(zdq[0])
            for dv in kicks:
                R = s.run(zz, vv + dv, t0, 150)
                st = sa.stats(R, 100, 150)
                kres.append(dict(phase=t0c, dv=dv, lam_end=st['lam'], Fmin_end=st['Fmin'],
                                 lam_max=float((R['tfree'] / m.T * 100).max())))
                print(f'   ({p2},{p3}) Phase {t0c} dz\' {dv:+.1f}: lam_end {st["lam"]:.4f}, F_min_end {st["Fmin"]:.4f}, '
                      f'lam_max {kres[-1]["lam_max"]:.1f}', flush=True)
        res[f'{p2},{p3}']['kicks'] = kres
        back = all(k['lam_end'] == 0 for k in kres)
        P(f'(c) Stöße ({p2},{p3}): ' + '; '.join(f'ph{k["phase"]} {k["dv"]:+.1f}: lam_end {k["lam_end"]:.3f} (max {k["lam_max"]:.0f} %)' for k in kres)
          + f'  -> alle zurück in Kontakt: {back}')
    txt = '\n'.join(lines)
    print(txt)
    tag = mode if mode == 'base' else f'kicks_{i0}_{i1}'
    open(OUT + f'vk_kontakt_{tag}_ausgabe.txt', 'w').write(txt + '\n')
    json.dump(res, open(OUT + f'vk_kontakt_{tag}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
