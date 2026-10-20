# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 4.2 und 8.
# Zweck: Gegenprobe der Größe von Regel B isotrop bei ν = 19, t = 1,5, bedingt exakt über die Rice-Überlebens-
#   funktion, gemittelt über 4·10⁶ Wishart-Ziehungen.
# Seed: default_rng(99). Laufzeit: gemessen 19 s Wandzeit, 19 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B b_iso.py > b_iso.out
# Herkunft: Gegenprobe des Hauptbearbeiters (gegenprobe_e3b). Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
import numpy as np
from scipy import stats
am=0.05/43
nu,t=19,1.5
kap=stats.t.isf(am,nu)/stats.norm.isf(am)
# isotrop: lambda_max einer Wishart(nu, I)/nu; Groesse bedingt exakt ueber Rice-Ueberlebensfunktion
g=np.random.default_rng(99)
tot=[]
for b in range(8):
    Z=g.standard_normal((500000,nu,2)); S=np.einsum('nki,nkj->nij',Z,Z)/nu
    s=np.sqrt(np.linalg.eigvalsh(S)[:,1])
    c=kap*s*stats.rice.isf(am, t/(kap*s))
    tot.append(stats.rice.sf(c, t))     # |D|=t, sigma=1 isotrop: |D+eps| ~ Rice(t)
p=np.concatenate(tot)
print('isotrop nu=19 t=1.5: Groesse/(a/m) = %.4f +- %.4f'%(p.mean()/am, p.std()/np.sqrt(p.size)/am))
