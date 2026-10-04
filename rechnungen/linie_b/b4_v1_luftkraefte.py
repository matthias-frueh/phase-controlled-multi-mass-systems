#!/usr/bin/env python3
"""
P2 / linie_b / Befund 4: Größenordnung der Luftkräfte (und eines elektrostatischen Überschlags) im V1-Aufbau
der Linie A, verglichen mit u_c = 0,0327 N, Delta(F_min) = 0,117 N, Delta F_Zelt = 0,4693 N (Präreg-Anhang A4)
und M*g = 6,3765 N.

EIGENE RECHNUNG auf Basis von:
  - Modulkinematik: Egg-Lageprofil der Referenz-Engine (code/finesweep.py, identisch zu pcmms_v3a):
    Hub RTOP + RBOT = 7,69 mm, f = 10 Hz, THOLD = 0,65.
  - Gehäusebewegung: lineare Dauerkontaktlösung (Ansatz wie code/linear_solver.py, hier mit
    zusätzlicher Masse m_a auf der Auflagerkoordinate):
        (M + m_a) z'' = N - M g - M abar(t),  N = -K z - C z'  (Kontakt)
        N_k = M Abar_k (K + i w C) / (K + i w C - (M + m_a) w^2)
    Abgleich mit linear_solver.solve() für m_a = 0 (F_min an drei Punkten).
ANNAHMEN (kein V1-Aufbau im Bestand, Geometrie nicht festgelegt):
  - Modul als Kugel R_m = 1,45 cm (100 g Stahl), 2,5 cm, oder Platte (Scheibe breitseitig) R = 4 cm.
  - Gehäuse 20 x 20 x 10 cm (Stirnfläche 0,04 m^2, Volumen 4 l) bzw. 15 x 15 x 8 cm (1,8 l).
  - Luft 20 °C: rho = 1,2 kg/m^3, mu = 1,8e-5 Pa s, c = 343 m/s.
Formeln:
  - Oszillierende Kugel (linear, Stokes 1851): F = -[6 pi mu R (1+R/delta)] v - [(2/3) pi R^3 rho + 3 pi R^2 rho delta] v'
  - Scheibe breitseitig, Potentialströmung: m_a = (8/3) rho R^3
  - Quadratischer Widerstand, quasistationär, als OBERE SCHRANKE: F = 0,5 rho C_D A v|v|, C_D = 2
  - Schallabstrahlung kompakte Kugel (ka << 1): R_rad = (pi/3) rho c a^2 (ka)^4
  - Quetschfilm Scheibe (inkompressibel): c_sq = 3 pi mu R^4 / (2 h^3)
  - Auftrieb rho g V; Elektrostatik Plattennäherung sigma^2 A / (2 eps0)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../code'))
import finesweep as fs          # noqa: E402  (nur Parameter und z_egg_zdd)
import linear_solver as ls      # noqa: E402  (nur Abgleich)

RHO, MU, C_SCHALL, G = 1.2, 1.8e-5, 343.0, 9.81
NU = MU / RHO
F = fs.F_HZ
W = 2 * np.pi * F
T = fs.T_CYC
M = fs.M
MG = fs.MG
U_C, D_FMIN, D_ZELT = 0.0327, 0.117, 0.4693      # Präreg-Anhang A4 (Quellenangabe)
EPS0 = 8.854e-12
NFEIN = 16000


def modul_kinematik():
    t = np.arange(NFEIN) * (T / NFEIN)
    a = fs.z_egg_zdd(t)
    # analytische Lage/Geschwindigkeit des Egg-Profils (Halbsinus-Lagebögen)
    phi = np.mod(t, T) / T
    hold = phi < fs.THOLD
    s_h = phi / fs.THOLD
    s_f = (phi - fs.THOLD) / fs.TFAST
    z = np.where(hold, fs.RTOP * np.sin(np.pi * s_h), -fs.RBOT * np.sin(np.pi * s_f))
    v = np.where(hold, fs.RTOP * np.pi / (fs.THOLD * T) * np.cos(np.pi * s_h),
                 -fs.RBOT * np.pi / (fs.TFAST * T) * np.cos(np.pi * s_f))
    # Selbstprüfung: numerische Ableitung von v gegen a
    dv = np.gradient(v, T / NFEIN)
    err = np.max(np.abs(dv - a)[5:-5]) / np.max(np.abs(a))
    return t, z, v, a, err


def harm(sig, kmax=4):
    c = np.fft.rfft(sig) / sig.size
    out = 2 * c[:kmax + 1]
    out[0] = c[0]
    return out                     # komplexe Amplituden; k = 0 reell (Gleichanteil)


def kugel_linear(R, k):
    w = k * W
    d = np.sqrt(2 * NU / w)
    c_v = 6 * np.pi * MU * R * (1 + R / d)
    m_e = (2 / 3) * np.pi * R**3 * RHO + 3 * np.pi * R**2 * RHO * d
    return c_v, m_e, d


def r_rad(R, k):
    ka = k * W / C_SCHALL * R
    return np.pi / 3 * RHO * C_SCHALL * R**2 * ka**4


def zeile(name, werte):
    return f"  {name:44s}" + " ".join(f"{x:11.3e}" for x in werte)


def main():
    t, z, v, a, err = modul_kinematik()
    print("=" * 110)
    print("Befund 4 – Luftkräfte im V1-Aufbau (Größenordnung), Vergleich u_c = 0,0327 N, 0,1*u_c = 3,27e-3 N")
    print("=" * 110)
    print(f"Modulprofil: Hub = {z.max()-z.min():.5e} m, v_max = {np.abs(v).max():.4f} m/s, "
          f"a_min/a_max = {a.min():.3f}/{a.max():.3f} m/s^2, Ableitungsprüfung rel. {err:.1e}")
    print(f"  <v|v|> = {np.mean(v*np.abs(v)):+.3e} m^2/s^2 (Egg-Lageprofil: je Modul exakt 0, da v in jeder"
          f" Phase symmetrisch), <v^3> = {np.mean(v**3):+.2e}")
    Vk, Ak = harm(v), harm(a)
    print("  |v_k| (k=0..4) m/s :", " ".join(f"{abs(x):.4e}" for x in Vk))
    print("  |a_k| (k=0..4) m/s^2:", " ".join(f"{abs(x):.4e}" for x in Ak))
    a_half = 0.5 * (z.max() - z.min())

    # ---------------- Module ----------------
    print("\n--- (1) bewegtes Modul in offener Luft (obere Schranke; im geschlossenen Gehäuse intern) ---")
    module = {"Kugel R=1,45 cm (100 g Stahl)": ("kugel", 0.0145),
              "Kugel R=2,5 cm": ("kugel", 0.025),
              "Scheibe breitseitig R=4 cm": ("scheibe", 0.04)}
    print(f"  {'Spalten: k =':44s}" + " ".join(f"{k:>11d}" for k in range(5)))
    for name, (typ, R) in module.items():
        D = 2 * R
        KC = 2 * np.pi * a_half / D
        beta = F * D**2 / NU
        d1 = np.sqrt(2 * NU / W)
        print(f"\n  {name}: KC = 2 pi a/D = {KC:.3f}, KC_U = v_max T/D = {np.abs(v).max()*T/D:.3f}, "
              f"beta = {beta:.0f}, delta = {d1*1e3:.3f} mm, delta/a = {d1/a_half:.3f}, "
              f"Re_s = w a^2/nu = {W*a_half**2/NU:.1f}, Re_max = {np.abs(v).max()*D/NU:.0f}")
        am, vis, rad = [0.0], [0.0], [0.0]
        for k in range(1, 5):
            c_v, m_e, d = kugel_linear(R, k)
            if typ == "scheibe":
                m_e = (8 / 3) * RHO * R**3 + 3 * np.pi * R**2 * RHO * d    # Potential + Schicht (Näherung)
            am.append(m_e * abs(Ak[k]))
            vis.append(c_v * abs(Vk[k]))
            rad.append(r_rad(R, k) * abs(Vk[k]))
        A = np.pi * R**2
        fq = 0.5 * RHO * 2.0 * A * v * np.abs(v)
        Fq = harm(fq)
        print(zeile("zugesetzte Masse + Schicht |m_e a_k| N", am))
        print(zeile("viskos (Stokes-Schicht) |c_v v_k| N", vis))
        print(zeile("quadratisch C_D=2 (Schranke) |F_k| N", [abs(x) if k else x.real for k, x in enumerate(Fq)]))
        print(zeile("Schallabstrahlung |R_rad v_k| N", rad))
        m_a = (2 / 3) * np.pi * R**3 * RHO if typ == "kugel" else (8 / 3) * RHO * R**3
        print(f"    zugesetzte Masse m_a = {m_a*1e3:.4f} g; relativ zu m_j = 0,1 kg: {m_a/0.1:.1e}, "
              f"zu M/3 = 0,2167 kg: {m_a/(M/3):.1e}  (Fehler von H3-Vorhersage G_F m_j a_k in gleicher Höhe)")

    # ---------------- Gehäuse ----------------
    print("\n--- (2) Gehäuse auf dem Kontakt: Bewegung aus linearer Dauerkontaktlösung, zugesetzte Masse ---")
    P, n = ls.profile_spectrum("egg")
    kk = np.arange(P.size)
    zeta = fs.C_DAMP / (2 * np.sqrt(fs.K * M))
    geh = {"20x20x10 cm (A=0,04 m^2, V=4 l)": (0.04, 4e-3), "15x15x8 cm (A=0,0225 m^2, V=1,8 l)": (0.0225, 1.8e-3)}
    konf = {"Einzelmodul (L_j)": None, "Triphasik (120,240)": (120.0, 240.0), "(100,240)": (100.0, 240.0)}

    def loesung(comb, K, C, m_add, hubfaktor=1.0):
        w = W * kk
        den = K + 1j * w * C - (M + m_add) * w**2
        A = P * comb * hubfaktor
        Nk = M * A * (K + 1j * w * C) / den
        Zk = -M * A / den
        N_t = MG + np.fft.irfft(Nk, n)
        z_t = -MG / K + np.fft.irfft(Zk, n)
        zdd_t = np.fft.irfft(-(w**2) * Zk, n)
        return N_t, z_t, zdd_t, Nk, Zk

    # Abgleich mit linear_solver (m_add = 0)
    sol = ls.solve([120.0, 100.0, 140.0], [240.0, 240.0, 240.0])
    for i, p2 in enumerate([120.0, 100.0, 140.0]):
        comb = (1 + np.exp(-1j * kk * np.radians(p2)) + np.exp(-1j * kk * np.radians(240.0))) / 3
        N_t, *_ = loesung(comb, fs.K, fs.C_DAMP, 0.0)
        print(f"  Abgleich F_min({p2:.0f},240): eigene lineare Lösung {N_t.min():.6f} N, "
              f"linear_solver {sol['F_min_lin'][i]:.6f} N")

    for gname, (A_h, V_h) in geh.items():
        R_h = np.sqrt(A_h / np.pi)
        m_ah = (8 / 3) * RHO * R_h**3
        print(f"\n  Gehäuse {gname}: Scheiben-Äquivalent R = {R_h:.4f} m, m_a = (8/3) rho R^3 = {m_ah*1e3:.2f} g "
              f"= {m_ah/M*100:.2f} % von M; f_n-Verschiebung = {(1/np.sqrt(1+m_ah/M)-1)*100:+.3f} %; "
              f"statischer Auftrieb rho g V = {RHO*G*V_h:.4f} N = {RHO*G*V_h/U_C:.2f} u_c")
        for K in [1e4, 1e5, 1e6]:
            C = 2 * zeta * np.sqrt(K * M)
            fn = np.sqrt(K / M) / (2 * np.pi)
            for cname, ph in konf.items():
                if ph is None:
                    comb = np.ones(P.size) / 3        # nur Modul 1 bewegt (Gewicht 1/3 wie in der Engine)
                else:
                    comb = (1 + np.exp(-1j * kk * np.radians(ph[0])) + np.exp(-1j * kk * np.radians(ph[1]))) / 3
                N0, z0, zdd0, Nk0, Zk0 = loesung(comb, K, C, 0.0)
                N1, z1, zdd1, Nk1, Zk1 = loesung(comb, K, C, m_ah)
                norm = 2.0 / n                         # rfft-Koeffizienten -> Amplituden
                dN = norm * np.abs(Nk1[1:4] - Nk0[1:4])
                Fam = norm * m_ah * np.abs(W * kk[1:4])**2 * np.abs(Zk0[1:4])
                Namp = norm * np.abs(Nk0[1:4])
                kontakt = "Dauerkontakt" if (N0.min() > 0) else "LIFTOFF (linear ungültig)"
                print(f"    K={K:.0e} (f_n={fn:6.2f} Hz) {cname:20s}: z_pp = {(z0.max()-z0.min())*1e3:.4f} mm, "
                      f"|z''|max = {np.abs(zdd0).max():.3f} m/s^2, F_min = {N0.min():.4f} N [{kontakt}]")
                print(f"       |N_k| k=1..3: " + " ".join(f"{x:.3e}" for x in Namp) + " N")
                print(f"       m_a*|z''_k| k=1..3: " + " ".join(f"{x:.2e}" for x in Fam) +
                      f" N | |dN_k| durch m_a: " + " ".join(f"{x:.2e}" for x in dN) +
                      f" N | dF_min = {N1.min()-N0.min():+.2e} N, dF_max = {N1.max()-N0.max():+.2e} N")
                # Quetschfilm-Trägheit: Skala des Gleichanteils |F_bar| ~ pi rho R^4 <zdot^2> / (16 h^2)
                # (reibungsfrei, kleine Amplitude; Vorzeichen hängt von der Randbedingung am Spaltrand ab)
                zd_t = np.fft.irfft(1j * W * kk * Zk0, n)
                zd2 = float(np.mean(zd_t**2))
                skal = [np.pi * RHO * R_h**4 * zd2 / (16 * h**2) for h in (1e-3, 3e-3, 10e-3)]
                print(f"       Quetschfilm-Trägheit, Skala Gleichanteil (h = 1/3/10 mm): "
                      + " ".join(f"{x:.1e}" for x in skal) + f" N  (zdot_rms = {np.sqrt(zd2)*1e3:.2f} mm/s, "
                      f"w h^2/nu bei 1/3/10 mm, 20 Hz: " + "/".join(f"{2*W*h**2/NU:.0f}" for h in (1e-3, 3e-3, 10e-3)) + ")")
        # Stokes-Schicht und Schall am Gehäuse, Quetschfilm
        R_s = (3 * V_h / (4 * np.pi)) ** (1 / 3)
        for k in [1, 2, 3]:
            c_v, m_e, d = kugel_linear(R_s, k)
            print(f"    Kugel-Äquivalent R = {R_s:.3f} m, k={k}: c_visc = {c_v:.3e} N s/m (C = 16 N s/m), "
                  f"R_rad = {r_rad(R_s, k):.2e} N s/m")
        for h in [1e-3, 3e-3, 10e-3]:
            c_sq = 3 * np.pi * MU * R_h**4 / (2 * h**3)
            sq = 12 * MU * (2 * W) * R_h**2 / (1e5 * h**2)
            print(f"    Quetschfilm unter Gehäuseboden, Spalt h = {h*1e3:4.1f} mm: c_sq = {c_sq:.3e} N s/m "
                  f"= {c_sq/16*100:.2f} % von C = 16 N s/m; Quetschzahl (20 Hz) = {sq:.2e}")
        # Thermik / Dichteänderung
        for dT in [1.0, 5.0, 10.0]:
            print(f"    belüftetes Gehäuse, Innenluft +{dT:4.1f} K: Delta m g = {RHO*V_h*dT/293.15*G:.2e} N; "
                  f"Aussenluft-Dichte -{dT/293.15*100:.2f} %: Delta Auftrieb = {RHO*G*V_h*dT/293.15:.2e} N")
        print(f"    Luftdruck +-10 hPa: Delta Auftrieb = {RHO*G*V_h*0.01:.2e} N")

    # ---------------- Elektrostatik / Konvektion (Überschlag) ----------------
    print("\n--- (3) Überschläge außerhalb der Luftmechanik ---")
    for sigma in [1e-7, 1e-6, 1e-5]:
        print(f"  Elektrostatik, Flächenladung {sigma:.0e} C/m^2 auf 0,04 m^2 gegenüber geerdeter Fläche: "
              f"F = sigma^2 A/(2 eps0) = {sigma**2*0.04/(2*EPS0):.2e} N")
    dT, L = 5.0, 0.1
    U = np.sqrt(G * dT / 293.15 * L)
    Gr = G * dT / 293.15 * L**3 / NU**2
    dl = L * Gr**-0.25
    tau = MU * U / dl
    print(f"  Konvektion, Gehäusewand +{dT} K, L = {L} m: U ~ {U:.3f} m/s, Gr = {Gr:.2e}, delta ~ {dl*1e3:.1f} mm, "
          f"Wandschub ~ {tau:.2e} Pa x 0,08 m^2 = {tau*0.08:.1e} N")


if __name__ == "__main__":
    main()
