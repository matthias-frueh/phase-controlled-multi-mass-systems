# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 1.2, 3.1 und 5.2.
# Zweck: Verteilung von u = ε_ctrl/(3·√1,5·σ), ν_eff von σ̂_ref (Momentenanpassung 2·E[s²]²/Var[s²]) und die
#   A8-Raten q(1,5), q(2), p1 als Mittel über σ̂_ref für 42 bzw. 61 Referenzläufe mit und ohne F-Test; χ²(ν)-
#   Vergleich und σ bekannt.
# Eingaben: Argument 1 = dieser Ordner (Import von phase0.py). Ausgabe auf stdout (p0_vert.json).
# Seed: numpy default_rng(20261019); je Variante 400 000 Phase-0-Datensätze.
# Laufzeit: etwa 1 min (Einschätzung; p0_vert.json ist übernommen).
# Aufruf: python3 -B p0_vert.py . > p0_vert.json
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Verteilung von u = ε_ctrl/(3·√1,5·σ) und ν_eff von σ̂_ref; Vergleich χ²(41)."""
import json, sys
import numpy as np
from scipy.stats import chi2, norm
sys.path.insert(0, sys.argv[1])
import phase0 as p0

rng = np.random.default_rng(20261019)
res = {}
for name, nref, je, ft in (('A8_42ref', 42, 2, False), ('A8_42ref_Ftest', 42, 2, True), ('gen_61ref', 61, 2, False),
                           ('gen_61ref_Ftest', 61, 2, True)):
    o = p0.simuliere(400000, rng, nref, je, ft)
    u = o['eps'] / (3 * np.sqrt(1.5))
    ur = o['sref'] / np.sqrt(1.5)
    s2 = ur ** 2
    nu_eff = 2 * s2.mean() ** 2 / s2.var()
    q15 = 2 * norm.sf(3 * u)                 # G1 mittig (v = 1,5), ε = 3·√1,5·u
    q2 = 2 * norm.sf(3 * u * np.sqrt(1.5 / 2))
    res[name] = dict(n_ref=nref, ftest=ft, krit=o['krit'], anteil_betr=float(o['betr'].mean()),
                     nu_eff_sref=round(float(nu_eff), 1), mean_u=round(float(u.mean()), 4), sd_u=round(float(u.std()), 4),
                     u_quantile={str(p): round(float(np.quantile(u, p)), 4) for p in (0.001, 0.01, 0.05, 0.1, 0.5, 0.9)},
                     P_u_lt={str(c): float((u < c).mean()) for c in (0.75, 0.8, 0.85, 0.9)},
                     q15=float(q15.mean()), q2=float(q2.mean()), p1=float((q2 * q15).mean()),
                     corr_u_ref_zellen=float(np.corrcoef(ur, o['sref_c'][:, 0] / np.sqrt(1.5 / 3))[0, 1]))
# χ²(ν)-Annahme
for nu in (41, 39, 20):
    s = np.sqrt(chi2.rvs(nu, size=400000, random_state=rng) / nu)
    q15 = 2 * norm.sf(3 * s); q2 = 2 * norm.sf(3 * s * np.sqrt(0.75))
    res[f'chi2_{nu}'] = dict(sd_u=round(float(s.std()), 4), u_quantile={str(p): round(float(np.quantile(s, p)), 4) for p in (0.001, 0.01, 0.05, 0.5)},
                             q15=float(q15.mean()), q2=float(q2.mean()), p1=float((q2 * q15).mean()))
res['fest'] = dict(q15=float(2 * norm.sf(3)), q2=float(2 * norm.sf(3 * np.sqrt(0.75))),
                   p1=float(2 * norm.sf(3) * 2 * norm.sf(3 * np.sqrt(0.75))))
print(json.dumps(res, indent=1, ensure_ascii=False))
