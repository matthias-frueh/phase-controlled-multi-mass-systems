"""Regelstand 2026-11 (Auftrag vom 20.10.2026): neue Profile, P0.7-Anordnung, Ablauffassung; die historischen Profile,
Pläne und Verfahrenskennungen bleiben bitgleich."""
import numpy as np
import pytest

from pcmms_auswertung import ablauf, regeln, verfahren as vf
from pcmms_auswertung.generator import kampagne as kp

# Prüfsummen der historischen Profile, wie sie bis PR #23 gespeichert wurden (unverändert, bitgleich)
HISTORISCH_SHA = {'AF-2026-10': '31afc483bdc9', 'ENTW-2026-10': '4032bc56396d'}


def test_historische_profile_bitgleich_und_aktueller_standard():
    for name, sha in HISTORISCH_SHA.items():
        assert regeln.profil(name).sha256().startswith(sha)
        assert regeln.ist_historisch(regeln.profil(name))
    assert regeln.profil().id == 'ENTW-2026-11' == regeln.STANDARD
    assert regeln.stand(regeln.profil('AF-2026-11').mit_reduktion(bootstrap_B=200)) == '2026-11'


def test_neue_regeln_nur_im_stand_2026_11_und_gekennzeichnet():
    af10, af11, entw11 = regeln.profil('AF-2026-10'), regeln.profil('AF-2026-11'), regeln.profil('ENTW-2026-11')
    neu = set(af11.regeln) - set(af10.regeln)
    assert {'ablauf.fassung', 'ablauf.bezugseroeffnung', 'p0.anordnung', 'g4.verfahren', 'e3.grenzen',
            'harness.mengen', 'harness.wiederaufnahme', 'planung.reserve_ziel'} <= neu
    for rid in neu:
        r = af11.eintrag(rid)
        assert r.status in (regeln.AF, regeln.TD) and r.verfuegbar(), rid
        if r.status == regeln.AF:
            assert '20.10.2026' in r.herkunft, rid
    # vom Auftrag entschieden: in AF-2026-11 verfügbar, im historischen AF offen
    for rid in ('e3.schwellen', 'e3.pruefzahl', 'e3.rueckfall', 'e3.pruefmenge', 'e3.e3b_form', 'h1.c_rauschmodelle'):
        assert af11.eintrag(rid).status == regeln.AF and af11.hat(rid)
        assert not af10.hat(rid)
        assert entw11.eintrag(rid).status == regeln.AF
    assert af11.wert('e3.pruefzahl') == 43 and af11.wert('ablauf.fassung') == 'ablauf-4'
    # nicht mitentschieden: δ_H2, δ_H3 bleiben offen bzw. Entwicklungsprüffall
    for rid in ('h2.delta_grad', 'h3.delta', 'planung.zielfunktion'):
        assert not af11.hat(rid) and entw11.eintrag(rid).status == regeln.EP


def test_p07_anordnung_hoechstens_zwoelf_andere_laeufe_zwischen_referenzlaeufen():
    for n0, n_pilot in ((20, 20), (20, 60), (40, 20), (1, 1)):
        plan = kp.Plan(n0=n0, n_pilot=n_pilot)
        p0 = [l for l in kp.laufplan(plan, np.random.default_rng(3)) if l['phase'] == 0]
        idx = [i for i, l in enumerate(p0) if l['laufart'] == 'R']
        abst = np.diff(idx) - 1
        andere = len(p0) - len(idx)
        assert idx[0] == 0 and idx[-1] == len(p0) - 1
        assert abst.max() <= plan.ref_abstand and abst.max() - abst.min() <= 1
        assert len(idx) >= min(plan.ref_min_p0, andere + 1)
    p0 = [l for l in kp.laufplan(kp.Plan(), np.random.default_rng(3)) if l['phase'] == 0]
    assert sum(l['laufart'] == 'R' for l in p0) == 42 and len(p0) == 162


def test_historische_anordnung_unveraendert_und_herkunft_bitgleich():
    alt = kp.Plan(p0_anordnung='historisch')
    p0 = [l for l in kp.laufplan(alt, np.random.default_rng(3)) if l['phase'] == 0]
    idx = [i for i, l in enumerate(p0) if l['laufart'] == 'R']
    assert len(idx) == 61 and set(np.diff(idx) - 1) == {2}
    # gespeicherte Pläne ohne das Feld stammen aus der Zeit bis PR #23
    d = kp.plan_dict(alt)
    assert 'p0_anordnung' not in d and kp.plan_aus_dict(d) == alt
    assert kp.plan_dict(kp.Plan())['p0_anordnung'] == 'p07' and kp.plan_aus_dict(kp.plan_dict(kp.Plan())) == kp.Plan()
    with pytest.raises(ValueError, match='unbekannt'):
        kp.Plan(p0_anordnung='gleichmaessig')
    # Phase 1 hängt nicht von der Phase-0-Anordnung ab
    p1a = [l['konfiguration']['id'] for l in kp.laufplan(alt, np.random.default_rng(5)) if l['phase'] == 1]
    p1b = [l['konfiguration']['id'] for l in kp.laufplan(kp.Plan(), np.random.default_rng(5)) if l['phase'] == 1]
    assert p1a == p1b


def test_ablauffassung_in_kennung_und_keine_stille_fortsetzung():
    assert vf.ZUSTAND.fassung == ablauf.VERSION == 'ablauf-4'
    assert vf.ZUSTAND_HISTORISCH.kennung()['ablauf_version'] == 'ablauf-3'
    assert vf.aus_kennung(vf.ZUSTAND_HISTORISCH.kennung()) == vf.ZUSTAND_HISTORISCH
    assert vf.aus_kennung(vf.ZUSTAND.kennung()) == vf.ZUSTAND
    assert vf.STATISCH.kennung()['ablauf_version'] is None
    with pytest.raises(ValueError, match='unbekannt'):
        vf.Verfahren('plan', 'zustand', ablauf.Ablaufoptionen(), 'ablauf-2')
    with pytest.raises(ValueError, match='keine Ablauffassung'):
        vf.Verfahren('plan', 'statisch', None, 'ablauf-4')
    with pytest.raises(ablauf.AblaufFehler, match='unbekannt'):
        ablauf.Ablauf([], None, None, None, None, ablauf.Ablaufoptionen(), 1.0, 1.0, fassung='ablauf-9')


def test_vorgaben_ohne_plan_und_verfahren_nach_dem_profil():
    """Ohne übergebenen Plan bzw. Verfahren rechnen historische Profile mit der Anordnung „historisch“ und ablauf-3
    (Ergebnisse bis PR #23), die Profile 2026-11 mit P0.7 und ablauf-4; ein ausdrücklicher Plan gilt, wie er ist."""
    import argparse
    from pcmms_auswertung import cli, verfahren as vf
    from pcmms_auswertung.generator import kampagne as kp
    alt, neu = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=100), regeln.profil('AF-2026-11')
    assert kp.plan_vorgabe(alt).p0_anordnung == 'historisch' and kp.plan_vorgabe(neu).p0_anordnung == 'p07'
    assert kp.plan_vorgabe(alt, p0_anordnung='p07').p0_anordnung == 'p07' and kp.plan_vorgabe().p0_anordnung == 'p07'
    assert vf.zustand_fuer(alt) == vf.ZUSTAND_HISTORISCH and vf.zustand_fuer(neu) == vf.ZUSTAND
    a = argparse.Namespace(n0=20, n_pilot=20, n_bloecke=4, n_zyklen=100, p0_anordnung=None, verfahren='zustand')
    assert cli._plan(a, alt).p0_anordnung == 'historisch' and cli._plan(a, neu).p0_anordnung == 'p07'
    assert cli._verfahren(a, alt).fassung == 'ablauf-3' and cli._verfahren(a, neu).fassung == 'ablauf-4'
    a.p0_anordnung = 'p07'
    assert cli._plan(a, alt).p0_anordnung == 'p07'
