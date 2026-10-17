"""Diagnose E3b/G4 (harness.diagnose_e3b_g4): Auftragsliste und Seeds vor den Rechnungen, Zulässigkeit der Piloten,
Flanken- und Jittergrößen an unabhängigen Grenzfällen, schlanke gegen volle Kette und der Wiederholungsvorrat."""
import csv
import json
import os

import numpy as np

from pcmms_auswertung import formate, gueltigkeit, konventionen as kv, regeln
from pcmms_auswertung.generator import kampagne as kp
from pcmms_auswertung.harness import diagnose_e3b_g4 as dg, kampagnen, kette, neulauf, pruefstand

DOKU = os.path.join(neulauf.WURZEL, dg.DOKU_REL)


def test_auftragsliste_seeds_rolle_und_umfang():
    """120 neue Kampagnen (40 je Referenzsystem) mit eigener Rolle und Basis, volle Ketten nur im vorab festgelegten
    Startsatz (12), Profil und G4-Faktor wie der Altlauf, Werkzeug 8 vollständig, keine Kalibrierkampagnen."""
    a = dg.lies_auftrag()
    g = a['gemeinsam']
    assert g['profil_sha256'] == neulauf.ALT_PROFIL_SHA256 and g['g4_faktor'] == 3.0
    assert g['plan'] == pruefstand.STANDARD['plan'] and g['n_min'] == 18 and g['stufe'] == 'L1'
    assert g['seed_basis'] == 20261017 and g['rolle'] == 'diagnose_g4' and g['prozesse'] <= 4
    jobs = a['auftraege']
    assert sum(len(j['seeds']) for j in jobs) == 120 and sum(len(j['seeds']) for j in jobs if j['voll']) == 12
    for sid, w in dg.SYSTEME:
        js = [j for j in jobs if j['szenario'] == sid]
        ind = sorted(i for j in js for i in j['indizes'])
        assert ind == list(range(40))
        assert [i for j in js if j['voll'] for i in j['indizes']] == [0, 1, 2, 3]
        for j in js:
            assert j['seeds'] == [kampagnen.kampagnen_seed(20261017, 'diagnose_g4', sid, 'L1', i) for i in j['indizes']]
        assert a['systeme'][sid]['werkzeug8'] == w
        w8, sha = neulauf.werkzeug8_laden(a, w)
        assert sha == a['werkzeug8'][w]['inhalt_sha256'] and 'TESTVORGABE' not in w8['c_H1_herkunft'].upper()
        assert dg.zulaessig(*a['systeme'][sid]['zielpilot']['phi'])
    alle = [s for j in jobs for s in j['seeds']]
    assert len(set(alle)) == 120
    alt = {s for j in neulauf.lies_auftrag(neulauf.AUFTRAG)['auftraege'] for s in j.get('seeds', [])}
    assert not alt & set(alle)                                  # keine Kampagne der Neuläufe wiederverwendet
    assert a['umfang']['kalibrierkampagnen'] == 0 and a['umfang']['e3_kampagnen_neu_gerechnet'] == 0


def test_e3_auszug_vollstaendig_und_nachzaehlbar():
    """Der versionierte E3-Auszug: 570 Kampagnen, Prüfsumme der Auftragsliste, Bewertungen je Punkt gleich der
    gerundeten kampagnen_e3.csv der Neuläufe (unabhängig gezählt)."""
    a = dg.lies_auftrag()
    p = os.path.join(neulauf.WURZEL, a['e3']['datei'])
    assert formate.sha256_datei(p) == a['e3']['sha256']
    with open(p, encoding='utf-8') as f:
        neu = list(csv.DictReader(f))
    with open(os.path.join(neulauf.WURZEL, 'docs/ap13_neulaeufe_2026-10-17/kampagnen_e3.csv'), encoding='utf-8') as f:
        alt = list(csv.DictReader(f))
    assert len(neu) == len(alt) == 570
    zaehle = lambda z, s: sorted((r['punkt'], r[s]) for r in z)                                    # noqa: E731
    assert zaehle(neu, 'bewertung') == zaehle(alt, 'E3_bewertung')
    for r, q in zip(sorted(neu, key=lambda r: (r['punkt'], int(r['kampagne']))),
                    sorted(alt, key=lambda r: (r['punkt'], int(r['kampagne'])))):
        assert r['seed'] == q['seed'] and np.isclose(float(r['q_Z']), float(q['q_Z']), rtol=1e-5)


def test_zulaessigkeit_der_piloten():
    """A7 mit dem Mindestabstand der registrierten Piloten: diese genau an der Grenze zulässig, Schnittpunkte nie."""
    for p2, p3 in kv.PILOTEN:
        assert dg.zulaessig(p2, p3)
        assert np.isclose(np.abs(dg.abstaende(p2, p3) - 120).min(), 10.0)
    assert not any(dg.zulaessig(p2, kv.SCHNITT_PHI3) for p2 in kv.SCHNITT_PHI2)
    assert dg.zulaessig(130.0, 262.0) and dg.zulaessig(100.0, 230.0)
    assert not dg.zulaessig(121.0, 250.0) and not dg.zulaessig(100.0, 231.0)


def test_steigung_und_jitterstreuung_grenzfaelle():
    """Linear: Steigungen |a|, |b| und √(2·Var(a·s₂z₁ + b·s₃z₂)); symmetrischer Knick −g·|φ₂ − c|: einseitige
    RMS-Steigung g, Jitterstreuung √(2(1 − 2/π))·g·s (Betrag einer Normalverteilung); konstant: null."""
    a, b, s = 0.03, -0.02, (0.045, 0.05)
    lin = lambda p2, p3: a * p2 + b * p3                                                           # noqa: E731
    assert np.allclose(dg.steigung(lin, 120.0, 240.0), [abs(a), abs(b)])
    viele = lambda P: a * np.asarray(P)[:, 1] + b * np.asarray(P)[:, 2]                           # noqa: E731
    z = dg._ziehungen()
    soll = np.sqrt(2 * np.var(a * s[0] * z[:, 0] + b * s[1] * z[:, 1], ddof=1))
    assert np.isclose(dg.jitter_streuung(viele, [(120.0, 240.0)], s)[0], soll, rtol=1e-12)
    assert np.isclose(soll, np.sqrt(2 * (a * a * s[0] ** 2 + b * b * s[1] ** 2)), rtol=0.1)
    g = 0.05
    knick = lambda P: -g * np.abs(np.asarray(P)[:, 1] - 120.0)                                    # noqa: E731
    assert np.allclose(dg.steigung(lambda p2, p3: knick([[0, p2, p3]])[0], 120.0, 240.0), [g, 0.0])
    sj = dg.jitter_streuung(knick, [(120.0, 240.0)], s)[0]
    assert np.isclose(sj, np.sqrt(2 * (1 - 2 / np.pi)) * g * s[0], rtol=0.1)
    assert dg.jitter_streuung(lambda P: np.zeros(len(P)), [(110.0, 250.0)], s)[0] == 0.0


def test_kampagne_schlank_gleich_voll_und_wiederholungsvorrat():
    """Kleiner Plan: die schlanke Gültigkeitsprüfung gleicht der vollen Kette (im Rechenmodul geprüft); die aus D_N,
    D_F, σ_Δ und ⟨N⟩ nachgerechnete produktive G4-Entscheidung gleicht der gespeicherten, auch im Vorrat; der Vorrat
    hat zwei Läufe je Platz und lässt die ursprünglichen Läufe unverändert."""
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, h3_mc=200, eps_ctrl_datensaetze=200)
    plan = kp.Plan(n0=20, n_pilot=20, n_bloecke=4)
    seed = dg.kampagnen_seeds('N01-V1G0', 1)[0]
    w8 = kette.testvorgabe_werkzeug8()
    v = dg.kampagne(('N01-V1G0', 0, seed, prof, plan, 3, w8, True, (130.0, 262.0)))
    s = dg.kampagne(('N01-V1G0', 0, seed, prof, plan, 3, w8, False, (130.0, 262.0)))
    fv, fs = v['felder'], s['felder']
    for k in fs:
        assert np.array_equal(fv[k], fs[k], equal_nan=True), k
    assert v['voll_kette']['gueltigkeit_gleich_schlank'] and s['voll_kette'] is None
    n = 21 * 4
    assert np.array_equal(np.bincount(fs['laeufe_rolle']), [n, n, n])
    assert np.array_equal(np.bincount(fs['laeufe_konf'][:n]), np.full(21, 4))
    sd = s['sigma_delta']['K']
    boden = gueltigkeit.RUNDUNG_REL * np.abs(fs['laeufe_Nmittel'])
    g4 = (np.abs(fs['laeufe_DN']) > 3 * sd['N'] + boden) | (np.abs(fs['laeufe_DF']) > 3 * sd['F'] + boden)
    assert np.array_equal(g4, fs['laeufe_regeln'][:, dg.REGELN.index('G4')] == 1)
    gueltig = ~(fs['laeufe_regeln'] == 1).any(1)
    assert np.array_equal(gueltig, fs['laeufe_gueltig'])
    assert fs['ziel_DF'].shape == (dg.N_ZIELPILOT,) and fs['pilot_DF'].shape == (60,)
    assert fs['jitter_phase0'].shape == (21 + 3 + 1,) and (fs['jitter_phase0'] > 0).all()


def test_rechencode_ohne_berichtsteil_und_parallel_mit_funktion():
    assert neulauf.rechencode_sha256() == neulauf.rechencode_sha256(neulauf.NICHT_RECHENCODE)
    assert set(neulauf.NICHT_RECHENCODE) < set(dg.NICHT_RECHENCODE)
    assert 'harness/diagnose_e3b_g4_bericht.py' in dg.NICHT_RECHENCODE
    assert kampagnen._parallel([-1, -2, 3], 2, fn=abs) == [1, 2, 3]


def test_e3_zeilen_klassen():
    """Zusammenfassung von E3a je Kampagne: auffällig (|x| − z_B·u > 0,1°), über der Schwelle (|x| + 1,645·u > 0,1°)."""
    sw = dict(phase_grad=0.1, q_tol=5.8e-4)
    e3a = np.array([[0.05, 0.01, 0.009], [0.09, 0.01, 0.009], [0.2, 0.02, 0.02]])
    lauf = dict(befunde=[dict(seed=1, E3=dict(e3a=e3a, e3b=np.array([4e-4, 2e-4, 2e-4]), z_B=3.0, m=7,
                                              bewertung='auffällig', status='x'), E3_grund=None),
                         dict(seed=2, E3=None, E3_grund='keine E3-Auswertung: T(kω) fehlt')])
    z = dg._e3_zeilen('P/L1', lauf, sw)
    assert z[0]['e3a_auffaellig'] == 1 and z[0]['e3a_ueber_schwelle'] == 2 and z[0]['n_e3a'] == 3
    assert np.isclose(z[0]['e3a_max_ober_grad'], 0.2 + 1.645 * 0.02)
    assert np.isclose(z[0]['e3a_max_unter_grad'], 0.2 - 3 * 0.02) and z[0]['status'] is None
    assert z[1]['E3_grund'].startswith('keine E3-Auswertung') and 'bewertung' not in z[1]
    assert json.dumps(sorted(z[0]))                                  # Spalten serialisierbar
