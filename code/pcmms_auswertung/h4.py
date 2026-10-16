"""AP-12 Stufe 2: H4 (Vorzeichen der Schiefe) nach Präreg §3, §8.5, §9.3 und A8.

Prüfmenge V aus Teil B nr8 (nur Konfigurationen mit |γ̂₁| ≥ (c₄ + 1,645)·u_c,erw(γ₁)); je i ∈ V die gemessene Schiefe
γ̄₁,i der Konfigurationsmittelkurve (k ≤ k_max), u(γ̄₁,i) aus Bootstrap A, c = t(1 − 0,05/23; n_i − 1).
Bestätigt: V nicht leer und an jedem i: sgn(γ̂₁,i)·γ̄₁,i > c·u; falsifiziert: an einem i: sgn(γ̂₁,i)·γ̄₁,i < −c·u;
sonst nicht entscheidbar (bei V leer: Präzision).
"""
import numpy as np
from scipy import stats

from . import bootstrap as bs, konventionen as kv


def h4_auswerten(V, K, idxA, kmax, profil, auswertbar):
    """V: Liste dict(id, gamma_vorhersage); K: id → dict(Nk (n, K)); idxA: id → Indexmatrix; auswertbar: Menge."""
    m = profil.wert('h4.m')
    tests = []
    gruende = []
    V_ausw = [v for v in V if v['id'] in auswertbar and v['id'] in K]      # V enthält nur auswertbare (§9.3)
    for v in V_ausw:
        kid = v['id']
        X = K[kid]['Nk'][:, :kmax]
        n = X.shape[0]
        g = float(kv.schiefe(X.mean(0)))
        C = bs.zaehlmatrix(idxA[kid], n)
        gb = kv.schiefe((C @ X) / n)
        u = float(np.std(gb, ddof=1))
        c = float(stats.t.ppf(1 - 0.05 / m, n - 1))
        s = np.sign(v['gamma_vorhersage'])
        tests.append(dict(id=kid, gamma_messung=g, gamma_vorhersage=v['gamma_vorhersage'], u=u, c=c, n=n,
                          bestaetigt=bool(s * g > c * u), gegenteil=bool(s * g < -c * u)))
    if any(t['gegenteil'] for t in tests):
        ausgang = 'falsifiziert'
    elif tests and all(t['bestaetigt'] for t in tests):
        ausgang = 'bestätigt'
    else:
        ausgang = 'nicht entscheidbar'
        gruende.append(('Präzision', 'V leer' if not tests else 'Vorzeichen nicht an jeder Konfiguration nachgewiesen'))
    return dict(ausgang=ausgang, grund=gruende[0][0] if gruende else None,
                gruende=[dict(klasse=k, text=t) for k, t in gruende], tests=tests, V=[v['id'] for v in V_ausw],
                V_teil_b=[v['id'] for v in V], m=m)
