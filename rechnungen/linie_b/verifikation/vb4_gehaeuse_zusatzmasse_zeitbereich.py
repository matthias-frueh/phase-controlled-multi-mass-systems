#!/usr/bin/env python3
"""
Gegenprüfung LB-10 (zugesetzte Luftmasse am Körper, Wirkung auf F_min und N_k).

UNABHÄNGIGER RECHENWEG: nichtlineares Kontaktmodell im ZEITBEREICH (eigenes vektorisiertes RK4, eigene
Egg-Beschleunigung aus den Formeln, kein Import von finesweep/linear_solver), statt linearer
Frequenzbereichslösung der Gruppe:
    (M + m_a) z'' = Fc(z, z') - M g - mu M abar(t),   Fc = -K z - C z'  falls z < 0 und Fc > 0, sonst 0
    (Kontaktregel wie Engine rhs(); abar = (a1 + a2 + a3)/3; Einzelmodul: abar = a1/3)
Gemessen wird nur die Kontaktkraft Fc (Luftkraft umgeht den Sensor; Annahme wie Gruppe).
Parameter (Quellenangabe, abgeschrieben): M = 0,65 kg, g = 9,81, f = 10 Hz, THOLD = 0,65, RTOP = 5 mm,
RBOT = RTOP*TFAST/THOLD, K = 1e4 N/m, C = 16 N s/m (zeta = 0,0992; bei anderen K zeta fest wie Präreg A4).
m_a: 4,60 g / 1,94 g (Gruppe: Scheibenformel (8/3) rho R^3 für 20x20 bzw. 15x15 cm) – ANNAHME der Gruppe.
Szenarien: (i) Gruppe: K = 1e4, mu = 1;  (ii) Präreg-A4-konsistent: mu = 0,4, K = 1e5 / 1e6 (zeta fest).
Auswertung: letzte 1,0 s (10 Perioden) nach 3 s Einschwingen; F_min/F_max auf dem 50-µs-Raster;
Harmonische N_k per FFT über ganze Perioden.
"""
import time

import numpy as np

M, G = 0.65, 9.81
MG = M * G
F = 10.0
T = 1 / F
THOLD = 0.65
TFAST = 1 - THOLD
RTOP = 0.005
RBOT = RTOP * TFAST / THOLD
A_H = -RTOP * (np.pi / (THOLD * T)) ** 2
A_F = RBOT * (np.pi / (TFAST * T)) ** 2
ZETA = 16.0 / (2 * np.sqrt(1e4 * M))


def a_egg(t):
    ph = np.mod(t, T) / T
    return np.where(ph < THOLD, A_H * np.sin(np.pi * ph / THOLD), A_F * np.sin(np.pi * (ph - THOLD) / TFAST))


def simulate(cases, dt=5e-5, t_sim=4.0, t_eval=1.0):
    """cases: Liste von dicts mit p2, p3 (None = Einzelmodul), K, C, mu, ma. Vektorisiert."""
    n = len(cases)
    K = np.array([c["K"] for c in cases]); C = np.array([c["C"] for c in cases])
    mu = np.array([c["mu"] for c in cases]); ma = np.array([c["ma"] for c in cases])
    single = np.array([c["p2"] is None for c in cases])
    tau2 = np.array([0.0 if c["p2"] is None else c["p2"] / 360 * T for c in cases])
    tau3 = np.array([0.0 if c["p3"] is None else c["p3"] / 360 * T for c in cases])
    Meff = M + ma

    def abar(t):
        a1 = a_egg(t)
        a23 = a_egg(t - tau2) + a_egg(t - tau3)
        return np.where(single, a1 / 3, (a1 + a23) / 3)

    def rhs(z, zd, t):
        Fs = -K * z - C * zd
        Fc = np.where((z < 0) & (Fs > 0), Fs, 0.0)
        return zd, (Fc - MG - mu * M * abar(t)) / Meff, Fc

    nst = int(round(t_sim / dt)); nev = int(round(t_eval / dt))
    z = np.full(n, -MG / K); zd = np.zeros(n)
    Fout = np.empty((nev, n))
    for i in range(nst):
        t = i * dt
        k1z, k1d, Fc = rhs(z, zd, t)
        if i >= nst - nev:
            Fout[i - (nst - nev)] = Fc
        k2z, k2d, _ = rhs(z + 0.5 * dt * k1z, zd + 0.5 * dt * k1d, t + 0.5 * dt)
        k3z, k3d, _ = rhs(z + 0.5 * dt * k2z, zd + 0.5 * dt * k2d, t + 0.5 * dt)
        k4z, k4d, _ = rhs(z + dt * k3z, zd + dt * k3d, t + dt)
        z = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6
        zd = zd + dt * (k1d + 2 * k2d + 2 * k3d + k4d) / 6
    return Fout


def main():
    t0 = time.time()
    combos = [("Triphasik (120,240)", 120.0, 240.0), ("(100,240)", 100.0, 240.0), ("(140,240)", 140.0, 240.0),
              ("Einzelmodul", None, None)]
    mas = [0.0, 1.94e-3, 4.60e-3]
    scen = [("K=1e4, mu=1 (Gruppe)", 1e4, 1.0), ("K=1e5, mu=0,4", 1e5, 0.4), ("K=1e6, mu=0,4", 1e6, 0.4),
            ("K=1e5, mu=1", 1e5, 1.0), ("K=1e6, mu=1", 1e6, 1.0)]
    cases = []
    for sn, K, mu in scen:
        C = 2 * ZETA * np.sqrt(K * M)
        for cn, p2, p3 in combos:
            for ma in mas:
                cases.append(dict(sn=sn, cn=cn, p2=p2, p3=p3, K=K, C=C, mu=mu, ma=ma))
    Fo = simulate(cases)
    nper = Fo.shape[0] // 10        # Samples je Periode
    spec = np.fft.rfft(Fo, axis=0) / Fo.shape[0]
    print("=" * 110)
    print(f"vb4 – zugesetzte Masse am Körper, Zeitbereich (RK4, DT 50 µs); Rechenzeit {time.time()-t0:.1f} s; "
          f"zeta = {ZETA:.5f}")
    print("=" * 110)
    idx = {(c["sn"], c["cn"], c["ma"]): i for i, c in enumerate(cases)}
    for sn, K, mu in scen:
        fn = np.sqrt(K / M) / (2 * np.pi)
        print(f"\n{sn}: f_n = {fn:.2f} Hz")
        fmins = {}
        for cn, p2, p3 in combos:
            i0 = idx[(sn, cn, 0.0)]
            F0 = Fo[:, i0]
            N0 = 2 * np.abs(spec[[10, 20, 30], i0])
            lift = (F0 <= 0).mean()
            fmins[cn] = F0.min()
            print(f"   {cn:20s} m_a=0: F_min = {F0.min():.6f} N, F_max = {F0.max():.5f} N, <N> = {F0.mean():.6f} N, "
                  f"Liftoff-Anteil {lift:.3f}, |N_1..3| = " + " ".join(f"{x:.4f}" for x in N0))
            for ma in mas[1:]:
                i1 = idx[(sn, cn, ma)]
                F1 = Fo[:, i1]
                dN = 2 * np.abs(spec[[10, 20, 30], i1] - spec[[10, 20, 30], i0])
                dabs = 2 * (np.abs(spec[[10, 20, 30], i1]) - np.abs(spec[[10, 20, 30], i0]))
                print(f"      m_a = {ma*1e3:.2f} g: dF_min = {F1.min()-F0.min():+.3e} N, dF_max = {F1.max()-F0.max():+.3e} N, "
                      f"d<N> = {F1.mean()-F0.mean():+.1e} N, |dN_k| = " + " ".join(f"{x:.2e}" for x in dN)
                      + " | d|N_k| = " + " ".join(f"{x:+.2e}" for x in dabs))
        # Zelt-Spanne nur grob (3 Punkte) zur Einordnung
        print(f"   F_min(120) - F_min(100) = {fmins['Triphasik (120,240)']-fmins['(100,240)']:.4f} N, "
              f"F_min(120) - F_min(140) = {fmins['Triphasik (120,240)']-fmins['(140,240)']:.4f} N")
        # Wirkung auf die Zeltdifferenz
        for ma in mas[1:]:
            d = []
            for cn in ("(100,240)", "(140,240)"):
                dd = (Fo[:, idx[(sn, 'Triphasik (120,240)', ma)]].min() - Fo[:, idx[(sn, cn, ma)]].min()) - \
                     (Fo[:, idx[(sn, 'Triphasik (120,240)', 0.0)]].min() - Fo[:, idx[(sn, cn, 0.0)]].min())
                d.append(dd)
            print(f"      m_a = {ma*1e3:.2f} g: Änderung der Differenz F_min(120)-F_min(100/140) = "
                  + " / ".join(f"{x:+.3e}" for x in d) + " N")


if __name__ == "__main__":
    main()
