# Sitzung vom 05.09.2026, aus dem Protokoll übernommen. Gegenüber dem Original ist nur der Pfad der Engine
# angepasst (Zeile mit „Pfad angepasst“) und dieser Kopf ergänzt; siehe LIESMICH.md. Aufruf im Ordner dieser Datei.
import numpy as np, math, sys, time
from scipy.stats import skew
src=open('../../../code/pcmms_v3a_phasen_sweep.py',encoding='utf-8').read().split("if __name__")[0]  # Pfad angepasst: Engine aus code/ (Original: engine.py im Arbeitsordner)
ns={}; exec(compile(src,'engine.py','exec'), ns)
M=ns['M']; G=ns['G']; MG=ns['MG']; K=ns['K']; C=ns['C_DAMP']; DT=ns['DT']; F_HZ=ns['F_HZ']
A=float(open('A_sin.txt').read()); w=2*math.pi*F_HZ
def zdd_sin(t): return -A*w*w*math.sin(w*t)
def Fc(z,zd):
    if z<0:
        f=-K*z-C*zd
        return f if f>0 else 0.0
    return 0.0
def rhs(z,zd,t,tau2,tau3):
    f=Fc(z,zd)
    zdd=-G+f/M-(zdd_sin(t)+zdd_sin(t-tau2)+zdd_sin(t-tau3))/3.0
    return zd,zdd,f
def rk4(z,zd,t,tau2,tau3):
    k1z,k1d,f=rhs(z,zd,t,tau2,tau3)
    k2z,k2d,_=rhs(z+0.5*DT*k1z,zd+0.5*DT*k1d,t+0.5*DT,tau2,tau3)
    k3z,k3d,_=rhs(z+0.5*DT*k2z,zd+0.5*DT*k2d,t+0.5*DT,tau2,tau3)
    k4z,k4d,_=rhs(z+DT*k3z,zd+DT*k3d,t+DT,tau2,tau3)
    return z+DT*(k1z+2*k2z+2*k3z+k4z)/6, zd+DT*(k1d+2*k2d+2*k3d+k4d)/6, f
def point(p2,p3,T_sim=15.0,T_burn=5.0):
    n=int(T_sim/DT); nb=int(T_burn/DT)
    tau2=math.radians(p2)/w; tau3=math.radians(p3)/w
    z,zd=-MG/K,0.0; F=np.empty(n-nb)
    for i in range(n):
        z,zd,f=rk4(z,zd,i*DT,tau2,tau3)
        if i>=nb: F[i-nb]=f
    lam=(F<1e-9).mean()*100; Fmin=F.min(); Fmax=F.max()
    A_=(Fmax-MG)/(MG-Fmin) if MG-Fmin>1e-6 else float('nan')
    R=abs(1+np.exp(1j*math.radians(p2))+np.exp(1j*math.radians(p3)))
    return dict(phi2=p2,phi3=p3,F_mean=F.mean(),F_skew=float(skew(F)),liftoff=lam,F_max=Fmax,F_min=Fmin,asym=A_,R=R)
if __name__=='__main__':
    grid=np.linspace(0,360,7,endpoint=False)  # 7x7, Schrittweite 51.4 Grad
    rows=[]; t0=time.time()
    for p2 in grid:
        for p3 in grid:
            rows.append(point(p2,p3)); print(f'{p2:6.1f} {p3:6.1f}  skew={rows[-1]["F_skew"]:+.3f}  lam={rows[-1]["liftoff"]:5.1f}  R={rows[-1]["R"]:.3f}',flush=True)
    import pandas as pd
    pd.DataFrame(rows).to_csv('sweep_7x7_sinus.csv',index=False)
    print('fertig in', round(time.time()-t0), 's')
