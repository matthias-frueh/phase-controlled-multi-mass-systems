#!/usr/bin/env python3
"""
P2 / linie_b / Befund 3: Wo geht rho in die Drift ein? Kraft- und Geschwindigkeitsaussage getrennt.

Eigene Rechnung mit quelle_kopie/pcmms_fluid_drift_v2.py (unverändert):
  (1) Code-Beleg: Quelltext von drift_balance() – die Bilanzfunktion für v_d enthält rho nicht.
  (2) drift_balance() bei rho = 1000 … 0,0012: v_d konstant, F_bar_A ∝ rho, tau ∝ 1/rho.
  (3) Modell B MIT linearem Term c1 (Notiz v5.2 §4.2): c1 <V> + c2 rho <V|V|> = 0 mit V = v_d + v_osc.
      Illustrativ c1 = 6 pi mu R (stationärer Stokes-Widerstand einer Kugel R = sqrt(A/pi)) – ANNAHME,
      nicht validiert (Drift-Re ~ 10, außerhalb Stokes). Zeigt: v_d ∝ rho unterhalb des Crossovers
      rho* = c1 / (2 c2 <|v_osc|>), Sättigung darüber.
"""
import inspect
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "quelle_kopie"))
import pcmms_fluid_drift_v2 as fd  # noqa: E402

MU = 1.8e-5


def main():
    print("(1) Quelltext drift_balance() (Kopie, unverändert):")
    src = inspect.getsource(fd.drift_balance)
    for ln in src.splitlines():
        mark = "  <-- v_d: rho kommt nicht vor" if "brentq" in ln else ("  <-- rho" if "rho" in ln and "def" not in ln
                                                                        and '"' not in ln else "")
        print("    " + ln + mark)

    print("\n(2) drift_balance() über rho:")
    print(f"    {'rho':>9s} | {'v_d mm/s (0,0)':>15s} | {'F_bar_A N':>11s} | {'tau s':>11s} | "
          f"{'v_d mm/s (120,240)':>18s} | {'F_bar_A N':>11s}")
    for rho in [1000.0, 100.0, 1.2, 0.12, 0.0012]:
        a = fd.drift_balance(0, 0, rho)
        b = fd.drift_balance(120, 240, rho)
        print(f"    {rho:9.4f} | {a[0]*1e3:+15.10f} | {a[1]:+11.3e} | {a[2]:11.4g} | {b[0]*1e3:+18.10f} | {b[1]:+11.3e}")

    print("\n(3) Modell B mit c1 > 0 (illustrativ, c1 = 6 pi mu R):")
    R = np.sqrt(fd.AREA / np.pi)
    c1 = 6 * np.pi * MU * R
    for (p2, p3) in [(0.0, 0.0), (120.0, 240.0)]:
        v = fd.v_osc_profile(p2, p3)
        amp = float(np.max(np.abs(v))) + 1e-9
        vd_inf = fd.drift_balance(p2, p3)[0]
        rho_star = c1 / (2 * fd.C2 * float(np.mean(np.abs(v))))
        print(f"  ({p2:.0f},{p3:.0f}): c1 = {c1:.3e} N s/m, rho* = c1/(2 c2 <|v_osc|>) = {rho_star:.3f} kg/m^3, "
              f"v_d(c1=0) = {vd_inf*1e3:+.5f} mm/s")
        for rho in [1000.0, 10.0, 2.4, 1.2, 0.6, 0.12, 0.012, 0.0012]:
            f = lambda x: c1 * x + fd.C2 * rho * float(np.mean((x + v) * np.abs(x + v)))
            vd = brentq(f, -amp, amp, xtol=1e-16)
            print(f"     rho = {rho:8.4f}: v_d = {vd*1e3:+.6f} mm/s = {vd/vd_inf:6.4f} * v_d(c1=0)")


if __name__ == "__main__":
    main()
