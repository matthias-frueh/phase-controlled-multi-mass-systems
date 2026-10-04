#!/usr/bin/env python3
"""P2 / linie_b / Befund 1 (Ergänzung): KC, beta, delta/a für die Fälle S und R des Medienkopplungsmodells v2
(unveränderte Kopie in quelle_kopie/), Luft rho = 1,2, mu = 1,8e-5; D = sqrt(4A/pi) mit A = 0,02 m^2."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "quelle_kopie"))
import pcmms_medienkopplung_modell_v2 as mk  # noqa: E402
nu, T, A = 1.8e-5 / 1.2, 0.1, 0.02
D = np.sqrt(4 * A / np.pi)
w = 2 * np.pi / T
delta = np.sqrt(2 * nu / w)
for name, r in [("S", mk.case_S_skewed_velocity()), ("R", mk.case_R_directional_drag(Fa=10, c_fwd=1.5, c_bwd=0.5))]:
    U = r["v_amp"]
    # Auslenkung aus v (Profil wie im Modell rekonstruiert)
    Nt = 40000
    t = np.linspace(0, T, Nt, endpoint=False); dt = T / Nt
    if name == "S":
        Fint = 5 * np.sin(w * t) + 3 * np.sin(2 * w * t + 0.25 * np.pi)
    else:
        Fint = np.where(t < 0.8 * T, 10.0, -10.0 * 0.8 / 0.2)
    v = np.cumsum(Fint) * dt / 1.0; v -= v.mean()
    x = np.cumsum(v) * dt; a = 0.5 * (x.max() - x.min())
    print(f"Fall {name}: U_max = {U*1e3:.1f} mm/s (Kontrolle {np.abs(v).max()*1e3:.1f}), a = {a*1e3:.3f} mm, D = {D:.4f} m, "
          f"KC_U = {U*T/D:.4f}, KC_a = {2*np.pi*a/D:.4f}, Re = {U*D/nu:.0f}, beta = {D**2/(nu*T):.3e}, "
          f"delta = {delta*1e3:.3f} mm, delta/a = {delta/a:.3f}")
