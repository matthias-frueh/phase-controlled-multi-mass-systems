"""Raten und Quantile des Harness mit Monte-Carlo-Fehler (Plan AP-13, Abschnitte 1.4 und 2.5).

Jede Rate trägt Zähler, Nenner, Monte-Carlo-Standardfehler √(p(1 − p)/n), Szenario, Stufe und Regelprofil. Wenige
Kampagnen liefern Entwicklungsdiagnostik: Ist der Nenner kleiner als die normative Kampagnenzahl, steht das als
„reduziert“ an der Rate. Ein Quantil (etwa c von H1) trägt seine Bootstrap-Unsicherheit über die Kampagnen.
"""
import numpy as np

from .. import zufall
from ..regeln import NORMATIVE_ZAHLEN


def rate(zaehler, nenner, groesse, szenario=None, stufe=None, profil=None, normativ=None):
    """Rate mit MC-Standardfehler. normativ: Sollzahl der Kampagnen (Vorgabe: kampagnen_pruefung)."""
    zaehler, nenner = int(zaehler), int(nenner)
    soll = NORMATIVE_ZAHLEN['kampagnen_pruefung'] if normativ is None else int(normativ)
    p = zaehler / nenner if nenner else None
    se = float(np.sqrt(p * (1 - p) / nenner)) if nenner else None
    return dict(groesse=groesse, zaehler=zaehler, nenner=nenner, rate=p, mc_se=se, szenario=szenario, stufe=stufe,
                profil=profil, normative_kampagnenzahl=soll, reduziert=bool(nenner < soll),
                lesart='Entwicklungsdiagnostik (weniger Kampagnen als normativ)' if nenner < soll else
                'normative Kampagnenzahl')


def rate_aus(maske, groesse, **kw):
    m = np.asarray(maske, bool)
    return rate(int(m.sum()), int(m.size), groesse, **kw)


def quantil(werte, q=0.95, B=2000, seed=0):
    """Empirisches q-Quantil (numpy, linear) mit Bootstrap-Standardfehler über die Kampagnen."""
    x = np.asarray(werte, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return dict(wert=None, se=None, n=0, q=q)
    w = float(np.quantile(x, q))
    if x.size < 2:
        return dict(wert=w, se=None, n=int(x.size), q=q)
    rng = zufall.strom(seed, 'quantil_bootstrap')
    idx = rng.integers(0, x.size, size=(B, x.size))
    qb = np.quantile(x[idx], q, axis=1)
    return dict(wert=w, se=float(np.std(qb, ddof=1)), n=int(x.size), q=q, B=B)


def mittel(werte):
    x = np.asarray(werte, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return dict(wert=None, se=None, n=0)
    return dict(wert=float(x.mean()), se=float(x.std(ddof=1) / np.sqrt(x.size)) if x.size > 1 else None,
                n=int(x.size))


def innerhalb(a, b, k=2.0):
    """Zwei Raten gleich innerhalb k gemeinsamer MC-Standardfehler (K19-Lesart)."""
    if a['rate'] is None or b['rate'] is None:
        return None
    se = np.hypot(a['mc_se'] or 0.0, b['mc_se'] or 0.0)
    return bool(abs(a['rate'] - b['rate']) <= k * se) if se > 0 else bool(a['rate'] == b['rate'])
