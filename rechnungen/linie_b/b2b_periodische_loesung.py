#!/usr/bin/env python3
"""
P2 / linie_b / Befund 2 und 3: integriertes Modell des Driftskripts v2 als Kontrolle der gemittelten Bilanz.

Eigene Rechnung mit den unveränderten Funktionen/Parametern aus quelle_kopie/pcmms_fluid_drift_v2.py:
  M_ges dV/dt = -C2 rho |v_rel| v_rel,   v_rel = V - RATIO r_dot(t)     (integrate_drift() des Skripts)

(a) Periodische Lösung des integrierten Modells per Schießverfahren über eine Periode
    (RK4, DT = 50 µs wie im Skript; G(V0) = V(T; V0) - V0 = 0 mit brentq). Das liefert den
    stationären Wert des integrierten Modells ohne Einschwingen, also auch für rho = 1,2 (tau ~ 80 min),
    wo eine Zeitintegration bis zur Konvergenz nicht praktikabel ist.
    Periodenmittel von V: (i) Rechteck über die Schritt-Endwerte wie im Skript, (ii) RK4-konsistent
    (Simpson über k1..k4 ist für V nicht nötig; Trapez über die Schritte, periodisch = Rechteck).
(b) Vergleich mit drift_balance() (gemittelte Bilanz) bei rho = 1000, 100, 1.2.
(c) Einschwingen aus der Ruhe: V(t) nach 8 s bei rho = 1000 und rho = 1.2 (Fenster wie v1: 4-8 s) –
    zeigt, dass eine nicht eingeschwungene "Drift" proportional zu rho ist (Anfangsbeschleunigung F_bar_A/M).
(d) integrate_drift() des Skripts am langsamsten Rasterpunkt (221.54°, 110.77°), rho = 1000, tol = 1e-5.
"""
import os
import sys
import time

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "quelle_kopie"))
import pcmms_fluid_drift_v2 as fd  # noqa: E402

DT = fd.DT
NCYC = int(round(fd.T_CYC / DT))
PUNKTE = {"(0,0)": (0.0, 0.0), "(120,240)": (120.0, 240.0),
          "(221.54,110.77)": (360 / 13 * 8, 360 / 13 * 4)}
RHOS = [1000.0, 100.0, 1.2]


def rdot_halbraster(p2, p3):
    rd = fd.r_dot_factory(p2, p3)
    t = np.arange(2 * NCYC + 1) * (DT / 2)
    return [fd.RATIO * rd(x) for x in t]           # RATIO*r_dot an t_i, t_i+DT/2, t_i+DT


def eine_periode(V0, c, R, n_per=1, mittel=False):
    """RK4 wie integrate_drift(); R = RATIO*r_dot auf dem Halbraster einer Periode (periodisch)."""
    V = V0
    s = 0.0
    for _ in range(n_per):
        for i in range(NCYC):
            r0, rh, r1 = R[2 * i], R[2 * i + 1], R[2 * i + 2]
            u = V - r0; k1 = -c * abs(u) * u
            u = V + 0.5 * DT * k1 - rh; k2 = -c * abs(u) * u
            u = V + 0.5 * DT * k2 - rh; k3 = -c * abs(u) * u
            u = V + DT * k3 - r1; k4 = -c * abs(u) * u
            V += DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            s += V
    if mittel:
        return V, s / (NCYC * n_per)
    return V


def periodisch(p2, p3, rho):
    c = fd.C2 * rho / fd.M_TOTAL
    R = rdot_halbraster(p2, p3)
    amp = max(abs(x) for x in R) + 1e-9
    V0 = brentq(lambda v: eine_periode(v, c, R) - v, -amp, amp, xtol=1e-18, rtol=1e-15, maxiter=200)
    _, vmean = eine_periode(V0, c, R, mittel=True)
    return V0, vmean


def main():
    print("=" * 100)
    print("(a)/(b) Periodische Lösung des integrierten Modells vs. gemittelte Bilanz drift_balance()")
    print("=" * 100)
    print(f"{'Punkt':16s} {'rho':>7s} | {'v_d Bilanz mm/s':>16s} | {'<V> periodisch mm/s':>20s} | "
          f"{'rel. Abw.':>10s} | {'F_bar_A N':>11s} | {'tau s':>9s}")
    res = {}
    for name, (p2, p3) in PUNKTE.items():
        for rho in RHOS:
            t0 = time.time()
            vb, fa, tau = fd.drift_balance(p2, p3, rho=rho)
            V0, vm = periodisch(p2, p3, rho)
            res[(name, rho)] = vm
            print(f"{name:16s} {rho:7.1f} | {vb*1e3:+16.9f} | {vm*1e3:+20.9f} | {(vm-vb)/abs(vb):+10.2e} | "
                  f"{fa:+11.3e} | {tau:9.2f}   ({time.time()-t0:.1f} s)")
    print("\nDichtevergleich des integrierten Modells (periodische Lösung), rel. Abweichung zu rho = 1000:")
    for name in PUNKTE:
        a = res[(name, 1000.0)]
        print(f"  {name:16s}: rho=100: {(res[(name,100.0)]-a)/abs(a):+.2e}   rho=1.2: {(res[(name,1.2)]-a)/abs(a):+.2e}")

    print("\n" + "=" * 100)
    print("(c) Einschwingen aus der Ruhe (V(0) = 0) – Wert nach 8 s und Fenstermittel 4–8 s (v1-Fenster)")
    print("=" * 100)
    for name, (p2, p3) in list(PUNKTE.items())[:2]:
        R = rdot_halbraster(p2, p3)
        for rho in [1000.0, 1.2]:
            c = fd.C2 * rho / fd.M_TOTAL
            vb, fa, tau = fd.drift_balance(p2, p3, rho=rho)
            V, _ = eine_periode(0.0, c, R, n_per=40, mittel=True)
            V8, m48 = eine_periode(V, c, R, n_per=40, mittel=True)
            print(f"  {name:10s} rho={rho:7.1f}: <V>_(4-8 s) = {m48*1e3:+.6f} mm/s = {m48/vb*100:7.3f} % von v_d; "
                  f"F_bar_A*6s/M_ges = {fa*6/fd.M_TOTAL*1e3:+.6f} mm/s; tau = {tau:.1f} s")

    print("\n" + "=" * 100)
    print("(d) integrate_drift() (Skriptfunktion) am langsamsten Punkt, rho = 1000, tol = 1e-5")
    print("=" * 100)
    p2, p3 = PUNKTE["(221.54,110.77)"]
    t0 = time.time()
    vi, n = fd.integrate_drift(p2, p3)
    vb, _, tau = fd.drift_balance(p2, p3)
    vp = res[("(221.54,110.77)", 1000.0)]
    print(f"  integriert {vi*1e3:+.6f} mm/s nach {n} Perioden ({n*fd.T_CYC:.0f} s), Bilanz {vb*1e3:+.6f}, "
          f"periodisch {vp*1e3:+.6f}; Abbruchfehler (int-per)/per = {(vi-vp)/abs(vp):+.2e}; tau = {tau:.1f} s "
          f"({time.time()-t0:.0f} s Rechenzeit)")


if __name__ == "__main__":
    main()
