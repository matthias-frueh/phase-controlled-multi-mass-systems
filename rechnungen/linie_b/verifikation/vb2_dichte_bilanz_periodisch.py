#!/usr/bin/env python3
"""
Gegenprüfung LB-05/LB-06 (Dichteabhängigkeit der Linie-B-Drift).

UNABHÄNGIGE IMPLEMENTIERUNG (Skript der Gruppe und Quellskript nicht importiert):
  (a) Gemittelte Bilanz <(v_d+v)|v_d+v|> = 0 mit eigener vektorisierter Egg-Kurve, Mittelpunktsregel
      (N = 200000 je Periode statt Linksrechteck mit 2000) -> Diskretisierungsempfindlichkeit.
  (b) Periodische Lösung des integrierten Modells M dV/dt = -c2 rho |V - RATIO r_dot| (V - RATIO r_dot)
      mit scipy solve_ivp (DOP853, rtol 1e-11) statt festschrittigem RK4; Schießen mit brentq.
      Ergebnis = Periodenmittel von V (Gesamtimpuls/Masse; Mittel von r_dot = 0, also = Mittel der Hüllengeschw.).
  (c) Modell B mit zusätzlichem linearem Widerstand c1 (Notiz §4.2): c1 v_d + c2 rho <(v_d+v)|v_d+v|> = 0.
      c1 = 6 pi mu R, R = sqrt(A/pi) als ANNAHME (wie Gruppe) und zusätzlich c1 x 0,1 und x 10.
      Crossover rho* = c1 / (2 c2 <|v|>)  (Linearisierung der Bilanz um v_d = 0).
  (d) Analytische Kleinsignal-Näherung v_d ~ -<v|v|>/(2<|v|>) (für |v_d| << |v|), als Plausibilitätskontrolle.
"""
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

M_TOT = 0.75
RATIO = 0.2
CD, AREA = 0.8, 0.03
C2 = 0.5 * CD * AREA
F, HOLD, V_FAST = 10.0, 0.65, 0.06
T = 1 / F
TF = 1 - HOLD
V_SLOW = V_FAST * TF / HOLD
MU = 1.8e-5


def egg_vel(ph):
    ph = np.mod(ph, 1.0)
    return np.where(ph < TF, V_FAST * np.sin(np.pi * ph / TF), -V_SLOW * np.sin(np.pi * (ph - TF) / HOLD))


def rdot(t, p2, p3):
    ph = np.asarray(t) / T
    return (egg_vel(ph) + egg_vel(ph - p2 / 360.0) + egg_vel(ph - p3 / 360.0)) / 3.0


def vosc_grid(p2, p3, N):
    t = (np.arange(N) + 0.5) * T / N
    return -RATIO * rdot(t, p2, p3)


def bilanz(v, c1=0.0, rho=1.0):
    amp = np.abs(v).max() + 1e-9
    return brentq(lambda x: c1 * x + C2 * rho * np.mean((x + v) * np.abs(x + v)), -amp, amp, xtol=1e-16, rtol=1e-14)


def periodisch(p2, p3, rho):
    c = C2 * rho / M_TOT

    def f(t, y):
        vr = y[0] - RATIO * rdot(t, p2, p3)
        return [-c * abs(vr) * vr, y[0]]

    def shoot(V0):
        s = solve_ivp(f, (0, T), [V0, 0.0], method="DOP853", rtol=1e-12, atol=1e-16, max_step=T / 400)
        return s.y[0, -1] - V0, s.y[1, -1] / T

    v = vosc_grid(p2, p3, 20000)
    vb = bilanz(v)
    a, b = vb - 0.3 * abs(vb) - 1e-6, vb + 0.3 * abs(vb) + 1e-6
    V0 = brentq(lambda x: shoot(x)[0], a, b, xtol=1e-18, rtol=1e-13)
    return V0, shoot(V0)[1], vb


def main():
    pts = [(0.0, 0.0), (120.0, 240.0), (221.54, 110.77)]
    print("=" * 100)
    print("vb2 – Dichteabhängigkeit, unabhängige Implementierung")
    print("=" * 100)
    print("(a) Bilanz, Diskretisierung N je Periode (Mittelpunktsregel), c1 = 0, rho fällt heraus:")
    for p in pts:
        out = []
        for N in (2000, 20000, 200000):
            out.append(bilanz(vosc_grid(*p, N)))
        v = vosc_grid(*p, 200000)
        vk = -np.mean(v * np.abs(v)) / (2 * np.mean(np.abs(v)))
        print(f"   {p}: v_d = " + " / ".join(f"{x*1e3:+.10f}" for x in out) + " mm/s (N=2e3/2e4/2e5); "
              f"Kleinsignal -<v|v|>/(2<|v|>) = {vk*1e3:+.5f} mm/s")
        for rho in (1000.0, 1.2, 1e-3):
            Fa = -C2 * rho * np.mean(v * np.abs(v))
            tau = M_TOT / (2 * C2 * rho * np.mean(np.abs(v)))
            print(f"      rho={rho:8.3g}: F_bar_A = {Fa:+.4e} N, tau = {tau:.4g} s")

    print("\n(b) periodische Lösung des integrierten Modells (DOP853 + Schießen):")
    t0 = time.time()
    res = {}
    for p in pts:
        for rho in (1000.0, 100.0, 1.2):
            V0, Vm, vb = periodisch(*p, rho)
            res[(p, rho)] = Vm
            print(f"   {p} rho={rho:7.1f}: <V>_periodisch = {Vm*1e3:+.9f} mm/s, Bilanz {vb*1e3:+.9f} mm/s, "
                  f"rel. Abw. {(Vm-vb)/vb:+.2e}")
        print(f"      Vergleich rho=1,2 gegen 1000: rel. {(res[(p,1.2)]-res[(p,1000.0)])/res[(p,1000.0)]:+.2e}")
    print(f"   Rechenzeit {time.time()-t0:.1f} s")

    print("\n(c) Modell B mit linearem Zusatzterm c1 (ANNAHME c1 = 6 pi mu R, R = sqrt(A/pi); Variation x0,1 / x10):")
    R = np.sqrt(AREA / np.pi)
    c1_0 = 6 * np.pi * MU * R
    for p in pts[:2]:
        v = vosc_grid(*p, 200000)
        vinf = bilanz(v)
        for fac in (0.1, 1.0, 10.0):
            c1 = fac * c1_0
            rs = c1 / (2 * C2 * np.mean(np.abs(v)))
            vals = []
            for rho in (1000.0, 1.2, 0.12, 0.012):
                vals.append(bilanz(v, c1, rho) / vinf)
            # Steigung d ln v_d / d ln rho bei rho = 1,2
            e = 1e-3
            sl = (np.log(abs(bilanz(v, c1, 1.2 * (1 + e)))) - np.log(abs(bilanz(v, c1, 1.2 * (1 - e))))) / (
                np.log(1 + e) - np.log(1 - e))
            print(f"   {p} c1 = {c1:.3e} N s/m: rho* = {rs:.3f} kg/m^3; v_d/v_d(c1=0) bei rho = 1000/1,2/0,12/0,012: "
                  + " / ".join(f"{x:.4f}" for x in vals) + f"; d ln v_d/d ln rho (rho=1,2) = {sl:.3f}")


if __name__ == "__main__":
    main()
