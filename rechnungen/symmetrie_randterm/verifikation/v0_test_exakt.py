import time, numpy as np
import v_engine as ve, v_exakt as vx
t1=time.time()
b=vx.Bahn(157.3,264.0)
b.integriere(0.0,-ve.MG/ve.K0,0.0,10.0)
print('exakt 10 s:',time.time()-t1,'s, Segmente',len(b.seg))
# Zustand an Periodenbeginnen 9.0..10.0
tc=np.arange(90,100)*0.1
z,v=b.zustand(tc)
print('z_f an Periodenbeginnen',z[-3:],'v_f',v[-3:])
I=b.impuls(9.0,10.0)
q0,qd0,_=ve.pbar(np.array([9.0,10.0-1e-12]),b.tau2,b.tau3)
print('Mittel N 9-10 s exakt',I/1.0,' Mg',ve.MG,' rel',(I/1.0-ve.MG)/ve.MG*1e6,'ppm')
tt=9.0+np.arange(20000)*5e-5
F=b.kraft(tt)
print('lambda',np.mean(F<1e-9)*100,'Fmax',F.max())
o=ve.run([157.3],[264.0],100,form='frame')
w=ve.window(o,90,100)
print('RK4: N1',w['N1'],'lam',w['lam'],'Fmax',w['Fmax'],'Q ppm',w['Q']/ve.MG*1e6)
print('RK4 Zustand Ende', o['xend'], o['vend'])
