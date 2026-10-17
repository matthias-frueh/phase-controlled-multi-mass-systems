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

from .. import ablauf, anpassung, auswertung, formate, pilot, rohdaten, stufe1, teil_b, verfahren as vf, zufall
from .. import zusammenfassung as zf
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


# ── Zustandsbehafteter Ablauf der Phase 1 ────────────────────────────────────────────────────────────────
class MessungH:
    """Messung eines Versuchs auf Ebene H: der ursprüngliche Versuch eines geplanten Laufs aus dessen Ziehung im Vorrat
    (Strom „generator“ wie kampagne_erzeugen), gebildet zum tatsächlichen Zeitpunkt; ein zusätzlicher Versuch aus dem
    Strom (seed, „generator_versuch“, Versuchsnummer). Ereignisse mit „versuch“-Auswahl gelten für passende Versuche."""

    def __init__(self, modell, laeufe, seed, rausch=None):
        self.modell, self.seed = modell, int(seed)
        self.vorrat = ebene_h.Vorrat(modell, laeufe, zufall.strom(seed, 'generator'), rausch)
        self.versuch_ereignisse = [e for e in modell.effekte_art('ereignis') if 'versuch' in e]

    def _effekte(self, spec, versuch):
        return [e for e in self.versuch_ereignisse if ablauf.versuch_passt(e['versuch'], spec, versuch)]

    def phase0(self, laeufe):
        return self.vorrat.tabelle([l for l in laeufe if l['phase'] == 0])

    def messen(self, spec, versuch):
        effs = self._effekte(spec, versuch)
        if versuch['geplant']:
            k, d, _ = self.vorrat.lauf(spec, bezug=versuch['bezug'], ereignisse=effs)
        else:
            k, d, _ = self.vorrat.lauf(spec, rng=zufall.strom(self.seed, 'generator_versuch', versuch['index']),
                                       ereignisse=effs)
        return k, d


class MessungZ(MessungH):
    """Messung eines Versuchs über Ebene Z und Stufe 1: dieselben Laufziehungen wie MessungH, die Rohzeitreihe aus dem
    Strom (seed, „generator_z_versuch“, Kennung) zum tatsächlichen Zeitpunkt, als Rohdatei geschrieben und mit Stufe 1
    zusammengefasst; der Ablauf entscheidet auf der Stufe-1-Zusammenfassung."""

    def __init__(self, modell, laeufe, seed, verzeichnis, kalib_wahr, kalibrierung, kennung, rausch=None):
        super().__init__(modell, laeufe, seed, rausch)
        self.verzeichnis, self.kalib_wahr, self.kalibrierung, self.kennung = verzeichnis, kalib_wahr, kalibrierung, kennung
        self.f_s = ebene_z.abtastrate(modell.system.f, modell.system.k_max)
        self.rausch = self.vorrat.rausch
        self.manifest = []
        os.makedirs(verzeichnis, exist_ok=True)

    def _roh(self, spec, z, zeile, rng, effs):
        inhalt, daten = ebene_z.zeitreihe(self.modell, z['g'], zeile, spec, rng, self.kalib_wahr, self.f_s,
                                          rausch=self.rausch, ereignisse=effs)
        self.manifest.append(rohdaten.schreibe_rohlauf(self.verzeichnis, inhalt, daten, self.kennung))
        lz = stufe1.laufzusammenfassung(os.path.join(self.verzeichnis, spec['lauf_id']), self.kalibrierung,
                                        k_voll=self.modell.k_voll)
        return lz.kopf, {f: np.asarray(x)[None] for f, x in lz.daten.items()}

    def phase0(self, laeufe):
        koepfe, zeilen = [], []
        for l in laeufe:
            if l['phase'] != 0:
                continue
            z, zeile = self.vorrat.ort[l['lauf_id']]
            effs = self.vorrat.ereignisse.get(l['position'], [])
            k, d = self._roh(l, z, zeile, zufall.strom(self.seed, 'generator_z_versuch', l['lauf_id']), effs)
            koepfe.append(k)
            zeilen.append(d)
        return zf.LaufTabelle(koepfe, {f: np.concatenate([d[f] for d in zeilen]) for f in zeilen[0]})

    def messen(self, spec, versuch):
        effs = self._effekte(spec, versuch)
        if versuch['geplant']:
            z, zeile = self.vorrat.ort[versuch['bezug']]
            effs = list(self.vorrat.ereignisse.get(spec.get('position_geplant'), [])) + effs
        else:
            z, zeile = ebene_h.ziehen(self.modell, [spec], zufall.strom(self.seed, 'generator_versuch',
                                                                         versuch['index']), self.rausch), 0
        return self._roh(spec, z, zeile, zufall.strom(self.seed, 'generator_z_versuch', versuch['id']), effs)


def ablauf_kennung(m, sid, stufe, seed, verfahren, sw, s3, profil, ebene):
    """Herkunft eines Ablaufs (gehört zum Ablaufstand): Verfahren mit Ablaufversion und Optionen, Szenario, Seed,
    Modell, Plan, die Entscheidungsschwellen aus Teil B (gerundet, ablauf.schwellen_kennung) und das Profil."""
    from dataclasses import asdict
    return dict(verfahren=verfahren.kennung(), szenario=sid, stufe=stufe, seed=int(seed), ebene=ebene,
                modell_sha256=formate.sha256_json(szenarien.beschreibung(m)), plan=asdict(m.plan),
                schwellen_sha256=ablauf.schwellen_kennung(sw, s3), profil_sha256=profil.sha256())


def kampagne_ablauf(sid, stufe, plan, seed, profil, werkzeug8=None, n_min=None, verfahren=None, staerke=None,
                    rausch=None, k_max=None, modell=None, ebene='H', verzeichnis=None, zustand=None, bis=None):
    """Kampagne mit zustandsbehaftetem Ablauf der Phase 1: Laufplan (Strom „reihenfolge“), Phase 0 zu den geplanten
    Zeitpunkten, Kalibrierung, Pilotanalyse, Teil B (Bindung an den Plan), dann Phase 1 als Ablauf; der
    Reihenfolgegenerator zieht danach die Wiederholungsplätze. modell: vorgegebenes Generatormodell (Prüffälle mit
    Ereignissen; Kalibrierabweichungen weiter aus dem Szenario sid). ebene 'Z': Rohdaten und Stufe 1 in verzeichnis.
    zustand: gespeicherter Ablaufstand (Fortsetzung; die Kennung muss passen); bis: technische Unterbrechung nach so
    vielen Phase-1-Versuchen. Rückgabe dict(modell, laeufe, tab0, kalibrierung, teil_b, pilot, ablauf, kennung, …)."""
    v = verfahren if verfahren is not None else vf.ZUSTAND
    if v.ablauf != 'zustand':
        raise ValueError('kampagne_ablauf verlangt ein Verfahren mit Ablauf „zustand“')
    sz = szenarien.KATALOG[sid]
    plan = kampagne.Plan() if plan is None else plan
    m = modell if modell is not None else szenarien.modell(sid, stufe, plan=plan, staerke=staerke, rausch=rausch,
                                                            k_max=k_max)
    kennung = formate.synth_kennung('ABLAUF', sid, stufe, seed)
    rng_r = zufall.strom(seed, 'reihenfolge')
    laeufe = kampagne.laufplan(m.plan, rng_r)
    mes, kwahr, kal = kalibrierung_erzeugen(sz, m, seed)
    if ebene == 'Z':
        kw = dict(nullpunkt_adc=kwahr['p01']['nullpunkt_adc'],
                  empfindlichkeit_N_je_adc=kwahr['p01']['empfindlichkeit_N_je_adc'])
        messung = MessungZ(m, laeufe, seed, verzeichnis, kw, kal, kennung, rausch)
    elif ebene == 'H':
        messung = MessungH(m, laeufe, seed, rausch)
    else:
        raise ValueError(f'Ebene {ebene!r} (Z oder H)')
    tab0 = messung.phase0(laeufe)
    w8 = testvorgabe_werkzeug8() if werkzeug8 is None else werkzeug8
    tb, pe = teil_b_erzeugen(tab0, kal, m, profil, w8, seed, n_min, kennung=kennung, verfahren=v)
    sw = auswertung._schwellen(tb, profil)
    gueltig0 = {x for e in tb['nr3']['einzel0'] for x in e['lauf_ids']}
    s3 = ablauf.s3_basis(tab0, gueltig0, sw.kmax)
    geplant = [l for l in laeufe if l['phase'] == 1]
    ak = ablauf_kennung(m, sid, stufe, seed, v, sw, s3, profil, ebene)
    if zustand is None:
        a = ablauf.Ablauf(geplant, messung, sw, s3, rng_r, v.optionen, m.plan.T_lauf, m.plan.tag_pause, kennung=ak)
    else:
        a = ablauf.Ablauf.aus_zustand(zustand, geplant, messung, sw, s3, rng_r, m.plan.T_lauf, m.plan.tag_pause, ak)
    a.ausfuehren(bis)
    out = dict(modell=m, laeufe=laeufe, tab0=tab0, kalibrierung=kal, teil_b=tb, pilot=pe, ablauf=a, kennung=ak,
               messung=messung, p0_messung=mes, p0_wahrheit=kwahr)
    return out


def ablauf_tabelle(r):
    """Phase-0-Läufe und alle Versuche der Phase 1 in einer Tabelle mit dem Ablaufstand (meta „ablauf“)."""
    t1 = r['ablauf'].tabelle()
    t0 = r['tab0']
    return zf.LaufTabelle(t0.koepfe + t1.koepfe, {f: np.concatenate([t0.daten[f], t1.daten[f]]) for f in t0.daten},
                          meta=dict(t1.meta))


def kette(sid, stufe, profil, plan=None, seed=1, werkzeug8=None, staerke=None, kalibrierung=None, n_min=None,
          mit_wahrheit=True, rausch=None, k_max=None, verfahren=None):
    """Eine Kampagne auf Ebene H vollständig: Ergebnis von AP-12, Teil B, Kalibrierung, Wahrheit (getrennt). Mit einem
    Verfahren „zustand“ läuft Phase 1 als zustandsbehafteter Ablauf (kampagne_ablauf); das Ergebnis enthält dann den
    Ablaufbericht."""
    v = vf.oder_standard(verfahren)
    if v.ablauf == 'zustand':
        return _kette_ablauf(sid, stufe, profil, plan, seed, werkzeug8, staerke, kalibrierung, n_min, mit_wahrheit,
                             rausch, k_max, v)
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


def _kette_ablauf(sid, stufe, profil, plan, seed, werkzeug8, staerke, kalibrierung, n_min, mit_wahrheit, rausch,
                  k_max, v):
    if kalibrierung is not None:
        raise ValueError('kette mit Ablauf „zustand“: vorgegebene Kalibrierung nicht vorgesehen')
    zeit = {}
    t = time.perf_counter()
    r = kampagne_ablauf(sid, stufe, plan, seed, profil, werkzeug8, n_min, v, staerke, rausch, k_max)
    zeit['ablauf'] = time.perf_counter() - t
    t = time.perf_counter()
    tab = ablauf_tabelle(r)
    erg = auswertung.auswerten(tab, r['kalibrierung'], r['teil_b'], profil)
    zeit['ap12_stufe2'] = time.perf_counter() - t
    out = dict(ergebnis=erg, teil_b=r['teil_b'], kalibrierung=r['kalibrierung'], tabelle=tab, modell=r['modell'],
               laeufe=r['laeufe'], pilot=r['pilot'], laufzeit_s={k: round(x, 3) for k, x in zeit.items()},
               verfahren=v.kennung(), ablauf=r['ablauf'].bericht())
    if mit_wahrheit:
        out['wahrheit'] = wahrheit.berechne(r['modell'], kampagne.schnitt_konfigurationen(r['modell'].plan))
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
