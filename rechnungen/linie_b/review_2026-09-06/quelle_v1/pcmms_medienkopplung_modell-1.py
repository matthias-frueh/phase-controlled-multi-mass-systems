"""
PCMMS - Dynamisches Modell der Medienkopplung (Konfig B/C)  [kanonisch]
=======================================================================
Starre, frei bewegliche Huelle (Masse M). Innere, mittelwertfreie
(impulserhaltende) Kraft F_int(t). Quadratischer Luftwiderstand:

    M * v'(t) = F_int(t) - 0.5 * rho * c_w * A * v|v|

Eingeschwungener Drift v_drift ueber die Bilanzbedingung (ueber eine
Periode: <F_int>=0 und <M v'>=0  =>  <drag>=0), mit v(t)=v_drift+v_osc(t)
und widerstandsfreier Schwingung v_osc (da |drag| << |F_int|).

ZENTRALE BEFUNDE
----------------
1) Linearer Widerstand  -> Drift = 0 (lineares System, mittelwertfreie Anregung).
2) Quadrat. Widerstand + zweistufige Kraft -> Dreieck-v -> GLEICHVERTEILTE,
   symmetrische Geschwindigkeit -> Drift = 0. Bloss zeitliche Asymmetrie reicht NICHT.
3) Drift entsteht nur bei  (M1) schiefer Geschwindigkeit  ODER
   (M2) richtungsabhaengigem Widerstand (c_w,fwd != c_w,bwd).
4) Realistische Magnituden: v_drift ~ mm/s..cm/s, effektiver Schub ~1e-7..1e-4 N
   -> UNTER der Kraft-Detektionsschwelle (~1e-3 N). In Luft ist die richtige
   Observable die DRIFT-KINEMATIK, nicht die Kontaktkraft.
"""
import numpy as np
from scipy.optimize import brentq

RHO_AIR = 1.2  # kg/m^3

def _drift(v_osc, kd_func, dt):
    def bal(vd):
        v = vd + v_osc
        return np.mean(kd_func(v))
    amp = np.max(np.abs(v_osc)) + 1e-9
    return brentq(bal, -amp, amp, xtol=1e-14)

def two_level(M=1.0, c_w=1.0, A=0.02, T=0.1, frac_f=0.8, Fa=5.0, Nt=40000):
    """Zweistufige Kraft, symmetrischer quadrat. Widerstand."""
    Fb = Fa*frac_f/(1-frac_f); kd = 0.5*RHO_AIR*c_w*A
    t = np.linspace(0,T,Nt,endpoint=False); dt=T/Nt
    Fint = np.where(t<frac_f*T, Fa, -Fb)
    v = np.cumsum(Fint)*dt/M; v -= v.mean()
    vd = _drift(v, lambda x: kd*x*np.abs(x), dt)
    return vd, kd*abs(vd)*vd, np.max(np.abs(v))

def skewed_velocity(M=1.0, c_w=1.0, A=0.02, T=0.1, a=5.0, b=3.0, phi=0.25*np.pi, Nt=40000):
    """M1: zwei-harmonische Kraft -> schiefe v(t)."""
    kd=0.5*RHO_AIR*c_w*A; t=np.linspace(0,T,Nt,endpoint=False); dt=T/Nt; w=2*np.pi/T
    Fint = a*np.sin(w*t)+b*np.sin(2*w*t+phi)
    v=np.cumsum(Fint)*dt/M; v-=v.mean()
    vd=_drift(v, lambda x: kd*x*np.abs(x), dt)
    return vd, kd*abs(vd)*vd, np.max(np.abs(v))

def directional_drag(M=1.0, A=0.02, T=0.1, frac_f=0.8, Fa=5.0, c_fwd=1.2, c_bwd=0.6, Nt=40000):
    """M2: zweistufige Kraft, richtungsabhaengiger Widerstand."""
    Fb=Fa*frac_f/(1-frac_f); t=np.linspace(0,T,Nt,endpoint=False); dt=T/Nt
    Fint=np.where(t<frac_f*T,Fa,-Fb); v=np.cumsum(Fint)*dt/M; v-=v.mean()
    kf=0.5*RHO_AIR*c_fwd*A; kb=0.5*RHO_AIR*c_bwd*A
    vd=_drift(v, lambda x: np.where(x>=0,kf*x*np.abs(x),kb*x*np.abs(x)), dt)
    keff=0.5*RHO_AIR*((c_fwd+c_bwd)/2)*A
    return vd, keff*abs(vd)*vd, np.max(np.abs(v))

if __name__=="__main__":
    print("KANONISCHE ERGEBNISSE (M=1kg, A=0.02m^2, T=0.1s)")
    print("-"*60)
    vd,Fe,va = two_level()
    print(f"Zweistufig 80/20, Fa=5N : v_drift={vd*1e3:8.4f} mm/s  F_eff={Fe:.2e} N   (Null-Befund)")
    vd,Fe,va = two_level(frac_f=0.5)
    print(f"  Kontrolle 50/50       : v_drift={vd*1e6:8.4f} um/s  (erwartet 0)")
    vd,Fe,va = skewed_velocity(a=5,b=3,phi=0.25*np.pi)
    print(f"M1 schiefe v (b=3,phi=pi/4): v_drift={vd*1e3:8.4f} mm/s  F_eff={Fe:.2e} N")
    vd,Fe,va = skewed_velocity(a=5,b=3,phi=0.5*np.pi)
    print(f"  Kontrolle phi=pi/2     : v_drift={vd*1e6:8.4f} um/s  (erwartet 0)")
    vd,Fe,va = directional_drag(Fa=10,c_fwd=1.5,c_bwd=0.5)
    print(f"M2 richtungsabh. (1.5/0.5,10N): v_drift={vd*1e3:7.3f} mm/s  F_eff={Fe:.2e} N")
    vd,Fe,va = directional_drag(c_fwd=1.0,c_bwd=1.0)
    print(f"  Kontrolle c gleich     : v_drift={vd*1e6:8.4f} um/s  (erwartet 0)")
    print("-"*60)
    print("Fazit: Schub ~1e-7..1e-4 N << 1e-3 N Kraftschwelle.")
    print("       -> In Luft Drift-Kinematik (mm/s) messen, nicht Kraft.")


# ======================================================================
# ERWEITERUNG v3.4: Mehrmassen-Realisierung, Reibung, Schub-Pendel
# ======================================================================
def two_mass_realization(m1=0.1, m2=0.1, a=5.0, b=3.0, T=0.1):
    """Zeigt: 2 Massen bei omega und 2*omega ergeben die 2-harmon. F_int.
    F_int = -(m1 z1'' + m2 z2''), z1=A1 sin(wt), z2=A2 sin(2wt+phi)
         => m1 A1 w^2 sin(wt) + m2 A2 4w^2 sin(2wt+phi)  == a sin + b sin2."""
    g=9.81; w=2*np.pi/T
    A1=a/(m1*w**2); A2=b/(m2*(2*w)**2)
    return dict(f_Hz=1/T, A1_cm=A1*100, acc1_g=(a/m1)/g,
                A2_cm=A2*100, acc2_g=(b/m2)/g)

def friction_floor(M=1.0, mu=0.001):
    """Coulomb-/Rollreibungsboden F_fric = mu*M*g."""
    return mu*M*9.81

def pendulum_deflection(F_eff, M=1.0, L=1.0):
    """Statische Auslenkung einer Pendel-/Schubwaage: x = F*L/(M*g)."""
    return F_eff*L/(M*9.81)

if __name__=="__main__":
    print("\n--- v3.4: Mehrmassen-Realisierung (M1-Fall) ---")
    r=two_mass_realization()
    print(f"  Masse1@{r['f_Hz']:.0f}Hz: A1={r['A1_cm']:.2f} cm, a={r['acc1_g']:.1f} g")
    print(f"  Masse2@{2*r['f_Hz']:.0f}Hz: A2={r['A2_cm']:.2f} cm, a={r['acc2_g']:.1f} g (Phase steuert Schiefe)")
    print("\n--- v3.4: Reibungsboden vs. Schub ---")
    for mu,nm in [(0.001,"Praez.-Rollen"),(1e-5,"Luftlager"),(1e-6,"Luftlager top")]:
        print(f"  {nm:14s} mu={mu:.0e}: F_fric={friction_floor(mu=mu):.1e} N")
    print("  Schub M1=3.4e-7 N, M2=6.3e-5 N -> freie Drift toter; Aufhaengung noetig.")
    print("\n--- v3.4: Schub-Pendel-Auslenkung (L=1 m) ---")
    print(f"  M1: {pendulum_deflection(3.4e-7)*1e9:.1f} nm   M2: {pendulum_deflection(6.3e-5)*1e6:.2f} um")
