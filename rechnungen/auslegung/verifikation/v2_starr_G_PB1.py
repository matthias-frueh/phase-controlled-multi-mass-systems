"""
v2_starr_G_PB1.py – Gegenprüfung AUS-03, AUS-07 (starre Grenzwerte), AUS-08 (ε-Fenster, Hubfenster, K-Grenzen),
AUS-09 (Zellmodell A2.5). Starr: N(t) = Mg + Σ m_j a_j(t) direkt im Zeitbereich ausgewertet (keine Fourierreihe).
Harmonische N_k über Trapezquadratur auf 400 000 Stützstellen je Periode.
Ausgabe: v2_starr_G_PB1_ausgabe.txt
"""
import numpy as np
from scipy import stats
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
f, hub = 10.0, vk.HUB_REF
eps1 = vk.eps_of(1.0, hub, f)
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


def Nrigid(ph, w, mu, n):
    s = vk.System(ph, w, mu, hub, f, None, 0.0)
    t = np.arange(n) / (n * f)
    return t, MG + s.Q(t)


p('=== Starre Grenzwerte G = (Mg − F_min)/(Mg·ε), direkt im Zeitbereich (μ = 1, Referenzhub, 10 Hz) ===')
p(f'ε(μ=1) = {eps1:.5f}; a_h·TH/TF (Rückholspitze) / a_h = {TH_TF if (TH_TF:=vk.TH/vk.TF) else 0:.4f}')
for name, ph, w in [('Einzelmodul', (0, 0, 0), (1, 0, 0)), ('Paar Δ=0', (0, 0, 0), (1, 1, 0)),
                    ('synchron', (0, 0, 0), (1, 1, 1)), ('(0°,180°)', (0, 0, 180), (1, 1, 1))] + \
                   [(f'Pilot {a:g}/{b:g}', (0, a, b), (1, 1, 1)) for a, b in vk.PILOTS]:
    vals = []
    for n in (2000, 400000):
        _, N = Nrigid(ph, w, 1.0, n)
        vals.append(((MG - N.min()) / (MG * eps1), (N.max() - MG) / (MG * eps1)))
    p(f'  {name:<16} G = {vals[0][0]:.5f} (2000/Per.)  {vals[1][0]:.5f} (400 000/Per.);  Ĝ = {vals[1][1]:.4f}')
# Paare über Δ
Gp = []
for d in np.arange(0, 360, 1.0):
    _, N = Nrigid((0, d, 0), (1, 1, 0), 1.0, 20000)
    Gp.append((MG - N.min()) / (MG * eps1))
p(f'  Paare Δ = 0…359° (1°): max G = {max(Gp):.5f} bei Δ = {np.argmax(Gp):.0f}°')
# Schnitt
Fsec, Fsec_f = [], []
for a in vk.SECTION:
    Fsec.append(Nrigid((0, a, 240), (1, 1, 1), 1.0, 2000)[1].min())
    Fsec_f.append(Nrigid((0, a, 240), (1, 1, 1), 1.0, 400000)[1].min())
Fsec, Fsec_f = np.array(Fsec), np.array(Fsec_f)
Gs = (MG - Fsec) / (MG * eps1)
dG = (Fsec.max() - Fsec.min()) / (MG * eps1)
dG_f = (Fsec_f.max() - Fsec_f.min()) / (MG * eps1)
p(f'  Schnitt: max G = {Gs.max():.5f} (bei {vk.SECTION[Gs.argmax()]:.0f}°), Spitze bei {vk.SECTION[Fsec.argmax()]:.0f}°, '
  f'ΔG_Zelt = {dG:.5f} (2000/Per.), {dG_f:.5f} (400 000/Per.)')
p(f'  2°-Sekanten je Mg·ε: {(Fsec[10]-Fsec[9])/2/(MG*eps1):.6f} / {(Fsec[10]-Fsec[11])/2/(MG*eps1):.6f} 1/°')
# Harmonische D_k
n = 400000
t = np.arange(n) / (n * f)
th = 2 * np.pi * np.arange(n) / n
D = np.zeros(3)
for a in vk.SECTION:
    _, N = Nrigid((0, a, 240), (1, 1, 1), 1.0, n)
    for k in (1, 2, 3):
        Nk = 2.0 / n * np.sum(N * np.exp(-1j * k * th))
        D[k - 1] = max(D[k - 1], abs(Nk))
p(f'  D_k = max_Schnitt |N_k| / (Mg·ε): {D[0]/(MG*eps1):.6f} / {D[1]/(MG*eps1):.6f} / {D[2]/(MG*eps1):.6f}; '
  f'D_2/ΔF_Zelt = {D[1]/(MG*eps1)/dG:.4f}')

p('\n=== AUS-03: PB1 im A4-Beispiel (starr, μ = 0,4) ===')
eA4 = vk.eps_of(0.4, hub, f)
F120 = MG - MG * eA4 * Gs[10]
F100 = MG - MG * eA4 * Gs[0]
dF = MG * eA4 * dG
c_inf = stats.norm.ppf(1 - 0.05 / 294)
c_19 = stats.t.ppf(1 - 0.05 / 294, 19)
p(f'ε_A4 = {eA4:.5f}; F_min(120°) = {F120:.4f} N; F_min(100°) = {F100:.4f} N; ΔF_Zelt = {dF:.4f} N; Δ = 0,25·ΔF = {0.25*dF:.4f} N')
p(f'c(ν→∞) = {c_inf:.4f}, c(19) = {c_19:.4f}; u_c ≤ {0.25*dF/c_inf:.4f} N bzw. {0.25*dF/c_19:.4f} N '
  f'({100*0.25*dF/c_19/MG:.3f} % Mg)')
D2 = D[1] / (MG * eps1) * MG * eA4
p(f'N₂: D₂ = {D2:.4f} N → u_c ≤ {0.25*D2/c_inf:.4f} N (ν→∞) bzw. {0.25*D2/c_19:.4f} N (ν=19); '
  f'Verhältnis zu F_min-Anforderung {D2/dF:.3f}')
p(f'2°-Sekante A4: {(Fsec[10]-Fsec[9])/2/(MG*eps1)*MG*eA4:.4f} N/°')

p('\n=== AUS-08: ε-Fenster und Hubfenster (starr) ===')
eps_sig = 0.4693 / (MG * dG)
p(f'ε_sig = 0,4693/(Mg·ΔG) = {eps_sig:.4f} (= ε_A4 = {eA4:.4f}: Kriterium ist "Signal mindestens wie A4")')
p(f'ε_max synchron (25 %): 0,75/G_syn = 0,750; PFLICHT: 0,75/max(G_Schnitt, G_Pilot, G_Einzel) = '
  f'{0.75/max(Gs.max(), 0.40479, 1/3):.3f}')
for mu, lab in [(0.3 / 0.65, '3×100 g'), (0.15 / 0.65, '3×50 g'), (0.45 / 0.65, '3×150 g')]:
    h_lo = eps_sig * G * vk.TH / (mu * np.pi ** 2 * f ** 2)
    h_hi = 0.75 * G * vk.TH / (mu * np.pi ** 2 * f ** 2)
    e_ref = vk.eps_of(mu, hub, f)
    p(f'  {lab} (μ = {mu:.4f}), 10 Hz: Hub ∈ [{h_lo*1e3:.2f}; {h_hi*1e3:.2f}] mm; bei Referenzhub ε = {e_ref:.3f}, '
      f'ΔF_Zelt = {MG*e_ref*dG:.3f} N, synchrone Reserve {100*(1-e_ref):.1f} %')
p(f'Bedingung (ii) 3f ≤ f_n/2 ⇔ K ≥ M·(12πf)² = {M*(12*np.pi)**2:.1f}·f² N/m; ρ ≤ 0,05 ⇔ K ≥ {M*(40*np.pi)**2:.0f}·f² N/m '
  f'(10 Hz: {M*(40*np.pi*10)**2:.3e} N/m)')
p(f'Index-Szenario: μ = 1 bei M = 1,95 kg (3×0,65 kg), 2,2 Hz, Referenzhub: ε = {vk.eps_of(1.0, hub, 2.2):.4f}, '
  f'ΔF_Zelt = {1.95*G*vk.eps_of(1.0, hub, 2.2)*dG:.3f} N')

p('\n=== AUS-09: Zellmodell A2.5 (jedes Modul über einer Zelle, starr) ===')
mu = 0.4615
e = vk.eps_of(mu, 8e-3, 10.0)
worst = []
for name, ph, w in [('Einzelmodul', (0, 0, 0), (1, 0, 0)), ('synchron', (0, 0, 0), (1, 1, 1)),
                    ('Triphasik', (0, 120, 240), (1, 1, 1)), ('(0,180)', (0, 0, 180), (1, 1, 1))]:
    s = vk.System(ph, w, mu, 8e-3, 10.0, None, 0.0)
    t = np.arange(20000) / (20000 * 10.0)
    cells = [MG / 3 + s.m[j] * vk.acc(t - s.tau[j], 8e-3, 10.0) for j in range(3)]
    cmin = min(c.min() for c in cells) / (MG / 3)
    worst.append(cmin)
    p(f'  V1-Masse/Hub, {name:<12}: kleinste Zellkraft / statische Zelllast = {cmin:.4f} (1 − ε = {1-e:.4f})')
open('v2_starr_G_PB1_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
