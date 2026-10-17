"""Auswertung und Bericht der Diagnose E3b/G4 (harness.diagnose_e3b_g4).

E3: Nachzählung der 570 Kampagnen der Neuläufe aus dem versionierten Auszug (e3_pruefgroessen.csv), Trennung nach
E3a und E3b, Zerlegung der Bedingung „unauffällig“ für E3b, Simulation eines komplexen Nullresiduums und eine
nachträgliche, nur beschreibende Sensitivität von q_tol auf denselben Kampagnen.

G4: je Kampagne und Konfiguration die Verletzungen durch D_N und D_F, G4 insgesamt, nur G4 und andere Regeln; gültige
Läufe, kleinster Bestand und Vollständigkeit der 21 Schnittpunkte ohne und mit Wiederholungen (A9.12), bei n = 24 und
gekürzt auf n = n_min + r(p̂); dieselben Größen für Varianten der Schwelle, die nur hier gerechnet werden:
  v0  produktiv: σ_Δ,F gepoolt über die Piloten bei k der Pilotgrößen (A4: k_b = 30), wie Teil B;
  v0k k-konsistent: dieselben Piloten bei k_max (Prüfgröße der Phase 1);
  v1  gezielter Pilot: σ_Δ,F aus den 20 Läufen des Zielpiloten, für alle Konfigurationen;
  v2  Standardisierung aus Phase 0: σ²_F,i = σ²_P + max(0, s²_i − mittel_p s²_p), σ_P wie v0k, s die aus Phase 0
      vorhergesagte Jitterstreuung von D_F an Konfiguration i bzw. den Piloten p;
  v3  Orakel: 1,4826·MAD(D_F) je Konfiguration über alle 40 Kampagnen des Systems (nur Illustration, kein
      verfügbares Messverfahren).
σ_Δ,N, Faktor 3 und Rundungsboden bleiben in allen Varianten produktiv; andere Regeln (auch G1) hängen nicht von G4 der
Kombinationsläufe ab. Dazu Reserve „+2“ gegen eine Reserve für die gemeinsame Vollständigkeit (Binomialnäherung,
gekennzeichnet), die direkte Zählung je Kampagne und ein kontrollierter Trendfall (Amplitudentrend im letzten
Fünftel, exakt über die Homogenität von F_min − ⟨N⟩; Nullpunkttrend in D_N).

Außerhalb des Rechencode-Hashes: Korrekturen hier wiederholen keine Rechnung.
"""
import csv
import json
import math
import os

import numpy as np
from scipy import stats

from .. import formate, gueltigkeit, konventionen as kv, pilot
from . import diagnose_e3b_g4 as dg, neulauf, neulauf_vergleich

VARIANTEN = ('v0', 'v0k', 'v1', 'v2', 'v3')
NAMEN = dict(v0='produktiv', v0k='k-konsistent', v1='gezielter Pilot', v2='Standardisierung aus Phase 0',
             v3='Orakel (Illustration)')
N_MIN = 18
N_BLOECKE = 24
PUNKTE = 21
STEIL = ('S114', 'S116', 'S118')
FLACH = ('S130', 'S132', 'S134', 'S136', 'S138', 'S140')
TREND_EPS = (0.0, 0.002, 0.005, 0.01)                   # Amplitudentrend zwischen erstem und letztem Fünftel
NULLPUNKT_N = (0.0, 0.5e-3, 1.0e-3, 2.0e-3)              # Nullpunkttrend [N] in D_N
ZIEL_VOLL = 0.95                                         # gemeinsame Vollständigkeit der Binomialnäherung
OBERE_GRENZE = 0.8                                       # einseitige obere Vertrauensgrenze von p̂ (wie A9.2 für s)
NULL_N, NULL_B, NULL_SEED = 20000, 1000, 20261017        # Nullresiduum: Kampagnen, Bootstrap-Replikate, Seed
QTOL_FAKTOREN = (1.0, 1.25, 1.5, 2.0, 2.5, 3.0)          # nachträgliche Sensitivität (nur beschreibend)
HISTORISCH = {'N01-A4': ('kalibrierung_a4', None, 0.023), 'N01-V1G0': ('kalibrierung_v1', 'V1-G0', 0.044),
              'N01-V1G60h': ('kalibrierung_v1', 'V1-G60h', 0.050)}   # G4-Anteil: Softwaredokument, Befund 1


# ── kleine Hilfen ─────────────────────────────────────────────────────────────────────────────────────────
def mad(x):
    x = np.asarray(x, float)
    return float(1.4826 * np.median(np.abs(x - np.median(x))))


def wilson(k, n, z=1.96):
    """95-%-Wilson-Intervall eines Anteils k/n (Kampagnen als unabhängige Einheiten)."""
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    m = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, m - h), min(1.0, m + h))


def r_plus2(p, n_min=N_MIN, reserve=2):
    """Reserve der Pilotanalyse r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 (A9.2, Profilwert planung.reserve)."""
    return int(math.ceil(n_min * p / (1 - p) - 1e-12)) + reserve


def obere_grenze(x, n, niveau=OBERE_GRENZE):
    """Einseitige obere Clopper-Pearson-Grenze eines Anteils x/n."""
    return 1.0 if x >= n else float(stats.beta.ppf(niveau, x + 1, n - x))


def p_vollstaendig(n, p, n_min=N_MIN, punkte=PUNKTE, wiederholungen=0):
    """Binomialnäherung (unabhängige Läufe, Rate p je Punkt; p skalar oder je Punkt): Wahrscheinlichkeit, dass alle
    Punkte mindestens n_min gültige Plätze haben; mit Wiederholungen fällt ein Platz mit p^(1 + w) aus."""
    q = np.broadcast_to(np.asarray(p, float), (punkte,)) ** (1 + wiederholungen)
    return float(np.prod(stats.binom.cdf(n - n_min, n, q)))


def r_gemeinsam(p, ziel=ZIEL_VOLL, wiederholungen=0, r_max=40):
    """Kleinste Reserve r mit p_vollstaendig(n_min + r, p) ≥ ziel (gleiche Rate an allen Punkten)."""
    for r in range(r_max + 1):
        if p_vollstaendig(N_MIN + r, p, wiederholungen=wiederholungen) >= ziel:
            return r
    return None


def block_nmin(ok, konf, block, n_min=N_MIN, punkte=PUNKTE):
    """Je Punkt der Block, mit dem n_min gültige Plätze erreicht sind (N_BLOECKE + 1: nie); Vollständigkeit bei n
    Blöcken heißt max ≤ n (Läufe je Konfiguration und Block: einer)."""
    out = np.full(punkte, N_BLOECKE + 1, int)
    for c in range(punkte):
        b = np.sort(block[(konf == c) & ok])
        if b.size >= n_min:
            out[c] = int(b[n_min - 1])
    return out


def _f(x, d=3):
    return '–' if x is None or (isinstance(x, float) and not np.isfinite(x)) else f'{x:.{d}f}'.replace('.', ',')


def _p(x, d=1):
    return _f(100 * x, d) + ' %'


def _kw(k, n):
    lo, hi = wilson(k, n)
    return f'{k}/{n} [{_f(lo, 2)}; {_f(hi, 2)}]'


# ── E3 ────────────────────────────────────────────────────────────────────────────────────────────────────
def lies_e3(a):
    p = os.path.join(neulauf.WURZEL, a['e3']['datei'])
    if formate.sha256_datei(p) != a['e3']['sha256']:
        raise dg.Fehler('E3-Auszug weicht von der Prüfsumme der Auftragsliste ab')
    with open(p, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def e3_klassen(r, sw, q_tol=None):
    """Dreiwertige Aussagen von E3a, E3b und E3 einer Kampagne nach A9.13 (aus dem Auszug)."""
    q_tol = sw['q_tol'] if q_tol is None else q_tol
    zB, q, u = float(r['z_B']), float(r['q_Z']), float(r['u_q_Z'])
    a_auf, a_un = int(r['e3a_auffaellig']) > 0, int(r['e3a_ueber_schwelle']) == 0
    b_auf, b_un = q - zB * u > q_tol, q + 1.645 * u <= q_tol
    drei = lambda au, un: 'auffällig' if au else ('unauffällig' if un else 'unbestimmt')            # noqa: E731
    return drei(a_auf, a_un), drei(b_auf, b_un), drei(a_auf or b_auf, a_un and b_un)


def _neulauf_h1z():
    """H1Z und H1 je Kampagne aus der versionierten Kampagnenübersicht der Neuläufe (PR #21, unverändert)."""
    with open(os.path.join(neulauf.WURZEL, 'docs/ap13_neulaeufe_2026-10-17/kampagnen_e3.csv'), encoding='utf-8') as f:
        return {(r['punkt'], r['kampagne']): (r['H1Z'], r['H1']) for r in csv.DictReader(f)}


def e3_auswertung(a):
    rows = lies_e3(a)
    sw = a['e3']['schwellen']
    grenze = sw['q_tol'] / 1.645
    h1z = _neulauf_h1z()
    reihe = [f'{x[0]}/{x[1]}' for x in neulauf.E3_AUSWAHL]
    if sorted(reihe) != sorted(a['e3']['punkte']):
        raise dg.Fehler('E3-Auszug: Punkte ≠ Auswahl der Neuläufe')
    punkte = []
    for p in reihe:
        R = [r for r in rows if r['punkt'] == p]
        if len(R) != a['e3']['punkte'][p]['n']:
            raise dg.Fehler(f'E3-Auszug {p}: Kampagnenzahl ≠ Herkunft')
        k = [e3_klassen(r, sw) for r in R]
        for r, (_, _, e) in zip(R, k):
            if e != r['bewertung']:
                raise dg.Fehler(f'E3 {p}/{r["kampagne"]}: Nachzählung „{e}“ ≠ gespeicherte Bewertung „{r["bewertung"]}“')
        zaehl = lambda j: {x: sum(1 for y in k if y[j] == x) for x in ('auffällig', 'unauffällig', 'unbestimmt')}  # noqa
        u = np.array([float(r['u_q_Z']) for r in R])
        u0 = np.array([float(r['u_q_Z_ohne_T']) for r in R])
        hz = [h1z[(p, r['kampagne'])][0] for r in R]
        punkte.append(dict(punkt=p, n=len(R), e3=zaehl(2), e3a=zaehl(0), e3b=zaehl(1),
                           nur_e3b=sum(1 for y in k if y[0] == 'unauffällig' and y[1] == 'unbestimmt'),
                           u_ueber_grenze=int((u > grenze).sum()),
                           m={str(m): sum(1 for r in R if int(r['m']) == m) for m in sorted({int(r['m']) for r in R})},
                           e3a_auffaellig_H1Z_bestaetigt=sum(1 for y, h in zip(k, hz) if y[0] == 'auffällig'
                                                            and h == 'bestätigt'),
                           e3b_auffaellig_H1Z_bestaetigt=sum(1 for y, h in zip(k, hz) if y[1] == 'auffällig'
                                                            and h == 'bestätigt'),
                           H1Z_bestaetigt=sum(1 for h in hz if h == 'bestätigt'),
                           zelllagen_rel_max=float(np.max(np.abs(u - u0) / u0))))
    R = [r for r in rows if r['punkt'] == 'N01-A4/L1']
    q = np.array([float(r['q_Z']) for r in R])
    u = np.array([float(r['u_q_Z']) for r in R])
    zB = np.array([float(r['z_B']) for r in R])
    ob = q + 1.645 * u
    qs = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
    rein = u > grenze
    a4 = dict(n=len(R), quantile=list(qs), q=np.quantile(q, qs).tolist(), u=np.quantile(u, qs).tolist(),
              ober=np.quantile(ob, qs).tolist(), grenze_u=grenze,
              e3a_max_ober_grad=np.quantile([float(r['e3a_max_ober_grad']) for r in R], qs).tolist(),
              zerlegung=dict(unsicherheit_allein=int(rein.sum()), punktschaetzer=int((~rein & (ob > sw['q_tol'])).sum()),
                             unauffaellig=int((ob <= sw['q_tol']).sum())),
              q_durch_u_median=float(np.median(q / u)), max_unter_durch_qtol=float(np.max(q - zB * u) / sw['q_tol']),
              s_rayleigh=float(np.sqrt(np.mean(q ** 2) / 2)), z_B=sorted(set(zB.tolist())),
              sensitivitaet=[dict(faktor=f, q_tol=f * sw['q_tol'], unauffaellig=int((ob <= f * sw['q_tol']).sum()),
                                  auffaellig=int((q - zB * u > f * sw['q_tol']).sum())) for f in QTOL_FAKTOREN])
    return dict(schwellen=sw, punkte=punkte, a4l1=a4, n=len(rows))


def nullresiduum(zB, n=NULL_N, B=NULL_B, seed=NULL_SEED, block=1000):
    """Komplexes Nullresiduum R = Z₁ + iZ₂ (Streuung 1 je Komponente) mit Bootstrap-Replikaten R + Z′₁ + iZ′₂: q = |R|
    und u = Streuung von |R_b|. Beide skalieren mit der Streuung s; die Aussagen bei q_tol/s = t folgen aus einer
    Ziehung. Rückgabe normierte Größen und die Grenze t*, ab der P(unauffällig) ≥ 0,8."""
    rng = np.random.default_rng(seed)
    q, u = np.empty(n), np.empty(n)
    for s0 in range(0, n, block):
        m = min(block, n - s0)
        R = rng.standard_normal(m) + 1j * rng.standard_normal(m)
        Rb = R[:, None] + rng.standard_normal((m, B)) + 1j * rng.standard_normal((m, B))
        q[s0:s0 + m], u[s0:s0 + m] = np.abs(R), np.abs(Rb).std(1, ddof=1)
    ober, unter = q + 1.645 * u, q - zB * u
    t_stern = float(np.quantile(ober, 0.8))
    gitter = []
    for t in (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0):
        gitter.append(dict(t=t, p_unauffaellig=float((ober <= t).mean()), p_auffaellig=float((unter > t).mean())))
    return dict(n=n, B=B, seed=seed, z_B=zB, q_mittel=float(q.mean()), q_median=float(np.median(q)),
                p_auffaellig_grenze=float((q > zB * u).mean()),
                u_mittel=float(u.mean()), u_median=float(np.median(u)), q_durch_u_median=float(np.median(q / u)),
                t_stern=t_stern, gitter=gitter, ober_median=float(np.median(ober)),
                analytisch=dict(q_mittel=math.sqrt(math.pi / 2), q_median=math.sqrt(2 * math.log(2)),
                                q_streuung=math.sqrt(2 - math.pi / 2)),
                _ober=ober, _q=q, _u=u)


# ── G4 ────────────────────────────────────────────────────────────────────────────────────────────────────
def _sigma_F(b, v, orakel):
    f = b['felder']
    if v == 'v0':
        return np.full(PUNKTE, b['sigma_delta']['K']['F'])
    sP = mad(f['pilot_DF'])
    if v == 'v0k':
        return np.full(PUNKTE, sP)
    if v == 'v1':
        return np.full(PUNKTE, mad(f['ziel_DF']))
    if v == 'v2':
        s = f['jitter_phase0']
        return np.sqrt(sP ** 2 + np.maximum(0.0, s[:PUNKTE] ** 2 - np.mean(s[PUNKTE:PUNKTE + 3] ** 2)))
    return np.asarray(orakel, float)


def _g4(b, sF, eps=0.0, delta=0.0):
    """G4-Entscheidung je Platz (Original, W1, W2) mit σ_Δ,F je Punkt; Amplitudentrend ε, Nullpunkttrend δ."""
    f = b['felder']
    sd = b['sigma_delta']['K']
    fak = b['g4_faktor']
    boden = gueltigkeit.RUNDUNG_REL * np.abs(f['laeufe_Nmittel'])
    gN = np.abs(f['laeufe_DN'] + delta) > fak * sd['N'] + boden
    gF = np.abs(f['laeufe_DF'] + eps * f['laeufe_Fletzt']) > fak * sF[f['laeufe_konf']] + boden
    return gN, gF


def _andere(b):
    return (np.delete(b['felder']['laeufe_regeln'], dg.REGELN.index('G4'), axis=1) == 1).any(1)


def orakel(bf):
    return np.array([mad(np.concatenate([b['felder']['laeufe_DF'][(b['felder']['laeufe_rolle'] == 0) &
                                                                  (b['felder']['laeufe_konf'] == c)] for b in bf]))
                     for c in range(PUNKTE)])


def kampagne_varianten(b, orak):
    """Je Variante: Zähler je Punkt (Originale), Bestand, Block des n_min-ten gültigen Platzes ohne und mit
    Wiederholungen und die gemessenen Wiederholungen. Prüft v0 gegen die gespeicherte produktive Entscheidung."""
    f = b['felder']
    n = int((f['laeufe_rolle'] == 0).sum())
    k, bl = f['laeufe_konf'][:n].astype(int), f['laeufe_block'][:n].astype(int)
    andere = _andere(b)
    out = {}
    for v in VARIANTEN:
        sF = _sigma_F(b, v, orak)
        gN, gF = _g4(b, sF)
        g = gN | gF
        if v == 'v0' and not np.array_equal(g, f['laeufe_regeln'][:, dg.REGELN.index('G4')] == 1):
            raise dg.Fehler(f'{b["szenario"]}/{b["index"]}: nachgerechnete G4-Entscheidung ≠ gespeicherte')
        if v == 'v0k' and b['k_max'] == b['k_pilotgroessen'] and not np.isclose(sF[0], b['sigma_delta']['K']['F']):
            raise dg.Fehler(f'{b["szenario"]}/{b["index"]}: σ_Δ,F bei k_max ≠ produktiv trotz gleichem k')
        ok = ~g & ~andere
        o, w1, w2 = ok[:n], ok[n:2 * n], ok[2 * n:]
        slot = o | w1 | w2
        zaehl = lambda m: np.bincount(k[m], minlength=PUNKTE)                                     # noqa: E731
        out[v] = dict(sigma_F=sF, G4=zaehl(g[:n]), G4_N=zaehl(gN[:n]), G4_F=zaehl(gF[:n]),
                      nur_G4=zaehl(g[:n] & ~andere[:n]), gueltig=zaehl(o), gueltig_w=zaehl(slot),
                      b18=block_nmin(o, k, bl), b18_w=block_nmin(slot, k, bl),
                      wiederholungen=zaehl(~o) + zaehl(~o & ~w1))
    out['andere'] = np.bincount(k[andere[:n]], minlength=PUNKTE)
    out['laeufe'] = np.bincount(k, minlength=PUNKTE)
    return out


def _cluster(x):
    """Mittel und Standardfehler über Kampagnen (Kampagnen als Einheiten)."""
    x = np.asarray(x, float)
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x)))


def g4_auswertung(a, B):
    systeme, kz, kk, trend, voll = {}, [], [], [], []
    for sid, w in dg.SYSTEME:
        bf = B[sid]
        if [b['index'] for b in bf] != list(range(dg.N_KAMPAGNEN)):
            raise dg.Fehler(f'{sid}: Kampagnen unvollständig')
        orak = orakel(bf)
        V = [kampagne_varianten(b, orak) for b in bf]
        schnitt = bf[0]['schnitt']
        p_hat = np.array([b['p_hat'] for b in bf])
        n_r = np.array([N_MIN + r_plus2(p) for p in p_hat])
        x_pil = np.array([int(round(p * b['n_pilot'])) for p, b in zip(p_hat, bf)])
        sysz = dict(werkzeug8=w, zielpilot=a['systeme'][sid]['zielpilot']['phi'], k_max=bf[0]['k_max'],
                    k_pilotgroessen=bf[0]['k_pilotgroessen'], n_fuenftel=bf[0]['n_fuenftel'],
                    p_hat=dict(mittel=float(p_hat.mean()), max=float(p_hat.max()), null=int((p_hat == 0).sum()),
                               verteilung={str(int(x)): int((x_pil == x).sum()) for x in sorted(set(x_pil))}),
                    n_plus2={str(int(x)): int((n_r == x).sum()) for x in sorted(set(n_r))},
                    sigma_N=_cluster([b['sigma_delta']['K']['N'] for b in bf]),
                    sigma_F={v: _cluster([V[i][v]['sigma_F'].mean() for i in range(len(bf))]) for v in ('v0', 'v0k', 'v1')},
                    orakel_sigma_F=orak.tolist(), varianten={})
        lauf = np.array([V[i]['laeufe'] for i in range(len(bf))])                    # (Kampagnen, Punkte)
        andere = np.array([V[i]['andere'] for i in range(len(bf))])
        for v in VARIANTEN:
            G = np.array([V[i][v]['G4'] for i in range(len(bf))])
            gu = np.array([V[i][v]['gueltig'] for i in range(len(bf))])
            b18 = np.array([V[i][v]['b18'] for i in range(len(bf))]).max(1)
            b18w = np.array([V[i][v]['b18_w'] for i in range(len(bf))]).max(1)
            wied = np.array([V[i][v]['wiederholungen'].sum() for i in range(len(bf))])
            je_punkt = G.sum(0) / lauf.sum(0)
            z = dict(G4=_cluster(G.sum(1) / lauf.sum(1)), G4_max_punkt=float(je_punkt.max()),
                     G4_max_punkt_id=schnitt[int(np.argmax(je_punkt))], G4_je_punkt=je_punkt.tolist(),
                     unvollstaendig_24=int((gu.min(1) < N_MIN).sum()), unvollstaendig_24_w=int((b18w > N_BLOECKE).sum()),
                     vollstaendig_n=[dict(n=n, ohne=int((b18 <= n).sum()), mit=int((b18w <= n).sum()))
                                     for n in range(N_MIN, N_BLOECKE + 1)],
                     vollstaendig_n_plus2=dict(ohne=int((b18 <= n_r).sum()), mit=int((b18w <= n_r).sum())),
                     kleinster_bestand={str(int(x)): int((gu.min(1) == x).sum()) for x in sorted(set(gu.min(1)))},
                     wiederholungen_je_kampagne=_cluster(wied), n=len(bf))
            if v == 'v0':
                for name in ('G4_N', 'G4_F', 'nur_G4'):
                    X = np.array([V[i][v][name] for i in range(len(bf))])
                    z[name] = _cluster(X.sum(1) / lauf.sum(1))
                    z[name + '_je_punkt'] = (X.sum(0) / lauf.sum(0)).tolist()
                z['andere'] = _cluster(andere.sum(1) / lauf.sum(1))
                z['ungueltig'] = _cluster((lauf - gu).sum(1) / lauf.sum(1))
                z['ungueltig_je_punkt'] = ((lauf - gu).sum(0) / lauf.sum(0)).tolist()
                pr = (lauf - gu).sum(0) / lauf.sum(0)
                z['binomial_punktweise_24'] = p_vollstaendig(N_BLOECKE, pr)
                z['binomial_phat_24'] = float(np.mean([p_vollstaendig(N_BLOECKE, p) for p in p_hat]))
                z['binomial_punktweise_24_w'] = p_vollstaendig(N_BLOECKE, pr, wiederholungen=2)
            sysz['varianten'][v] = z
        # Reserve: „+2“ gegen gemeinsame Vollständigkeit (Binomialnäherung) je Kampagne
        ob = np.array([obere_grenze(x, b['n_pilot']) for x, b in zip(x_pil, bf)])
        rg = lambda ps, w=0: {str(r): int(c) for r, c in zip(*np.unique([r_gemeinsam(p, wiederholungen=w) for p in ps],  # noqa
                                                                        return_counts=True))}
        sysz['reserve'] = dict(plus2={str(int(r)): int(c) for r, c in zip(*np.unique([r_plus2(p) for p in p_hat],
                                                                                   return_counts=True))},
                               gemeinsam_phat=rg(p_hat), gemeinsam_obere=rg(ob), gemeinsam_obere_w=rg(ob, 2),
                               ziel=ZIEL_VOLL, obere_grenze=OBERE_GRENZE)
        # Phase-0-Prüfung der Standardisierung an den Piloten: vorhergesagt gegen beobachtet (über Kampagnen gepoolt)
        pk = np.concatenate([b['felder']['pilot_konf'] for b in bf])
        pdf = np.concatenate([b['felder']['pilot_DF'] for b in bf])
        s0 = np.array([b['felder']['jitter_phase0'] for b in bf])
        sP = np.array([mad(b['felder']['pilot_DF']) for b in bf])
        pred = np.sqrt(sP[:, None] ** 2 + s0[:, PUNKTE:PUNKTE + 3] ** 2 - np.mean(s0[:, PUNKTE:PUNKTE + 3] ** 2, 1,
                                                                                  keepdims=True))
        sysz['piloten'] = dict(beobachtet=[mad(pdf[pk == j]) for j in range(3)], vorhergesagt=pred.mean(0).tolist(),
                               ziel_beobachtet=mad(np.concatenate([b['felder']['ziel_DF'] for b in bf])),
                               ziel_jitter_modell=a['systeme'][sid]['zielpilot']['jitter_streuung_N'],
                               jitter_modell=a['systeme'][sid]['zielpilot']['jitter_streuung_piloten_N'],
                               jitter_phase0=s0[:, PUNKTE:].mean(0).tolist())
        sysz['punkte'] = dict(id=schnitt, phi2=[float(x) for x in kv.SCHNITT_PHI2],
                              jitter_modell=a['systeme'][sid]['zielpilot']['jitter_streuung_schnitt_N'],
                              steigung_modell=a['systeme'][sid]['zielpilot']['steigung_schnitt'],
                              jitter_phase0=s0[:, :PUNKTE].mean(0).tolist(), mad_DF=orak.tolist(),
                              sigma_F_v2=np.mean([V[i]['v2']['sigma_F'] for i in range(len(bf))], 0).tolist())
        systeme[sid] = sysz
        # Zeilen je Kampagne und je Kampagne und Punkt
        for i, b in enumerate(bf):
            f, vv = b['felder'], V[i]
            kz.append(dict(system=sid, kampagne=b['index'], seed=b['seed'], volle_kette=int(b['voll']),
                           laufzeit_s=b['laufzeit_s']['gesamt'], k_pilot=b['k_pilotgroessen'], k_max=b['k_max'],
                           n_fuenftel=b['n_fuenftel'], pilot_laeufe=b['n_pilot'], pilot_ungueltig=int(x_pil[i]),
                           pilot_ungueltig_G4=int((f['pilot_regeln'][:, dg.REGELN.index('G4')] == 1).sum()),
                           p_hat=b['p_hat'], n_plus2=int(n_r[i]),
                           sigma_N_mN=1e3 * b['sigma_delta']['K']['N'],
                           **{f'sigma_F_{v}_mN': 1e3 * float(vv[v]['sigma_F'][0]) for v in ('v0', 'v0k', 'v1')},
                           jitter2_grad=b['jitter_grad'][1], jitter3_grad=b['jitter_grad'][2],
                           phase1_laeufe=b['phase1']['n_laeufe'], phase1_ungueltig=b['phase1']['n_ungueltig'],
                           S2=b['phase1']['S2'], S4=b['phase1']['S4'],
                           **{f'wiederholungen_{v}': int(vv[v]['wiederholungen'].sum()) for v in VARIANTEN},
                           **_voll_spalten(b)))
            for c in range(PUNKTE):
                z = dict(system=sid, kampagne=b['index'], punkt=schnitt[c], laeufe=int(vv['laeufe'][c]),
                         G4_N=int(vv['v0']['G4_N'][c]), G4_F=int(vv['v0']['G4_F'][c]), nur_G4=int(vv['v0']['nur_G4'][c]),
                         andere=int(vv['andere'][c]))
                for v in VARIANTEN:
                    z.update({f'G4_{v}': int(vv[v]['G4'][c]), f'gueltig_{v}': int(vv[v]['gueltig'][c]),
                              f'b18_{v}': int(vv[v]['b18'][c]), f'b18w_{v}': int(vv[v]['b18_w'][c])})
                z.update(sigma_F_v2_mN=1e3 * float(vv['v2']['sigma_F'][c]),
                         jitter_phase0_mN=1e3 * float(f['jitter_phase0'][c]))
                kk.append(z)
            if b['voll']:
                v0 = vv['v0']
                vk = b['voll_kette']
                voll.append(dict(system=sid, kampagne=b['index'], H1=vk['H1'], H1_grund=vk['H1_grund'], H2=vk['H2'],
                                 H2_grund=vk['H2_grund'], H1Z=vk['H1Z'], H3=vk['H3'], H4=vk['H4'], E3=vk['E3'],
                                 kleinster_bestand=int(v0['gueltig'].min()),
                                 alle_auswertbar=all(x['auswertbar'] for x in vk['konfigurationen'].values()),
                                 bestand_gleich=[vk['konfigurationen'][c]['n_gueltig'] for c in schnitt] ==
                                 v0['gueltig'].tolist()))
        trend += trendfall(sid, [b for b in bf if b['voll']], orak)
    return dict(systeme=systeme, volle_ketten=voll), kz, kk, trend


def _voll_spalten(b):
    vk = b['voll_kette'] or {}
    return dict(H1=vk.get('H1', ''), H1_grund=vk.get('H1_grund') or '', H2=vk.get('H2', ''),
                H2_grund=vk.get('H2_grund') or '')


def trendfall(sid, bf, orak):
    """Kontrollierter Trendfall an den Kampagnen des Startsatzes: Amplitudentrend ε (letztes Fünftel um 1 + ε
    skaliert; D_F' = D_F + ε·(F_min − ⟨N⟩)_letztes, exakt) und Nullpunkttrend δ in D_N; Anteil der von G4 erfassten
    Originalläufe gesamt, an den steilsten (S114–S118) und an flachen Punkten (S130–S140)."""
    rows = []
    for art, werte in (('amplitude', TREND_EPS), ('nullpunkt', NULLPUNKT_N)):
        for x in werte:
            for v in VARIANTEN:
                n = dict(gesamt=[0, 0], steil=[0, 0], flach=[0, 0])
                for b in bf:
                    f = b['felder']
                    o = f['laeufe_rolle'] == 0
                    gN, gF = _g4(b, _sigma_F(b, v, orak), eps=x if art == 'amplitude' else 0.0,
                                 delta=x if art == 'nullpunkt' else 0.0)
                    g = (gN | gF)[o]
                    ids = np.array(b['schnitt'])[f['laeufe_konf'][o]]
                    for name, m in (('gesamt', np.ones(g.size, bool)), ('steil', np.isin(ids, STEIL)),
                                    ('flach', np.isin(ids, FLACH))):
                        n[name][0] += int(g[m].sum())
                        n[name][1] += int(m.sum())
                rows.append(dict(system=sid, trend=art, staerke=x, variante=v, kampagnen=len(bf),
                                 **{f'{k}_erfasst': c[0] for k, c in n.items()}, **{f'{k}_laeufe': c[1] for k, c in n.items()}))
    return rows


# ── Ausgabe ──────────────────────────────────────────────────────────────────────────────────────────────
def _csv(pfad, rows, stellen=6):
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.{stellen}g}' if isinstance(v, float) else v) for k, v in r.items()})
    return formate.sha256_datei(pfad)


def tabellen(z):
    e3, g4 = z['e3'], z['g4']
    t = {}
    zl = ['| Punkt | n | auffällig | unauffällig | unbestimmt | E3a a/u/b | E3b a/u/b | „unauffällig“ nur an E3b verfehlt | '
          'u(q_Z) > q_tol/1,645 | auffällig E3a / E3b bei H1Z bestätigt | Prüfzahl m (Kampagnen) |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for p in e3['punkte']:
        d = lambda x: f'{x["auffällig"]}/{x["unauffällig"]}/{x["unbestimmt"]}'                    # noqa: E731
        zl.append(f'| {p["punkt"]} | {p["n"]} | {p["e3"]["auffällig"]} | {p["e3"]["unauffällig"]} | '
                  f'{p["e3"]["unbestimmt"]} | {d(p["e3a"])} | {d(p["e3b"])} | {p["nur_e3b"]} | {p["u_ueber_grenze"]} | '
                  f'{p["e3a_auffaellig_H1Z_bestaetigt"]} / {p["e3b_auffaellig_H1Z_bestaetigt"]} | '
                  + ', '.join(f'{m}: {c}' for m, c in p['m'].items()) + ' |')
    t['e3_punkte'] = '\n'.join(zl)
    a4 = e3['a4l1']
    zl = ['| Größe [10⁻⁴] | Min | 10 % | 25 % | Median | 75 % | 90 % | Max |', '|---|---|---|---|---|---|---|---|']
    for name, key in (('q_Z', 'q'), ('u(q_Z)', 'u'), ('q_Z + 1,645·u(q_Z)', 'ober')):
        zl.append(f'| {name} | ' + ' | '.join(_f(1e4 * x, 2) for x in a4[key]) + ' |')
    t['e3b_verteilung'] = '\n'.join(zl)
    zr = a4['zerlegung']
    t['e3b_zerlegung'] = '\n'.join([
        '| Kampagnen N01-A4/L1 | Anzahl |', '|---|---|',
        f'| u(q_Z) > q_tol/1,645 = {_f(1e4 * a4["grenze_u"], 3)}·10⁻⁴: „unauffällig“ schon wegen q_Z ≥ 0 ausgeschlossen '
        f'| {zr["unsicherheit_allein"]} |',
        f'| u(q_Z) unter dieser Grenze, aber q_Z > q_tol − 1,645·u(q_Z) | {zr["punktschaetzer"]} |',
        f'| „unauffällig“ (q_Z + 1,645·u(q_Z) ≤ q_tol) | {zr["unauffaellig"]} |',
        f'| zusammen | {a4["n"]} |'])
    nr = z['nullresiduum']
    zl = ['| q_tol/s | P(unauffällig) | P(auffällig) |', '|---|---|---|']
    for g in nr['gitter']:
        zl.append(f'| {_f(g["t"], 2)} | {_f(g["p_unauffaellig"], 3)} | {_f(g["p_auffaellig"], 4)} |')
    t['nullresiduum'] = '\n'.join(zl)
    zl = ['| q_tol (nachträglich, nur beschreibend) | „unauffällig“ an E3b | „auffällig“ an E3b |', '|---|---|---|']
    for s in a4['sensitivitaet']:
        zl.append(f'| {_f(s["faktor"], 2)} × 5,8·10⁻⁴ | {s["unauffaellig"]}/{a4["n"]} | {s["auffaellig"]}/{a4["n"]} |')
    t['qtol_sensitivitaet'] = '\n'.join(zl)
    # G4
    S = g4['systeme']
    zl = ['| | N01-A4 | N01-V1G0 | N01-V1G60h |', '|---|---|---|---|']
    zeile = lambda name, fn: zl.append(f'| {name} | ' + ' | '.join(fn(S[s]) for s, _ in dg.SYSTEME) + ' |')  # noqa
    zeile('k der Prüfgröße (k_max) / k der Pilotgrößen', lambda s: f'{s["k_max"]} / {s["k_pilotgroessen"]}')
    zeile('p̂ der Piloten: Mittel, Max, Kampagnen mit p̂ = 0',
          lambda s: f'{_f(s["p_hat"]["mittel"], 3)}, {_f(s["p_hat"]["max"], 3)}, {s["p_hat"]["null"]}/40')
    zeile('n = n_min + r(p̂) mit „+2“ (Kampagnen)', lambda s: ', '.join(f'{k}: {v}' for k, v in s['n_plus2'].items()))
    zeile('σ_Δ,N [mN]', lambda s: _f(1e3 * s['sigma_N'][0], 3))
    zeile('σ_Δ,F produktiv / bei k_max [mN]', lambda s: f'{_f(1e3 * s["sigma_F"]["v0"][0], 2)} / '
                                                     f'{_f(1e3 * s["sigma_F"]["v0k"][0], 2)}')
    v0 = lambda s: s['varianten']['v0']                                                              # noqa: E731
    zeile('ungültig durch D_N (G4) je Lauf', lambda s: _p(v0(s)['G4_N'][0], 2))
    zeile('ungültig durch D_F (G4) je Lauf', lambda s: _p(v0(s)['G4_F'][0], 2))
    zeile('G4 insgesamt ± SE (Kampagnen)', lambda s: f'{_p(v0(s)["G4"][0], 2)} ± {_p(v0(s)["G4"][1], 2)}')
    zeile('nur G4', lambda s: _p(v0(s)['nur_G4'][0], 2))
    zeile('andere Regeln (G1 …)', lambda s: _p(v0(s)['andere'][0], 2))
    zeile('ungültig insgesamt je Lauf: Mittel; ungünstigster Punkt',
          lambda s: f'{_p(v0(s)["ungueltig"][0], 2)}; {_p(max(v0(s)["ungueltig_je_punkt"]), 1)}')
    zeile('ungünstigster Punkt (G4)', lambda s: f'{v0(s)["G4_max_punkt_id"]}: {_p(v0(s)["G4_max_punkt"], 1)}')
    zeile('Kampagnen mit einem Punkt < n_min (n = 24, ohne Wiederholung)',
          lambda s: _kw(v0(s)['unvollstaendig_24'], v0(s)['n']))
    zeile('Binomialnäherung P(vollständig), n = 24: mit p̂ / mit punktweisen Raten',
          lambda s: f'{_f(v0(s)["binomial_phat_24"], 3)} / {_f(v0(s)["binomial_punktweise_24"], 3)}')
    zeile('kleinster Bestand je Kampagne (Anzahl Kampagnen)',
          lambda s: ', '.join(f'{k}: {v}' for k, v in v0(s)['kleinster_bestand'].items()))
    hz = z['historisch']
    zl.append('| historisch (Prüfstand 16.10.2026): G4-Anteil aller Läufe der Phase 1; H1 „Datenlage“; H1 und H2 '
              'bestätigt | ' + ' | '.join(f'{_p(hz[s]["G4_anteil_dokumentiert"], 1)}; {hz[s]["H1_datenlage"]}; '
                                          f'{hz[s]["gemeinsame_bestaetigung"]}' for s, _ in dg.SYSTEME) + ' |')
    t['g4_uebersicht'] = '\n'.join(zl)
    zl = ['| Punkt | φ₂ | Jitterstreuung Modell A4 / V1 [mN] | MAD(D_F) A4 / V1-G0 / V1-G60h [mN] | G4 produktiv A4 / '
          'V1-G0 / V1-G60h | davon D_N A4 / V1-G0 / V1-G60h |', '|---|---|---|---|---|---|']
    A, G, H = (S[s] for s, _ in dg.SYSTEME)
    for c, pid in enumerate(A['punkte']['id']):
        zl.append(f'| {pid} | {A["punkte"]["phi2"][c]:g}° | {_f(1e3 * A["punkte"]["jitter_modell"][c], 2)} / '
                  f'{_f(1e3 * G["punkte"]["jitter_modell"][c], 2)} | ' +
                  ' / '.join(_f(1e3 * x['punkte']['mad_DF'][c], 2) for x in (A, G, H)) + ' | ' +
                  ' / '.join(_p(x['varianten']['v0']['G4_je_punkt'][c], 1) for x in (A, G, H)) + ' | ' +
                  ' / '.join(_p(x['varianten']['v0']['G4_N_je_punkt'][c], 1) for x in (A, G, H)) + ' |')
    zl.append(f'| Piloten (110°, 250°), (130°, 230°), (110°, 252°) | | ' +
              ' / '.join(', '.join(_f(1e3 * y, 2) for y in x['piloten']['jitter_modell']) for x in (A, G)) + ' | ' +
              ' / '.join(', '.join(_f(1e3 * y, 2) for y in x['piloten']['beobachtet']) for x in (A, G, H)) + ' | | |')
    zl.append(f'| Zielpilot (130°, 262°) | | ' +
              ' / '.join(_f(1e3 * x['piloten']['ziel_jitter_modell'], 2) for x in (A, G)) + ' | ' +
              ' / '.join(_f(1e3 * x['piloten']['ziel_beobachtet'], 2) for x in (A, G, H)) + ' | | |')
    t['g4_punkte'] = '\n'.join(zl)
    zl = ['| System | Variante | G4 je Lauf | ungünstigster Punkt | Kampagnen mit Punkt < n_min (n = 24) ohne / mit '
          'Wiederholung | vollständig bei n_min + r(p̂) ohne / mit Wiederholung | Wiederholungsläufe je Kampagne |',
          '|---|---|---|---|---|---|---|']
    for s, _ in dg.SYSTEME:
        for v in VARIANTEN:
            x = S[s]['varianten'][v]
            zl.append(f'| {s} | {v} {NAMEN[v]} | {_p(x["G4"][0], 2)} | {x["G4_max_punkt_id"]}: {_p(x["G4_max_punkt"], 1)} '
                      f'| {x["unvollstaendig_24"]}/{x["n"]} / {x["unvollstaendig_24_w"]}/{x["n"]} | '
                      f'{x["vollstaendig_n_plus2"]["ohne"]}/{x["n"]} / {x["vollstaendig_n_plus2"]["mit"]}/{x["n"]} | '
                      f'{_f(x["wiederholungen_je_kampagne"][0], 1)} |')
    t['g4_varianten'] = '\n'.join(zl)
    zl = ['| System | Variante | ' + ' | '.join(f'n = {n}' for n in range(N_MIN, N_BLOECKE + 1)) + ' |',
          '|---|---|' + '---|' * (N_BLOECKE - N_MIN + 1)]
    for s, _ in dg.SYSTEME:
        for v in ('v0', 'v2'):
            x = S[s]['varianten'][v]
            zl.append(f'| {s} | {v} | ' + ' | '.join(f'{y["ohne"]} / {y["mit"]}' for y in x['vollstaendig_n']) + ' |')
    t['g4_vollstaendigkeit'] = '\n'.join(zl)
    zl = ['| System | r mit „+2“ aus p̂ | r gemeinsam (Näherung), p̂ | r gemeinsam, obere 80-%-Grenze von p̂ | r gemeinsam, '
          'obere Grenze, mit Wiederholung |', '|---|---|---|---|---|']
    for s, _ in dg.SYSTEME:
        r = S[s]['reserve']
        fm = lambda d: ', '.join(f'{k}: {v}' for k, v in d.items())                                # noqa: E731
        zl.append(f'| {s} | {fm(r["plus2"])} | {fm(r["gemeinsam_phat"])} | {fm(r["gemeinsam_obere"])} | '
                  f'{fm(r["gemeinsam_obere_w"])} |')
    t['g4_reserve'] = '\n'.join(zl)
    zl = ['| System | Trend | Stärke | ' + ' | '.join(f'{v}' for v in VARIANTEN) + ' |', '|---|---|---|' + '---|' * len(VARIANTEN)]
    tr = z['trend']
    for s, _ in dg.SYSTEME:
        for art, werte in (('amplitude', (0.0, 0.005, 0.01)), ('nullpunkt', (0.5e-3, 1.0e-3))):
            for x in werte:
                rs = {r['variante']: r for r in tr if r['system'] == s and r['trend'] == art and r['staerke'] == x}
                st = (_p(x, 1) if art == 'amplitude' else f'{_f(1e3 * x, 1)} mN')
                zl.append(f'| {s} | {art} | {st} | ' + ' | '.join(
                    f'{_p(rs[v]["steil_erfasst"] / rs[v]["steil_laeufe"], 0)} / {_p(rs[v]["flach_erfasst"] / rs[v]["flach_laeufe"], 0)}'
                    for v in VARIANTEN) + ' |')
    t['g4_trend'] = '\n'.join(zl)
    zl = ['| System | Kampagne | H1 | H2 | kleinster Bestand | alle Schnittpunkte auswertbar | Bestand schlank = voll |',
          '|---|---|---|---|---|---|---|']
    for r in g4['volle_ketten']:
        zl.append(f'| {r["system"]} | {r["kampagne"]} | {r["H1"]}{" (" + r["H1_grund"] + ")" if r["H1_grund"] else ""} | '
                  f'{r["H2"]}{" (" + r["H2_grund"] + ")" if r["H2_grund"] else ""} | {r["kleinster_bestand"]} | '
                  f'{"ja" if r["alle_auswertbar"] else "nein"} | {"ja" if r["bestand_gleich"] else "nein"} |')
    t['g4_volle_ketten'] = '\n'.join(zl)
    k = z['pilotsuche']
    zelle = lambda x: x.replace('|', '\\|')                                                         # noqa: E731
    t['pilotsuche'] = '\n'.join([
        '| | Begründung (Ergebnis unverändert: „' + k['ergebnis'] + '“) |', '|---|---|',
        f'| bisher | {zelle(k["alt"])} |', f'| neu | {zelle(k["neu"])} |',
        '| Klassen je Paar (k, T_a) | ' + ', '.join(f'{n}: {c}' for n, c in sorted(k['klassen'].items())) + ' |'])
    lz = z['laufzeiten']
    zl = ['| Auftrag | Kampagnen | Wandzeit [s] | Kernsekunden |', '|---|---|---|---|']
    for j, x in lz['auftraege'].items():
        zl.append(f'| {j} | {x["kampagnen"]} | {_f(x["laufzeit_s"], 1)} | {_f(x["kernsekunden"], 1)} |')
    zl.append(f'| zusammen | {lz["kampagnen"]} | {_f(lz["laufzeit_s"], 1)} | {_f(lz["kernsekunden"], 1)} '
              f'({_f(lz["kernsekunden"] / 3600, 3)} Kernstunden) |')
    t['laufzeiten'] = '\n'.join(zl)
    return t


def schreiben(pfad=dg.AUFTRAG, ausgabe=None, doku=None):
    """ergebnisse.json, g4_kampagnen.csv, g4_konfigurationen.csv, g4_trendfall.csv und die Tabellen in bericht.md."""
    doku = doku or os.path.join(neulauf.WURZEL, dg.DOKU_REL)
    a = dg.lies_auftrag(pfad)
    B, cp = dg.lies_ergebnisse(a, ausgabe)
    e3 = e3_auswertung(a)
    nr = nullresiduum(float(stats.norm.ppf(1 - 0.05 / (2 * PUNKTE + 1))))     # z_B bei voller Prüfmenge (m = 43)
    pr = dict((k, v) for k, v in nr.items() if not k.startswith('_'))
    s = e3['a4l1']['s_rayleigh']
    t = e3['schwellen']['q_tol'] / s
    pr['daten'] = dict(s_rayleigh=s, q_tol_durch_s=t, p_unauffaellig_vorhergesagt=float((nr['_ober'] <= t).mean()),
                       u_median_vorhergesagt=float(s * nr['u_median']), u_median_beobachtet=e3['a4l1']['u'][3],
                       q_median_vorhergesagt=float(s * nr['q_median']), q_median_beobachtet=e3['a4l1']['q'][3],
                       s_stern=e3['schwellen']['q_tol'] / nr['t_stern'],
                       faktor_s=float(s / (e3['schwellen']['q_tol'] / nr['t_stern'])))
    g4, kz, kk, trend = g4_auswertung(a, B)
    hist = _historisch()
    lz = dict(auftraege={j: dict(kampagnen=len(next(x for x in a['auftraege'] if x['id'] == j)['seeds']),
                                 laufzeit_s=c['laufzeit_s'], kernsekunden=c['kernsekunden'], git=c['git'],
                                 start=c['start'], ende=c['ende'], prozesse=c['prozesse']) for j, c in cp.items()})
    lz.update(kampagnen=sum(x['kampagnen'] for x in lz['auftraege'].values()),
              laufzeit_s=sum(x['laufzeit_s'] for x in lz['auftraege'].values()),
              kernsekunden=sum(x['kernsekunden'] for x in lz['auftraege'].values()))
    z = dict(kennung=dg.KENNUNG, auftrag=dict(datei=f'{dg.DOKU_REL}/auftrag.json', sha256=formate.sha256_datei(pfad)),
             herkunft=dict(checkpoints={j: dict(git=c['git'], dateien=c['dateien']) for j, c in cp.items()},
                           profil=a['gemeinsam']['profil'], profil_reduktion=a['gemeinsam']['profil_reduktion'],
                           profil_sha256=a['gemeinsam']['profil_sha256'], g4_faktor=a['gemeinsam']['g4_faktor'],
                           seeds_sha256={j['id']: formate.sha256_json(j['seeds']) for j in a['auftraege']},
                           werkzeug8={k: v['inhalt_sha256'] for k, v in a['werkzeug8'].items()},
                           e3_auszug=dict(datei=a['e3']['datei'], sha256=a['e3']['sha256'], quelle=a['e3']['quelle']),
                           umgebung=neulauf.umgebung()),
             laufzeiten=lz, e3=e3, nullresiduum=pr, g4=g4, historisch=hist, pilotsuche=k12_begruendung(),
             umfang=dict(neue_kampagnen=lz['kampagnen'], volle_ketten=len(g4['volle_ketten']),
                         e3_kampagnen=e3['n'], kalibrierkampagnen=0, kernstunden=round(lz['kernsekunden'] / 3600, 3)))
    z['dateien'] = {n: _csv(os.path.join(doku, n), r, st) for n, r, st in (
        ('g4_kampagnen.csv', kz, 6), ('g4_konfigurationen.csv', kk, 4), ('g4_trendfall.csv', trend, 6))}
    formate.schreibe_objekt(os.path.join(doku, 'ergebnisse'), formate.kopf(
        'bewertung', formate.synth_kennung(dg.KENNUNG, 'ERGEBNISSE')), z)
    tab = tabellen(dict(z, trend=trend))
    b = os.path.join(doku, 'bericht.md')
    if os.path.exists(b):
        with open(b, encoding='utf-8') as f:
            text = f.read()
        fehlt = [n for n in tab if f'<!-- tabelle:{n} -->' not in text]
        if fehlt:
            raise dg.Fehler(f'bericht.md: Tabellenblöcke fehlen: {fehlt}')
        neulauf_vergleich.bericht_einsetzen(b, tab)
    return z


def k12_begruendung():
    """Begründung der Pilotsuche alt und neu am versionierten K12-Ablauf des Altlaufs (altstand_auszug.json aus PR #21:
    alle Aufrufe des Planungshakens mit Kandidaten und Gründen)."""
    with open(os.path.join(neulauf.WURZEL, 'docs/ap13_neulaeufe_2026-10-17/altstand_auszug.json'), encoding='utf-8') as f:
        k = json.load(f)['k12']
    schritte = [dict(k=x['k'], N_z=x['N_z'], planung=x) for x in k['aufrufe']]
    klassen = {}
    for x in schritte:
        kl = pilot._klasse_paar(x)[0]
        klassen[kl] = klassen.get(kl, 0) + 1
    return dict(alt=k['suche']['grund'], neu=pilot.grund_ohne_arbeitspunkt(schritte, k['suche'].get('reduktion')),
                ergebnis=k['suche']['ergebnis'], reduktion=k['suche'].get('reduktion'), paare=len(schritte),
                klassen=klassen, quelle='docs/ap13_neulaeufe_2026-10-17/altstand_auszug.json: k12.aufrufe')


def _historisch():
    """Referenzwerte des Prüfstands (versionierte kompakte Datei, unverändert): gemeinsame Bestätigung, H1 Datenlage."""
    p = os.path.join(neulauf.WURZEL, neulauf.HISTORISCH_REL)
    if neulauf.git_blob(p) != neulauf.ALT_BLOB:
        raise dg.Fehler('historische kompakte Datei verändert')
    with open(p, encoding='utf-8') as f:
        s = json.load(f)['inhalt']['schritte']
    out = {}
    for sid, (schritt, unter, g4) in HISTORISCH.items():
        k = s[schritt] if unter is None else s[schritt][unter]
        out[sid] = dict(gemeinsame_bestaetigung=k['gemeinsame_bestaetigung'],
                        H1_datenlage=k['raten_pruefung']['H1: nicht entscheidbar, Grund Datenlage'],
                        G4_anteil_dokumentiert=g4, quelle=f'{neulauf.HISTORISCH_REL}: schritte.{schritt}' +
                        (f'.{unter}' if unter else ''))
    return out
