"""Gezielte Entwicklungsläufe von AP-13 (Auftrag Etappe 5): eine konfigurierbare Folge von Kalibrier-, Prüf- und
Szenariokampagnen, Gegenproben und Prüfsatz mit kompakter Zusammenfassung (Raten mit Zähler, Nenner, MC-Fehler).

Alles ist ausdrücklich konfiguriert (Profil mit Reduktion, Plan, Kampagnenzahlen, Seeds, Prozesse). Die große Matrix mit
≥ 1000 Kampagnen je Szenario und Stufe startet dieses Modul nicht; mit kleineren Zahlen ist jedes Ergebnis
Entwicklungsdiagnostik und so gekennzeichnet. Die Bewertung gegen die Kriterien K01–K21 macht harness.kriterien.
"""
import os
import time

import numpy as np

from .. import formate, regeln
from ..generator import kampagne as kp
from . import abgleich, dateien, ebenen, kalibrierung, kampagnen, kette, planung, pruefsatz, s3

# Szenariopunkte je System; c, Rauschbias und Intervalltyp stammen aus der Kalibrierung an N01 desselben Systems
A4_SZENARIEN = ('N03-ungleich', 'N03-N3bindet', 'N04-laufart', 'N05-F', 'N05-N2', 'N05-N3', 'A04-R1', 'A04-R2',
                'A04-R3', 'A04-R4', 'E07-verstaerkung', 'E07-basisdrift', 'H01-zelt', 'H-fehlend', 'S02-kontrolllauf',
                'S06-saettigung', 'S-indexfehler')
V1G0_SZENARIEN = ('A06-phase', 'H03-phase', 'I01-amplitude', 'I01-frequenz', 'I04-drift')
V1G60H_SZENARIEN = ('I02-amplitude', 'I02-frequenz', 'I05-misch', 'S01a-liftoff')
EIGENE_SYSTEME = ('C03-GF1', 'C03-GF5', 'C04-steif', 'E04-kette', 'A07-hertz50')   # mit Testvorgabe für c
STANDARD = dict(profil_reduktion=dict(bootstrap_B=1000, h3_mc=1000, eps_ctrl_datensaetze=1000),
                plan=dict(n0=20, n_pilot=20, n_bloecke=24), n_min=18, stufe='L1', seed=20261016,
                n_kal=200, n_pruef=200, n_szenario=40, n_kal_v1=60, n_pruef_v1=60, n_szenario_v1=30,
                n_eigen=30, k06_stufen=('L0', 'L2', 'L4'), n_k06=40, n_ebenen=4, n_planung=(4, 4),
                planung_kandidaten=(18, 24), planung_max_aufrufe=2, zeltfit_fits=4000,
                referenz=(('N01-A4', 'L2'), ('A04-R2', 'L1'), ('A04-R4', 'L1')))


def _kurz_kal(k):
    """Kompakte Fassung der Kalibrierung (ohne Felder je Kampagne)."""
    w8 = {x: (np.asarray(v).tolist() if isinstance(v, np.ndarray) else v) for x, v in k['werkzeug8'].items()}
    return dict(meta=k['meta'], c_H1=k['c_H1'], c_H1Z=k['c_H1Z'], pruefung=k['pruefung'], gepoolt=k['gepoolt'],
                pruefschwelle=k['pruefschwelle'], h2=dict(typ=k['h2'].get('typ'), niveau=k['h2'].get('niveau'),
                                                          schluessel=k['h2'].get('schluessel'),
                                                          ueberdeckung=k['h2'].get('ueberdeckung'),
                                                          grund=k['h2'].get('grund')),
                gemeinsame_bestaetigung=k['gemeinsame_bestaetigung'],
                rauschbias=dict(b0=np.asarray(k['rauschbias']['b0']).tolist(),
                                u_b0=np.asarray(k['rauschbias']['u_b0']).tolist(),
                                b1=np.asarray(k['rauschbias']['b1']).tolist(),
                                u_b1=np.asarray(k['rauschbias']['u_b1']).tolist(),
                                verhaeltnis_zu_u_c=k['rauschbias']['verhaeltnis_zu_u_c']),
                restbias=k.get('restbias'), raten_pruefung=k['raten_pruefung']['raten'],
                gueltigkeit_pruefung=k['raten_pruefung']['gueltigkeit'], werkzeug8=w8, zmax=k['zmax'])


def _szenario(sid, stufe, profil, n, seed, plan, n_min, w8, prozesse, mit_ueberdeckung=False):
    lauf = kampagnen.ausfuehren(sid, stufe, profil, n, seed, 'pruefung', plan, n_min, w8, prozesse=prozesse)
    r = kampagnen.raten(lauf)
    r['wahrheit_detail'] = {k: lauf['wahrheit'].get(k) for k in ('klasse', 'r_max_rel_beide', 'r_max_rel_yhat0',
                                                                  'r_max_rel_yhat1', 'klasse_sens_faktor_0_1',
                                                                  'klasse_sens_fassung_A', 'r_max_rel_je_groesse',
                                                                  'staerke')}
    if mit_ueberdeckung:
        r['h2_ueberdeckung'] = kalibrierung.h2_ueberdeckung(lauf, profil)
    return r


def ausfuehren(ziel, konfiguration=None, schritte=None, prozesse=4, protokoll=print):
    """Führt die gezielten Läufe aus und schreibt <ziel>/pruefstand.json (+ .npz). Rückgabe der Zusammenfassung."""
    kf = dict(STANDARD, **(konfiguration or {}))
    alle = ('kalibrierung_a4', 'szenarien_a4', 'kalibrierung_v1', 'szenarien_v1', 'eigene', 'k06', 's3', 'ebenen',
            'reproduzierbarkeit', 'wahrheit', 'referenz', 'zeltfit', 'planung', 'pruefsatz')
    schritte = alle if schritte is None else tuple(schritte)
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(**kf['profil_reduktion'])
    plan = kp.Plan(**kf['plan'])
    st, seed, n_min = kf['stufe'], int(kf['seed']), kf['n_min']
    out = dict(konfiguration={k: (list(v) if isinstance(v, tuple) else v) for k, v in kf.items()}, profil=prof.id,
               profil_sha256=prof.sha256(), code_version=formate.code_version(), schritte={}, laufzeit_s={})
    os.makedirs(ziel, exist_ok=True)

    def schritt(name, fn):
        if name not in schritte:
            return None
        t = time.perf_counter()
        protokoll(f'[{time.strftime("%H:%M:%S")}] {name} …')
        r = fn()
        out['laufzeit_s'][name] = round(time.perf_counter() - t, 1)
        out['schritte'][name] = r
        protokoll(f'[{time.strftime("%H:%M:%S")}] {name} fertig ({out["laufzeit_s"][name]} s)')
        formate.schreibe_objekt(os.path.join(ziel, 'pruefstand'), formate.kopf('bewertung', formate.synth_kennung(
            'PRUEFSTAND', seed)), out)
        return r

    w8 = {}
    kal_a4 = schritt('kalibrierung_a4', lambda: kalibrierung.kalibrieren('N01-A4', st, prof, kf['n_kal'], kf['n_pruef'],
                                                                         seed, plan, n_min, prozesse))
    if kal_a4 is not None:
        w8['A4'] = kal_a4['werkzeug8']
        out['schritte']['kalibrierung_a4'] = _kurz_kal(kal_a4)
    schritt('szenarien_a4', lambda: {f'{s}/{st}': _szenario(s, st, prof, kf['n_szenario'], seed, plan, n_min,
                                                            w8.get('A4'), prozesse, s == 'H01-zelt')
                                     for s in A4_SZENARIEN})

    def kal_v1():
        r = {}
        for sid, name in (('N01-V1G0', 'V1-G0'), ('N01-V1G60h', 'V1-G60h')):
            k = kalibrierung.kalibrieren(sid, st, prof, kf['n_kal_v1'], kf['n_pruef_v1'], seed, plan, n_min, prozesse)
            w8[name] = k['werkzeug8']
            r[name] = _kurz_kal(k)
        return r
    schritt('kalibrierung_v1', kal_v1)
    schritt('szenarien_v1', lambda: {**{f'{s}/{st}': _szenario(s, st, prof, kf['n_szenario_v1'], seed, plan, n_min,
                                                               w8.get('V1-G0'), prozesse) for s in V1G0_SZENARIEN},
                                     **{f'{s}/{st}': _szenario(s, st, prof, kf['n_szenario_v1'], seed, plan, n_min,
                                                               w8.get('V1-G60h'), prozesse) for s in V1G60H_SZENARIEN}})
    schritt('eigene', lambda: {f'{s}/{st}': _szenario(s, st, prof, kf['n_eigen'], seed, plan, n_min, None, prozesse)
                               for s in EIGENE_SYSTEME})
    schritt('k06', lambda: {f'N01-A4/{s}': _szenario('N01-A4', s, prof, kf['n_k06'], seed, plan, n_min, None, prozesse)
                            for s in kf['k06_stufen']})
    schritt('s3', lambda: {s: s3.pruefen(s) for s in ('F01-S3', 'F03-S3ungleich')})

    def ebenen_():
        d = os.path.join(ziel, 'ebenen_tmp')
        rf = ebenen.vergleich_rauschfrei('N01-A4', st, os.path.join(d, 'rauschfrei'))
        rv = ebenen.vergleich_verrauscht('N01-A4', st, prof, kf['n_ebenen'], seed, os.path.join(d, 'verrauscht'), plan,
                                         n_min, w8.get('A4'), prozesse=prozesse)
        import shutil
        shutil.rmtree(d, ignore_errors=True)
        return dict(rauschfrei=rf, verrauscht=rv)
    schritt('ebenen', ebenen_)

    def repro():
        a = kampagnen.ausfuehren('A04-R4', st, prof, 4, seed, 'repro', plan, n_min, w8.get('A4'), prozesse=1)
        b = kampagnen.ausfuehren('A04-R4', st, prof, 4, seed, 'repro', plan, n_min, w8.get('A4'), prozesse=min(
            prozesse, 4))
        ha = [formate.sha256_json({k: v for k, v in x.items() if k != 'laufzeit_s'}) for x in a['befunde']]
        hb = [formate.sha256_json({k: v for k, v in x.items() if k != 'laufzeit_s'}) for x in b['befunde']]
        c = kampagnen.ausfuehren('A04-R4', st, prof, 4, seed + 1, 'repro', plan, n_min, w8.get('A4'), prozesse=1)
        hc = [formate.sha256_json({k: v for k, v in x.items() if k != 'laufzeit_s'}) for x in c['befunde']]
        return dict(seriell_gleich_parallel=ha == hb, andere_seeds_verschieden=not set(ha) & set(hc),
                    kampagnen=len(ha), toleranz='bitgleich auf derselben Maschine und Bibliotheksversion')
    schritt('reproduzierbarkeit', repro)

    def wahr():
        d = os.path.join(ziel, 'wahrheit_tmp')
        import shutil
        shutil.rmtree(d, ignore_errors=True)
        r = dateien.kette_dateien(d, 'A04-R4', st, prof, plan=plan, seed=seed, ebene='H', n_min=n_min,
                                  werkzeug8=w8.get('A4'))
        h0 = dateien.ergebnis_hash(r['ergebnis'])
        p = r['pfade']
        dateien.wahrheit_verfaelschen(d, 'aendern')
        h1 = dateien.ergebnis_hash(dateien.ap12_auswerten(p['zusammenfassungen'], p['kalibrierung'], p['teil_b'],
                                                          prof, p['ergebnis'] + '_geaendert'))
        dateien.wahrheit_verfaelschen(d, 'entfernen')
        h2 = dateien.ergebnis_hash(dateien.ap12_auswerten(p['zusammenfassungen'], p['kalibrierung'], p['teil_b'],
                                                          prof, p['ergebnis'] + '_entfernt'))
        shutil.rmtree(d, ignore_errors=True)
        return dict(geaendert_gleich=h0 == h1, entfernt_gleich=h0 == h2, bewertung=r['bewertung'])
    schritt('wahrheit', wahr)

    def ref():
        r = {}
        for sid, stf in kf['referenz']:
            k = kette.kette(sid, stf, prof, plan=plan, seed=seed, n_min=n_min)
            a = abgleich.h1_abgleich(k, prof)
            r[f'{sid}/{stf}'] = dict(alle_innerhalb=a['alle_innerhalb'], ausgang=a['ausgang'], gleich=a['gleich'],
                                     max_abs={x: v['max_abs'] for x, v in a['werte'].items()})
        return r
    schritt('referenz', ref)

    def zelt():
        z = abgleich.zeltfit_vergleich(kf['zeltfit_fits'])
        z['abweichung'] = [list(map(float, x[1:])) for x in z['abweichung']]
        return z
    schritt('zeltfit', zelt)

    def plan_():
        prot = []
        hk = planung.haken('N01-A4', st, prof, kf['n_planung'][0], kf['n_planung'][1], seed, kf['planung_kandidaten'],
                           (20,), plan, prozesse, prot, max_aufrufe=kf.get('planung_max_aufrufe'))
        m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', st, plan, seed)
        _, _, kal = kette.kalibrierung_erzeugen(kette.szenarien.KATALOG['N01-A4'], m, seed)
        from .. import pilot
        zeit = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21,
                    N_I=0)
        pe = pilot.pilot_auswerten(tab.auswahl(tab.spalte('phase', int) == 0), kal, prof, m.system.f, zeit=zeit,
                                   seed=seed, planung=hk)
        return dict(suche={k: v for k, v in pe['suche'].items() if k != 'schritte'}, aufrufe=prot, zeit=zeit,
                    hinweis='Zeitangaben sind Entwicklungsannahmen, keine Teil-B-Werte')
    schritt('planung', plan_)
    schritt('pruefsatz', lambda: pruefsatz.pruefen(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tests',
                                                                'fixtures', 'ap13_pruefsatz')))
    return out


def kompakt(ps):
    """Kompakte Zusammenfassung zum Versionieren: Raten als „Zähler/Nenner“, Kennwerte ohne Felder je Kampagne."""
    def rate(r):
        return None if r is None else f'{r["zaehler"]}/{r["nenner"]}'

    def raten(d):
        return {k: rate(v) for k, v in (d or {}).items() if isinstance(v, dict) and 'zaehler' in v}

    def szen(x):
        out = dict(wahrheit=x.get('wahrheit'), raten=raten(x.get('raten')), gueltigkeit=raten(x.get('gueltigkeit')),
                   abbruch=raten(x.get('abbruch')), u_c_median=x.get('u_c_median'),
                   laufzeit_je_kampagne_s=(x.get('laufzeit_je_kampagne_s') or {}).get('wert'))
        if x.get('h2_ueberdeckung'):
            h = x['h2_ueberdeckung']
            out['h2_ueberdeckung'] = dict(schluessel=h.get('schluessel'), ueberdeckung={
                k: dict(yhat0=rate(v['yhat0']), yhat1=rate(v['yhat1'])) for k, v in (h.get('ueberdeckung') or {}).items()})
        return out

    def kal(k):
        return dict(c_H1=k['c_H1'], c_H1Z=k['c_H1Z'], pruefung=rate(k['pruefung']), gepoolt=k['gepoolt'],
                    h2=dict(schluessel=k['h2'].get('schluessel'), ueberdeckung={
                        x: dict(yhat0=rate(v['yhat0']), yhat1=rate(v['yhat1']))
                        for x, v in (k['h2'].get('ueberdeckung') or {}).items()}),
                    gemeinsame_bestaetigung=rate(k['gemeinsame_bestaetigung']), restbias=k.get('restbias'),
                    raten_pruefung=raten(k['raten_pruefung']), meta=k['meta'])
    s = ps['schritte']
    out = dict(konfiguration=ps['konfiguration'], profil=ps['profil'], profil_sha256=ps['profil_sha256'],
               code_version=ps['code_version'], laufzeit_s=ps['laufzeit_s'], schritte={})
    for name, v in s.items():
        if name == 'kalibrierung_a4':
            out['schritte'][name] = kal(v)
        elif name == 'kalibrierung_v1':
            out['schritte'][name] = {x: kal(y) for x, y in v.items()}
        elif name in ('szenarien_a4', 'szenarien_v1', 'eigene', 'k06'):
            out['schritte'][name] = {x: szen(y) for x, y in v.items()}
        elif name == 'ebenen':
            out['schritte'][name] = dict(rauschfrei=v['rauschfrei'], verrauscht=dict(
                n=v['verrauscht']['n'], u_c_relativ=v['verrauscht']['u_c_relativ'],
                u_c_innerhalb_5_prozent=v['verrauscht']['u_c_innerhalb_5_prozent'],
                raten={k: dict(Z=rate(x['Z']), H=rate(x['H']), innerhalb_2se=x['innerhalb_2se'])
                       for k, x in v['verrauscht']['raten'].items()}))
        elif name == 's3':
            out['schritte'][name] = {k: {x: y for x, y in r.items() if x != 'punkte'} for k, r in v.items()}
        elif name == 'planung':
            out['schritte'][name] = dict(suche=v['suche'], aufrufe=[{x: y for x, y in a.items() if x != 'quelle'}
                                                                   for a in v['aufrufe']])
        else:
            out['schritte'][name] = v
    return out
