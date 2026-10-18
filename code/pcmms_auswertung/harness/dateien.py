"""Dateikette aus einer frischen Ausgabestruktur (Abnahme „Durchgängigkeit“): jeder Schritt liest und schreibt Dateien.

  <ziel>/eingang/   p0_messung, planangaben, laeufe/ (Ebene Z: Rohläufe und Manifest) oder zusammenfassungen (Ebene H),
                    kalibrierung (AP-11), zusammenfassungen (Stufe 1 bei Ebene Z), pilot, teil_b, regelprofil
  <ziel>/ergebnis/  ergebnis (AP-12), bewertung (Harness)
  <ziel>/wahrheit/  wahrheit, p0_wahrheit – nur der Generator schreibt und nur der Harness liest sie

Der Generator schreibt ausschließlich Generatorausgaben (Rohdaten bzw. Zusammenfassungen, P0-Daten, Planangaben, die
Wahrheit getrennt). Kalibrierung und Pilot/Teil B entstehen in AP-11 aus diesen Dateien, auf Ebene Z aus den
Stufe-1-Zusammenfassungen der Phase-0-Läufe. Mit denselben Seeds liefert die Dateikette auf Ebene H dieselben Werte wie
harness.kette (gleiche Zufallsströme).
"""
import os

import numpy as np

from .. import anpassung, auswertung, formate, pilot, regeln, stufe1, teil_b, verfahren as vf, zufall
from .. import zusammenfassung as zf
from ..generator import ebene_z, kalibrierdaten, kampagne as kp, szenarien, wahrheit
from . import kette

ORDNER = ('eingang', 'ergebnis', 'wahrheit')


def pfade(ziel):
    e, r, w = (os.path.join(ziel, x) for x in ORDNER)
    return dict(ziel=ziel, eingang=e, ergebnis_dir=r, wahrheit_dir=w, p0=os.path.join(e, 'p0_messung'),
                planangaben=os.path.join(e, 'planangaben'), laeufe=os.path.join(e, 'laeufe'),
                zusammenfassungen=os.path.join(e, 'zusammenfassungen'), kalibrierung=os.path.join(e, 'kalibrierung'),
                pilot=os.path.join(e, 'pilot'), teil_b=os.path.join(e, 'teil_b'),
                regelprofil=os.path.join(e, 'regelprofil'), werkzeug8=os.path.join(e, 'werkzeug8'),
                ergebnis=os.path.join(r, 'ergebnis'), bewertung=os.path.join(r, 'bewertung'),
                wahrheit=os.path.join(w, 'wahrheit'), p0_wahrheit=os.path.join(w, 'p0_wahrheit'))


def generator_schreiben(ziel, sid, stufe, plan, seed, ebene='Z', n_min=None, staerke=None, kennung=None,
                        verfahren=None):
    """Generatorausgaben einer Kampagne in eine frische Struktur; Rückgabe der Pfade. Die Planangaben nennen das
    Verfahren (Bindung der Phase-0-Größen in Teil B). Die Dateikette schreibt den statischen Laufplan; ein Verfahren
    mit Ablauf „zustand“ wird zurückgewiesen statt still statisch gerechnet (Ablauf: kette.kampagne_ablauf)."""
    v = vf.oder_standard(verfahren)
    if v.ablauf != 'statisch':
        raise ValueError(f'Dateikette: Ablauf „{v.ablauf}“ nicht umgesetzt, nur der statische Laufplan; den Ablauf '
                         'der Phase 1 rechnet kette.kampagne_ablauf (Ebene H oder Z)')
    p = pfade(ziel)
    if os.path.exists(p['eingang']) and os.listdir(p['eingang']):
        raise FileExistsError(f'{p["eingang"]} ist nicht leer (frische Ausgabestruktur verlangt)')
    kennung = kennung or formate.synth_kennung('DATEI', sid, stufe, seed)
    sz = szenarien.KATALOG[sid]
    m, laeufe, tab = kette.kampagne_erzeugen(sid, stufe, plan, seed, staerke)
    kw = {a: b for a, b in sz.kalibrierung}
    mes, kwahr = kalibrierdaten.p0_messungen(m.system, zufall.strom(seed, 'p0'), p01=kw.get('p01'),
                                             p04=kw.get('p04'), p05=kw.get('p05'))
    kalibrierdaten.schreibe_p0(p['p0'], mes, kennung)
    pl = kette.plan_info(m, n_min)
    pl.update(seed_bootstrap=zufall.unterseed(seed, 'bootstrap'), seed_reihenfolge=seed,
              seed_teil_b=zufall.unterseed(seed, 'teil_b'), seed_pilot=int(seed), szenario=sid, stufe=stufe,
              ebene=ebene, bindung=v.bindung, verfahren=v.kennung())
    formate.schreibe_objekt(p['planangaben'], formate.kopf('planangaben', kennung), pl)
    if ebene == 'Z':
        kalib_wahr = dict(nullpunkt_adc=kwahr['p01']['nullpunkt_adc'],
                          empfindlichkeit_N_je_adc=kwahr['p01']['empfindlichkeit_N_je_adc'])
        ebene_z.erzeuge(m, laeufe, zufall.strom(seed, 'generator_z'), p['laeufe'], kennung, kalib_wahr)
    elif ebene == 'H':
        tab.schreiben(p['zusammenfassungen'], kennung)
    else:
        raise ValueError(f'Ebene {ebene!r} (Z oder H)')
    w, felder = wahrheit.berechne(m, kp.schnitt_konfigurationen(m.plan))
    wahrheit.speichern(p['wahrheit'], m, w, felder, kennung, sid)
    formate.schreibe_objekt(p['p0_wahrheit'], formate.kopf('wahrheit', kennung), kwahr)
    return p


def ap11_kalibrierung(p0, ausgabe, band_hz):
    k, mes = anpassung.lies_p0(p0)
    kal = anpassung.kalibrieren(mes, band_hz=tuple(band_hz))
    anpassung.schreibe_kalibrierung(ausgabe, kal, k['kennung'])
    return kal


def ap12_stufe1(manifest, kalibrierung, ausgabe):
    _, kal = anpassung.lies_kalibrierung(kalibrierung)
    tab = stufe1.manifest_auswerten(manifest, kal)
    tab.schreiben(ausgabe, tab.meta['kennung'])
    return tab


def lies_werkzeug8(pfad):
    if pfad in (None, 'testvorgabe'):
        return kette.testvorgabe_werkzeug8()
    return formate.lies_objekt(pfad, 'werkzeug8')[1]


def ap11_teil_b(zusammenfassungen, kalibrierung, planangaben, profil, werkzeug8, ausgabe_teil_b, ausgabe_pilot):
    """Pilotanalyse und Teil B aus den Phase-0-Zusammenfassungen, der AP-11-Kalibrierung und Werkzeug 8."""
    tab = zf.LaufTabelle.lesen(zusammenfassungen)
    _, kal = anpassung.lies_kalibrierung(kalibrierung)
    k, pl = formate.lies_objekt(planangaben, 'planangaben')
    tab0 = tab.auswahl(tab.spalte('phase', int) == 0)
    pe = pilot.pilot_auswerten(tab0, kal, profil, pl['f'], seed=pl['seed_pilot'])
    pilot.schreibe_pilot(ausgabe_pilot, pe, k['kennung'])
    tb = teil_b.erstellen(tab0, kal, pe, profil, pl, lies_werkzeug8(werkzeug8), kennung=k['kennung'],
                          seed_b0=pl['seed_teil_b'], bindung=pl.get('bindung', vf.STANDARD.bindung))
    if pl.get('verfahren') is not None:
        tb['verfahren'] = pl['verfahren']
    teil_b.schreiben(ausgabe_teil_b, tb, k['kennung'])
    return tb


def ap12_auswerten(zusammenfassungen, kalibrierung, teil_b_pfad, profil, ausgabe):
    erg = auswertung.auswerten(zusammenfassungen, kalibrierung, teil_b_pfad, profil)
    kenn = erg['herkunft']['kennung'] or formate.synth_kennung('ERGEBNIS')
    auswertung.schreibe_ergebnis(ausgabe, erg, kenn)
    return erg


def bewerten(ergebnis, wahrheit_pfad, ausgabe=None):
    """Harness: Ergebnis gegen die Wahrheit (Klasse, wahre Residuen relativ zu Δ_rel, Ausgänge)."""
    _, erg = auswertung.lies_ergebnis(ergebnis)
    k, w, _ = wahrheit.laden(wahrheit_pfad)
    out = dict(szenario=k.get('szenario'), klasse=w.get('klasse'), r_max_rel=w.get('r_max_rel_beide'),
               ausgaenge={h: dict(ausgang=erg[h]['ausgang'], grund=erg[h].get('grund'),
                                  zusaetze=erg[h].get('zusaetze', [])) for h in ('H1', 'H1Z', 'H2', 'H3', 'H4')},
               erwartung=_erwartung(w.get('klasse')), kennung=k['kennung'])
    out['H1_falsifiziert_bei_R0_R1'] = bool(out['klasse'] in ('R0', 'R1') and
                                            erg['H1']['ausgang'] == 'falsifiziert')
    if ausgabe:
        formate.schreibe_objekt(ausgabe, formate.kopf('bewertung', k['kennung']), out)
    return out


def _erwartung(klasse):
    return {'R0': 'H1 nicht falsifiziert (K01/K02), Bestätigung erwartet bei ausreichender Präzision',
            'R1': 'H1 nicht falsifiziert (K03); Zusatz „Abweichung nachgewiesen“ möglich',
            'R2': 'H1 nicht bestätigt (K04)', 'R3': 'nur berichtet; „nicht entscheidbar“ erwartet',
            'R4': 'H1 falsifiziert mit Power ≥ 0,8 (K07/K21)'}.get(klasse, 'keine Klasse')


def kette_dateien(ziel, sid, stufe, profil, plan=None, seed=1, ebene='Z', n_min=None, werkzeug8=None, band_hz=None,
                  verfahren=None):
    """Alle Schritte nacheinander aus einer frischen Ausgabestruktur; Rückgabe dict(pfade, ergebnis, bewertung)."""
    plan = kp.Plan() if plan is None else plan
    p = generator_schreiben(ziel, sid, stufe, plan, seed, ebene, n_min, verfahren=verfahren)
    regeln.schreibe_profil(p['regelprofil'], profil)
    prof = regeln.lade_profil(p['regelprofil'])
    ap11_kalibrierung(p['p0'], p['kalibrierung'], band_hz or kette.BAND_HZ)
    if ebene == 'Z':
        ap12_stufe1(p['laeufe'], p['kalibrierung'], p['zusammenfassungen'])
    if werkzeug8 is not None and not isinstance(werkzeug8, str):
        formate.schreibe_objekt(p['werkzeug8'], formate.kopf('werkzeug8', formate.synth_kennung('W8')), werkzeug8)
        werkzeug8 = p['werkzeug8']
    ap11_teil_b(p['zusammenfassungen'], p['kalibrierung'], p['planangaben'], prof, werkzeug8, p['teil_b'], p['pilot'])
    erg = ap12_auswerten(p['zusammenfassungen'], p['kalibrierung'], p['teil_b'], prof, p['ergebnis'])
    bw = bewerten(p['ergebnis'], p['wahrheit'], p['bewertung'])
    return dict(pfade=p, ergebnis=erg, bewertung=bw)


def ergebnis_hash(erg):
    """Prüfsumme der Auswertung ohne Laufzeit und Codestand (Reproduzierbarkeit, Wahrheitstrennung)."""
    e = {k: v for k, v in erg.items() if k not in ('herkunft', 'text')}
    h = {k: v for k, v in erg['herkunft'].items() if k not in ('laufzeit_s', 'code_version')}
    return formate.sha256_json(dict(e, herkunft=h))


def wahrheit_verfaelschen(ziel, art='aendern'):
    """Negativtest der Trennung: Wahrheit ändern ('aendern') oder entfernen ('entfernen')."""
    p = pfade(ziel)
    if art == 'entfernen':
        for f in os.listdir(p['wahrheit_dir']):
            os.remove(os.path.join(p['wahrheit_dir'], f))
        os.rmdir(p['wahrheit_dir'])
        return
    k, inhalt, felder = wahrheit.laden(p['wahrheit'])
    felder = {n: (np.asarray(v) * 7.0 + 1.0 if np.issubdtype(np.asarray(v).dtype, np.number) else v)
              for n, v in felder.items()}
    inhalt = dict(inhalt, klasse='R4', r_max_rel_beide=99.0)
    formate.schreibe(p['wahrheit'], k, felder, inhalt)
