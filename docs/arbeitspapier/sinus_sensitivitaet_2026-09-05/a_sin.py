# Sitzung vom 05.09.2026, aus dem Protokoll übernommen; dort eine direkte Eingabe ohne Dateinamen (Name am
# 16.11.2026 vergeben). Gegenüber dem Original ist nur der Pfad der Engine angepasst (Zeile mit „Pfad angepasst“)
# und dieser Kopf ergänzt; siehe LIESMICH.md. Aufruf im Ordner dieser Datei.
import numpy as np, math
src=open('../../../code/pcmms_v3a_phasen_sweep.py',encoding='utf-8').read().split("if __name__")[0]  # Pfad angepasst: Engine aus code/ (Original: engine.py im Arbeitsordner)
ns={}; exec(compile(src,'engine.py','exec'), ns)
DT=ns['DT']; F_HZ=ns['F_HZ']; T=1/F_HZ
# Egg-Profil: Beschleunigung zweimal integrieren -> Hub
t=np.arange(0,T,DT); a=np.array([ns['z_egg_zdd'](x) for x in t])
v=np.cumsum(a)*DT; v-=v.mean()
z=np.cumsum(v)*DT
hub=z.max()-z.min()
print(f'Egg-Profil: Hub (Spitze-Spitze) = {hub*1e3:.3f} mm, a_max = {abs(a).max():.2f} m/s^2')
A=hub/2; w=2*math.pi*F_HZ
print(f'Sinus mit gleichem Hub: A = {A*1e3:.3f} mm, a_max = {A*w*w:.2f} m/s^2')
print(f'Verhaeltnis a_max Egg/Sinus = {abs(a).max()/(A*w*w):.2f}')
open('A_sin.txt','w').write(str(A))
