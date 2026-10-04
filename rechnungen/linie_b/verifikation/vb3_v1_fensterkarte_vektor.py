#!/usr/bin/env python3
"""
Gegenprüfung LB-07 (v1-Fensterkarte: Werkstattbericht-Spanne -0,104 ... +0,692 mm/s; Skalierung mit rho).

UNABHÄNGIGE IMPLEMENTIERUNG:
  (a) Vektorisiertes RK4 über alle 169 Punkte gleichzeitig (eigene Egg-Kurve, Halbschrittraster),
      v1-Verfahren laut Quelltext pcmms_fluid_drift.py (Bestand): DT = 50 µs, T_SIM = 8 s, Mittel der
      Schritt-Endwerte für i >= 80000 (Z. 35-39, 65-82). rho = 1000 und 1,2. Zusätzlich DT = 25 µs
      (Diskretisierungsempfindlichkeit).
  (b) Für rho = 1,2 halbanalytische Störungsrechnung 1. Ordnung in c = C2 rho / M:
      V(t) ~ c * G(t), G(t) = int_0^t (-v_osc|v_osc|) ds  (gültig für t << tau). Fenstermittel = c * <G>_[4,8).
  Abgleich mit der archivierten v1-CSV (Stand 01.09.2026, Kopie unter ../daten/; alle 10 Kopien der Quelle außerhalb des Repositorys MD5-gleich) und Verhältnis rho=1000/1,2.
"""
import os
import time

import numpy as np
import pandas as pd

V1CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../daten/sweep_13x13_drift_v1.csv')   # v1-Karte, Kopie des archivierten Stands vom 01.09.2026
M_TOT, RATIO, C2 = 0.75, 0.2, 0.5 * 0.8 * 0.03
F, HOLD, V_FAST = 10.0, 0.65, 0.06
T = 1 / F
TF = 1 - HOLD
V_SLOW = V_FAST * TF / HOLD


def egg_vel(ph):
    ph = np.mod(ph, 1.0)
    return np.where(ph < TF, V_FAST * np.sin(np.pi * ph / TF), -V_SLOW * np.sin(np.pi * (ph - TF) / HOLD))


def raster():
    phis = np.linspace(0, 360, 13, endpoint=False)
    P2, P3 = np.meshgrid(phis, phis, indexing="ij")
    return P2.ravel(), P3.ravel()


def rdot_half(p2, p3, dt):
    ncyc = int(round(T / dt))
    th = np.arange(2 * ncyc + 1) * (dt / 2)                     # Halbschritte einer Periode
    ph = th[:, None] / T
    r = (egg_vel(ph) + egg_vel(ph - p2[None, :] / 360) + egg_vel(ph - p3[None, :] / 360)) / 3
    return RATIO * r, ncyc


def fenster(p2, p3, rho, dt=5e-5, t_sim=8.0, t_burn=4.0):
    R, ncyc = rdot_half(p2, p3, dt)
    c = C2 * rho / M_TOT
    nst, nb = int(round(t_sim / dt)), int(round(t_burn / dt))
    V = np.zeros(p2.size)
    s = np.zeros(p2.size)
    for i in range(nst):
        j = i % ncyc
        r0, rh, r1 = R[2 * j], R[2 * j + 1], R[2 * j + 2]
        u = V - r0; k1 = -c * np.abs(u) * u
        u = V + 0.5 * dt * k1 - rh; k2 = -c * np.abs(u) * u
        u = V + 0.5 * dt * k2 - rh; k3 = -c * np.abs(u) * u
        u = V + dt * k3 - r1; k4 = -c * np.abs(u) * u
        V = V + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if i >= nb:
            s += V
    return s / (nst - nb)


def stoerung1(p2, p3, rho, n=4000):
    """c * <G>_[4,8), G = int_0^t g, g = -v_osc|v_osc| = RATIO r |RATIO r| (periodisch)."""
    c = C2 * rho / M_TOT
    th = (np.arange(n) + 0.5) * T / n
    ph = th[:, None] / T
    r = RATIO * (egg_vel(ph) + egg_vel(ph - p2[None, :] / 360) + egg_vel(ph - p3[None, :] / 360)) / 3
    g = r * np.abs(r)                      # v_osc = -r  ->  -v_osc|v_osc| = r|r|
    gbar = g.mean(0)
    Gp = np.cumsum(g - gbar, axis=0) * T / n   # periodischer Anteil (bis auf Konstante)
    # <G>_[4,8) = gbar * 6 s + <Gp> (Fenster = 40 ganze Perioden, Start bei t=0 mit G=0)
    return c * (gbar * 6.0 + Gp.mean(0))


def main():
    p2, p3 = raster()
    t0 = time.time()
    w1000 = fenster(p2, p3, 1000.0)
    w12 = fenster(p2, p3, 1.2)
    t1 = time.time()
    w1000_h = fenster(p2, p3, 1000.0, dt=2.5e-5)
    t2 = time.time()
    s12 = stoerung1(p2, p3, 1.2)
    df = pd.DataFrame(dict(phi2=np.round(p2, 3), phi3=np.round(p3, 3), w1000=w1000, w12=w12, w1000_dt25=w1000_h,
                           stoer1_rho1p2=s12))
    df.to_csv("vb3_v1_fensterkarte_vektor.csv", index=False)
    print("=" * 100)
    print(f"vb3 – v1-Fensterkarte, vektorisiert; Rechenzeit {t1-t0:.1f} s (2 rho) + {t2-t1:.1f} s (DT = 25 µs)")
    print("=" * 100)
    a = pd.read_csv(V1CSV)
    m = df.merge(a, left_on=["phi2", "phi3"], right_on=["phi2_deg", "phi3_deg"])
    d = (m.w1000 - m.drift_mps).abs()
    print(f"Abgleich archivierte v1-CSV ({len(m)} Punkte): max |Diff| = {d.max():.3e} m/s; "
          f"Archiv min/max = {a.drift_mmps.min():+.6f}/{a.drift_mmps.max():+.6f} mm/s")
    print(f"eigene Karte rho=1000 (DT 50 µs): min/max = {w1000.min()*1e3:+.6f}/{w1000.max()*1e3:+.6f} mm/s, "
          f"negativ {(w1000<0).sum()}/169")
    dd = np.abs(w1000_h - w1000)
    print(f"DT = 25 µs gegen 50 µs: max |Diff| = {dd.max():.2e} m/s (rel. zur Spanne {dd.max()/np.ptp(w1000):.1e})")
    print(f"rho = 1,2: min/max = {w12.min()*1e3:+.7f}/{w12.max()*1e3:+.7f} mm/s")
    rel = (w12 - s12) / np.where(np.abs(s12) > 0, s12, 1)
    print(f"  Störungsrechnung 1. Ordnung (rho=1,2) gegen RK4: max rel. Abw. {np.abs(rel).max():.2e}; "
          f"Störung min/max {s12.min()*1e3:+.7f}/{s12.max()*1e3:+.7f} mm/s")
    q = w1000 / w12
    print(f"Verhältnis Fenster rho=1000 / rho=1,2: {q.min():.1f} … {q.max():.1f} (Dichteverhältnis {1000/1.2:.1f})")
    # Kontrolle: lineare Skalierung im Fenster bei kleinem rho
    w012 = fenster(p2, p3, 0.12)
    q2 = w12 / w012
    print(f"Verhältnis Fenster rho=1,2 / rho=0,12: {q2.min():.4f} … {q2.max():.4f} (Dichteverhältnis 10)")


if __name__ == "__main__":
    main()
