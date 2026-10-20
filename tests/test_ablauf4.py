"""Ablauffassung ablauf-4 (Auftrag vom 20.10.2026, Regeln ablauf.* des Profilstands 2026-11): Reihenfolge A1 + Z1,
Halt und Wiederaufnahme H1 + K1, Kontrollsatz N5 + N7, Bezugseröffnung nach einem Nullpunkthalt, Aufwärmen nur bei
Tageswechsel; jeweils gegen die historische Fassung ablauf-3 und gegen die unabhängige Offline-Prüfung von Stufe 2.

Wie test_ap13_ablauf mit der steuerbaren Skriptmessung (gezielte Verstöße an ausgewählten Versuchen), nicht mit
Monte-Carlo-Raten."""
import numpy as np
import pytest

from pcmms_auswertung import ablauf, auswertung, formate, gueltigkeit
from test_ap13_ablauf import EREIGNIS, S3, SW, FesteZiehung, Skript, _regel_verschachtelt, nach_id, plan_klein, versuche

OHNE_AUFWAERMEN = ablauf.Ablaufoptionen(aufwaermen=False)


def lauf(regel=None, plan=None, optionen=OHNE_AUFWAERMEN, rng=None, fassung='ablauf-4'):
    a = ablauf.Ablauf(plan if plan is not None else plan_klein(), Skript(regel), SW, S3,
                      rng or np.random.default_rng(1), optionen, 10.0, 500.0, kennung=dict(test=True), fassung=fassung)
    a.ausfuehren()
    return a


def rollen(a):
    return [v['rolle'] for v in versuche(a)]


def offline(a):
    """Stufe 2 aus der Tabelle: Gültigkeit je Versuch wie online, Klammern von X′ und die Folgen von ablauf-4."""
    t = a.tabelle()
    pr = gueltigkeit.pruefe(t, SW)
    assert [auswertung._online_gueltig(k['versuch']) for k in t.koepfe] == [bool(x) for x in pr['gueltig']]
    v4 = a.fassung == 'ablauf-4'
    auswertung._x_strich_gegenprobe(t, pr, v4=v4)
    if v4:
        auswertung._folgen_gegenprobe(t, a.kurz())
    return t, pr


def wieder(a, nach=600.0, **kw):
    """Wiederaufnahme `nach` Sekunden nach dem Halt (600 s: derselbe Messtag; tag_pause der Skriptpläne 500 s, daher
    hier ausdrücklich tageswechsel=False, wenn nicht anders verlangt)."""
    e = dict(EREIGNIS, zeitpunkt=a.z['halt']['t'] + nach)
    e.update(kw)
    e.setdefault('tageswechsel', False)
    return a.fortsetzen(e)


class Umgekehrt(FesteZiehung):
    """Reihenfolge des Kontrollsatzes der Wiederaufnahme umgekehrt: der Kontrolllauf L₁ vor dem Referenzlauf."""

    def __init__(self, j):
        super().__init__(j)
        self.bit_generator = np.random.default_rng(7).bit_generator     # für speichern/aus_zustand

    def permutation(self, n):
        return np.arange(n)[::-1]


# ── A1 + Z1: Reihenfolge ──────────────────────────────────────────────────────────────────────────────
def _regel_r1_s3(ks):
    """L₁ des Kontrollsatzes ks: +0,05 N (Vorprüfung gegen R₀ über ε_ctrl = 0,010 N, G1) und S3 (Re N₁ +2,0 bei
    Schwelle 0,5); die S3-Wiederholung bleibt unauffällig."""
    def regel(s, v):
        if v['rolle'] == 'kontrolle' and s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == ks:
            return dict(dN=0.05, S3=2.0)
    return regel


def test_r1_vor_der_s3_wiederholung():
    """A1: Auf den Lauf mit Vorprüfung folgt R₁, erst danach die S3-Wiederholung (ablauf-3 umgekehrt). Steht G1 fest
    (Kontrollsatz vor dem ersten Block), folgen R₂, X′, R₃ geschlossen vor der S3-Wiederholung; im Schlusskontrollsatz
    gibt es nach §6 keine G1-Wiederholung, R₁ kommt trotzdem zuerst."""
    for ks, plan, erwartet, alt_erwartet in (
            (1, plan_klein(tage=((3, 3),)), ['R1', 'R2', 'X_strich', 'R3', 's3_wiederholung'],
             ['s3_wiederholung', 'R1', 'R2', 'X_strich', 'R3']),
            (2, plan_klein(), ['R1', 's3_wiederholung'], ['s3_wiederholung', 'R1'])):
        neu, alt = lauf(_regel_r1_s3(ks), plan=plan), lauf(_regel_r1_s3(ks), plan=plan, fassung='ablauf-3')
        for a, e in ((neu, erwartet), (alt, alt_erwartet)):
            offline(a)
            vs = versuche(a)
            x = next(v for v in vs if v['rolle'] == 'kontrolle' and v['konfiguration'] == 'L1' and v['kontrollsatz'] == ks)
            i = vs.index(x)
            assert x['s3_ueber'] and x['g1'] is True and a.status == 'abgeschlossen'
            assert rollen(a)[i + 1:i + 1 + len(e)] == e, (a.fassung, ks)
            assert all(v['bezug_versuch'] == x['id'] for v in vs[i + 1:i + 1 + len(e)] if v['rolle'] != 'R2'
                       or ks == 1)
        x = next(v for v in versuche(neu) if v['rolle'] == 'kontrolle' and v['konfiguration'] == 'L1'
                 and v['kontrollsatz'] == ks)
        assert any('nach der begonnenen Referenzfolge' in t for t in x['entscheidung']) or ks == 2


def _regel_x_ungueltig(s, v):
    """L₁ des Kontrollsatzes vor Block 1 +0,05 N (G1 → R₂, X′, R₃); X′ selbst gestört (G8, ungültig nach G2–G10)."""
    if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 1:
        if v['rolle'] == 'kontrolle':
            return dict(dN=0.05)
        if v['rolle'] == 'X_strich':
            return dict(stoerung=True)


def test_ungueltiges_x_strich_laesst_die_kontrollwiederholung_nicht_vor_r3():
    neu, alt = lauf(_regel_x_ungueltig), lauf(_regel_x_ungueltig, fassung='ablauf-3')
    r = rollen(neu)
    i = r.index('X_strich')
    assert not versuche(neu)[i]['gueltig'] and 'G8' in versuche(neu)[i]['gruende']
    assert r[i - 1:i + 3] == ['R2', 'X_strich', 'R3', 'kontrollwiederholung']
    ra = rollen(alt)
    k = ra.index('X_strich')
    assert ra[k + 1] == 'kontrollwiederholung'                         # ablauf-3: Kontrollwiederholung vor R₃
    offline(neu)
    offline(alt)
    # Offline erkennt eine vorgezogene Kontrollwiederholung in einer ablauf-4-Tabelle
    t, pr = offline(neu)
    t.koepfe[i + 1], t.koepfe[i + 2] = t.koepfe[i + 2], t.koepfe[i + 1]
    with pytest.raises(formate.FormatFehler, match='nicht R₃ des Falls'):
        auswertung._x_strich_gegenprobe(t, gueltigkeit.pruefe(t, SW), v4=True)


# ── H1 + K1: Halt und Wiederaufnahme ─────────────────────────────────────────────────────────────────
def test_ausstehendes_r1_wird_beim_halt_verworfen_und_protokolliert():
    """Die S3-Wiederholung eines L₁ reproduziert S3 (Halt) und hätte zugleich die Vorprüfung ausgelöst: Das
    ausstehende R₁ wird bei der Wiederaufnahme verworfen und protokolliert; die offene G1-Prüfung schließt der erste
    gültige Referenzlauf danach. ablauf-3 misst das R₁ nach dem Kontrollsatz."""
    def regel(s, v):
        if s['konfiguration']['id'] == 'L1' and s['kontrollsatz'] == 2:
            return dict(S3=2.0, dN=0.015 if v['rolle'] == 's3_wiederholung' else None)

    for fassung in ('ablauf-4', 'ablauf-3'):
        a = lauf(regel, fassung=fassung)
        assert a.status == 'angehalten' and a.z['halt']['regel'] == 'S3'
        h = versuche(a)[-1]
        assert h['rolle'] == 's3_wiederholung' and h['halt'] == 'S3'
        if fassung == 'ablauf-4':
            assert [el['rolle'] for el in a.z['queue']][:1] == ['R1']
        wieder(a)
        r1 = [v for v in versuche(a) if v['rolle'] == 'R1' and v['bezug_versuch'] == h['id']]
        if fassung == 'ablauf-4':
            assert not r1
            assert [(e['rolle'], e['bezug_versuch']) for e in a.z['verworfen']] == [('R1', h['id'])]
            assert a.kurz()['verworfen'][0]['grund'].startswith('Halt: ausstehender sofortiger Folgelauf verworfen')
            assert h['g1'] is not None                                       # geschlossen über die Unterbrechung
        else:
            assert len(r1) == 1
        offline(a)


def test_ausstehende_s3_wiederholung_eines_x_strich_wird_beim_halt_verworfen():
    """X′ (L₁) weicht 0,015 N von R₂/R₃ ab: S1 hält nach R₃ an, die S3-Wiederholung von X′ steht noch aus. ablauf-4
    verwirft sie bei der Wiederaufnahme (protokolliert); ablauf-3 misst sie nach dem Kontrollsatz."""
    a = lauf(_regel_verschachtelt(0.015))
    x = next(v for v in versuche(a) if v['rolle'] == 'X_strich')
    assert a.z['halt']['regel'] == 'S1' and a.z['queue'][0]['rolle'] == 's3_wiederholung'
    wieder(a)
    assert 's3_wiederholung' not in rollen(a) and a.status == 'abgeschlossen'
    assert [(e['rolle'], e['bezug_versuch']) for e in a.z['verworfen']] == [('s3_wiederholung', x['id'])]
    assert a.kurz()['wiederaufnahmen'][0]['verworfen'] == 1 and a.kurz()['wiederaufnahmen'][0]['neue_g1_folgen'] == 0
    offline(a)


def test_halt_an_r3_unvollstaendige_klammer_ohne_sonderwiederholung():
    """K1: R₃ löst einen reproduzierten Nullpunktalarm aus (Nullpunkthalt nach X′). X′ war gemessen, also keine neue
    Folge; der erste gültige Referenzlauf nach der Wiederaufnahme (Bezugslauf) schließt X′ ohne vorgesehene Klammer:
    S1 nicht prüfbar, keine weitere Sonderwiederholung. Hält X′ G1 gegen R₂/Bezugslauf ein, ersetzt es den Lauf;
    verletzt es G1 (+0,03 N), fehlt der Platz."""
    for dx, status in ((0.0, 'ersetzt'), (0.03, 'fehlt: S1 nicht prüfbar')):
        halt = dict(t=None)

        def regel(s, v, dx=dx):
            if halt['t'] is not None and s['t_start'] >= halt['t']:
                return dict(dN=0.02)
            if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and v['rolle'] == 'konfiguration':
                return dict(dN=0.05)
            if v['rolle'] == 'X_strich':
                return dict(dN=dx)
            if v['rolle'] in ('R3', 'alarmwiederholung'):
                return dict(dN=0.02)
        a = lauf(regel)
        assert a.z['halt']['regel'] == 'S1' and a.z['halt']['nullpunkt']
        assert versuche(a)[-1]['rolle'] == 'alarmwiederholung'
        halt['t'] = a.z['halt']['t']
        wieder(a)
        x = next(v for v in versuche(a) if v['rolle'] == 'X_strich')
        assert sum(v['rolle'] == 'X_strich' for v in versuche(a)) == 1 and not a.z['verworfen']
        assert not x['g1_klammer']['vorgesehen'] and x['g1_bezug'][1] == next(
            v['id'] for v in versuche(a) if v['rolle'] == 'bezugslauf')
        assert any('S1 nicht prüfbar' in t for t in x['entscheidung']) and not x.get('halt')
        assert x['g1'] is (dx > 0) and (x.get('s1') == 'nicht prüfbar') is (dx > 0)
        assert a.bericht()['auswahl']['S102|1']['status'] == status and a.status == 'abgeschlossen'
        offline(a)


def _regel_nullpunkthalt(verschiebung=0.02, alle_danach=True):
    """S102 in Block 1 +0,05 N (G1 → R₂, X′, R₃); R₂ und seine Alarmwiederholung +verschiebung N (reproduzierter
    Nullpunktalarm, S1, Nullpunkthalt), X′ und R₃ stehen noch aus. Nach dem Halt (alle_danach) liegen alle Läufe um
    dieselbe Verschiebung höher: eine tatsächliche Nullpunktänderung."""
    zustand = dict(halt=None)

    def regel(s, v):
        if zustand['halt'] is not None and alle_danach and s['t_start'] >= zustand['halt']:
            return dict(dN=verschiebung)
        if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and v['rolle'] == 'konfiguration':
            return dict(dN=0.05)
        if v['rolle'] in ('R2', 'alarmwiederholung') and s['block'] == 1:
            return dict(dN=verschiebung)
    return regel, zustand


def test_nullpunkthalt_bezugseroeffnung_vor_dem_kontrollsatz_und_neue_folge():
    regel, zustand = _regel_nullpunkthalt()
    a = lauf(regel, rng=Umgekehrt(0))
    assert a.status == 'angehalten' and a.z['halt']['regel'] == 'S1' and a.z['halt']['nullpunkt']
    assert [el['rolle'] for el in a.z['queue']][:2] == ['X_strich', 'R3']
    r0_alt = a.z['r0']
    zustand['halt'] = a.z['halt']['t']
    wieder(a)
    vs, r = versuche(a), rollen(a)
    h = next(i for i, v in enumerate(vs) if v.get('halt') == 'S1')
    # 1. gesonderter Bezugslauf vor dem (umgekehrt gezogenen) Kontrollsatz, ohne Nullpunktvergleich mit dem alten R₀
    assert r[h + 1] == 'bezugslauf' and vs[h + 1]['gueltig'] and not vs[h + 1].get('alarm')
    assert vs[h + 1]['kontrollsatz'] is None
    w = [i for i, v in enumerate(vs) if v['kontrollsatz'] == 'W1']
    assert [vs[i]['konfiguration'] for i in w] == ['L1', 'R'] and w[0] == h + 2
    # 2./4. der zuerst gezogene L₁ wird gegen den neuen Bezug geprüft, nicht gegen das verworfene R₀: keine Vorprüfung
    assert vs[w[0]]['gueltig'] and vs[w[0]]['g1'] is False and r[w[0] + 1] != 'R1'
    # 3. der neue G1-Fall (X′ war beim Halt nicht gemessen) als vollständige neue Folge nach dem Kontrollsatz
    assert r[w[-1] + 1:w[-1] + 4] == ['R2', 'X_strich', 'R3']
    assert all(v['bezug_versuch'] == nach_id(a, 'S102', 1)[0]['id'] for v in vs[w[-1] + 1:w[-1] + 4])
    # 6. altes/neues R₀ und Differenz im Protokoll; die Wiederaufnahme ist erst nach dem Kontrollsatz erfolgreich
    bw = a.kurz()['bezugswechsel']
    assert len(bw) == 1 and bw[0]['alt'] == versuche(a)[r0_alt]['id'] and bw[0]['neu'] == vs[h + 1]['id']
    assert bw[0]['differenz_N'] == pytest.approx(0.02, abs=1e-12)
    wa = a.kurz()['wiederaufnahmen']
    assert len(wa) == 1 and wa[0]['erfolgreich'] and wa[0]['bezugseroeffnung'] and not wa[0]['tageswechsel']
    assert wa[0]['verworfen'] == 2 and wa[0]['neue_g1_folgen'] == 1
    assert {e['rolle'] for e in a.z['verworfen']} == {'X_strich', 'R3'}
    b = a.bericht()
    assert b['zusatzlaeufe']['bezugslauf'] == 1 and b['bezugswechsel'] == bw
    assert a.status == 'abgeschlossen' and b['auswahl']['S102|1']['status'] == 'ersetzt'
    offline(a)


def test_ohne_bezugseroeffnung_vergleicht_ablauf_3_den_l_lauf_mit_dem_verworfenen_bezug():
    """Dieselbe Folge in ablauf-3: Der zuerst gezogene L₁ des Kontrollsatzes wird gegen das verworfene R₀ vorgeprüft
    (die Lücke „L-Lauf vor erstem R im zufälligen W-Satz“)."""
    regel, zustand = _regel_nullpunkthalt()
    a = lauf(regel, rng=Umgekehrt(0), fassung='ablauf-3')
    zustand['halt'] = a.z['halt']['t']
    wieder(a)
    vs, r = versuche(a), rollen(a)
    h = next(i for i, v in enumerate(vs) if v.get('halt') == 'S1')
    assert vs[h + 1]['kontrollsatz'] == 'W1' and vs[h + 1]['konfiguration'] == 'L1' and r[h + 2] == 'R1'


def test_ungueltiger_bezugslauf_grenze_und_erneuter_halt():
    """Bezugsläufe gestört (G8): zwei sofortige Wiederholungen, dann Halt „Bezugseröffnung“; keine Vorprüfung und kein
    Kontrolllauf vor einem gültigen Bezug. Die nächste Wiederaufnahme beginnt wieder mit einem Bezugslauf; ist er
    gültig, folgt der Kontrollsatz und die Wiederaufnahme ist erfolgreich."""
    regel0, zustand = _regel_nullpunkthalt()
    gestoert = dict(an=True)

    def regel(s, v):
        if v['rolle'] == 'bezugslauf' and gestoert['an']:
            return dict(stoerung=True)
        return regel0(s, v)
    a = lauf(regel, rng=Umgekehrt(0))
    zustand['halt'] = a.z['halt']['t']
    wieder(a)
    assert a.status == 'angehalten' and a.z['halt']['regel'] == 'Bezugseröffnung' and a.z['halt']['fortsetzbar']
    vs = versuche(a)
    h = next(i for i, v in enumerate(vs) if v.get('halt') == 'S1')
    assert rollen(a)[h + 1:] == ['bezugslauf'] * (ablauf.GRENZE_BEZUG + 1)
    assert a.z['r0'] is None and a.kurz()['wiederaufnahmen'][0]['erfolgreich'] is False
    gestoert['an'] = False
    wieder(a)
    vs, r = versuche(a), rollen(a)
    g = next(i for i, v in enumerate(vs) if v.get('halt') == 'Bezugseröffnung')
    assert r[g + 1] == 'bezugslauf' and vs[g + 1]['gueltig'] and vs[g + 2]['kontrollsatz'] == 'W2'
    wa = a.kurz()['wiederaufnahmen']
    assert [w['erfolgreich'] for w in wa] == [False, True] and wa[1]['bezugseroeffnung']
    assert a.status == 'abgeschlossen' and len(a.kurz()['bezugswechsel']) == 1
    offline(a)


def test_einzelner_nullpunktalarm_und_s3_im_kontrollsatz_werden_wiederholt_reproduzierte_halten():
    """N7: Im Kontrollsatz der Wiederaufnahme hält ein einzelner Nullpunktalarm bzw. eine einzelne S3-Überschreitung
    nicht sofort an (ablauf-3: Halt „Wiederaufnahme“), sondern wird wie sonst wiederholt; erst der reproduzierte Alarm
    hält an."""
    def basis(s, v):
        if s['konfiguration']['id'] == 'S102' and s['block'] == 1 and v['nummer'] == 0:
            return dict(G6=True)                                         # S2: Halt
    for art, nur_erste in (('alarm', True), ('alarm', False), ('s3', True), ('s3', False)):
        def regel(s, v, art=art, nur_erste=nur_erste):
            if s['kontrollsatz'] == 'W1' and (v['rolle'] == 'wiederaufnahme_kontrolle' or not nur_erste):
                if art == 'alarm' and s['laufart'] == 'R':
                    return dict(dN=0.02)
                if art == 's3' and s['laufart'] == 'L':
                    return dict(S3=2.0)
            return basis(s, v)
        for fassung in ('ablauf-4', 'ablauf-3'):
            a = lauf(regel, rng=FesteZiehung(0), fassung=fassung)
            wieder(a)
            if fassung == 'ablauf-3':
                assert a.z['halt']['regel'] == 'Wiederaufnahme'
            elif nur_erste:
                assert a.status == 'abgeschlossen', (art, a.z['halt'])
                w = [v for v in versuche(a) if v['kontrollsatz'] == 'W1']
                assert {'alarmwiederholung', 'kontrollwiederholung', 's3_wiederholung'} & {v['rolle'] for v in w}
                assert a.kurz()['wiederaufnahmen'][0]['erfolgreich']
            else:
                assert a.status == 'angehalten' and a.z['halt']['regel'] == ('S1' if art == 'alarm' else 'S3')
                assert a.kurz()['wiederaufnahmen'][0]['erfolgreich'] is False
            offline(a)


# ── N6: Aufwärmen nur bei Tageswechsel ───────────────────────────────────────────────────────────────
def test_aufwaermen_nur_bei_tageswechsel_ersetzt_den_bezugslauf():
    regel, zustand = _regel_nullpunkthalt()
    opt = ablauf.Ablaufoptionen()
    a = lauf(regel, optionen=opt, rng=FesteZiehung(0))
    tag = versuche(a)[-1]['messtag_ist']
    zustand['halt'] = a.z['halt']['t']
    wieder(a, nach=3600.0, tageswechsel=True)
    vs, r = versuche(a), rollen(a)
    h = next(i for i, v in enumerate(vs) if v.get('halt') == 'S1')
    assert r[h + 1:h + 3] == ['aufwaermen', 'aufwaermen'] and 'bezugslauf' not in r
    assert vs[h + 1]['messtag_ist'] == tag + 1 and vs[h + 1]['messtag'] == vs[h]['messtag']
    assert a.kurz()['bezugswechsel'][0]['rolle_neu'] == 'aufwaermen'
    assert a.kurz()['wiederaufnahmen'][0]['tageswechsel'] and a.status == 'abgeschlossen'
    offline(a)
    # derselbe Tag: kein Aufwärmen, Bezugslauf
    regel, zustand = _regel_nullpunkthalt()
    b = lauf(regel, optionen=opt, rng=FesteZiehung(0))
    zustand['halt'] = b.z['halt']['t']
    wieder(b, nach=60.0)
    r = rollen(b)
    h = next(i for i, v in enumerate(versuche(b)) if v.get('halt') == 'S1')
    assert r[h + 1] == 'bezugslauf' and 'aufwaermen' not in r[h + 1:]
    assert versuche(b)[h + 1]['messtag_ist'] == versuche(b)[h]['messtag_ist']
    # ohne Ereignisfeld entscheidet der Abstand zum Halt (tag_pause des Plans)
    regel, zustand = _regel_nullpunkthalt()
    c = lauf(regel, optionen=opt, rng=FesteZiehung(0))
    zustand['halt'] = c.z['halt']['t']
    c.fortsetzen(dict(EREIGNIS, zeitpunkt=c.z['halt']['t'] + 501.0))
    assert c.kurz()['wiederaufnahmen'][0]['tageswechsel']


def test_ungueltiger_aufwaermlauf_ohne_aufwaermoption_fuehrt_zum_bezugslauf():
    regel0, zustand = _regel_nullpunkthalt()

    def regel(s, v):
        if v['rolle'] == 'aufwaermen' and zustand['halt'] is not None:
            return dict(stoerung=True)
        return regel0(s, v)
    a = lauf(regel, rng=FesteZiehung(0))
    zustand['halt'] = a.z['halt']['t']
    wieder(a, nach=3600.0, tageswechsel=True)
    r = rollen(a)
    h = next(i for i, v in enumerate(versuche(a)) if v.get('halt') == 'S1')
    assert r[h + 1:h + 3] == ['aufwaermen', 'bezugslauf'] and a.status == 'abgeschlossen'
    offline(a)


# ── Gegenprobe offline, Checkpoint ───────────────────────────────────────────────────────────────────
def test_offline_erkennt_einen_vergleich_mit_dem_verworfenen_bezug():
    regel, zustand = _regel_nullpunkthalt()
    a = lauf(regel, rng=Umgekehrt(0))
    zustand['halt'] = a.z['halt']['t']
    wieder(a)
    t, pr = offline(a)
    h = next(i for i, k in enumerate(t.koepfe) if k['versuch'].get('halt') == 'S1')
    t.koepfe[h + 1]['versuch'] = dict(t.koepfe[h + 1]['versuch'], rolle='wiederaufnahme_kontrolle')
    alarm = gueltigkeit.nullpunktalarm(t, SW, np.ones(len(t), bool))
    assert alarm[h + 1]['alarm']                                         # gegen das verworfene R₀ verglichen
    with pytest.raises(formate.FormatFehler, match='erwartet bezugslauf'):
        auswertung._folgen_gegenprobe(t, a.kurz())


def test_checkpoint_fortsetzung_bitgleich_und_keine_fortsetzung_ueber_fassungen(tmp_path):
    """Nach dem Bezugslauf technisch unterbrochen, gespeichert und fortgesetzt: dieselben Versuche, derselbe
    Bezugswechsel und dasselbe Wiederaufnahmeprotokoll wie ohne Unterbrechung; ein Stand von ablauf-4 wird weder als
    ablauf-3 noch mit anderer Kennung fortgesetzt."""
    regel, zustand = _regel_nullpunkthalt()
    ganz = lauf(regel, rng=Umgekehrt(0))
    zustand['halt'] = ganz.z['halt']['t']
    wieder(ganz)
    i = rollen(ganz).index('bezugslauf')
    regel, zustand = _regel_nullpunkthalt()
    plan = plan_klein()
    b = ablauf.Ablauf(plan, Skript(regel), SW, S3, Umgekehrt(0), OHNE_AUFWAERMEN, 10.0, 500.0, kennung=dict(test=True))
    b.ausfuehren()
    zustand['halt'] = b.z['halt']['t']
    e = dict(EREIGNIS, zeitpunkt=b.z['halt']['t'] + 600.0, tageswechsel=False)
    _teil_fortsetzen(b, e, bis=i + 2)
    assert b.status == 'unterbrochen' and versuche(b)[i]['rolle'] == 'bezugslauf'
    ablauf.speichern(str(tmp_path / 'stand'), b)
    z = ablauf.laden(str(tmp_path / 'stand'))
    c = ablauf.Ablauf.aus_zustand(z, plan, Skript(regel), SW, S3, Umgekehrt(0), 10.0, 500.0, dict(test=True))
    assert c.ausfuehren() == 'abgeschlossen'
    feld = ('id', 'rolle', 'gueltig', 'g1', 'g1_bezug', 'alarm', 'kontrollsatz', 't_start', 'messtag_ist')
    assert [{f: v.get(f) for f in feld} for v in versuche(c)] == [{f: v.get(f) for f in feld} for v in versuche(ganz)]
    assert c.kurz()['bezugswechsel'] == ganz.kurz()['bezugswechsel']
    assert c.kurz()['wiederaufnahmen'] == ganz.kurz()['wiederaufnahmen']
    with pytest.raises(ablauf.AblaufFehler, match='keine stille Fortsetzung über Ablauffassungen'):
        ablauf.Ablauf.aus_zustand(z, plan, Skript(regel), SW, S3, Umgekehrt(0), 10.0, 500.0, dict(test=True),
                                  fassung='ablauf-3')
    with pytest.raises(ablauf.AblaufFehler, match='anderer Kennung'):
        ablauf.Ablauf.aus_zustand(z, plan, Skript(regel), SW, S3, Umgekehrt(0), 10.0, 500.0, dict(test=False))


def _teil_fortsetzen(a, ereignis, bis):
    """fortsetzen bis zur Versuchszahl `bis` (technische Unterbrechung nach der Wiederaufnahme)."""
    orig = a.ausfuehren
    a.ausfuehren = lambda bis_=None: orig(bis=bis)
    try:
        a.fortsetzen(ereignis)
    finally:
        a.ausfuehren = orig


def test_ablauf_pruefsatz_ablauf4_nachrechenbar():
    """Prüfsatz des Regelstands 2026-11 (ablauf-4, ENTW-2026-11, P0.7-Anordnung) neben dem unveränderten historischen:
    Inhalt, Prüfsummen und Gegenprobe rechnen sich nach; der S2-Fall wird mit der simulierten Wiederaufnahme
    abgeschlossen."""
    import os
    from pcmms_auswertung.harness import ablauf_pruefsatz
    r = ablauf_pruefsatz.pruefen(os.path.join(os.path.dirname(__file__), 'fixtures', 'ap13_ablauf_pruefsatz_ablauf4'))
    assert r['gleich'], r['abweichungen']
    assert r['inhalt']['N01-A4/L1/13/aus']['laufzahl']['zusaetzlich'] == 0
    s = r['inhalt']['S02-kontrolllauf/L1/7/zustand']
    assert s['status'] == 'abgeschlossen' and s['s2'] and s['halt'] is None
