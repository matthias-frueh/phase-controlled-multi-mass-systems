"""Berichtsteil der Diagnose E3b/G4 (harness.diagnose_e3b_g4_bericht): Hilfsrechnungen an unabhängigen Grenzfällen und
Nachzählung der berichteten Zähler aus den versionierten kompakten Ergebnissen."""
import csv
import math
import os

import numpy as np
import pytest

from pcmms_auswertung import formate, konventionen as kv, regeln
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import diagnose_e3b_g4 as dg, diagnose_e3b_g4_bericht as db, kette, neulauf

DOKU = os.path.join(neulauf.WURZEL, dg.DOKU_REL)


def _lies(name):
    with open(os.path.join(DOKU, name), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _ergebnisse():
    return formate.lies_objekt(os.path.join(DOKU, 'ergebnisse'), 'bewertung')[1]


def test_reserve_und_intervalle_grenzfaelle():
    assert db.r_plus2(0.0) == 2 and db.r_plus2(1 / 60) == 3 and db.r_plus2(4 / 60) == 4
    assert np.isclose(db.obere_grenze(0, 60), 1 - 0.2 ** (1 / 60)) and db.obere_grenze(60, 60) == 1.0
    lo, hi = db.wilson(0, 40)
    assert lo == 0.0 and 0.08 < hi < 0.09
    lo, hi = db.wilson(40, 40)
    assert hi == 1.0 and 0.91 < lo < 0.92
    assert db.p_vollstaendig(18, 0.0) == 1.0
    assert np.isclose(db.p_vollstaendig(18, 0.1), 0.9 ** (18 * 21))
    assert np.isclose(db.p_vollstaendig(18, 0.1, wiederholungen=2), (1 - 1e-3) ** (18 * 21))
    assert db.r_gemeinsam(0.0) == 0
    r = [db.r_gemeinsam(p) for p in (0.01, 0.02, 0.05, 0.1)]
    assert r == sorted(r) and r[0] >= 1                         # monoton; ohne Ausfälle bräuchte man keine Reserve
    assert db.p_vollstaendig(18 + r[2], 0.05) >= 0.95 > db.p_vollstaendig(17 + r[2], 0.05)


def test_block_des_n_min_ten_gueltigen_platzes():
    bl = np.tile(np.arange(1, 25), 3)
    konf = np.repeat(np.arange(3), 24)
    ok = np.ones(72, bool)
    ok[24 + np.array([2, 4])] = False                            # Punkt 1: Blöcke 3 und 5 ungültig
    ok[48:48 + 7] = False                                        # Punkt 2: nur 17 gültige
    b = db.block_nmin(ok, konf, bl, punkte=3)
    assert b.tolist() == [18, 20, 25]
    assert (b <= 24).tolist() == [True, True, False]


def test_e3_klassen_an_den_grenzen():
    sw = dict(phase_grad=0.1, q_tol=5.8e-4)
    zeile = lambda q, u, aa=0, au=0: dict(z_B='3.0', q_Z=repr(q), u_q_Z=repr(u), e3a_auffaellig=str(aa),  # noqa: E731
                                          e3a_ueber_schwelle=str(au))
    u = 1e-4
    assert db.e3_klassen(zeile(5.8e-4 - 1.645 * u, u), sw)[1] == 'unauffällig'                # Grenze ≤ eingeschlossen
    assert db.e3_klassen(zeile(5.8e-4 - 1.645 * u + 1e-9, u), sw)[1] == 'unbestimmt'
    assert db.e3_klassen(zeile(5.8e-4 + 3 * u, u), sw)[1] == 'unbestimmt'                     # Grenze > ausgeschlossen
    assert db.e3_klassen(zeile(5.8e-4 + 3 * u + 1e-9, u), sw)[1] == 'auffällig'
    assert db.e3_klassen(zeile(1e-5, u, au=1), sw) == ('unbestimmt', 'unauffällig', 'unbestimmt')
    assert db.e3_klassen(zeile(1e-5, u, aa=1, au=1), sw)[2] == 'auffällig'


def test_nullresiduum_rayleigh_und_monotonie():
    """Betrag des komplexen Nullresiduums: Mittel √(π/2), Median √(2 ln 2) (Rayleigh); P(unauffällig) steigt mit
    q_tol/s von 0 auf 1, P(auffällig) fällt."""
    r = db.nullresiduum(3.0, n=4000, B=200)
    assert np.isclose(r['q_mittel'], math.sqrt(math.pi / 2), rtol=0.03)
    assert np.isclose(r['q_median'], math.sqrt(2 * math.log(2)), rtol=0.04)
    pu = [g['p_unauffaellig'] for g in r['gitter']]
    pa = [g['p_auffaellig'] for g in r['gitter']]
    assert pu == sorted(pu) and pu[0] == 0.0 and pu[-1] > 0.99
    assert pa == sorted(pa, reverse=True) and pa[-1] == 0.0
    assert np.isclose(np.mean(r['_ober'] <= r['t_stern']), 0.8, atol=1e-3)
    assert 0.6 < r['u_median'] < 1.0                              # Streuung des Betrags kleiner als s


def test_amplitudentrend_exakt_ueber_homogenitaet():
    """F_min − ⟨N⟩ ist homogen vom Grad 1 in den Harmonischen: (1 + ε)·N_k ergibt (1 + ε)·F; daraus
    D_F′ = D_F + ε·F_letztes ohne Neuerzeugung."""
    rng = np.random.default_rng(1)
    Nk = rng.standard_normal((50, 9)) + 1j * rng.standard_normal((50, 9))
    for eps in (0.002, 0.01, -0.05):
        assert np.allclose(kv.fmin_rel((1 + eps) * Nk), (1 + eps) * kv.fmin_rel(Nk), rtol=0, atol=1e-12)


def test_standardisierung_nie_unter_pilot_und_produktiv_gleich_gespeichert():
    """v2 liegt nie unter σ_P (v0k); bei gleichem k ist v0k = v0; v0 gleicht der gespeicherten Entscheidung (die
    Prüfung steckt in kampagne_varianten)."""
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, h3_mc=200, eps_ctrl_datensaetze=200)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=4)
    b = dg.kampagne(('N01-V1G0', 0, dg.kampagnen_seeds('N01-V1G0', 1)[0], prof, plan, 3,
                     kette.testvorgabe_werkzeug8(), False, (130.0, 262.0)))
    sP = db.mad(b['felder']['pilot_DF'])
    s2 = db._sigma_F(b, 'v2', None)
    assert (s2 >= sP - 1e-15).all() and s2.max() > sP
    assert np.isclose(db._sigma_F(b, 'v0k', None)[0], b['sigma_delta']['K']['F'])
    b['felder']['jitter_phase0'] = np.zeros(25)                  # keine Jittervorhersage: v2 = v0k
    assert np.allclose(db._sigma_F(b, 'v2', None), sP)
    v = db.kampagne_varianten(b, np.full(21, sP))
    assert v['v0']['G4'].sum() == (b['felder']['laeufe_regeln'][:84, dg.REGELN.index('G4')] == 1).sum()
    assert (v['v0']['gueltig_w'] >= v['v0']['gueltig']).all()


@pytest.mark.skipif(not os.path.exists(os.path.join(DOKU, 'ergebnisse.json')), reason='ergebnisse.json fehlt')
def test_zaehler_aus_den_kompakten_ergebnissen_nachzaehlbar():
    """Vollständigkeit (n = 24, n_min + r(p̂), ohne/mit Wiederholung), G4-Raten und E3-Zähler aus den CSV-Dateien gleich
    ergebnisse.json; Prüfsummen der CSV-Dateien wie dort vermerkt."""
    z = _ergebnisse()
    for name, h in z['dateien'].items():
        assert formate.sha256_datei(os.path.join(DOKU, name)) == h
    kk, kz = _lies('g4_konfigurationen.csv'), _lies('g4_kampagnen.csv')
    for sid, _ in dg.SYSTEME:
        n_r = {int(r['kampagne']): int(r['n_plus2']) for r in kz if r['system'] == sid}
        for v in db.VARIANTEN:
            x = z['g4']['systeme'][sid]['varianten'][v]
            je = {}
            for r in kk:
                if r['system'] == sid:
                    je.setdefault(int(r['kampagne']), []).append(r)
            assert len(je) == 40 and all(len(y) == 21 for y in je.values())
            unv = sum(1 for y in je.values() if min(int(r[f'gueltig_{v}']) for r in y) < 18)
            unv_w = sum(1 for y in je.values() if max(int(r[f'b18w_{v}']) for r in y) > 24)
            voll = sum(1 for i, y in je.items() if max(int(r[f'b18_{v}']) for r in y) <= n_r[i])
            voll_w = sum(1 for i, y in je.items() if max(int(r[f'b18w_{v}']) for r in y) <= n_r[i])
            assert (unv, unv_w) == (x['unvollstaendig_24'], x['unvollstaendig_24_w'])
            assert (voll, voll_w) == (x['vollstaendig_n_plus2']['ohne'], x['vollstaendig_n_plus2']['mit'])
            g = [sum(int(r[f'G4_{v}']) for r in y) / sum(int(r['laeufe']) for r in y) for y in je.values()]
            assert np.isclose(np.mean(g), x['G4'][0])
    rows = _lies('e3_pruefgroessen.csv')
    for p in z['e3']['punkte']:
        R = [r for r in rows if r['punkt'] == p['punkt']]
        assert sum(r['bewertung'] == 'unauffällig' for r in R) == p['e3']['unauffällig']
        assert sum(float(r['u_q_Z']) > 5.8e-4 / 1.645 for r in R) == p['u_ueber_grenze']
    a4 = z['e3']['a4l1']['zerlegung']
    assert (a4['unsicherheit_allein'], a4['punktschaetzer'], a4['unauffaellig']) == (27, 159, 14)


def test_pilotsuche_begruendung_am_versionierten_k12_ablauf():
    k = db.k12_begruendung()
    assert k['alt'] == 'kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max'
    assert k['klassen'] == {'aufrufgrenze': 26, 'bedingung': 2}
    assert k['neu'].startswith('an 2 Paaren (k, T_a) erreicht kein simulierter Kandidat')
    assert '26 Paare wegen der Grenze der Planungsaufrufe nicht simuliert' in k['neu']
    assert k['neu'].endswith('kein Nachweis der Unzulässigkeit außerhalb dieser Suche')
    assert 'n_max' not in k['neu']                                   # das Zeitbudget band nicht
