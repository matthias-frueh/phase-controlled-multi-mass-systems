#!/usr/bin/env python3
"""P2 / linie_b / Befund 3 (Ergänzung): v1-Auswertung (Start aus der Ruhe, Mittel über 4–8 s, RK4, DT = 50 µs,
wie pcmms_fluid_drift.py v1) für alle 169 Rasterpunkte bei rho = 1000 und rho = 1,2.
Abgleich mit der archivierten v1-Karte sweep_13x13_drift.csv (Kernpaket 01.09.) und mit der stationären v2-Karte.
Zeigt, dass eine nicht eingeschwungene Fensterauswertung mit rho skaliert (t << tau: V ~ F_bar_A t / M)."""
import os, sys, time
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "quelle_kopie"))
import pcmms_fluid_drift_v2 as fd           # noqa: E402
from b2b_periodische_loesung import rdot_halbraster, NCYC, DT  # noqa: E402

V1CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daten/sweep_13x13_drift_v1.csv')   # v1-Karte, Kopie aus dem Kernpaket 01.09.2026


def fenster(R, c):
    """Start V = 0, 160000 Schritte (8 s); Mittel der Schritt-Endwerte ab Schritt 80000 (wie v1: i >= N_BURN)."""
    V = 0.0; s = 0.0; n = 0
    for per in range(80):
        for i in range(NCYC):
            r0, rh, r1 = R[2 * i], R[2 * i + 1], R[2 * i + 2]
            u = V - r0; k1 = -c * abs(u) * u
            u = V + 0.5 * DT * k1 - rh; k2 = -c * abs(u) * u
            u = V + 0.5 * DT * k2 - rh; k3 = -c * abs(u) * u
            u = V + DT * k3 - r1; k4 = -c * abs(u) * u
            V += DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            if per * NCYC + i >= 80000:
                s += V; n += 1
    return s / n


def main():
    t0 = time.time()
    phis = np.linspace(0, 360, 13, endpoint=False)
    rows = []
    for p2 in phis:
        for p3 in phis:
            R = rdot_halbraster(p2, p3)
            vb = fd.drift_balance(p2, p3)[0]
            w1000 = fenster(R, fd.C2 * 1000.0 / fd.M_TOTAL)
            w12 = fenster(R, fd.C2 * 1.2 / fd.M_TOTAL)
            rows.append((round(p2, 3), round(p3, 3), vb, w1000, w12))
    df = pd.DataFrame(rows, columns=["phi2", "phi3", "v_d_stat", "v1fenster_rho1000", "v1fenster_rho1p2"])
    df.to_csv(os.path.join(HERE, "b3b_v1_fenster_karte.csv"), index=False)
    print(f"Rechenzeit {time.time()-t0:.0f} s")
    if os.path.exists(V1CSV):
        a = pd.read_csv(V1CSV)
        print("Spalten v1-CSV:", list(a.columns), a.shape)
        col = [c for c in a.columns if "drift" in c.lower() and "mps" in c.lower()][0]
        m = df.merge(a, left_on=["phi2", "phi3"], right_on=[a.columns[0], a.columns[1]], how="inner")
        d = (m["v1fenster_rho1000"] - m[col]).abs()
        print(f"Abgleich mit archivierter v1-Karte ({len(m)} Punkte): max |Diff| = {d.max():.3e} m/s; "
              f"v1-CSV min/max = {m[col].min()*1e3:+.6f}/{m[col].max()*1e3:+.6f} mm/s")
    for c in ["v_d_stat", "v1fenster_rho1000", "v1fenster_rho1p2"]:
        print(f"{c:20s}: min {df[c].min()*1e3:+.6f}  max {df[c].max()*1e3:+.6f}  mittel {df[c].mean()*1e3:+.6f} mm/s, "
              f"negativ {(df[c] < 0).sum()}/169")
    q = df["v1fenster_rho1000"] / df["v_d_stat"]
    print(f"Fensterwert/stationär (rho=1000): {q.min()*100:.1f} … {q.max()*100:.1f} %")
    q2 = df["v1fenster_rho1p2"] / df["v_d_stat"]
    print(f"Fensterwert/stationär (rho=1,2): {q2.min()*100:.3f} … {q2.max()*100:.3f} %")
    r = df["v1fenster_rho1000"] / df["v1fenster_rho1p2"]
    print(f"Verhältnis Fensterwert rho=1000 / rho=1,2: {r.min():.0f} … {r.max():.0f} (rho-Verhältnis 833)")
    print("Vorzeichen gleich (Fenster rho=1000 vs. stationär):", bool((np.sign(df.v1fenster_rho1000) == np.sign(df.v_d_stat)).all()))


if __name__ == "__main__":
    main()
