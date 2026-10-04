"""
a3b_arbeitspunkte.py – Aufgabe 3, Teil B: zulässiger Bereich in (Hub, K, f, μ) und Arbeitspunktvorschläge.

Kriterien (Quelle: Präreg v2 §5.3, §8.5, Anhang A4/A8; Zellmodell als ANNAHME):
 (i)   F_min ≥ 0,25·Mg für jeden geplanten Lauf, Zellkraft = Summe/3 (Annahme: Modulkräfte wirken im
       Flächenschwerpunkt des Zelldreiecks). Zusätzlich ausgewiesen: Zellmodell Präreg A2.5 (jedes Modul über
       einer Zelle, starr) – dann trägt Zelle j Mg/3 + m_j·a_j und jede Konfiguration hat je Zelle die Reserve
       der synchronen Phasung (quasistatisch); Kippdynamik rechnet eine andere Gruppe.
       Laufmengen: PFLICHT = 21 Schnittpunkte + 3 Piloten + Einzelmodule (Präreg §5.3 a);
                   ZUSATZ = PFLICHT + (0°,180°) + synchron (H4-Zusatzkonfigurationen, „falls zulässig“);
                   ALLE   = ZUSATZ + Zweierkombinationen (zwei Module laufen, Δ = 0…355°, im Präreg nicht geplant).
 (ii)  3f ≤ f₁/2 ⇔ ρ = f/f_n ≤ 1/6 (f₁ = f_n des 1-FG-Modells; reale Kippmoden können tiefer liegen).
 (iii) PB1: Δ = 0,25·ΔF_Zelt, nötig u_c ≤ Δ/c, c = 3,583 (ν→∞) bzw. 4,356 (ν = 19). Kriterium:
       ΔF_Zelt ≥ 0,4693 N, d. h. die Anforderung ist nicht strenger als u_c ≤ 0,0327 N (A4-Beispiel).
       Für Re/Im N_k analog mit D_k = max_i |N̂_k,i|.
Ausgaben: a3b_bereich.csv, a3b_hubfenster.csv, a3b_vorschlaege.csv, a3b_arbeitspunkte_ausgabe.txt
Laufzeit < 1 min.
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mu_modell as mm  # noqa: E402

M, G, MG = mm.M_REF, mm.G, mm.M_REF * mm.G
R25 = 0.25
DF_REQ = 0.4693                       # N, PB1-Bezug (A4)
C_INF = stats.norm.ppf(1 - 0.05 / 294)
C_19 = stats.t.ppf(1 - 0.05 / 294, 19)
out = []


def p(s=''):
    print(s)
    out.append(s)


df = pd.read_csv(os.path.join(HERE, 'a3a_G_funktionen.csv'))
SETS = {'PFLICHT': ['schnitt', 'pilot', 'einzel'],
        'ZUSATZ': ['schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron'],
        'ALLE': ['schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron', 'paar']}
for s, gs in SETS.items():
    df[f'G_{s}'] = df[[f'G_{g}' for g in gs]].max(axis=1)
    df[f'emax_{s}'] = (1 - R25) / df[f'G_{s}']
    df[f'emaxX_{s}'] = 1.0 / df[[f'X_{g}' for g in gs]].max(axis=1).replace(0, np.nan)   # x < 0 ohne Reserve
df['esig'] = DF_REQ / (MG * df['dG'])
df['esig_bl'] = DF_REQ / (MG * df['dG_bl'])
df.to_csv(os.path.join(HERE, 'a3b_bereich.csv'), index=False, float_format='%.6g')

p('=== A3b  Zulässiger Bereich (dimensionslos: ε = μ·π²·Hub·f²/(TH·g), ρ = f/f_n, ζ) ===')
p(f'c(ν→∞) = {C_INF:.4f}, c(ν=19) = {C_19:.4f}; Signalkriterium ΔF_Zelt ≥ {DF_REQ} N ⇔ ε ≥ ε_sig = '
  f'{DF_REQ}/(M·g·ΔG); Reserve: ε ≤ 0,75/G_set; x < 0 (ohne Reserve): ε < 1/X')
p('\nε-Fenster [ε_sig, ε_max] je Laufmenge bei ausgewählten ρ (ε_sig mit vollem Spektrum; '
  'bandbegrenzt in Klammern):')
p(f'{"ζ":>5}{"ρ":>7}{"3f/f_n":>7}{"ε_sig":>14}{"PFLICHT":>9}{"ZUSATZ":>9}{"ALLE":>9}{"Spitze":>8}'
  f'{"G_syn":>7}{"ΔG":>7}{"1/X_syn":>8}')
for zeta in (0.02, 0.05, 0.1, 0.2):
    for rho in (0.0, 0.03, 0.05, 0.06, 0.08, 0.0833, 0.1, 0.111, 0.125, 0.143, 0.166):
        r = df[(df.zeta == zeta) & (np.isclose(df.rho, rho, atol=6e-4))]
        if r.empty:
            continue
        r = r.iloc[0]
        p(f'{zeta:>5}{r.rho:>7.3f}{3 * r.rho:>7.3f}{r.esig:>7.3f} ({r.esig_bl:.3f}){r.emax_PFLICHT:>9.3f}'
          f'{r.emax_ZUSATZ:>9.3f}{r.emax_ALLE:>9.3f}{r.peak:>8.0f}{r.G_synchron:>7.3f}{r.dG:>7.4f}'
          f'{(1 / r.X_synchron if r.X_synchron > 0 else np.inf):>8.3f}')
p('\nAnteil zulässiger ρ in (0, 1/6] (Raster 0,001), ε-Fenster nicht leer, je ζ und Laufmenge:')
for zeta in (0.02, 0.05, 0.1, 0.2):
    s = df[(df.zeta == zeta) & (df.rho > 0) & (df.rho <= 1 / 6 + 1e-9)]
    txt = []
    for st in SETS:
        ok = s[f'emax_{st}'] >= s['esig']
        txt.append(f'{st} {100 * ok.mean():5.1f} % (unzulässig z. B. ρ = '
                   f'{", ".join(f"{v:.3f}" for v in s.rho[~ok].values[:4])}{" …" if (~ok).sum() > 4 else ""})')
    p(f'  ζ = {zeta}: ' + '; '.join(txt))
p('  robuster Bereich für ZUSATZ (ε-Fenster ≥ 0,15 breit für alle ζ ≥ 0,02): ρ ∈ ' + ', '.join(
    f'{v:.3f}' for v in sorted(set.intersection(*[set(np.round(df[(df.zeta == z) & (df.rho > 0) & (df.rho <= 1 / 6)
                                                                    & (df.emax_ZUSATZ - df.esig >= 0.15)].rho, 3))
                                                    for z in (0.02, 0.05, 0.1, 0.2)]))[:1]) + ' … ' + ', '.join(
    f'{v:.3f}' for v in sorted(set.intersection(*[set(np.round(df[(df.zeta == z) & (df.rho > 0) & (df.rho <= 1 / 6)
                                                                    & (df.emax_ZUSATZ - df.esig >= 0.15)].rho, 3))
                                                    for z in (0.02, 0.05, 0.1, 0.2)]))[-1:]))
rob = sorted(set.intersection(*[set(np.round(df[(df.zeta == z) & (df.rho > 0) & (df.rho <= 1 / 6)
                                              & (df.emax_ZUSATZ - df.esig >= 0.15)].rho, 3))
                                for z in (0.02, 0.05, 0.1, 0.2)]))
gaps = [(a, b) for a, b in zip(rob[:-1], rob[1:]) if b - a > 0.0015]
p(f'  (Lücken im robusten Bereich: {", ".join(f"{a:.3f}–{b:.3f}" for a, b in gaps) if gaps else "keine"})')

# ── Hubfenster in mm für (f, μ), starrer Grenzfall und ρ = 0,05 bei ζ = 0,02 ─────────────────
p('\nHubfenster [Hub_sig, Hub_max] in mm (Spitze-Spitze) für Laufmenge ZUSATZ bzw. PFLICHT, M = 0,65 kg:')
rows = []
r_rig = df[df.rho == 0].iloc[0]
r_c = df[(df.zeta == 0.02) & np.isclose(df.rho, 0.05)].iloc[0]
p(f'{"f/Hz":>5}{"μ":>7}{"m_j/g":>7}{"K_min(ii)/kN/m":>15}{"starr ZUSATZ":>16}{"starr PFLICHT":>16}'
  f'{"ρ=0,05 ζ=0,02 ZUSATZ":>22}{"K(ρ=0,05)/kN/m":>16}')
for f in (8, 10, 12, 14, 16):
    for mu in (0.2308, 0.3462, 0.4615, 0.60, 0.6923):
        hs = mm.hub_of(r_rig.esig, mu, f) * 1e3
        hz = mm.hub_of(r_rig.emax_ZUSATZ, mu, f) * 1e3
        hp = mm.hub_of(r_rig.emax_PFLICHT, mu, f) * 1e3
        hs2 = mm.hub_of(r_c.esig, mu, f) * 1e3
        hz2 = mm.hub_of(r_c.emax_ZUSATZ, mu, f) * 1e3
        Kmin = mm.K_of_rho(1 / 6, f) / 1e3
        K05 = mm.K_of_rho(0.05, f) / 1e3
        rows.append(dict(f=f, mu=mu, m_modul_g=1e3 * mu * M / 3, K_min_ii=Kmin * 1e3, hub_sig_starr=hs,
                         hub_max_zusatz_starr=hz, hub_max_pflicht_starr=hp, hub_sig_r05z02=hs2,
                         hub_max_zusatz_r05z02=hz2, K_r05=K05 * 1e3))
        p(f'{f:>5}{mu:>7.3f}{1e3 * mu * M / 3:>7.0f}{Kmin:>15.0f}{hs:>7.2f} – {hz:>5.2f}{hs:>8.2f} – {hp:>5.2f}'
          f'{hs2:>13.2f} – {hz2:>5.2f}{K05:>16.0f}')
pd.DataFrame(rows).to_csv(os.path.join(HERE, 'a3b_hubfenster.csv'), index=False, float_format='%.5g')


# ── Arbeitspunktvorschläge ──────────────────────────────────────────────────
def evaluate_point(mu, hub, f, K, zeta):
    C = mm.C_of_zeta(zeta, K)
    res = {}
    rts = mm.run_types(pair_step=5.0)
    vals = {}
    for name, grp, ph, w in rts:
        r = mm.linear_run(ph, w, mu, hub, f, K, C)
        vals.setdefault(grp, []).append((name, r))
    for grp, lst in vals.items():
        j = int(np.argmin([r['F_min'] for _, r in lst]))
        res[f'res_{grp}'] = lst[j][1]['F_min'] / MG
        res[f'Fmax_{grp}'] = max(r['F_max'] for _, r in lst)
        res[f'valid_{grp}'] = all(r['valid'] for _, r in lst)
    sec = [r for _, r in vals['schnitt']]
    fmin = np.array([r['F_min'] for r in sec])
    kb = int(np.floor(mm.f_n(K) / (2 * f)))
    fbl = np.array([mm.linear_run((0, q, 240), (1, 1, 1), mu, hub, f, K, C, k_max=kb)['F_min'] for q in mm.SECTION_PHI2])
    fk3 = np.array([mm.linear_run((0, q, 240), (1, 1, 1), mu, hub, f, K, C, k_max=3)['F_min'] for q in mm.SECTION_PHI2])
    D = [max(abs(r['Nk'][k]) for r in sec) for k in range(3)]
    res.update(eps=mm.eps_of(mu, hub, f), fn=mm.f_n(K), r3=3 * f / mm.f_n(K), C=C, kb=kb,
               F120=fmin[10], dF=fmin.max() - fmin.min(), dF_bl=fbl.max() - fbl.min(), dF_k3=fk3.max() - fk3.min(),
               sL=(fmin[10] - fmin[9]) / 2, sR=(fmin[10] - fmin[11]) / 2, peak=mm.SECTION_PHI2[fmin.argmax()],
               peak_bl=mm.SECTION_PHI2[fbl.argmax()], D1=D[0], D2=D[1], D3=D[2],
               skew120=sec[10]['skew'])
    res['uc_Fmin_inf'] = 0.25 * res['dF'] / C_INF
    res['uc_Fmin_19'] = 0.25 * res['dF'] / C_19
    res['uc_Nk_inf'] = 0.25 * min(D) / C_INF
    res['uc_Nk_19'] = 0.25 * min(D) / C_19
    allmax = max(res[f'Fmax_{g}'] for g in ('schnitt', 'pilot', 'einzel', 'zweiergruppe', 'synchron', 'paar'))
    res['cell_max_sum3'] = allmax / 3
    res['cell_max_pflicht_sum3'] = max(res[f'Fmax_{g}'] for g in ('schnitt', 'pilot', 'einzel')) / 3
    res['cell_max_A25'] = res['Fmax_synchron'] / 3
    return res


VORSCHLAEGE = [
    ('V1 Laborplan-Mitte, steif', 0.4615, 8.0e-3, 10.0, 1.5e6, 'ZUSATZ'),
    ('V2 Referenzhub, 12 Hz, steif', 0.40, mm.HUB_REF, 12.0, 2.5e6, 'ZUSATZ'),
    ('V3 leichte Module 3x50 g, 14 Hz', 0.2308, 8.0e-3, 14.0, 3.0e6, 'ZUSATZ'),
    ('V4 weicher Kontakt (Pad), rho~0,09', 0.4615, 8.0e-3, 10.0, 3.2e5, 'ZUSATZ'),
    ('V5 nur PFLICHT, Wirkung im Zentrum', 0.60, mm.HUB_REF, 12.0, 2.5e6, 'PFLICHT'),
]
rows = []
for name, mu, hub, f, K, lset in VORSCHLAEGE:
    for zeta in (0.02, 0.05, 0.1):
        r = evaluate_point(mu, hub, f, K, zeta)
        r.update(name=name, mu=mu, m_modul_g=1e3 * mu * M / 3, hub_mm=1e3 * hub, f=f, K=K, zeta=zeta, laufmenge=lset)
        r['Z_set'] = r['cell_max_pflicht_sum3'] if lset == 'PFLICHT' else r['cell_max_sum3']
        rows.append(r)
V = pd.DataFrame(rows)
V.to_csv(os.path.join(HERE, 'a3b_vorschlaege.csv'), index=False, float_format='%.6g')
p('\nArbeitspunktvorschläge (lineares Modell, volles Spektrum für Reserven; M = 0,65 kg):')
p(f'{"Vorschlag":<36}{"ζ":>5}{"μ":>6}{"Hub":>6}{"f":>4}{"K/kN/m":>8}{"f_n":>7}{"3f/fn":>6}{"ε":>6}'
  f'{"Einz":>6}{"Paar":>6}{"Syn":>6}{"0/180":>6}{"Pil":>6}{"Schn":>6}{"ΔF_Z":>7}{"ΔF_bl":>7}{"s_L":>7}{"s_R":>7}'
  f'{"Sp.":>5}{"u_c,F":>7}{"u_c,Nk":>7}{"Z_max":>6}{"Z_A25":>6}')
for _, r in V.iterrows():
    p(f'{r["name"]:<36}{r.zeta:>5}{r.mu:>6.3f}{r.hub_mm:>6.2f}{r.f:>4.0f}{r.K / 1e3:>8.0f}{r.fn:>7.1f}{r.r3:>6.3f}'
      f'{r.eps:>6.3f}{100 * r.res_einzel:>5.0f}%{100 * r.res_paar:>5.0f}%{100 * r.res_synchron:>5.0f}%'
      f'{100 * r.res_zweiergruppe:>5.0f}%{100 * r.res_pilot:>5.0f}%{100 * r.res_schnitt:>5.0f}%{r.dF:>7.3f}'
      f'{r.dF_bl:>7.3f}{r.sL:>7.4f}{r.sR:>7.4f}{r.peak:>5.0f}{r.uc_Fmin_inf:>7.4f}{r.uc_Nk_inf:>7.4f}'
      f'{r.Z_set:>6.2f}{r.cell_max_A25:>6.2f}')
p('Spalten: Reserven = kleinstes F_min/Mg je Lauftyp (Zelle = Summe/3; „Syn“ ist zugleich die Zellreserve aller '
  'Läufe im Zellmodell A2.5); ΔF_Z = ΔF_Zelt voll, ΔF_bl bandbegrenzt k ≤ k_b; s_L, s_R = 2°-Sekanten [N/°]; '
  'Sp. = Lage der Zeltspitze [°]; u_c,F bzw. u_c,Nk = PB1-Anforderung für F_min bzw. min_k Re/Im N_k (ν→∞) [N]; '
  'Z_max = größte Zellkraft der Läufe der Laufmenge (V5: PFLICHT, sonst ALLE; Summe/3) [N]; Z_A25 = größte Zellkraft im Modell A2.5 = F_max,syn/3 [N]; '
  f'statische Zelllast {MG / 3:.4f} N.')

# ── Robustheit: K ± 30 %, ζ ∈ {0,02; 0,05; 0,1; 0,2} ────────────────────────
p('\nRobustheit je Vorschlag über K ∈ [0,7; 1,3]·K_nenn (Schritt 0,05) und ζ ∈ {0,02; 0,05; 0,1; 0,2}:')
p('  schlechtester Wert von: Reserve der Laufmenge, ΔF_Zelt (voll), u_c,F; Lage der Zeltspitze (Menge der Werte)')
rrows = []
for name, mu, hub, f, K, lset in VORSCHLAEGE:
    worst_res, worst_dF, peaks, worst_r3 = 9.0, 9.0, set(), 0.0
    for kf in np.arange(0.7, 1.3001, 0.05):
        for zeta in (0.02, 0.05, 0.1, 0.2):
            Kx = K * kf
            C = mm.C_of_zeta(zeta, Kx)
            grp = SETS[lset]
            mins = []
            for nm, g, ph, w in mm.run_types(pair_step=15.0):
                if g in grp:
                    mins.append(mm.linear_run(ph, w, mu, hub, f, Kx, C)['F_min'] / MG)
            fmin = np.array([mm.linear_run((0, q, 240), (1, 1, 1), mu, hub, f, Kx, C)['F_min'] for q in mm.SECTION_PHI2])
            worst_res = min(worst_res, min(mins))
            worst_dF = min(worst_dF, fmin.max() - fmin.min())
            peaks.add(float(mm.SECTION_PHI2[fmin.argmax()]))
            worst_r3 = max(worst_r3, 3 * f / mm.f_n(Kx))
            rrows.append(dict(name=name, kf=kf, zeta=zeta, res=min(mins), dF=fmin.max() - fmin.min(),
                              peak=mm.SECTION_PHI2[fmin.argmax()], r3=3 * f / mm.f_n(Kx)))
    p(f'  {name:<36} Reserve ≥ {100 * worst_res:5.1f} %  ΔF_Zelt ≥ {worst_dF:.3f} N  u_c,F ≥ {0.25 * worst_dF / C_INF:.4f} N  '
      f'Spitze ∈ {sorted(peaks)}  3f/f_n ≤ {worst_r3:.3f}')
pd.DataFrame(rrows).to_csv(os.path.join(HERE, 'a3b_robustheit.csv'), index=False, float_format='%.6g')

with open(os.path.join(HERE, 'a3b_arbeitspunkte_ausgabe.txt'), 'w') as fh:
    fh.write('\n'.join(out) + '\n')
