#!/usr/bin/env python3
"""P3 / bewertung_a – B03 (Kandidaten 10, 25, 51): Wie stark verletzt eine richtungsabhängige
Kontaktdämpfung (c_load != c_unload) die Superposition, auf der H1/H2/H4 der Präreg v2 beruhen?

Eigenes 1-FG-Modell (Präreg-Anhang A2.1, Vorzeichen wie code/linear_solver.py):
    M*z'' = -M*g + F_c - (mu*M/3) * sum_j a(t - tau_j),
    F_c   = -K*z - c(z')*z',  c = c_load (z' < 0, Kompression nimmt zu), c_unload sonst.
Mittleres c = C = 2*zeta*sqrt(K*M); Asymmetrie a: c_load = C(1+a), c_unload = C(1-a).
Profil: Egg wie code/finesweep.py (THOLD 0,65), auf den Hub (Spitze-Spitze) skaliert.
Lauftypen: drei Einzelmodulläufe (Modul j allein, mu*M/3) und Kombinationsläufe auf dem
Präreg-Schnitt phi2 = 100..140°, phi3 = 240°. Superposition im Zeitbereich (A2.1):
    N_hat(t) = N_s + sum_j [N^(j)(t - tau_j) - N_s].
Residuen: F_min - <N> und Re/Im N_1..N_3 (Definition N_k wie Präreg §4, Zyklus mit 4000 Punkten).
Kontrolle: a = 0 muss Residuen auf Rundungsniveau geben (lineares System).
Zusätzlich: Verschiebung der mittleren Einfederung <delta> (Identität k*Delta<delta> = -Delta F_d).

Arbeitspunkte (Annahmen, aus P2 Tab. 2.1): V1 = 3x100 g (mu = 0,4615), Hub 8 mm, 10 Hz,
K = 1,5e6 N/m, zeta = 0,05; Vergleich weicher: K = 1e5 N/m (rho ~ 0,16), sonst gleich.
"""
import numpy as np

M, G = 0.650, 9.81
MG = M * G
F_HZ = 10.0
T = 1.0 / F_HZ
THOLD, TFAST = 0.65, 0.35
HUB_REF = 0.005 * (1 + TFAST / THOLD)         # 7,6923 mm Spitze-Spitze (finesweep)


def egg_acc(t, hub):
    rtop = 0.005 * hub / HUB_REF
    rbot = rtop * TFAST / THOLD
    a_hold = -rtop * (np.pi / (THOLD * T)) ** 2
    a_fast = rbot * (np.pi / (TFAST * T)) ** 2
    ph = np.mod(t, T) / T
    return np.where(ph < THOLD, a_hold * np.sin(np.pi * ph / THOLD),
                    a_fast * np.sin(np.pi * (ph - THOLD) / TFAST))


def simulate(phases_list, K, zeta, asym, mu, hub, n_per=4000, t_settle=1.0):
    """phases_list: Liste von Tupeln (aktive Module mit Phasen in Grad). Gibt N(t) über einen Zyklus
    (n_per Punkte) und <delta> je Konfiguration zurück, dazu die Zyklusdifferenz als Konvergenzmaß."""
    C = 2 * zeta * np.sqrt(K * M)
    c_load, c_unl = C * (1 + asym), C * (1 - asym)
    dt = T / n_per
    n_cfg = len(phases_list)
    taus = np.zeros((3, n_cfg))
    act = np.zeros((3, n_cfg))
    for i, ph in enumerate(phases_list):
        for j, p in enumerate(ph):
            if p is not None:
                taus[j, i] = np.radians(p) / (2 * np.pi * F_HZ)
                act[j, i] = 1.0
    w = mu * M / 3.0

    def forcing(t):
        return w * (act * egg_acc(t - taus, hub)).sum(0)

    def rhs(z, v, t):
        c = np.where(v < 0.0, c_load, c_unl)
        Fc = -K * z - c * v
        return v, (-MG + Fc - forcing(t)) / M, Fc

    z = np.full(n_cfg, -MG / K)
    v = np.zeros(n_cfg)
    n_settle = int(round(t_settle / T)) * n_per
    N_last = np.empty((n_per, n_cfg))
    N_prev = np.empty((n_per, n_cfg))
    Z_last = np.empty((n_per, n_cfg))
    for i in range(n_settle + 2 * n_per):
        t = i * dt
        k1z, k1v, Fc = rhs(z, v, t)
        k2z, k2v, _ = rhs(z + 0.5 * dt * k1z, v + 0.5 * dt * k1v, t + 0.5 * dt)
        k3z, k3v, _ = rhs(z + 0.5 * dt * k2z, v + 0.5 * dt * k2v, t + 0.5 * dt)
        k4z, k4v, _ = rhs(z + dt * k3z, v + dt * k3v, t + dt)
        j = i - n_settle
        if 0 <= j < n_per:
            N_prev[j] = Fc
        elif j >= n_per:
            N_last[j - n_per] = Fc
            Z_last[j - n_per] = z
        z = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
        v = v + dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6.0
    conv = np.abs(N_last - N_prev).max(0)
    return N_last, -Z_last.mean(0), conv


def harmonics(N, kmax=3):
    n = N.shape[0]
    th = 2 * np.pi * np.arange(n) / n
    return np.array([(2.0 / n) * (N * np.exp(-1j * k * th)[:, None]).sum(0) for k in range(1, kmax + 1)])


def run_case(K, zeta, asym, mu=0.3 / 0.65, hub=0.008, n_per=4000):
    cut = np.arange(100.0, 140.0 + 1e-9, 2.0)
    cfgs = [(0.0, None, None), (None, 0.0, None), (None, None, 0.0)]
    cfgs += [(0.0, p2, 240.0) for p2 in cut]
    cfgs += [(0.0, 0.0, 0.0)]                         # synchron als Zusatz
    N, dmean, conv = simulate(cfgs, K, zeta, asym, mu, hub, n_per)
    single = N[:, 0]                                   # alle drei Module identisch -> Modul 1 genügt
    single_dmean = dmean[0]
    out = []
    for i, cfg in enumerate(cfgs[3:], start=3):
        phis = [p if p is not None else 0.0 for p in cfg]
        Nhat = np.full(n_per, MG)
        for p in phis:
            shift = int(round(p / 360.0 * n_per))      # Rasterphasen exakt auf dem Gitter (2° = 22,2 Punkte -> gerundet)
            Nhat += np.roll(single, shift) - MG
        meas = N[:, i]
        # exakte Phasenverschiebung über Fourierreihe statt Rundung auf das Gitter
        S = np.fft.rfft(single - MG)
        k = np.arange(S.size)
        Nhat_f = MG + np.fft.irfft(S * sum(np.exp(-1j * k * np.radians(p)) for p in phis), n_per)
        r_fmin = (meas.min() - meas.mean()) - (Nhat_f.min() - Nhat_f.mean())
        Hm, Hp = harmonics(meas[:, None])[:, 0], harmonics(Nhat_f[:, None])[:, 0]
        # bandbegrenzte Mittelkurve wie Präreg §4/A9.4 (Koeffizienten oberhalb k_max null)
        r_bl = {}
        for kmax in (3, 6, 9, 12):
            def bl(x):
                X = np.fft.rfft(x); X[kmax + 1:] = 0.0
                return np.fft.irfft(X, n_per)
            mb, pb = bl(meas), bl(Nhat_f)
            r_bl[kmax] = (mb.min() - mb.mean()) - (pb.min() - pb.mean())
        out.append(dict(cfg=cfg, r_fmin=r_fmin, r_bl=r_bl, r_N=Hm - Hp, mean_meas=meas.mean(),
                        fmin=meas.min(), dmean=dmean[i], conv=conv[i]))
    return out, single, single_dmean, conv


def main():
    import sys
    print(__doc__.split('\n')[0])
    zeta = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
    Ks = (1.5e6,) if len(sys.argv) > 1 else (1.5e6, 1.0e5)
    for K in Ks:
        f_n = np.sqrt(K / M) / (2 * np.pi)
        C = 2 * zeta * np.sqrt(K * M)
        print(f'\n=== K = {K:.3g} N/m, zeta = {zeta}, C = {C:.2f} N s/m, f_n = {f_n:.1f} Hz, rho = {F_HZ / f_n:.3f}, '
              f'mu = 0,4615, Hub 8 mm, f = 10 Hz')
        for asym in (0.0, 0.1, 0.3, 0.5):
            res, single, sd, conv = run_case(K, zeta, asym)
            cut = [r for r in res if r['cfg'][1] is not None and r['cfg'][1] != 0.0]
            syn = [r for r in res if r['cfg'] == (0.0, 0.0, 0.0)][0]
            rf = np.array([r['r_fmin'] for r in cut])
            rN = np.array([r['r_N'] for r in cut])           # 21 x 3 komplex
            zelt = np.array([r['fmin'] for r in cut])
            i_max = int(np.argmax(zelt))
            print(f' a = {asym:.1f}: max|r(F_min-<N>)| = {np.abs(rf).max()*1e3:8.4f} mN; '
                  f'max|r Re/Im N1| = {np.abs(np.r_[rN[:,0].real, rN[:,0].imag]).max()*1e3:8.4f} mN, '
                  f'N2 = {np.abs(np.r_[rN[:,1].real, rN[:,1].imag]).max()*1e3:8.4f} mN, '
                  f'N3 = {np.abs(np.r_[rN[:,2].real, rN[:,2].imag]).max()*1e3:8.4f} mN; '
                  f'max|<N>-Mg| = {max(abs(r["mean_meas"]-MG) for r in res)*1e6:.3f} uN; '
                  f'Zeltspitze bei {cut[i_max]["cfg"][1]:.0f}°, Spannweite {zelt.max()-zelt.min():.4f} N; '
                  f'Delta<delta> Einzel/synchron = {(sd - MG/K)*1e9:+.3f}/{(syn["dmean"] - MG/K)*1e9:+.3f} nm; '
                  f'Konvergenz max {conv.max():.1e} N')
            print('    bandbegrenzt max|r(F_min-<N>)| [mN]: ' + ', '.join(
                f'k_max={km}: {max(abs(r["r_bl"][km]) for r in cut)*1e3:.4f}' for km in (3, 6, 9, 12)))
            if asym == 0.3:
                j = int(np.argmax(np.abs(rf)))
                print(f'    Ort des größten F_min-Residuums: phi2 = {cut[j]["cfg"][1]:.0f}°; '
                      f'Residuum synchron F_min: {syn["r_fmin"]*1e3:.4f} mN')


if __name__ == '__main__':
    main()
