#!/usr/bin/env python3
"""Plausibilitaet (eigene Rechnung, P3/neuheit): Hat ein reines Sinusprofil im linearen,
starren Dauerkontakt ebenfalls eine F_min-Zeltspitze mit Knick am Triphasik-Punkt?
Starre Auflage (H=1): N(t) = M g + sum_j m_j a_j(t - tau_j)  (Praereg-Anhang A2, Z. 147).
Sinus: a_j = -A w^2 sin(w t - phi_j)  ->  N - Mg = -m A w^2 Im(Phi_1 e^{i w t}),
F_min = Mg - m A w^2 |Phi_1|,  Phi_1 = 1 + e^{-i phi2} + e^{-i phi3}.
Parameter V1-aehnlich (P2-Vorschlag V1): Module 3 x 0,1 kg, Hub 8 mm Spitze-Spitze, f = 10 Hz.
Gesamtmasse M = 0,650 kg wie Referenz (nur fuer Mg).
"""
import numpy as np
M, g = 0.650, 9.81
m, hub, f = 0.100, 0.008, 10.0
A, w = hub / 2, 2 * np.pi * f
Fm = m * A * w**2
print(f"Modulkraftamplitude m*A*w^2 = {Fm:.4f} N; Mg = {M*g:.4f} N")
for p2 in [100, 110, 116, 118, 119, 120, 121, 122, 124, 130, 140]:
    phi = np.deg2rad([0.0, p2, 240.0])
    Phi1 = np.exp(-1j * phi).sum()
    print(f"phi2={p2:5.1f}  |Phi1|={abs(Phi1):.4f}  F_min-Mg={-Fm*abs(Phi1):+.4f} N")
# Zeltsekante je Grad nahe 120:
d = 1e-3
s = [Fm * abs(np.exp(-1j*np.deg2rad([0, 120 + d, 240])).sum()) / d,
     Fm * abs(np.exp(-1j*np.deg2rad([0, 120 - d, 240])).sum()) / d]
print(f"Steigung rechts/links am Knick: {s[0]:.4f} / {s[1]:.4f} N/Grad (symmetrisch, starr)")
