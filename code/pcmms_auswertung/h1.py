"""AP-12 Stufe 2: H1 (Superposition der Summe, 147 Tests) und H1Z (je Zelle, 441 Tests) nach Präreg §3, §8.3–§8.5,
§9.3, §9.4 und A8, A9.5.

Je Test (Punkt i, Größe q) gegen beide Vorhersagen: r = ȳ − ŷ (für F_min − ⟨N⟩ minus Rauschbias b̂ aus Teil B),
u² = Var_A + Var_B (+ u²(b̂)), ν_eff nach Welch–Satterthwaite mit n_A (Läufe der Konfiguration) und n_B (kleinstes
Modul der Vorhersageseite; der Biasterm zählt mit ν = ∞), z = r/u, t_eq = t(0,95; ν_eff).
PB1: [r − t_eq·u, r + t_eq·u] ⊂ [−Δ_q, Δ_q] für alle Tests gegen ŷ⁰ und ŷ¹ (IUT), alle 21 Punkte auswertbar.
Mindesteffekt: |r⁰| − c·u⁰ > Δ_rel und |r¹| − c·u¹ > Δ_rel mit gleichem Vorzeichen; c aus Teil B (Kalibrierung).
Ausgang: falsifiziert vor bestätigt vor nicht entscheidbar (mit Δ_rel = Δ_q schließen sie sich aus); ohne c ist die
Falsifikation nicht prüfbar. Zusätze und Gründe nach §9.3/§9.4 (Regeln h1.zusaetze, h1.gruende,
h1.grund_zuordnung, h1.groesste_abweichung, drift.zusatz, drift.logik). Grenzfall u ≈ 0: Regel h1.grenzfall.
"""
import numpy as np
from scipy import stats

from .regeln import RegelOffen

EPS_U = 1e-14


def tests_bilden(q_mess, q_vor, var_A, var_B, n_A, n_B, bias=None, u_bias=None, bias_achse_q=0, delta=None):
    """r, u, ν, z, t_eq je Test. q_*: (…, Q); var_*: gleiche Form; n_A: (…) oder Skalar; bias: (…) für q = 0;
    delta: Äquivalenzgrenze (…, Q) für die Skala des Grenzfalls u ≈ 0 (Regel h1.grenzfall)."""
    q_mess, q_vor = np.asarray(q_mess, float), np.asarray(q_vor, float)
    r = q_mess - q_vor
    vA, vB = np.asarray(var_A, float), np.asarray(var_B, float)
    u2 = vA + vB
    if bias is not None:
        r = r.copy()
        u2 = u2.copy()
        r[..., bias_achse_q] -= np.asarray(bias, float)
        u2[..., bias_achse_q] += np.asarray(u_bias, float) ** 2
    u = np.sqrt(u2)
    nA = np.broadcast_to(np.asarray(n_A, float)[..., None] if np.ndim(n_A) else n_A, r.shape)
    nB = np.broadcast_to(np.asarray(n_B, float), r.shape)
    with np.errstate(divide='ignore', invalid='ignore'):
        nenner = vA ** 2 / (nA - 1) + vB ** 2 / (nB - 1)
        nu = np.where(nenner > 0, u2 ** 2 / nenner, np.inf)
    skala = np.maximum.reduce([np.abs(q_mess), np.abs(q_vor), np.full(r.shape, 1e-300)] +
                              ([np.broadcast_to(np.abs(np.asarray(delta, float)), r.shape)] if delta is not None
                               else []))
    null = u <= EPS_U * skala
    with np.errstate(divide='ignore', invalid='ignore'):
        z = np.where(null, np.where(np.abs(r) <= EPS_U * skala, 0.0, np.sign(r) * np.inf), r / np.where(null, 1, u))
    u = np.where(null, 0.0, u)
    nu = np.where(null, np.inf, nu)
    teq = np.where(np.isfinite(nu), stats.t.ppf(0.95, np.where(np.isfinite(nu), nu, 1.0)), stats.norm.ppf(0.95))
    return dict(r=r, u=u, nu=nu, z=z, teq=teq, varA=vA, varB=vB, null=null)


def _tost(T, Delta):
    return (T['r'] - T['teq'] * T['u'] >= -Delta) & (T['r'] + T['teq'] * T['u'] <= Delta)


def entscheiden(T0, T1, Delta, Delta_rel, c, vollstaendig, profil, sperren=(), name='H1'):
    """Ausgang aus den Tests gegen ŷ⁰ (T0) und ŷ¹ (T1). Delta, Delta_rel: Form der Größenachse (Broadcast über
    Punkte); c: kritischer Wert oder None; vollstaendig: alle Punkte auswertbar (nur für „bestätigt“ nötig);
    sperren: Gründe, die jede Entscheidung verhindern (Liste von (Klasse, Text)), etwa ŷ¹ ungültig."""
    Delta = np.asarray(Delta, float)
    Drel = np.asarray(Delta_rel, float)
    vorhanden = np.isfinite(T0['r']) & np.isfinite(T1['r'])
    tost0 = _tost(T0, Delta) & vorhanden
    tost1 = _tost(T1, Delta) & vorhanden
    aequivalent = bool(vollstaendig and vorhanden.all() and tost0.all() and tost1.all())
    zusatz_txt = profil.wert('h1.zusaetze')
    gesperrt = list(sperren)
    hinweise = []
    if c is None:
        relevant = np.zeros_like(tost0)
        abw = drift_t = None
        hinweise.append(('Verfahren', 'kritischer Wert c fehlt in Teil B: Falsifikation und Zusätze nicht prüfbar'))
    else:
        with np.errstate(invalid='ignore'):
            relevant = vorhanden & (np.abs(T0['r']) - c * T0['u'] > Drel) & (np.abs(T1['r']) - c * T1['u'] > Drel) & \
                (np.sign(T0['r']) == np.sign(T1['r']))
            g0 = vorhanden & (np.abs(T0['z']) > c)
            g1 = vorhanden & (np.abs(T1['z']) > c)
        gleich = np.sign(T0['z']) == np.sign(T1['z'])
        abw = g0 & g1 & gleich
        drift_t = (g0 & ~(g1 & gleich)) | (g1 & ~(g0 & gleich))
    drift = None if drift_t is None else bool(drift_t.any())
    drift_hinweis = None
    if drift:
        try:
            logik = profil.wert('drift.logik')
        except RegelOffen as e:
            logik = None
            drift_hinweis = e.grund
        if logik == 'b':
            gesperrt.append(('Drift', 'nachgewiesene Drift der Einzelmodulbasis (Driftlogik b)'))
        elif logik is None:
            gesperrt.append(('Verfahren', 'Drift nachgewiesen und Driftlogik offen (Regel drift.logik)'))
    falsifiziert = bool(relevant.any())
    if gesperrt:
        ausgang = 'nicht entscheidbar'
    elif falsifiziert:
        ausgang = 'falsifiziert'
    elif aequivalent:
        ausgang = 'bestätigt'
    else:
        ausgang = 'nicht entscheidbar'
    gruende = list(gesperrt)
    grund = None
    if ausgang == 'nicht entscheidbar':
        gruende += hinweise
        if not vollstaendig:
            gruende.append(('Datenlage', 'nicht alle Punkte auswertbar'))
        weit = (T0['teq'] * T0['u'] >= Delta) | (T1['teq'] * T1['u'] >= Delta)
        fehl = vorhanden & ~(tost0 & tost1)
        if (fehl & ~weit).any():
            gruende.append(('Graubereich', 'Abweichung zwischen Äquivalenz- und Relevanzgrenze'))
        if (fehl & weit).any():
            gruende.append(('Präzision', 'Präzision reicht für die Äquivalenz nicht (t_eq·u ≥ Δ_q)'))
        rang = ['Datenlage', 'Verfahren', 'Drift', 'Graubereich', 'Präzision']
        klassen = sorted({k for k, _ in gruende}, key=rang.index)
        grund = klassen[0] if klassen else 'Präzision'
    else:
        gruende += hinweise
    zus = []
    groesste = None
    if abw is not None and abw.any():
        zus.append(zusatz_txt['bestaetigt'] if ausgang == 'bestätigt' else
                   zusatz_txt['nicht_entscheidbar'] if ausgang == 'nicht entscheidbar' else 'Abweichung nachgewiesen')
        with np.errstate(invalid='ignore'):
            mass = np.where(abw, np.minimum(np.abs(T0['r']) - c * T0['u'], np.abs(T1['r']) - c * T1['u']) /
                            np.broadcast_to(Delta, abw.shape), -np.inf)
        ii = np.unravel_index(int(np.argmax(mass)), mass.shape)
        groesste = dict(test=[int(x) for x in ii], r0=float(T0['r'][ii]), u0=float(T0['u'][ii]),
                        r1=float(T1['r'][ii]), u1=float(T1['u'][ii]),
                        grenzen0=[float(T0['r'][ii] - c * T0['u'][ii]), float(T0['r'][ii] + c * T0['u'][ii])],
                        grenzen1=[float(T1['r'][ii] - c * T1['u'][ii]), float(T1['r'][ii] + c * T1['u'][ii])],
                        Delta=float(np.broadcast_to(Delta, abw.shape)[ii]))
    if drift:
        try:
            profil.wert('drift.zusatz')
            zus.append(zusatz_txt['drift'])
        except RegelOffen as e:
            zus.append(f'{zusatz_txt["drift"]} (Definition offen: {e.grund})')
    with np.errstate(invalid='ignore'):
        mz0 = float(np.nanmax(np.abs(np.where(vorhanden, T0['z'], np.nan)))) if vorhanden.any() else None
        mz1 = float(np.nanmax(np.abs(np.where(vorhanden, T1['z'], np.nan)))) if vorhanden.any() else None
    return dict(name=name, ausgang=ausgang, grund=grund, gruende=[dict(klasse=k, text=t) for k, t in gruende],
                zusaetze=zus, groesste_abweichung=groesste,
                abweichung_nachgewiesen=None if abw is None else bool(abw.any()), drift=drift,
                drift_hinweis=drift_hinweis, aequivalent=aequivalent, falsifikation=falsifiziert,
                n_tests=int(vorhanden.sum()), vollstaendig=bool(vollstaendig), c=c, Delta=Delta, Delta_rel=Drel,
                max_abs_z0=mz0, max_abs_z1=mz1, tost0=tost0, tost1=tost1, relevant=relevant, abweichung_test=abw,
                drift_test=drift_t)


def ausgang_kurz(d):
    return d['ausgang'] + (f' ({d["grund"]})' if d.get('grund') else '') + (
        f'; {", ".join(d["zusaetze"])}' if d.get('zusaetze') else '')
