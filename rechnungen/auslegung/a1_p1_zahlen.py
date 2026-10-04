"""
a1_p1_zahlen.py – Aufgabe 1: Nachrechnung der P1-Zahlen (λ Einzelmodul, Dauerkontaktgrenze, f_n,
3f/f_n, 2f/f_n, F_min Triphasik, Zeltsekanten, PB1-Herleitung, A4-Frequenzgrenzen).
Eigene Rechnung mit mu_modell.py (lineares Modell analytisch, RK4-μ-Engine); Gegenprobe mit
code/linear_solver.py und data/finesweep_2deg_120_240.csv (nur gelesen).
Laufzeit ca. 4–5 min (RK4).
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402
import linear_solver as ls  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
f0, K0, C0, H0 = 10.0, 1e4, 16.0, mm.HUB_REF
out = []


def p(s=''):
    print(s)
    out.append(s)


p('=== A1  Nachrechnung der P1-Zahlen (Prüfgruppe auslegung) ===')
fn = mm.f_n(K0)
p(f'f_n = √(K/M)/2π = {fn:.4f} Hz;  2f/f_n = {2 * f0 / fn:.4f};  3f/f_n = {3 * f0 / fn:.4f};  '
  f'f_n/2 = {fn / 2:.3f} Hz gegen 3f = 30 Hz')
H, _ = mm.transfer(K0, C0, f0, 5)
p(f'|H(kω)| k = 1..4: ' + ' / '.join(f'{abs(H[k]):.3f}' for k in range(1, 5)) + f';  ζ = {mm.ZETA_REF:.6f}')
p(f'Hub (Spitze-Spitze) = {1e3 * H0:.4f} mm, a_hold = {mm.a_hold(H0, f0):.4f} m/s², '
  f'a_fast = {mm.a_fast(H0, f0):.4f} m/s², ε(μ=1) = {mm.eps_of(1, H0, f0):.4f}')

# ── Triphasik-Punkt ─────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(REPO, 'data', 'finesweep_2deg_120_240.csv'))
row = df[(df.phi2_deg == 120) & (df.phi3_deg == 240)].iloc[0]
lin = mm.linear_run((0, 120, 240), (1, 1, 1), 1.0, H0, f0, K0, C0)
p(f'\nTriphasik (120°,240°): CSV F_min = {row.F_min:.6f} N (Zeile {row.name + 2} der Datei), '
  f'eigenes lineares Modell {lin["F_min"]:.6f} N, linear_solver {ls.solve(120, 240)["F_min"][0]:.6f} N, '
  f'CSV F_max {row.F_max:.6f} / linear {lin["F_max"]:.6f} N, Schiefe CSV {row.F_skew:.6f} / linear {lin["skew"]:.6f}')
p(f'  F_min ist Maximum des Feinsweeps? max F_min der CSV = {df.F_min.max():.6f} N bei '
  f'({df.loc[df.F_min.idxmax(), "phi2_deg"]:.0f}°, {df.loc[df.F_min.idxmax(), "phi3_deg"]:.0f}°); '
  f'liftoff-frei {int((df.liftoff == 0).sum())}/441')

# ── Zeltsekanten ────────────────────────────────────────────────────────────
fm = {q: mm.linear_run((0, q, 240), (1, 1, 1), 1.0, H0, f0, K0, C0)['F_min'] for q in (100, 118, 120, 122, 140)}
csv = {q: df[(df.phi2_deg == q) & (df.phi3_deg == 240)].F_min.iloc[0] for q in (100, 118, 120, 122, 140)}
p(f'\n2°-Sekanten 118→120 / 122→120: linear {(fm[120] - fm[118]) / 2:.4f} / {(fm[120] - fm[122]) / 2:.4f} N/°; '
  f'CSV {(csv[120] - csv[118]) / 2:.4f} / {(csv[120] - csv[122]) / 2:.4f} N/°')
p(f'20°-Sekanten 100→120 / 140→120: linear {(fm[120] - fm[100]) / 20:.4f} / {(fm[120] - fm[140]) / 20:.4f} N/°  '
  f'(Exposé „≈0,23 / ≈0,19“)')
fsec = np.array([mm.linear_run((0, q, 240), (1, 1, 1), 1.0, H0, f0, K0, C0)['F_min'] for q in mm.SECTION_PHI2])
p(f'ΔF_Zelt (Referenz K=1e4, μ=1) = {fsec.max() - fsec.min():.4f} N (Präreg A4: 4,5627 N)')

# ── Einzelmodul: linear ─────────────────────────────────────────────────────
s1 = mm.linear_run((0, 0, 0), (1, 0, 0), 1.0, H0, f0, K0, C0)
dmin = MG - s1['F_min']
p(f'\nEinzelmodul, Referenzhub, linear: F_min_lin = {s1["F_min"]:+.4f} N, F_max = {s1["F_max"]:.4f} N, '
  f'x_max = {s1["x_max"] * 1e3:+.4f} mm')
hf_contact = MG / dmin
hf_res = 0.75 * MG / dmin
# Grenze aus der Körperkoordinate x_max < 0: x = −Mg/K + s·(x_dyn); lineare Skalierung in s
x_dyn = s1['x_max'] + MG / K0
hf_x = (MG / K0) / x_dyn
p(f'  lineare Dauerkontaktgrenze (F_min = 0): Hubanteil {hf_contact:.4f} = {100 * hf_contact:.1f} % des Referenzhubs '
  f'(Grenze aus x_max < 0: {100 * hf_x:.1f} %)')
p(f'  mit 25-%-Reserve (F_min ≥ 0,25·Mg): Hubanteil {100 * hf_res:.1f} %')

# ── Einzelmodul: RK4 (eigene Engine, Engine-Konvention 15 s / Burn-in 5 s) ──
svals = np.array([0.70, 0.72, 0.74, 0.75, 0.755, 0.76, 0.77, 0.78, 0.80, 0.90, 1.00])
W = np.zeros((svals.size, 3)); W[:, 0] = svals
r = mm.rk4_mu(np.zeros((svals.size, 3)), W, 1.0, H0, f0, K0, C0)
p('\nEinzelmodul RK4 (μ = 1, K = 1e4, C = 16, Δt = 50 µs, 15 s, Auswertung 10 s), Hubanteil s:')
for j, s in enumerate(svals):
    p(f'  s = {s:5.3f}  λ = {r["liftoff"][j]:6.2f} %  F_min = {r["F_min"][j]:.4f} N  F_max = {r["F_max"][j]:.4f} N  '
      f'⟨N⟩−Mg = {r["mean"][j] - MG:+.2e} N  Schiefe = {r["skew"][j]:+.4f}')
# Gegenprobe-Konvention: 20 s, letzte 4 s; zusätzlich Δt/2
r20 = mm.rk4_mu(np.zeros((1, 3)), [[1, 0, 0]], 1.0, H0, f0, K0, C0, t_sim=20.0, t_burn=16.0)
r20h = mm.rk4_mu(np.zeros((1, 3)), [[1, 0, 0]], 1.0, H0, f0, K0, C0, t_sim=20.0, t_burn=16.0, n_per=4000)
p(f'  s = 1, 20 s / letzte 4 s: λ = {r20["liftoff"][0]:.2f} %;  mit Δt/2 = 25 µs: λ = {r20h["liftoff"][0]:.2f} %  '
  f'(Gegenprobe 26.09.: 17,9 %)')

# ── PB1-Herleitung (Präreg A4/A8) ───────────────────────────────────────────
fr = np.array([mm.linear_run((0, q, 240), (1, 1, 1), 0.4, H0, f0, None, 0.0)['F_min'] for q in mm.SECTION_PHI2])
dF = fr.max() - fr.min()
c_inf = stats.norm.ppf(1 - 0.05 / (2 * 147))
c19 = stats.t.ppf(1 - 0.05 / (2 * 147), 19)
p(f'\nPB1 (starr, μ = 0,4, 10 Hz, Referenzhub): F_min(120°) = {fr[10]:.4f} N, F_min(100°) = {fr[0]:.4f} N, '
  f'F_min(140°) = {fr[-1]:.4f} N, ΔF_Zelt = {dF:.4f} N')
p(f'  Δ = 0,25·ΔF_Zelt = {0.25 * dF:.4f} N;  c(ν→∞) = {c_inf:.4f}, c(ν=19) = {c19:.4f};  '
  f'u_c ≤ {0.25 * dF / c_inf:.4f} N bzw. {0.25 * dF / c19:.4f} N ({100 * 0.25 * dF / c19 / MG:.3f} % von Mg)')
p(f'  2°-Sekanten starr μ=0,4: {(fr[10] - fr[9]) / 2:.4f} / {(fr[10] - fr[11]) / 2:.4f} N/°')

# ── A4-Frequenzgrenzen (starr, μ = 0,4, Referenzhub) ────────────────────────
p('\nA4-Prüfung: starr, μ = 0,4, Referenzhub; kleinstes F_min/Mg je Lauftyp über f')
p(f'{"f":>4} {"Schnitt":>8} {"Einzel":>8} {"(0,180)":>8} {"synchron":>9}')
lim = {}
for f in range(10, 27):
    sec = min(mm.linear_run((0, q, 240), (1, 1, 1), 0.4, H0, f, None, 0.0)['F_min'] for q in mm.SECTION_PHI2)
    e1 = mm.linear_run((0, 0, 0), (1, 0, 0), 0.4, H0, f, None, 0.0)['F_min']
    zg = mm.linear_run((0, 0, 180), (1, 1, 1), 0.4, H0, f, None, 0.0)['F_min']
    sy = mm.linear_run((0, 0, 0), (1, 1, 1), 0.4, H0, f, None, 0.0)['F_min']
    v = dict(Schnitt=sec / MG, Einzel=e1 / MG, Zweiergruppe=zg / MG, synchron=sy / MG)
    for kname, val in v.items():
        lim.setdefault(kname, {'lo': None, 'r25': None})
        if val > 0:
            lim[kname]['lo'] = f
        if val >= 0.25:
            lim[kname]['r25'] = f
    p(f'{f:>4} {100 * v["Schnitt"]:>7.1f}% {100 * v["Einzel"]:>7.1f}% {100 * v["Zweiergruppe"]:>7.1f}% '
      f'{100 * v["synchron"]:>8.1f}%')
p('  größte ganzzahlige f mit F_min > 0 bzw. ≥ 25 %: ' +
  '; '.join(f'{k}: {d["lo"]} / {d["r25"]} Hz' for k, d in lim.items()))
for name, ph, w in [('Schnitt max', None, None), ('synchron', (0, 0, 0), (1, 1, 1)),
                    ('(0,180)', (0, 0, 180), (1, 1, 1)), ('Einzelmodul', (0, 0, 0), (1, 0, 0))]:
    if ph is None:
        v = max(mm.linear_run((0, q, 240), (1, 1, 1), 0.4, H0, 10, None, 0.0)['F_max'] for q in mm.SECTION_PHI2)
    else:
        v = mm.linear_run(ph, w, 0.4, H0, 10, None, 0.0)['F_max']
    p(f'  F_max bei 10 Hz, {name}: {v:.4f} N')

with open(os.path.join(HERE, 'a1_p1_zahlen_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
