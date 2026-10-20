"""G4 für Konfigurationen und Einzelmodul-Kontrollläufe im Profilstand 2026-11 (Auftrag vom 20.10.2026, b1; Regeln
g4.verfahren, g4.b_plus, g4.zielrate, g4.lj; Entscheidungsvorlage vom 19.10.2026, Abschnitt 2).

Modi (g4.verfahren):
- 'b_plus' (Standard): konfigurationsabhängige Schwelle von D_F aus Phase-0-Größen mit vier Korrekturen gegenüber der
  Standardisierung v2 von PR #22:
  (1) Mischung der vorhergesagten Jitterstreuung über die Laufgrößen: s_i² = E_{τ,A}[2·Var_e F(φ_i + τ + e; A)] mit den
      Relativphasen τⱼ = offⱼ + δⱼ − δ₁ (j = 2, 3) und den Modulamplituden A aus den Komponentenschätzern von Phase 0
      (laufgroessen: σ_off,j aus den Pilot-Laufmitteln, σ_δ,j und σ_a,j aus den Lⱼ-Läufen; dieselben wie im Generator),
      e die Fünftelmittel der Indexphasen (σⱼ/√n_f). τ wird nicht zu e addiert (Var_τ E_e F fällt in D_F heraus).
      Die Pilotgröße s̄_P² wird mit derselben Mischung gebildet.
  (2) Liegt der vorhergesagte Knick innerhalb ±u(Δδⱼ), das Maximum von s über diesen Bereich; gerechnet wird das
      Maximum über die Verschiebungen 0, ±u(Δδ₂), ±u(Δδ₃) an jedem Punkt (an glatten Punkten ändert es s kaum;
      konservativ).
  (3) Feste Ziehungen, auf Mittel null und Einheitskovarianz normiert (antithetisch, Cholesky der Stichprobe).
  (4) Schwelle über ein Quantil statt über die Streuung: Die bedingte Verteilung von D_F bei gegebenen Laufgrößen ist
      näherungsweise normal mit Varianz 2·Var_e F + σ_W² (σ_W² = max(0, σ²_Δ,F,P − s̄_P²), Boden aus den Piloten); über
      die Laufgrößen gemischt hat D_F schwere Ränder. T_i löst E_{τ,A}[2·Φ̄(T_i/√v)] = α mit α = 2·Φ̄(3), Untergrenze
      3·σ_Δ,F,P. Die endliche Schätzunsicherheit von σ_Δ,F,P (MAD aus den Piloten) erhöht die Rate wie bei der
      3σ-MAD-Regel; das Arbeitsziel ≤ 1,5 % je Konfiguration und Lauf (g4.zielrate, D_N und D_F zusammen) ist eine
      Zielvorgabe unter dem benannten Nullmodell, keine bestätigte Rate.
  Gebunden an k_max, N_z (n_f), den Kalibrierstand (Δδⱼ, u(Δδⱼ)) und die Konfiguration. Fehlt s_i (Konfiguration
  nicht standardisiert), ist G4 für diesen Lauf „nicht prüfbar“.
- 'd' (Diagnose-/Entwicklungsmodus): phasenkorrigierte Fünftel-Differenz D = D_F − (F̂_letzt − F̂_erst), F̂ aus den
  gemessenen Fünftelzeigern und den Einzelmodul-Mittelkurven der Phase 0; eine Schwelle 3·σ_D aus den ebenso
  korrigierten gültigen Piloten für alle Konfigurationen. Ohne Fünftelzeiger (ältere Laufzusammenfassungen) ist D „nicht
  prüfbar“; es wird nicht still durch B+ ersetzt.
- 'je_laufart' (historisch): 3·σ_Δ,X je Laufart wie bis PR #23.
Lⱼ (g4.lj): Schwelle k(n₀ⱼ)·σ_Δ,X,Lⱼ mit dem von n abhängigen Faktor, der unter dem Normalmodell mit MAD-Schätzer aus n
Läufen dieselbe Rate je Prüfgröße ergibt wie 3σ bei bekanntem σ; dazu als Vergleich die Pooling-Variante über die mit
dem Phase-0-Betrag ihrer Größe standardisierten Module (n = Σn₀ⱼ) mit einer Homogenitätsprüfung der Modulstreuungen.
"""
from functools import lru_cache

import numpy as np
from scipy import optimize, special, stats

from . import konventionen as kv, vorhersage as vh

VERSION = 'g4-2026-11.1'
MODI = ('b_plus', 'd', 'je_laufart')
N_MISCHUNG = 32                      # Ziehungen der Laufgrößen (τ, A), antithetisch verdoppelt
N_FUENFTEL = 12                      # Ziehungen der Fünftelmittel e, antithetisch verdoppelt
SEED_ZIEHUNGEN = 20261020
FAKTOR = 3.0


def alpha(faktor=FAKTOR):
    """Nominale zweiseitige Rate je Prüfgröße der 3σ-Regel bei bekanntem σ."""
    return float(2 * stats.norm.sf(faktor))


def _normiert(n, d, seed):
    """n antithetisch verdoppelte Standardnormalziehungen (2n, d) mit Stichprobenmittel 0 und Einheitskovarianz."""
    z = np.random.default_rng(seed).standard_normal((n, d))
    z = np.concatenate([z, -z])
    L = np.linalg.cholesky(np.cov(z, rowvar=False).reshape(d, d))
    return z @ np.linalg.inv(L).T


@lru_cache(maxsize=4)
def ziehungen(n_m=N_MISCHUNG, n_e=N_FUENFTEL, seed=SEED_ZIEHUNGEN):
    """Feste normierte Ziehungen: Laufgrößen (2·n_m, 8) = (off₂, off₃, δ₁, δ₂, δ₃, a₁, a₂, a₃) und Fünftelmittel der
    Indexphasen der Module 2, 3 (2·n_e, 2)."""
    return _normiert(n_m, 8, seed), _normiert(n_e, 2, seed + 1)


def laufgroessen(lg):
    """Streuungen der Mischung aus den Komponentenschätzern von Phase 0 (laufgroessen.schaetzen; dieselben wie im
    Generator): σ_off,2, σ_off,3 [°] mit ihrer Korrelation, σ_δ,j [°], σ_a,j [1]. Nicht bestimmte Werte zählen als
    null (Komponente nicht nachgewiesen, im Bericht genannt)."""
    from . import laufgroessen as lgm
    k = lgm.komponenten(lg)

    def w(x):
        return 0.0 if x is None or not np.isfinite(float(x)) else float(x)
    rho = (lg.get('versatz') or {}).get('korrelation') or {}
    rho = rho.get('wert') if isinstance(rho, dict) else None
    rho = 0.0 if rho is None or not np.isfinite(float(rho)) else float(np.clip(rho, -0.99, 0.99))
    return dict(off=np.array([w(k['sigma_off_grad'][j]) for j in (1, 2)]), rho_off=rho,
                delta=np.array([w(x) for x in k['sigma_delta_grad']]), a=np.array([w(x) for x in k['sigma_a']]))


def _mischung(lg, n_m=N_MISCHUNG):
    """Relativphasen τ (2·n_m, 3) [°] (Modul 1: 0) und Amplituden A (2·n_m, 3) aus den normierten Ziehungen."""
    Z, _ = ziehungen(n_m)
    o2 = lg['off'][0] * Z[:, 0]
    o3 = lg['off'][1] * (lg['rho_off'] * Z[:, 0] + np.sqrt(1 - lg['rho_off'] ** 2) * Z[:, 1])
    d = lg['delta'][None, :] * Z[:, 2:5]
    tau = np.column_stack([np.zeros(len(Z)), o2 + d[:, 1] - d[:, 0], o3 + d[:, 2] - d[:, 0]])
    A = 1.0 + lg['a'][None, :] * Z[:, 5:8]
    return tau, A


def _F(phi_idx, Nbar, daempfung, kmax):
    """F_min − ⟨N⟩ (k ≤ k_max) für Indexphasen phi_idx (…, 3) [°] mit Amplituden in Nbar (…, 3, K)."""
    K = Nbar.shape[-1]
    k = np.arange(1, K + 1)
    rho = kv.zeigerfaktor(phi_idx, k) * daempfung
    return vh.fmin_rel_viele(np.einsum('...jk,...jk->...k', rho, Nbar)[..., :kmax])


def bedingte_varianzen(phi_profil, Nbar0, dd, jitter_grad, n_f, kmax, lg, verschiebung=(0.0, 0.0)):
    """2·Var_e F je Ziehung der Laufgrößen an einer Konfiguration (Profilphasen (0, φ₂, φ₃)); Rückgabe (2·n_m,)."""
    tau, A = _mischung(lg)
    _, e1 = ziehungen()
    K = Nbar0.shape[-1]
    k = np.arange(1, K + 1)
    daempfung = np.exp(-0.5 * np.outer(np.radians(np.asarray(jitter_grad, float)), k) ** 2)
    s_e = np.asarray(jitter_grad, float)[1:] / np.sqrt(n_f)
    idx0 = np.asarray(phi_profil, float) - np.asarray(dd, float) + np.r_[0.0, verschiebung]
    e = np.column_stack([np.zeros(len(e1)), s_e[0] * e1[:, 0], s_e[1] * e1[:, 1]])           # (n_e, 3)
    phi = idx0[None, None, :] + tau[:, None, :] + e[None, :, :]                              # (n_m, n_e, 3)
    Nb = A[:, None, :, None] * Nbar0[None, None]
    F = _F(phi, Nb, daempfung[None, None], kmax)
    return 2.0 * F.var(axis=1, ddof=1)


def _quantil_schwelle(v, sigma_W2, a):
    """T mit mean(2·Φ̄(T/√(v + σ_W²))) = a (Skalenmischung normaler Verteilungen)."""
    s = np.sqrt(np.asarray(v, float) + sigma_W2)
    s = s[s > 0]
    if s.size == 0:
        return 0.0
    f = lambda T: float(np.mean(special.erfc(T / s / np.sqrt(2)))) - a                   # noqa: E731
    hi = 10 * s.max()
    return float(optimize.brentq(f, 0.0, hi, xtol=1e-12 * hi))


def bplus(konfigurationen, piloten, Nbar0, dd, u_dd, jitter_grad, n_f, kmax, sigma_P_F, lg, regel):
    """Schwellen von D_F je Konfiguration nach B+.

    konfigurationen: [(id, (0, φ₂, φ₃))]; piloten: [(0, φ₂, φ₃)]; Nbar0 (3, K) Einzelmodul-Mittelkurven (Summe der
    Zellen) aus P0.8; dd, u_dd (3,) Δδⱼ und u(Δδⱼ) [°]; jitter_grad (3,) σⱼ der Piloten [°]; n_f Zyklen je Fünftel;
    sigma_P_F gepooltes σ_Δ,F der Piloten (unverändert definiert); lg: laufgroessen.schaetzen; regel: Wert von
    g4.b_plus. Rückgabe dict(schwellen_F, s, s_P, sigma_W, knick, alpha, …)."""
    erwartet = dict(mischung='Laufversatz, Phasenrest, Modulamplitude', piloten='dieselbe Mischung für s̄_P',
                    knick='Maximum über ±u(Δδⱼ)', ziehungen='normiert', schwelle='quantil')
    if {k: regel.get(k) for k in erwartet} != erwartet:
        raise ValueError(f'g4.b_plus: Bestandteile {regel} nicht umgesetzt')
    unten = float(regel['untergrenze_faktor'])
    a = alpha(unten)
    lg = laufgroessen(lg)
    u = np.asarray(u_dd, float)
    versch = [(0.0, 0.0), (u[1], 0.0), (-u[1], 0.0), (0.0, u[2]), (0.0, -u[2])]

    def var_max(phi):
        V = np.stack([bedingte_varianzen(phi, Nbar0, dd, jitter_grad, n_f, kmax, lg, v) for v in versch])
        j = int(np.argmax(V.mean(1)))
        return V[j], j
    s_P2 = [float(var_max(p)[0].mean()) for p in piloten]
    sbar_P2 = float(np.mean(s_P2))
    sigma_W2 = max(0.0, float(sigma_P_F) ** 2 - sbar_P2)
    out_T, out_s, knick = {}, {}, {}
    for cid, phi in konfigurationen:
        V, j = var_max(phi)
        out_s[cid] = float(np.sqrt(V.mean()))
        knick[cid] = bool(j != 0)                                    # Maximum an verschobener Lage
        out_T[cid] = max(unten * float(sigma_P_F), _quantil_schwelle(V, sigma_W2, a))
    return dict(version=VERSION, modus='b_plus', schwellen_F=out_T, s=out_s, s_P=[float(np.sqrt(x)) for x in s_P2],
                sbar_P=float(np.sqrt(sbar_P2)), sigma_W=float(np.sqrt(sigma_W2)), sigma_P_F=float(sigma_P_F),
                alpha=a, untergrenze=unten * float(sigma_P_F), maximum_verschoben=knick, k_max=int(kmax), n_f=int(n_f),
                laufgroessen=dict(off_grad=lg['off'].tolist(), rho_off=lg['rho_off'], delta_grad=lg['delta'].tolist(),
                                  a=lg['a'].tolist()),
                ziehungen=dict(mischung=2 * N_MISCHUNG, fuenftel=2 * N_FUENFTEL, seed=SEED_ZIEHUNGEN),
                hinweis='Arbeitsziel ≤ 1,5 % Fehlausschlüsse je Konfiguration und Lauf (g4.zielrate) unter dem '
                        'benannten Nullmodell; keine bestätigte Rate')


# ── D: phasenkorrigierte Fünftel-Differenz ────────────────────────────────────────────────────────────────
def fuenftel_vorhersage(fz, Nbar0, n_f, kmax):
    """F̂ (…, 2) des ersten und letzten Fünftels eines Kombinationslaufs aus den Fünftelzeigern fz (…, 2, 3) =
    Σ_c e^{−iφⱼ,c} (k = 1; Modul 1 als Bezug n_f) und den Einzelmodul-Mittelkurven Nbar0 (3, K):
    ρⱼₖ = (ζ/|ζ|)^k·(|ζ|/n_f)^{k²}. Fehlt ein Zeiger (nan), ist F̂ nan."""
    fz = np.asarray(fz, complex)
    K = Nbar0.shape[-1]
    k = np.arange(1, K + 1)
    a = np.abs(fz)
    ph = fz / np.where(a > 0, a, 1.0)
    r = np.clip(a / n_f, 1e-300, 1.0)
    rho = ph[..., None] ** k * r[..., None] ** (k ** 2)
    Y = np.einsum('...jk,jk->...k', rho, Nbar0)[..., :kmax]
    ok = np.isfinite(Y).all(-1)
    out = np.full(ok.shape, np.nan)
    if ok.any():
        out[ok] = vh.fmin_rel_viele(Y[ok])
    return out


def d_statistik(DF, fz, Nbar0, n_f, kmax):
    """D = D_F − (F̂_letzt − F̂_erst); nan ohne Fünftelzeiger."""
    F = fuenftel_vorhersage(fz, Nbar0, n_f, kmax)
    return np.asarray(DF, float) - (F[..., 1] - F[..., 0])


def d_schwelle(D_piloten, faktor=FAKTOR):
    x = np.asarray(D_piloten, float)
    x = x[np.isfinite(x)]
    if x.size < 2:
        return None
    s = float(1.4826 * np.median(np.abs(x - np.median(x))))
    return dict(modus='d', sigma_D=s, schwelle_D=faktor * s, n_piloten=int(x.size), faktor=faktor, version=VERSION)


# ── Lⱼ: von n abhängige Schwelle, Pooling-Vergleich ───────────────────────────────────────────────────────
@lru_cache(maxsize=64)
def faktor_n(n, faktor=FAKTOR, n_mc=40_000, seed=SEED_ZIEHUNGEN):
    """k(n): E_σ̂[2·Φ̄(k·σ̂/σ)] = 2·Φ̄(faktor) für σ̂ = 1,4826·MAD aus n Normalwerten (unabhängig vom geprüften
    Lauf; feste Ziehungen, deterministisch). Für n → ∞ geht k(n) gegen faktor."""
    n = int(n)
    if n < 3:
        raise ValueError('faktor_n: n ≥ 3')
    x = np.random.default_rng(seed + n).standard_normal((n_mc, n))
    s = 1.4826 * np.median(np.abs(x - np.median(x, 1, keepdims=True)), 1)
    a = alpha(faktor)
    f = lambda k: float(np.mean(special.erfc(k * s / np.sqrt(2)))) - a                   # noqa: E731
    return float(optimize.brentq(f, faktor, 4 * faktor, xtol=1e-10))


def lj_schwellen(sigma_delta, n0, skalen=None, faktor=FAKTOR):
    """Lⱼ-Schwellen: n-abhängig (Standard) je Modul und Größe; Pooling-Vergleich über die mit `skalen` (je Modul
    {'N': …, 'F': …}, Phase-0-Betrag der Größe) standardisierten Streuungen, mit F-Test der Homogenität.
    sigma_delta: {'L1': {'N', 'F'}, …}; n0: {'L1': n, …}."""
    out = dict(n_abhaengig={}, pooling=None, faktor=faktor)
    for g in ('L1', 'L2', 'L3'):
        if g not in sigma_delta or g not in n0:
            continue
        k = faktor_n(int(n0[g]), faktor)
        out['n_abhaengig'][g] = dict(faktor=k, n=int(n0[g]), N=k * sigma_delta[g]['N'],
                                     F=None if sigma_delta[g].get('F') is None else k * sigma_delta[g]['F'])
    if skalen:
        gr = [g for g in ('L1', 'L2', 'L3') if g in sigma_delta and g in skalen]
        pool = {}
        for x in ('N', 'F'):
            w = [(sigma_delta[g][x] / skalen[g][x]) ** 2 for g in gr if sigma_delta[g].get(x) is not None
                 and skalen[g].get(x)]
            if len(w) < 2:
                continue
            nn = np.array([int(n0[g]) for g in gr])
            s2 = float(np.average(w, weights=nn - 1))
            out_b = _bartlett(np.asarray(w, float), nn)
            kp = faktor_n(int(nn.sum()), faktor)
            pool[x] = dict(sigma_std=float(np.sqrt(s2)), faktor=kp, n=int(nn.sum()), bartlett=out_b,
                           schwellen={g: kp * float(np.sqrt(s2)) * skalen[g][x] for g in gr},
                           hinweis='Vergleich, nicht Standard; Homogenität der Modulstreuungen geprüft, nicht '
                                   'vorausgesetzt (die kleine Diagnose entscheidet keine allgemeine Homogenität)')
        out['pooling'] = pool or None
    return out


def _bartlett(s2, n):
    """Bartlett-Test gleicher Varianzen aus Stichprobenvarianzen s2 (hier aus MAD, näherungsweise) und Umfängen n."""
    f = n - 1
    sp = float(np.sum(f * s2) / f.sum())
    T = (f.sum() * np.log(sp) - np.sum(f * np.log(s2))) / (1 + (np.sum(1 / f) - 1 / f.sum()) / (3 * (len(s2) - 1)))
    return dict(statistik=float(T), df=len(s2) - 1, p=float(stats.chi2.sf(T, len(s2) - 1)))


# ── Teil B: Block nr2.g4 ─────────────────────────────────────────────────────────────────────────────────
def teil_b_block(tab0, ungueltig, sigma_delta, Nbar0, dd, u_dd, jitter_grad, kmax, konfigurationen, lg, profil):
    """nr2.g4 im Profilstand 2026-11 aus den gebundenen Phase-0-Größen (Fenster N_z und k_max des Plans): B+ (Standard,
    immer gebildet), D (wenn die Phase-0-Läufe Fünftelzeiger tragen) und die Lⱼ-Schwellen. Keine Phase-1-Daten.
    tab0: Phase-0-Läufe des Satzes; ungueltig: Lauf-IDs ungültiger Läufe; Nbar0 (3, K) Einzelmodul-Mittelkurven
    (Summe der Zellen); konfigurationen: Teil-B-Liste (id, phi, einstellung); lg: Laufgrößen des Satzes."""
    from . import gueltigkeit, zusammenfassung as zf
    t = tab0.auswahl(tab0.spalte('phase', int) == 0)
    nf = {int(k['n_fuenftel']) for k in t.koepfe}
    if len(nf) != 1:
        raise ValueError(f'G4: Phase-0-Läufe mit verschiedenen Fünftellängen {sorted(nf)}')
    n_f = nf.pop()
    modus = profil.wert('g4.verfahren')
    if modus not in MODI:
        raise ValueError(f'g4.verfahren {modus!r} nicht umgesetzt ({", ".join(MODI)})')
    Nbar0 = np.asarray(Nbar0, complex)
    out = dict(version=VERSION, modus_profil=modus, bindung=dict(k_max=int(kmax), N_z=int(t.koepfe[0]['n_zyklen']),
                                                                 n_f=n_f, delta_delta_grad=list(map(float, dd)),
                                                                 u_delta_delta_grad=list(map(float, u_dd))))
    konf = [(c['id'], tuple(c['phi'])) for c in konfigurationen if c['einstellung'] == 1]
    piloten = [(0.0, p2, p3) for p2, p3 in kv.PILOTEN]
    sK = (sigma_delta or {}).get('K') or {}
    if lg is None or sK.get('F') is None:
        out['b_plus'] = None
        out['b_plus_grund'] = 'Laufgrößen oder σ_Δ,F der Piloten fehlen: B+ nicht bildbar (G4 nicht prüfbar)'
    else:
        out['b_plus'] = bplus(konf, piloten, Nbar0, dd, u_dd, jitter_grad, n_f, kmax, sK['F'], lg,
                              profil.wert('g4.b_plus'))
    gut = np.array([k['lauf_id'] not in ungueltig for k in t.koepfe])
    pil = np.array([k['konfiguration']['gruppe'] == 'pilot' and k['laufart'] == 'K' for k in t.koepfe]) & gut
    if zf.hat_fuenftelzeiger(t.daten) and pil.any():
        _, DF = gueltigkeit.fuenftel_differenzen(t, int(kmax))
        D = d_statistik(DF[pil], t.daten['fuenftel_zeiger'][pil], Nbar0, n_f, int(kmax))
        dd_ = d_schwelle(D)
        out['d'] = None if dd_ is None else dict(dd_, Nbar0=Nbar0, n_f=n_f)
    else:
        out['d'] = None
        out['d_grund'] = 'Fünftelzeiger fehlen in den Phase-0-Läufen (Format vor dem 20.10.2026): D nicht prüfbar'
    n0 = {f'L{j}': int(sum(1 for k, g in zip(t.koepfe, gut) if g and k['laufart'] == 'L' and k['modul'] == j
                           and k['einstellung'] == 1)) for j in (1, 2, 3)}
    skalen = {f'L{j}': dict(N=1.0, F=float(abs(vh.fmin_rel_viele(Nbar0[j - 1][:int(kmax)])))) for j in (1, 2, 3)}
    out['lj'] = lj_schwellen({g: v for g, v in (sigma_delta or {}).items() if g in n0}, n0, skalen)
    out['lj']['hinweis'] = ('Standard: n-abhängige Schwelle k(n₀ⱼ)·σ_Δ,X je Modul; Pooling nur als Vergleich '
                            '(D_N ohne Standardisierung, D_F mit |F_min − ⟨N⟩| von N̄⁽ʲ⁾ standardisiert)')
    return out
