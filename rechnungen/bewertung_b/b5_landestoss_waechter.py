"""P3 bewertung_b, neuer Kandidat 'Echtzeit-Liftoff-Waechter' (B09/B06, P2-2).
Grobe Abschaetzung [E]: Spitzenkraft beim Wiederaufsetzen nach Abheben, linearer Kontakt
(Kelvin-Voigt, einseitig) mit Gesamtsteifigkeit K, Daempfung zeta, starre Masse M.
Vergleich mit P2 (AUS-12/13: Hüpfzustand V1 synchron, Stoesse 483-487 N; Schwelle 0,24-0,60 m/s).
Abklingen nach Antriebsstopp: Stosszahl e = exp(-pi*zeta/sqrt(1-zeta^2)) (lineares Modell,
ohne Schwerkraft waehrend des Kontakts), Zahl der Stoesse bis v < 0,05 m/s, Summe der Flugzeiten.
Annahmen [A]: V1-Kandidat K = 1,5e6 N/m, M = 0,65 kg, zeta 0,02/0,05/0,1; Antriebe stehen sofort.
"""
import numpy as np
from scipy.integrate import solve_ivp

M, g = 0.650, 9.81
K = 1.5e6

def impact_peak(v0, zeta):
    C = 2 * zeta * np.sqrt(K * M)
    # Kontakt beginnt bei z = 0 mit Abwaertsgeschwindigkeit v0; Kraft F = max(0, -K z - C zdot)
    def rhs(t, y):
        z, v = y
        F = max(0.0, -K * z - C * v)
        return [v, F / M - g]
    def leave(t, y):
        return y[0]
    leave.terminal, leave.direction = True, 1
    sol = solve_ivp(rhs, (0, 0.05), [0.0, -v0], max_step=2e-6, events=leave, rtol=1e-9, atol=1e-12)
    z, v = sol.y
    F = np.maximum(0.0, -K * z - C * v)
    vout = sol.y_events[0][0][1] if sol.y_events[0].size else float('nan')
    return F.max(), vout / v0

print("Fallhoehe  v0      F_peak(zeta=0,02/0,05/0,10)      v0*sqrt(K*M)")
for h in (0.001, 0.003, 0.012, 0.018):
    v0 = np.sqrt(2 * g * h)
    peaks = [impact_peak(v0, z)[0] for z in (0.02, 0.05, 0.10)]
    print(f"{h*1e3:5.0f} mm  {v0:.3f}   " + " / ".join(f"{p:6.0f} N" for p in peaks)
          + f"      {v0*np.sqrt(K*M):6.0f} N")

for zeta in (0.02, 0.05, 0.10):
    e_num = impact_peak(0.5, zeta)[1]
    e = np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2))
    n = np.log(0.5 / 0.05) / np.log(1 / e)
    tflug = 2 * 0.5 / g * (1 - e ** np.ceil(n)) / (1 - e)
    print(f"zeta={zeta:.2f}: e={e:.3f} (numerisch {e_num:.3f}), Stoesse bis v<0,05 m/s: {np.ceil(n):.0f},"
          f" Summe Flugzeiten ab 0,5 m/s: {tflug:.2f} s")
