# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.2 und 8.
# Zweck: Gegenprobe zur Größe von Regel B am Rand mit direkter Wishart-Ziehung (Monte Carlo) an vier Punkten,
#   darunter ν = 10, ρ = 0,1, t = 10 und ν = 19 isotrop, t = 1,5; dazu „unauffällig“ am Rand.
# Seed: default_rng(2024); N = 10⁶ je Punkt. Laufzeit: gemessen 30 s Wandzeit, 29 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B b_rand.py > b_rand.out
# Herkunft: Gegenprobe des Hauptbearbeiters (gegenprobe_e3b). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
import numpy as np
from scipy import stats
g=np.random.default_rng(2024)
am=0.05/43
def groesse(nu,rho,t,th_deg,N=4_000_000):
    # Sigma=diag(1,rho^2); wahres D am Rand |D|=t*sqrt(lambda_max)=t, Richtung th gegen Hauptachse
    th=np.radians(th_deg); D=t*np.array([np.cos(th),np.sin(th)])
    eps=g.standard_normal((N,2))*np.array([1,rho])
    # Wishart(nu, Sigma)/nu
    Z=g.standard_normal((N,nu,2))*np.array([1,rho])
    S=np.einsum('nki,nkj->nij',Z,Z)/nu
    lam=np.linalg.eigvalsh(S)[:,1]; s=np.sqrt(lam)
    kap=stats.t.isf(am,nu)/stats.norm.isf(am)
    c=kap*s*stats.rice.isf(am, t/(kap*s))
    q=np.hypot(D[0]+eps[:,0],D[1]+eps[:,1])
    a=(q>c).mean(); o1=((q+stats.t.isf(0.05,nu)*s)<=t).mean()
    return a/am, np.sqrt(a*(1-a)/N)/am, o1
for args in ((19,0.1,10,0),(10,0.1,10,0),(19,1.0,1.5,0),(19,0.1,1.5,0)):
    r=groesse(*args, N=1_000_000)
    print(args,'auffaellig/(a/m)=%.3f +- %.3f  unauffaellig=%.4f'%r)
