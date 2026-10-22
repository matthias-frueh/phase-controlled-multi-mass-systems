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
