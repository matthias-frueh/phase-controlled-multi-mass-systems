"""Generatorwahrheit (Plan AP-13, Abschnitt 3.5): rauschfreie Erwartungswerte je Konfiguration, wahre Residuen gegen
die wahre Superposition, Grenzen aus der rauschfreien Vorhersage und Klasse der erwarteten Antwort.

Die Wahrheit entsteht mit dem rauschfreien Generator (Amplitude 1, kein Phasenrest, kein Jitter): je Konfiguration
ein Lauf der Phase 1 (Messseite) und je Modul ein Einzelmodullauf der Phase 0 (ŷ⁰) und der Phase 1 (ŷ¹) mit allen
Effekten des Szenarios. Die H1-Größen folgen unabhängig von AP-12 direkt aus den Konventionen. Die Wahrheit wird
getrennt vom Auswerteeingang abgelegt; nur der Harness liest sie.

Klassen (Plan 3.5) nach dem größten wahren Residuum relativ zu Δ_rel (rauschfreie Vorhersage):
R0 = 0 (bis auf 10⁻⁹ relativ), R1 < Δ_rel, R2 genau an Δ_q (Toleranz 10⁻³), R3 zwischen Δ_rel und 2·Δ_rel, R4 ≥ 2·Δ_rel.
"""
import numpy as np

from .. import formate, konventionen as kv
from . import ebene_h, rauschen


def _spec(laufart, gruppe, phase, phi=None, modul=None, einstellung=1, pos=0):
    from .kampagne import _konf
    d = _konf(laufart, gruppe, phi, modul, einstellung)
    d.update(phase=phase, block=None, messtag=1, position=pos, kontrollsatz=None, t_start=0.0, t_ende=1.0,
             lauf_id=f'W-{pos:04d}')
    return d


def rauschfreie_laeufe(modell, konfigurationen):
    """Je Konfiguration (Liste von Kopf-Spezifikationen aus kampagne) ein rauschfreier Lauf der Phase 1, dazu die
    Einzelmodulläufe der Phasen 0 und 1 (bei Einstellung 2 ebenfalls)."""
    specs, pos = [], 0
    einst = [1] + ([2] if modell.plan.einstellung2 else [])
    for e in einst:
        for ph in (0, 1):
            for j in (1, 2, 3):
                specs.append(_spec('L', 'einzel', ph, modul=j, einstellung=e, pos=pos))
                pos += 1
    for k in konfigurationen:
        sp = _spec('K', k['konfiguration']['gruppe'], 0 if k['konfiguration']['gruppe'] == 'pilot' else 1,
                   k['konfiguration']['phi_soll_grad'], einstellung=k['einstellung'], pos=pos)
        specs.append(sp)
        pos += 1
    rng = np.random.default_rng(0)                                  # wird rauschfrei nicht gebraucht
    tab = ebene_h.erzeuge(modell, specs, rng, rausch=rauschen.RAUSCHFREI)
    return specs, tab


def h1_groessen(Nk, kmax):
    return kv.h1_vektor(np.asarray(Nk)[..., :kmax])


def d_grenzen(yhat_schnitt, kmax, faktor=0.25):
    """D_q (Fassung B und A) und Δ_q aus Vorhersagen am Schnitt (21, k), wie Präreg §8.5 (unabhängig geschrieben)."""
    F = kv.fmin_rel(yhat_schnitt[:, :kmax])
    D_B = [F.max() - F.min()]
    D_A = [F.max() - F.min()]
    for k in range(3):
        z = yhat_schnitt[:, k]
        dB = np.abs(z[:, None] - z[None, :]).max()
        dA = np.abs(z).max()
        D_B += [dB, dB]
        D_A += [dA, dA]
    D_B, D_A = np.array(D_B), np.array(D_A)
    return dict(D_B=D_B, D_A=D_A, Delta_B=faktor * D_B, Delta_A=faktor * D_A, Delta_B_01=0.1 * D_B)


def klasse(r_max_rel):
    """Klasse nach Plan 3.5 aus max|r|/Δ_rel (rauschfreie Grenzen)."""
    if r_max_rel <= 1e-9:
        return 'R0'
    if abs(r_max_rel - 1.0) <= 1e-3:
        return 'R2'
    if r_max_rel < 1.0:
        return 'R1'
    return 'R3' if r_max_rel < 2.0 else 'R4'


def berechne(modell, konfigurationen):
    """Wahrheit eines Szenarios (dict mit Feldern für NPZ und JSON-Inhalt)."""
    kmax = modell.system.k_max
    specs, tab = rauschfreie_laeufe(modell, konfigurationen)
    K = tab.k_voll
    k = np.arange(1, K + 1)
    einz = {}
    for i, sp in enumerate(specs):
        if sp['laufart'] == 'L':
            einz[(sp['einstellung'], sp['phase'], sp['modul'])] = (tab.daten['Nk_summe'][i], tab.daten['Nk_zellen'][i])
    out = dict(konfigurationen=[], kmax=kmax)
    felder = {}
    schnitt_idx = []
    for i, sp in enumerate(specs):
        if sp['laufart'] != 'K':
            continue
        kid = sp['konfiguration']['id']
        e = sp['einstellung']
        phi_idx = modell.index_soll_grad(sp['konfiguration']['phi_soll_grad'])
        Z = kv.zeigerfaktor(phi_idx, k)                                         # ideale Zeiger (3, K)
        mess, mess_z = tab.daten['Nk_summe'][i], tab.daten['Nk_zellen'][i]
        vor = {}
        for ph in (0, 1):
            s = sum(Z[j] * einz[(e, ph, j + 1)][0] for j in range(3))
            sz = sum(Z[j][None, :] * einz[(e, ph, j + 1)][1] for j in range(3))
            vor[ph] = (s, sz)
        felder[f'mess_summe__{kid}'] = mess
        felder[f'mess_zellen__{kid}'] = mess_z
        felder[f'yhat0_summe__{kid}'] = vor[0][0]
        felder[f'yhat1_summe__{kid}'] = vor[1][0]
        felder[f'yhat0_zellen__{kid}'] = vor[0][1]
        felder[f'yhat1_zellen__{kid}'] = vor[1][1]
        felder[f'min_zellen_voll__{kid}'] = tab.daten['min_roh_zellen'][i]
        out['konfigurationen'].append(kid)
        if sp['konfiguration']['gruppe'] == 'schnitt' and e == 1:
            schnitt_idx.append(kid)
    # H1-Wahrheit am Schnitt
    if schnitt_idx:
        Y0 = np.array([felder[f'yhat0_summe__{q}'] for q in schnitt_idx])
        Y1 = np.array([felder[f'yhat1_summe__{q}'] for q in schnitt_idx])
        Ym = np.array([felder[f'mess_summe__{q}'] for q in schnitt_idx])
        g = d_grenzen(Y0, kmax)
        r0 = h1_groessen(Ym, kmax) - h1_groessen(Y0, kmax)
        r1 = h1_groessen(Ym, kmax) - h1_groessen(Y1, kmax)
        felder.update(r0_wahr=r0, r1_wahr=r1, D_B=g['D_B'], D_A=g['D_A'], Delta_B=g['Delta_B'], Delta_A=g['Delta_A'],
                      F_mess=kv.fmin_rel(Ym[:, :kmax]), F_yhat0=kv.fmin_rel(Y0[:, :kmax]),
                      F_yhat1=kv.fmin_rel(Y1[:, :kmax]))
        rel0 = np.abs(r0) / g['Delta_B'][None, :]
        rel1 = np.abs(r1) / g['Delta_B'][None, :]
        beide = np.minimum(rel0, rel1)                                  # Falsifikation verlangt beide Vorhersagen
        rmin = np.minimum(np.abs(r0), np.abs(r1))
        out.update(schnitt=schnitt_idx, r_max_rel_yhat0=float(rel0.max()), r_max_rel_yhat1=float(rel1.max()),
                   r_max_rel_beide=float(beide.max()), klasse=klasse(float(beide.max())),
                   r_max_rel_je_groesse=dict(zip(kv.GROESSEN_H1, [float(x) for x in beide.max(0)])),
                   klasse_sens_faktor_0_1=klasse(float((rmin / (0.1 * g['D_B'])[None, :]).max())),
                   klasse_sens_fassung_A=klasse(float((rmin / g['Delta_A'][None, :]).max())),
                   bindend_test=[int(x) for x in np.unravel_index(int(np.argmax(beide)), beide.shape)],
                   Delta_B=dict(zip(kv.GROESSEN_H1, [float(x) for x in g['Delta_B']])))
    # kleinste lineare Zellkraft (ganzer Lauf ohne Rauschen, vor dem Abschneiden) je Laufart
    zmin = {}
    for i, sp in enumerate(specs):
        x = tab.daten['N_mittel_zellen'][i][:, None] + kv.kurve(tab.daten['Nk_zellen'][i])
        zmin[sp['konfiguration']['id'] + ('/0' if sp['phase'] == 0 else '/1')] = float(x.min())
    out['zellminimum_N'] = zmin
    out['zellminimum_min_N'] = float(min(zmin.values()))
    return out, felder


def speichern(pfad, modell, out, felder, kennung, szenario):
    k = formate.kopf('wahrheit', kennung, szenario=szenario, system=modell.system.name)
    return formate.schreibe(pfad, k, felder, inhalt=out)


def laden(pfad):
    k, inhalt, felder = formate.lies(pfad, 'wahrheit')
    return k, inhalt, felder
