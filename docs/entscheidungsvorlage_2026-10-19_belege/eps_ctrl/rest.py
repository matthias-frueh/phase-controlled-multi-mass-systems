# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 und 5.2.
# Zweck: (1) Anteil der A8-Schranke 2,5·10⁻⁴ je Lauf aus Kampagnen mit kleinem u (Befehl Anhang Tab. F Z. 1437,
#   gleicher Seed); (2) F-Test nach A9.8, wenn R- und K/L-Läufe mit verschiedenen Faktoren skaliert werden;
#   κ(21)/κ(57) und κ(41)/κ(57).
# Eingaben: Argument 1 = dieser Ordner (Import von phase0.py). Seeds: default_rng(1) und default_rng(4).
# Laufzeit: gemessen 7 s Wandzeit, 7 s CPU (ein Prozess, ein Thread, 20.10.2026). Aufruf: python3 -B rest.py . > rest.out
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
import sys, numpy as np
from scipy.stats import norm, chi2
sys.path.insert(0, sys.argv[1]); import phase0 as p0
# (1) Anteil der Randschranke 2,5·10⁻⁴ aus dem unteren Rand von σ̂_ref (Befehl Anhang Z. 1437, gleicher Seed)
g = np.random.default_rng(1); R = g.standard_normal((400000, 42))
s = (R[:, 1:-1] - (R[:, :-2] + R[:, 2:]) / 2).std(1, ddof=1); u = s / np.sqrt(1.5)
p = 2 * norm.sf(3 * u) * 2 * norm.sf(3 * u * np.sqrt(0.75))
for c in (0.8, 0.9, 1.0):
    print('u < %.1f: Anteil Datensätze %.3f, Anteil an p1 %.2f' % (c, (u < c).mean(), p[u < c].sum() / p.sum()))
print('p1 marginal %.3g, Median der bedingten p1 %.2g, 90-%%-Quantil %.2g' % (p.mean(), np.median(p), np.quantile(p, 0.9)))
# (2) F-Test bei getrennt skalierten ⟨N⟩-Streuungen (κ je Komponente): σ_betr/σ_ref = r
rng = np.random.default_rng(4)
be, ai = p0.layout(61, 2); nrm = np.sqrt(1.5 / (1 + be ** 2 + (1 - be) ** 2))
for r in (1.0, 1.0177, 1.069):
    Rr = rng.standard_normal((100000, 61)); O = r * rng.standard_normal((100000, ai.size))
    loo = Rr[:, 1:-1] - 0.5 * (Rr[:, :-2] + Rr[:, 2:]); d = (O - ((1 - be) * Rr[:, ai] + be * Rr[:, ai + 1])) * nrm
    F = d.var(1, ddof=1) / loo.var(1, ddof=1)
    print('σ_betr/σ_ref = %.4f: P(F > 1,581) = %.3f' % (r, (F > 1.581).mean()))
k = lambda nu: np.sqrt(nu / chi2.ppf(0.2, nu))
print('κ(21)/κ(57) = %.4f, κ(41)/κ(57) = %.4f' % (k(21) / k(57), k(41) / k(57)))
