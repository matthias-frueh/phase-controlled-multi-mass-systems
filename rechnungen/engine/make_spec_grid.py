"""P2/engine – 19x19-Raster (exakte Phasen i*360/19) mit drei Starts (std, imp, ramp2), je 40 s.
Zweck: Startabhängigkeit der Karte und Mehrfachstarts je Symmetriebahn (6 Mitglieder x 3 Starts =
bis zu 18 verschiedene Anfangsbedingungen derselben physikalischen Konfiguration)."""
import os
import json
import numpy as np
import eng
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
GR = 360.0 / 19
for st in ('std', 'imp', 'ramp2'):
    lanes = []
    for i in range(19):
        for j in range(19):
            a, b = i * GR, j * GR
            if st == 'imp':
                z0, v0 = eng.start_imp(a, b); z0, v0 = float(z0), float(v0)
            else:
                z0, v0 = -eng.MG / eng.K, 0.0
            lanes.append(dict(name=f'g{i}_{j}_{st}', point=f'{i},{j}', i2=i, i3=j, phi2=a, phi3=b, start=st,
                              z0=z0, v0=v0, t0=0.0, Tr=2.0 if st == 'ramp2' else 0.0))
    json.dump(dict(dt=eng.DT, lanes=lanes), open(OUT + f'spec_grid_{st}.json', 'w'))
    print(st, len(lanes))
