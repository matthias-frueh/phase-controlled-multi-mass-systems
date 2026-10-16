"""S₃-Prüffall (Plan AP-13, Gruppe F, Kriterium K16), rauschfrei auf Ebene H.

Für jeden Prüfpunkt (0, φ₂, φ₃) des Szenarios und seine sechs Bilder unter Modulvertauschung und Zeitverschiebung
(konventionen.s3_bilder): bei identischen Modulen gleiche F_min − ⟨N⟩, |N_k| und γ₁ (Schranke 10⁻⁹ N bzw. 10⁻⁹) und
die Phasenregel arg N_k(Bild) = arg N_k(Basis) + k·φ_ref (Schranke 10⁻⁶°); bei ungleichen Modulen weicht der
modellfreie Bildvergleich ab, die Superpositionsvorhersage aus den Einzelmodulantworten (wahre Zeiger) nicht.

Befund zu K16: F_min ist nach A1 das Minimum der bandbegrenzten Mittelkurve auf ihren N_θ = 2000 Stützstellen. Unter
einer Zeitverschiebung φ_ref, die kein Vielfaches von 360°/N_θ ist, ist F_min − ⟨N⟩ deshalb nur bis auf die
Rasterschranke Σ_k k²|N_k|·(2π/N_θ)²/8 invariant, nicht auf 10⁻⁹ N; die Prüfung weist beide Schranken aus.
"""
import numpy as np

from .. import konventionen as kv
from ..generator import kampagne as kp, szenarien, wahrheit

SCHRANKE_N = 1e-9
SCHRANKE_GRAD = 1e-6


def _id(q2, q3):
    from .. import zusammenfassung as zf
    return zf.konfig_id('K', (0.0, float(q2), float(q3)), None, 1, 'pruef')


def pruefen(sid='F01-S3', stufe='L1'):
    m = szenarien.modell(sid, stufe)
    kmax = m.system.k_max
    konf = kp.schnitt_konfigurationen(m.plan)
    w, felder = wahrheit.berechne(m, konf)
    k = np.arange(1, kmax + 1)
    punkte = []
    for p2, p3 in m.plan.pruef:
        bilder = kv.s3_bilder(p2, p3)
        basis = felder[f'mess_summe__{_id(*bilder[0][1])}'][:kmax]
        Fb = float(kv.fmin_rel(basis[None])[0])
        gb = float(kv.schiefe(basis))
        dF = dA = dg = dphi = dvor = 0.0
        raster = float(np.sum(k ** 2 * np.abs(basis)) * (2 * np.pi / kv.N_THETA) ** 2 / 8)
        for perm, (q2, q3), ref in bilder:
            kid = _id(q2, q3)
            N = felder[f'mess_summe__{kid}'][:kmax]
            Y = felder[f'yhat0_summe__{kid}'][:kmax]
            dF = max(dF, abs(float(kv.fmin_rel(N[None])[0]) - Fb))
            dA = max(dA, float(np.abs(np.abs(N) - np.abs(basis)).max()))
            dg = max(dg, abs(float(kv.schiefe(N)) - gb))
            soll = basis * np.exp(1j * k * np.radians(ref))
            mask = np.abs(basis) > 1e-6
            if mask.any():
                dphi = max(dphi, float(np.degrees(np.abs(np.angle(N[mask] / soll[mask]))).max()))
            dvor = max(dvor, float(np.abs(N - Y).max()))
        punkte.append(dict(punkt=[float(p2), float(p3)], F_min_rel_N=dF, betrag_N=dA, gamma1=dg, phase_grad=dphi,
                           vorhersage_N=dvor, F_min_rasterschranke_N=raster))
    mx = {x: max(p[x] for p in punkte) for x in ('F_min_rel_N', 'betrag_N', 'gamma1', 'phase_grad', 'vorhersage_N')}
    f_raster = all(p['F_min_rel_N'] <= max(SCHRANKE_N, p['F_min_rasterschranke_N']) for p in punkte)
    gleiche_module = len({round(float(v), 12) for v in np.atleast_1d(m.system.m)}) == 1
    return dict(szenario=sid, k_max=kmax, punkte=punkte, maximum=mx, gleiche_module=gleiche_module,
                bilder_gleich=bool(f_raster and mx['betrag_N'] <= SCHRANKE_N and mx['gamma1'] <= SCHRANKE_N and
                                   mx['phase_grad'] <= SCHRANKE_GRAD),
                F_min_auf_1e9=bool(mx['F_min_rel_N'] <= SCHRANKE_N), F_min_in_rasterschranke=bool(f_raster),
                vorhersage_exakt=bool(mx['vorhersage_N'] <= SCHRANKE_N),
                schranken=dict(N=SCHRANKE_N, grad=SCHRANKE_GRAD))
