"""
PCMMS - Dynamisches Modell der Medienkopplung (Konfig B/C/D) - Version 2 (06.09.2026)
=====================================================================================
Basis: pcmms_medienkopplung_modell-1.py (112 Zeilen, v3.4-Erweiterung). Die Originale bleiben
unverändert daneben. Änderungen:

  1. Zwei Kräfte werden getrennt zurückgegeben und benannt:
       F_drag_drift = kd * v_d * |v_d|
           Widerstand, den ein stationär mit v_d bewegter Körper erführe. Das war in v1 die
           Größe "F_eff". Sie ist NICHT die Kraft, die eine Aufhängung (Konfiguration D) misst.
       F_bar_A = -kd * <v_osc |v_osc|>
           Gleichrichtungskraft bei vorgegebener mittelwertfreier Bewegung (Modell A der Notiz);
           unter den Bedingungen (i)-(iii) der Notiz gleich der mittleren Medienkraft im
           Pendelmodell (Modell C): k<x> = F_bar_C ~ F_bar_A.
     Für den Fall S (schiefe Geschwindigkeit) ist F_bar_A/F_drag_drift ~ 2<|v_osc|>/|v_d| ~ 20.
  2. pendulum_deflection() erhält F_bar_A, nicht F_drag_drift. Die v1-Ausgabe "34.7 nm" war
     die Auslenkung aus der falschen Kraft; mit F_bar_A ergeben sich ~680 nm (M = 1 kg, L = 1 m).
  3. Fallbezeichnungen: Z (zweistufige Kraft), S (schiefe Geschwindigkeit), R (richtungs-
     abhängiger Widerstand). Das v1-Etikett "M2" kollidierte mit "Mechanismus 2" der Notiz
     (dynamische Instabilität) und wird nicht mehr verwendet.
  4. Konsolenaussagen entsprechend berichtigt.

Unverändert: die Bilanz  <kd(v_d + v_osc)|v_d + v_osc|> = 0  mit widerstandsfreiem v_osc
(Näherung |drag| << |F_int|; für die Skriptparameter erfüllt) und der Nullbefund für die
zweistufige Kraft (Sägezahn-v, gleichverteilte Geschwindigkeit). Der Nullbefund gilt im
verwendeten Profilmodell mit gemittelter Bilanz; er ist kein allgemeiner Satz über die
vollständige dissipative Dynamik.

Alle Größen gelten innerhalb des Zweiterm-Ansatzes mit stationärem C_D (Notiz §6 offen).
"""
import numpy as np
from scipy.optimize import brentq

RHO_AIR = 1.2  # kg/m^3
G = 9.81


def _drift(v_osc, kd_func):
    """Stationäre Drift aus der gemittelten Bilanz <kd_func(v_d + v_osc)> = 0."""
    def bal(vd):
        v = vd + v_osc
        return np.mean(kd_func(v))
    amp = np.max(np.abs(v_osc)) + 1e-9
    return brentq(bal, -amp, amp, xtol=1e-14)


def _report(v_osc, vd, kd_eff, drag_at_drift):
    return dict(
        v_d=vd,
        F_drag_drift=drag_at_drift,                    # kd*v_d*|v_d|  (v1: "F_eff")
        F_bar_A=-kd_eff * np.mean(v_osc * np.abs(v_osc)),  # Modell A/C
        v_amp=np.max(np.abs(v_osc)),
        mean_abs_v=np.mean(np.abs(v_osc)),
    )


def case_Z_two_level(M=1.0, c_w=1.0, A=0.02, T=0.1, frac_f=0.8, Fa=5.0, Nt=40000):
    """Fall Z: zweistufige Kraft, symmetrischer quadratischer Widerstand."""
    Fb = Fa * frac_f / (1 - frac_f)
    kd = 0.5 * RHO_AIR * c_w * A
    t = np.linspace(0, T, Nt, endpoint=False)
    dt = T / Nt
    Fint = np.where(t < frac_f * T, Fa, -Fb)
    v = np.cumsum(Fint) * dt / M
    v -= v.mean()
    vd = _drift(v, lambda x: kd * x * np.abs(x))
    return _report(v, vd, kd, kd * abs(vd) * vd)


def case_S_skewed_velocity(M=1.0, c_w=1.0, A=0.02, T=0.1, a=5.0, b=3.0, phi=0.25 * np.pi, Nt=40000):
    """Fall S: zwei-harmonische Kraft -> schiefe v(t)."""
    kd = 0.5 * RHO_AIR * c_w * A
    t = np.linspace(0, T, Nt, endpoint=False)
    dt = T / Nt
    w = 2 * np.pi / T
    Fint = a * np.sin(w * t) + b * np.sin(2 * w * t + phi)
    v = np.cumsum(Fint) * dt / M
    v -= v.mean()
    vd = _drift(v, lambda x: kd * x * np.abs(x))
    return _report(v, vd, kd, kd * abs(vd) * vd)


def case_R_directional_drag(M=1.0, A=0.02, T=0.1, frac_f=0.8, Fa=5.0, c_fwd=1.2, c_bwd=0.6, Nt=40000):
    """Fall R: zweistufige Kraft, richtungsabhängiger Widerstand (c_fwd != c_bwd).
    F_bar_A wird mit dem richtungsabhängigen Gesetz gebildet, nicht mit einem Mittelwert von c."""
    Fb = Fa * frac_f / (1 - frac_f)
    t = np.linspace(0, T, Nt, endpoint=False)
    dt = T / Nt
    Fint = np.where(t < frac_f * T, Fa, -Fb)
    v = np.cumsum(Fint) * dt / M
    v -= v.mean()
    kf = 0.5 * RHO_AIR * c_fwd * A
    kb = 0.5 * RHO_AIR * c_bwd * A
    law = lambda x: np.where(x >= 0, kf * x * np.abs(x), kb * x * np.abs(x))
    vd = _drift(v, law)
    keff = 0.5 * RHO_AIR * ((c_fwd + c_bwd) / 2) * A
    rep = dict(v_d=vd, F_drag_drift=float(law(np.array([vd]))[0]),
               F_bar_A=-float(np.mean(law(v))), v_amp=np.max(np.abs(v)), mean_abs_v=np.mean(np.abs(v)))
    rep["keff"] = keff
    return rep


# ----------------------------------------------------------------------
# v3.4-Hilfsfunktionen (aus der 112-Zeilen-Fassung, inhaltlich unverändert)
# ----------------------------------------------------------------------
def two_mass_realization(m1=0.1, m2=0.1, a=5.0, b=3.0, T=0.1):
    """2 Massen bei omega und 2*omega ergeben die zwei-harmonische F_int:
    F_int = -(m1 z1'' + m2 z2''), z1 = A1 sin(wt), z2 = A2 sin(2wt+phi)."""
    w = 2 * np.pi / T
    A1 = a / (m1 * w ** 2)
    A2 = b / (m2 * (2 * w) ** 2)
    return dict(f_Hz=1 / T, A1_cm=A1 * 100, acc1_g=(a / m1) / G, A2_cm=A2 * 100, acc2_g=(b / m2) / G)


def friction_floor(M=1.0, mu=0.001):
    """Coulomb-/Rollreibungsboden F_fric = mu*M*g."""
    return mu * M * G


def pendulum_deflection(F_bar, M=1.0, L=1.0):
    """Statische mittlere Auslenkung einer Pendel-/Schubwaage: <x> = F_bar * L / (M*g).
    F_bar ist die mittlere Medienkraft im Pendelmodell (Modell C), unter den Bedingungen
    (i)-(iii) der Notiz gleich F_bar_A. NICHT F_drag_drift übergeben."""
    return F_bar * L / (M * G)


def _line(label, r):
    return (f"{label:32s} v_d={r['v_d'] * 1e3:8.4f} mm/s  <|v_osc|>={r['mean_abs_v'] * 1e3:6.1f} mm/s  "
            f"F_drag_drift={r['F_drag_drift']:+.2e} N  F_bar_A={r['F_bar_A']:+.2e} N")


if __name__ == "__main__":
    print("MEDIENKOPPLUNG v2 (M=1kg, A=0.02m^2, T=0.1s, rho=1.2)")
    print("-" * 110)
    rZ = case_Z_two_level()
    print(_line("Z zweistufig 80/20, Fa=5N", rZ) + "   (Nullbefund)")
    print(_line("  Kontrolle 50/50", case_Z_two_level(frac_f=0.5)))
    rS = case_S_skewed_velocity(a=5, b=3, phi=0.25 * np.pi)
    print(_line("S schiefe v (b=3, phi=pi/4)", rS))
    print(_line("  Kontrolle phi=pi/2", case_S_skewed_velocity(a=5, b=3, phi=0.5 * np.pi)))
    rR = case_R_directional_drag(Fa=10, c_fwd=1.5, c_bwd=0.5)
    print(_line("R richtungsabh. (1.5/0.5, 10N)", rR))
    print(_line("  Kontrolle c gleich", case_R_directional_drag(c_fwd=1.0, c_bwd=1.0)))
    print("-" * 110)
    print(f"Fall S: F_bar_A / F_drag_drift = {rS['F_bar_A'] / rS['F_drag_drift']:.1f} "
          f"(~ 2<|v_osc|>/|v_d| = {2 * rS['mean_abs_v'] / abs(rS['v_d']):.1f})")
    print("Konfiguration D misst k<x> = F_bar_C ~ F_bar_A (Bedingungen (i)-(iii) der Notiz), nicht F_drag_drift.")

    print("\n--- Mehrmassen-Realisierung (Fall S) ---")
    r = two_mass_realization()
    print(f"  Masse1@{r['f_Hz']:.0f}Hz: A1={r['A1_cm']:.2f} cm, a={r['acc1_g']:.1f} g")
    print(f"  Masse2@{2 * r['f_Hz']:.0f}Hz: A2={r['A2_cm']:.2f} cm, a={r['acc2_g']:.1f} g (Phase steuert Schiefe)")

    print("\n--- Reibungsboden vs. freie Drift ---")
    for mu, nm in [(0.001, "Praez.-Rollen"), (1e-5, "Luftlager"), (1e-6, "Luftlager top")]:
        print(f"  {nm:14s} mu={mu:.0e}: F_fric={friction_floor(mu=mu):.1e} N")
    print("  Freie Drift in Luft zusätzlich durch tau ~ Stunden unpraktikabel; Aufhängung (Konfig. D).")

    print("\n--- Pendelauslenkung (L=1 m, M=1 kg), bedingte Modellabschätzung ---")
    print(f"  Fall S: aus F_bar_A {pendulum_deflection(rS['F_bar_A']) * 1e9:.0f} nm   "
          f"(v1 aus F_drag_drift: {pendulum_deflection(rS['F_drag_drift']) * 1e9:.1f} nm)")
    print(f"  Fall R: aus F_bar_A {pendulum_deflection(rR['F_bar_A']) * 1e6:.2f} um   "
          f"(v1 aus F_drag_drift: {pendulum_deflection(rR['F_drag_drift']) * 1e6:.2f} um)")
    print("  Gültig nur innerhalb des Zweiterm-Ansatzes mit stationärem C_D (Notiz §6 offen).")
