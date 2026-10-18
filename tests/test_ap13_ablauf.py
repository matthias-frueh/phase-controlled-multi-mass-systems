"""Zustandsbehafteter Ablauf der Phase 1 (Auftrag vom 17.10.2026, Teil B/C): Wiederholungen nach §6/A9.12, G1/S1,
Kontrollläufe, S2–S4, Halt und Wiederaufnahme, Zeitfortschreibung, Datenübergabe an Stufe 2 und Checkpoint.

Die Logik wird mit einer steuerbaren Skriptmessung geprüft (alle Läufe gültig, ausgewählte Versuche mit gezielten
Verstößen), nicht mit Monte-Carlo-Raten; dazu Gegenproben auf Ebene H mit dem Generator."""
import ast
import copy
import os

import numpy as np
import pytest

from pcmms_auswertung import ablauf, auswertung, formate, gueltigkeit, konventionen as kv, regeln, verfahren as vf
from pcmms_auswertung import zusammenfassung as zf
from pcmms_auswertung.generator import kampagne as kp, rauschen, szenarien
from pcmms_auswertung.harness import kette

K = 3
C0 = np.array([1.0 + 0.5j, 0.4 - 0.2j, 0.1 + 0.05j])                 # Summenharmonische der Skriptläufe
SW = gueltigkeit.Schwellen(f_soll=10.0, kmax=3, sigma_tol_grad={2: 1.0, 3: 1.0},
                           sigma_delta={**{g: dict(N=0.01, F=0.01) for g in ('K', 'L1', 'L2', 'L3')},
                                        'R': dict(N=0.01, F=None)},
                           F_LO_zellen=np.full(3, 0.1), delta_delta_grad=np.zeros(3), eps_ctrl=0.01,
                           sigma_ref=0.001, sigma_ref_zellen=[0.001] * 3)
S3 = {'1': dict(mu=kv.h1_vektor(C0[None, :3])[0], schwelle=np.full(7, 0.5), n0=20)}


# ── Skriptplan und Skriptmessung ──────────────────────────────────────────────────────────────────────
def plan_klein(tage=((3,),), kontroll=('R', 'L1'), mitte=12, T=10.0, t0=1000.0, pause=500.0):
    """Phase-1-Laufplan wie kampagne.laufplan, aber mit wenigen Konfigurationen je Block und fester Reihenfolge:
    je Tag Aufwärm-R, Kontrollsatz vor dem ersten Block, Konfigurationen S100, S102, … (R nach der `mitte`-ten),
    Kontrollsatz am Blockende (mit dem Folgeblock geteilt), Schlussreferenzlauf."""
    laeufe = []

    def neu(spec, block, tag, ks=None):
        pos = 1000 + len(laeufe)
        d = dict(spec, phase=1, block=block, messtag=tag, kontrollsatz=ks, position=pos)
        d['lauf_id'] = f'1-{pos:05d}-{d["konfiguration"]["id"]}'
        laeufe.append(d)

    def mitglied(m):
        if m == 'R':
            return kp._konf('R', 'referenz')
        return kp._konf('L', 'einzel', modul=int(m[1]), einstellung=2 if m.endswith('′') else 1)
    ks = b = 0
    for tag, bloecke in enumerate(tage, start=1):
        neu(kp._konf('R', 'referenz'), None, tag)
        for i, nk in enumerate(bloecke):
            b += 1
            if i == 0:
                ks += 1
                for m in kontroll:
                    neu(mitglied(m), b, tag, ks)
            for c in range(nk):
                neu(kp._konf('K', 'schnitt', (0.0, 100.0 + 2 * c, 240.0)), b, tag)
                if c + 1 == mitte:
                    neu(kp._konf('R', 'referenz'), b, tag)
            ks += 1
            for m in kontroll:
                neu(mitglied(m), b, tag, ks)
        neu(kp._konf('R', 'referenz'), None, tag)
    t, tag_alt = t0, 1
    for l in laeufe:
        if l['messtag'] != tag_alt:
            t += pause
            tag_alt = l['messtag']
        l['t_start'], l['t_ende'] = t, t + T
        t += T
    return laeufe


class Skript:
    """Messung mit gültigen, rauschfreien Zusammenfassungen; regel(spec, versuch) → dict gezielter Änderungen:
    stoerung (G8), G5, G6 (Liftoff), G2 (Indexfehler), dN (⟨N⟩ und Zellen), dN_summe (nur Summe), S3 (Re N₁)."""

    def __init__(self, regel=None):
        self.regel = regel or (lambda s, v: {})
        self.aufrufe = []

    def messen(self, spec, versuch):
        self.aufrufe.append((dict(spec), dict(versuch)))
        d = zf.leere_daten(K, 1)
        d['N_mittel'][:] = 10.0
        d['N_mittel_zellen'][:] = 10.0 / 3
        d['fuenftel_N_mittel'][:] = 10.0
        d['Nk_summe'][0] = C0
        d['Nk_zellen'][0] = C0[None, :] / 3
        d['fuenftel_Nk'][0] = C0[None, :]
        d['sigma_grad'][:] = 0.0
        d['min_roh_zellen'][:] = 5.0
        d['max_roh_zellen'][:] = 15.0
        k = dict(lauf_id=spec['lauf_id'], laufart=spec['laufart'], modul=spec['modul'], einstellung=spec['einstellung'],
                 konfiguration=spec['konfiguration'], phase=1, block=spec['block'], messtag=spec['messtag'],
                 position=spec['position'], kontrollsatz=spec['kontrollsatz'], t_start=spec['t_start'],
                 t_ende=spec['t_ende'], f_soll=10.0, f_mittel=10.0, n_zyklen=100, n_fuenftel=20, k_voll=K,
                 n_theta=kv.N_THETA, stoerung=False, aufzeichnung_ok=True,
                 park_ok=None if spec['laufart'] == 'K' else True, fehlende_kanaele=[], hash_rohdatei=None,
                 version_stufe1='skript', kalibrier_hash=None, ebene='H')
        c = self.regel(spec, versuch) or {}
        if c.get('stoerung'):
            k['stoerung'] = True
        if c.get('G5'):
            d['uebersteuert_zellen'][0, 0] = True
        if c.get('G6'):
            d['min_roh_zellen'][0, 1] = 0.0
        if c.get('G2'):
            d['index_fehler'][0, 1] = 1
        if c.get('dN'):
            d['N_mittel'][0] += c['dN']
            d['N_mittel_zellen'][0] += c['dN'] / 3
            d['fuenftel_N_mittel'][0] += c['dN']
        if c.get('dN_summe'):
            d['N_mittel'][0] += c['dN_summe']
            d['fuenftel_N_mittel'][0] += c['dN_summe']
        if c.get('S3'):
            d['Nk_summe'][0, 0] += c['S3']
        return k, d


def lauf(regel=None, plan=None, optionen=ablauf.Ablaufoptionen(aufwaermen=False), s3=None, rng=None, sw=SW):
    geplant = plan if plan is not None else plan_klein()
    a = ablauf.Ablauf(geplant, Skript(regel), sw, S3 if s3 is None else s3, rng or np.random.default_rng(1), optionen,
                      10.0, 500.0, kennung=dict(test=True))
    a.ausfuehren()
    return a


def versuche(a):
    return [v['kopf']['versuch'] for v in a.z['versuche']]


def nach_id(a, kid, block=None):
    return [v for v in versuche(a) if v['konfiguration'] == kid and (block is None or v['block'] == block)]


class FesteZiehung:
    """Reihenfolgegenerator für Logiktests: integers(lo, hi) liefert den vorgegebenen Platz und protokolliert hi."""

    def __init__(self, j):
        self.j, self.aufrufe = j, []

    def integers(self, lo, hi):
        self.aufrufe.append((lo, hi))
        return min(self.j, hi - 1)

    def permutation(self, n):
        return np.arange(n)


# ── Grundfälle ────────────────────────────────────────────────────────────────────────────────────────
def test_kein_fehler_urspruenglicher_plan_ohne_zusaetzliche_versuche():
    plan = plan_klein(tage=((3, 2), (2,)))
    a = lauf(plan=plan)
    vs = versuche(a)
    assert a.status == 'abgeschlossen' and len(vs) == len(plan) and all(v['geplant'] for v in vs)
    assert [v['bezug'] for v in vs] == [l['lauf_id'] for l in plan]
    assert [v['t_start'] for v in vs] == [l['t_start'] for l in plan]          # Zeiten wie geplant
    b = a.bericht()
    assert b['laufzahl']['zusaetzlich'] == 0 and set(b['auswahl_zaehler']) == {'gueltig'}
    assert not b['ziehungen'] and not b['grenzen'] and not b['luecken']


def test_regulaerer_ersatz_zweite_wiederholung_und_grenze():
    def regel(spec, v):
        k, n = spec['konfiguration']['id'], v['nummer']
        if spec['block'] == 1 and (k == 'S100' and n == 0 or k == 'S102' and n < 2 or k == 'S104'):
            return dict(stoerung=True)
    a = lauf(regel)
    b = a.bericht()['auswahl']
    assert b['S100|1']['status'] == 'ersetzt' and len(b['S100|1']['versuche']) == 2
    assert b['S102|1']['status'] == 'ersetzt' and len(b['S102|1']['versuche']) == 3      # zweite Wiederholung
    assert b['S104|1']['status'] == 'fehlt: Grenze ausgeschöpft' and len(b['S104|1']['versuche']) == 3
    assert [x['nummer'] for x in nach_id(a, 'S102', 1)] == [0, 1, 2]
    assert nach_id(a, 'S104', 1)[-1].get('grenze') and a.z['wdh']['S104|1'] == 2
    assert all(x['rolle'] == 'wiederholung' for x in nach_id(a, 'S102', 1)[1:])
    # Wiederholungen bleiben im Block, vor dem Schlusskontrollsatz; die geplante Reihenfolge der übrigen Läufe bleibt
    vs = versuche(a)
    schluss = next(i for i, v in enumerate(vs) if v['kontrollsatz'] == 2)
    assert all(vs.index(x) < schluss for x in nach_id(a, 'S102', 1) + nach_id(a, 'S104', 1))
    plan_ids = [l['lauf_id'] for l in plan_klein()]
    assert [v['bezug'] for v in vs if v['geplant']] == plan_ids


def test_zu_spaet_erkannte_ungueltigkeit_bleibt_ohne_wiederholung():
    """G1 einer Konfiguration nach der Blockmitte steht erst mit dem R des Schlusskontrollsatzes fest: keine
    Wiederholung, keine S1-Prüfung. Vorher (bis zur Blockmitte) folgen R₂, X′, R₃."""
    plan = plan_klein(tage=((14,),), kontroll=('R', 'L1'))

    def regel(spec, v):
        k = spec['konfiguration']['id']
        if spec['laufart'] == 'R':                                     # Schritte unter der Alarmschwelle (0,0035)
            if spec['kontrollsatz'] == 2 or v['rolle'] == 'schlussreferenz':
                return dict(dN=-0.006)
            if spec['block'] == 1 and spec['kontrollsatz'] is None:
                return dict(dN=-0.003)                                 # Blockmitte, R₂, R₃
            return None
        if v['nummer'] == 0 and k in ('S106', 'S124'):                 # Vorprüfung besteht, Interpolation nicht
            return dict(dN=0.0095 if k == 'S106' else 0.0065)
    a = lauf(regel, plan=plan)
    früh, spät = nach_id(a, 'S106', 1), nach_id(a, 'S124', 1)
    assert früh[0]['g1'] is True and len(früh) == 2 and früh[1]['rolle'] == 'X_strich'
    assert spät[0]['g1'] is True and len(spät) == 1
    assert any('nach Beginn des Schlusskontrollsatzes' in t for t in spät[0]['entscheidung'])
    assert a.bericht()['auswahl']['S124|1']['status'] == 'fehlt: spät erkannt'
    vs = versuche(a)
    i = vs.index(früh[1])
    assert vs[i - 1]['rolle'] == 'R2' and vs[i + 1]['rolle'] == 'R3' and früh[1]['g1_bezug'] == [vs[i - 1]['id'],
                                                                                                  vs[i + 1]['id']]


def test_platzwahl_an_allen_kleinen_zustaenden():
    """Für Blöcke mit 1–4 Konfigurationen, jeden ungültigen Platz und jede gezogene Zahl j: Der Wiederholungslauf steht
    unmittelbar vor dem j-ten offenen Konfigurationslauf oder (j = m) vor dem Schlusskontrollsatz; gezogen wird
    integers(0, m + 1) mit m = Zahl der offenen Konfigurationsläufe. Die Abbildung j → Platz ist eineindeutig, also
    bei gleichverteiltem j gleichverteilt."""
    for nk in range(1, 5):
        for i in range(nk):
            ziel = f'S{100 + 2 * i:g}'
            plaetze = set()
            for j in range(nk - i):
                rng = FesteZiehung(j)
                a = lauf(lambda s, v: dict(stoerung=True) if s['konfiguration']['id'] == ziel and v['nummer'] == 0
                         and s['block'] == 1 else None, plan=plan_klein(tage=((nk,),)), rng=rng)
                m = nk - i - 1
                assert rng.aufrufe == [(0, m + 1)]
                vs = versuche(a)
                w = next(k for k, v in enumerate(vs) if v['rolle'] == 'wiederholung')
                danach = vs[w + 1]
                offen = [f'S{100 + 2 * c:g}' for c in range(i + 1, nk)]
                if j < m:
                    assert danach['konfiguration'] == offen[j] and danach['geplant']
                else:
                    assert danach['kontrollsatz'] == 2                    # vor dem Schlusskontrollsatz
                plaetze.add(w)
                z = a.z['ziehungen'][0]
                assert z['m'] == m and z['gezogen'] == j and z['plaetze'] == m + 1
            assert len(plaetze) == nk - i                                 # alle m + 1 Plätze erreichbar, verschieden


def test_platzwahl_mit_bereits_eingefuegter_wiederholung_und_letztem_platz():
    """Eine bereits eingefügte Wiederholung zählt als offener Konfigurationsplatz; der letzte Platz (j = m) liegt vor
    dem Schlusskontrollsatz, nach allen offenen Läufen."""
    rng = FesteZiehung(10)                                               # immer der letzte Platz

    def regel(s, v):
        k = s['konfiguration']['id']
        if s['block'] == 1 and v['nummer'] == 0 and k in ('S100', 'S102'):
            return dict(stoerung=True)
    a = lauf(regel, plan=plan_klein(tage=((4,),)), rng=rng)
    assert rng.aufrufe == [(0, 4), (0, 4)]                               # S100: 3 offen; S102: 2 offen + Wdh. S100
    vs = versuche(a)
    rolle = [(v['konfiguration'], v['rolle']) for v in vs if v['block'] == 1 and v['kontrollsatz'] is None]
    assert rolle[-2:] == [('S100', 'wiederholung'), ('S102', 'wiederholung')]


def test_zeiten_werden_fortgeschrieben_und_tage_verschoben():
    plan = plan_klein(tage=((3,), (2,)))

    def regel(s, v):
        if s['konfiguration']['id'] == 'S100' and s['block'] == 1 and v['nummer'] == 0:
            return dict(stoerung=True)
    a = lauf(regel, plan=plan, rng=FesteZiehung(0))
    vs = versuche(a)
    w = next(i for i, v in enumerate(vs) if v['rolle'] == 'wiederholung')
    for i, v in enumerate(vs):
        if i > 0 and vs[i - 1]['messtag'] == v['messtag']:
            assert v['t_start'] == vs[i - 1]['t_ende']                    # lückenlos, je Versuch T_Lauf
    geplant = {l['lauf_id']: l for l in plan}
    nach = [v for v in vs[w + 1:] if v['geplant']]
    assert all(v['t_start'] == geplant[v['bezug']]['t_start'] + 10.0 for v in nach)   # um einen Lauf verschoben
    tag2 = next(v for v in vs if v['messtag'] == 2)
    assert tag2['t_start'] == next(v for v in reversed(vs) if v['messtag'] == 1)['t_ende'] + 500.0


# ── G1 und S1 ─────────────────────────────────────────────────────────────────────────────────────────
def test_g1_sofort_mit_r1_und_ersatz_durch_x_strich():
    a = lauf(lambda s, v: dict(dN=0.05) if s['konfiguration']['id'] == 'S102' and v['nummer'] == 0 and
             s['block'] == 1 else None)
    vs = versuche(a)
    x = nach_id(a, 'S102', 1)
    i = vs.index(x[0])
    assert [v['rolle'] for v in vs[i + 1:i + 5]] == ['R1', 'R2', 'X_strich', 'R3']
    assert x[0]['g1'] is True and x[0]['g1_bezug'][1] == vs[i + 1]['id'] and x[1]['g1'] is False
    assert a.bericht()['auswahl']['S102|1']['status'] == 'ersetzt' and a.status == 'abgeschlossen'


def test_x_strich_ueber_der_grenze_und_s1():
    """Zwei reguläre Wiederholungen ungültig (G8), die dritte Messung mit G1-Verstoß: X′ wird trotz ausgeschöpfter
    Grenze gemessen und zählt als Wiederholung; verletzt auch X′ G1, greift S1."""
    def regel(s, v):
        if s['konfiguration']['id'] != 'S100' or s['block'] != 1:
            return None
        if v['nummer'] < 2:
            return dict(stoerung=True)
        return dict(dN=0.05)
    a = lauf(regel)
    x = nach_id(a, 'S100', 1)
    assert [v['nummer'] for v in x] == [0, 1, 2, 3] and x[3]['rolle'] == 'X_strich'
    assert a.z['wdh']['S100|1'] == 3 and a.status == 'angehalten' and a.z['halt']['regel'] == 'S1'
    assert x[3]['halt'] == 'S1' and 'X′' in a.z['halt']['grund']


def test_reproduzierter_und_nicht_reproduzierter_nullpunktalarm():
    def regel_rep(s, v):
        if s['laufart'] == 'R' and s['block'] == 1 and s['kontrollsatz'] == 2:
            return dict(dN=0.02)                                       # Alarm, Wiederholung ebenso
    a = lauf(regel_rep)
    assert a.status == 'angehalten' and a.z['halt']['regel'] == 'S1' and 'reproduzierter' in a.z['halt']['grund']

    def regel_einmal(s, v):
        if s['laufart'] == 'R' and s['kontrollsatz'] == 2 and v['nummer'] == 0:
            return dict(dN=0.02)
    b = lauf(regel_einmal)
    r = [v for v in versuche(b) if v['konfiguration'] == 'R' and v['kontrollsatz'] == 2]
    assert b.status == 'abgeschlossen' and r[0]['alarm'] and r[1]['rolle'] == 'kontrollwiederholung'
    assert not r[1]['alarm'] and r[1]['gueltig']


# ── Kontrollläufe und Einstellung 2 ─────────────────────────────────────────────────────────────────
def test_kontrolllauf_wiederholung_halt_und_l_strich_ausnahme():
    ok = lauf(lambda s, v: dict(stoerung=True) if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 1 and
              v['nummer'] == 0 else None)
    l1 = [v for v in versuche(ok) if v['konfiguration'] == 'L1' and v['kontrollsatz'] == 1]
    assert ok.status == 'abgeschlossen' and [v['gueltig'] for v in l1] == [False, True]
    halt = lauf(lambda s, v: dict(stoerung=True) if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 1
                else None)
    assert halt.status == 'angehalten' and halt.z['halt']['regel'] == 'Kontrolllauf'
    assert len([v for v in versuche(halt) if v['konfiguration'] == 'L1']) == 3
    plan = plan_klein(kontroll=('R', 'L1', 'L1′'))
    strich = lauf(lambda s, v: dict(stoerung=True) if s['konfiguration']['id'] == 'L1′' and s['kontrollsatz'] == 1
                  else None, plan=plan)
    ls = [v for v in versuche(strich) if v['konfiguration'] == 'L1′' and v['kontrollsatz'] == 1]
    assert strich.status == 'abgeschlossen' and len(ls) == 3 and ls[-1].get('grenze')
    b = strich.bericht()
    assert b['luecken'] == list(ablauf.LUECKEN_E2) and b['qualifikation_einstellung2'] == 'ausgeschlossen'
    # S2 für L′ offen: Liftoff in L′ hält nicht an, wird aber am Versuch vermerkt
    lift = lauf(lambda s, v: dict(G6=True) if s['konfiguration']['id'] == 'L1′' and s['kontrollsatz'] == 1 and
                v['nummer'] == 0 else None, plan=plan)
    assert lift.status == 'abgeschlossen' and ablauf.LUECKEN_E2[1] in lift.z['luecken'] and not lift.z['s2']
    assert any('S2 für L′ offen' in t for v in versuche(lift) for t in v['entscheidung'])


# ── S2, S3, S4, Halt und Wiederaufnahme ─────────────────────────────────────────────────────────────
EREIGNIS = dict(art='wiederaufnahme', quelle='extern (simuliert, Test)', zeitpunkt=1e6, befund='Ursachenanalyse ohne '
                'Befund (Testereignis)', mechanischer_eingriff=False, apparaturfehler=False)


def test_s2_halt_ausschluss_weitere_messung_und_zweites_s2():
    plan = plan_klein(tage=((3, 3),))

    def regel(s, v):
        if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and v['nummer'] == 0:
            return dict(G6=True)
    a = lauf(regel, plan=plan)
    assert a.status == 'angehalten' and a.z['halt']['regel'] == 'S2' and a.z['ausgeschlossen'] == ['S102']
    with pytest.raises(ablauf.AblaufFehler, match='fortsetzen'):
        a.ausfuehren()
    with pytest.raises(ablauf.AblaufFehler, match='externes Ereignis'):
        a.fortsetzen(dict(art='wiederaufnahme'))
    a.fortsetzen(EREIGNIS)
    assert a.status == 'abgeschlossen' and a.z['ereignisse'][0]['befund'].startswith('Ursachenanalyse')
    w = [v for v in versuche(a) if v['rolle'] == 'wiederaufnahme_kontrolle']
    assert len(w) == 2 and all(v['t_start'] >= 1e6 for v in w)
    assert [v['block'] for v in nach_id(a, 'S102')] == [1, 1, 2]           # Wiederholung im Block 1, weiter gemessen
    b = a.bericht()['auswahl']
    assert b['S102|2']['status'] == 'gueltig, S2-ausgeschlossen'
    # zweites S2: Phase 1 beendet, keine Fortsetzung
    c = lauf(lambda s, v: dict(G6=True) if s['konfiguration']['id'] == 'S102' and v['nummer'] == 0 else None,
             plan=plan)
    c.fortsetzen(EREIGNIS)
    assert c.status == 'abgebrochen' and not c.z['halt']['fortsetzbar']
    with pytest.raises(ablauf.AblaufFehler, match='nur nach einem Halt'):
        c.fortsetzen(EREIGNIS)


def test_s4_bleibt_trotz_einschueben_und_kontrollwiederholung():
    """G2 in zwei aufeinanderfolgenden Läufen mit bewegten Modulen: auch über eingefügte Referenzläufe hinweg und
    wenn die zweite Messung die sofortige Wiederholung eines Kontrolllaufs ist."""
    def regel(s, v):
        if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 1:
            return dict(G2=True)
    a = lauf(regel)
    assert a.status == 'angehalten' and a.z['halt']['regel'] == 'S4'
    l1 = [v for v in versuche(a) if v['konfiguration'] == 'L1']
    assert [v['rolle'] for v in l1] == ['kontrolle', 'kontrollwiederholung'] and l1[1]['halt'] == 'S4'

    def regel2(s, v):                                                # die Wiederholung von S100 steht später
        if s['block'] == 1 and v['nummer'] == 0 and s['konfiguration']['id'] in ('S100', 'S102'):
            return dict(G2=True)
    b = lauf(regel2, rng=FesteZiehung(1))
    assert b.status == 'angehalten' and b.z['halt']['regel'] == 'S4'
    # ein Referenzlauf dazwischen unterbricht die Folge nicht
    plan = plan_klein(tage=((13,),))

    def regel3(s, v):
        if s['block'] == 1 and v['nummer'] == 0 and s['konfiguration']['id'] in ('S122', 'S124'):
            return dict(G2=True)
    c = lauf(regel3, plan=plan, rng=FesteZiehung(5))
    vs = versuche(c)
    i = vs.index(nach_id(c, 'S124', 1)[0])
    assert vs[i - 1]['konfiguration'] == 'R' and c.z['halt']['regel'] == 'S4'


def test_s3_reproduziert_nicht_reproduziert_und_ueber_ungueltige_wiederholung():
    rep = lauf(lambda s, v: dict(S3=2.0) if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 2 else None)
    assert rep.status == 'angehalten' and rep.z['halt']['regel'] == 'S3'
    einmal = lauf(lambda s, v: dict(S3=2.0) if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 2 and
                  v['nummer'] == 0 else None)
    l1 = [v for v in versuche(einmal) if v['konfiguration'] == 'L1' and v['kontrollsatz'] == 2]
    assert einmal.status == 'abgeschlossen' and [v['rolle'] for v in l1] == ['kontrolle', 's3_wiederholung']

    def regel(s, v):
        if s['konfiguration']['id'] != 'L1' or s['kontrollsatz'] != 2:
            return None
        return [dict(S3=2.0), dict(stoerung=True), dict(S3=2.0)][min(v['nummer'], 2)]
    ueber = lauf(regel)
    l1 = [v for v in versuche(ueber) if v['konfiguration'] == 'L1' and v['kontrollsatz'] == 2]
    assert [v['rolle'] for v in l1] == ['kontrolle', 's3_wiederholung', 'kontrollwiederholung']
    assert ueber.z['halt']['regel'] == 'S3' and l1[-1]['halt'] == 'S3'      # S3 verschwindet nicht


def test_aufwaermen_nach_paragraph_6_und_halt():
    a = lauf(optionen=ablauf.Ablaufoptionen())
    vs = versuche(a)
    assert [v['rolle'] for v in vs[:2]] == ['aufwaermen', 'aufwaermen'] and a.status == 'abgeschlossen'
    i = [0]

    def wackeln(s, v):
        if v['rolle'] == 'aufwaermen':
            i[0] += 1
            return dict(dN_summe=0.002 * (i[0] % 2))                     # jeder zweite um 2 σ̂_ref versetzt
    b = lauf(wackeln, optionen=ablauf.Ablaufoptionen())
    assert b.status == 'angehalten' and b.z['halt']['regel'] == 'Aufwärmen'
    assert sum(v['rolle'] == 'aufwaermen' for v in versuche(b)) == ablauf.GRENZE_AUFWAERMEN


def test_keine_wahrheit_in_ablaufentscheidungen():
    """Das Ablaufmodul liest keine Wahrheit, Vorhersage, Hypothesen- oder E3-Größen; die Messung erhält nur die
    Kopfangaben des Versuchs."""
    with open(ablauf.__file__, encoding='utf-8') as f:
        baum = ast.parse(f.read())
    namen = set()
    for n in ast.walk(baum):
        if isinstance(n, ast.ImportFrom):
            namen.update(a.name for a in n.names)
            namen.add(n.module or '')
        elif isinstance(n, ast.Import):
            namen.update(a.name for a in n.names)
    verboten = ('wahrheit', 'vorhersage', 'h1', 'h2', 'h3', 'h4', 'kontrollen', 'zeltfit', 'bootstrap', 'teil_b',
                'auswertung', 'generator', 'harness')
    assert not [x for x in namen if any(x == v or x.endswith('.' + v) for v in verboten)]
    a = lauf()
    spec, v = a.messung.aufrufe[5]
    assert set(spec) <= {'lauf_id', 'laufart', 'modul', 'einstellung', 'konfiguration', 'phase', 'block', 'messtag',
                         'kontrollsatz', 'position', 't_start', 't_ende', 'position_geplant'}


# ── Ebene H: Generator, Stufe 2, Checkpoint ─────────────────────────────────────────────────────────
PROFIL = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, h3_mc=200, eps_ctrl_datensaetze=300)
PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=3)


def test_ohne_ablaufoptionen_bitgleich_zum_laufplan():
    m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', 'L1', PLAN, 7)
    r = kette.kampagne_ablauf('N01-A4', 'L1', PLAN, 7, PROFIL, n_min=2,
                              verfahren=vf.Verfahren('plan', 'zustand', ablauf.AUS))
    neu = kette.ablauf_tabelle(r)
    assert all(np.array_equal(tab.daten[f], neu.daten[f], equal_nan=True) for f in tab.daten)
    assert formate.sha256_json([{k: v for k, v in h.items() if k != 'versuch'} for h in neu.koepfe]) == \
        formate.sha256_json(tab.koepfe)


def test_rauschfrei_mit_allen_optionen_nur_das_aufwaermen_kommt_hinzu():
    r = kette.kampagne_ablauf('N01-A4', 'L0', PLAN, 3, PROFIL, n_min=2, rausch=rauschen.RAUSCHFREI)
    b = r['ablauf'].bericht()
    assert r['ablauf'].status == 'abgeschlossen'
    assert b['laufzahl']['zusaetzlich'] == 1 and b['rollen']['aufwaermen'] == 2 and set(b['auswahl_zaehler']) == {
        'gueltig'}


def test_zeitabhaengige_nullpunktdrift_folgt_dem_tatsaechlichen_zeitpunkt():
    """Mit Nullpunktdrift verschiebt eine Wiederholung alle späteren Läufe; ⟨N⟩ des ursprünglichen Versuchs eines
    geplanten Laufs folgt seinem tatsächlichen Zeitpunkt (Δ⟨N⟩ = Drift·Δt), seine übrigen Größen bleiben gleich."""
    sz = szenarien.KATALOG['N01-A4']
    rausch = rauschen.stufe('L1').mit(nullpunkt_drift_N_je_s=2e-7)
    m = szenarien.modell(sz, 'L1', plan=PLAN, rausch=rausch)
    eff = (dict(art='ereignis', ereignis='stoerung', versuch=dict(konfiguration='S110', block=1, nummer=0)),)
    m_ev = szenarien.modell(sz, 'L1', plan=PLAN, rausch=rausch)
    m_ev.effekte = eff
    aus = kette.kampagne_ablauf('N01-A4', 'L1', PLAN, 11, PROFIL, n_min=2, modell=m)
    mit = kette.kampagne_ablauf('N01-A4', 'L1', PLAN, 11, PROFIL, n_min=2, modell=m_ev)
    ta, tm = kette.ablauf_tabelle(aus), kette.ablauf_tabelle(mit)
    ia = {h['versuch']['bezug']: i for i, h in enumerate(ta.koepfe) if h.get('versuch', {}).get('geplant')}
    im = {h['versuch']['bezug']: i for i, h in enumerate(tm.koepfe) if h.get('versuch', {}).get('geplant')}
    w = next(i for i, h in enumerate(tm.koepfe) if h.get('versuch', {}).get('rolle') == 'wiederholung')
    spaeter = [b for b, i in im.items() if i > w and tm.koepfe[i]['messtag'] == tm.koepfe[w]['messtag']]
    assert spaeter
    zus = sum(1 for h in tm.koepfe if h.get('versuch')) - sum(1 for h in ta.koepfe if h.get('versuch'))
    for b in spaeter[:20]:
        i, j = ia[b], im[b]
        dt = tm.koepfe[j]['t_start'] - ta.koepfe[i]['t_start']
        assert dt > 0 and dt == pytest.approx(round(dt / PLAN.T_lauf) * PLAN.T_lauf)
        assert tm.daten['N_mittel'][j] - ta.daten['N_mittel'][i] == pytest.approx(2e-7 * dt, rel=1e-6, abs=1e-12)
        assert np.array_equal(tm.daten['Nk_summe'][j], ta.daten['Nk_summe'][i])
    assert zus >= 1


@pytest.fixture(scope='module')
def a4_ablauf():
    """A4, Seed 13: reguläre Wiederholungen, G1 mit R₂/X′/R₃, Alarm- und Kontrollwiederholungen, spät erkanntes G1."""
    return kette.kampagne_ablauf('N01-A4', 'L1', kp.Plan(n0=20, n_pilot=20, n_bloecke=6), 13, PROFIL, n_min=4)


def test_uebergabe_an_stufe2_eindeutige_zaehlung_und_halt_sperrt(a4_ablauf):
    r = a4_ablauf
    tab = kette.ablauf_tabelle(r)
    dl = auswertung.datenlage(tab, r['teil_b'], PROFIL)                 # Online = offline, ≤ 1 gültiger je Platz
    b = r['ablauf'].bericht()
    for c, e in dl['info'].items():
        if c.startswith('S'):
            n = sum(1 for x in b['auswahl'].values() if x['konfiguration'] == c and x['ausgewaehlt'])
            assert e['n_gueltig'] == n <= 6
    # Doppelbeitrag (manipulierte Tabelle) wird zurückgewiesen
    t2 = copy.deepcopy(tab)
    i = next(k for k, h in enumerate(t2.koepfe) if h.get('versuch', {}).get('rolle') == 'wiederholung')
    orig = next(k for k, h in enumerate(t2.koepfe) if h.get('versuch', {}).get('geplant') and
                h['versuch']['bezug'] == t2.koepfe[i]['versuch']['bezug'])
    t2.koepfe[orig] = dict(t2.koepfe[orig], stoerung=False)
    t2.koepfe[orig]['versuch'] = dict(t2.koepfe[orig]['versuch'], gueltig=True, gruende=[])
    t2.daten = {f: v.copy() for f, v in t2.daten.items()}
    for f in ('N_mittel', 'N_mittel_zellen', 'fuenftel_N_mittel', 'fuenftel_Nk', 'Nk_summe', 'Nk_zellen', 'zeiger',
              'sigma_grad', 'min_roh_zellen', 'max_roh_zellen', 'index_fehler', 'uebersteuert_zellen'):
        t2.daten[f][orig] = t2.daten[f][i]
    with pytest.raises(formate.FormatFehler, match='mehr als ein gültiger Versuch'):
        auswertung.datenlage(t2, r['teil_b'], PROFIL)
    # abweichende Online-Entscheidung wird erkannt
    t3 = copy.deepcopy(tab)
    t3.koepfe[i]['versuch'] = dict(t3.koepfe[i]['versuch'], gueltig=False)
    with pytest.raises(formate.FormatFehler, match='Entscheidung des Ablaufs'):
        auswertung.datenlage(t3, r['teil_b'], PROFIL)
    # ein angehaltener Ablauf sperrt alle Ausgänge
    t4 = copy.deepcopy(tab)
    t4.meta['ablauf'] = dict(t4.meta['ablauf'], status='angehalten', ende=dict(grund='S1: Test'))
    assert any('angehalten' in t for _, t in auswertung.datenlage(t4, r['teil_b'], PROFIL)['sperren_alle'])
    with pytest.raises(formate.FormatFehler, match='ohne Ablaufstand'):
        auswertung.datenlage(zf.LaufTabelle(tab.koepfe, tab.daten), r['teil_b'], PROFIL)


def test_checkpoint_fortsetzung_bitgleich_und_zurueckweisung(tmp_path, a4_ablauf):
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=6)
    r = kette.kampagne_ablauf('N01-A4', 'L1', plan, 13, PROFIL, n_min=4, bis=60)
    assert r['ablauf'].status == 'unterbrochen'
    ablauf.speichern(str(tmp_path / 'stand'), r['ablauf'])
    zustand = ablauf.laden(str(tmp_path / 'stand'))
    r2 = kette.kampagne_ablauf('N01-A4', 'L1', plan, 13, PROFIL, n_min=4, zustand=zustand)
    t_ganz, t_fort = kette.ablauf_tabelle(a4_ablauf), kette.ablauf_tabelle(r2)
    assert r2['ablauf'].status == 'abgeschlossen' and len(t_ganz) == len(t_fort)
    assert all(np.array_equal(t_ganz.daten[f], t_fort.daten[f], equal_nan=True) for f in t_ganz.daten)
    assert formate.sha256_json(t_ganz.koepfe) == formate.sha256_json(t_fort.koepfe)
    assert r2['ablauf'].z['ziehungen'] == a4_ablauf['ablauf'].z['ziehungen']
    anders = vf.Verfahren('plan', 'zustand', ablauf.Ablaufoptionen(aufwaermen=False))
    with pytest.raises(ablauf.AblaufFehler, match='anderer Kennung'):
        kette.kampagne_ablauf('N01-A4', 'L1', plan, 13, PROFIL, n_min=4, zustand=zustand, verfahren=anders)
    with pytest.raises(ablauf.AblaufFehler, match='anderer Kennung'):
        kette.kampagne_ablauf('N01-A4', 'L1', plan, 8, PROFIL, n_min=4, zustand=zustand)


def test_kette_mit_ablauf_und_kurzbefund(a4_ablauf):
    """Die Kampagnenkette mit Verfahren „zustand“ wertet die Versuche mit Stufe 2 aus und berichtet den Ablauf."""
    from pcmms_auswertung.harness import kampagnen
    r = kette.kette('N01-A4', 'L1', PROFIL, plan=kp.Plan(n0=20, n_pilot=20, n_bloecke=6), seed=13, n_min=4,
                    verfahren=vf.ZUSTAND, mit_wahrheit=False)
    assert r['verfahren'] == vf.ZUSTAND.kennung() and r['ergebnis']['herkunft']['ablauf']['status'] == 'abgeschlossen'
    assert r['ablauf']['laufzahl'] == a4_ablauf['ablauf'].bericht()['laufzahl']
    kb = kampagnen.kurzbefund(r['ergebnis'], r['teil_b'], 13, r['ablauf'])
    assert kb['ablauf']['status'] == 'abgeschlossen' and kb['ablauf']['laufzahl']['zusaetzlich'] >= 1
    with pytest.raises(ValueError, match='Ablaufoptionen'):
        vf.Verfahren('plan', 'zustand')


def test_geteilte_kontrollsaetze_einmal_gezaehlt(a4_ablauf):
    """Ein Kontrollsatz am Blockende dient dem Folgeblock als Anfangssatz und wird einmal gemessen; Stufe 2 bildet ŷ¹
    aus allen gültigen Kontrollläufen (n + d Sätze, dazu gültige Wiederholungen)."""
    r = a4_ablauf
    a = r['ablauf']
    saetze = {l['kontrollsatz'] for l in a.geplant if l['kontrollsatz'] is not None}
    assert len(saetze) == 6 + 1                                           # n Blöcke + d Messtage
    tab = kette.ablauf_tabelle(r)
    dl = auswertung.datenlage(tab, r['teil_b'], PROFIL)
    for j in (1, 2, 3):
        gueltig = [v for v in versuche(a) if v['konfiguration'] == f'L{j}' and v['gueltig'] and v['g1'] is not True]
        assert len(dl['kontroll'][(1, j)]) == len(gueltig)
        assert len({(v['kontrollsatz'], v['nummer']) for v in gueltig}) == len(gueltig)


def test_ebene_z_mit_derselben_ablaufsteuerung(tmp_path):
    """Ebene Z: Rohdatei je Versuch, Stufe 1, Entscheidungen auf der Stufe-1-Zusammenfassung; Stufe 2 bestätigt die
    Entscheidungen offline."""
    plan = kp.Plan(n0=6, n_pilot=6, n_bloecke=1, ref_min_p0=8)
    r = kette.kampagne_ablauf('N01-A4', 'L1', plan, 13, PROFIL, n_min=1, ebene='Z', verzeichnis=str(tmp_path / 'z'))
    a = r['ablauf']
    assert a.status == 'abgeschlossen' and all(h['ebene'] == 'Z' for h in r['tab0'].koepfe)
    t1 = a.tabelle()
    assert all(k['ebene'] == 'Z' and k['version_stufe1'].startswith('stufe1') for k in t1.koepfe)
    assert len(r['messung'].manifest) == len(r['tab0']) + len(t1)
    auswertung.datenlage(kette.ablauf_tabelle(r), r['teil_b'], PROFIL)


def test_planungshaken_berichtet_geplante_und_realisierte_messzeit():
    from pcmms_auswertung.harness import planung
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=50, h3_mc=50, eps_ctrl_datensaetze=100)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=4)
    prot = []
    hk = planung.haken('N01-A4', 'L1', prof, 2, 2, 5, (2,), (20,), plan, protokoll=prot, max_aufrufe=1,
                       verfahren=vf.ZUSTAND)
    m = szenarien.modell('N01-A4', 'L1', plan=plan)
    e = dict(k=9, N_z=plan.n_zyklen, T_a=plan.n_zyklen / m.system.f, T_e=1.0, T_lauf=plan.T_lauf, p_hat=0.0,
             n_max=None, f=m.system.f, zeit=dict(d=1, N_K=21, N_I=0), s_q=dict(nu_p=59))
    out = hk(e)
    c = out['kandidaten'][0]
    assert out['verfahren'] == vf.ZUSTAND.kennung()
    mz = c['messzeit']
    assert mz['formel_s'] == pytest.approx(((21 + 8) * 4 + 18) * plan.T_lauf)
    assert mz['ablauf']['messzeit_s']['geplant'] > 0
    assert mz['ablauf']['messzeit_s']['realisiert_mittel'] >= mz['ablauf']['messzeit_s']['geplant']


def test_ablauf_pruefsatz_nachrechenbar():
    """Der Prüfsatz des Ablaufs (eigene Datei, der alte Software-Prüfsatz bleibt unverändert) rechnet sich mit Inhalt,
    Prüfsummen und Gegenprobe nach."""
    from pcmms_auswertung.harness import ablauf_pruefsatz
    pfad = os.path.join(os.path.dirname(__file__), 'fixtures', 'ap13_ablauf_pruefsatz')
    r = ablauf_pruefsatz.pruefen(pfad)
    assert r['gleich'], r['abweichungen']
    assert r['inhalt']['N01-A4/L1/13/aus']['laufzahl']['zusaetzlich'] == 0
    assert r['inhalt']['S02-kontrolllauf/L1/7/zustand']['halt'] == 'S2'


def test_kein_stiller_rueckfall_auf_den_statischen_laufplan(tmp_path):
    """Ein angeforderter Ablauf fällt nicht still auf den statischen Laufplan zurück: Die Dateikette (nur statischer
    Laufplan) weist „zustand“ zurück, bevor sie etwas schreibt; kampagne_ablauf verlangt „zustand“."""
    from pcmms_auswertung.harness import dateien
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=50, h3_mc=50, eps_ctrl_datensaetze=100)
    plan = kp.Plan(n0=6, n_pilot=6, n_bloecke=1)
    with pytest.raises(ValueError, match='Dateikette: Ablauf'):
        dateien.kette_dateien(str(tmp_path / 'k'), 'N01-A4', 'L1', prof, plan=plan, seed=1, ebene='H',
                              verfahren=vf.ZUSTAND)
    assert not (tmp_path / 'k').exists()
    with pytest.raises(ValueError, match='nur der statische Laufplan'):
        kette.eingang_schreiben(str(tmp_path / 'e'), 'N01-A4', 'L1', plan, 1, prof, ebene='H', verfahren=vf.ZUSTAND)
    assert not (tmp_path / 'e').exists()
    with pytest.raises(ValueError, match='verlangt ein Verfahren'):
        kette.kampagne_ablauf('N01-A4', 'L1', plan, 1, prof, verfahren=vf.STATISCH)
