"""Kennwerte berechneter Felder und ihr Vergleich mit Toleranz (kennwerte.py; Ergebnisprüfung nach Entscheidung E-4
vom 12.11.2026, docs/kennwerte_untersuchung_2026-11-13/bericht.md).

Geprüft wird: die Kennwerte selbst (von Hand nachgerechnet, exakt gerundete Summen, exakte Felder, nicht endliche
Einträge), die Zusage des Vergleichs (kein Alarm, solange jeder Eintrag innerhalb seiner Toleranz liegt), was er
erkennt, was er nicht erkennt (einzelner Eintrag unterhalb von n·τ), der Vergleich vollständiger Objekte und die
Kennwerte derselben Kampagne unter zwei Rechenkernen von OpenBLAS.

Alle Daten sind synthetisch. Geprüft wird die Software, keine Apparatur."""
import json
import math
import os
import subprocess
import sys
from fractions import Fraction

import numpy as np
import pytest

from pcmms_auswertung import formate, kennwerte as kw
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import kette

CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code')


def _feld(seed=1, form=(40, 3, 12), komplex=True):
    """Feld mit gemischten Größenordnungen (wie Harmonische: wenige große, viele kleine Einträge)."""
    rng = np.random.default_rng(seed)
    skala = 10.0 ** rng.uniform(-6, 0.5, form)
    x = skala * rng.standard_normal(form)
    return x + 1j * skala * rng.standard_normal(form) if komplex else x


def _tau(a, rtol=kw.RTOL, atol=kw.ATOL):
    return rtol * float(np.abs(kw._reell(a)).max()) + atol


def _n(a):
    return kw._reell(a).size


# ── Kennwerte ────────────────────────────────────────────────────────────────────────────────────────
def test_kennwerte_eines_feldes_von_hand():
    """Summe, Quadratsumme und Extremwerte an dyadischen Zahlen exakt; die gewichteten Summen gegen die Gewichte
    gᵢ = ((a·i + c) mod p)/p in rationaler Rechnung."""
    x = np.array([[1.0, -2.0, 3.5], [0.25, -0.5, 8.0]])
    k = kw.feld(x)
    assert (k['dtype'], k['form'], k['n']) == ('float64', [2, 3], 6)
    assert k['nicht_endlich'] == dict(n=0, sha256=None)
    assert (k['summe'], k['quadrat']) == (10.25, 81.5625)
    assert (k['minimum'], k['maximum']) == (-2.0, 8.0)
    werte = [Fraction(v) for v in x.ravel().tolist()]
    for nr, (a, c, p) in enumerate(kw.GEWICHTE, 1):
        soll = sum(Fraction((a * i + c) % p, p) * v for i, v in enumerate(werte))
        assert k[f'gewichtet_{nr}'] == pytest.approx(float(soll), rel=1e-15, abs=0)
        assert math.gcd(a, p) == 1 and 0 <= (a * 5 + c) % p < p
    assert set(k) == {'dtype', 'form', 'n', 'nicht_endlich', 'summe', 'quadrat', 'gewichtet_1', 'gewichtet_2',
                      'minimum', 'maximum'}
    json.dumps(k)                                                       # JSON-fähig ohne Umwandlung


def test_komplex_real_und_imaginaerteil_nacheinander():
    z = np.array([1 + 2j, -3 + 0.5j])
    k = kw.feld(z)
    assert k == dict(kw.feld(np.array([1.0, 2.0, -3.0, 0.5])), dtype='complex128', form=[2])
    assert k['n'] == 4 and k['summe'] == 0.5 and k['minimum'] == -3.0


def test_exakte_felder_tragen_eine_pruefsumme():
    i, b = np.array([[0, 1], [2, -3]]), np.array([True, False, True])
    ki, kb = kw.feld(i), kw.feld(b)
    assert set(ki) == {'dtype', 'form', 'n', 'sha256'} and herk(ki) and herk(kb)
    assert kw.vergleich(ki, kw.feld(i.copy())) == dict(gleich=True, kennwerte_gleich=True, abweichungen=[],
                                                        auslastung=0.0)
    for anders in (np.array([[0, 1], [2, -4]]), i.astype(np.int32), i.ravel()):
        v = kw.vergleich(ki, kw.feld(anders))
        assert not v['gleich'] and v['auslastung'] == math.inf and v['abweichungen']
    assert not kw.vergleich(kb, kw.feld(~b))['gleich']
    assert kw.vergleich(ki, kw.feld(i.astype(float)))['abweichungen'] == ['dtype: float64 statt int64']
    with pytest.raises(kw.KennwertFehler, match='Datentyp'):
        kw.feld(np.array(['a', 'b']))


def herk(k):
    return len(k['sha256']) == 64 and set(k['sha256']) <= set('0123456789abcdef')


def test_nicht_endliche_eintraege_zaehlen_null_und_stehen_im_muster():
    x = np.array([1.0, np.nan, -2.0, np.inf, 4.0, -np.inf])
    k = kw.feld(x)
    assert k['nicht_endlich']['n'] == 3 and herk(k['nicht_endlich'])
    assert (k['summe'], k['quadrat'], k['minimum'], k['maximum']) == (3.0, 21.0, -2.0, 4.0)
    assert kw.vergleich(k, kw.feld(x.copy()))['kennwerte_gleich']
    for anders in (np.array([1.0, -2.0, np.nan, np.inf, 4.0, -np.inf]),           # NaN an anderer Stelle
                   np.array([1.0, np.inf, -2.0, np.nan, 4.0, -np.inf]),           # NaN und ∞ vertauscht
                   np.array([1.0, 0.0, -2.0, np.inf, 4.0, -np.inf])):             # NaN durch 0 ersetzt
        v = kw.vergleich(k, kw.feld(anders))
        assert not v['gleich'] and 'nicht endliche' in v['abweichungen'][0]
    leer = kw.feld(np.full(3, np.nan))
    assert leer['minimum'] is None and leer['maximum'] is None and leer['summe'] == 0.0
    assert kw.vergleich(leer, kw.feld(np.full(3, np.nan)))['gleich']
    assert kw.feld(np.zeros((0, 3)))['minimum'] is None


def test_summen_exakt_gerundet_unabhaengig_von_der_reihenfolge():
    """math.fsum: Summe und Quadratsumme hängen nicht von der Reihenfolge der Einträge ab (und damit nicht von einer
    Summationsreihenfolge der Bibliothek); die gewichteten Summen hängen von der Stelle ab."""
    x = _feld(3, (500,), komplex=False)
    k = kw.feld(x)
    um = kw.feld(x[np.random.default_rng(0).permutation(x.size)])
    assert all(k[g] == um[g] for g in ('summe', 'quadrat', 'minimum', 'maximum'))
    assert k['gewichtet_1'] != um['gewichtet_1'] and k['gewichtet_2'] != um['gewichtet_2']
    assert k['summe'] == math.fsum(x.tolist()) and k['quadrat'] == math.fsum((x * x).tolist())


def test_json_rundreise_erhaelt_die_kennwerte(tmp_path):
    d = dict(a=_feld(1), b=_feld(2, (7,), komplex=False), c=np.arange(5), d=np.array([1.0, np.nan]))
    k = kw.felder(d)
    assert list(k) == ['a', 'b', 'c', 'd'] and list(kw.felder(d, ['b', 'a'])) == ['a', 'b']
    p = str(tmp_path / 'k')
    formate.schreibe_objekt(p, formate.kopf('pruefsatz', formate.synth_kennung('KENNWERTE')), dict(kennwerte=k))
    _, gelesen = formate.lies_objekt(p, 'pruefsatz')
    v = kw.vergleich_felder(k, gelesen['kennwerte'])
    assert v['gleich'] and v['kennwerte_gleich'] and v['auslastung'] == 0.0


# ── Zusage des Vergleichs ────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize('komplex', [True, False])
def test_kein_alarm_solange_jeder_eintrag_innerhalb_der_toleranz_liegt(komplex):
    """Liegt jeder Eintrag innerhalb von τ = rtol·M + atol, schlägt kein Kennwert an: gleichgerichtete Abweichungen
    (ungünstigster Fall für die Summen), wechselnde, zufällige und die Verschiebung der Extremwerte."""
    rng = np.random.default_rng(11)
    for seed in range(6):
        x = _feld(seed, komplex=komplex)
        tau = 0.999 * _tau(x)
        r = kw._reell(x)
        muster = [np.ones(r.size), -np.ones(r.size), np.where(np.arange(r.size) % 2, 1.0, -1.0),
                  rng.uniform(-1, 1, r.size), np.sign(r), -np.sign(r)]
        for m in muster:
            y = r + tau * m
            y = (y[0::2] + 1j * y[1::2]).reshape(x.shape) if komplex else y.reshape(x.shape)
            v = kw.vergleich(kw.feld(x), kw.feld(y))
            assert v['gleich'] and not v['kennwerte_gleich'] and 0 < v['auslastung'] <= 1.0, v


def test_auslastung_misst_den_abstand_zur_toleranz():
    x = _feld(5, komplex=False)
    k = kw.feld(x)
    halb = kw.vergleich(k, kw.feld(x + 0.5 * _tau(x)))
    assert halb['gleich'] and halb['auslastung'] == pytest.approx(0.5, rel=1e-3)
    doppelt = kw.vergleich(k, kw.feld(x + 2.0 * _tau(x)))
    assert not doppelt['gleich'] and doppelt['auslastung'] == pytest.approx(2.0, rel=1e-3)
    assert any(t.startswith('summe:') for t in doppelt['abweichungen'])


# ── Was der Vergleich erkennt ────────────────────────────────────────────────────────────────────────
def _vertauscht(x):
    y = x.copy().ravel()
    y[[10, 700]] = y[[700, 10]]
    return y.reshape(x.shape)


def _ein_eintrag(x, faktor):
    """Ein Eintrag mittlerer Größe (kein Extremwert) um faktor·n·τ verändert."""
    y = x.copy()
    r = np.abs(kw._reell(x))
    i = int(np.argsort(r)[r.size // 2])
    y.ravel()[i // 2] += faktor * _n(x) * _tau(x) * (1j if i % 2 else 1.0)
    return y


FAELLE_ERKANNT = {
    'alle Einträge um 10⁻⁸ relativ größer': lambda x: x * (1 + 1e-8),
    'alle Einträge um 10·τ verschoben': lambda x: x + 10 * _tau(x),
    'ein Eintrag um 2·n·τ geändert': lambda x: _ein_eintrag(x, 2.0),
    'zwei Einträge vertauscht': _vertauscht,
    'um eine Stelle verschoben': lambda x: np.roll(x.ravel(), 1).reshape(x.shape),
    'zwei Zeilen vertauscht': lambda x: np.concatenate([x[1:2], x[0:1], x[2:]]),
    'Imaginärteil mit anderem Vorzeichen': np.conj,
    'Real- und Imaginärteil vertauscht': lambda x: x.imag + 1j * x.real,
    'größter Eintrag um 5·τ größer': lambda x: x + 5 * _tau(x) * (np.abs(x.real) == np.abs(x.real).max()),
    'ein Eintrag NaN': lambda x: np.where(np.arange(x.size).reshape(x.shape) == 77, np.nan, x),
    'andere Form': lambda x: x.reshape(x.shape[0], -1),
    'nur der Realteil': lambda x: x.real,
    'erste Zeile fehlt': lambda x: x[1:],
}


@pytest.mark.parametrize('fall', FAELLE_ERKANNT)
def test_erkennt(fall):
    x = _feld(8)
    v = kw.vergleich(kw.feld(x), kw.feld(FAELLE_ERKANNT[fall](x)))
    assert not v['gleich'] and v['abweichungen'] and v['auslastung'] > 1.0, fall


def test_grenze_ein_einzelner_eintrag_unterhalb_von_n_tau_bleibt_unerkannt():
    """Bekannte Grenze der Kennwerte (Bericht, Abschnitt 5): Die Änderung eines einzelnen Eintrags, der kein
    Extremwert ist, fällt erst oberhalb von n·τ auf, also n-mal gröber als bei einem Vergleich Eintrag für Eintrag.
    Der Vergleich vollständiger Objekte erkennt dieselbe Änderung."""
    x = _feld(8)
    unter, ueber = _ein_eintrag(x, 0.5), _ein_eintrag(x, 2.0)
    assert np.abs(unter - x).max() > 1000 * _tau(x)                     # weit über der Toleranz eines Eintrags
    assert kw.vergleich(kw.feld(x), kw.feld(unter))['gleich']
    assert not kw.vergleich(kw.feld(x), kw.feld(ueber))['gleich']
    assert not kw.vergleich_objekt(dict(x=x), dict(x=unter))['gleich']


def test_vergleich_der_feldsaetze_nennt_das_feld():
    d = dict(a=_feld(1), b=_feld(2, (9,), komplex=False), c=np.arange(4))
    k = kw.felder(d)
    v = kw.vergleich_felder(k, kw.felder(dict(d, b=d['b'] + 1e-13)))
    assert v['gleich'] and not v['kennwerte_gleich'] and v['feld_auslastung'] == 'b' and 0 < v['auslastung'] < 1
    assert v['toleranz'] == dict(rtol=kw.RTOL, atol=kw.ATOL, bezug=kw.toleranz()['bezug'])
    v = kw.vergleich_felder(k, kw.felder(dict(d, b=d['b'] * 1.001)))
    assert not v['gleich'] and all(t.startswith('Feld b: ') for t in v['abweichungen']) and len(v['abweichungen']) > 1
    assert kw.vergleich_felder(k, kw.felder({x: d[x] for x in 'ab'}))['abweichungen'] == ['Feld c: fehlt']
    assert kw.vergleich_felder(kw.felder({x: d[x] for x in 'ab'}), k)['abweichungen'] == ['Feld c: zusätzlich']
    with pytest.raises(kw.KennwertFehler, match=r'Phase-0-Daten: Feld b: .* \(und \d+ weitere\)'):
        kw.pruefe(k, kw.felder(dict(d, b=d['b'] * 1.001)), 'Phase-0-Daten')
    assert kw.pruefe(k, kw.felder(d), 'x')['kennwerte_gleich']
    # eine größere Toleranz lässt sich ausdrücklich wählen und steht im Ergebnis
    assert kw.vergleich_felder(k, kw.felder(dict(d, b=d['b'] * (1 + 1e-8))), rtol=1e-6)['toleranz']['rtol'] == 1e-6
    assert kw.vergleich_felder(k, kw.felder(dict(d, b=d['b'] * (1 + 1e-8))), rtol=1e-6)['gleich']


# ── Vergleich vollständiger Objekte ──────────────────────────────────────────────────────────────────
def test_vergleich_vollstaendiger_objekte():
    """Exakt: Schlüssel, Längen, Texte, ganze Zahlen, Wahrheitswerte, None; mit Toleranz: Gleitkommazahlen und
    -felder; übergangene Schlüssel auf jeder Ebene."""
    a = dict(ausgang='bestätigt', n=3, ok=True, grund=None, wert=0.25, liste=[1.0, 2.0, 4.0], ganz=[1, 2, 3],
             feld=_feld(4), tief=[dict(z=np.array([1.5, np.nan]), laufzeit_s=1.0), 'text'], laufzeit_s=3.0)
    gleich = kw.vergleich_objekt(a, json.loads(json.dumps(formate._json_wert({k: v for k, v in a.items()
                                                                               if k not in ('feld', 'tief')}))),
                                 ohne=('feld', 'tief'))
    assert gleich['gleich'] and gleich['genau_gleich'] and gleich['auslastung'] == 0.0
    rauschen = dict(a, wert=0.25 * (1 + 1e-13), feld=a['feld'] + 0.3 * _tau(a['feld']), laufzeit_s=9.0,
                    tief=[dict(z=np.array([1.5 + 1e-13, np.nan]), laufzeit_s=2.0), 'text'])
    v = kw.vergleich_objekt(a, rauschen, ohne=('laufzeit_s',))
    assert v['gleich'] and not v['genau_gleich'] and v['stelle_auslastung'] == 'feld'
    assert v['auslastung'] == pytest.approx(0.3, rel=1e-3)
    assert kw.vergleich_objekt(a, rauschen)['abweichungen'] == ['laufzeit_s: größte Abweichung 6, zulässig 9.01e-10 '
                                                                '(1 von 1 Einträgen)', 'tief[0].laufzeit_s: größte '
                                                                'Abweichung 1, zulässig 2.01e-10 (1 von 1 Einträgen)']
    faelle = dict(ausgang='falsifiziert', n=4, ok=False, grund='x', wert=0.26, liste=[1.0, 2.0], ganz=[1, 2, 4],
                  feld=a['feld'] * 1.001, tief=[dict(z=np.array([1.5, 2.0]), laufzeit_s=1.0), 'text'])
    for k, w in faelle.items():
        v = kw.vergleich_objekt(a, dict(a, **{k: w}))
        assert not v['gleich'] and len(v['abweichungen']) == 1 and v['abweichungen'][0].startswith(k), k
    assert kw.vergleich_objekt(a, {k: v for k, v in a.items() if k != 'n'})['abweichungen'][0].startswith(
        '(Wurzel): Schlüssel verschieden')
    assert kw.vergleich_objekt(dict(a=True), dict(a=1))['abweichungen'] == ['a: int statt bool']
    assert kw.vergleich_objekt(dict(a=1), dict(a=1.0))['gleich']        # ganze Zahl gegen gleiche Gleitkommazahl
    assert not kw.vergleich_objekt([1.0, 'a'], [1.0, 'b'])['gleich'] and kw.vergleich_objekt([], [])['gleich']


# ── Zwei Rechenkerne ─────────────────────────────────────────────────────────────────────────────────
KERNE = ('HASWELL', 'SANDYBRIDGE')
SKRIPT = """
import json, sys
sys.path.insert(0, sys.argv[1])
from pcmms_auswertung import formate, kennwerte, pilot
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import kette
tab = kette.kampagne_erzeugen('N01-V1G0', 'L1', kp.Plan(n0=20, n_pilot=20, n_bloecke=2), 7)[2]
print(json.dumps(dict(kennwerte=formate._json_wert(kennwerte.felder(tab.daten)), datenfelder=pilot.daten_sha256(tab))))
"""


def test_kennwerte_derselben_kampagne_unter_zwei_rechenkernen():
    """Dieselbe Kampagne, in zwei Prozessen mit verschiedenen Rechenkernen von OpenBLAS erzeugt (HASWELL und
    SANDYBRIDGE laufen auf jedem x86-64-Prozessor mit AVX2): Die Kennwerte stimmen mit denen dieses Prozesses innerhalb
    der Toleranz überein. Wo OpenBLAS die Vorgabe befolgt, unterscheiden sich die Werte im Rundungsrauschen (gemessen
    am 13.11.2026 in einem Prozess mit dem Kern SkylakeX: Auslastung der Toleranz 2,1·10⁻⁶ gegen HASWELL und gegen
    SANDYBRIDGE, Prüfsummen der Datenfelder verschieden); das wird nicht verlangt, weil eine andere BLAS-Bibliothek
    die Vorgabe nicht kennt."""
    hier = kw.felder(kette.kampagne_erzeugen('N01-V1G0', 'L1', kp.Plan(n0=20, n_pilot=20, n_bloecke=2), 7)[2].daten)
    for kern in KERNE:
        lauf = subprocess.run([sys.executable, '-c', SKRIPT, CODE], capture_output=True, text=True,
                              env=dict(os.environ, OPENBLAS_CORETYPE=kern, OPENBLAS_NUM_THREADS='1'))
        if lauf.returncode < 0:
            pytest.skip(f'Rechenkern {kern} auf diesem Prozessor nicht ausführbar (Signal {-lauf.returncode})')
        assert lauf.returncode == 0, lauf.stderr[-2000:]
        dort = json.loads(lauf.stdout.strip().splitlines()[-1])['kennwerte']
        v = kw.vergleich_felder(hier, dort)
        assert v['gleich'], (kern, v['abweichungen'], v['auslastung'])
