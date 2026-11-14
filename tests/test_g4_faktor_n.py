"""k(n) der Lⱼ-Schwelle (g4.faktor_n) bei kleinen Stichproben: Korrektur des Suchintervalls vom 14.11.2026.

Die Zieldefinition (Präregistrierung A9.2) bleibt, wie sie ist: E_σ̂[2·Φ̄(k·σ̂/σ)] = 2·Φ̄(3) für σ̂ = 1,4826·MAD aus n
Normalwerten, gerechnet mit festen Ziehungen. Bis zur Korrektur suchte faktor_n die Lösung nur zwischen 3 und 12 und
brach für n = 3, 4, 5 ab, weil sie dort darüber liegt. Geprüft wird:
- die Lösung für n = 3, 4, 5 an einer von faktor_n unabhängig nachgebildeten Zielfunktion;
- die Bitgleichheit mit der alten Suche überall, wo sie rechnete (n = 6 … 30 und 60);
- die Suche des Intervalls selbst, auch ohne Vorzeichenwechsel;
- die unveränderte Untergrenze n ≥ 3;
- Lⱼ-Schwellen und der Teil-B-Block mit drei bis fünf gültigen Läufen.

Die Zahlen gelten für die festen Ziehungen des Codes (SEED_ZIEHUNGEN, 40 000 Ziehungen). Geprüft wird die Rechnung,
keine Rate an Daten."""
import numpy as np
import pytest
from scipy import optimize, special, stats

from pcmms_auswertung import g4, gueltigkeit
from test_g4_2026_11 import DD, JIT, K, NBAR, NEU, _lg, _mad, _phase0

ALT = (g4.FAKTOR, 4 * g4.FAKTOR)                             # Suchintervall vor der Korrektur: 3 bis 12
KLEIN = {3: 324.750657, 4: 26.450018, 5: 23.721852}          # k(n) mit den festen Ziehungen


def _ziel(n, faktor=g4.FAKTOR, n_mc=40_000, seed=g4.SEED_ZIEHUNGEN):
    """Zielfunktion nach A9.2, unabhängig von g4.faktor_n nachgebildet: Rate über die festen Ziehungen minus
    2·Φ̄(faktor); dazu die Schätzwerte σ̂ der Ziehungen."""
    x = np.random.default_rng(seed + n).standard_normal((n_mc, n))
    s = 1.4826 * np.median(np.abs(x - np.median(x, 1, keepdims=True)), 1)
    a = float(2 * stats.norm.sf(faktor))
    return (lambda k: float(np.mean(special.erfc(k * s / np.sqrt(2)))) - a), s


@pytest.mark.parametrize('n', sorted(KLEIN))
def test_kleine_stichproben_loesen_die_zielgleichung(n):
    """n = 3, 4, 5: Die Lösung liegt über der alten Obergrenze 12 (dort ist die Rate noch über dem Ziel, die alte
    Suche bricht ab) und erfüllt die Zielgleichung; links von ihr liegt die Rate über, rechts unter dem Ziel."""
    f, s = _ziel(n)
    assert f(ALT[0]) > f(ALT[1]) > 0 and s.mean() < 1
    with pytest.raises(ValueError):
        optimize.brentq(f, *ALT, xtol=1e-10)
    k = g4.faktor_n(n)
    assert k > ALT[1] and k == pytest.approx(KLEIN[n], rel=1e-6)
    assert abs(f(k)) < 1e-12
    assert f(k * (1 - 1e-6)) > 0 > f(k * (1 + 1e-6))


def test_wo_die_alte_suche_rechnete_bleibt_das_ergebnis_bitgleich():
    """n = 6 … 30 und 60: Die Lösung liegt im alten Intervall; faktor_n liefert denselben Wert wie die Suche
    zwischen 3 und 12 (==, nicht genähert). An der Untergrenze liegt die Rate über dem Ziel (σ̂ im Mittel unter 1)."""
    for n in list(range(6, 31)) + [60]:
        f, s = _ziel(n)
        assert f(ALT[0]) > 0 > f(ALT[1]) and s.mean() < 1, n
        assert g4.faktor_n(n) == optimize.brentq(f, *ALT, xtol=1e-10), n
    assert [round(g4.faktor_n(n), 2) for n in (6, 7, 20, 60)] == [11.68, 11.23, 4.30, 3.38]


def test_suchintervall():
    """Unverändert, wenn die Lösung im übergebenen Intervall liegt (auch genau an seinem oberen Rand); sonst wird die
    obere Grenze verdoppelt und die untere nachgezogen; ohne Vorzeichenwechsel eine Meldung statt einer Endlosschleife
    (nan zählt nicht als Vorzeichenwechsel)."""
    stellen = []

    def f(grenze):
        def g(k):
            stellen.append(k)
            return grenze - k
        return g
    assert g4._suchintervall(f(10.0), 3.0, 12.0, 'x') == (3.0, 12.0) and stellen == [12.0]
    assert g4._suchintervall(f(12.0), 3.0, 12.0, 'x') == (3.0, 12.0)
    del stellen[:]
    assert g4._suchintervall(f(100.0), 3.0, 12.0, 'x') == (96.0, 192.0)
    assert stellen == [12.0, 24.0, 48.0, 96.0, 192.0]
    with pytest.raises(ValueError, match='Probe: kein Vorzeichenwechsel bis 96'):
        g4._suchintervall(lambda k: 1.0, 3.0, 12.0, 'Probe', verdopplungen=3)
    with pytest.raises(ValueError, match='kein Vorzeichenwechsel'):
        g4._suchintervall(lambda k: float('nan'), 3.0, 12.0, 'x')


@pytest.mark.parametrize('n', (2, 1, 0))
def test_unter_drei_werten_bleibt_k_abgelehnt(n):
    with pytest.raises(ValueError, match='n ≥ 3'):
        g4.faktor_n(n)


def test_lj_schwellen_mit_drei_bis_fuenf_laeufen():
    """Schwelle k(n₀ⱼ)·σ_Δ,X je Modul mit n₀ⱼ = 3, 4, 5; der Pooling-Vergleich rechnet mit k(12)."""
    sd = {g: dict(N=0.001, F=0.002) for g in ('L1', 'L2', 'L3')}
    n0 = dict(L1=3, L2=4, L3=5)
    r = g4.lj_schwellen(sd, n0, {g: dict(N=1.0, F=1.0) for g in sd})
    for g, n in n0.items():
        k = g4.faktor_n(n)
        assert r['n_abhaengig'][g] == dict(faktor=k, n=n, N=k * 0.001, F=k * 0.002)
    for x in ('N', 'F'):
        p = r['pooling'][x]
        assert p['n'] == 12 and p['faktor'] == g4.faktor_n(12) and p['bartlett']['p'] > 0.99


@pytest.mark.parametrize('n', (6, 7, 8))
def test_teil_b_block_mit_drei_bis_fuenf_gueltigen_l1_laeufen(n):
    """n Lⱼ-Läufe je Modul, bei L1 sind drei ungültig (bleiben drei, vier, fünf): Der Block nr2.g4 wird gebildet –
    bis zur Korrektur brach Teil B hier ab – und k(n₀ⱼ) gehört zur Zahl der gültigen Läufe, deren MAD es skaliert."""
    t, ungueltig = _phase0(n=n)
    konf = [dict(id='S120', phi=[0.0, 120.0, 240.0], einstellung=1)]
    blk = g4.teil_b_block(t, ungueltig, NBAR, DD, np.zeros(3), JIT, K, konf, _lg(), NEU)
    lj = blk['lj']['n_abhaengig']
    assert [lj[g]['n'] for g in ('L1', 'L2', 'L3')] == [n - 3, n, n]
    assert all(v['faktor'] == g4.faktor_n(v['n']) for v in lj.values())
    DN, DF = gueltigkeit.fuenftel_differenzen(t, K)
    gut = np.array([k['lauf_id'] not in ungueltig for k in t.koepfe])
    l1 = np.array([k['laufart'] == 'L' and k['modul'] == 1 for k in t.koepfe])
    assert lj['L1']['N'] == pytest.approx(g4.faktor_n(n - 3) * _mad(DN[l1 & gut]), rel=1e-12)
    assert lj['L1']['F'] == pytest.approx(g4.faktor_n(n - 3) * _mad(DF[l1 & gut]), rel=1e-12)
    for x in ('N', 'F'):
        p = blk['lj']['pooling'][x]
        assert p['n'] == 3 * n - 3 and p['faktor'] == g4.faktor_n(3 * n - 3)
    assert blk['b_plus'] is not None
