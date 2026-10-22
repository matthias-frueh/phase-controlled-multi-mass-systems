#!/usr/bin/env python3
"""
PCMMS – Reproduktionsskript zur Skriptprüfung Linie B (06.09.2026)

Prüft gegen die Notiz PCMMS_Notiz_Richtung_Medienkopplung_2026-09-06_v5.md:
  (1) Konvergenz des Referenzpunkts (phi2, phi3) = (0, 0) in pcmms_fluid_drift.py
      (Periodenmittel von Vcm über 60 s statt Mittel 4–8 s)
  (2) Dichtevergleich rho = 1000 gegen rho = 100 (Modell B, c1 = 0)
  (3) gemittelte Bilanz <(vd + v_osc)|vd + v_osc|> = 0 gegen das integrierte Modell
  (4) Definition des "effektiven Schubs" in pcmms_medienkopplung_modell.py
      (kd*vd^2) gegen F_bar_A = -kd*<v_osc|v_osc|> der Notiz

Benötigt die Originalskripte im selben Verzeichnis:
  pcmms_fluid_drift.py, pcmms_medienkopplung_modell.py
Die Originalskripte werden nicht verändert; ihre Funktionen werden importiert.
Laufzeit ca. 35 s (reines Python, RK4 mit DT = 5e-5 wie im Original).
"""
import math, time, importlib.util
import numpy as np
from scipy.optimize import brentq


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fd = load("pcmms_fluid_drift.py", "fd")
mk = load("pcmms_medienkopplung_modell.py", "mk")


def cycle_means(rho, T_SIM, phi2=0.0, phi3=0.0):
    """Gleiche Numerik wie simulate_drift (RK4, v_rel = Vcm - RATIO*r_dot),
    aber rho als Parameter und Ausgabe der Periodenmittel von Vcm."""
    p2, p3 = math.radians(phi2), math.radians(phi3)
    tau2, tau3 = p2 / (2 * math.pi * fd.F_HZ), p3 / (2 * math.pi * fd.F_HZ)

    def r_dot(t):
        return (fd.egg_vel(t) + fd.egg_vel(t - tau2) + fd.egg_vel(t - tau3)) / fd.N_ARMS

    c, M, R, DT = 0.5 * rho * fd.CD * fd.AREA, fd.M_TOTAL, fd.RATIO, fd.DT

    def a(Vx, tx):
        vr = Vx - R * r_dot(tx)
        return -(c / M) * abs(vr) * vr

    V, cyc, acc, cm = 0.0, int(round(fd.T_CYC / DT)), [], []
    for i in range(int(T_SIM / DT)):
        t = i * DT
        k1 = a(V, t)
        k2 = a(V + 0.5 * DT * k1, t + 0.5 * DT)
        k3 = a(V + 0.5 * DT * k2, t + 0.5 * DT)
        k4 = a(V + DT * k3, t + DT)
        V += DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        acc.append(V)
        if len(acc) == cyc:
            cm.append(np.mean(acc))
            acc = []
    return np.array(cm)


if __name__ == "__main__":
    t0 = time.time()
    print("(1) Konvergenz Referenzpunkt (0,0), rho = 1000 (Skriptparameter)")
    cm = cycle_means(1000.0, 60.0)
    for s in (2, 4, 8, 16, 32, 60):
        print(f"    Periodenmittel bei t = {s:>2} s: {cm[s*10-1]*1e3:.4f} mm/s")
    print(f"    Mittel 4–8 s (wie CSV-Fenster): {cm[40:80].mean()*1e3:.4f} mm/s   (CSV: 0.691635)")
    print(f"    Mittel 40–60 s:                 {cm[400:600].mean()*1e3:.4f} mm/s")

    print("(3) gemittelte Bilanz, Modell B, c1 = 0, v_osc = -RATIO*r_dot")
    t = np.arange(0, fd.T_CYC, fd.DT)
    vosc = -fd.RATIO * np.array([fd.egg_vel(x) for x in t])
    vd = brentq(lambda v: np.mean((v + vosc) * np.abs(v + vosc)), -0.1, 0.1, xtol=1e-14)
    print(f"    v_d(Bilanz) = {vd*1e3:.4f} mm/s")
    for rho in (1000.0, 100.0, 1.2):
        tau = fd.M_TOTAL / (2 * 0.5 * rho * fd.CD * fd.AREA * np.mean(np.abs(vosc)))
        print(f"    tau-Schaetzung rho = {rho:>6}: {tau:.1f} s")

    print("(2) Dichtevergleich rho = 100, T_SIM = 400 s")
    cm100 = cycle_means(100.0, 400.0)
    print(f"    Periodenmittel bei 100/200/300/400 s: "
          f"{cm100[999]*1e3:.4f} / {cm100[1999]*1e3:.4f} / {cm100[2999]*1e3:.4f} / {cm100[-1]*1e3:.4f} mm/s")
    print(f"    Mittel 300–400 s: {cm100[3000:].mean()*1e3:.4f} mm/s")

    print("(4) Definition 'effektiver Schub' im Medienkopplungsmodell, Fall M1 (Skriptparameter)")
    M, c_w, A, T, a_, b_, phi, Nt = 1.0, 1.0, 0.02, 0.1, 5.0, 3.0, 0.25 * np.pi, 40000
    kd = 0.5 * mk.RHO_AIR * c_w * A
    tt = np.linspace(0, T, Nt, endpoint=False); dt = T / Nt; w = 2 * np.pi / T
    Fint = a_ * np.sin(w * tt) + b_ * np.sin(2 * w * tt + phi)
    v = np.cumsum(Fint) * dt / M; v -= v.mean()
    vd1 = mk._drift(v, lambda x: kd * x * np.abs(x), dt)
    F_script = kd * abs(vd1) * vd1          # Skript: Widerstand bei Driftgeschwindigkeit
    F_A = -kd * np.mean(v * np.abs(v))       # Notiz: Gleichrichtungskraft bei vorgegebener Bewegung
    print(f"    v_d = {vd1*1e3:.3f} mm/s, <|v_osc|> = {np.mean(np.abs(v))*1e3:.1f} mm/s")
    print(f"    F_eff (Skript, kd*vd^2)     = {F_script:.3e} N")
    print(f"    F_bar_A (Notiz, -kd<v|v|>)  = {F_A:.3e} N")
    print(f"    Verhaeltnis                  = {F_A/F_script:.1f}  (~ 2<|v_osc|>/|v_d| = {2*np.mean(np.abs(v))/abs(vd1):.1f})")
    print(f"    Pendelauslenkung L = 1 m, M = 1 kg: Skript-Def {F_script/9.81*1e9:.1f} nm | F_bar_A {F_A/9.81*1e9:.0f} nm")
    print(f"Laufzeit {time.time()-t0:.0f} s")
