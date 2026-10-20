# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 und 5.4.
# Zweck: Verteilung der S1-Halte (und der Halte im W-Satz) je Kampagne bei geschätztem σ̂_ref bzw. σ̂_betr für die
#   Phase-0-Varianten gen_F (61 R mit F-Test), A8 (42 R ohne F-Test), A8_F (42 R mit F-Test), chi41, fest.
# Eingaben: Argument 1 = dieser Ordner (phase0.py, phase1.py, gitter.json; die Ausgabe wird dorthin geschrieben),
#   2 = Zahl der Kampagnen, 3 = Varianten (Komma), 4 = "streng" (Halt bei jedem Nullpunktalarm im W-Satz wie
#   ablauf-3) oder "mild", 5 = Seed.
# Annahmen: wie phase0.py/phase1.py; kritische Werte des F-Tests aus je 200 000 Nulldatensätzen.
# Seeds der übernommenen Ausgaben: 101 gen_F, 102 A8, 103 chi41, 104 fest, 105 A8_F (alle "streng", N = 20 000).
# Laufzeit: je Variante 107–111 s für die Kampagnen (Feld "sekunden"), dazu die beiden F-Test-Nullsimulationen.
# Aufruf: python3 -B s1_verteilung.py . 20000 gen_F streng 101   (analog A8 102, chi41 103, fest 104, A8_F 105)
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""S1-Halte je Kampagne (mit Wiederaufnahme ohne Befund, unbegrenzt) bei geschätztem σ̂_ref bzw. σ̂_betr.

Varianten der Phase-0-Schätzung (σ = 1):
  gen_F   : Generator-Layout (61 Referenzläufe, je zwei andere dazwischen), F-Test A9.8, ε = 3·σ̂_ref oder 3·σ̂_betr
  A8      : 42 Referenzläufe, ε = 3·σ̂_ref (Annahmen von Anhang A8, ohne F-Test)
  A8_F    : 42 Referenzläufe mit F-Test
  chi41   : σ̂_ref²/σ²_LOO ~ χ²₄₁/41 für Summe und Zellen unabhängig (Annahme des Berichts b-vollständigkeit)
  fest    : σ̂ ohne Schätzfehler (u = 1)
Phase 1: Plan von PR #23 (N_K = 21, n = 24, ein Messtag, 630 geplante Läufe); optional 688er-Plan.
Ausgabe: direkte Simulation (Mittel, Varianz, Dispersionsindex, P(≥k)) und gemischte Poisson-Näherung für P(≥4).
"""
import sys, json, math, random, time
import numpy as np
from scipy.stats import norm, poisson, chi2
sys.path.insert(0, sys.argv[1])
import phase0 as p0, phase1 as p1

N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
STRENG = len(sys.argv) > 4 and sys.argv[4] == 'streng'
SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 20261019
rng = np.random.default_rng(SEED)
rnd = random.Random(SEED)
KRIT = {}


def phase0_variante(name, n):
    if name == 'gen_F':
        o = p0.simuliere(n, rng, 61, 2, True, krit=KRIT['gen'])
    elif name == 'A8':
        o = p0.simuliere(n, rng, 42, 2, False)
    elif name == 'A8_F':
        o = p0.simuliere(n, rng, 42, 2, True, krit=KRIT['a8'])
    elif name == 'chi41':
        u = np.sqrt(chi2.rvs(41, size=(n, 4), random_state=rng) / 41)
        o = dict(sref=np.sqrt(1.5) * u[:, 0], sref_c=np.sqrt(0.5) * u[:, 1:], betr=np.zeros(n, bool))
        o['eps'] = 3 * o['sref']
    elif name == 'fest':
        o = dict(sref=np.full(n, np.sqrt(1.5)), sref_c=np.full((n, 3), np.sqrt(0.5)), betr=np.zeros(n, bool))
        o['eps'] = 3 * o['sref']
    return o


# kritische Werte des F-Tests einmal aus der Nullsimulation (wie pilot.eps_ctrl_test, 200 000 Datensätze)
KRIT['gen'] = p0.simuliere(200000, rng, 61, 2, True)['krit']
KRIT['a8'] = p0.simuliere(200000, rng, 42, 2, True)['krit']


def p2(u):
    """Reproduzierter Nullpunktalarm je Referenzlauf und Kanal bei Schwelle 3·√(4/3)·σ̂ (σ̂ = √1,5·σ·u)."""
    z = np.linspace(-8, 8, 4001); w = norm.pdf(z) * (z[1] - z[0])
    tau = 3 * math.sqrt(2) * np.atleast_1d(u)[:, None]
    pz = norm.cdf(z - tau) + norm.cdf(-z - tau)
    return (pz ** 2 * w).sum(1)


plan = p1.plan()
erg = {'krit': KRIT, 'N': N}
gitter = json.load(open(sys.argv[1] + '/gitter.json'))
F = gitter['felder']; gu = np.array([float(x) for x in gitter['gitter']])
GM = np.array([gitter['gitter'][k]['mittel'] for k in gitter['gitter']])
lam_X = lambda u: np.exp(np.interp(np.clip(u, 0.7, 1.3), gu, np.log(np.maximum(GM[:, F.index('S1X')], 1e-7))))
nref = lambda u: np.interp(np.clip(u, 0.7, 1.3), gu, GM[:, F.index('nref')])

for name in sys.argv[3].split(','):
    t0 = time.time()
    o = phase0_variante(name, N)
    u_eps = o['eps'] / (3 * np.sqrt(1.5)); u_ref = o['sref'] / np.sqrt(1.5); u_c = o['sref_c'] / np.sqrt(0.5)
    z = np.array([p1.kampagne(o['eps'][i], o['sref'][i], list(o['sref_c'][i]), rnd, plan, streng=STRENG) for i in range(N)], float)
    s1 = z[:, F.index('S1X')] + z[:, F.index('S1A')]
    wa = z[:, -1]
    h = s1 + wa
    m, v = s1.mean(), s1.var()
    r = dict(anteil_betr=float(o['betr'].mean()), sd_u_eps=float(u_eps.std()),
             mittel_S1=float(m), var_S1=float(v), dispersion=float(v / m) if m > 0 else None,
             mittel_S1X=float(z[:, F.index('S1X')].mean()), mittel_S1A=float(z[:, F.index('S1A')].mean()),
             mittel_G1f=float(z[:, F.index('G1f')].mean()), mittel_R1=float(z[:, F.index('R1')].mean()),
             mittel_alarm=float(z[:, F.index('alarm')].mean()),
             P_direkt={str(k): float((s1 >= k).mean()) for k in (1, 2, 3, 4)},
             n_direkt={str(k): int((s1 >= k).sum()) for k in (1, 2, 3, 4)},
             halte_mit_WA=dict(mittel=float(h.mean()), var=float(h.var()), dispersion=float(h.var() / h.mean()) if h.mean() > 0 else None,
                               mittel_WA=float(wa.mean()), P={str(k): float((h >= k).mean()) for k in (1, 2, 3, 4)},
                               n={str(k): int((h >= k).sum()) for k in (1, 2, 3, 4)}),
             P_zweiter_halt_gegeben_erster=float((h >= 2).mean() / max((h >= 1).mean(), 1e-12)))
    # gemischte Poisson-Näherung: λ = λ_X(u_ε) + n_ref(u_ε)·Σ_Kanal p2(u_Kanal)
    lam = lam_X(u_eps) + nref(u_eps) * (p2(u_ref) + p2(u_c[:, 0]) + p2(u_c[:, 1]) + p2(u_c[:, 2]))
    r['mischung'] = dict(mittel=float(lam.mean()), var_lambda=float(lam.var()),
                         dispersion=float(1 + lam.var() / lam.mean()),
                         P={str(k): float(poisson.sf(k - 1, lam).mean()) for k in (1, 2, 3, 4, 5)})
    lh = lam.mean()
    r['homogen_gleiches_mittel'] = {str(k): float(poisson.sf(k - 1, lh)) for k in (1, 2, 3, 4, 5)}
    # Wer hält? Anteil der Halte aus Kampagnen mit u_ε < 0,85 bzw. unterstem Zehntel
    q10 = np.quantile(u_eps, 0.1)
    r['anteil_halte_u_lt_0.85'] = float(s1[u_eps < 0.85].sum() / max(s1.sum(), 1))
    r['anteil_kampagnen_u_lt_0.85'] = float((u_eps < 0.85).mean())
    r['anteil_halte_unterstes_zehntel_u'] = float(s1[u_eps <= q10].sum() / max(s1.sum(), 1))
    r['rang_spearman_u_S1'] = float(np.corrcoef(np.argsort(np.argsort(u_eps)), np.argsort(np.argsort(s1)))[0, 1])
    r['sekunden'] = round(time.time() - t0, 1)
    erg[name] = r
    print(name, json.dumps(r, ensure_ascii=False), flush=True)
json.dump(erg, open(sys.argv[1] + f'/s1_verteilung_{sys.argv[3].replace(",", "_")}_{"streng" if STRENG else "mild"}_{SEED}.json', 'w'), indent=1, ensure_ascii=False)
