"""P3 bewertung_b, Kandidat 37 (B08): unabhaengige Nachrechnung des Median-Versatzes
aus Praereg v2 Anhang A9.1 / Tab. F (med(u) = -0,368, gamma1 = +0,755, Faktor 2,9).
Eigene Implementierung (kein Code aus dem Repo): Egg-Lageprofil aus zwei Halbsinus,
Hold-Anteil TH, C1-Bedingung RBOT = RTOP*TF/TH, starre Auflage, Einzelmodul.
"""
import numpy as np

def egg_acc(th, n=2_000_000):
    tf = 1.0 - th
    p = (np.arange(n) + 0.5) / n
    rtop = 1.0
    rbot = rtop * tf / th
    a = np.where(p < th,
                 -rtop * (np.pi / th) ** 2 * np.sin(np.pi * p / th),
                 rbot * (np.pi / tf) ** 2 * np.sin(np.pi * (p - th) / tf))
    return a - a.mean()

for th in (0.50, 0.65, 0.80):
    x = egg_acc(th)
    s = x.std()
    u = x / s
    med = float(np.median(u))
    g1 = float(np.mean(u ** 3))
    closed = -np.sqrt(2 * (1 - th) / th) * np.sin(np.pi * (1 - 1 / (2 * th)) / 2)
    ratio = med / (-g1 / 6) if abs(g1) > 1e-12 else float('nan')
    print(f"TH={th:.2f}: med(u)={med:+.4f} (geschlossen {closed:+.4f}), gamma1={g1:+.4f}, "
          f"med/(-gamma1/6)={ratio:.2f}, gespiegelt med={float(np.median(-u)):+.4f}")

# Anzeigeversatz relativ zu Mg: Median - Mittel = s_N * med(u); s_N/Mg fuer 0,2 und 0,5 %
med65 = float(np.median(egg_acc(0.65) / egg_acc(0.65).std()))
print("s_N/Mg fuer 0,2 % / 0,5 % Versatz:", round(0.2 / -med65, 2), "/", round(0.5 / -med65, 2), "%")
