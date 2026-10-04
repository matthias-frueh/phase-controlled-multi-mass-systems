#!/usr/bin/env python3
"""
P2 / linie_b / Befund 1: Kennzahlen (KC, Re, beta, delta, Re_s) des Trägers im Driftskript v2
und Größenordnung der linearen und quadratischen Kraftanteile (Luft, Wasser).

Eigene Rechnung. Kinematik direkt aus pcmms_fluid_drift_v2.py (unveränderte Kopie in quelle_kopie/):
v_osc(t) = -RATIO * r_dot(t), Raster DT = 50 µs über eine Periode.

Definitionen (alle SI):
  U_max   = max |v_osc|
  a       = halbe Spitze-Spitze-Auslenkung des Trägers (aus Integration von v_osc)
  KC_U    = U_max * T / D            (Definition über Spitzengeschwindigkeit)
  KC_a    = 2*pi*a / D               (Definition über Amplitude; identisch mit KC_U nur bei Sinus)
  Re      = U_max * D / nu
  beta    = Re / KC_U = D^2 / (nu*T) = f D^2 / nu
  delta   = sqrt(2 nu / omega)       (Stokes-Schicht)
  Re_s    = omega a^2 / nu = 2 (a/delta)^2   (Streaming-Reynoldszahl)
D-Varianten: 0.2 m (Notiz v5.2), sqrt(4A/pi) = 0.1954 m (Kreis gleicher Fläche A = 0.03 m^2 aus dem
Skript), sqrt(A) = 0.1732 m (Quadrat gleicher Fläche).

Kraftanteile (Annahme: Träger als Kugel gleicher Stirnfläche, R = sqrt(A/pi)); lineare Lösung für die
oszillierende Kugel (Stokes 1851, Landau-Lifschitz §24):
  F = -[6 pi mu R (1 + R/delta)] U - [ (2/3) pi R^3 rho + 3 pi R^2 rho delta ] dU/dt
Quasistationärer Zweiterm-Widerstand des Skripts: F_q = -C2*rho*U|U|, C2 = 0.5*0.8*0.03.
Ausgewertet je Harmonische k der tatsächlichen v_osc(t) und als Mittelwert (k = 0).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "quelle_kopie"))
import pcmms_fluid_drift_v2 as fd  # noqa: E402  (unveränderte Kopie)

MEDIEN = {
    # rho [kg/m^3], mu [Pa s]   (Luft 20 °C wie Notiz §8: mu = 1.8e-5; Wasser 20 °C)
    "Luft": (1.2, 1.8e-5),
    "Wasser": (1000.0, 1.0e-3),
}
F = fd.F_HZ
T = fd.T_CYC
OMEGA = 2 * np.pi * F
A_SKRIPT = fd.AREA
D_VARIANTEN = {"D=0.2 m (Notiz)": 0.2,
               "D=sqrt(4A/pi)": np.sqrt(4 * A_SKRIPT / np.pi),
               "D=sqrt(A)": np.sqrt(A_SKRIPT)}
KONFIG = {"synchron (0,0)": (0.0, 0.0),
          "Triphasik (120,240)": (120.0, 240.0),
          "langsamster Punkt (221.54,110.77)": (360 / 13 * 8, 360 / 13 * 4)}


def kinematik(p2, p3):
    v = fd.v_osc_profile(p2, p3)                       # m/s, 2000 Punkte
    x = np.cumsum(v) * fd.DT
    x -= x.mean()
    U = float(np.max(np.abs(v)))
    a = 0.5 * float(x.max() - x.min())
    return v, x, U, a


def harmonische(sig, kmax=4):
    c = np.fft.rfft(sig) / sig.size
    amp = np.abs(c[:kmax + 1]) * 2
    amp[0] = c[0].real                                 # Gleichanteil vorzeichenrichtig, ohne Faktor 2
    return amp, c


def kugelkraft_linear(Vk_complex, k, rho, mu, R):
    """Komplexe Amplitude der linearen Kugelkraft für eine Harmonische V_k exp(i k w t)."""
    w = k * OMEGA
    nu = mu / rho
    d = np.sqrt(2 * nu / w)
    c_visc = 6 * np.pi * mu * R * (1 + R / d)
    m_eff = (2 / 3) * np.pi * R**3 * rho + 3 * np.pi * R**2 * rho * d
    return -(c_visc + 1j * w * m_eff) * Vk_complex, c_visc * abs(Vk_complex), w * m_eff * abs(Vk_complex), d


def main():
    print("=" * 100)
    print("Befund 1 – Kennzahlen Träger (Driftskript v2), f = %.1f Hz, RATIO = %.4f, V_FAST = %.3f m/s"
          % (F, fd.RATIO, fd.V_FAST))
    print("=" * 100)
    for name, (p2, p3) in KONFIG.items():
        v, x, U, a = kinematik(p2, p3)
        print(f"\n[{name}]  U_max = {U*1e3:.4f} mm/s, a (halbe Spitze-Spitze) = {a*1e3:.4f} mm, "
              f"Spitze-Spitze = {2*a*1e3:.4f} mm, a_sin = U_max/omega = {U/OMEGA*1e3:.4f} mm")
        for med, (rho, mu) in MEDIEN.items():
            nu = mu / rho
            delta = np.sqrt(2 * nu / OMEGA)
            print(f"  {med}: nu = {nu:.3e} m^2/s, delta = {delta*1e3:.4f} mm, delta/a = {delta/a:.3f}, "
                  f"Re_s = omega a^2/nu = {OMEGA*a**2/nu:.4f}")
            for dn, D in D_VARIANTEN.items():
                KC_U = U * T / D
                KC_a = 2 * np.pi * a / D
                Re = U * D / nu
                beta = F * D**2 / nu
                print(f"    {dn:16s} D = {D:.4f} m: KC_U = {KC_U:.5f}, KC_a = {KC_a:.5f}, "
                      f"KC(a_Notiz=0.3 mm) = {2*np.pi*0.3e-3/D:.5f}, Re = {Re:8.2f}, beta = {beta:.4e}, "
                      f"Re/KC_U = {Re/KC_U:.4e}, delta/D = {delta/D:.2e}")

    # ---- Kraftanteile, Kugel gleicher Stirnfläche ----
    R = np.sqrt(A_SKRIPT / np.pi)
    print("\n" + "=" * 100)
    print(f"Kraftanteile (Annahme Kugel R = sqrt(A/pi) = {R:.4f} m; Skriptwiderstand C2 = {fd.C2:.4f} m^2)")
    print("=" * 100)
    for name, (p2, p3) in KONFIG.items():
        v, x, U, a = kinematik(p2, p3)
        _, cv = harmonische(v)
        for med, (rho, mu) in MEDIEN.items():
            fq = -fd.C2 * rho * v * np.abs(v)
            aq, _ = harmonische(fq)
            print(f"\n[{name}] {med}:")
            print("   k | |V_k| mm/s | lin. viskos N | lin. Trägheit N | quasistat. quadr. N (Skript)")
            for k in range(0, 5):
                if k == 0:
                    print(f"   0 | {abs(cv[0])*1e3:10.2e} | {'0 (lin.)':>13s} | {'0 (lin.)':>15s} | "
                          f"{aq[0]:+.3e}  (= F_bar_A Skript: {-fd.C2*rho*np.mean(v*np.abs(v)):+.3e})")
                    continue
                Vk = 2 * cv[k]
                _, fvis, finer, d = kugelkraft_linear(Vk, k, rho, mu, R)
                print(f"   {k} | {abs(Vk)*1e3:10.4f} | {fvis:13.3e} | {finer:15.3e} | {aq[k]:.3e}")
            # Verhältnis viskos/träge bei k=1 analytisch: 9 delta/(2R) für R >> delta
            d1 = np.sqrt(2 * mu / rho / OMEGA)
            print(f"   viskos/träge (k=1) analytisch ~ 9*delta/(2R)/(1+9*delta/(2R)) = "
                  f"{(9*d1/(2*R))/(1+9*d1/(2*R)):.4f};  Eigenträgheit Träger M_SHELL*omega*|V_1| = "
                  f"{fd.M_SHELL*OMEGA*abs(2*cv[1]):.3e} N; zugesetzte Masse/M_ges = "
                  f"{(2/3)*np.pi*R**3*rho/fd.M_TOTAL:.2e}")

    # ---- Stokes-Wang-Zylinder (Morison-Form, Notiz §6/Literatur Wang 1968) ----
    print("\n" + "=" * 100)
    print("Stokes-Wang (Kreiszylinder, laminar, anliegend): C_D und C_M als formale Morison-Beiwerte")
    print("=" * 100)
    for med, (rho, mu) in MEDIEN.items():
        nu = mu / rho
        for dn, D in D_VARIANTEN.items():
            beta = F * D**2 / nu
            pb = np.pi * beta
            v, x, U, a = kinematik(0.0, 0.0)
            KC = U * T / D
            CD = 1.5 * np.pi**3 / KC * (pb**-0.5 + pb**-1 - 0.25 * pb**-1.5)
            CM = 2 + 4 * pb**-0.5 + pb**-1.5
            ratio = CD * KC / (np.pi**2 * CM)
            print(f"  {med:6s} {dn:16s}: beta = {beta:.3e}, KC_U(sync) = {KC:.5f}, C_D,Wang = {CD:9.2f}, "
                  f"C_M = {CM:.4f}, F_D/F_I (Spitzen) = C_D KC/(pi^2 C_M) = {ratio:.4f}")


if __name__ == "__main__":
    main()
