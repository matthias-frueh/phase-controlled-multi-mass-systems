"""Planungssimulation (Präreg §5.4, A9.2; Plan AP-13 1.2 „geplant“) als Haken `planung` des Pilotskripts.

Für jeden Kandidaten (n_min, n₀) in der Reihenfolge der Zielfunktion (Regel planung.zielfunktion, Fassung (a):
N_K·n_min + 3·n₀) läuft die Kalibrier- und Prüfsimulation von harness.kalibrierung bei dieser Laufzahl
(n = n_min + r Blöcke mit r = ⌈n_min·p̂/(1 − p̂)⌉ + 2): Rauschbias, c, Intervalltyp von H2 und daraus
P(H1 und H2 bestätigt | exakt). Der erste Kandidat mit P ≥ 0,8 (Regel planung.bedingung, Punktschätzer) legt n_min
und n₀ fest. Streuungen an der oberen 80-%-Grenze: Das Rauschmodell des Szenarios wird mit
κ = s_q,oben80/s_q (gleicher Faktor für alle q bei gleichem ν_p) skaliert.

Grenzen dieser Stufe: Die Simulation nutzt das Rauschmodell des Szenarios, skaliert auf die Pilotgrenze; ein
unmittelbar aus gemessenen Pilotkovarianzen gespeister Generator (für Teil B nötig) fehlt. Die zusätzliche
Power-Bedingung (Regel planung.power) ist offen und nicht geprüft. Mit weniger als 1000 Kampagnen je Simulation ist
das Ergebnis Entwicklungsdiagnostik; die Planung trägt dann diese Kennzeichnung.
"""
import math

import numpy as np
from scipy import stats

from .. import regeln as rg, zufall
from ..generator import kampagne as kp, szenarien
from . import kalibrierung


def obere80_faktor(nu):
    """Faktor der oberen 80-%-Vertrauensgrenze einer Standardabweichung mit ν Freiheitsgraden."""
    return float(np.sqrt(nu / stats.chi2.ppf(0.2, nu)))


def skaliert(rausch, faktor):
    """Rauschmodell mit allen Streuungen (weiß, Amplitude, Phasenrest, Jitter) mal faktor."""
    return rausch.mit(name=f'{rausch.name}×{faktor:.4f}', sigma_zelle=rausch.sigma_zelle * faktor,
                      amp=tuple((a, v * faktor) for a, v in rausch.amp),
                      phase_grad=tuple((a, v * faktor) for a, v in rausch.phase_grad),
                      jitter_grad=rausch.jitter_grad * faktor)


def kandidaten_ordnen(n_liste, n0_liste, N_K=21):
    return sorted(((int(n), int(n0)) for n in n_liste for n0 in n0_liste), key=lambda x: (N_K * x[0] + 3 * x[1], x))


def haken(sid, stufe, profil, n_kal, n_pruef, seed_basis, n_kandidaten, n0_kandidaten=(20,), plan_basis=None,
          prozesse=1, protokoll=None, max_aufrufe=None):
    """Haken für pilot.pilot_auswerten(planung=…). protokoll: Liste, in die jeder Aufruf seine Kandidaten schreibt.
    max_aufrufe: Entwicklungsgrenze der Simulationen (weitere Paare (k, T_a) ohne Planung, gekennzeichnet)."""
    zaehler = [0]
    plan_basis = kp.Plan() if plan_basis is None else plan_basis
    sz = szenarien.KATALOG[sid]
    bedingung = profil.wert('planung.bedingung')
    profil.wert('planung.zielfunktion')
    n0_min = profil.wert('planung.n0_min')
    reserve = profil.wert('planung.reserve')

    def planung(e):
        if max_aufrufe is not None and zaehler[0] >= max_aufrufe:
            out = dict(n_min=None, n0=None, kandidaten=[], reduziert=True,
                       grund=f'nicht simuliert: Entwicklungsgrenze von {max_aufrufe} Planungsaufrufen erreicht')
            if protokoll is not None:
                protokoll.append(dict(k=e['k'], N_z=e['N_z'], **out))
            return out
        zaehler[0] += 1
        s = e['s_q']
        if not s.get('nu_p'):
            return dict(n_min=None, n0=None, grund='keine Pilotstreuungen (ν_p = 0)', kandidaten=[])
        kappa = obere80_faktor(s['nu_p'])                   # = s_q,oben80/s_q für jede Größe (pilot.obere_grenze)
        rausch = skaliert(szenarien.modell(sz, stufe).rausch, kappa)
        p = float(e['p_hat'])
        schritte = []
        for n, n0 in kandidaten_ordnen(n_kandidaten, [x for x in n0_kandidaten if x >= n0_min]):
            r = math.ceil(n * p / (1 - p)) + reserve if p < 1 else None
            if r is None or (e.get('n_max') is not None and n + r > e['n_max']):
                schritte.append(dict(n_min=n, n0=n0, reserve_r=r, uebersprungen='n = n_min + r > n_max'))
                continue
            plan = plan_basis.mit(n_bloecke=n + r, n0=n0)
            k = kalibrierung.kalibrieren(sid, stufe, profil, n_kal, n_pruef, zufall.unterseed(seed_basis, 'planung', n,
                                                                                             n0, e['k'], e['N_z']),
                                         plan=plan, n_min=n, prozesse=prozesse, rauschvarianten=[rausch],
                                         k_max=e['k'])
            g = k['gemeinsame_bestaetigung']
            schritte.append(dict(n_min=n, n0=n0, reserve_r=r, P_gemeinsam=g['rate'], mc_se=g['mc_se'],
                                 zaehler=g['zaehler'], nenner=g['nenner'], c_H1=k['c_H1']['wert'],
                                 intervalltyp_H2=k['h2'].get('schluessel'), pruefrate_c=None if k['pruefung'] is None
                                 else k['pruefung']['rate'], erfuellt=bool(g['rate'] is not None and
                                                                           g['rate'] >= bedingung)))
            if schritte[-1]['erfuellt']:
                break
        red = n_kal < rg.NORMATIVE_ZAHLEN['kampagnen_kalibrierung'] or n_pruef < rg.NORMATIVE_ZAHLEN[
            'kampagnen_pruefung'] or profil.reduziert
        quelle = (f'AP-13-Planungssimulation (Szenario {sid}, {stufe}, κ = {kappa:.4f}, {n_kal}+{n_pruef} Kampagnen je '
                  f'Kandidat, Profil {profil.id})' + (' – Entwicklungsdiagnostik, keine Planung für Teil B' if red
                                                      else ''))
        treffer = [x for x in schritte if x.get('erfuellt')]
        out = dict(n_min=treffer[0]['n_min'] if treffer else None, n0=treffer[0]['n0'] if treffer else None,
                   kappa=kappa, bedingung=bedingung, kandidaten=schritte, quelle=quelle, reduziert=bool(red),
                   power_bedingung='offen (Regel planung.power), nicht geprüft')
        if not treffer:
            out['grund'] = 'kein Kandidat erreicht P(H1 und H2 bestätigt | exakt) ≥ 0,8'
        if protokoll is not None:
            protokoll.append(dict(k=e['k'], N_z=e['N_z'], **out))
        return out
    return planung
