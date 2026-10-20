"""Planungssimulation (Präreg §5.4, A9.2; Plan AP-13 1.2 „geplant“) als Haken `planung` des Pilotskripts.

Für jeden Kandidaten (n_min, n₀) in der Reihenfolge der Zielfunktion (Regel planung.zielfunktion, Fassung (a):
N_K·n_min + 3·n₀) läuft die Kalibrier- und Prüfsimulation von harness.kalibrierung bei dieser Laufzahl
(n = n_min + r Blöcke mit r = ⌈n_min·p̂/(1 − p̂)⌉ + 2): Rauschbias, c, Intervalltyp von H2 und daraus
P(H1 und H2 bestätigt | exakt). Der erste Kandidat mit P ≥ 0,8 (Regel planung.bedingung, Punktschätzer) legt n_min
und n₀ fest. Streuungen an der oberen 80-%-Grenze: Das Rauschmodell des Szenarios wird mit
κ = s_q,oben80/s_q (gleicher Faktor für alle q bei gleichem ν_p) skaliert.

Der simulierte Plan ist der des Kandidaten: N_z (Plan.n_zyklen, T_a = N_z/f), T_Lauf = T_park + T_ramp + T_e + T_a +
T_ab und d Messtage aus dem Aufruf des Pilotskripts, n = n_min + r Blöcke und n₀; Frequenz, N_K und N_I müssen zum
Szenario bzw. zum Grundplan passen, sonst bricht der Haken ab (keine widersprechenden Vorgabewerte). Jeder Kandidat
nennt den tatsächlich simulierten Plan (plan_simuliert).

Grenzen dieser Stufe: Die zusätzliche Power-Bedingung (Regel planung.power) ist offen und nicht geprüft. Mit weniger
als 1000 Kampagnen je Simulation ist das Ergebnis Entwicklungsdiagnostik; die Planung trägt dann diese Kennzeichnung.

Rauschmodellquelle (Teil d2, Regel harness.planung_rauschen): Im historischen Regelstand 2026-10 rechnet der Haken wie
bisher mit dem Rauschmodell des Szenarios, skaliert mit einem gemeinsamen Faktor κ(ν_p). Im Regelstand 2026-11
(Wert „phase0_modell“) baut er das Modell nur aus dem Aufruf des Pilotskripts (Phase-0-Tabelle, Gültigkeit,
Kalibrierung, Laufgrößen des Satzes): Struktur aus P0.8, Strukturmodell mit oberen 80-%-Grenzen je identifizierbarer
Komponente und einem gemeinsamen Faktor für den Boden von ⟨N⟩ aller Laufarten (Regel planung.obere_grenze,
marginale Grenzen, keine gemeinsame 80-%-Garantie), Prüfsimulation mit c_B (Regel planung.teil_b_werte). Eine
Szenario-ID ist dann nicht nötig und geht nicht in das Modell ein; das Szenariomodell bleibt als unabhängige Referenz
nur ausdrücklich wählbar (rauschquelle='szenario_orakel'). teil_b_werte rechnet nach der Planung die Werte für Teil B
mit Punktschätzern (Strukturmodell als Standard, Familienanpassung für die Spannweite von b̂, c nach
h1.c_rauschmodelle) und die benannten Sensitivitäten.
"""
import math

import numpy as np
from scipy import stats

from .. import laufgroessen as lgm, regeln as rg, verfahren as vf, zufall
from ..generator import kampagne as kp, phase0_modell as p0m, szenarien
from . import kalibrierung

RAUSCHQUELLEN = ('szenario', 'phase0_modell', 'szenario_orakel')


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


def fenster_aus_aufruf(e, f_szenario, plan_basis):
    """Fensterlänge, Laufdauer und Messtage des Kandidaten aus dem Aufruf des Pilotskripts (A9.2), geprüft gegen
    Szenario und Grundplan. Rückgabe dict(N_z, T_a_s, T_e_s, T_lauf_s, f_hz) und die Zahl d der Messtage."""
    f = float(e['f'])
    if abs(f - f_szenario) > 1e-9 * f_szenario:
        raise ValueError(f'Planungshaken: f = {f:g} Hz des Pilotskripts ≠ f = {f_szenario:g} Hz des Szenarios')
    N_z = int(e['N_z'])
    T_a = N_z / f
    if e.get('T_a') is not None and abs(float(e['T_a']) - T_a) > 1e-9 * T_a:
        raise ValueError(f'Planungshaken: T_a = {e["T_a"]} s ≠ N_z/f = {T_a} s')
    zeit = e.get('zeit') or {}
    if e.get('T_lauf') is None or e.get('T_e') is None or zeit.get('d') is None:
        raise ValueError('Planungshaken: T_Lauf, T_e und die Zeitangaben (d, N_K, N_I) des Pilotskripts fehlen; ohne '
                         'sie simulierte der Haken einen anderen Plan als den Kandidaten')
    konf = kp.schnitt_konfigurationen(plan_basis)
    N_K = sum(k['konfiguration']['gruppe'] in ('schnitt', 'zusatz') for k in konf)
    N_I = sum(k['konfiguration']['gruppe'] == 'identifizierbarkeit' for k in konf)
    if (zeit.get('N_K') is not None and int(zeit['N_K']) != N_K) or int(zeit.get('N_I', 0)) != N_I:
        raise ValueError(f'Planungshaken: N_K = {zeit.get("N_K")}, N_I = {zeit.get("N_I", 0)} der Zeitangaben ≠ '
                         f'{N_K}, {N_I} Konfigurationen des Grundplans')
    return dict(N_z=N_z, T_a_s=T_a, T_e_s=float(e['T_e']), T_lauf_s=float(e['T_lauf']), f_hz=f), int(zeit['d'])


def rauschquelle_regel(profil, rauschquelle=None):
    """Rauschmodellquelle des Hakens: ausdrücklich ('szenario_orakel' im Regelstand 2026-11, sonst wie die Regel) oder
    aus der Regel harness.planung_rauschen ('szenario' historisch, 'phase0_modell' im Regelstand 2026-11). Ein anderer
    Wert ist ein Fehler, kein stiller Ersatzweg."""
    if rg.ist_historisch(profil):
        if rauschquelle not in (None, 'szenario'):
            raise ValueError(f'Planungshaken: Rauschquelle {rauschquelle!r} im historischen Regelstand nicht '
                             'vorgesehen')
        return 'szenario'
    regel = profil.wert('harness.planung_rauschen')
    if regel != 'phase0_modell':
        raise ValueError(f'Regel harness.planung_rauschen = {regel!r} nicht umgesetzt (phase0_modell)')
    q = regel if rauschquelle is None else rauschquelle
    if q not in ('phase0_modell', 'szenario_orakel'):
        raise ValueError(f'Planungshaken: Rauschquelle {q!r} unbekannt (phase0_modell, szenario_orakel)')
    if q == 'phase0_modell':
        if profil.wert('planung.obere_grenze') != 'je_komponente_gemeinsamer_boden':
            raise ValueError(f'Regel planung.obere_grenze = {profil.wert("planung.obere_grenze")!r} nicht umgesetzt')
        rm = profil.wert('rauschmodelle')
        if rm.get('standard') != 'strukturmodell_phase0':
            raise ValueError(f'Regel rauschmodelle: Standard {rm.get("standard")!r} nicht umgesetzt')
    return q


def c_planung(profil):
    """Prüfsimulation der Planung mit c_B (Regel planung.teil_b_werte = 'punktschaetzer'; historisch: kalibriertes c
    wie bisher)."""
    if rg.ist_historisch(profil):
        return False
    w = profil.wert('planung.teil_b_werte')
    if w != 'punktschaetzer':
        raise ValueError(f'Regel planung.teil_b_werte = {w!r} nicht umgesetzt (punktschaetzer)')
    return True


def laufgroessen_aus_aufruf(e):
    """Laufgrößen des Satzes aus dem Aufruf des Pilotskripts; fehlen sie, aus Tabelle, Gültigkeit und k des Aufrufs."""
    lg = e.get('laufgroessen')
    if lg is None:
        lg = lgm.schaetzen(e['tabelle'], e['gueltig'], e['k'])
    b = lg['bindung']
    if b['k'] != e['k'] or b['N_z'] != e['N_z']:
        raise ValueError(f'Planungshaken: Laufgrößen bei (k = {b["k"]}, N_z = {b["N_z"]}) passen nicht zum Aufruf '
                         f'(k = {e["k"]}, N_z = {e["N_z"]})')
    return lg


def quelle_aus_aufruf(e, grenze='oben80', modell='struktur', profil=None):
    """Modellquelle der Planung nur aus dem Aufruf des Pilotskripts (Phase-0-Tabelle, Gültigkeit, Kalibrierung,
    Laufgrößen; keine Szenario-ID, keine Wahrheit) mit der Herkunft des Satzes; mit profil gebunden an die Regel
    p0.strukturmodell."""
    if profil is not None:
        p0m.regeln_pruefen(profil)
    lg = laufgroessen_aus_aufruf(e)
    t = e['tabelle']
    q = p0m.quelle_aus_phase0(t, e['gueltig'], e['kal'], lg, grenze, k_max=e['k'], modell=modell)
    q.herkunft['satz_bindung'] = e.get('bindung')
    return q, lg


def obere_grenzen_bericht(lg, q):
    """Grenzen je Komponente (marginal) für die Ausgabe des Hakens."""
    kp_ = lg['komponenten']
    return dict(regel='je_komponente_gemeinsamer_boden',
                lesart='marginale obere 80-%-Grenzen je identifizierbarer Komponente mit eigenem ν; ein gemeinsamer '
                       'Faktor für den Boden von ⟨N⟩ aller Laufarten; keine gemeinsame 80-%-Garantie',
                sigma_a=dict(wert=kp_['sigma_a'], oben80=kp_['sigma_a_oben80'], nu=kp_['sigma_a_nu']),
                sigma_delta_grad=dict(wert=kp_['sigma_delta_grad'], oben80=kp_['sigma_delta_grad_oben80'],
                                      nu=kp_['sigma_delta_grad_nu']),
                sigma_off_grad=dict(wert=kp_['sigma_off_grad'], oben80=kp_['sigma_off_grad_oben80'],
                                    nu=kp_['sigma_off_grad_nu']),
                boden_mittel=dict(faktor=dict(q.rausch.herkunft).get('faktor_boden_mittel'), nu=kp_['sigma_mittel_nu']),
                nicht_identifizierbar=list(dict(q.rausch.herkunft).get('nicht_identifizierbar', ())),
                modellquelle=q.kennung()['sha256'])


def haken_phase0(profil, n_kal, n_pruef, seed_basis, n_kandidaten, n0_kandidaten=(20,), plan_basis=None, prozesse=1,
                 protokoll=None, max_aufrufe=None, verfahren=None):
    """Planungshaken mit dem Phase-0-Modell ohne Szenario-ID (Regelstand 2026-11)."""
    return haken(None, None, profil, n_kal, n_pruef, seed_basis, n_kandidaten, n0_kandidaten, plan_basis, prozesse,
                 protokoll, max_aufrufe, verfahren, rauschquelle='phase0_modell')


def haken(sid, stufe, profil, n_kal, n_pruef, seed_basis, n_kandidaten, n0_kandidaten=(20,), plan_basis=None,
          prozesse=1, protokoll=None, max_aufrufe=None, verfahren=None, rauschquelle=None):
    """Haken für pilot.pilot_auswerten(planung=…). protokoll: Liste, in die jeder Aufruf seine Kandidaten schreibt.
    max_aufrufe: Entwicklungsgrenze der Simulationen (weitere Paare (k, T_a) ohne Planung, gekennzeichnet).
    verfahren: Verfahren der simulierten Kampagnen (Vorgabe verfahren.STANDARD); jede simulierte Kampagne bindet ihre
    Phase-0-Größen an das k des Aufrufs. rauschquelle: siehe rauschquelle_regel; mit 'phase0_modell' sind sid und
    stufe nur Kennzeichnung (dürfen None sein)."""
    verfahren = vf.oder_standard(verfahren)
    zaehler = [0]
    plan_basis = kp.Plan() if plan_basis is None else plan_basis
    quelle_art = rauschquelle_regel(profil, rauschquelle)
    phase0 = quelle_art == 'phase0_modell'
    mit_cB = c_planung(profil)
    sz = None if phase0 else szenarien.KATALOG[sid]
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
        kw_kal, grenzen = {}, None
        if phase0:                                          # Strukturmodell aus Phase 0, Grenzen je Komponente
            q, lg = quelle_aus_aufruf(e, 'oben80', profil=profil)
            kappa = None
            fenster, tage = fenster_aus_aufruf(e, q.struktur.f, plan_basis)
            rausch = q.rausch
            grenzen = obere_grenzen_bericht(lg, q)
            kw_kal = dict(quelle=q)
        else:
            kappa = obere80_faktor(s['nu_p'])               # = s_q,oben80/s_q für jede Größe (pilot.obere_grenze)
            m0 = szenarien.modell(sz, stufe)
            fenster, tage = fenster_aus_aufruf(e, m0.system.f, plan_basis)
            rausch = skaliert(m0.rausch, kappa)
        if mit_cB:
            kw_kal['c_planung'] = True
        p = float(e['p_hat'])
        schritte = []
        for n, n0 in kandidaten_ordnen(n_kandidaten, [x for x in n0_kandidaten if x >= n0_min]):
            r = math.ceil(n * p / (1 - p)) + reserve if p < 1 else None
            if r is None or (e.get('n_max') is not None and n + r > e['n_max']):
                schritte.append(dict(n_min=n, n0=n0, reserve_r=r, uebersprungen='n = n_min + r > n_max'))
                continue
            plan = plan_basis.mit(n_bloecke=n + r, n0=n0, n_zyklen=fenster['N_z'], T_lauf=fenster['T_lauf_s'],
                                  tage=tage)
            k = kalibrierung.kalibrieren(sid, stufe, profil, n_kal, n_pruef, zufall.unterseed(seed_basis, 'planung', n,
                                                                                             n0, e['k'], e['N_z']),
                                         plan=plan, n_min=n, prozesse=prozesse, rauschvarianten=[rausch],
                                         k_max=e['k'], verfahren=verfahren, **kw_kal)
            g = k['gemeinsame_bestaetigung']
            gr = [x['konfiguration']['gruppe'] for x in kp.schnitt_konfigurationen(plan)]
            N_KI = sum(x in ('schnitt', 'zusatz') for x in gr) + sum(x == 'identifizierbarkeit' for x in gr)
            zeit_formel = ((N_KI + 8) * plan.n_bloecke + 18 * tage) * plan.T_lauf / (1 - p) if p < 1 else None
            schritte.append(dict(n_min=n, n0=n0, reserve_r=r,
                                 plan_simuliert=dict(n_bloecke=plan.n_bloecke, n0=plan.n0, n_pilot=plan.n_pilot,
                                                     tage=plan.tage, n_zyklen=plan.n_zyklen,
                                                     T_a_s=plan.n_zyklen / fenster['f_hz'], T_lauf_s=plan.T_lauf),
                                 P_gemeinsam=g['rate'], mc_se=g['mc_se'],
                                 zaehler=g['zaehler'], nenner=g['nenner'], c_H1=k['c_H1']['wert'],
                                 intervalltyp_H2=k['h2'].get('schluessel'), pruefrate_c=None if k['pruefung'] is None
                                 else k['pruefung']['rate'], erfuellt=bool(g['rate'] is not None and
                                                                           g['rate'] >= bedingung),
                                 messzeit=dict(formel_s=zeit_formel, ablauf=(k.get('raten_pruefung') or {}).get('ablauf'),
                                               hinweis='Formel §5.3 (c) unverändert (offen, §12); „ablauf“ nur beim '
                                                       'Verfahren „zustand“: realisierte Laufzahl × T_Lauf')))
            if schritte[-1]['erfuellt']:
                break
        red = n_kal < rg.NORMATIVE_ZAHLEN['kampagnen_kalibrierung'] or n_pruef < rg.NORMATIVE_ZAHLEN[
            'kampagnen_pruefung'] or profil.reduziert
        if phase0:
            quelle = (f'AP-13-Planungssimulation (Phase-0-Modell: Struktur aus P0.8, Strukturmodell an den oberen '
                      f'80-%-Grenzen je Komponente, c_B; {n_kal}+{n_pruef} Kampagnen je Kandidat, Profil {profil.id})'
                      + (' – Entwicklungsdiagnostik, keine Planung für Teil B' if red else ''))
        else:
            quelle = (f'AP-13-Planungssimulation (Szenario {sid}, {stufe}, κ = {kappa:.4f}, {n_kal}+{n_pruef} '
                      f'Kampagnen je Kandidat, Profil {profil.id})'
                      + (' – Entwicklungsdiagnostik, keine Planung für Teil B' if red else ''))
            if quelle_art == 'szenario_orakel':
                quelle = 'Szenario-Orakel (Referenz, nicht Planung nach harness.planung_rauschen): ' + quelle
        treffer = [x for x in schritte if x.get('erfuellt')]
        out = dict(n_min=treffer[0]['n_min'] if treffer else None, n0=treffer[0]['n0'] if treffer else None,
                   kappa=kappa, bedingung=bedingung, kandidaten=schritte, quelle=quelle, reduziert=bool(red),
                   fenster=fenster, power_bedingung='offen (Regel planung.power), nicht geprüft',
                   verfahren=verfahren.kennung())
        if not rg.ist_historisch(profil):
            out.update(rauschquelle=quelle_art, c_planung='c_B' if mit_cB else 'kalibriert')
            if grenzen is not None:
                out['obere_grenzen'] = grenzen
                out['szenario_kennzeichnung'] = sid
        if not treffer:
            out['grund'] = 'kein Kandidat erreicht P(H1 und H2 bestätigt | exakt) ≥ 0,8'
        if protokoll is not None:
            protokoll.append(dict(k=e['k'], N_z=e['N_z'], **out))
        return out
    return planung


def teil_b_werte(e, profil, n_kal, n_pruef, seed_basis, plan, n_min, prozesse=1, sensitivitaeten=(), verfahren=None):
    """Werte für Teil B nach der Planung (Regel planung.teil_b_werte = 'punktschaetzer'): Kalibrier- und
    Prüfsimulation bei den geplanten Laufzahlen mit Punktschätzern. Rauschmodelle nach der Regel rauschmodelle:
    Standard (Strukturmodell) und eingebettete Familienanpassung; b̂ aus der Mitte, u(b̂) mit der halben Spannweite
    über beide (h1.bias_u, Rechteck); c nach h1.c_rauschmodelle (Fassung a: Quantil des Standardmodells, die
    Familienanpassung als Sensitivität). Benannte Sensitivitäten (generator.phase0_modell.SENSITIVITAETEN) werden mit
    denselben Seeds getrennt gerechnet und nur berichtet. e: Aufruf des Pilotskripts beim festgelegten Paar bzw. ein
    dict mit tabelle, gueltig, kal, k, N_z und laufgroessen. Ein Residuen-Bootstrap (rauschmodelle: bootstrap
    'optional') ist nicht umgesetzt und wird nicht gerechnet."""
    if not c_planung(profil):
        raise ValueError('Teil-B-Werte aus Punktschätzern nur im Regelstand 2026-11 (Regel planung.teil_b_werte)')
    rm = profil.wert('rauschmodelle')
    soll = dict(standard='strukturmodell_phase0', eingebettet='familienanpassung', sensitivitaet='benannte_szenarien')
    if any(rm.get(x) != v for x, v in soll.items()) or rm.get('bootstrap') not in ('optional', None):
        raise ValueError(f'Regel rauschmodelle = {rm!r} nicht umgesetzt ({soll}, bootstrap optional)')
    q, lg = quelle_aus_aufruf(e, 'punkt', profil=profil)
    p0m.regeln_pruefen(profil, sensitivitaeten=bool(sensitivitaeten))
    fam = p0m.familienanpassung(lg, 'punkt')
    k = kalibrierung.kalibrieren(None, None, profil, n_kal, n_pruef, seed_basis, plan=plan, n_min=n_min,
                                 prozesse=prozesse, rauschvarianten=[q.rausch, fam], k_max=e['k'], verfahren=verfahren,
                                 quelle=q)
    w8 = dict(k['werkzeug8'], modellquelle=q.name, rauschmodelle=[q.rausch.name, fam.name],
              teil_b_werte='punktschaetzer', modellquelle_sha256=q.kennung()['sha256'])
    sens = {}
    for name in sensitivitaeten:
        st, eff = p0m.sensitivitaet(q.rausch, name, plan=plan, f=q.struktur.f)
        ks = kalibrierung.kalibrieren(None, None, profil, n_kal, n_pruef, seed_basis, plan=plan, n_min=n_min,
                                      prozesse=prozesse, rauschvarianten=[st], k_max=e['k'], verfahren=verfahren,
                                      quelle=q.mit(rausch=st, effekte=tuple(q.effekte) + tuple(eff)))
        sens[name] = dict(beschreibung=p0m.SENSITIVITAETEN[name]['beschreibung'], c_H1=ks['c_H1']['wert'],
                          bias0=ks['rauschbias']['b0'], gemeinsam=ks['gemeinsame_bestaetigung'],
                          pruefung=ks['pruefung'], h2=ks['h2'].get('schluessel'))
    return dict(werkzeug8=w8, c_varianten=k.get('c_varianten'), gemeinsam=k['gemeinsame_bestaetigung'],
                rauschbias=k['rauschbias'], h2=k['h2'], sensitivitaeten=sens,
                sensitivitaeten_version=p0m.SENSITIVITAETEN_VERSION, meta=k['meta'],
                herkunft=dict(modellquelle=q.kennung(), lesart='Punktschätzer nach der Planung; Sensitivitäten nur '
                                                               'berichtet'))
