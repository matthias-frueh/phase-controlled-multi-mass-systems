"""E3-Grenzen im Regelstand 2026-11: Option B der Entscheidungsvorlage vom 19.10.2026 (Abschnitt 4) mit
beschreibendem Rückfall je Prüfgröße (Auftrag vom 20.10.2026, Abschnitt 9). Gilt nur für Profile mit
regeln.stand(profil) == '2026-11'; die historischen Profile rechnen in kontrollen.e3_auswerten unverändert.

Prüfmenge (e3.pruefmenge = 'schnitt21_triphasik', e3.pruefzahl = 43): die 21 Schnittpunkte mit je zwei E3a-Prüfungen
(Module 2 und 3) und E3b am Triphasik-Punkt, m = 43 fest. Nicht auswertbare Punkte, ein fehlender Triphasik-Punkt oder
der Rückfall einer Prüfgröße verringern m nicht; jede Prüfung trägt das Niveau α/m mit α = 0,05 (Bonferroni).

E3a (e3.grenzen.e3a = 't_quantil_gefaltet'): x̂ = Δφⱼ^Z, u² = Var_b(Δφ_b) + u_Quant² (Bootstrap mit T- und
Δδ-Ziehungen wie bisher), korrigiert ũ² = n_A/(n_A − 1)·u² auf das ganze u² (konservativ für die bekannten Anteile T,
Δδ, Quantisierung), ν = n_A − 1. Auffällig, wenn |x̂| > s + k·ũ (s = 0,1°) mit dem gefalteten Faktor k, der
  F̄_t(k; ν) + F̄_t(k + 2·s/ũ; ν) = α/m
löst (F̄_t obere Verteilungsfunktion von t_ν). Die zweite Summe ist die Gegenseite (x̂ < −s − k·ũ bei wahrem Wert +s);
k liegt zwischen dem einseitigen t(1 − α/m; ν) (s/ũ → ∞) und t(1 − α/(2m); ν) (s/ũ → 0). Größe am Rand: in beiden
Grenzen analytisch genau α/m (einseitiger t-Test bzw. Vereinigungsschranke), dazwischen kleiner, gezeigt durch
deterministische Quadratur über die Verteilung von ũ (tests/test_e3_grenzen.py); die Regel ohne Gegenseite hielte
bis 2·α/m. Unauffällig, wenn |x̂| + t(0,95; ν)·ũ ≤ s; Fehlerrate ≤ 0,05 unter Gauß- und χ²-Annahme (einseitige
Projektion |x̂| ≥ ±x̂).

E3b (e3.grenzen.e3b = 'rice_kappa_lambda_max'): komplexe Replikate d_b = (R₋₁,b − R̂₋₁,b)/|R̂₊₁,b| vor der
Betragsbildung, n* = min(n_A, n₀,₁, n₀,₂, n₀,₃), Σ̂ = n*/(n* − 1)·Cov_b(Re d_b, Im d_b), ŝ² = λ_max(Σ̂),
ρ̂ = √(λ_min/λ_max) (Anisotropie), ν = n* − 1. Auffällig, wenn q_Z > κ·ŝ·Rice⁻¹(1 − α/m; q_tol/(κ·ŝ)) mit
κ = t(1 − α/m; ν)/z(1 − α/m); unauffällig, wenn q_Z + t(0,95; ν)·ŝ ≤ q_tol. Größe von „auffällig“ am Rand unter
den Annahmen unten: < α/m auf dem Raster der Quadratur (ν = 5 und 19, ρ von 1 bis 0,03, Richtung, t = q_tol/s von
0,25 bis 40; Vergleichswerte der Nachprüfung 0,908 und 0,146·α/m), Grenzwert α/m für ρ → 0 und t → ∞ (einseitiger
t-Test); „unauffällig“ ≤ 0,05 aus der Projektionsungleichung |d̂| ≥ Re(d̂·e^{−iθ}) und λ_max(Σ̂) ≥ eᵀΣ̂e.

Freiheitsgrade (e3.grenzen.nu = 'min_n_minus_1', nu_min): bei B < 10 000 gültigen Replikaten tritt in alle Quantile
ν_eff = (1/ν + 1/(B − 1))⁻¹; ν_eff < nu_min (5) → „nicht prüfbar“ mit Grund.

Rückfall je Prüfgröße (e3.rueckfall = 'je_pruefgroesse'), Stufen:
  dreiwertig     auffällig / unauffällig / unbestimmt
  einseitig      auffällig / keine Überschreitung nachgewiesen (kein „unauffällig“)
  beschreibend   Zahlen ohne Aussage (Grund)
  nicht prüfbar  Prüfung ohne Aussage (Grund); m bleibt 43
Eine Prüfgröße fällt auf „beschreibend“ zurück, wenn die Unsicherheit von T fehlt oder unvollständig ist, wenn
Replikate ungültig sind (die Gültigkeit am Rand ist für eine gestutzte Replikatverteilung nicht gezeigt) oder wenn
Teil B (Kalibriersimulation, A9.11) das Kriterium „auffällig“ oder die Modellprüfung als verfehlt ausweist; auf
„einseitig“, wenn Teil B nur das Kriterium „unauffällig“ als verfehlt ausweist. Weist Teil B keine Kriterien aus,
bleibt die Stufe, und das Ergebnis vermerkt, dass weder die Kriterien von A9.11 noch die Modellprüfung gerechnet
sind (keine Kalibrierabnahme).
Gesamturteil: „auffällig“, wenn eine Prüfung auffällig ist; „unauffällig“ nur, wenn beide Prüfgrößen dreiwertig sind
und alle 43 Prüfungen ausgewertet und unauffällig; „unbestimmt“, wenn beide dreiwertig sind und sonst; „keine
Überschreitung nachgewiesen“, wenn mindestens eine Prüfung ausgewertet ist, keine auffällig, aber nicht beide
Prüfgrößen dreiwertig; sonst ohne Urteil (Grund). „Keine Überschreitung nachgewiesen“ heißt nicht „unauffällig“.

Annahmen der Grenzen (benannt, nicht je Kampagne geprüft): x̂ bzw. d̂ näherungsweise normal (E3b: Nenner |R̂₊₁|
nahezu fest, seine Streuung steht als nenner_cv im Ergebnis), Läufe je Quelle unabhängig ohne Drift, Σ̂ ≈ Wishart mit
mindestens ν Freiheitsgraden und unabhängig von d̂ bzw. ũ² ≈ u²·χ²_ν/ν unabhängig von x̂, Rauschbias klein gegen
die Schwelle. Eine eingesetzte Rice-Verteilung ist bei geschätzter oder anisotroper Streuung keine exakte Grenze;
erst κ und λ_max halten die Größe am Rand ≤ α/m (Quadratur über ν ≥ nu_min, Anisotropie, Richtung und Abstand).
Nicht geprüft: Drift, serielle Korrelation, Schiefe, Rauschen im Nenner, gestutzte T-Ziehungen. Die Modellprüfung
(Kalibrierung von ŝ, Isotropie über ρ̂, ν über die Streuung von ŝ², PIT von q_Z) gehört in die Kalibrierkampagnen;
dafür stehen Σ̂, ŝ, ρ̂, ν, n_A und n₀ⱼ im Ergebnis.
"""
import math

import numpy as np
from scipy import optimize, stats

from .regeln import NORMATIVE_ZAHLEN

VERSION = 'e3_grenzen-0.1'
ALPHA = 0.05                            # Gesamtniveau von E3 (Bonferroni über m Prüfungen, A9.13)
N_SCHNITT = 21                          # Schnittpunkte der Prüfmenge (konventionen.SCHNITT_PHI2)
B_NORMATIV = NORMATIVE_ZAHLEN['bootstrap_B']
NU_MIN_GEPRUEFT = 5                     # kleinste Freiheitsgradzahl, für die die Randgültigkeit gerechnet ist
SINGULAER = 1e-12                       # λ_min ≤ 10⁻¹²·λ_max: Σ̂ gilt als singulär
STREUUNG_NULL_E3B = 1e-12               # ŝ ≤ 10⁻¹² (d̂ ist auf |R̂₊₁| bezogen): nur Rundungsrest, Streuung null
STREUUNG_NULL_E3A_GRAD = 1e-9           # ũ ≤ 10⁻⁹°: nur Rundungsrest, Streuung null
GRENZEN = dict(e3a='t_quantil_gefaltet', e3b='rice_kappa_lambda_max', nu='min_n_minus_1', unauffaellig='t_0.95')
STUFEN = ('dreiwertig', 'einseitig', 'beschreibend', 'nicht prüfbar')
ERGEBNISSE = ('auffällig', 'unauffällig', 'unbestimmt', 'keine Überschreitung nachgewiesen')
KEINE_UEBERSCHREITUNG = 'keine Überschreitung nachgewiesen'
# Felder des Kurzbefunds je Kampagne (harness.kampagnen._e3_kurz) für die Modellprüfung in den Kalibrierkampagnen
KURZ_E3A = ('wert', 'u', 'nu', 'nu_eff', 'n_A', 'B_gueltig', 'k', 'untere_grenze', 'obere_grenze')
KURZ_E3B = ('d_Z', 'sigma', 's_hat', 'rho_hat', 'lambda_max', 'lambda_min', 'richtung_grad', 'winkel_d_grad', 'nu',
            'nu_eff', 'n_A', 'n0', 'n_stern', 'B', 'B_gueltig', 'kappa', 'kritisch', 't95', 'obere_grenze', 'nenner_cv',
            'ergebnis', 'grund')
ANNAHMEN = (
    'x̂ (E3a) bzw. d̂ (E3b) näherungsweise normal; E3b: Nenner |R̂₊₁| nahezu fest (Streuung: nenner_cv)',
    'Läufe je Quelle unabhängig, ohne Drift und serielle Korrelation',
    'ũ² ≈ u²·χ²_ν/ν bzw. Σ̂ ≈ Wishart(ν, Σ)/ν mit ν = min(n) − 1, unabhängig vom Schätzer; bekannte Anteile (T, Δδ, '
    'Quantisierung, Zelllagen) machen die Schätzung nur weniger variabel',
    'Rauschbias klein gegen die Schwelle',
    'bei B < 10 000 Replikaten zusätzliches Monte-Carlo-Rauschen der Streuung über ν_eff = (1/ν + 1/(B − 1))⁻¹',
)


# ── Regelwerte ─────────────────────────────────────────────────────────────────────────────────────────
def regeln_lesen(profil):
    """Die E3-Regeln des Regelstands 2026-11 aus dem Profil, streng geprüft: nicht unterstützte Werte → ValueError
    (kein stiller Ersatzweg). Rückgabe dict(schwellen, m, alpha, alpha_m, rueckfall, pruefmenge, e3b_form, grenzen)."""
    sw = profil.wert('e3.schwellen')
    m = profil.wert('e3.pruefzahl')
    rf = profil.wert('e3.rueckfall')
    pm = profil.wert('e3.pruefmenge')
    form = profil.wert('e3.e3b_form')
    gr = profil.wert('e3.grenzen')
    if not isinstance(sw, dict) or set(sw) != {'phase_grad', 'q_tol'} or not all(
            isinstance(sw[k], (int, float)) and math.isfinite(sw[k]) and sw[k] > 0 for k in sw):
        raise ValueError(f'e3.schwellen {sw!r} nicht unterstützt (phase_grad und q_tol, endlich und positiv)')
    if pm != 'schnitt21_triphasik':
        raise ValueError(f'e3.pruefmenge {pm!r} nicht unterstützt (nur „schnitt21_triphasik“)')
    if isinstance(m, bool) or not isinstance(m, int) or m != 2 * N_SCHNITT + 1:
        raise ValueError(f'e3.pruefzahl {m!r} nicht unterstützt (Prüfmenge schnitt21_triphasik: m = 43 fest)')
    if rf != 'je_pruefgroesse':
        raise ValueError(f'e3.rueckfall {rf!r} nicht unterstützt (Regelstand 2026-11: nur „je_pruefgroesse“)')
    if form != 'differenz':
        raise ValueError(f'e3.e3b_form {form!r} nicht unterstützt (nur „differenz“)')
    if not isinstance(gr, dict) or set(gr) != set(GRENZEN) | {'nu_min'}:
        raise ValueError(f'e3.grenzen {gr!r}: Schlüssel {sorted(set(GRENZEN) | {"nu_min"})} verlangt')
    for k, v in GRENZEN.items():
        if gr[k] != v:
            raise ValueError(f'e3.grenzen.{k} = {gr[k]!r} nicht unterstützt (nur {v!r})')
    nm = gr['nu_min']
    if isinstance(nm, bool) or not isinstance(nm, int) or nm < NU_MIN_GEPRUEFT:
        raise ValueError(f'e3.grenzen.nu_min = {nm!r} nicht unterstützt (ganzzahlig, ≥ {NU_MIN_GEPRUEFT}: darunter ist '
                         'die Gültigkeit am Rand nicht gerechnet)')
    return dict(schwellen=dict(phase_grad=float(sw['phase_grad']), q_tol=float(sw['q_tol'])), m=m, alpha=ALPHA,
                alpha_m=ALPHA / m, rueckfall=rf, pruefmenge=pm, e3b_form=form, grenzen=dict(gr))


def nu_eff(nu, B):
    """Freiheitsgrade der Quantile: ν bei mindestens 10 000 gültigen Replikaten, sonst (1/ν + 1/(B − 1))⁻¹
    (Monte-Carlo-Rauschen der Bootstrap-Streuung, Vorlage 4.2)."""
    nu = float(nu)
    if B >= B_NORMATIV:
        return nu
    return 1.0 / (1.0 / nu + 1.0 / (B - 1.0))


# ── E3a ────────────────────────────────────────────────────────────────────────────────────────────────
def e3a_faktor(nu, tau, alpha_m):
    """Gefalteter Faktor k(τ) mit F̄_t(k; ν) + F̄_t(k + 2τ; ν) = α/m, τ = s/ũ ≥ 0 (τ = inf: einseitig)."""
    k1, k2 = float(stats.t.isf(alpha_m, nu)), float(stats.t.isf(alpha_m / 2, nu))
    if not np.isfinite(tau):
        return k1
    if tau < 0:
        raise ValueError('τ < 0')

    def f(k):
        return float(stats.t.sf(k, nu) + stats.t.sf(k + 2 * tau, nu)) - alpha_m
    if f(k1) <= 0:                      # Gegenseite unter der Rechengenauigkeit
        return k1
    if f(k2) >= 0:
        return k2
    return float(optimize.brentq(f, k1, k2, xtol=1e-13, rtol=1e-14))


def _ungueltig_grund(n_ung, B):
    return (f'{n_ung} von {B} Replikaten ungültig (ausgelassen): Gültigkeit am Rand für eine gestutzte '
            'Replikatverteilung nicht gezeigt, keine Aussage')


def e3a_pruefung(x, u2, n_A, B, B_gueltig, schwelle, alpha_m, nu_min):
    """Eine E3a-Prüfung aus dem vorzeichenbehafteten Schätzer x̂ [°], u² (Bootstrap-Varianz der gültigen Replikate
    plus Quantisierung, ohne Korrektur), der Zahl gültiger Kombinationsläufe n_A und der Zahl der Replikate (alle,
    gültige). Rückgabe der Kenngrößen mit „ergebnis“ (dreiwertig vor dem Rückfall) oder None und „grund“."""
    out = dict(wert=float(x), u_roh=float(np.sqrt(u2)) if np.isfinite(u2) and u2 >= 0 else float('nan'), n_A=int(n_A),
               B=int(B), B_gueltig=int(B_gueltig), nu=None, nu_eff=None, u=None, faktor_n=None, k=None,
               k_einseitig=None, t95=None, untere_grenze=None, obere_grenze=None, ergebnis=None, grund=None)
    if n_A < 2 or B_gueltig < 2:
        out['grund'] = f'zu wenige Läufe oder Replikate (n_A = {n_A}, B = {B_gueltig})'
        return out
    nu = n_A - 1
    ne = nu_eff(nu, B_gueltig)
    fak = n_A / (n_A - 1)
    out.update(nu=int(nu), nu_eff=float(ne), faktor_n=float(fak))
    if ne < nu_min:
        out['grund'] = f'zu wenige Freiheitsgrade: ν_eff = {ne:.3g} < {nu_min} (n_A = {n_A})'
        return out
    if not (np.isfinite(x) and np.isfinite(u2)):
        out['grund'] = 'nicht endliche Prüfgröße oder Unsicherheit'
        return out
    u = float(np.sqrt(fak * max(u2, 0.0)))
    if u <= STREUUNG_NULL_E3A_GRAD:
        out['grund'] = ('Unsicherheit null oder nur Rundungsrest (Modellvoraussetzung einer geschätzten Streuung '
                        'verletzt)')
        return out
    k = e3a_faktor(ne, schwelle / u, alpha_m)
    t95 = float(stats.t.isf(0.05, ne))
    lo, hi = abs(x) - k * u, abs(x) + t95 * u
    erg = 'auffällig' if lo > schwelle else ('unauffällig' if hi <= schwelle else 'unbestimmt')
    out.update(u=u, k=float(k), k_einseitig=float(stats.t.isf(alpha_m, ne)), t95=t95, untere_grenze=float(lo),
               obere_grenze=float(hi), ergebnis=erg)
    if B_gueltig < B:
        out.update(ergebnis=None, grund=_ungueltig_grund(B - B_gueltig, B))
    return out


# ── E3b ────────────────────────────────────────────────────────────────────────────────────────────────
RICE_ASYMPTOTISCH = 1e4                 # ab hier Rice⁻¹ über b + z + 1/b (SciPy versagt oberhalb etwa 10⁵)


def rice_quantil(p_ober, b):
    """Rice⁻¹(1 − p; b) zur Skala 1 (Betrag von b + N₂(0, I)); b = 0: Rayleigh. Für b > 10⁴ die obere Näherung
    b + z(1 − p) + 1/b: das Quantil ist b + z + 1/(2b) + O(b⁻²), die Näherung liegt darüber (konservativ)."""
    b = float(b)
    if not np.isfinite(b) or b < 0:
        raise ValueError(f'Rice-Parameter {b!r}')
    if b == 0.0:
        return float(stats.rayleigh.isf(p_ober))
    if b > RICE_ASYMPTOTISCH:
        return b + float(stats.norm.isf(p_ober)) + 1.0 / b
    return float(stats.rice.isf(p_ober, b))


def e3b_kappa(nu, alpha_m):
    return float(stats.t.isf(alpha_m, nu) / stats.norm.isf(alpha_m))


def e3b_kritisch(s, nu, q_tol, alpha_m):
    """Kritischer Wert von „auffällig“: κ·ŝ·Rice⁻¹(1 − α/m; q_tol/(κ·ŝ))."""
    ks = e3b_kappa(nu, alpha_m) * float(s)
    return ks * rice_quantil(alpha_m, q_tol / ks)


def e3b_kovarianz(d_b, n_stern):
    """Σ̂ = n*/(n* − 1)·Cov_b(Re d_b, Im d_b) aus den gültigen Replikaten (ddof = 1)."""
    z = np.asarray(d_b, complex)
    X = np.c_[z.real, z.imag]
    return n_stern / (n_stern - 1.0) * np.cov(X, rowvar=False, ddof=1)


def e3b_pruefung(d, d_b, n_A, n0, q_tol, alpha_m, nu_min, nenner_b=None, q=None):
    """E3b aus dem komplexen Schätzer d̂ = (R₋₁ − R̂₋₁)/|R̂₊₁|, seinen Replikaten d_b (ungültige als nicht endliche
    Werte), n_A und n₀ⱼ; q: q_Z wie im historischen Feld (sonst |d̂|). Rückgabe der Kenngrößen (Σ̂ als
    [Σ_rr, Σ_ri, Σ_ii], ŝ, ρ̂, Richtung der großen Achse, ν, ν_eff, κ, Grenzen) mit „ergebnis“ (dreiwertig vor dem
    Rückfall) oder None und „grund“."""
    d = complex(d)
    db = np.asarray(d_b, complex)
    ok = np.isfinite(db)
    n0 = [int(x) for x in n0]
    ns = int(min([int(n_A)] + n0))
    out = dict(q_Z=float(abs(d) if q is None else q), d_Z=[float(d.real), float(d.imag)], n_A=int(n_A), n0=n0,
               n_stern=ns, B=int(db.size), B_gueltig=int(ok.sum()), sigma=None, s_hat=None, lambda_max=None,
               lambda_min=None, rho_hat=None, richtung_grad=None,
               winkel_d_grad=float(np.degrees(np.angle(d))) if d != 0 else None,
               nu=None, nu_eff=None, kappa=None, kritisch=None, t95=None, obere_grenze=None, nenner_cv=None,
               ergebnis=None, grund=None)
    if nenner_b is not None:
        nb = np.asarray(nenner_b, float)
        nb = nb[np.isfinite(nb)]
        if nb.size > 1 and nb.mean() > 0:
            out['nenner_cv'] = float(nb.std(ddof=1) / nb.mean())
    if ns < 2 or ok.sum() < 3:
        out['grund'] = f'zu wenige Läufe oder Replikate (n* = {ns}, B = {int(ok.sum())})'
        return out
    S = e3b_kovarianz(db[ok], ns)
    out['sigma'] = [float(S[0, 0]), float(S[0, 1]), float(S[1, 1])]
    nu = ns - 1
    ne = nu_eff(nu, int(ok.sum()))
    out.update(nu=int(nu), nu_eff=float(ne))
    if not np.all(np.isfinite(S)) or not np.isfinite(d):
        out['grund'] = 'nicht endliche Kovarianz oder Prüfgröße'
        return out
    lam, V = np.linalg.eigh(0.5 * (S + S.T))
    lmin, lmax = float(lam[0]), float(lam[1])
    out.update(lambda_max=lmax, lambda_min=lmin,
               richtung_grad=float(np.degrees(np.arctan2(V[1, 1], V[0, 1])) % 180.0))
    if lmax <= STREUUNG_NULL_E3B ** 2 or lmin <= SINGULAER * lmax:
        out['grund'] = (f'singuläre Kovarianz Σ̂ (λ_min/λ_max = {lmin / lmax:.3g})' if lmax > STREUUNG_NULL_E3B ** 2
                        else 'singuläre Kovarianz Σ̂ (Streuung null oder nur Rundungsrest)')
        return out
    s = math.sqrt(lmax)
    out.update(s_hat=s, rho_hat=math.sqrt(lmin / lmax))
    if ne < nu_min:
        out['grund'] = f'zu wenige Freiheitsgrade: ν_eff = {ne:.3g} < {nu_min} (n* = {ns})'
        return out
    kap = e3b_kappa(ne, alpha_m)
    c = e3b_kritisch(s, ne, q_tol, alpha_m)
    t95 = float(stats.t.isf(0.05, ne))
    q = out['q_Z']
    hi = q + t95 * s
    erg = 'auffällig' if q > c else ('unauffällig' if hi <= q_tol else 'unbestimmt')
    out.update(kappa=kap, kritisch=float(c), t95=t95, obere_grenze=float(hi), ergebnis=erg)
    if (~ok).any():
        out.update(ergebnis=None, grund=_ungueltig_grund(int((~ok).sum()), db.size))
    return out


# ── Rückfall je Prüfgröße und Urteile ──────────────────────────────────────────────────────────────────
KRITERIEN_SCHLUESSEL = ('auffaellig', 'unauffaellig', 'modellpruefung')


def kriterien_pruefen(kriterien):
    """Kriterienbefund aus Teil B (Kalibriersimulation, A9.11): dict(herkunft=…, E3a=dict(auffaellig, unauffaellig,
    modellpruefung), E3b=…) mit bool oder None (nicht gerechnet). None: nicht ausgewiesen."""
    if kriterien is None:
        return None
    if not isinstance(kriterien, dict) or not set(kriterien) <= {'herkunft', 'E3a', 'E3b'}:
        raise ValueError(f'E3-Kriterien in Teil B: unbekanntes Format {kriterien!r}')
    for g in ('E3a', 'E3b'):
        v = kriterien.get(g) or {}
        if not isinstance(v, dict) or not set(v) <= set(KRITERIEN_SCHLUESSEL) or not all(
                x is None or isinstance(x, bool) for x in v.values()):
            raise ValueError(f'E3-Kriterien in Teil B für {g}: {v!r} (Schlüssel {KRITERIEN_SCHLUESSEL}, bool oder '
                             'None)')
    return kriterien


def stufen(grund_beschreibend=None, kriterien=None):
    """Stufe je Prüfgröße vor den Daten der Prüfungen: dreiwertig, oder Rückfall auf beschreibend/einseitig mit
    Grund. grund_beschreibend: gemeinsamer Grund (T-Unsicherheit fehlt, unvollständig, ungültige Ziehungen)."""
    kr = kriterien_pruefen(kriterien)
    out = {}
    for g in ('E3a', 'E3b'):
        st, gr = 'dreiwertig', []
        if grund_beschreibend:
            st, gr = 'beschreibend', [grund_beschreibend]
        v = (kr or {}).get(g) or {}
        if v.get('auffaellig') is False:
            st, gr = 'beschreibend', gr + ['Kriterium „P(auffällig | exakt) ≤ 0,05“ von A9.11 in Teil B verfehlt']
        if v.get('modellpruefung') is False:
            st, gr = 'beschreibend', gr + ['Modellprüfung (A9.11) in Teil B verfehlt']
        if v.get('unauffaellig') is False:
            if st == 'dreiwertig':
                st = 'einseitig'
            gr.append('Kriterium „P(unauffällig | exakt) ≥ 0,8“ von A9.11 in Teil B verfehlt: nur einseitig')
        out[g] = dict(stufe=st, gruende=gr)
    return out


def _nach_stufe(erg, stufe):
    if erg is None or stufe == 'beschreibend':
        return None
    if stufe == 'einseitig' and erg != 'auffällig':
        return KEINE_UEBERSCHREITUNG
    return erg


def urteil(pruefungen, stufe, n_soll):
    """Urteil einer Prüfgröße aus ihren Prüfungen (dict mit „ergebnis“ nach dem Rückfall) und der Sollzahl."""
    ausw = [p for p in pruefungen if p['ergebnis'] is not None]
    if stufe == 'beschreibend':
        return None, stufe
    if not ausw:
        return None, 'nicht prüfbar'
    if any(p['ergebnis'] == 'auffällig' for p in ausw):
        return 'auffällig', stufe
    if stufe == 'einseitig':
        return KEINE_UEBERSCHREITUNG, stufe
    if len(ausw) == n_soll and all(p['ergebnis'] == 'unauffällig' for p in ausw):
        return 'unauffällig', stufe
    return 'unbestimmt', stufe


def gesamturteil(pg):
    """Gesamturteil aus den Prüfgrößen pg = {'E3a': dict(urteil, stufe), 'E3b': …}."""
    u = [pg[g]['urteil'] for g in ('E3a', 'E3b')]
    st = [pg[g]['stufe'] for g in ('E3a', 'E3b')]
    if 'auffällig' in u:
        return 'auffällig'
    if all(s == 'dreiwertig' for s in st) and all(x in ('unauffällig', 'unbestimmt') for x in u):
        return 'unauffällig' if all(x == 'unauffällig' for x in u) else 'unbestimmt'
    if any(x is not None for x in u):
        return KEINE_UEBERSCHREITUNG
    return None


def bewerten(e3a, e3b, punkte, triphasik, regel, grund_beschreibend=None, kriterien=None):
    """Bewertung aller m = 43 Prüfungen. e3a: id → {'modul2': prüfung, 'modul3': prüfung} (nur ausgewertete
    Punkte); e3b: Prüfung am Triphasik-Punkt oder None; punkte: die 21 Schnittpunkte der Prüfmenge in fester
    Reihenfolge. Rückgabe dict(pruefungen, pruefgroessen, bewertung, status, …) für das Ergebnis."""
    if len(punkte) != N_SCHNITT or len(set(punkte)) != N_SCHNITT:
        raise ValueError(f'Prüfmenge schnitt21_triphasik: {len(punkte)} Schnittpunkte statt {N_SCHNITT}')
    if triphasik not in punkte:
        raise ValueError(f'Triphasik-Punkt {triphasik!r} nicht unter den Schnittpunkten')
    unbekannt = set(e3a) - set(punkte)
    if unbekannt:
        raise ValueError(f'E3a-Punkte außerhalb der Prüfmenge: {sorted(unbekannt)}')
    st = stufen(grund_beschreibend, kriterien)
    pr = []
    for kid in punkte:
        for mod in ('modul2', 'modul3'):
            p = (e3a.get(kid) or {}).get(mod)
            eintrag = dict(id=f'E3a/{kid}/{mod}', groesse='E3a', punkt=kid, modul=int(mod[-1]))
            if p is None:
                eintrag.update(ergebnis=None, grund='Punkt nicht auswertbar (fehlt in der Auswertung)')
            else:
                eintrag.update(ergebnis=_nach_stufe(p['ergebnis'], st['E3a']['stufe']),
                               grund=p['grund'] if p['ergebnis'] is None else None)
            pr.append(eintrag)
    eintrag = dict(id=f'E3b/{triphasik}', groesse='E3b', punkt=triphasik, modul=None)
    if e3b is None:
        eintrag.update(ergebnis=None, grund='Triphasik-Punkt nicht auswertbar')
    else:
        eintrag.update(ergebnis=_nach_stufe(e3b['ergebnis'], st['E3b']['stufe']),
                       grund=e3b['grund'] if e3b['ergebnis'] is None else None)
    pr.append(eintrag)
    for x in pr:
        if x['ergebnis'] is None and not x['grund']:
            x['grund'] = f'Rückfall der Prüfgröße {x["groesse"]} auf „beschreibend“ (Zahlen ohne Aussage)'
    if len(pr) != regel['m']:
        raise ValueError(f'{len(pr)} Prüfungen statt m = {regel["m"]}')
    pg = {}
    for g, n_soll in (('E3a', 2 * N_SCHNITT), ('E3b', 1)):
        p = [x for x in pr if x['groesse'] == g]
        u, stufe = urteil(p, st[g]['stufe'], n_soll)
        gr = list(st[g]['gruende'])
        if stufe == 'nicht prüfbar':
            gr += sorted({x['grund'] for x in p if x['grund']})
        zl = {e: sum(x['ergebnis'] == e for x in p) for e in ERGEBNISSE}
        zl['ohne Aussage'] = sum(x['ergebnis'] is None for x in p)
        pg[g] = dict(stufe=stufe, urteil=u, gruende=gr, n_pruefungen=n_soll,
                     n_ausgewertet=sum(x['ergebnis'] is not None for x in p), zaehlung=zl)
    bew = gesamturteil(pg)
    kr = kriterien_pruefen(kriterien)
    kr_text = ('Kriterien von A9.11 und Modellprüfung in Teil B nicht ausgewiesen (keine Kalibriersimulation; keine '
               'Kalibrierabnahme)' if kr is None else
               f'Kriterien von A9.11 aus Teil B: {kr.get("herkunft", "ohne Herkunft")}')
    teile = ', '.join(f'{g} {pg[g]["stufe"]}' + (f' ({pg[g]["urteil"]})' if pg[g]['urteil'] else '') for g in pg)
    if bew is None:
        gruende = sorted({x for g in pg for x in pg[g]['gruende']})
        art = ('nur numerisch' if grund_beschreibend else          # T-Unsicherheit fehlt, unvollständig, unzulässig
               'nur beschreibend' if any(pg[g]['stufe'] == 'beschreibend' for g in pg) else 'nicht prüfbar')
        status = f'{art}: ' + '; '.join(gruende)
    else:
        status = f'Regelstand 2026-11 (Option B, Rückfall je Prüfgröße): {teile}'
    return dict(pruefungen=pr, pruefgroessen=pg, bewertung=bew, status=status, kriterien_a9_11=kr_text,
                kriterien=kr)
