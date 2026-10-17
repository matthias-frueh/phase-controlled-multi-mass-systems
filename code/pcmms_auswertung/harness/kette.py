"""Durchgängige Kette einer synthetischen Kampagne: Generator (Ebene H oder Z) → AP-11 (Kalibrierung aus P0-Daten,
Pilotanalyse) → Teil B → AP-12 (Stufe 1 bei Ebene Z, Stufe 2) und getrennt die Wahrheit.

Werkzeug-8-Werte für Teil B (c von H1 und H1Z, Rauschbias, Intervalltyp von H2) sind Eingaben: aus der Kalibrier-
simulation (harness.kalibrierung) oder ausdrücklich als Testvorgabe gekennzeichnet. Die Kette prüft keine Raten;
das leisten harness.kampagnen und harness.kalibrierung.

Das Verfahren (verfahren.Verfahren) legt fest, an welches k die Phase-0-Größen in Teil B gebunden sind (Vorgabe: k_max
und N_z des Plans) und wie Phase 1 abläuft; es steht in der Herkunft jeder Kampagne.
"""
import os
import time

import numpy as np
from scipy import stats

from .. import anpassung, auswertung, formate, pilot, teil_b, verfahren as vf, zufall
from ..generator import ebene_h, ebene_z, kalibrierdaten, kampagne, szenarien, wahrheit

BAND_HZ = (20.0, 600.0)                 # Anpassungsband der Entwicklungsläufe (ausdrücklich, Regel p0.4.band)


def testvorgabe_werkzeug8(nu=19, kennzeichnung='TESTVORGABE (keine Kalibriersimulation)'):
    """Werkzeug-8-Platzhalter für Softwaretests: c = c_B (Bonferroni), Rauschbias 0, Perzentilintervall ungeprüft.
    Ergebnisse damit sind Softwareprüfungen, keine Kalibrierung."""
    cB = float(stats.t.ppf(1 - 0.05 / 294, nu))
    cBZ = float(stats.t.ppf(1 - 0.05 / 882, nu))
    z = np.zeros(21)
    zz = np.zeros((21, 3))
    return dict(c_H1=cB, c_H1_herkunft=f'{kennzeichnung}: c_B = t(1 − 0,05/294; {nu})', c_H1Z=cBZ,
                c_H1Z_herkunft=f'{kennzeichnung}: c_B = t(1 − 0,05/882; {nu})', bias0=z, bias1=z, u_bias0=z,
                u_bias1=z, bias0_zellen=zz, bias1_zellen=zz, u_bias0_zellen=zz, u_bias1_zellen=zz,
                bias_herkunft=f'{kennzeichnung}: b̂ = 0', h2_intervall=dict(typ='perzentil', niveau=0.95,
                                                                           quelle=kennzeichnung))


def plan_info(m, n_min=None):
    """Extern vorgegebener Entwicklungsplan des Harness (nicht aus der Suche): k_max des Systems (oder der Planungssuche),
    N_z und T_Lauf des Kampagnenplans, n Blöcke, r = n − n_min."""
    p = m.plan
    e2 = p.einstellung2
    n_min = n_min if n_min is not None else max(p.n_bloecke - 2, 2)
    return dict(f=m.system.f, k_max=m.system.k_max, N_z=p.n_zyklen, T_lauf=p.T_lauf, n_min=n_min,
                n0=p.n0, r=p.n_bloecke - n_min, n=p.n_bloecke, d=p.tage, n_max=None, zusatz=p.zusatz,
                einstellung2=None if not e2 else dict(art=e2['art'], s=e2.get('s'), f2=e2.get('f2'),
                                                      punkte_I=list(e2['punkte_I'])),
                seed_bootstrap=None, seed_reihenfolge=None, laufreihenfolge=None,
                quelle='Entwicklungsplan des Harness (extern, nicht aus der Pilotsuche)')


def kalibrierung_erzeugen(sz, m, seed):
    """P0-Daten des Szenarios (mit seinen Kalibrierabweichungen) und AP-11-Kalibrierung."""
    kw = {a: b for a, b in sz.kalibrierung}
    mes, wahr = kalibrierdaten.p0_messungen(m.system, zufall.strom(seed, 'p0'), p01=kw.get('p01'),
                                            p04=kw.get('p04'), p05=kw.get('p05'))
    return mes, wahr, anpassung.kalibrieren(mes, band_hz=BAND_HZ)


def kampagne_erzeugen(sid, stufe, plan, seed, staerke=None, rausch=None, k_max=None):
    """Modell, Laufplan und Ebene-H-Tabelle einer Kampagne mit getrennten Zufallsströmen."""
    m = szenarien.modell(sid, stufe, plan=plan, staerke=staerke, rausch=rausch, k_max=k_max)
    laeufe = kampagne.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    tab = ebene_h.erzeuge(m, laeufe, zufall.strom(seed, 'generator'))
    return m, laeufe, tab


def teil_b_erzeugen(tab, kal, m, profil, werkzeug8, seed, n_min=None, kennung='SYNTH-KETTE', verfahren=None):
    """Pilotanalyse und Teil B; die Phase-0-Größen sind nach dem Verfahren gebunden (Vorgabe: an k_max und N_z des
    Plans, auch wenn k der Pilotgrößen davon abweicht)."""
    v = vf.oder_standard(verfahren)
    tab0 = tab.auswahl(tab.spalte('phase', int) == 0)
    pe = pilot.pilot_auswerten(tab0, kal, profil, m.system.f, seed=seed)
    pl = plan_info(m, n_min)
    pl.update(seed_bootstrap=zufall.unterseed(seed, 'bootstrap'), seed_reihenfolge=seed)
    tb = teil_b.erstellen(tab0, kal, pe, profil, pl, werkzeug8, kennung=kennung,
                          seed_b0=zufall.unterseed(seed, 'teil_b'), bindung=v.bindung)
    tb['verfahren'] = v.kennung()
    return tb, pe


def kette(sid, stufe, profil, plan=None, seed=1, werkzeug8=None, staerke=None, kalibrierung=None, n_min=None,
          mit_wahrheit=True, rausch=None, k_max=None, verfahren=None):
    """Eine Kampagne auf Ebene H vollständig: Ergebnis von AP-12, Teil B, Kalibrierung, Wahrheit (getrennt)."""
    v = vf.oder_standard(verfahren)
    sz = szenarien.KATALOG[sid]
    plan = kampagne.Plan() if plan is None else plan
    kennung = formate.synth_kennung('KETTE', sid, stufe, seed)
    zeit = {}
    t = time.perf_counter()
    m, laeufe, tab = kampagne_erzeugen(sid, stufe, plan, seed, staerke, rausch, k_max)
    tab.meta.setdefault('kennung', kennung)
    zeit['generator'] = time.perf_counter() - t
    t = time.perf_counter()
    if kalibrierung is None:
        mes, kwahr, kal = kalibrierung_erzeugen(sz, m, seed)
    else:
        kal = kalibrierung
    zeit['ap11_kalibrierung'] = time.perf_counter() - t
    w8 = testvorgabe_werkzeug8() if werkzeug8 is None else werkzeug8
    t = time.perf_counter()
    tb, pe = teil_b_erzeugen(tab, kal, m, profil, w8, seed, n_min, kennung=kennung, verfahren=v)
    zeit['ap11_pilot_teil_b'] = time.perf_counter() - t
    t = time.perf_counter()
    erg = auswertung.auswerten(tab, kal, tb, profil)
    zeit['ap12_stufe2'] = time.perf_counter() - t
    out = dict(ergebnis=erg, teil_b=tb, kalibrierung=kal, tabelle=tab, modell=m, laeufe=laeufe, pilot=pe,
               laufzeit_s={k: round(x, 3) for k, x in zeit.items()}, verfahren=v.kennung())
    if mit_wahrheit:
        out['wahrheit'] = wahrheit.berechne(m, kampagne.schnitt_konfigurationen(m.plan))
    return out


def eingang_schreiben(verzeichnis, sid, stufe, plan, seed, profil, ebene='Z', nur=None, werkzeug8=None,
                      kennung=None, verfahren=None):
    """Frische Ausgabestruktur: eingang/ (P0-Daten, Kalibrierung, Teil B, Regelprofil, Rohläufe bzw.
    Zusammenfassungen, Manifest) und wahrheit/ (nur Harness). Rückgabe der Pfade."""
    kennung = kennung or formate.synth_kennung('KETTE', sid, stufe, seed)
    sz = szenarien.KATALOG[sid]
    m, laeufe, tab = kampagne_erzeugen(sid, stufe, plan, seed)
    mes, kwahr, kal = kalibrierung_erzeugen(sz, m, seed)
    ein = os.path.join(verzeichnis, 'eingang')
    wv = os.path.join(verzeichnis, 'wahrheit')
    kalibrierdaten.schreibe_p0(os.path.join(ein, 'p0_messung'), mes, kennung)
    anpassung.schreibe_kalibrierung(os.path.join(ein, 'kalibrierung'), kal, kennung)
    from .. import regeln
    regeln.schreibe_profil(os.path.join(ein, 'regelprofil'), profil)
    w8 = testvorgabe_werkzeug8() if werkzeug8 is None else werkzeug8
    tb, pe = teil_b_erzeugen(tab, kal, m, profil, w8, seed, kennung=kennung, verfahren=verfahren)
    teil_b.schreiben(os.path.join(ein, 'teil_b'), tb, kennung)
    pilot.schreibe_pilot(os.path.join(ein, 'pilot'), pe, kennung)
    pfade = dict(eingang=ein, wahrheit=wv, kalibrierung=os.path.join(ein, 'kalibrierung'),
                 teil_b=os.path.join(ein, 'teil_b'), regelprofil=os.path.join(ein, 'regelprofil'))
    if ebene == 'Z':
        kalib_wahr = dict(nullpunkt_adc=kwahr['p01']['nullpunkt_adc'],
                          empfindlichkeit_N_je_adc=kwahr['p01']['empfindlichkeit_N_je_adc'])
        ebene_z.erzeuge(m, laeufe, zufall.strom(seed, 'generator_z'), os.path.join(ein, 'laeufe'), kennung, kalib_wahr,
                        nur=nur)
        pfade['manifest'] = os.path.join(ein, 'laeufe')
    else:
        tab.schreiben(os.path.join(ein, 'zusammenfassungen'), kennung)
        pfade['zusammenfassungen'] = os.path.join(ein, 'zusammenfassungen')
    w, felder = wahrheit.berechne(m, kampagne.schnitt_konfigurationen(m.plan))
    wahrheit.speichern(os.path.join(wv, 'wahrheit'), m, w, felder, kennung, sid)
    formate.schreibe_objekt(os.path.join(wv, 'p0_wahrheit'), formate.kopf('wahrheit', kennung), kwahr)
    return pfade
