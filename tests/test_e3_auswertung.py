"""E3 im Regelstand 2026-11 auf Code-Ebene (kontrollen.e3_auswerten mit e3_grenzen, Aufruf in auswertung): Regelwerte
gebunden (nicht unterstützte → ValueError), m = 43 fest auch bei fehlenden Punkten, fehlender Triphasik-Punkt,
singuläre Kovarianz und zu wenige Freiheitsgrade mit Grund ohne dreiwertige Aussage, Rückfall je Prüfgröße,
Gesamturteil, gespeicherte Felder für die Modellprüfung, historisches Profil bitgleich, Zusatzprüffälle 0,5 %/1 %.

Die synthetischen Fälle haben bekannte Zeiger (T aus der Statik, Modulzeiger mit vorgegebenem Phasenfehler) und
Gaußrauschen; geprüft wird die Logik, nicht eine Rate."""
import dataclasses
import json

import numpy as np
import pytest
from scipy import stats

from pcmms_auswertung import auswertung, e3_grenzen as eg, formate, kontrollen, konventionen as kv, regeln, zufall
from pcmms_auswertung.generator import ebene_h, kampagne, szenarien
from pcmms_auswertung.harness import kampagnen, kette, kriterien

AF11, ENTW11, ENTW10 = regeln.profil('AF-2026-11'), regeln.profil('ENTW-2026-11'), regeln.profil('ENTW-2026-10')
PUNKTE = [f'S{p:g}' for p in kv.SCHNITT_PHI2]
A_M = 0.05 / 43
R_Z = 0.1
ZELLEN = R_Z * np.c_[np.cos(np.radians([0, 120, 240])), np.sin(np.radians([0, 120, 240]))]
MODULE = 0.5 * R_Z * np.c_[np.cos(np.radians([60, 180, 300])), np.sin(np.radians([60, 180, 300]))]
KETTE_P = np.array([[1.0, 2e-6, 0.0], [1.0, -1e-6, 0.0], [1.0, 3e-6, 0.0]])
AMP = (1.0, 0.9, 1.1)


def _t_nenn():
    return kontrollen.t_aus_parametern(np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1], MODULE, KETTE_P, 240.0, 0.05, 10.0)


def _beschr(s_lage=1e-5):
    """Unsicherheitsbeschreibung von T (Format Teil B nr5) mit kleiner Zelllagenunsicherheit."""
    Cg = np.zeros((9, 9))
    Cg[3:, 3:] = np.eye(6) * s_lage ** 2
    kette_ = [dict(zelle=c + 1, modell='laufzeit', p=KETTE_P[c].copy(), kovarianz=np.zeros((3, 3))) for c in range(3)]
    return dict(format=kontrollen.T_FORMAT, modell=kontrollen.T_MODELL, f_hz=10.0, ks=[1, 2],
                gxy=dict(wert=np.r_[np.ones(3), ZELLEN[:, 0], ZELLEN[:, 1]], kovarianz=Cg), kette=kette_,
                fn_zeta=dict(wert=np.array([240.0, 0.05]), gezogen=False, kovarianz_statistisch=np.zeros((2, 2)),
                             kette_richtungen=[]),
                module_nominal_m=MODULE, nicht_gezogen=[], unvollstaendig=[], naeherungen=[])


def _konfig(T0, p2, delta=(0.0, 0.0, 0.0), amp2=1.0, n=12, rauschen=2e-3, rng=None):
    """Läufe einer Schnittkonfiguration: Zellzeiger T(kω)·C_k mit Modulzeigern aⱼ·e^{−ik(φⱼ + δⱼ)} (Modul 2 × amp2),
    Indexzeiger der Sollphasen (Δδ = 0), komplexes Gaußrauschen je Lauf und Zelle."""
    k = np.arange(1, 3)
    phi = (0.0, p2, 240.0)
    a = np.array(AMP) * np.array([1.0, amp2, 1.0])
    C = a[:, None] * np.exp(-1j * np.outer(np.radians(np.add(phi, delta)), k))
    N = np.stack([T0[i] @ C[:, i] for i in range(2)], -1)
    Xz = N[None] + rauschen * (rng.standard_normal((n, 3, 2)) + 1j * rng.standard_normal((n, 3, 2)))
    nz = np.full(n, 100)
    return dict(Xz=Xz, Z=nz[:, None, None] * np.exp(-1j * np.outer(np.radians(phi), k))[None], nz=nz)


def _fall(punkte=PUNKTE, n=12, n0=12, rauschen=2e-3, B=300, delta=None, amp2=None, mit_T=True, seed=1,
          rauschen0=None, s_lage=1e-5):
    """Eingaben von e3_auswerten für die Punkte `punkte` (delta, amp2: dict Punkt → Wert)."""
    rng = np.random.default_rng(seed)
    T0 = _t_nenn()
    K = {kid: _konfig(T0, float(kid[1:]), (delta or {}).get(kid, (0.0, 0.0, 0.0)), (amp2 or {}).get(kid, 1.0), n,
                      rauschen, rng) for kid in punkte}
    r0 = rauschen if rauschen0 is None else rauschen0
    E0 = [np.stack([T0[i][:, j] * AMP[j] for i in range(2)], -1)[None] +
          r0 * (rng.standard_normal((n0, 3, 2)) + 1j * rng.standard_normal((n0, 3, 2))) for j in range(3)]
    idxA = {kid: rng.integers(0, d['Xz'].shape[0], (B, d['Xz'].shape[0])) for kid, d in K.items()}
    idxB0 = [rng.integers(0, n0, (B, n0)) for _ in range(3)]
    tz = kontrollen.t_ziehungen(_beschr(s_lage), np.random.default_rng(seed + 7), B) if mit_T else None
    return dict(K=K, E0=E0, idxA=idxA, idxB0=idxB0, T=T0, tz=tz, seed=seed)


def _e3(f, profil=ENTW11, punkte=PUNKTE, kriterien_=None, **kw):
    return kontrollen.e3_auswerten(f['K'], f['E0'], f['idxA'], f['idxB0'], f['T'], ZELLEN, np.zeros(3), np.zeros(3),
                                   None, 'S120', profil, np.random.default_rng(f['seed'] + 1), 0.0, T_zieh=f['tz'],
                                   punkte=punkte, kriterien=kriterien_, **kw)


def _profil_mit(rid, wert, basis=AF11):
    return regeln.Regelprofil(basis.id, basis.beschreibung,
                              [dataclasses.replace(r, wert=wert) if r.id == rid else r for r in basis.regeln.values()])


# ── Regelwerte ─────────────────────────────────────────────────────────────────────────────────────────
def test_regelwerte_gebunden_und_nicht_unterstuetzte_werte_abgewiesen():
    """Die Werte von e3.* werden gelesen und angewandt; jeder nicht unterstützte Wert → ValueError, kein Ersatzweg."""
    r = eg.regeln_lesen(AF11)
    assert r['m'] == 43 and r['alpha_m'] == pytest.approx(A_M) and r['grenzen']['nu_min'] == 5
    assert r['schwellen'] == dict(phase_grad=0.1, q_tol=5.8e-4) and eg.regeln_lesen(ENTW11) == r
    gr = AF11.wert('e3.grenzen')
    falsch = [('e3.pruefzahl', 42), ('e3.pruefzahl', 'zwei_je_konfiguration_plus_eins'), ('e3.rueckfall', 'ganz'),
              ('e3.pruefmenge', 'auswertbare_schnittpunkte'), ('e3.e3b_form', 'absolut'),
              ('e3.schwellen', dict(phase_grad=0.1)), ('e3.grenzen', {**gr, 'e3a': 'z_quantil'}),
              ('e3.grenzen', {**gr, 'e3b': 'rice_spur'}), ('e3.grenzen', {**gr, 'nu': 'welch'}),
              ('e3.grenzen', {**gr, 'nu_min': 3}), ('e3.grenzen', {**gr, 'unauffaellig': 'z_0.95'})]
    f = _fall(punkte=['S120'], B=50)
    for rid, w in falsch:
        p = _profil_mit(rid, w)
        with pytest.raises(ValueError):
            eg.regeln_lesen(p)
        with pytest.raises(ValueError):
            _e3(f, profil=p)
    with pytest.raises(ValueError, match='Prüfmenge'):
        _e3(f, punkte=None)
    with pytest.raises(ValueError, match='Schnittpunkte statt 21'):
        _e3(f, punkte=PUNKTE[:20])
    with pytest.raises(ValueError):
        szenarien.zusatz_e3b([0.0055])


# ── Prüfmenge, m und fehlende Prüfungen ────────────────────────────────────────────────────────────────
def test_m_fest_43_auch_bei_fehlenden_punkten():
    """Drei von 21 Punkten auswertbar: 43 Prüfungen, die fehlenden ohne Aussage mit Grund; jede Prüfung auf α/43;
    E3a kann dann nicht „unauffällig“ sein. Die Grenzen eines Punkts hängen nicht von der Zahl der übrigen ab."""
    teil = ['S100', 'S120', 'S140']
    e = _e3(_fall(punkte=teil, rauschen=1e-4))
    voll = _e3(_fall(punkte=PUNKTE, rauschen=1e-4))
    assert e['m'] == voll['m'] == 43 and len(e['pruefungen']) == 43 and e['alpha_m'] == pytest.approx(A_M)
    fehlt = [p for p in e['pruefungen'] if p['ergebnis'] is None]
    assert len(fehlt) == 36 and all('nicht auswertbar' in p['grund'] for p in fehlt)
    assert e['pruefmenge']['fehlend'] == [k for k in PUNKTE if k not in teil]
    pa = e['pruefgroessen']['E3a']
    assert pa['n_ausgewertet'] == 6 and pa['zaehlung']['unauffällig'] == 6 and pa['urteil'] == 'unbestimmt'
    assert voll['pruefgroessen']['E3a']['urteil'] == 'unauffällig'
    for x in e['e3a']:
        p = x['e3a']['modul2']['pruefung']
        assert p['k_einseitig'] == pytest.approx(stats.t.isf(A_M, p['nu_eff']), rel=1e-12)
    assert e['bewertung'] in ('unbestimmt', 'auffällig') and voll['bewertung'] != 'keine Überschreitung nachgewiesen'


def test_fehlender_triphasik_punkt_ohne_dreiwertige_aussage():
    """Ohne Triphasik-Punkt: E3b nicht prüfbar mit Grund, m bleibt 43, E3a dreiwertig; das Gesamturteil ist keine
    dreiwertige Aussage („keine Überschreitung nachgewiesen“), auch wenn alle E3a-Prüfungen unauffällig sind."""
    punkte = [k for k in PUNKTE if k != 'S120']
    e = _e3(_fall(punkte=punkte, rauschen=1e-4))
    pb = e['pruefgroessen']['E3b']
    assert e['e3b'] is None and pb['stufe'] == 'nicht prüfbar' and pb['urteil'] is None
    assert any('Triphasik' in g for g in pb['gruende']) and e['m'] == 43
    assert e['pruefgroessen']['E3a']['stufe'] == 'dreiwertig'
    assert e['pruefgroessen']['E3a']['zaehlung']['unauffällig'] == 40
    assert e['bewertung'] == 'keine Überschreitung nachgewiesen'


def test_singulaere_oder_nicht_endliche_kovarianz_und_zu_wenige_freiheitsgrade():
    """E3b: Replikate auf einer Geraden (Rang 1), ohne Streuung oder nicht endlich → nicht prüfbar mit Grund; ν < 5
    (n₀ = 5) ebenso. E3a: n_A = 5 → nicht prüfbar; bei B < 10 000 zählt ν_eff (ν = 5, B = 50 → ν_eff < 5)."""
    rng = np.random.default_rng(3)
    z = rng.standard_normal(400)
    gerade = 1e-4 * (1 + 2j) * z
    for db, text in ((1e-4 + gerade, 'singulär'), (np.full(400, 1e-4 + 0j), 'singulär'),
                     (np.r_[gerade[:-1], np.nan] * 0 + np.inf, 'zu wenige')):
        p = eg.e3b_pruefung(1e-4 + 0j, db, 20, [20, 20, 20], 5.8e-4, A_M, 5)
        assert p['ergebnis'] is None and text in p['grund'], p['grund']
    iso = 1e-4 * (rng.standard_normal(400) + 1j * rng.standard_normal(400))
    p = eg.e3b_pruefung(1e-4 + 0j, iso, 20, [20, 5, 20], 5.8e-4, A_M, 5)
    assert p['n_stern'] == 5 and p['nu'] == 4 and p['ergebnis'] is None and 'Freiheitsgrade' in p['grund']
    assert p['sigma'] is not None and p['s_hat'] > 0                  # Zahlen bleiben berichtet
    assert eg.e3a_pruefung(0.01, 1e-4, 5, 400, 400, 0.1, A_M, 5)['grund'].startswith('zu wenige Freiheitsgrade')
    assert eg.e3a_pruefung(0.01, 1e-4, 6, 50, 50, 0.1, A_M, 5)['nu_eff'] == pytest.approx(1 / (1 / 5 + 1 / 49))
    assert eg.e3a_pruefung(0.01, 1e-4, 6, 50, 50, 0.1, A_M, 5)['ergebnis'] is None
    assert eg.e3a_pruefung(0.01, 1e-4, 6, 10000, 10000, 0.1, A_M, 5)['ergebnis'] == 'unauffällig'
    assert eg.e3a_pruefung(0.01, 0.0, 12, 400, 400, 0.1, A_M, 5)['ergebnis'] is None   # u = 0: Modell verletzt
    # in der Auswertung: rauschfreier Triphasik-Punkt und rauschfreie Phase 0 → Σ̂ singulär
    e = _e3(_fall(punkte=['S120'], rauschen=0.0, s_lage=0.0, B=60))
    assert e['e3b']['pruefung']['ergebnis'] is None and 'singulär' in e['e3b']['pruefung']['grund']
    assert e['pruefgroessen']['E3b']['stufe'] == 'nicht prüfbar' and e['bewertung'] is None
    assert e['status'].startswith('nicht prüfbar')
    e = _e3(_fall(punkte=['S120'], n0=5, B=60))
    assert 'Freiheitsgrade' in e['e3b']['pruefung']['grund'] and e['m'] == 43


def test_ungueltige_replikate_ausgewiesen_und_ohne_aussage():
    """Ungültige Replikate werden ausgelassen und mit Zahl ausgewiesen; die Prüfung bleibt ohne Aussage, weil die
    Gültigkeit am Rand für eine gestutzte Replikatverteilung nicht gezeigt ist. Unzulässige T-Ziehungen führen beide
    Prüfgrößen auf „beschreibend“ zurück (Status „nur numerisch“)."""
    rng = np.random.default_rng(5)
    db = 1e-4 * (rng.standard_normal(400) + 1j * rng.standard_normal(400))
    db[:3] = np.nan
    p = eg.e3b_pruefung(1e-4 + 0j, db, 20, [20, 20, 20], 5.8e-4, A_M, 5)
    assert p['B'] == 400 and p['B_gueltig'] == 397 and p['ergebnis'] is None and '3 von 400' in p['grund']
    assert p['sigma'] is not None and p['nu_eff'] == pytest.approx(1 / (1 / 19 + 1 / 396))
    p = eg.e3a_pruefung(0.01, 1e-4, 20, 400, 397, 0.1, A_M, 5)
    assert p['ergebnis'] is None and '3 von 400' in p['grund'] and p['untere_grenze'] is not None
    f = _fall(punkte=['S118', 'S120'], B=80)
    f['tz']['gueltig'] = f['tz']['gueltig'].copy()
    f['tz']['gueltig'][:2] = False
    e = _e3(f)
    assert all(e['pruefgroessen'][g]['stufe'] == 'beschreibend' for g in ('E3a', 'E3b'))
    assert e['bewertung'] is None and e['status'].startswith('nur numerisch') and 'unzulässig' in e['status']
    assert e['e3b']['pruefung']['B_gueltig'] == 78


# ── Rückfall je Prüfgröße und Gesamturteil ─────────────────────────────────────────────────────────────
def test_rueckfall_je_pruefgroesse():
    """Kriterien von A9.11 aus Teil B: verfehlt E3b nur „unauffällig ≥ 0,8“, wird E3b einseitig (auffällig oder keine
    Überschreitung nachgewiesen), E3a bleibt dreiwertig; verfehlte Modellprüfung oder verfehltes „auffällig ≤ 0,05“
    → beschreibend mit Grund, Zahlen bleiben. Ohne Unsicherheit von T sind beide Prüfgrößen nur numerisch."""
    f = _fall(rauschen=1e-4)
    basis = _e3(f)
    assert basis['bewertung'] == 'unauffällig' and 'nicht ausgewiesen' in basis['kriterien_a9_11']
    ein = _e3(f, kriterien_=dict(herkunft='Test', E3b=dict(auffaellig=True, unauffaellig=False, modellpruefung=True)))
    assert ein['pruefgroessen']['E3b']['stufe'] == 'einseitig' and ein['pruefgroessen']['E3a']['stufe'] == 'dreiwertig'
    assert ein['pruefgroessen']['E3b']['urteil'] == 'keine Überschreitung nachgewiesen'
    assert ein['pruefgroessen']['E3a']['urteil'] == 'unauffällig'
    assert ein['bewertung'] == 'keine Überschreitung nachgewiesen'                    # nicht „unauffällig“
    assert ein['pruefungen'][-1]['ergebnis'] == 'keine Überschreitung nachgewiesen' and 'Test' in ein['kriterien_a9_11']
    mod = _e3(f, kriterien_=dict(E3b=dict(modellpruefung=False)))
    assert mod['pruefgroessen']['E3b']['stufe'] == 'beschreibend' and mod['pruefgroessen']['E3b']['urteil'] is None
    assert mod['e3b']['pruefung']['ergebnis'] == 'unauffällig' and mod['pruefungen'][-1]['ergebnis'] is None
    assert 'beschreibend' in mod['pruefungen'][-1]['grund']
    assert mod['bewertung'] == 'keine Überschreitung nachgewiesen'
    a = _e3(f, kriterien_=dict(E3a=dict(auffaellig=False)))
    assert a['pruefgroessen']['E3a']['stufe'] == 'beschreibend' and a['pruefgroessen']['E3b']['urteil'] == 'unauffällig'
    beide = _e3(f, kriterien_=dict(E3a=dict(auffaellig=False), E3b=dict(modellpruefung=False)))
    assert beide['bewertung'] is None and beide['status'].startswith('nur beschreibend')
    with pytest.raises(ValueError):
        _e3(f, kriterien_=dict(E3b=dict(unauffaellig='nein')))
    with pytest.raises(ValueError):
        _e3(f, kriterien_=dict(E3c={}))
    ohne = dict(f, tz=None)
    o = _e3(ohne)
    assert o['bewertung'] is None and o['status'].startswith('nur numerisch') and 'Unsicherheit von T' in o['status']
    assert all(o['pruefgroessen'][g]['stufe'] == 'beschreibend' for g in ('E3a', 'E3b'))
    assert o['e3b']['pruefung']['s_hat'] > 0                          # Zahlen ohne Aussage


def test_auffaellig_je_pruefgroesse_und_gesamt():
    """Ein Phasenfehler von 0,5° an Modul 2 eines Punkts macht genau diese E3a-Prüfung auffällig, E3b (Triphasik ohne
    Fehler) nicht; eine Amplitudenänderung von 1 % am Triphasik-Punkt macht E3b auffällig, E3a nicht. Auffällig
    bleibt auch in einer einseitigen Prüfgröße auffällig."""
    e = _e3(_fall(rauschen=1e-4, delta={'S110': (0.0, 0.5, 0.0)}))
    auff = [p['id'] for p in e['pruefungen'] if p['ergebnis'] == 'auffällig']
    assert auff == ['E3a/S110/modul2'] and e['bewertung'] == 'auffällig'
    assert e['pruefgroessen']['E3a']['urteil'] == 'auffällig' and e['pruefgroessen']['E3b']['urteil'] == 'unauffällig'
    e = _e3(_fall(rauschen=1e-4, amp2={'S120': 1.01}),
            kriterien_=dict(E3b=dict(unauffaellig=False)))
    assert e['pruefgroessen']['E3b'] == {**e['pruefgroessen']['E3b'], 'stufe': 'einseitig', 'urteil': 'auffällig'}
    assert e['pruefgroessen']['E3a']['zaehlung']['auffällig'] == 0 and e['bewertung'] == 'auffällig'
    assert e['e3b']['pruefung']['q_Z'] == pytest.approx(0.01 * 0.9 / 3, rel=0.1)   # |d| ≈ a·|C₂|/(Σ|Cⱼ|)


def test_gesamturteil_logik():
    """„Unauffällig“ nur bei beiden Prüfgrößen dreiwertig und unauffällig; „keine Überschreitung nachgewiesen“ ist
    keine Einhaltung; ohne jede Aussage kein Urteil. Fehlende Prüfungen verhindern „unauffällig“ einer Prüfgröße."""
    def pg(a, b):
        return {'E3a': dict(stufe=a[0], urteil=a[1]), 'E3b': dict(stufe=b[0], urteil=b[1])}
    D, E, BE, NP = 'dreiwertig', 'einseitig', 'beschreibend', 'nicht prüfbar'
    K = 'keine Überschreitung nachgewiesen'
    faelle = [((D, 'unauffällig'), (D, 'unauffällig'), 'unauffällig'),
              ((D, 'unauffällig'), (D, 'unbestimmt'), 'unbestimmt'),
              ((D, 'unbestimmt'), (D, 'unbestimmt'), 'unbestimmt'),
              ((D, 'unauffällig'), (E, K), K), ((D, 'unauffällig'), (NP, None), K), ((D, 'unauffällig'), (BE, None), K),
              ((D, 'auffällig'), (BE, None), 'auffällig'), ((D, 'unauffällig'), (E, 'auffällig'), 'auffällig'),
              ((BE, None), (NP, None), None), ((NP, None), (D, 'unauffällig'), K)]
    for a, b, soll in faelle:
        assert eg.gesamturteil(pg(a, b)) == soll, (a, b)
    p = [dict(ergebnis='unauffällig')] * 41 + [dict(ergebnis=None)]
    assert eg.urteil(p, D, 42) == ('unbestimmt', D)
    assert eg.urteil([dict(ergebnis='unauffällig')] * 42, D, 42) == ('unauffällig', D)
    assert eg.urteil([dict(ergebnis=None)] * 42, D, 42) == (None, NP)
    assert eg.urteil([dict(ergebnis=K)], E, 1) == (K, E)


# ── Gespeicherte Felder ────────────────────────────────────────────────────────────────────────────────
def test_felder_fuer_die_modellpruefung_gespeichert():
    """E3b speichert d̂ komplex, Σ̂ (drei Zahlen, n*/(n* − 1)·Cov_b), ŝ = √λ_max, ρ̂, Richtung, ν, ν_eff, n_A, n₀ⱼ, n*,
    κ und die Grenzen; E3a je Prüfung ũ, ν, ν_eff, n_A, k und die Grenzen; der Kurzbefund trägt sie für die
    Kalibrierkampagnen. Die historischen Zahlenfelder bleiben gleich (dieselben Replikate)."""
    f = _fall(punkte=['S118', 'S120'], n=14, n0=11, B=400)
    e = _e3(f)
    pb = e['e3b']['pruefung']
    S = np.array([[pb['sigma'][0], pb['sigma'][1]], [pb['sigma'][1], pb['sigma'][2]]])
    lam = np.linalg.eigvalsh(S)
    assert pb['n_A'] == 14 and pb['n0'] == [11, 11, 11] and pb['n_stern'] == 11 and pb['nu'] == 10
    assert pb['nu_eff'] == pytest.approx(1 / (1 / 10 + 1 / 399)) and pb['B_gueltig'] == 400
    assert pb['s_hat'] ** 2 == pytest.approx(lam[1], rel=1e-12) and pb['lambda_min'] == pytest.approx(lam[0])
    assert pb['rho_hat'] == pytest.approx(np.sqrt(lam[0] / lam[1]), rel=1e-12)
    assert pb['q_Z'] == pytest.approx(np.hypot(*pb['d_Z']), rel=1e-12) == e['e3b']['q_Z']
    assert pb['kappa'] == pytest.approx(stats.t.isf(A_M, pb['nu_eff']) / stats.norm.isf(A_M))
    assert pb['kritisch'] == pytest.approx(eg.e3b_kritisch(pb['s_hat'], pb['nu_eff'], 5.8e-4, A_M))
    assert 0 <= pb['richtung_grad'] < 180 and pb['nenner_cv'] < 0.01
    # Σ̂ aus Replikaten: n*/(n* − 1)·Cov
    zb = np.random.default_rng(0).standard_normal((50, 2)) @ np.array([[2.0, 0.0], [0.5, 1.0]])
    assert eg.e3b_kovarianz(zb[:, 0] + 1j * zb[:, 1], 11) == pytest.approx(1.1 * np.cov(zb.T, ddof=1), rel=1e-12)
    pa = e['e3a'][0]['e3a']['modul2']['pruefung']
    assert pa['n_A'] == 14 and pa['nu'] == 13 and pa['faktor_n'] == pytest.approx(14 / 13)
    assert pa['u'] == pytest.approx(np.sqrt(14 / 13) * e['e3a'][0]['e3a']['modul2']['u_grad'], rel=1e-12)
    alt = _e3(f, profil=ENTW10)
    for x, y in zip(alt['e3a'], e['e3a']):
        for mod in ('modul2', 'modul3'):
            assert {k: v for k, v in y['e3a'][mod].items() if k != 'pruefung'} == x['e3a'][mod]
    assert {k: v for k, v in e['e3b'].items() if k != 'pruefung'} == alt['e3b']
    kb = kampagnen._e3_kurz(e)
    assert kb['regelstand'] == '2026-11' and kb['m'] == 43 and kb['z_B'] is None and len(kb['pruefungen']) == 43
    assert kb['e3a_pruefung'].shape == (4, len(eg.KURZ_E3A)) and kb['e3a_pruefung'][0, 4] == 14
    assert set(kb['e3b_modell']) == set(eg.KURZ_E3B) and kb['e3b_modell']['sigma'] == pb['sigma']
    assert kb['pruefgroessen']['E3b']['stufe'] == 'dreiwertig' and kb['e3b'][0] == pb['q_Z']
    assert set(kampagnen._e3_kurz(alt)) == {'bewertung', 'status', 'z_B', 'm', 'e3a', 'e3b', 't'}


# ── Historischer Modus und Kette ───────────────────────────────────────────────────────────────────────
# E3-Ausgabe der Kampagne N01-A4/L1, Seed 7, Plan (n₀ 20, Piloten 20, 24 Blöcke, historische Anordnung), B = 200: Referenz
# mit dem Code von main berechnet (tests/historisch_referenz.py, Vergleich mit Toleranz).
HISTORISCHE_PROFILE = ('AF-2026-10', 'ENTW-2026-10')
PLAN = kampagne.Plan(n0=20, n_pilot=20, n_bloecke=24)


def _red(p):
    return p.mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=1000)


@pytest.mark.parametrize('name', HISTORISCHE_PROFILE)
def test_historisches_profil_e3_ausgabe_gleich_main(name):
    """Unter den historischen Profilen ist die E3-Ausgabe einer kleinen Kampagne mit der historischen Anordnung gleich
    der mit dem Code von main berechneten Referenz (Vergleich mit Toleranz, nicht über Prüfsummen, die an den letzten
    Bits der Rechenumgebung hängen)."""
    import historisch_referenz as hr
    plan = PLAN.mit(p0_anordnung='historisch')
    r = kette.kette('N01-A4', 'L1', _red(regeln.profil(name)), plan=plan, seed=7, n_min=18, mit_wahrheit=False)
    e = r['ergebnis']['E3']
    abw = hr.vergleich(hr.lies_referenz()['e3'][name], json.loads(json.dumps(hr.jsonbar(e))))
    assert not abw, abw[:10]
    assert 'regelstand' not in e and 'pruefungen' not in e
    f = _fall(punkte=['S118', 'S120'], B=60)                  # punkte, kriterien: im historischen Modus ohne Wirkung
    a = _e3(f, profil=ENTW10)
    b = kontrollen.e3_auswerten(f['K'], f['E0'], f['idxA'], f['idxB0'], f['T'], ZELLEN, np.zeros(3), np.zeros(3), None,
                                'S120', ENTW10, np.random.default_rng(f['seed'] + 1), 0.0, T_zieh=f['tz'])
    assert formate.sha256_json(a) == formate.sha256_json(b) and a['m'] == 5 and 'z_B' in a


def test_kette_2026_11_mit_fehlenden_punkten():
    """Kette im Regelstand 2026-11 mit zwei gestörten Schnittpunkten (H-fehlend: S118, S140): m = 43, vier E3a-Prüfungen
    ohne Aussage mit Grund, die Prüfmenge nennt die fehlenden Punkte; Kurzbefund mit den neuen Feldern."""
    prof = _red(ENTW11)
    r = kette.kette('H-fehlend', 'L1', prof, plan=PLAN, seed=7, n_min=18, mit_wahrheit=False)
    e = r['ergebnis']['E3']
    assert e['regelstand'] == '2026-11' and e['m'] == 43 and e['pruefmenge']['fehlend'] == ['S118', 'S140']
    ohne = [p['id'] for p in e['pruefungen'] if p['ergebnis'] is None]
    assert ohne == ['E3a/S118/modul2', 'E3a/S118/modul3', 'E3a/S140/modul2', 'E3a/S140/modul3']
    assert e['pruefgroessen']['E3a']['urteil'] != 'unauffällig' and e['bewertung'] != 'unauffällig'
    kb = kampagnen.kurzbefund(r['ergebnis'], r['teil_b'], 7)
    assert kb['E3']['m'] == 43 and kb['E3']['e3b_modell']['n_A'] >= 18 and len(kb['E3']['pruefungen']) == 43


# ── Zusatzprüffälle 0,5 % und 1 % ──────────────────────────────────────────────────────────────────────
def _kampagne(sz, prof, seed=7):
    m = szenarien.modell(sz, 'L1', plan=PLAN)
    laeufe = kampagne.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    tab = ebene_h.erzeuge(m, laeufe, zufall.strom(seed, 'generator'))
    _, _, kal = kette.kalibrierung_erzeugen(sz, m, seed)
    tb, _ = kette.teil_b_erzeugen(tab, kal, m, prof, kette.testvorgabe_werkzeug8(), seed, 18)
    return auswertung.auswerten(tab, kal, tb, prof)['E3']


def test_zusatzszenarien_amplitude_05_und_1_prozent():
    """Zusatzprüffälle aus e3.zusatzszenarien (0,5 % und 1 % Amplitude von Modul 2 nur in den Kombinationsläufen):
    außerhalb des Katalogs (Prüfsatz bitgleich), je eine Kampagne als Funktionsnachweis. Mit denselben Zufallsströmen
    wie N01-A4 verschiebt sich d̂ am Triphasik-Punkt um a/3 (Vorlage: 1 % ≙ 5,74·q_tol), E3a bleibt ohne Befund. Eine
    Rate wird daraus nicht abgeleitet."""
    werte = AF11.wert('e3.zusatzszenarien')
    assert [szenarien.ZUSATZ_E3[szenarien.zusatz_id(a)].staerke for a in werte] == werte == [0.005, 0.01]
    assert not set(szenarien.ZUSATZ_E3) & set(szenarien.KATALOG)
    prof = _red(ENTW11).mit_reduktion(h3_mc=200)
    d0 = np.array(_kampagne(szenarien.KATALOG['N01-A4'], prof)['e3b']['pruefung']['d_Z'])
    for a in werte:
        e = _kampagne(szenarien.ZUSATZ_E3[szenarien.zusatz_id(a)], prof)
        pb = e['e3b']['pruefung']
        dd = np.hypot(*(np.array(pb['d_Z']) - d0))
        assert dd == pytest.approx(a / 3, rel=0.01) and dd / 5.8e-4 == pytest.approx(5.74 * a / 0.01, rel=0.01)
        assert e['m'] == 43 and pb['ergebnis'] in ('auffällig', 'unauffällig', 'unbestimmt')
        assert e['pruefgroessen']['E3a']['zaehlung']['auffällig'] == 0


def test_kriterienmatrix_e3_nach_regelstand():
    """Kriterienmatrix: im Regelstand 2026-11 ist E3 nicht mehr „fachlich offen“, aber nur probeweise gerechnet (keine
    Abnahme); historisch unverändert."""
    rt = dict(raten={'E3: unbestimmt': dict(rate=1.0, mc_se=0.0, zaehler=2, nenner=2)}, wahrheit=dict(klasse='R0'))
    kfg = dict(stufe='L1', plan=dict(n_bloecke=24), n_min=18, planung_kandidaten=[18], profil_reduktion={})
    for pid, soll in (('ENTW-2026-11+red(bootstrap_B=200)', 'nur probeweise gerechnet'),
                      ('ENTW-2026-10+red(bootstrap_B=200)', 'fachlich offen')):
        ps = dict(profil=pid, code_version={}, konfiguration=kfg,
                  schritte=dict(eigene={'E3b-amp10/L1': rt, 'N03-ungleich/L1': rt}))
        z = next(x for x in kriterien.bewerten(ps) if x['id'] == 'E3')
        assert z['status'] == soll
        assert ('E3b-amp10' in z['befund']) == pid.startswith('ENTW-2026-11')
    ps = dict(profil='AF-2026-11', code_version={}, konfiguration=kfg, schritte={})
    z = next(x for x in kriterien.bewerten(ps) if x['id'] == 'E3')
    assert z['status'] == 'fehlt' and 'Kalibrierabnahme' in z['grund']
