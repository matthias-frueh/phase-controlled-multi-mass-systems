import time, numpy as np, vk_model as m, vk_rk4com as rk
p = np.arange(19)*360/19
P2,P3 = np.meshgrid(p,p,indexing='ij')
t=time.time(); r = rk.run(P2.ravel(), P3.ravel(), n_cyc=2); print('361 Punkte, 2 Zyklen', time.time()-t)
t=time.time(); r = rk.run([120,35],[240,116], n_cyc=100); print('2 Punkte 100 Zyklen', time.time()-t)
w = rk.window(r,50,100); print({k: v for k,v in w.items()})
