#!/usr/bin/env python3
"""
PCMMS – Fluid-Drift mit Phasenkopplung (3 Module) – Version 2 (06.09.2026)
==========================================================================
Ersetzt pcmms_fluid_drift.py (v1) nicht, sondern liegt daneben. Änderungen gegenüber v1:

  1. Stationäre Drift primär über die gemittelte Bilanz
         <(v_d + v_osc) |v_d + v_osc|> = 0,   v_osc = -RATIO * r_dot(t)
     (Modell B der Notiz, c1 = 0). Die v1-Karte war mit dem Fenster 4–8 s bei
     Einschwingzeiten von 6–38 s (Wasser) unzureichend eingeschwungen: Beträge nur
     15–66 % des stationären Werts, konfigurationsabhängig; Vorzeichen unverändert.
  2. Integriertes Modell (RK4 wie v1) nur noch als Kontrolle, mit Abbruchkriterium über
     aufeinanderfolgende Periodenmittel statt festem Fenster.
  3. rho als Parameter (v1: fest RHO_WATER = 1000). Die stationäre Drift ist im gemittelten
     Modell dichteunabhängig; nur Einschwingzeit und Kraft skalieren mit rho.
  4. Je Rasterpunkt zusätzlich: F_bar_A = -c2*rho*<v_osc|v_osc|> (Gleichrichtungskraft bei
     vorgegebener Bewegung, Modell A/C der Notiz) und tau = M/(2*c2*rho*<|v_osc|>).
  5. CSV wird geschrieben ('w'), nicht angehängt ('a'); Header erweitert.
  6. Kleinigkeiten: kein nacktes except, keine ungültige Escape-Sequenz.

Alle Größen gelten innerhalb des Zweiterm-Ansatzes mit stationärem C_D (Notiz §6 offen).
Vorzeichen: +x = Richtung der schnellen Innenmassenphase (egg_vel > 0). Der Träger bewegt sich
dann schnell nach -x; die mittlere Medienkraft zeigt nach +x, die Drift ebenfalls.
"""

import csv
import math
import time

import numpy as np
from scipy.optimize import brentq

# ------------------------------------------------------------
# KONFIGURATION
# ------------------------------------------------------------
N_GRID = 13
RHO = 1000.0            # kg/m^3  (1000 Wasser wie v1; 1.2 Luft)
SAVE_CSV = True
CSV_NAME = f"sweep_{N_GRID}x{N_GRID}_drift_v2.csv"
INTEGRATED_CHECK = False        # True: zusätzlich integriertes Modell an den Kontrollpunkten unten
CHECK_POINTS = [(0.0, 0.0), (120.0, 240.0)]

# Physikalische Parameter (wie v1)
M_SHELL = 0.6
M_ARM = 0.05
N_ARMS = 3
M_TOTAL = M_SHELL + N_ARMS * M_ARM
RATIO = (N_ARMS * M_ARM) / M_TOTAL
CD = 0.8
AREA = 0.03
C2 = 0.5 * CD * AREA          # F_quad = -C2 * rho * V|V|

F_HZ = 10.0
T_CYC = 1.0 / F_HZ
HOLD = 0.65
V_FAST = 0.06
V_SLOW = V_FAST * (1.0 - HOLD) / HOLD

DT = 5e-5
T_GRID = np.arange(0.0, T_CYC, DT)


# ------------------------------------------------------------
# EGG-PROFIL (wie v1)
# ------------------------------------------------------------
def egg_vel(t):
    phi = (t % T_CYC) / T_CYC
    tf = 1.0 - HOLD
    if phi < tf:
        return V_FAST * math.sin(math.pi * phi / tf)
    return -V_SLOW * math.sin(math.pi * (phi - tf) / HOLD)


def r_dot_factory(phi2_deg, phi3_deg):
    tau2 = math.radians(phi2_deg) / (2 * math.pi * F_HZ)
    tau3 = math.radians(phi3_deg) / (2 * math.pi * F_HZ)

    def r_dot(t):
        return (egg_vel(t) + egg_vel(t - tau2) + egg_vel(t - tau3)) / N_ARMS

    return r_dot


def v_osc_profile(phi2_deg, phi3_deg):
    """Trägergeschwindigkeit ohne Drift über eine Periode: v_osc = -RATIO * r_dot."""
    r_dot = r_dot_factory(phi2_deg, phi3_deg)
    return -RATIO * np.array([r_dot(t) for t in T_GRID])


# ------------------------------------------------------------
# STATIONÄRE DRIFT (gemittelte Bilanz, Modell B, c1 = 0)
# ------------------------------------------------------------
def drift_balance(phi2_deg, phi3_deg, rho=RHO):
    """Gibt (v_d, F_bar_A, tau) zurück.
    v_d      : stationäre Drift aus <(v_d+v_osc)|v_d+v_osc|> = 0  (dichteunabhängig)
    F_bar_A  : -C2*rho*<v_osc|v_osc|>, Gleichrichtungskraft bei vorgegebener Bewegung
    tau      : M/(2*C2*rho*<|v_osc|>), Einschwingzeit der Drift
    """
    v = v_osc_profile(phi2_deg, phi3_deg)
    amp = float(np.max(np.abs(v))) + 1e-9
    vd = brentq(lambda x: float(np.mean((x + v) * np.abs(x + v))), -amp, amp, xtol=1e-15)
    f_bar_a = -C2 * rho * float(np.mean(v * np.abs(v)))
    tau = M_TOTAL / (2 * C2 * rho * float(np.mean(np.abs(v))))
    return vd, f_bar_a, tau


# ------------------------------------------------------------
# INTEGRIERTES MODELL (RK4 wie v1) MIT ABBRUCHKRITERIUM
# ------------------------------------------------------------
def integrate_drift(phi2_deg, phi3_deg, rho=RHO, tol=1e-5, min_periods=20, max_periods=20000):
    """Integriert M*dVcm/dt = -C2*rho*|v_rel|*v_rel, v_rel = Vcm - RATIO*r_dot(t).
    Abbruch, wenn sich das Periodenmittel über 10 Perioden um weniger als tol (relativ) ändert.
    Gibt (v_d, Anzahl Perioden) zurück."""
    r_dot = r_dot_factory(phi2_deg, phi3_deg)
    c = C2 * rho / M_TOTAL
    cyc = int(round(T_CYC / DT))

    def acc(Vx, tx):
        vr = Vx - RATIO * r_dot(tx)
        return -c * abs(vr) * vr

    V = 0.0
    means = []
    for n in range(max_periods):
        s = 0.0
        for i in range(cyc):
            t = (n * cyc + i) * DT
            k1 = acc(V, t)
            k2 = acc(V + 0.5 * DT * k1, t + 0.5 * DT)
            k3 = acc(V + 0.5 * DT * k2, t + 0.5 * DT)
            k4 = acc(V + DT * k3, t + DT)
            V += DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            s += V
        means.append(s / cyc)
        if n + 1 >= min_periods and abs(means[-1] - means[-11]) < tol * max(abs(means[-1]), 1e-12):
            break
    return means[-1], len(means)


# ------------------------------------------------------------
# AUSGABE
# ------------------------------------------------------------
def print_text_heatmap(rows):
    phis = sorted({r["phi2_deg"] for r in rows})
    grid = {(r["phi2_deg"], r["phi3_deg"]): r["v_d_mmps"] for r in rows}
    print("\n" + "=" * 80)
    print("   STATIONÄRE DRIFT (gemittelte Bilanz), mm/s")
    print("=" * 80)
    for p3 in sorted(phis, reverse=True):
        line = f"φ3={p3:5.1f}° |"
        for p2 in phis:
            val = grid[(p2, p3)]
            line += "   ·  " if abs(val) < 0.005 else f" {val:+5.2f}"
        print(line)
    vals = np.array([r["v_d_mmps"] for r in rows])
    print("=" * 80)
    print(f"min = {vals.min():.4f} | max = {vals.max():.4f} | mean = {vals.mean():.4f} mm/s | "
          f"negativ: {(vals < 0).sum()}/{len(vals)}")


def main():
    print("═" * 70)
    print(f"PCMMS Fluid-Drift v2 – stationäre Karte {N_GRID}×{N_GRID}, rho = {RHO} kg/m³")
    print("═" * 70)
    t0 = time.time()
    phis = np.linspace(0, 360, N_GRID, endpoint=False)
    rows = []
    for p2 in phis:
        for p3 in phis:
            vd, fa, tau = drift_balance(p2, p3)
            rows.append(dict(phi2_deg=round(float(p2), 3), phi3_deg=round(float(p3), 3),
                             v_d_mps=vd, v_d_mmps=vd * 1e3, F_bar_A_N=fa, tau_s=tau))
    print(f"Karte in {time.time() - t0:.1f} s berechnet.")
    print_text_heatmap(rows)

    vd_tri, fa_tri, tau_tri = drift_balance(120.0, 240.0)
    print(f"\nZusatzpunkt Triphasik (120°, 240°): v_d = {vd_tri * 1e3:+.4f} mm/s, "
          f"F_bar_A = {fa_tri:+.3e} N, tau = {tau_tri:.1f} s  (nicht im {N_GRID}er-Raster)")

    if SAVE_CSV:
        with open(CSV_NAME, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["phi2_deg", "phi3_deg", "v_d_mps", "v_d_mmps", "F_bar_A_N", "tau_s", "rho"])
            for r in rows:
                w.writerow([r["phi2_deg"], r["phi3_deg"], f"{r['v_d_mps']:.6e}", f"{r['v_d_mmps']:.6f}",
                            f"{r['F_bar_A_N']:.6e}", f"{r['tau_s']:.3f}", RHO])
        print(f"CSV geschrieben: {CSV_NAME}")

    if INTEGRATED_CHECK:
        print("\nKontrolle integriertes Modell (Abbruch über Periodenmittel):")
        for p2, p3 in CHECK_POINTS:
            vb, _, tau = drift_balance(p2, p3)
            vi, n = integrate_drift(p2, p3)
            print(f"  ({p2:6.2f}°, {p3:6.2f}°): Bilanz {vb * 1e3:+.4f} | integriert {vi * 1e3:+.4f} mm/s "
                  f"nach {n} Perioden ({n * T_CYC:.0f} s), tau ≈ {tau:.1f} s")


if __name__ == "__main__":
    main()
