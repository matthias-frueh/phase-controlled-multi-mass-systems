"""
v5_nichtlinear.py – Gegenprüfung AUS-11, AUS-12, AUS-13 mit ereignisgesteuerter, abschnittsweise exakter Lösung
(vk_lib.System.simulate; kein fester Zeitschritt, λ = exakte Flugzeit/Fenster) und einer analytischen
Stoßabbildung (Hüpfball-Grenzfall: Stoß momentan, Restitution e).
Aufruf: python3 v5_nichtlinear.py A|B|C|D
  A  AUS-11: Kontaktast vom Standardstart an V1 (ζ = 0,05), V2 (ζ = 0,02), V5 synchron (ζ = 0,05); 8 s, letzte 5 s
  B  AUS-12: Wurfstarts ż₀ aus der statischen Ruhelage an V1 synchron/Triphasik, V2 Triphasik; 16 s, letzte 4 s
  C  AUS-13: E1 an V1-Parametern synchron (ζ = 0,05) bei 12/13/14/16 Hz, Standardstart, 15 s, Fenster 5–15 s
  D  Analytik: Restitution des einseitigen KV-Kontakts (numerisch exakt) und Existenzbedingung des
     1-periodischen Hüpforbits für V1 synchron
Ausgabe: v5_nichtlinear_<Teil>_ausgabe.txt
"""
import sys
import time
import numpy as np
import vk_lib as vk

M, G = vk.M_REF, vk.G
MG = M * G
part = sys.argv[1]
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
V1 = (0.4615, 8.0e-3, 10.0, 1.5e6)
V2 = (0.40, vk.HUB_REF, 12.0, 2.5e6)
V5 = (0.60, vk.HUB_REF, 12.0, 2.5e6)

if part == 'A':
    p('=== AUS-11: Standardstart (x = −Mg/K, ẋ = 0, t = 0), 8 s, Auswertung letzte 5 s ===')
    cases = [('V1', V1, 0.05, [('einzel', (0, 0, 0), (1, 0, 0)), ('paar 0', (0, 0, 0), (1, 1, 0)),
                                ('paar 120', (0, 120, 0), (1, 1, 0)), ('paar 180', (0, 180, 0), (1, 1, 0)),
                                ('synchron', (0, 0, 0), (1, 1, 1)), ('(0,180)', (0, 0, 180), (1, 1, 1)),
                                ('pilot 110/250', (0, 110, 250), (1, 1, 1)), ('pilot 130/230', (0, 130, 230), (1, 1, 1)),
                                ('schnitt 100', (0, 100, 240), (1, 1, 1)), ('schnitt 118', (0, 118, 240), (1, 1, 1)),
                                ('schnitt 120', (0, 120, 240), (1, 1, 1)), ('schnitt 122', (0, 122, 240), (1, 1, 1)),
                                ('schnitt 140', (0, 140, 240), (1, 1, 1))]),
             ('V2', V2, 0.02, [('synchron', (0, 0, 0), (1, 1, 1)), ('schnitt 100', (0, 100, 240), (1, 1, 1)),
                                ('schnitt 120', (0, 120, 240), (1, 1, 1)), ('schnitt 140', (0, 140, 240), (1, 1, 1))]),
             ('V5', V5, 0.05, [('synchron', (0, 0, 0), (1, 1, 1)), ('schnitt 120', (0, 120, 240), (1, 1, 1))])]
    for nm, (mu, hub, f, K), zeta, runs in cases:
        C = vk.zeta_to_C(zeta, K)
        dmax = 0.0
        for rn, ph, w in runs:
            s = vk.System(ph, w, mu, hub, f, K, C)
            lin = s.periodic_linear(fine=20000)['N']
            o = s.simulate(8.0, 3.0)
            d = o['F_min'] - lin.min()
            if o['lam'] == 0:
                dmax = max(dmax, abs(d))
            p(f'  {nm} ζ={zeta} {rn:<14} λ = {o["lam"]:7.3f} %  F_min = {o["F_min"]:8.4f} N (linear {lin.min():8.4f}, Δ = {d:+.1e})  '
              f'F_max = {o["F_max"]:8.3f} N (linear {lin.max():.3f})  ({time.time()-t0:.0f} s)')
        p(f'  {nm}: max |ΔF_min| über Läufe mit λ = 0: {dmax:.1e} N')

if part == 'B':
    p('=== AUS-12: Wurfstarts aus der statischen Ruhelage bei t = 0, 16 s, Auswertung letzte 4 s ===')
    mu, hub, f, K = V1
    for zeta in (0.02, 0.05, 0.1, 0.2):
        C = vk.zeta_to_C(zeta, K)
        for v0 in (0.25, 0.30, 0.50):
            s = vk.System((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
            o = s.simulate(16.0, 12.0, v0=v0)
            st = o['starts'][o['starts'] >= 12.0]
            ph = np.mod(st * f, 1.0)
            p(f'  V1 synchron ζ = {zeta:<4} ż₀ = {v0:.2f} m/s: λ = {o["lam"]:7.3f} %  F_max = {o["F_max"]:8.2f} N '
              f'({o["F_max"]/MG:.1f}·Mg)  Kontaktbeginne/Periode = {o["n_imp"]/40:.2f}  '
              f'Phase der Kontaktbeginne θ/T = {ph.mean() if ph.size else float("nan"):.4f} ± {ph.std() if ph.size else 0:.1e}  ({time.time()-t0:.0f} s)')
    # Kontrolle: Zeitraster der Ereignissuche
    C = vk.zeta_to_C(0.05, K)
    s = vk.System((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
    o = s.simulate(16.0, 12.0, v0=0.30, h=2.5e-6)
    p(f'  Kontrolle V1 synchron ζ = 0,05, ż₀ = 0,30, h/2: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.2f} N')
    o = s.simulate(40.0, 36.0, v0=0.30)
    p(f'  Kontrolle V1 synchron ζ = 0,05, ż₀ = 0,30, 40 s: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.2f} N')
    for zeta in (0.02, 0.1):
        C = vk.zeta_to_C(zeta, K)
        o = vk.System((0, 120, 240), (1, 1, 1), mu, hub, f, K, C).simulate(16.0, 12.0, v0=0.5)
        p(f'  V1 Triphasik ζ = {zeta} ż₀ = 0,50 m/s: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.2f} N, F_min = {o["F_min"]:.4f} N')
    mu2, hub2, f2, K2 = V2
    o = vk.System((0, 120, 240), (1, 1, 1), mu2, hub2, f2, K2, vk.zeta_to_C(0.02, K2)).simulate(16.0, 12.0, v0=0.5)
    p(f'  V2 Triphasik ζ = 0,02 ż₀ = 0,50 m/s: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.2f} N, F_min = {o["F_min"]:.4f} N')
    # Referenz
    o = vk.System((0, 120, 240), (1, 1, 1), 1.0, vk.HUB_REF, 10.0, 1e4, 16.0).simulate(15.0, 5.0, v0=3.0)
    p(f'  Referenz Triphasik ż₀ = 3 m/s: λ = {o["lam"]:.3f} %, F_min = {o["F_min"]:.4f} N')

if part == 'C':
    p('=== AUS-13: E1 an V1-Parametern (μ = 0,4615, Hub 8 mm, K = 1,5e6 N/m, ζ = 0,05), synchron, Standardstart ===')
    mu, hub, _, K = V1
    C = vk.zeta_to_C(0.05, K)
    for f in (12.0, 13.0, 14.0, 16.0):
        s = vk.System((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
        lin = s.periodic_linear(fine=20000)['N']
        o = s.simulate(15.0, 5.0)
        st = o['starts'][o['starts'] >= 5.0]
        p(f'  f = {f:.0f} Hz: lineares F_min = {lin.min():+.3f} N; λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.1f} N '
          f'({o["F_max"]/MG:.0f}·Mg), Kontaktbeginne/Periode = {o["n_imp"]/(10*f):.3f}  ({time.time()-t0:.0f} s)')
    s = vk.System((0, 0, 0), (1, 1, 1), mu, hub, 14.0, K, C)
    o = s.simulate(15.0, 5.0, h=2.5e-6)
    p(f'  Kontrolle 14 Hz mit h/2: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.1f} N')
    o = s.simulate(30.0, 20.0)
    p(f'  Kontrolle 14 Hz, 30 s, Fenster 20–30 s: λ = {o["lam"]:.3f} %, F_max = {o["F_max"]:.1f} N')

if part == 'D':
    p('=== Analytik zum Hüpfzustand (V1 synchron) ===')
    mu, hub, f, K = V1
    T = 1 / f
    for zeta in (0.02, 0.05, 0.1, 0.2):
        C = vk.zeta_to_C(zeta, K)
        e_kv = np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2))
        p(f'  ζ = {zeta}: e_KV(Formel) = {e_kv:.3f}', )
        vmax_s = mu * np.pi * hub * f          # max ṡ der "Tisch"-Bewegung s = μ·z (synchron)
        for e in (e_kv,):
            need = G * T * (1 - e) / (2 * (1 + e))
            vin = G * T / (1 + e)
            p(f'     Existenz 1-periodischer Orbit (Flugzeit T, momentaner Stoß): nötig max ṡ ≥ gT(1−e)/(2(1+e)) = {need:.4f} m/s; '
              f'vorhanden μ·π·Hub·f = {vmax_s:.4f} m/s → {"existiert" if vmax_s >= need else "existiert nicht"}; '
              f'Aufprallgeschwindigkeit gT/(1+e) = {vin:.3f} m/s, √(KM)·v = {np.sqrt(K*M)*vin:.0f} N')
    # Spitzenkraft eines KV-Stoßes mit v_in = 0,53 m/s (ohne Schwerkraft/Module), ζ = 0,05
    for zeta in (0.02, 0.05, 0.1):
        C = vk.zeta_to_C(zeta, K)
        wn = np.sqrt(K / M); sg = C / (2 * M); wd = np.sqrt(wn**2 - sg**2)
        tt = np.linspace(0, np.pi / wd, 200001)
        vin = G * T / (1 + np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2)))
        x = -vin / wd * np.exp(-sg * tt) * np.sin(wd * tt)
        v = -vin * np.exp(-sg * tt) * (np.cos(wd * tt) - sg / wd * np.sin(wd * tt))
        F = -K * x - C * v
        p(f'  KV-Stoß ζ = {zeta}: v_in = {vin:.3f} m/s → F_peak = {F.max():.0f} N ({F.max()/MG:.0f}·Mg), Kontaktdauer ≈ {1e3*tt[np.argmax(F<0) if (F<0).any() else -1]:.2f} ms')
p(f'Rechenzeit {time.time()-t0:.0f} s')
open(f'v5_nichtlinear_{part}_ausgabe.txt', 'w').write('\n'.join(out) + '\n')
