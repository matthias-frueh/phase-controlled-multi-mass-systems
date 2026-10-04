"""
a4_rk4_stichprobe.py – Aufgabe 4: Stichprobe mit der nichtlinearen μ-Engine (einseitiger Kontakt, RK4 wie
Referenz-Engine, mu_modell.rk4_mu) gegen die lineare Vorhersage (mu_modell.linear_run) an den
Arbeitspunktvorschlägen aus a3b. Je Fall 30 Läufe: Einzelmodul, Paare Δ = 0°/120°/180° (drittes Modul geparkt),
synchron, (0°,180°), 3 Piloten, 21 Schnittpunkte. Standardstart (z = −Mg/K, ż = 0 bei t = 0), 8 s, Auswertung
der letzten 5 s (ganze Perioden), Δt = T/2000.
Aufruf: python3 a4_rk4_stichprobe.py FALL   mit FALL ∈ {V1z05, V2z02, V4z02, V4z10, V5z05, start, E1}
  start: Wurfstarts ż₀ = 0,5 und 1,5 m/s an V2 (ζ = 0,02) für 5 Läufe
  E1:    synchrone Läufe oberhalb der Dauerkontaktgrenze an V1 (ζ = 0,05), f = 13, 14, 16 Hz → Spitzenkraft
Ausgabe: a4_rk4_<FALL>.csv und a4_rk4_<FALL>_ausgabe.txt
"""
import os
import sys
import time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
FAELLE = {   # name: (μ, Hub, f, K, ζ)
    'V1z05': (0.4615, 8.0e-3, 10.0, 1.5e6, 0.05),
    'V2z02': (0.40, mm.HUB_REF, 12.0, 2.5e6, 0.02),
    'V4z02': (0.4615, 8.0e-3, 10.0, 3.2e5, 0.02),
    'V4z10': (0.4615, 8.0e-3, 10.0, 3.2e5, 0.10),
    'V5z05': (0.60, mm.HUB_REF, 12.0, 2.5e6, 0.05),
}
RUNS = ([('Einzelmodul', 'einzel', (0, 0, 0), (1, 0, 0))] +
        [(f'Paar Δ={d}°', 'paar', (0, d, 0), (1, 1, 0)) for d in (0, 120, 180)] +
        [('synchron', 'synchron', (0, 0, 0), (1, 1, 1)), ('(0°,180°)', 'zweiergruppe', (0, 0, 180), (1, 1, 1))] +
        [(f'Pilot ({a:g},{b:g})', 'pilot', (0, a, b), (1, 1, 1)) for a, b in mm.PILOTS] +
        [(f'Schnitt {q:g}°', 'schnitt', (0, q, 240.0), (1, 1, 1)) for q in mm.SECTION_PHI2])

fall = sys.argv[1]
out = []


def p(s=''):
    print(s, flush=True)
    out.append(s)


t0 = time.time()
if fall in FAELLE:
    mu, hub, f, K, zeta = FAELLE[fall]
    C = mm.C_of_zeta(zeta, K)
    ph = np.array([r[2] for r in RUNS], float)
    w = np.array([r[3] for r in RUNS], float)
    rk = mm.rk4_mu(ph, w, mu, hub, f, K, C, t_sim=8.0, t_burn=3.0)
    rows = []
    for j, (name, grp, phs, ws) in enumerate(RUNS):
        li = mm.linear_run(phs, ws, mu, hub, f, K, C)
        rows.append(dict(lauf=name, gruppe=grp, lam_rk4=rk['liftoff'][j], valid_lin=li['valid'],
                         Fmin_lin=li['F_min'], Fmin_rk4=rk['F_min'][j], Fmax_lin=li['F_max'], Fmax_rk4=rk['F_max'][j],
                         mean_rk4_minus_Mg=rk['mean'][j] - MG, skew_lin=li['skew'], skew_rk4=rk['skew'][j],
                         **{f'N{k}_lin': abs(li['Nk'][k - 1]) for k in (1, 2, 3)},
                         **{f'N{k}_rk4': abs(rk['Nk'][k - 1, j]) for k in (1, 2, 3)},
                         **{f'dN{k}': abs(rk['Nk'][k - 1, j] - li['Nk'][k - 1]) for k in (1, 2, 3)}))
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(HERE, f'a4_rk4_{fall}.csv'), index=False, float_format='%.7g')
    p(f'=== A4 RK4-Stichprobe {fall}: μ = {mu}, Hub = {1e3 * hub:.2f} mm, f = {f} Hz, K = {K:.3g} N/m, ζ = {zeta}, '
      f'C = {C:.2f} N·s/m, f_n = {mm.f_n(K):.1f} Hz, ε = {mm.eps_of(mu, hub, f):.4f}, Δt = {1e6 * rk["dt"]:.2f} µs, '
      f'{rk["ncyc"]} Perioden ausgewertet ===')
    p(f'{"Lauf":<18}{"lin":>5}{"λ_RK4":>8}{"Fmin_lin":>10}{"Fmin_RK4":>10}{"ΔFmin":>10}{"Fmax_lin":>10}{"Fmax_RK4":>10}'
      f'{"⟨N⟩−Mg":>10}{"γ_lin":>8}{"γ_RK4":>8}{"max|ΔN_k|":>11}')
    for _, r in D.iterrows():
        p(f'{r.lauf:<18}{"ja" if r.valid_lin else "nein":>5}{r.lam_rk4:>7.2f}%{r.Fmin_lin:>10.5f}{r.Fmin_rk4:>10.5f}'
          f'{r.Fmin_rk4 - r.Fmin_lin:>10.2e}{r.Fmax_lin:>10.5f}{r.Fmax_rk4:>10.5f}{r.mean_rk4_minus_Mg:>10.1e}'
          f'{r.skew_lin:>8.4f}{r.skew_rk4:>8.4f}{max(r.dN1, r.dN2, r.dN3):>11.2e}')
    S = D[D.gruppe == 'schnitt']
    fl, fr = S.Fmin_lin.values, S.Fmin_rk4.values
    p(f'Schnitt: ΔF_Zelt lin {fl.max() - fl.min():.5f} N, RK4 {fr.max() - fr.min():.5f} N; Sekanten lin '
      f'{(fl[10] - fl[9]) / 2:.5f}/{(fl[10] - fl[11]) / 2:.5f}, RK4 {(fr[10] - fr[9]) / 2:.5f}/{(fr[10] - fr[11]) / 2:.5f} N/°; '
      f'Spitze lin {mm.SECTION_PHI2[fl.argmax()]:.0f}°, RK4 {mm.SECTION_PHI2[fr.argmax()]:.0f}°')
    cont = D[D.valid_lin]
    p(f'Kontaktast-Läufe ({len(cont)}): max λ_RK4 = {cont.lam_rk4.max():.3f} %, max|ΔF_min| = '
      f'{(cont.Fmin_rk4 - cont.Fmin_lin).abs().max():.2e} N, max|ΔF_max| = {(cont.Fmax_rk4 - cont.Fmax_lin).abs().max():.2e} N, '
      f'max|ΔN_k| = {cont[["dN1", "dN2", "dN3"]].max().max():.2e} N, max|⟨N⟩−Mg| = {cont.mean_rk4_minus_Mg.abs().max():.1e} N')
    nc = D[~D.valid_lin]
    if len(nc):
        p(f'Läufe ohne Kontaktast (linear F_min ≤ 0): ' + '; '.join(
            f'{r.lauf}: λ_RK4 = {r.lam_rk4:.2f} %, F_max RK4 = {r.Fmax_rk4:.2f} N (lin {r.Fmax_lin:.2f})' for _, r in nc.iterrows()))
elif fall == 'start':
    mu, hub, f, K, zeta = FAELLE['V2z02']
    C = mm.C_of_zeta(zeta, K)
    sel = [r for r in RUNS if r[0] in ('Einzelmodul', 'synchron', 'Schnitt 100°', 'Schnitt 120°', 'Schnitt 140°')]
    ph = np.array([r[2] for r in sel] * 2, float)
    w = np.array([r[3] for r in sel] * 2, float)
    v0 = np.repeat([0.5, 1.5], len(sel))
    rk = mm.rk4_mu(ph, w, mu, hub, f, K, C, t_sim=8.0, t_burn=3.0, v0=v0)
    p(f'=== A4 Wurfstarts an V2 (ζ = 0,02): ż₀ = 0,5 / 1,5 m/s aus z = −Mg/K bei t = 0 ===')
    rows = []
    for j in range(len(ph)):
        name = sel[j % len(sel)][0]
        li = mm.linear_run(sel[j % len(sel)][2], sel[j % len(sel)][3], mu, hub, f, K, C)
        rows.append(dict(lauf=name, v0=v0[j], lam=rk['liftoff'][j], Fmin=rk['F_min'][j], Fmin_lin=li['F_min']))
        p(f'  {name:<14} ż₀ = {v0[j]:.1f} m/s: λ = {rk["liftoff"][j]:.3f} %, F_min RK4 {rk["F_min"][j]:.5f} N, '
          f'linear {li["F_min"]:.5f} N')
    pd.DataFrame(rows).to_csv(os.path.join(HERE, f'a4_rk4_{fall}.csv'), index=False, float_format='%.7g')
elif fall == 'E1':
    mu, hub, f0, K, zeta = FAELLE['V1z05']
    C = mm.C_of_zeta(zeta, K)
    p(f'=== A4 E1-Abschätzung: synchron an V1 (μ = {mu}, Hub {1e3 * hub:.1f} mm, K = {K:.3g}, ζ = {zeta}) über f ===')
    rows = []
    for f in (12.0, 13.0, 14.0, 16.0):
        rk = mm.rk4_mu(np.zeros((1, 3)), np.ones((1, 3)), mu, hub, f, K, C, t_sim=8.0, t_burn=3.0)
        li = mm.linear_run((0, 0, 0), (1, 1, 1), mu, hub, f, K, C)
        rows.append(dict(f=f, eps=mm.eps_of(mu, hub, f), Fmin_lin=li['F_min'], Fmax_lin=li['F_max'],
                         lam=rk['liftoff'][0], Fmax=rk['F_max'][0], mean=rk['mean'][0] - MG))
        p(f'  f = {f:4.1f} Hz, ε = {mm.eps_of(mu, hub, f):.3f}: linear F_min {li["F_min"]:+.3f} N, F_max {li["F_max"]:.2f} N; '
          f'RK4 λ = {rk["liftoff"][0]:.2f} %, F_max = {rk["F_max"][0]:.2f} N (Zelle bei Summe/3: {rk["F_max"][0] / 3:.2f} N, '
          f'{rk["F_max"][0] / MG:.1f}·Mg)')
    pd.DataFrame(rows).to_csv(os.path.join(HERE, f'a4_rk4_{fall}.csv'), index=False, float_format='%.7g')
p(f'Rechenzeit {time.time() - t0:.0f} s')
with open(os.path.join(HERE, f'a4_rk4_{fall}_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
