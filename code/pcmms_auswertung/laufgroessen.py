"""Laufgrößen aus Phase 0 (Teil d0, Regel p0.laufgroessen): Komponentenschätzer des Strukturmodells aus den
Laufzusammenfassungen der Phase 0, nur zweite Momente, gebunden an k und N_z.

Aufruf (Pilotskript, Satz der Phase-0-Größen bei (k, N_z); auch eigenständig):

    lg = laufgroessen.schaetzen(tab, gueltig, k)
    kp = laufgroessen.komponenten(lg)          # flache Felder (numpy) für G4 B+, Generator und Planung

Eingaben: tab – LaufTabelle der Phase-0-Läufe eines einheitlichen Fensters (N_z Zyklen; Läufe anderer Phase oder
Einstellung werden ignoriert); gueltig – boolsche Maske je Zeile von tab (Gültigkeit des Satzes nach G1–G10, A9.2);
k – Zahl der Harmonischen k ≤ k, über die projiziert wird (k des Satzes). Optional uebertragungstest (Vorgabe True):
Übertragungstest L → K an den Pilotkonfigurationen (nur zweite Momente, verwendet N̄⁽ʲ⁾ zusammen mit den Zeigern
der Pilotläufe; keine Superpositionsresiduen).

Rückgabe (Format laufgroessen-0.1, JSON-fähig) mit den Komponenten; jede Komponente ist ein dict
  wert (Punktschätzer der Streuung, abgeschnitten bei null), einheit, nu (Freiheitsgrade), oben80 (marginale obere
  80-%-Grenze s·√(ν/χ²₀,₂(ν)) der Gesamtstreuung abzüglich des Bodenanteils), s_gesamt (Streuung einschließlich
  Boden), boden (Bodenanteil der Varianz), u (Standardunsicherheit von wert, Deltamethode), identifiziert (Basis nicht
  entartet, ν ≥ 1), nachgewiesen (F-Test gegen den Boden, 95 %), quelle, grund.
Felder:
  bindung       k, N_z, n_fuenftel, T_a_s, f_soll, Zahl gültiger Läufe je Art (n_R, n0 je Modul, n_pilot).
  boden         sigma_h_zellen (je Zelle: Re/Im N_c,k, k ≤ k, aus den R-Läufen, ν = 2·k·(n_R − 1)) [N],
                sigma_h_je_k (3, k) [N] mit Weißheitsprüfung über k, sigma_mittel_zellen (Boden von ⟨N_c⟩ je Lauf aus
                den Fünfteln (F₁ + F₅)/2 − ⟨N⟩ der R-Läufe, Summe, Aufteilung auf die Zellen nach σ̂_ref,c) [N] und
                sigma_mittel_summe [N], sigma_c (Rohstreuung je Abtastwert, sigma_roh_zellen der R-Läufe) [N].
                Der Boden von ⟨N⟩ gilt für alle Laufarten (ein gemeinsamer Faktor in der Planung).
  nullpunkt     lineare Drift [N/s] und Diffusion eines Zufallspfads [N²/s] der Summe aus der Referenzfolge
                (Leave-one-out gegen die Interpolation der Nachbarn, Brückenvarianz), getrennt vom Boden aus den
                Fünfteln; sigma_loo [N] (σ̂_ref-artig, ν_eff analytisch).
  laufintern    Drift von ⟨N⟩ im Lauf (D_N = F₅ − F₁ der R-Läufe: Mittel und Zusatzstreuung über dem Boden) [N];
                je Modul Amplituden- und Phasenänderung letztes − erstes Fünftel aus den Lⱼ-Läufen (kohärente
                Projektion der Fünftelharmonischen) [1], [°], mit dem orthogonalen Fünftelrest als Prüfgröße.
  module        je Modul j = 1, 2, 3 aus den gültigen Lⱼ-Läufen (P0.8): sigma_a (relative Amplitude, ν = n₀ⱼ − 1) [1],
                sigma_delta (Phasenrest Encoder ↔ Masse) [°] aus der kohärenten, mit dem Zellboden gewichteten
                Projektion der Lⱼ-Abweichungen über k ≤ k und Zellen auf N̄⁽ʲ⁾ bzw. −ik·N̄⁽ʲ⁾; rest (orthogonaler Rest
                je Harmonischer als Vielfaches q_jk des Zellbodens, ν ≈ (n₀ⱼ − 1)·Σ_c(2 − h)); kohaerenz (Prüfung über
                k: Q = Σ_r Σ_k (â_rk − â_r)²/f_k ~ χ²((n₀ⱼ − 1)(k_eff − 1)) für Amplitude und Phase, Streuung je k).
  versatz       je Modul 2, 3 aus den Laufmitteln φ̄ⱼ der gültigen Piloten: σ²_off,j = max(0, Var φ̄ⱼ − σ̄ⱼ²/N_z)
                (Abweichungen vom Mittel je Pilotkonfiguration, ν = Σ(n − 1)) [°], Korrelation der Versätze 2/3.
  jitter        je Modul 2, 3 RMS von σⱼ der gültigen Piloten [°] (je Zyklus, erfasst), je Pilotkonfiguration.
  uebertragung  erfasster Phasenanteil (aus den gemessenen Zeigern und N̄⁽ʲ⁾) und Übertragungstest L → K je
                Harmonischer k = 1 … 3 (Verhältnis beobachtete/modellierte Varianz von Re/Im N_k der Piloten,
                näherungsweiser F-Test); keine Mittelwerte, keine Residuen.
  technik       T_φ (Mittel, Streuung), Zelltemperatur (Mittel, Streuung im Lauf), Streuung von f_mittel.
  komponenten   flache Zusammenfassung (sigma_a, sigma_delta_grad, sigma_off_grad, sigma_jitter_grad je Modul mit ν und
                oben80; Module ohne Größe: 0 bzw. None).
  nicht_identifizierbar  Liste der Komponenten ohne Schätzung (mit Grund); sie sind in Planung und Generator als
                benannte Sensitivitäten zu führen, nicht still zu ersetzen.

Bindung: Die Größen hängen über die Gültigkeitsmaske (G4 mit k ≤ k) und die Projektion von k ab, über den Boden, den
Jitter und die Fünftel von N_z. Für ein anderes (k, N_z) wird neu geschätzt (Pilotskript je Paar der Suche).

Annahmen (gekennzeichnet, nicht aus Phase 0 prüfbar): Zellen und Läufe unabhängig; Boden weiß über die Zyklen
(Fünftel enthalten ⌊N_z/5⌋ Zyklen; die Generatorkonvention ⟨N⟩ = Mittel der fünf Fünftel gilt für N_z = 5·n_f);
Amplituden- und Phasenstreuung der Kombinationsläufe wie in den Lⱼ-Läufen (prüft der Übertragungstest nur an den
Piloten); eine gemeinsame Laufzeitschwankung der Kette ist in Lⱼ nicht von modulweisem δ trennbar; farbiger,
korrelierter oder lastabhängiger Jitter und Drift zwischen Phase 0 und Phase 1 sind nicht identifizierbar
(benannte Sensitivitäten, Strukturmodell in generator.phase0_modell).
"""
from functools import lru_cache

import numpy as np
from scipy import stats

from . import konventionen as kv

VERSION = 'laufgroessen-0.1'
REGEL_ID = 'p0.laufgroessen'
# Wert der Regel p0.laufgroessen, den dieser Code umsetzt (regeln._NEU_11); ein anderer Wert ist ein ValueError
REGELWERT = dict(amplitude_phase='kohärente Projektion der Lⱼ-Abweichungen (σ_a,j, σ_δ,j, ν = n₀ⱼ − 1)',
                 versatz='Laufmittel der Indexphasen der gültigen Piloten (σ_off,j)', boden='Referenzläufe')
NIVEAU = 0.8
F_NIVEAU = 0.95


def regel(profil):
    """Wert der Regel p0.laufgroessen im Profil; nur der umgesetzte Wert ist zulässig (kein stiller Ersatzweg)."""
    w = profil.wert(REGEL_ID)
    if w != REGELWERT:
        raise ValueError(f'Regel {REGEL_ID}: Wert {w!r} nicht umgesetzt (umgesetzt: {REGELWERT!r})')
    return w


def kappa(nu, niveau=NIVEAU):
    """Faktor der oberen Vertrauensgrenze einer Streuung mit ν Freiheitsgraden: √(ν/χ²_{1−niveau}(ν))."""
    if nu is None or not np.isfinite(nu) or nu <= 0:
        return None
    return _kappa(float(nu), float(niveau))


@lru_cache(maxsize=4096)
def _kappa(nu, niveau):
    return float(np.sqrt(nu / stats.chi2.ppf(1 - niveau, nu)))


@lru_cache(maxsize=4096)
def _f_quantil(nu1, nu2):
    """F₀,₉₅(ν₁, ν₂); ν₂ = ∞: χ²₀,₉₅(ν₁)/ν₁."""
    if not np.isfinite(nu2):
        return float(stats.chi2.ppf(F_NIVEAU, nu1) / nu1)
    return float(stats.f.ppf(F_NIVEAU, nu1, nu2))


def _f(x):
    return None if x is None or not np.isfinite(x) else float(x)


def komponente(s2_gesamt, boden, nu, einheit, quelle, identifiziert=True, grund=None, nu_boden=np.inf,
               skala=1.0, **extra):
    """Streuungskomponente aus einer Gesamtvarianz s² (ν Freiheitsgrade) und ihrem Bodenanteil b (bekannt bzw. mit
    ν_boden): wert = √max(0, s² − b), oben80 = √max(0, s²·κ(ν)² − b), nachgewiesen bei s²/b > F₀,₉₅(ν, ν_boden).
    skala rechnet in die Einheit um (z. B. Radiant → Grad)."""
    if not identifiziert or s2_gesamt is None or not np.isfinite(s2_gesamt) or nu is None or nu < 1:
        return dict(wert=None, einheit=einheit, nu=None if nu is None else float(nu), oben80=None, s_gesamt=None,
                    boden=None if boden is None else float(boden * skala ** 2), u=None, identifiziert=False,
                    nachgewiesen=False, quelle=quelle, grund=grund or 'nicht identifizierbar', **extra)
    b = 0.0 if boden is None or not np.isfinite(boden) else float(boden)
    s2 = float(s2_gesamt)
    w2 = max(0.0, s2 - b)
    k = kappa(nu)
    o2 = max(0.0, s2 * k ** 2 - b)
    if b > 0:
        nb = np.inf if nu_boden is None else float(nu_boden)
        nach = bool(s2 / b > _f_quantil(float(nu), nb))
    else:
        nach = bool(s2 > 0)
    u_s2 = s2 * np.sqrt(2.0 / nu)
    u = u_s2 / (2 * np.sqrt(w2)) if w2 > 0 else None
    return dict(wert=float(np.sqrt(w2) * skala), einheit=einheit, nu=float(nu), oben80=float(np.sqrt(o2) * skala),
                s_gesamt=float(np.sqrt(s2) * skala), boden=float(b * skala ** 2), u=None if u is None else
                float(u * skala), identifiziert=True, nachgewiesen=nach, quelle=quelle, grund=grund, **extra)


def _phase0(tab):
    ph = tab.spalte('phase', int)
    e = tab.spalte('einstellung', int)
    return (ph == 0) & (e == 1)


def fenster(tab):
    nz = sorted({int(k['n_zyklen']) for k in tab.koepfe})
    if len(nz) != 1:
        raise ValueError(f'Laufgrößen: Phase-0-Läufe mit verschiedenen Zyklenzahlen {nz}')
    return nz[0], nz[0] // 5


# ── Boden aus den Referenzläufen ──────────────────────────────────────────────────────────────────────
def _boden(tab, R, k, N_z, n_f):
    d = tab.daten
    nR = int(R.sum())
    out = dict(n=nR)
    if nR < 2:
        out.update(sigma_h_zellen=[komponente(None, None, None, 'N', 'Referenzläufe (P0.7)', False,
                                              f'{nR} gültige Referenzläufe') for _ in range(3)],
                   s2_h_zellen=np.full(3, np.nan), nu_h=None, s2_m_summe=np.nan, nu_m=None)
        return out
    X = d['Nk_zellen'][R][:, :, :k]
    D = X - X.mean(0)
    v = ((D.real ** 2).sum(0) + (D.imag ** 2).sum(0)) / (2 * (nR - 1))      # (3, k) je Re/Im-Komponente
    s2c = v.mean(1)
    nu_h = 2 * k * (nR - 1)
    out['s2_h_zellen'] = s2c
    out['s2_h_je_k'] = v
    out['nu_h'] = nu_h
    out['sigma_h_zellen'] = [komponente(s2c[c], 0.0, nu_h, 'N', f'Referenzläufe (P0.7): Re/Im N_c,k, k ≤ {k}')
                             for c in range(3)]
    out['sigma_h_je_k'] = np.sqrt(v)
    # Weißheit über k: Bartlett mit gleichen Freiheitsgraden je k (Zellen gepoolt)
    vk = v.mean(0)
    nk = 6 * (nR - 1)
    if k >= 2 and np.all(vk > 0):
        sp = vk.mean()
        T = (nk * k * np.log(sp) - nk * np.log(vk).sum()) / (1 + (k + 1) / (3 * k * nk))
        out['weiss_ueber_k'] = dict(bartlett=float(T), nu=k - 1, p=float(stats.chi2.sf(T, k - 1)),
                                    verhaeltnis_max_min=float(vk.max() / vk.min()))
    else:
        out['weiss_ueber_k'] = dict(bartlett=None, nu=None, p=None, verhaeltnis_max_min=None)
    # Boden von ⟨N⟩ aus den Fünfteln (innerhalb des Laufs, unabhängig vom Nullpunktprozess)
    F = d['fuenftel_N_mittel'][R]
    Nm = d['N_mittel'][R]
    g = N_z / (2.0 * n_f) - 1.0 if n_f >= 1 else np.nan
    if n_f >= 1 and np.isfinite(F).all() and g > 0:
        Y = 0.5 * (F[:, 0] + F[:, 1]) - Nm
        s2m = float(Y.var(ddof=1) / g)
        out.update(s2_m_summe=s2m, nu_m=nR - 1, faktor_fuenftel=g,
                   sigma_mittel_summe=komponente(s2m, 0.0, nR - 1, 'N',
                                                 'Referenzläufe (P0.7): (F₁ + F₅)/2 − ⟨N⟩, Boden je Lauf'))
    else:
        out.update(s2_m_summe=np.nan, nu_m=None, faktor_fuenftel=None,
                   sigma_mittel_summe=komponente(None, None, None, 'N', 'Referenzläufe (P0.7)', False,
                                                 'keine Fünftel (N_z < 5) oder nicht endlich'))
    # Rohstreuung je Abtastwert (σ_c)
    sc = d['sigma_roh_zellen'][R]
    out['sigma_c'] = np.sqrt(np.mean(sc ** 2, 0))
    return out


def _zellanteile_mittel(tab, R):
    """Anteile der Zellen am Boden von ⟨N⟩ aus den Leave-one-out-Werten je Zelle (σ̂_ref,c), Summe 1."""
    x, t = _ref_folge(tab, R)
    d = tab.daten['N_mittel_zellen'][R][x['ordnung']]
    if d.shape[0] < 3:
        return np.full(3, 1 / 3)
    dz = d[1:-1] - ((1 - x['beta'])[:, None] * d[:-2] + x['beta'][:, None] * d[2:])
    v = (dz ** 2 / x['w'][:, None]).mean(0)
    return v / v.sum() if v.sum() > 0 else np.full(3, 1 / 3)


def _ref_folge(tab, R):
    pos = tab.spalte('position', int)
    t = 0.5 * (tab.spalte('t_start', float) + tab.spalte('t_ende', float))
    idx = np.flatnonzero(R)
    o = np.argsort(pos[idx])
    tt = t[idx][o]
    if tt.size < 3:
        return dict(ordnung=o, beta=np.zeros(0), w=np.zeros(0), b=np.zeros(0)), tt
    be = (tt[1:-1] - tt[:-2]) / (tt[2:] - tt[:-2])
    return dict(ordnung=o, beta=be, w=1 + be ** 2 + (1 - be) ** 2, b=be * (1 - be) * (tt[2:] - tt[:-2])), tt


def _nu_loo(beta):
    """Effektive Freiheitsgrade der Leave-one-out-Varianz Σd²/Σw bei weißem ⟨N⟩: (Σ C_ii)²/Σ C_ij² mit C = A·Aᵀ."""
    n = beta.size + 2
    A = np.zeros((beta.size, n))
    for i, b in enumerate(beta):
        A[i, i], A[i, i + 1], A[i, i + 2] = -(1 - b), 1.0, -b
    C = A @ A.T
    return float(np.trace(C) ** 2 / (C ** 2).sum())


def _nullpunkt(tab, R, s2m, nu_m):
    x, tt = _ref_folge(tab, R)
    n = tt.size
    if n < 3:
        return dict(n=n, drift=None, diffusion=komponente(None, None, None, 'N²/s', 'Referenzfolge', False,
                                                          'weniger als drei gültige Referenzläufe'))
    N = tab.daten['N_mittel'][R][x['ordnung']]
    A = np.c_[np.ones(n), tt - tt.mean()]
    c, *_ = np.linalg.lstsq(A, N, rcond=None)
    res = N - A @ c
    se = float(np.sqrt(res @ res / max(n - 2, 1) / ((tt - tt.mean()) ** 2).sum())) if n > 2 else None
    d = N[1:-1] - ((1 - x['beta']) * N[:-2] + x['beta'] * N[2:])
    sw, sb = x['w'].sum(), x['b'].sum()
    s2_loo = float((d ** 2).sum() / sw)
    nu_l = _nu_loo(x['beta'])
    out = dict(n=n, drift=dict(wert=float(c[1]), einheit='N/s', u=se, quelle='Referenzfolge: lineare Regression',
                               hinweis='u ohne Berücksichtigung eines Zufallspfads'),
               sigma_loo=dict(wert=float(np.sqrt(d.var(ddof=1))), einheit='N', nu_eff=nu_l, n_werte=int(d.size),
                              hinweis='Streuung der Leave-one-out-Werte (wie σ̂_ref), ν_eff analytisch für weißes ⟨N⟩'))
    if not np.isfinite(s2m) or sb <= 0:
        out['diffusion'] = komponente(None, None, None, 'N²/s', 'Referenzfolge', False,
                                      'Boden von ⟨N⟩ aus den Fünfteln fehlt: Zufallspfad nicht vom Boden trennbar')
        return out
    # E[d²] = σ_m²·w + D·b (Brückenvarianz des Zufallspfads): Momentenschätzer, obere Grenze über ν_eff der
    # Leave-one-out-Varianz, Nachweis per F-Test gegen den Fünftelboden (ν_m)
    skala = sw / sb
    fk = _f_quantil(float(nu_l), float(nu_m)) if nu_m else np.inf
    out['diffusion'] = dict(wert=float(max(0.0, s2_loo - s2m) * skala), einheit='N²/s', nu=nu_l,
                            oben80=float(max(0.0, s2_loo * kappa(nu_l) ** 2 - s2m) * skala), s_gesamt=None,
                            boden=float(s2m), u=float(s2_loo * np.sqrt(2.0 / nu_l) * skala), identifiziert=True,
                            nachgewiesen=bool(s2m > 0 and s2_loo / s2m > fk), grund=None,
                            quelle='Referenzfolge: Leave-one-out gegen den Fünftelboden (Brückenvarianz β(1 − β)·Δt)',
                            hinweis='Varianzgröße D [N²/s] eines Zufallspfads, keine Streuung; u: Standardunsicherheit '
                                    'von D')
    return out


def _laufintern_mittel(tab, R, s2m, N_z, n_f):
    F = tab.daten['fuenftel_N_mittel'][R]
    n = int(R.sum())
    if n < 2 or n_f < 1 or not np.isfinite(F).all():
        return dict(mittel=None, streuung=komponente(None, None, None, 'N', 'Referenzläufe: F₅ − F₁', False,
                                                     'keine Fünftel'))
    DN = F[:, 1] - F[:, 0]
    b = 2.0 * N_z / n_f * s2m if np.isfinite(s2m) else None
    return dict(mittel=dict(wert=float(DN.mean()), einheit='N', u=float(DN.std(ddof=1) / np.sqrt(n)),
                            quelle='Referenzläufe: Mittel von D_N = F₅ − F₁'),
                streuung=komponente(float(DN.var(ddof=1)), b, n - 1, 'N', 'Referenzläufe: D_N = F₅ − F₁ über dem '
                                    'Fünftelboden', identifiziert=b is not None, nu_boden=n - 1))


# ── Projektion der Lⱼ-Abweichungen ─────────────────────────────────────────────────────────────────────
def _projektion(D, u, w):
    """Skalare Laufwerte der Abweichungen D (n, …) auf die Basis u (…) mit Gewichten w (…, reell, je Re/Im):
    â = Σ w·Re(ū·D)/Σ w|u|²; Rückgabe (Werte, U = Σ w|u|²)."""
    U = float((w * np.abs(u) ** 2).sum())
    if not U > 0:
        return None, 0.0
    a = (w[None] * np.real(np.conj(u)[None] * D)).reshape(D.shape[0], -1).sum(1) / U
    return a, U


def _modul(tab, Lj, k, s2c, nu_h, N_z, n_f, kk):
    """Komponenten eines Moduls aus seinen gültigen Lⱼ-Läufen (Maske Lj)."""
    n = int(Lj.sum())
    quelle = f'Lⱼ-Läufe (P0.8): kohärente Projektion über k ≤ {k} und Zellen'
    leer = dict(n=n, sigma_a=komponente(None, None, None, '1', quelle, False, f'{n} gültige Lⱼ-Läufe'),
                sigma_delta=komponente(None, None, None, '°', quelle, False, f'{n} gültige Lⱼ-Läufe'),
                rest=None, kohaerenz=None, laufintern=None)
    if n < 2:
        return leer
    X = tab.daten['Nk_zellen'][Lj][:, :, :k]                               # (n, 3, k)
    Nb = X.mean(0)
    D = X - Nb[None]
    gewichtet = bool(np.all(np.isfinite(s2c)) and np.all(s2c > 0))
    sig2 = s2c if gewichtet else np.ones(3)
    W = np.broadcast_to((1.0 / sig2)[:, None], Nb.shape).astype(float)
    u = Nb
    v = -1j * kk[None, :] * Nb
    a, U = _projektion(D, u, W)
    dl, V = _projektion(D, v, W)
    if a is None or dl is None:
        return dict(leer, sigma_a=komponente(None, None, None, '1', quelle, False, 'N̄⁽ʲ⁾ = 0: Basis entartet'),
                    sigma_delta=komponente(None, None, None, '°', quelle, False, 'N̄⁽ʲ⁾ = 0: Basis entartet'))
    # orthogonaler Rest je Harmonischer (Vielfaches q_jk des Zellbodens), Hebelwerte der Projektion
    Rr = D - a[:, None, None] * u[None] - dl[:, None, None] * v[None]
    Vck = ((Rr.real ** 2) + (Rr.imag ** 2)).sum(0) / (n - 1)                # (3, k)
    h = W * np.abs(u) ** 2 * (1.0 / U + kk[None, :] ** 2 / V)             # Summe der Hebel von Re und Im
    erw = sig2[:, None] * (2 - h)
    rest = []
    q = np.zeros(k)
    for i in range(k):
        nu_i = float((n - 1) * (2 - h[:, i]).sum())
        # Rest o²_c = q·σ²_c (Vielfaches des Zellbodens) hat dieselben Hebel wie der Boden: E[V] = (1 + q)·σ²_c·(2 − h)
        R_i = float(Vck[:, i].sum() / erw[:, i].sum()) if gewichtet else np.nan
        qi = max(0.0, R_i - 1.0) if gewichtet else 0.0
        k80 = kappa(nu_i)
        qo = max(0.0, R_i * k80 ** 2 - 1.0) if gewichtet else None
        fk = _f_quantil(nu_i, float(nu_h)) if nu_h else np.inf
        q[i] = qi
        rest.append(dict(k=i + 1, q=float(qi), q_oben80=None if qo is None else float(qo), verhaeltnis=_f(R_i),
                         nu=nu_i, nachgewiesen=bool(gewichtet and R_i > fk), einheit='Vielfaches des Zellbodens'))
    # Bodenanteil der Laufwerte einschließlich des orthogonalen Rests (ein Korrekturschritt)
    fa = float((W * np.abs(u) ** 2 * (1 + q[None, :])).sum() / U ** 2) if gewichtet else 0.0
    fd = float((W * np.abs(v) ** 2 * (1 + q[None, :])).sum() / V ** 2) if gewichtet else 0.0
    nu = n - 1
    sa = komponente(float(a.var(ddof=1)), fa, nu, '1', quelle, nu_boden=nu_h)
    sd = komponente(float(dl.var(ddof=1)), fd, nu, '°', quelle, nu_boden=nu_h, skala=np.degrees(1.0))
    # Kohärenz über k: Projektion je Harmonischer, Q = Σ_r Σ_k (â_rk − â_r)²/f_k
    koh = {}
    for name, basis, werte, B in (('amplitude', u, a, U), ('phase', v, dl, V)):
        je, gew, s2k = [], [], []
        for i in range(k):
            ai, Ui = _projektion(D[:, :, i], basis[:, i], W[:, i])
            if ai is None or Ui <= 1e-12 * B:
                je.append(None)
                gew.append(0.0)
                s2k.append(None)
                continue
            je.append(ai)
            gew.append(Ui)
            s2k.append(float(ai.var(ddof=1)))
        Qs, dof = 0.0, 0
        for i in range(k):
            if je[i] is None:
                continue
            Qs += float(((je[i] - werte) ** 2).sum() * gew[i]) if gewichtet else 0.0
            dof += 1
        dof = (dof - 1) * (n - 1)
        skala = 1.0 if name == 'amplitude' else np.degrees(1.0)
        bod = [None if g == 0 else 1.0 / g for g in gew]
        koh[name] = dict(Q=float(Qs) if gewichtet else None, nu=int(dof),
                         p=float(stats.chi2.sf(Qs, dof)) if gewichtet and dof > 0 else None,
                         streuung_je_k=[None if s is None else float(np.sqrt(max(0.0, s - b)) * skala)
                                        for s, b in zip(s2k, bod)],
                         s_gesamt_je_k=[None if s is None else float(np.sqrt(s) * skala) for s in s2k],
                         gewicht_je_k=[float(g / B) for g in gew],
                         hinweis='Q ~ χ²(ν) bei kohärenter Laufgröße über k; kleines p: Streuung hängt von k ab')
    # Fünftel: Amplituden- und Phasenänderung letztes − erstes Fünftel (Summe über Zellen)
    li = None
    Fk = tab.daten['fuenftel_Nk'][Lj][:, :, :k]
    if n_f >= 1 and np.isfinite(Fk).all() and gewichtet:
        dF = Fk[:, 1] - Fk[:, 0]
        uS = tab.daten['Nk_summe'][Lj][:, :k].mean(0)
        vS = -1j * kk * uS
        f_dF = 2.0 * N_z / n_f * float(s2c.sum())
        w1 = np.full(k, 1.0 / f_dF)
        da, Ua = _projektion(dF, uS, w1)
        dd, Vd = _projektion(dF, vS, w1)
        if da is not None and dd is not None:
            RF = dF - da[:, None] * uS[None] - dd[:, None] * vS[None]
            hF = w1 * np.abs(uS) ** 2 * (1 / Ua + kk ** 2 / Vd)
            verh = float(((RF.real ** 2 + RF.imag ** 2).sum() / (n - 1)) / (f_dF * (2 - hF)).sum())
            li = dict(amplitude_mittel=dict(wert=float(da.mean()), u=float(da.std(ddof=1) / np.sqrt(n)), einheit='1'),
                      phase_mittel=dict(wert=float(np.degrees(dd.mean())),
                                        u=float(np.degrees(dd.std(ddof=1)) / np.sqrt(n)), einheit='°'),
                      amplitude=komponente(float(da.var(ddof=1)), 1.0 / Ua, n - 1, '1',
                                           'Lⱼ-Läufe: Fünftelharmonische F₅ − F₁, Projektion auf N̄⁽ʲ⁾', nu_boden=nu_h),
                      phase=komponente(float(dd.var(ddof=1)), 1.0 / Vd, n - 1, '°',
                                       'Lⱼ-Läufe: Fünftelharmonische F₅ − F₁, Projektion auf −ik·N̄⁽ʲ⁾',
                                       nu_boden=nu_h, skala=np.degrees(1.0)),
                      orthogonal_verhaeltnis=verh,
                      hinweis='Änderung letztes − erstes Fünftel; orthogonal_verhaeltnis: Restvarianz/Boden '
                              '(Prüfgröße)')
    return dict(n=n, sigma_a=sa, sigma_delta=sd, rest=rest, kohaerenz=koh, laufintern=li, gewichtet=gewichtet,
                boden_anteil_a=float(fa / max(a.var(ddof=1), 1e-300)) if gewichtet else None,
                boden_anteil_delta=float(fd / max(dl.var(ddof=1), 1e-300)) if gewichtet else None)


# ── Piloten: Versatz, Jitter, Übertragung ────────────────────────────────────────────────────────────
def _piloten(tab, P, N_z):
    d = tab.daten
    ids = np.array(tab.konfig_ids())
    phi = d['phi_mittel_grad']
    sg = d['sigma_grad']
    dev, nus, je = [], 0, {}
    for kid in sorted(set(ids[P])):
        m = P & (ids == kid)
        n = int(m.sum())
        if n < 2:
            continue
        p = phi[m][:, 1:]
        mu, _ = kv.zirkulaer_mittel_grad(p, achse=0)
        dv = kv.wickel_grad(p - mu[None])
        dev.append(dv)
        nus += n - 1
        je[kid] = dict(n=n, jitter_grad=np.sqrt(np.mean(sg[m][:, 1:] ** 2, 0)).tolist())
    out = dict(n=int(P.sum()), nu=nus, je_konfiguration=je)
    quelle = 'Pilotläufe (P0.10): Laufmittel φ̄ⱼ je Konfiguration, abzüglich σⱼ²/N_z'
    if not dev:
        out['versatz'] = [komponente(None, None, None, '°', quelle, False, 'keine Pilotkonfiguration mit ≥ 2 '
                                     'gültigen Läufen') for _ in range(2)]
        out['jitter'] = [None, None]
        out['korrelation_versatz'] = None
        return out
    dv = np.concatenate(dev, 0)
    s2 = (dv ** 2).sum(0) / nus
    s2j = np.mean(sg[P][:, 1:] ** 2, 0)
    out['versatz'] = [komponente(float(s2[j]), float(s2j[j] / N_z), nus, '°', quelle, nu_boden=np.inf)
                      for j in range(2)]
    nu_j = int(P.sum()) * max(N_z - 1, 1)
    out['jitter'] = [komponente(float(s2j[j]), 0.0, nu_j, '°', 'Pilotläufe: σⱼ je Zyklus (RMS), erfasst')
                     for j in range(2)]
    c = (dv[:, 0] * dv[:, 1]).sum() / nus
    r = c / np.sqrt(s2[0] * s2[1]) if s2[0] > 0 and s2[1] > 0 else np.nan
    out['korrelation_versatz'] = dict(wert=_f(r), nu=nus, einheit='1',
                                      hinweis='Korrelation der Laufmittelabweichungen der Module 2 und 3 '
                                              '(mit Jitteranteil)')
    return out


def kovarianz_harmonische(Nbar, rho, s2_a, s2_d_rad, k, boden_summe, q=None, s2c=None):
    """Modellkovarianz (2×2, Re/Im) der Summenharmonischen N_k einer Konfiguration aus den nicht erfassten Laufgrößen:
    Σⱼ σ²_a,j·g gᵀ + k²σ²_δ,j·h hᵀ mit g = (Re, Im)(ρⱼₖ N̄ⱼₖ), h = (Re, Im)(−i·ρⱼₖ N̄ⱼₖ), dazu Boden (Summe über die
    Zellen, je Re/Im) und orthogonaler Rest q_jk·Σ_c σ²_c·|ρⱼₖ|². Nbar (3,) Summenharmonische je Modul bei k,
    rho (3,)."""
    C = np.eye(2) * boden_summe
    for j in range(3):
        z = rho[j] * Nbar[j]
        g = np.array([z.real, z.imag])
        hh = np.array([(-1j * z).real, (-1j * z).imag])
        C = C + s2_a[j] * np.outer(g, g) + k ** 2 * s2_d_rad[j] * np.outer(hh, hh)
        if q is not None and s2c is not None:
            C = C + np.eye(2) * q[j] * float(np.sum(s2c)) * abs(rho[j]) ** 2
    return C


def _uebertragung(tab, P, L, module, boden, kmax=3):
    """Erfasster Phasenanteil und Übertragungstest L → K an den Piloten (zweite Momente, N̄⁽ʲ⁾ und Zeiger)."""
    d = tab.daten
    ids = np.array(tab.konfig_ids())
    if any(m['sigma_a']['wert'] is None or m['sigma_delta']['wert'] is None for m in module):
        return dict(pruefbar=False, grund='Laufgrößen eines Moduls nicht identifizierbar')
    s2c = boden['s2_h_zellen']
    if not np.all(np.isfinite(s2c)):
        return dict(pruefbar=False, grund='Boden nicht bestimmbar')
    Nbar = np.stack([d['Nk_summe'][L[j]][:, :kmax].mean(0) for j in range(3)])            # (3, kmax)
    s2a = np.array([m['sigma_a']['wert'] ** 2 for m in module])
    s2d = np.array([np.radians(m['sigma_delta']['wert']) ** 2 for m in module])
    q = np.array([[r['q'] for r in m['rest'][:kmax]] for m in module])                    # (3, kmax)
    erg = []
    for kk in range(1, kmax + 1):
        obs, mod, erf, nu = 0.0, 0.0, 0.0, 0
        for kid in sorted(set(ids[P])):
            m = P & (ids == kid)
            n = int(m.sum())
            if n < 2:
                continue
            Nk = d['Nk_summe'][m][:, kk - 1]
            rho = d['zeiger'][m][:, :, kk - 1] / tab.koepfe[np.flatnonzero(m)[0]]['n_zyklen']
            Cap = (rho * Nbar[None, :, kk - 1]).sum(1)                                     # erfasster Anteil je Lauf
            obs += float(((Nk - Nk.mean()).real ** 2 + (Nk - Nk.mean()).imag ** 2).sum())
            erf += float(((Cap - Cap.mean()).real ** 2 + (Cap - Cap.mean()).imag ** 2).sum())
            rb = rho.mean(0)
            C = kovarianz_harmonische(Nbar[:, kk - 1], rb, s2a, s2d, kk, float(s2c.sum()), q[:, kk - 1], s2c)
            mod += float(np.trace(C)) * (n - 1)
            nu += n - 1
        if nu == 0:
            erg.append(dict(k=kk, pruefbar=False))
            continue
        gesamt = mod + erf
        ratio = obs / gesamt if gesamt > 0 else None
        nu2 = 2 * nu
        p = None if ratio is None else float(2 * min(stats.chi2.cdf(ratio * nu2, nu2), stats.chi2.sf(ratio * nu2, nu2)))
        erg.append(dict(k=kk, pruefbar=True, varianz_beobachtet=obs / nu, varianz_modell=gesamt / nu,
                        erfasster_anteil=float(erf / gesamt) if gesamt > 0 else None,
                        erfasster_anteil_beobachtet=float(erf / obs) if obs > 0 else None,
                        verhaeltnis=_f(ratio), nu=nu2, p_zweiseitig=p))
    return dict(pruefbar=True, harmonische=erg,
                hinweis='Spur der 2×2-Kovarianz von Re/Im N_k je Pilotkonfiguration, gepoolt; Modell: erfasster '
                        'Anteil aus den gemessenen Zeigern und N̄⁽ʲ⁾ plus nicht erfasste Lⱼ-Komponenten, Boden und '
                        'orthogonaler Rest; p näherungsweise (χ² mit 2ν, isotrop); keine Mittelwerte, keine Residuen')


def _technik(tab, P, alle):
    d = tab.daten
    tp = d['t_phi'][P][:, 1:]
    tmin, tmax = d['temperatur_min_zellen'][alle], d['temperatur_max_zellen'][alle]
    fm = tab.spalte('f_mittel', float)[alle]
    ok = np.isfinite(tp)
    T0 = 0.5 * (tmin + tmax)
    return dict(t_phi_s=dict(mittel=_f(np.nanmean(tp)) if ok.any() else None,
                             streuung=_f(np.nanstd(tp, ddof=1)) if ok.sum() > 1 else None, einheit='s'),
                temperatur_C=dict(mittel=_f(np.nanmean(T0)), streuung_im_lauf=_f(np.nanmean(tmax - tmin) /
                                                                                 (2 * np.sqrt(2 / np.pi))),
                                  einheit='°C', hinweis='Streuung im Lauf aus E[max − min] = 2σ·√(2/π) (Halbnormal)'),
                f_streuung_hz=_f(np.std(fm, ddof=1)) if fm.size > 1 else None)


# ── Hauptfunktion ────────────────────────────────────────────────────────────────────────────────────
def schaetzen(tab, gueltig, k, uebertragungstest=True):
    """Komponentenschätzer der Laufgrößen aus den gültigen Phase-0-Läufen bei k (siehe Moduldocstring)."""
    k = int(k)
    gueltig = np.asarray(gueltig, bool)
    if gueltig.shape != (len(tab),):
        raise ValueError(f'Laufgrößen: Maske der Form {gueltig.shape} passt nicht zu {len(tab)} Läufen')
    if k < 1 or k > tab.k_voll:
        raise ValueError(f'Laufgrößen: k = {k} außerhalb 1 … {tab.k_voll}')
    N_z, n_f = fenster(tab)
    art = tab.spalte('laufart', object)
    mod = tab.spalte('modul', object)
    grp = np.array([kk['konfiguration']['gruppe'] for kk in tab.koepfe])
    p0 = _phase0(tab) & gueltig
    R = p0 & (art == 'R')
    L = [p0 & (art == 'L') & (mod == j) for j in (1, 2, 3)]
    P = p0 & (art == 'K') & (grp == 'pilot')
    f_soll = float(tab.koepfe[0]['f_soll'])
    kk = np.arange(1, k + 1, dtype=float)
    bo = _boden(tab, R, k, N_z, n_f)
    s2m = bo['s2_m_summe']
    anteile = _zellanteile_mittel(tab, R) if R.sum() >= 3 else np.full(3, 1 / 3)
    if np.isfinite(s2m):
        bo['sigma_mittel_zellen'] = [komponente(float(s2m * anteile[c]), 0.0, bo['nu_m'], 'N',
                                                'Fünftelboden der Summe, Zellanteile aus den Leave-one-out-Werten')
                                     for c in range(3)]
    else:
        bo['sigma_mittel_zellen'] = [komponente(None, None, None, 'N', 'Referenzläufe', False, 'keine Fünftel')
                                     for _ in range(3)]
    bo['zellanteile_mittel'] = anteile
    nu_h = bo.get('nu_h')
    module = [_modul(tab, L[j], k, bo['s2_h_zellen'], nu_h, N_z, n_f, kk) for j in range(3)]
    pil = _piloten(tab, P, N_z)
    nul = _nullpunkt(tab, R, s2m, bo.get('nu_m'))
    lim = _laufintern_mittel(tab, R, s2m, N_z, n_f)
    ueb = (_uebertragung(tab, P, L, module, bo, min(3, k)) if uebertragungstest
           else dict(pruefbar=False, grund='nicht angefordert'))
    out = dict(
        version=VERSION, format=VERSION,
        bindung=dict(k=k, N_z=int(N_z), n_fuenftel=int(n_f), T_a_s=float(N_z / f_soll), f_soll=f_soll,
                     n_R=int(R.sum()), n0=[int(x.sum()) for x in L], n_pilot=int(P.sum())),
        boden={x: v for x, v in bo.items() if x not in ('s2_h_je_k',)},
        nullpunkt=nul, laufintern=dict(mittel_N=lim, module=[m['laufintern'] for m in module]),
        module=[{x: v for x, v in m.items() if x != 'laufintern'} for m in module],
        versatz=dict(module=[None] + pil['versatz'], korrelation=pil['korrelation_versatz'], nu=pil['nu'],
                     n_pilot=pil['n']),
        jitter=dict(module=[None] + pil['jitter'], je_konfiguration=pil['je_konfiguration']),
        uebertragung=ueb, technik=_technik(tab, P, p0),
        hinweis=('marginale obere 80-%-Grenzen je Komponente; keine gemeinsame 80-%-Garantie über mehrere '
                 'Komponenten'))
    out['komponenten'] = _flach(out)
    out['nicht_identifizierbar'] = _nicht_identifizierbar(out)
    return out


def _wert(c, feld='wert', leer=None):
    return leer if c is None or c.get(feld) is None else c[feld]


def _flach(lg):
    m, v, j = lg['module'], lg['versatz']['module'], lg['jitter']['module']
    out = {}
    for name, liste, key in (('sigma_a', m, 'sigma_a'), ('sigma_delta_grad', m, 'sigma_delta')):
        out[name] = [_wert(x[key]) for x in liste]
        out[name + '_nu'] = [_wert(x[key], 'nu') for x in liste]
        out[name + '_oben80'] = [_wert(x[key], 'oben80') for x in liste]
    for name, liste in (('sigma_off_grad', v), ('sigma_jitter_grad', j)):
        out[name] = [0.0] + [_wert(x) for x in liste[1:]]
        out[name + '_nu'] = [None] + [_wert(x, 'nu') for x in liste[1:]]
        out[name + '_oben80'] = [0.0] + [_wert(x, 'oben80') for x in liste[1:]]
    b = lg['boden']
    out['sigma_h_zellen'] = [_wert(x) for x in b['sigma_h_zellen']]
    out['sigma_h_nu'] = b.get('nu_h')
    out['sigma_mittel_zellen'] = [_wert(x) for x in b['sigma_mittel_zellen']]
    out['sigma_mittel_nu'] = b.get('nu_m')
    out['einheiten'] = dict(sigma_a='1 (relativ)', sigma_delta_grad='°', sigma_off_grad='°', sigma_jitter_grad='° je '
                            'Zyklus', sigma_h_zellen='N je Re/Im', sigma_mittel_zellen='N')
    return out


def _nicht_identifizierbar(lg):
    out = []
    for j, m in enumerate(lg['module'], start=1):
        for key in ('sigma_a', 'sigma_delta'):
            if not m[key]['identifiziert']:
                out.append(dict(komponente=f'{key}, Modul {j}', grund=m[key]['grund']))
    for j, c in enumerate(lg['versatz']['module'][1:], start=2):
        if not c['identifiziert']:
            out.append(dict(komponente=f'sigma_off, Modul {j}', grund=c['grund']))
    if not lg['nullpunkt']['diffusion']['identifiziert']:
        out.append(dict(komponente='Nullpunktdiffusion', grund=lg['nullpunkt']['diffusion']['grund']))
    for name in ('Drift zwischen Phase 0 und Phase 1 und zwischen Messtagen', 'farbiger Jitter (Fünftelzeiger fehlen)',
                 'zwischen Modulen korrelierter Jitter je Zyklus', 'lastabhängiger Jitter außerhalb der Piloten',
                 'gemeinsame Laufzeitschwankung der Kette gegen modulweises δ',
                 'Amplituden- und Phasenstreuung der Kombinationsläufe (nur Übertragungstest an den Piloten)'):
        out.append(dict(komponente=name, grund='aus Phase-0-Zusammenfassungen nicht identifizierbar: benannte '
                                               'Sensitivität'))
    return out


def komponenten(lg):
    """Flache Komponenten als numpy-Felder (je Modul j = 1, 2, 3; nicht bestimmte Werte als nan)."""
    f = lg['komponenten']
    return {k: (np.array([np.nan if x is None else x for x in v], float) if isinstance(v, list) else v)
            for k, v in f.items() if k != 'einheiten'}
