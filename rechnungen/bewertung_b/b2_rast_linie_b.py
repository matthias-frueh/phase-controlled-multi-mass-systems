"""P3 bewertung_b, Kandidaten 15/86 (B12): Rastvariante im gedaechtnisfreien Modell A.
Pruefung der Zahlen 0,462 / 0,364 / 0,222 / 0 (Archiv-Vermerk vom 28.09.2026, Quelle außerhalb des Repositorys, §2.4) und
der geschlossenen Form. Hub (Weg 1, Halbsinus) ueber t_h, Rast t_r0, Rueckfuehrung (Weg 1)
ueber t_r = 1 - t_h - t_r0. Gleichrichtung ~ <v|v|> (quadratischer, gedaechtnisfreier Widerstand).
Geschlossen (gleiche Form fuer Hub und Rueckfuehrung): netto/hub = 1 - c_r/c_h * t_h/t_r.
"""
import numpy as np

N = 400_000
PH = (np.arange(N) + 0.5) / N

def form(u, art, rampe=0.1):
    if art == "Halbsinus":
        w = np.sin(np.pi * u)
    else:
        w = np.ones_like(u)
        if art == "Trapez":
            a, b = u < rampe, u > 1 - rampe
            w[a] = 0.5 * (1 - np.cos(np.pi * u[a] / rampe))
            w[b] = 0.5 * (1 - np.cos(np.pi * (1 - u[b]) / rampe))
    return w / w.mean()

def netto(t_h, t_r0, art):
    v = np.zeros(N)
    h = PH < t_h
    v[h] = form(PH[h] / t_h, "Halbsinus") / t_h
    t_r = 1 - t_h - t_r0
    r = PH >= t_h + t_r0
    v[r] = -form((PH[r] - t_h - t_r0) / t_r, art) / t_r
    q = v * np.abs(v)
    return q.mean() / (q[h].sum() / N)   # Netto <v|v|> relativ zum Hubanteil

print("Rast   Halbsinus  Trapez  konstant   geschlossen(Halbsinus)  geschlossen(konstant)")
ch = np.pi ** 2 / 8  # <w^2> fuer Halbsinus mit Mittel 1
for t_r0 in (0.0, 0.1, 0.2, 0.3):
    t_r = 1 - 0.35 - t_r0
    vals = [netto(0.35, t_r0, a) for a in ("Halbsinus", "Trapez", "konstant")]
    print(f"{t_r0:.1f}T  " + "  ".join(f"{x:+.3f}" for x in vals)
          + f"     {1 - 0.35 / t_r:+.3f}                 {1 - (1 / ch) * 0.35 / t_r:+.3f}")
print("Folgerung: im gedaechtnisfreien Modell faellt die Gleichrichtung streng monoton mit der Rast"
      " (analytisch 1 - c*t_h/t_r); ein Optimum bei endlicher Rast ist dort ausgeschlossen.")
