"""Planungshaken im Regelstand 2026-11 (Auftrag vom 20.10.2026, b2): Zielfunktion aus der Regel, Reservebedingung 0,95
mit r += 1 bis zusatz_max und Grund „Reservegrenze“, Zeitbilanz im Kandidaten, Ablauf ablauf-4 als Vorgabe; der
historische Stand bleibt unverändert. Die Kalibrier- und Prüfsimulation ist eine Attrappe (keine Kampagnen). Den Fall
der Phase-0-Modellquelle (statischer Laufplan, Bedingung nicht prüfbar) prüft test_d_planung_phase0."""
import pytest

from pcmms_auswertung import regeln, verfahren as vf
from pcmms_auswertung.generator import kampagne as kp, szenarien
from pcmms_auswertung.harness import planung

NEU = regeln.profil('ENTW-2026-11')
ALT = regeln.profil('ENTW-2026-10')
PLAN = kp.Plan(n0=20, n_pilot=20, n_bloecke=4)
ORAKEL = 'szenario_orakel'          # Szenariopfad im Stand 2026-11 nur ausdrücklich (Rauschquelle des Hakens)


def _mit(profil, rid, wert):
    r = profil.eintrag(rid)
    neu = regeln.Regel(r.id, r.gegenstand, r.fundstelle, r.status, wert, r.herkunft, r.wirkung)
    return regeln.Regelprofil(profil.id, 'Test', [neu if x.id == rid else x for x in profil.regeln.values()],
                              profil.reduktion)


def _aufruf(p_hat=0.0, n_max=None):
    m = szenarien.modell('N01-A4', 'L1', plan=PLAN)
    return dict(k=9, N_z=PLAN.n_zyklen, T_a=PLAN.n_zyklen / m.system.f, T_e=1.0, T_lauf=PLAN.T_lauf, p_hat=p_hat,
                n_max=n_max, f=m.system.f, zeit=dict(d=1, N_K=21, N_I=0), s_q=dict(nu_p=59))


def _attrappe(monkeypatch, erfuellt_ab=None, P=0.9, geprueft=True):
    """kalibrieren-Attrappe: Reservebedingung erfüllt ab n_bloecke ≥ erfuellt_ab (None: nie)."""
    gesehen = []

    def kal(sid, stufe, profil, n_kal, n_pruef, seed, plan=None, n_min=None, verfahren=None, **kw):
        gesehen.append(dict(n_bloecke=plan.n_bloecke, seed=seed, verfahren=verfahren))
        ok = erfuellt_ab is not None and plan.n_bloecke >= erfuellt_ab
        rz = (dict(geprueft=True, erfuellt=ok, rate=1.0 if ok else 0.5, zaehler=2 if ok else 1, nenner=2)
              if geprueft else dict(geprueft=False, grund='nur mit Ablauf ablauf-4 und gegebenem n_min'))
        return dict(gemeinsame_bestaetigung=dict(rate=P, mc_se=0.0, zaehler=9, nenner=10), c_H1=dict(wert=3.7),
                    h2=dict(schluessel='perzentil_0.95'), pruefung=None, reserve_ziel=rz,
                    zeitbilanz=dict(terme={}, nenner=2))
    monkeypatch.setattr(planung.kalibrierung, 'kalibrieren', kal)
    return gesehen


def test_reserve_wird_erhoeht_bis_die_bedingung_erfuellt_ist(monkeypatch):
    gesehen = _attrappe(monkeypatch, erfuellt_ab=2 + 2 + 3)          # n_min = 2, r = 2 → drei Erhöhungen
    out = planung.haken('N01-A4', 'L1', NEU, 2, 2, 5, (2,), (20,), PLAN, rauschquelle=ORAKEL)(_aufruf())
    c = out['kandidaten'][0]
    assert [g['n_bloecke'] for g in gesehen] == [4, 5, 6, 7] and len({g['seed'] for g in gesehen}) == 1
    assert c['reserve_r'] == 5 and c['reserve_zusatz'] == 3 and [x['reserve_r'] for x in c['reserve_verlauf']] == \
        [2, 3, 4]
    assert c['erfuellt'] and c['plan_simuliert']['n_bloecke'] == 7 and out['n_min'] == 2
    assert c['messzeit']['zeitbilanz'] == dict(terme={}, nenner=2)
    assert out['zielfunktion'] == dict(fassung='a', N_K=21) and out['reserve_ziel_regel']['anteil'] == 0.95
    assert gesehen[0]['verfahren'] == vf.ZUSTAND and out['verfahren'] == vf.ZUSTAND.kennung()   # ablauf-4


def test_reservegrenze_nach_zusatz_max_und_bei_n_max(monkeypatch):
    gesehen = _attrappe(monkeypatch, erfuellt_ab=None)
    out = planung.haken('N01-A4', 'L1', NEU, 2, 2, 5, (2,), (20,), PLAN, rauschquelle=ORAKEL)(_aufruf())
    c = out['kandidaten'][0]
    assert len(gesehen) == 11 and c['reserve_zusatz'] == 10 and c['reserve_r'] == 12
    assert not c['erfuellt'] and c['P_erfuellt'] and c['grund'].startswith('Reservegrenze')
    assert out['n_min'] is None and out['kandidat_nur_P']['n_min'] == 2 and 'Reservegrenze' in out['grund']
    gesehen.clear()
    out = planung.haken('N01-A4', 'L1', NEU, 2, 2, 5, (2,), (20,), PLAN, rauschquelle=ORAKEL)(_aufruf(n_max=6))
    c = out['kandidaten'][0]
    assert [g['n_bloecke'] for g in gesehen] == [4, 5, 6] and c['grund'] == 'Reservegrenze: n_min + r + 1 > n_max'


def test_nicht_pruefbar_ohne_ablauf_kein_kandidat(monkeypatch):
    gesehen = _attrappe(monkeypatch, geprueft=False)
    out = planung.haken('N01-A4', 'L1', NEU, 2, 2, 5, (2, 3), (20,), PLAN, verfahren=vf.STATISCH,
                        rauschquelle=ORAKEL)(_aufruf())
    assert len(gesehen) == 1 and out['n_min'] is None and 'nicht prüfbar' in out['grund']
    assert out['kandidat_nur_P']['n_min'] == 2 and len(out['kandidaten']) == 1     # weitere ebenso nicht prüfbar


def test_zielfunktion_aus_der_regel_und_historisch_unveraendert(monkeypatch):
    with pytest.raises(ValueError, match='zielfunktion'):
        _attrappe(monkeypatch, erfuellt_ab=0)
        planung.haken('N01-A4', 'L1', _mit(NEU, 'planung.zielfunktion', 'b'), 2, 2, 5, (2,), (20,), PLAN,
                      rauschquelle=ORAKEL)(_aufruf())
    gesehen = _attrappe(monkeypatch, erfuellt_ab=None)
    out = planung.haken('N01-A4', 'L1', ALT, 2, 2, 5, (2,), (20,), PLAN)(_aufruf())
    c = out['kandidaten'][0]
    assert len(gesehen) == 1 and gesehen[0]['verfahren'] == vf.STANDARD and c['erfuellt'] and out['n_min'] == 2
    assert not {'reserve_ziel', 'P_erfuellt', 'reserve_verlauf'} & set(c) and 'zielfunktion' not in out
    assert 'zeitbilanz' not in c['messzeit']
