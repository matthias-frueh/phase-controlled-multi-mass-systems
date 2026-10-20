# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 2.2 (Option F) und 3.1 (G4-Halte an Lⱼ).
# Zweck: empirische G4-Raten je L-Lauf und Kontroll-R, Streuung über Kampagnen, Selektion durch Halte,
#   Neukalibrierung des Normal-MAD-Modells (Skalenfaktor κ), Varianten (Pooling, n₀ = 40, k(20)).
# Eingaben: Argument 1 = g4L_daten.json (Standard: hier; aus g4L_daten.py).
# Seed: default_rng(20261019). Laufzeit: gemessen 66 s Wandzeit, 65 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B g4L_kalib.py > g4L_kalib.out
# Herkunft: Nachprüfung 2 (G4 an Lⱼ). Geändert: Pfad von g4L_daten.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# Nur lesen. G4 an Kontrollläufen: empirische Raten je L-Lauf und Kontroll-R aus gespeicherten Befunden
# (PR #22: statischer Plan, 40 Kampagnen je System; PR #23: zustandsbehafteter Ablauf, 10 je System, gleiche Seeds),
# Streuung über Kampagnen, Selektion durch Halte, Neukalibrierung des Normal-MAD-Modells (Skalenfaktor κ).
import json, collections, os, sys
import numpy as np
from scipy import stats, optimize

DATEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4L_daten.json')
D = json.load(open(DATEN)); d22, d23 = D['d22'], D['d23']
SYS = ('N01-A4', 'N01-V1G0', 'N01-V1G60h')
rng = np.random.default_rng(20261019)
c = 1.4826


def mads(n, shape):
    x = rng.standard_normal(tuple(shape) + (n,))
    return c * np.median(np.abs(x - np.median(x, -1, keepdims=True)), -1)


def garwood(k, a=0.05):
    lo = 0.0 if k == 0 else stats.chi2.ppf(a / 2, 2 * k) / 2
    return lo, stats.chi2.ppf(1 - a / 2, 2 * k + 2) / 2


def kw(b, art):
    an = b['ablauf']['anlaesse']
    return sum(v for k, v in an.items() if k.startswith('kontrollwiederholung') and art in k)


keys = sorted(d23, key=lambda s: (s.split('|')[0], int(s.split('|')[1])))
print('1) PR #23 je Kampagne (ablauf-2, mit Wiederholungen) und PR #22 statisch (gleicher Seed)')
print('   Kampagne       Status/Halt   Kontr. kwdh_G4 kwdh_Alarm nichtK_G4 R_außerhalb | PR22 nichtK_G4 (126) | PR22 vorh.|σ̂')
T = []
for k in keys:
    b = d23[k]; a = b['ablauf']; r = a['rollen']; p1 = b['phase1']
    nonk = p1['regeln'].get('G4', 0) - p1['konfig_g4']
    Raus = sum(r.get(x, 0) for x in ('referenz_block', 'schlussreferenz', 'aufwaermen', 'R1', 'R2', 'R3', 'alarmwiederholung'))
    halt = a['halt']['regel'] if isinstance(a['halt'], dict) else None
    T.append(dict(k=k, sys=k.split('|')[0], i=int(k.split('|')[1]), fertig=a['status'] == 'abgeschlossen', halt=halt,
                  kontrolle=r.get('kontrolle', 0), kg4=kw(b, 'G4'), kal=kw(b, 'Nullpunktalarm'), nonk=nonk, Raus=Raus,
                  s22=d22[k]['phase1']['sonstige_ungueltig']['G4'], eps=b['teil_b']['eps_ctrl'],
                  seed_gleich=d22[k]['seed'] == b['seed']))
for t in T:
    print(f"   {t['k']:14s} {('fertig' if t['fertig'] else 'Halt ' + str(t['halt'])):12s} {t['kontrolle']:5d} {t['kg4']:6d} "
          f"{t['kal']:8d} {t['nonk']:9d} {t['Raus']:8d}    | {t['s22']:4d}")
assert all(t['seed_gleich'] for t in T)
print('   Halte nach Regel:', collections.Counter(t['halt'] for t in T if not t['fertig']))
F = [t for t in T if t['fertig']]
print(f"   Summen: kwdh_G4 alle {sum(t['kg4'] for t in T)}, abgeschlossen {sum(t['kg4'] for t in F)}; "
      f"kwdh_Alarm {sum(t['kal'] for t in T)}; nichtK_G4 {sum(t['nonk'] for t in T)}")
x = np.array([t['kg4'] for t in F])
print(f"   abgeschlossene (25): je Kampagne {sorted(collections.Counter(x).items())}, Mittel {x.mean():.2f}, Var {x.var(ddof=1):.2f}")

print('\n2) Referenzläufe: G4-Rate (nur ⟨N⟩, σ̂_Δ,R aus 61 Phase-0-Referenzläufen)')
kR = sum(t['nonk'] - t['kg4'] for t in T); nR = sum(t['Raus'] for t in T)
lo, hi = garwood(kR)
qR_emp = kR / nR
print(f"   PR #23, R außerhalb der Kontrollsätze (nicht wiederholt, ablauf.py Z. 390–396): {kR} G4 in {nR} Läufen = "
      f"{100*qR_emp:.2f} % [95 %: {100*lo/nR:.3f}; {100*hi/nR:.2f} %]")
m61 = mads(61, (400000,))
qR_mod = float(np.mean(2 * stats.norm.sf(3 * m61)))
print(f"   Normal-MAD-Modell (n = 61, unbedingt): {100*qR_mod:.3f} % je Lauf")
for s in SYS[1:]:
    ff = [t for t in F if t['sys'] == s]
    print(f"   {s}, abgeschlossene: PR22 statisch (75 L + 51 R) {sum(t['s22'] for t in ff)}, PR23 kwdh_G4 (L + Kontroll-R) "
          f"{sum(t['kg4'] for t in ff)}, PR23 nichtK_G4 {sum(t['nonk'] for t in ff)}")
nKR = sum(t['kontrolle'] / 4 for t in T); nKRf = sum(t['kontrolle'] / 4 for t in F)
for lab, q in (('empirisch', qR_emp), ('Modell', qR_mod)):
    print(f"   erwartete Kontroll-R unter den G4-Kontrollwiederholungen ({lab}, {100*q:.2f} %): alle 30: "
          f"{q*nKR:.2f} von 55 ({nKR:.0f} Kontroll-R), abgeschlossene: {q*nKRf:.2f} von 41; "
          f"Poisson-P(≥ 1) {1-np.exp(-q*nKR):.2f}")

print('\n3) G4-Rate je L-Lauf (Original, D_N oder D_F)')
res = {}
for s in SYS:
    if s != 'N01-A4':
        o = np.array([d22[f'{s}|{i}']['phase1']['sonstige_ungueltig']['G4'] for i in range(40)])
        for lab, q in (('R empirisch', qR_emp), ('R Modell', qR_mod)):
            L = o.sum() - 40 * 51 * q
            rate = L / 3000
            se = np.sqrt(o.var(ddof=1) * 40) / 3000
            print(f"   {s}, PR #22 (40 Kampagnen, je 75 L + 51 R, nicht selektiert): G4 {o.sum()}, abzüglich R ({lab}) "
                  f"{L:.1f} → {100*rate:.2f} % je L-Lauf (± {100*se:.2f} % SE aus Kampagnenstreuung)")
            res.setdefault(s, {})[lab] = rate
    ts = [t for t in T if t['sys'] == s]
    nL = sum(0.75 * t['kontrolle'] for t in ts); g = sum(t['kg4'] for t in ts); nKR_s = sum(t['kontrolle'] / 4 for t in ts)
    lo, hi = garwood(g)
    print(f"   {s}, PR #23 (10 Kampagnen, Exposition {nL:.0f} geplante L): kwdh_G4 {g} → {100*(g - qR_emp*nKR_s)/nL:.2f} % je L-Lauf "
          f"(R empirisch abgezogen; Poisson-95 % der Rohrate [{100*lo/nL:.2f}; {100*hi/nL:.2f} %])")
    if s == 'N01-A4':
        res[s] = {'R empirisch': (g - qR_emp * nKR_s) / nL}

print('\n4) Streuung über die Kampagnen (PR #22, Zählung je Kampagne der 126 Nicht-K-Läufe)')
m20 = mads(20, (400000,))
for s in SYS[1:]:
    o = np.array([d22[f'{s}|{i}']['phase1']['sonstige_ungueltig']['G4'] for i in range(40)])
    v_l = max(o.var(ddof=1) - o.mean(), 0)
    print(f"   {s}: Mittel {o.mean():.2f}, Var {o.var(ddof=1):.2f}, Dispersionsindex {o.var(ddof=1)/o.mean():.2f}; "
          f"SD der Kampagnenrate (Momente) {np.sqrt(v_l):.2f} Läufe ≈ {100*np.sqrt(v_l)/75:.2f} %-Punkte je L-Lauf")
    # Bootstrap der Kampagnen für den Dispersionsindex
    bs = np.array([(lambda y: y.var(ddof=1) / y.mean())(rng.choice(o, 40)) for _ in range(4000)])
    print(f"      Bootstrap-90-% des Dispersionsindex [{np.quantile(bs, 0.05):.2f}; {np.quantile(bs, 0.95):.2f}]")
# Modell: Dispersion je Kampagne (75 L + 51 R, statisch)
aN, aF, r = mads(20, (100000, 3)), mads(20, (100000, 3)), mads(61, (100000,))
pj = 1 - (1 - 2 * stats.norm.sf(3 * aN)) * (1 - 2 * stats.norm.sf(3 * aF))
lam = 25 * pj.sum(1) + 51 * 2 * stats.norm.sf(3 * r)
cnt = rng.poisson(lam)
print(f"   Normal-MAD-Modell (κ = 1): Mittel {cnt.mean():.2f}, Var {cnt.var():.2f}, Dispersionsindex {cnt.var()/cnt.mean():.2f}, "
      f"SD der Kampagnenrate {lam.std():.2f} Läufe")

print('\n5) Selektion: G4-Zählung (PR #22, gleiche Seeds) nach Ausgang der PR-#23-Kampagne (nur V1, Phase 0 bitgleich)')
for s in SYS[1:]:
    ts = [t for t in T if t['sys'] == s]
    a_ = [t['s22'] for t in ts if t['fertig']]; h_ = [t['s22'] for t in ts if not t['fertig']]
    print(f"   {s}: abgeschlossen {a_} (Mittel {np.mean(a_):.2f}); angehalten {h_} (Mittel {np.mean(h_):.2f})")
v1 = [t for t in T if t['sys'] != 'N01-A4']
a_ = [t['s22'] for t in v1 if t['fertig']]; h_ = [t['s22'] for t in v1 if not t['fertig']]
print(f"   V1 gesamt: Mann-Whitney (angehalten > abgeschlossen) p = {stats.mannwhitneyu(h_, a_, alternative='greater').pvalue:.3f}")
o40 = np.concatenate([[d22[f'{s}|{i}']['phase1']['sonstige_ungueltig']['G4'] for i in range(40)] for s in SYS[1:]])
print(f"   zum Vergleich PR #22 V1, alle 80: Mittel {o40.mean():.2f}; Seeds 0–9: {np.mean([t['s22'] for t in v1]):.2f}")
# ε_ctrl und σ̂_L gegen Ausgang
for s in SYS:
    ts = [t for t in T if t['sys'] == s]
    sl = [np.mean([d22[t['k']]['sigma_delta'][g]['N'] for g in ('L1', 'L2', 'L3')]) for t in ts]
    eps = [t['eps'] for t in ts]
    print(f"   {s}: Spearman(ε_ctrl, mittleres σ̂_N,L) {stats.spearmanr(eps, sl)[0]:+.2f}; ε_ctrl angehalten "
          f"{[round(1e3*t['eps'],3) for t in ts if not t['fertig']]} mN, abgeschlossen Median {1e3*np.median([t['eps'] for t in ts if t['fertig']]):.3f} mN")

print('\n6) Neukalibrierung: Skalenfaktor κ in P(|D| > 3·σ̂) = 2·Φ(−3·κ·σ̂/σ) (κ = 1: Normalmodell b-g4)')
aN, aF = mads(20, (200000, 3)), mads(20, (200000, 3))


def rate_L(kap, aN=aN, aF=aF, fak=3.0):
    return 1 - (1 - 2 * stats.norm.sf(fak * kap * aN)) * (1 - 2 * stats.norm.sf(fak * kap * aF))


ziel = {s: res[s]['R empirisch'] for s in SYS}
ziel['V1 gepoolt'] = (res['N01-V1G0']['R empirisch'] + res['N01-V1G60h']['R empirisch']) / 2
kap = {}
for s, z in ziel.items():
    kap[s] = optimize.brentq(lambda k: rate_L(k).mean() - z, 0.5, 2.0)
    print(f"   {s}: Zielrate {100*z:.2f} % je L-Lauf → κ = {kap[s]:.3f}")
print(f"   κ = 1 (b-g4): {100*rate_L(1.0).mean():.2f} % je L-Lauf")


def kennzahlen(kap, n=20, pool=False, fak=3.0, B=200000, L=25):
    if pool:
        sN = np.repeat(mads(3 * n, (B,))[:, None], 3, 1); sF = np.repeat(mads(3 * n, (B,))[:, None], 3, 1)
    else:
        sN, sF = mads(n, (B, 3)), mads(n, (B, 3))
    p = rate_L(kap, sN, sF, fak)
    halt = 1 - np.prod((1 - p ** 3) ** L, 1)
    wied = (L * (p + p ** 2)).sum(1)
    return 100 * p.mean(), 100 * np.quantile(p, 0.9), wied.mean(), 100 * halt.mean()


print('   Varianten (25 Kontrollsätze, L₁–L₃; Kontroll-R nicht enthalten):')
print('   κ-Quelle            Variante                    Rate/L   90-%-Q.  Wdh./Kampagne  P(G4-Halt an Lⱼ)/Kampagne')
for s in ('b-g4 (κ = 1)', 'N01-V1G0', 'N01-V1G60h', 'N01-A4', 'V1 gepoolt'):
    k_ = 1.0 if s.startswith('b-g4') else kap[s]
    for lab, kwargs in (('n₀ = 20 je Modul', {}), ('gepoolt n = 60', dict(pool=True)), ('n₀ = 40 je Modul', dict(n=40)),
                        ('k(20) = 4,33', dict(fak=4.33))):
        r_, q_, w_, h_ = kennzahlen(k_, **kwargs)
        print(f"   {s:18s}  {lab:24s}  {r_:5.2f} %  {q_:6.2f} %  {w_:6.2f}         {h_:6.3f} %")

print('\n7) Wirkung einer Korrelation ρ von D_N und D_F auf die Rate je L-Lauf (κ = 1, n₀ = 20)')
sN, sF = mads(20, (20000,)), mads(20, (20000,))
for rho in (0.0, 0.3, 0.6):
    cov = [[1, rho], [rho, 1]]
    z = rng.multivariate_normal([0, 0], cov, size=(20000, 200))
    p = np.mean((np.abs(z[..., 0]) > 3 * sN[:, None]) | (np.abs(z[..., 1]) > 3 * sF[:, None]), 1)
    print(f"   ρ = {rho:.1f}: Rate je L-Lauf {100*p.mean():.2f} %")
