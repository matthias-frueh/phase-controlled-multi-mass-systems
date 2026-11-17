# Sitzung vom 05.09.2026, aus dem Protokoll übernommen. Gegenüber dem Original ist nur der Pfad der Engine
# angepasst (Zeile mit „Pfad angepasst“) und dieser Kopf ergänzt; siehe LIESMICH.md. Aufruf im Ordner dieser Datei.
import numpy as np, math, time, pandas as pd
from scipy.stats import skew
src=open('../../../code/pcmms_v3a_phasen_sweep.py',encoding='utf-8').read().split("if __name__")[0]  # Pfad angepasst: Engine aus code/ (Original: engine.py im Arbeitsordner)
ns={}; exec(compile(src,'engine.py','exec'), ns)
M=ns['M']; G=ns['G']; MG=ns['MG']; DT=ns['DT']; F_HZ=ns['F_HZ']; zdd=ns['total_zdd_egg']
def point(p2,p3,K,C,T_sim=15.0,T_burn=5.0):
    w=2*math.pi*F_HZ; tau2=math.radians(p2)/w; tau3=math.radians(p3)/w
    def Fc(z,zd):
        if z<0:
            f=-K*z-C*zd; return f if f>0 else 0.0
        return 0.0
    def rhs(z,zd,t):
        f=Fc(z,zd); return zd, -G+f/M-zdd(t,tau2,tau3), f
    n=int(T_sim/DT); nb=int(T_burn/DT); z,zd=-MG/K,0.0; F=np.empty(n-nb)
    for i in range(n):
        t=i*DT
        k1z,k1d,f=rhs(z,zd,t); k2z,k2d,_=rhs(z+.5*DT*k1z,zd+.5*DT*k1d,t+.5*DT)
        k3z,k3d,_=rhs(z+.5*DT*k2z,zd+.5*DT*k2d,t+.5*DT); k4z,k4d,_=rhs(z+DT*k3z,zd+DT*k3d,t+DT)
        z+=DT*(k1z+2*k2z+2*k3z+k4z)/6; zd+=DT*(k1d+2*k2d+2*k3d+k4d)/6
        if i>=nb: F[i-nb]=f
    lam=(F<1e-9).mean()*100
    return dict(phi2=p2,phi3=p3,F_mean=F.mean(),F_skew=float(skew(F)),liftoff=lam,F_max=F.max(),F_min=F.min())
def mind(p2,p3):
    a=[p2%360,p3%360,(p3-p2)%360]; return min(min(x,360-x) for x in a)
grid=np.linspace(0,360,7,endpoint=False)
rows=[]; t0=time.time()
zeta0=16/(2*math.sqrt(1e4*M))
for label,K,zeta in [('k',1e3,zeta0),('k',3e3,zeta0),('k',1e4,zeta0),('k',3e4,zeta0),('k',1e5,zeta0),
                     ('z',1e4,0.02),('z',1e4,0.05),('z',1e4,0.20),('z',1e4,0.40)]:
    C=2*zeta*math.sqrt(K*M); fn=math.sqrt(K/M)/(2*math.pi)
    pts=[point(p2,p3,K,C) for p2 in grid for p3 in grid]
    d=pd.DataFrame(pts); d['dmin']=[mind(a,b) for a,b in zip(d.phi2,d.phi3)]
    neg=d[d.F_skew<-1e-3]; paar=d[d.dmin<1e-6]
    rows.append(dict(serie=label,K=K,zeta=round(zeta,3),f_n=round(fn,1),r=round(3*F_HZ/fn,2),
        frei=int((d.liftoff<1e-9).sum()),lam_max=round(d.liftoff.max(),1),
        skew_min=round(d.F_skew.min(),3),skew_max=round(d.F_skew.max(),3),
        n_neg=len(neg),neg_bei_paar=int((neg.dmin<1e-6).sum()),skew_min_paar=round(paar.F_skew.min(),3),
        Nmax_Mg=round(d.F_max.max()/MG,2),Nmin_max=round(d.F_min.max(),3),
        res_ppm_max=round(abs((d.F_mean-MG)/MG).max()*1e6,0)))
    print(rows[-1],flush=True)
    d.to_csv(f'sens_{label}_{K:.0e}_{zeta:.2f}.csv',index=False)
pd.DataFrame(rows).to_csv('sensitivitaet.csv',index=False)
print('fertig', round(time.time()-t0),'s')
