"""
v2_linear_zellkraefte.py – Gegenprüfung KM-06 (Zellkräfte/Summe/Momente), KM-08 (Zellreserve je Zelle),
KM-04 (Drehfeld-These) und KM-09 (Leckage), linear (Dauerkontakt, bilateral).

Unabhängiger Weg (vf_modell): Zellkoordinaten mit Formfunktionen, analytische Egg-Koeffizienten (k ≤ 400),
quasistatisch direkt im Zeitbereich (20000 Stützstellen je Periode, ohne Fourier).
Konfigurationen wie die Prüfgruppe (Präreg v2 §5.3/§5.4): T = (0,120,240), Z = (0,110,240),
Schnitt φ₂ = 100…140° (2°) bei φ₃ = 240°, Piloten (110,250), (130,230), (110,252), Einzelmodul, Paare,
synchron, (0,0,180).  Geometrien [Annahme der Gruppe, übernommen]: R_c = 100 mm; G0 Module über Zellen,
G60 um 60° gedreht auf R_c, G0h/G60h auf R_c/2, Zc alle im Zentrum; Rahmen ρ_f = R_c/2.
"""
import numpy as np
from vf_modell import (Geom, zell_koeff, synth, starr_zeit, momente, c_egg, a_egg, MG3, K_REF, C_REF,
                       K_STEIF, C_STEIF, M_TOT, GRAV)

R = 0.10
GEO = {'G0': dict(R_m=R, psi0=0.0), 'G60': dict(R_m=R, psi0=60.0), 'G0h': dict(R_m=R / 2, psi0=0.0),
       'G60h': dict(R_m=R / 2, psi0=60.0), 'Zc': dict(R_m=1e-12, psi0=0.0)}
NT = 8000


def zellkraefte(geo, phi, fall, f=10.0, hub=(1, 1, 1), n=NT):
    """Zeitreihen F (3 × n) über eine Periode; fall = 'STARR' | 'REF' | 'STEIF'."""
    if fall == 'STARR':
        F = starr_zeit(geo, phi, f=f, hub=hub, n=n)
        Fk = zell_koeff(geo, phi, None, None, f=f, hub=hub, kmax=12)
    else:
        K, C = (K_REF, C_REF) if fall == 'REF' else (K_STEIF, C_STEIF)
        Fk = zell_koeff(geo, phi, K, C, f=f, hub=hub, kmax=400)
        F = geo.F0[:, None] + synth(Fk, n)
    return F, Fk


def rot(geo, Fk):
    """Links (R+) / rechts (R−) umlaufende Radien je Harmonischer aus zweiseitigen Koeffizienten.
    Z(t) = M_x + i M_y; Anteil e^{+ikωt}: X_k + iY_k (links), Anteil e^{−ikωt}: conj(X_k) + i conj(Y_k) (rechts)."""
    Xk = geo.xc[:, 1] @ Fk
    Yk = -(geo.xc[:, 0] @ Fk)
    return np.abs(Xk + 1j * Yk), np.abs(np.conj(Xk) + 1j * np.conj(Yk))


print('=== A: KM-06 Zellkräfte, Summe, Momente (linear) ===')
print('Fall    μ     Geo  Cfg | N_min    N_SS  | Zelle_min Reserve  Summe/3 | Zelle_SS | R+1     R−2     | |M| min…max   | N1')
FAELLE = [('REF', 1.0, 'G0', 'T'), ('REF', 1.0, 'G0h', 'T'), ('REF', 0.462, 'G0', 'T'), ('STEIF', 0.462, 'G0', 'T'),
          ('STEIF', 0.462, 'G60', 'T'), ('STARR', 0.462, 'G0', 'T'), ('STARR', 0.4, 'G0', 'T'),
          ('STARR', 0.462, 'G0', 'Z'), ('STARR', 0.462, 'G60', 'T')]
CFG = {'T': (0, 120, 240), 'Z': (0, 110, 240)}
for fall, mu, gn, cf in FAELLE:
    g = Geom(mu, R_c=R, **GEO[gn])
    F, Fk = zellkraefte(g, CFG[cf], fall)
    N = F.sum(0)
    Rp, Rm = rot(g, Fk)
    Mx, My = momente(g, F)
    Ma = np.hypot(Mx, My)
    Nk1 = 2 * abs(Fk[:, 1].sum())
    print(f'{fall:6s} {mu:5.3f} {gn:4s} {cf}   | {N.min():7.4f} {N.max()-N.min():6.3f} | {F.min():8.4f} {100*F.min()/MG3:6.1f} % '
          f'{100*N.min()/3/MG3:6.1f} % | {(F.max(1)-F.min(1)).max():7.3f}  | {Rp[1]:.4f}  {Rm[2]:.4f}  | '
          f'{Ma.min():.3f}…{Ma.max():.3f} | {Nk1:.4f}')
g = Geom(0.462, R_c=R)
F, Fk = zellkraefte(g, CFG['Z'], 'STARR')
Rp, Rm = rot(g, Fk)
print(f'Z (STARR μ=0,462 G0): R−1/R+1 = {Rm[1]/Rp[1]:.4f}  (δ/3 = {np.radians(10)/3:.4f})')
# S mit Hub 0,15: Moment null?
F, Fk = zellkraefte(g, (0, 0, 0), 'REF', hub=(0.15,) * 3)
Mx, My = momente(g, F)
print(f'S (REF μ=0,462 G0, h=0,15): max|M| = {np.hypot(Mx, My).max():.2e} N·m, max|F_j − N/3| = {np.max(np.abs(F - F.sum(0)/3)):.2e} N')

print('\n=== A2: Präzisierung A2.5 – sind die Zellkräfte aller Konfigurationen bis auf Zeitverschiebung gleich? ===')
print('(Kriterium: Zellreserve min_j F_j/(Mg/3) über die Konfigurationen; Spannweite 0 ⇔ gleich)')
LAUF = {'Einzel1': ((0, 0, 0), (1, 0, 0)), 'Paar0': ((0, 0, 0), (1, 1, 0)), 'Paar120': ((0, 120, 0), (1, 1, 0)),
        'Paar180': ((0, 180, 0), (1, 1, 0)), 'synchron': ((0, 0, 0), (1, 1, 1)), '(0,0,180)': ((0, 0, 180), (1, 1, 1)),
        'P110/250': ((0, 110, 250), (1, 1, 1)), 'P130/230': ((0, 130, 230), (1, 1, 1)),
        'P110/252': ((0, 110, 252), (1, 1, 1))}
SCHNITT = [((0, p, 240), (1, 1, 1)) for p in range(100, 141, 2)]


def reserven(g, fall, f):
    out = {}
    for name, (ph, hb) in LAUF.items():
        F, _ = zellkraefte(g, ph, fall, f=f, hub=hb, n=4000)
        out[name] = (F.min() / MG3, F.sum(0).min() / 3 / MG3)
    sch = [zellkraefte(g, ph, fall, f=f, hub=hb, n=4000)[0] for ph, hb in SCHNITT]
    out['Schnitt'] = (min(F.min() for F in sch) / MG3, min(F.sum(0).min() for F in sch) / 3 / MG3)
    return out


for fall, mu, rho in (('STEIF', 0.462, 0.5), ('STEIF', 0.462, 1 / np.sqrt(2)), ('REF', 0.462, 1 / np.sqrt(2))):
    for f in (10.0, 12.0):
        g = Geom(mu, R_c=R, rho_f=rho * R)
        r = reserven(g, fall, f)
        z = np.array([v[0] for v in r.values()]) * 100
        print(f'{fall} μ={mu} G0 ρ_f={rho:.3f}R_c f={f:.0f} Hz: Zellreserve {z.min():.1f}…{z.max():.1f} % '
              f'(synchron {100*r["synchron"][0]:.1f} %, (0,0,180) {100*r["(0,0,180)"][0]:.1f} %, '
              f'P110/250 {100*r["P110/250"][0]:.1f} %, Schnitt {100*r["Schnitt"][0]:.1f} %, Einzel {100*r["Einzel1"][0]:.1f} %)')

print('\n=== B: KM-08 Zellreserve je Zelle | Summe/3 (in % von Mg/3) ===')
for fall, mu in (('STARR', 0.462), ('STEIF', 0.462), ('STARR', 0.4)):
    for f in (10.0, 12.0):
        print(f'{fall} μ = {mu}, f = {f:.0f} Hz')
        print('  Geo  ' + ''.join(f'{k:>16s}' for k in list(LAUF) + ['Schnitt']))
        for gn in GEO:
            g = Geom(mu, R_c=R, **GEO[gn])
            r = reserven(g, fall, f)
            print(f'  {gn:4s} ' + ''.join(f'  {100*v[0]:6.1f}|{100*v[1]:5.1f}' for v in r.values()))

print('\n=== C: KM-04 Drehfeld-These ===')
c = c_egg(6)
print('A_k = 2|c_k| (analytisch):', np.round(2 * np.abs(c[1:7]), 4))
for mu in (1.0, 0.462):
    m = mu * M_TOT / 3
    print(f'μ = {mu}: (3/2)·m·A1·R = {1.5*m*2*abs(c[1])*R:.5f} N·m')
# quasistatisch, μ = 1, G0, Zeitbereich direkt
g = Geom(1.0, R_c=R)
n = 20000
F = starr_zeit(g, (0, 120, 240), n=n)
Mx, My = momente(g, F)
Ma = np.hypot(Mx, My)
Fk = zell_koeff(g, (0, 120, 240), None, None, kmax=12)
Rp, Rm = rot(g, Fk)
ang = np.unwrap(np.arctan2(My, Mx))
wind = (ang[-1] - ang[0] + (np.arctan2(My[1], Mx[1]) - np.arctan2(My[0], Mx[0]))) / (2 * np.pi)
spec = np.abs(np.fft.rfft(Ma)) / n
print(f'quasistatisch μ=1 G0 T: |M| = {Ma.min():.4f} … {Ma.max():.4f} N·m, max/min = {Ma.max()/Ma.min():.3f}; '
      f'R+1 = {Rp[1]:.5f}, R−2 = {Rm[2]:.5f} (R−2/R+1 = {Rm[2]/Rp[1]:.4f}); ⟨Mx⟩,⟨My⟩ = {Mx.mean():.1e}, {My.mean():.1e}; '
      f'Netto-Umläufe ≈ {wind:+.2f}')
big = [k for k in range(1, 13) if spec[k] > 1e-6 * spec[0]]
print(f'  Harmonische in |M(t)| (> 1e-6 des Mittels): {big}')
# Sinusprofil gleicher Spitze-Spitze-Hub
T = 0.1
t = np.arange(n) * T / n
w = 2 * np.pi * 10
asin = lambda tt: -((0.005 + 0.0026923) / 2) * w ** 2 * np.sin(w * tt)
tau = np.radians([0, 120, 240]) / w
Fs = g.F0[:, None] + g.Nm.T @ (g.m[:, None] * np.stack([asin(t - tau[i]) for i in range(3)]))
Mxs, Mys = momente(g, Fs)
Ms = np.hypot(Mxs, Mys)
print(f'  Sinusprofil: |M| = {Ms.min():.5f} … {Ms.max():.5f} N·m')
# umgekehrte Zuordnung der Module (Rechtsreihenfolge)
gR = Geom(1.0, R_c=R)
gR.xm = gR.xm * np.array([1, -1]); gR.Nm = 1 / 3 + 2 / (3 * R ** 2) * (gR.xm @ gR.xc.T)
FkR = zell_koeff(gR, (0, 120, 240), None, None, kmax=12)
RpR, RmR = rot(gR, FkR)
print(f'  Modulzuordnung gespiegelt: R+1 = {RpR[1]:.5f}, R−1 = {RmR[1]:.5f}, R+2 = {RpR[2]:.5f}, R−2 = {RmR[2]:.5f}')
# Summe: nur k ≡ 0 mod 3; Moment: nur k ≢ 0
Nk = np.abs(Fk.sum(0))
Mk = Rp + Rm
print('  |N_k| k=1..9:', np.round(2 * Nk[1:10], 5))
print('  R+_k + R−_k k=1..9:', np.round(Mk[1:10], 5))
# dynamisch REF μ = 1, G0
for mu, rho in ((1.0, 0.5), (0.462, 0.7), (0.462, 0.5)):
    g = Geom(mu, R_c=R, rho_f=rho * R)
    Fk = zell_koeff(g, (0, 120, 240), K_REF, C_REF, kmax=400)
    F = g.F0[:, None] + synth(Fk, NT)
    Mx, My = momente(g, F)
    Ma = np.hypot(Mx, My)
    Rp, Rm = rot(g, Fk)
    ang = np.unwrap(np.arctan2(np.r_[My, My[0]], np.r_[Mx, Mx[0]]))
    wind = (ang[-1] - ang[0]) / (2 * np.pi)
    Fq = zell_koeff(g, (0, 120, 240), None, None, kmax=4)
    Rq, Rmq = rot(g, Fq)
    print(f'REF μ={mu} G0 ρ_f={rho}: R+1 = {Rp[1]:.4f}, R−2 = {Rm[2]:.4f}; |H_t(ω)| = {Rp[1]/Rq[1]:.3f}, '
          f'|H_t(2ω)| = {Rm[2]/Rmq[2]:.3f}; |M| {Ma.min():.4f}…{Ma.max():.4f} (max/min {Ma.max()/Ma.min():.2f}); '
          f'Netto-Umläufe je Zyklus {wind:+.2f}')

print('\n=== D: KM-09 Leckage am Triphasik-Punkt (STARR μ = 0,462, G0) ===')
g0 = Geom(0.462, R_c=R)
F0, Fk0 = zellkraefte(g0, CFG['T'], 'STARR', n=20000)
N0 = F0.sum(0)
Rp0, Rm0 = rot(g0, Fk0)


def stoer(name, F, Fk, g, gain=None):
    if gain is not None:
        F = F * gain[:, None]; Fk = Fk * gain[:, None]
    N = F.sum(0)
    Nk = Fk.sum(0) - Fk0.sum(0)
    Rp, Rm = rot(g, Fk)
    print(f'  {name:22s}: δN1 = {2*abs(Nk[1]):.4f} N, δN2 = {2*abs(Nk[2]):.4f} N, δF_min = {N.min()-N0.min():+.4f} N, '
          f'R−1/R+1 = {Rm[1]/Rp[1]:.5f}; δN1/u_c = {2*abs(Nk[1])/0.0327:.2f}')


g = Geom(0.462, R_c=R, m_rel=(1, 1.01, 1)); F, Fk = zellkraefte(g, CFG['T'], 'STARR', n=20000); stoer('Masse M2 +1 %', F, Fk, g)
F, Fk = zellkraefte(g0, CFG['T'], 'STARR', hub=(1, 1.01, 1), n=20000); stoer('Hub M2 +1 %', F, Fk, g0)
F, Fk = zellkraefte(g0, (0, 121, 240), 'STARR', n=20000); stoer('Phase M2 +1°', F, Fk, g0)
F, Fk = zellkraefte(g0, (0, 120, 241), 'STARR', n=20000); stoer('Phase M3 +1°', F, Fk, g0)
stoer('Zellverstärkung Z2 +1 %', F0, Fk0, g0, gain=np.array([1, 1.01, 1]))
# REF μ = 1 resonant
gr = Geom(1.0, R_c=R); grm = Geom(1.0, R_c=R, m_rel=(1, 1.01, 1))
Fa = zell_koeff(gr, CFG['T'], K_REF, C_REF, kmax=12); Fb = zell_koeff(grm, CFG['T'], K_REF, C_REF, kmax=12)
d = Fb.sum(0) - Fa.sum(0)
print(f'  REF μ=1 G0, Masse M2 +1 %: δN1 = {2*abs(d[1]):.4f} N, δN2 = {2*abs(d[2]):.4f} N')
# Zerlegung: ohne Verstimmung (nur Anregung +1 %, Massenmatrix nominal)
Fc = zell_koeff(gr, CFG['T'], K_REF, C_REF, hub=(1, 1.01, 1), kmax=12)
d2 = Fc.sum(0) - Fa.sum(0)
print(f'  REF μ=1 G0, nur Anregung +1 % (Hub, Masse nominal): δN2 = {2*abs(d2[2]):.4f} N  -> Rest ist Verstimmung der Zelle 2')
