"""Halte, Wiederaufnahme und Bezugsmengen der Simulationen (Auftrag vom 20.10.2026, b2): simulierte Wiederaufnahme mit
W = 3 und T_UA, Mengen G und A, Nachziehen mit Versuchslimit, Rauschbias über A mit mehreren Rauschvarianten.

Die Logik wird mit der Skriptmessung von test_ap13_ablauf und mit kleinen konstruierten Kurzbefunden geprüft, nicht
mit Kampagnenraten."""
import numpy as np
import pytest

from pcmms_auswertung import ablauf, regeln, verfahren as vf
from pcmms_auswertung.harness import kalibrierung, kette, mengen
from test_ap13_ablauf import S3, SW, FesteZiehung, Skript, plan_klein, versuche

NEU = regeln.profil('ENTW-2026-11')
ALT = regeln.profil('ENTW-2026-10')
REGEL = kette.wiederaufnahme_regel(NEU, vf.ZUSTAND, {'nr2': {}})


def _ablauf(regel):
    a = ablauf.Ablauf(plan_klein(tage=((3, 3),)), Skript(regel), SW, S3, FesteZiehung(0),
                      ablauf.Ablaufoptionen(aufwaermen=False), 10.0, 43200.0, kennung=dict(test=True))
    a.ausfuehren()
    return a


def test_wiederaufnahme_regel_nur_im_neuen_stand_mit_ablauf_4():
    assert REGEL == dict(W=3, T_UA_s=1800.0, T_UA_quelle='Entwicklungsbeispiel der Regel (Teil B ohne T_UA)',
                         ereignis=NEU.wert('harness.wiederaufnahme')['ereignis'])
    assert kette.wiederaufnahme_regel(NEU, vf.ZUSTAND, {'nr2': {'T_UA_s': 900.0}})['T_UA_quelle'] == \
        'Teil B (nr2.T_UA_s)'
    assert kette.wiederaufnahme_regel(ALT, vf.ZUSTAND, {'nr2': {}}) is None          # historisch: Halt beendet
    assert kette.wiederaufnahme_regel(NEU, vf.ZUSTAND_HISTORISCH, {'nr2': {}}) is None


def test_halt_wiederaufgenommen_mit_zeitkosten_und_synthetischem_ereignis():
    a = _ablauf(lambda s, v: dict(G6=True) if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and
                v['nummer'] == 0 else None)
    t_halt = a.z['halt']['t']
    w = kette.wiederaufnehmen(a, REGEL)
    assert a.status == 'abgeschlossen' and w['wiederaufnahmen'] == 1 and not w['endgueltig']
    assert w['ursachenanalyse_s'] == 1800.0
    e = a.z['ereignisse'][0]
    assert e['quelle'].startswith('synthetisch') and e['zeitpunkt'] == t_halt + 1800.0
    assert not e['mechanischer_eingriff'] and not e['apparaturfehler']
    k = ablauf.kurz(dict(a.bericht(), harness_wiederaufnahme=w))
    assert k['halte_nach_ursache'] == {'S2': 1} and k['wiederaufnahmen_erfolgreich'] == 1
    assert k['harness_wiederaufnahme']['wiederaufnahmen'] == 1 and k['halt_dauer_s'] == 1800.0
    # zweites S2: endgültig beendet, nicht weiter wiederaufgenommen
    b = _ablauf(lambda s, v: dict(G6=True) if s['konfiguration']['id'] == 'S102' and v['nummer'] == 0 else None)
    w = kette.wiederaufnehmen(b, REGEL)
    assert b.status == 'abgebrochen' and w['endgueltig'] and w['wiederaufnahmen'] == 1
    assert w['grund'].startswith('endgültig: nicht fortsetzbar')


def test_ausgeschoepfte_wiederaufnahmen_beenden_die_kampagne_endgueltig():
    """Im Kontrollsatz jeder Wiederaufnahme reproduziert L₁ eine S3-Überschreitung: nach W = 3 Wiederaufnahmen bleibt
    der Ablauf angehalten, die Kampagne ist endgültig beendet und gehört zu G, nicht zu A."""
    def regel(s, v):
        if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and v['nummer'] == 0:
            return dict(G6=True)
        if str(s['kontrollsatz']).startswith('W') and s['laufart'] == 'L':
            return dict(S3=2.0)
    a = _ablauf(regel)
    w = kette.wiederaufnehmen(a, REGEL)
    assert a.status == 'angehalten' and a.z['wiederaufnahmen'] == 3 and w['wiederaufnahmen'] == 3
    assert w['endgueltig'] and 'W = 3 Wiederaufnahmen ausgeschöpft (Halt S3)' in w['grund']
    k = ablauf.kurz(dict(a.bericht(), harness_wiederaufnahme=w))
    assert k['halte_nach_ursache'] == {'S2': 1, 'S3': 3} and k['wiederaufnahmen_erfolgreich'] == 0
    assert mengen.grund(_befund(ablauf=k)).startswith('nicht abgeschlossen (endgültig: W = 3')
    with pytest.raises(ablauf.AblaufFehler, match='fortsetzen'):
        a.ausfuehren()


# ── Mengen G und A ───────────────────────────────────────────────────────────────────────────────────
def _befund(ablauf=None, yhat1=True, nan=None, h2=True, r0=0.0):
    f = {x: np.full((21, 7), r0 if x.startswith('r') else 1.0) for x in mengen.FELDER_H1}
    f.update({x: np.full((21, 3), 0.0 if x.startswith('r') else 1.0) for x in mengen.FELDER_H1Z})
    if nan:
        f[nan] = f[nan].copy()
        f[nan][3, 0] = np.nan
    return dict(ablauf=ablauf, yhat1_gueltig=yhat1, felder=f, H2=dict(intervalle={'perzentil_0.95': ((0, 1), (0, 1))}
                                                                       if h2 else {}))


def test_mengen_g_und_a_mit_gruenden():
    fertig = dict(status='abgeschlossen', harness_wiederaufnahme=dict(wiederaufnahmen=1, grund=None))
    spaet = dict(status='angehalten', harness_wiederaufnahme=dict(grund='endgültig: W = 3 Wiederaufnahmen ausgeschöpft '
                                                                        '(Halt S1)'))
    bf = [_befund(), _befund(ablauf=fertig), _befund(ablauf=spaet), _befund(yhat1=False), _befund(nan='v1'),
          _befund(nan='rz0'), _befund(h2=False), _befund(ablauf=dict(status='abgebrochen'))]
    m = mengen.aufteilen(bf)
    assert m['G'] == 8 and m['A'] == 2 and m['indizes_A'] == [0, 1]       # nach Wiederaufnahme abgeschlossen: in A
    assert m['ausschluesse'] == {'nicht abgeschlossen': 2, 'ŷ¹ ungültig': 1, 'H1-Prüfgrößen nicht endlich': 1,
                                 'H1Z-Prüfgrößen nicht endlich': 1, 'H2-Intervalle fehlen': 1}
    assert 'nicht abgeschlossen (endgültig: W = 3 Wiederaufnahmen ausgeschöpft (Halt S1))' in m['ausschluesse_genau']


def test_rauschbias_ueber_a_mit_mehreren_rauschvarianten():
    """b̂ über A je Variante, Mitte der Spannweite, u(b̂) mit der halben Spannweite; eine nicht abgeschlossene Kampagne
    mit großem Rohresiduum geht nicht ein."""
    v1 = [_befund(r0=0.01), _befund(r0=0.03), _befund(r0=5.0, ablauf=dict(status='angehalten'))]
    v2 = [_befund(r0=0.05), _befund(r0=0.07)]
    laeufe = [dict(befunde=mengen.in_A(v)) for v in (v1, v2)]
    rb = kalibrierung.rauschbias(laeufe, 'r0')
    assert rb['n_varianten'] == 2 and np.allclose(rb['bias'], 0.04) and np.allclose(rb['halbe_spannweite'], 0.02)
    assert np.all(rb['u'] > 0.02 / np.sqrt(3))
    assert rb['je_variante'][0]['n'][0] == 2


def test_nachziehen_bis_soll_und_versuchslimit():
    folge = []

    def laufe(start, n, ausfall=0.25):
        folge.append((start, n))
        return [_befund(yhat1=((start + i) % 4 != 3)) for i in range(n)]   # jede vierte Kampagne ŷ¹ ungültig
    r = mengen.nachziehen(laufe, 6, 1.5)
    assert r['status'] == 'abgeschlossen' and r['A'] >= 6 and r['G'] == 8 and folge == [(0, 6), (6, 2)]
    folge.clear()
    r = mengen.nachziehen(lambda s, n: [_befund(yhat1=False) for _ in range(n)], 4, 1.5)
    assert r['status'] == 'nicht abgeschlossen' and r['G'] == r['limit'] == 6 and r['A'] == 0
    assert 'Versuchslimit 6' in r['grund']
    with pytest.raises(ValueError):
        mengen.nachziehen(laufe, 0, 1.5)


def test_nachziehen_nur_im_neuen_stand():
    with pytest.raises(ValueError, match='harness.nachziehen'):
        kalibrierung.kalibrieren('N01-A4', 'L1', ALT, 2, 2, 1, soll_A=4)


# ── Reserve, Zeit, Zielfunktion ──────────────────────────────────────────────────────────────────────
from pcmms_auswertung.harness import reserve  # noqa: E402


def _kampagne(je, status='abgeschlossen', endgueltig=False, zusatz=None, wa=0):
    zl = dict(bezugslauf=0, wiederaufnahme_kontrolle=0, aufwaermen_nach_halt=0)
    zl.update(zusatz or {})
    return dict(ablauf=dict(status=status, gueltig_je_schnittpunkt=je, zusatzlaeufe=zl,
                            laufzahl=dict(geplant_ausgefuehrt=100, zusaetzlich=sum(zl.values()) + 3),
                            harness_wiederaufnahme=dict(endgueltig=endgueltig, wiederaufnahmen=wa,
                                                        ursachenanalyse_s=1800.0 * wa)))


def test_reservebedingung_mit_bedingtem_nenner():
    regel = NEU.wert('planung.reserve_ziel')
    voll, knapp = {'S100': 5, 'S102': 5}, {'S100': 5, 'S102': 4}
    bf = [_kampagne(voll)] * 19 + [_kampagne(knapp)] + [_kampagne(knapp, status='angehalten', endgueltig=True)] * 3
    b = reserve.bedingung(bf, 5, regel)
    assert (b['zaehler'], b['nenner'], b['endgueltig_beendet'], b['G']) == (19, 20, 3, 23)
    assert b['rate'] == pytest.approx(0.95) and b['erfuellt']    # endgültig beendete nicht im bedingten Nenner
    b = reserve.bedingung(bf[1:], 5, regel)
    assert not b['erfuellt'] and (b['zaehler'], b['nenner']) == (18, 19)
    with pytest.raises(ValueError, match='Nenner'):
        reserve.bedingung(bf, 5, dict(regel, nenner='alle'))


def test_zeitbilanz_nach_termen_und_zielfunktion():
    bf = [_kampagne({}, zusatz=dict(bezugslauf=1, wiederaufnahme_kontrolle=7), wa=1), _kampagne({})]
    z = reserve.zeitbilanz(bf, 10.0, NEU.wert('planung.zeitformel'), formel_s=2000.0)
    t = z['terme']
    assert t['Läufe']['mittel_s'] == 1000.0 and t['Bezugseröffnung']['summe_s'] == 10.0
    assert t['Kontrollsatz der Wiederaufnahme']['summe_s'] == 70.0 and t['Wiederholungen']['summe_s'] == 60.0
    assert t['Ursachenanalyse T_UA']['mittel_s'] == 900.0 and z['nenner'] == 2 and z['formel_s'] == 2000.0
    assert z['gesamt']['wert'] == pytest.approx((1000 + 30 + 70 + 10 + 1800) / 2 + 1030 / 2)
    with pytest.raises(ValueError, match='Terme'):
        reserve.zeitbilanz(bf, 10.0, ['Läufe'])
    assert reserve.kandidaten_ordnen([3, 2], [20, 30])[0] == (2, 20)
    with pytest.raises(ValueError, match='nicht umgesetzt'):
        reserve.kandidaten_ordnen([3], [20], fassung='b')
