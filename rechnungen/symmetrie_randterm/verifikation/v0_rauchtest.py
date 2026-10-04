import os
import time, numpy as np, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import v_engine as ve
import finesweep as fs
# Profilvergleich gegen Referenz-Beschleunigung
t=np.linspace(0,0.3,30001)
print('max|qdd_mine - qdd_ref| =', np.max(np.abs(ve.prof(t)[2]-fs.z_egg_zdd(t))))
# numerische Ableitung von q und qd
h=1e-7; tt=np.linspace(0.001,0.299,5000)
print('max|dq/dt - qd| =', np.max(np.abs((ve.prof(tt+h)[0]-ve.prof(tt-h)[0])/(2*h)-ve.prof(tt)[1])))
print('max|dqd/dt - qdd| =', np.max(np.abs((ve.prof(tt+h)[1]-ve.prof(tt-h)[1])/(2*h)-ve.prof(tt)[2])))
t1=time.time()
o=ve.run([110,0],[234,208.421],20,form='frame')
print('20 Zyklen 2 Punkte:',time.time()-t1,'s')
w=ve.window(o,10,20)
print({k:w[k] for k in ('N1','NW','gam','lam','Fmin','Fmax','R','Q','E')})
t1=time.time()
o=ve.run([110,0],[234,208.421],20,form='com')
print('com 20 Zyklen:',time.time()-t1,'s')
w=ve.window(o,10,20)
print({k:w[k] for k in ('N1','NW','gam','lam','Fmin','Fmax','R','Q','E')})
