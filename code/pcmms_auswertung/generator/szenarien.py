"""Szenarienkatalog der ersten Softwarestufe (Plan AP-13, Abschnitt 3.4; Auftrag Etappe 5, Mindestfälle).

Jedes Szenario nennt die Plan-ID, die Art des Prüffalls, System, Rauschfamilie, Plan, Effekte, betroffene
Hypothesen, die erwartete Antwort laut Plan und dokumentierte Abweichungen vom Plan. Arten:

  null         exakte Superposition (lineares System, auch ungleiche Module, LTI-Kette, Drift der Kette)
  statistisch  Residuen-Injektion auf Ebene der Harmonischen (Kopplung × (1 − x), Phasenversatz, Modulfaktor):
               prüft die Regeln, belegt kein physikalisches Kontaktgesetz
  mechanisch   Physikgenerator mit eigener Lösung der Kombination (Hertz-Kontakt über den ereignisgenauen Löser,
               quadratische Kettenkennlinie im Zeitbereich)
  kalibrierung falsche Kalibrier-/Modellannahme für H3 (Eingänge aus P0.1–P0.5 weichen vom wahren System ab)
  regelpfad    Gültigkeits- und Abbruchregeln (Liftoff, Sättigung, Indexfehler, fehlende Punkte)
  kette        deterministische Gegenprobe der Kette (S₃-Bilder)

Die Klasse R0–R4 bildet `wahrheit` aus dem rauschfreien Generator. Szenarien mit Zielverhältnis bestimmen die
Effektstärke durch Nullstellensuche auf der Wahrheit (größtes wahres Residuum relativ zu Δ_rel der rauschfreien
Vorhersage, gegen beide Vorhersagen); der Plan nennt dafür feste Stärken, die hier als Startwerte dienen
(Abweichung „normiert auf das Residuum“ wie A05/A07 des Plans).
"""
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .. import konventionen as kv
from . import kampagne, physik, rauschen, wahrheit
from .modell import Generatormodell
from .systeme import Kette, system

ARTEN = ('null', 'statistisch', 'mechanisch', 'kalibrierung', 'regelpfad', 'kette')


@dataclass(frozen=True)
class Szenario:
    id: str
    plan_id: str
    titel: str
    art: str
    system: object                          # Name eines Bezugssystems oder Funktion () → System
    hypothesen: tuple
    erwartung: str
    effekte: object = ()                    # Tupel oder Funktion (stärke) → Tupel
    rauschen: object = None                 # None: Präzisionsstufe; Funktion (stufe) → Rauschmodell
    plan: tuple = ()                        # Abweichungen vom Kampagnenplan als (Name, Wert)
    staerke: object = None                  # feste Stärke (Plan) oder Startwert der Suche
    ziel: object = None                     # dict(groesse=None|'F_min_rel'|…, wert=…, bereich=(lo, hi), art=…)
    kalibrierung: tuple = ()                # Abweichungen der P0-Daten (Name, dict) für AP-11
    ebenen: tuple = ('H',)
    abweichung: str = ''
    hertz: object = None                    # dict für physik.hertz_fall
    systemfunktion: object = None           # Funktion (stärke) → System (Hubskalierung S01a)

    def __post_init__(self):
        if self.art not in ARTEN:
            raise ValueError(f'Art {self.art!r} unbekannt')


def _sys(name, **kw):
    return lambda: system(name, **kw)


def _weiss(stufe):
    """Weiß dominiertes Rauschen (N04): σ je Abtastwert und Zelle 0,25 N, Lauf-Streuung klein (Stufe L0)."""
    return rauschen.stufe('L0', sigma_zelle=0.25, jitter_grad=0.02, index_versatz_grad=0.0).mit(name=f'weiss({stufe})')


def _laufart(stufe):
    """Getrennte Streuungen je Laufart (N04): Kombinationsläufe doppelt so stark wie Einzelmodulläufe."""
    b = rauschen.stufe(stufe)
    a, p = b.a('L'), b.p('L')
    return rauschen.getrennt(f'laufart({stufe})', a, 2 * a, p, 2 * p, sigma_zelle=b.sigma_zelle)


def _e2(art, **kw):
    d = dict(art=art, punkte_I=(116.0, 120.0, 124.0), n0_strich=20, L_strich=True)
    d.update(kw)
    return d


KATALOG = {}


def _neu(*args, **kw):
    s = Szenario(*args, **kw)
    if s.id in KATALOG:
        raise ValueError(f'Szenario {s.id} doppelt')
    KATALOG[s.id] = s


# — Gruppe N ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_neu('N01-A4', 'N01', 'exakte Superposition, identische Module, A4', 'null', 'A4', ('H1', 'H2', 'H4', 'c'),
     'R0; K01, K05, K09; c mit Biaskorrektur', ebenen=('H', 'Z'))
_neu('N01-V1G0', 'N01', 'exakte Superposition, identische Module, V1-G0', 'null', 'V1-G0', ('H1', 'H2', 'H4', 'c'),
     'R0; K01, K05, K09', ebenen=('H', 'Z'))
_neu('N01-V1G60h', 'N01', 'exakte Superposition, identische Module, V1-G60h', 'null', 'V1-G60h', ('H1', 'H2'),
     'R0; K01, K05')
_neu('N03-ungleich', 'N03', 'ungleiche Module: Masse und Hub ±1 %, δ ±0,2°, Profilform k = 2 (Modul 3, +2 %)', 'null',
     _sys('V1-G0', m=(0.1, 0.101, 0.099), hub=(8e-3, 8.08e-3, 7.92e-3), delta_profil_grad=(0.0, 0.2, -0.2),
          profilform=((3, 2, 1.02),)),
     ('H1', 'H2'), 'R0 wie N01; H2-Spitze verschoben und richtig vorhergesagt', ebenen=('H', 'Z'))
_neu('N03-N3bindet', 'N03', 'ungleiche Module, Profilharmonische k = 3 von Modul 2 × 0,5, weiß dominiertes Rauschen (A4)',
     'null', _sys('A4', profilform=((2, 3, 0.5),)), ('H1',),
     'R0; unter D-Fassung B bindet Re/Im N₃ die Präzision (kleinstes Δ_q/u_q)', rauschen=_weiss,
     abweichung='Plan N03 nennt Masse/Hub/Δδ/Profilform; die Profilform ist hier so gewählt, dass N₃ unter '
                'Fassung B bindet (Auftrag Etappe 5)')
_neu('N04-laufart', 'N04', 'exakte Superposition, Streuungen der Kombinationsläufe doppelt so groß wie der '
     'Einzelmodulläufe', 'null', 'A4', ('H1', 'Rauschbias'), 'R0; Bias b̂⁰ (n₀) und b̂¹ (Kontrollläufe) getrennt',
     rauschen=_laufart)
_neu('N05-F', 'N05', 'Rand der Äquivalenzzone: F_min genau an Δ_q (Kopplung aller Harmonischen, A4)', 'statistisch',
     'A4', ('H1',), 'R2; K04: P(bestätigt) ≤ 0,05', effekte=lambda x: ({'art': 'kopplung', 'x': x},), staerke=0.10638,
     ziel=dict(groesse='F_min_rel', wert=1.0, bereich=(0.0, 0.5)),
     abweichung='Stärke durch Nullstellensuche auf der Wahrheit statt fest 10,638 %')
for _k in (2, 3):                    # N₁: mit Kopplung nur von N₁ erreicht F_min Δ vor N₁ (Befund)
    _neu(f'N05-N{_k}', 'N05', f'Rand der Äquivalenzzone: N{_k} genau an Δ_q (Kopplung nur der Harmonischen {_k}, A4)',
         'statistisch', 'A4', ('H1',), 'R2; K04: P(bestätigt) ≤ 0,05',
         effekte=(lambda kk: (lambda x: ({'art': 'kopplung', 'x': x, 'harmonische': [kk]},)))(_k),
         ziel=dict(groesse=f'N{_k}', wert=1.0, bereich=(0.0, 1.0)),
         abweichung='Kopplung nur einer Harmonischen, damit genau ein Test an Δ_q liegt')

# — Gruppe A ———————————————————————————————————————————————————————————————————————————————————————————————————————————
for _name, _wert, _kl in (('R1', 0.5, 'R1'), ('R2', 1.0, 'R2'), ('R3', 1.5, 'R3'), ('R4', 2.5, 'R4')):
    _neu(f'A04-{_name}', 'A04', f'Kopplung × (1 − x) aller Harmonischen der Kombinationsläufe, größtes wahres Residuum '
         f'{_wert:g}·Δ_rel (A4)', 'statistisch', 'A4', ('H1',),
         {'R1': 'R1; K03 (keine Falsifikation), bei hoher Präzision „bestätigt“ mit Zusatz „Abweichung nachgewiesen“',
          'R2': 'R2; K04: P(bestätigt) ≤ 0,05', 'R3': 'R3; nur berichtet (Graubereich, „nicht entscheidbar“ erwartet)',
          'R4': 'R4; K07: Power gegen Kopplung'}[_kl],
         effekte=lambda x: ({'art': 'kopplung', 'x': x},), ziel=dict(groesse=None, wert=_wert, bereich=(0.0, 0.9)),
         abweichung='Plan A04 nennt feste x; hier normiert auf das Residuum (wie A05/A07)')
_neu('A06-phase', 'A06', 'konfigurationsabhängiger Phasenversatz von Modul 2 nur in Kombinationsläufen, 0,2°', 'statistisch',
     'V1-G0', ('H1', 'H2'), 'R1; ≪ Δ_rel; auf hoher Präzision signifikant',
     effekte=lambda x: ({'art': 'phasenversatz_k', 'modul': 2, 'grad': x},), staerke=0.2)
_neu('A07-hertz50', 'A07', 'Hertz-Kontakt mit weicher Auflage (A4-weich, f_n0 = 50 Hz, ζ = 0,05, k_max = 9), '
     'Kombination und Einzelmodule aus dem ereignisgenauen Löser', 'mechanisch',
     lambda: physik.hertz_system(f_n0=50.0, zeta=0.05), ('H1', 'H4'),
     'nach Generatorwahrheit (Plan: 50 Hz ≈ 1,04·Δ ohne Skalierung); Modellbereich 1 FG, Dauerkontakt',
     hertz=dict(f_n0=50.0, zeta=0.05),
     abweichung='nur f_n0 = 50 Hz ohne Hubskalierung (Plan: 50/60 Hz mit Skalierung auf 0,5–3·Δ_rel)')

# — Gruppe C ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_KETTE_C = Kette(f_tp=(150.0, 150.0, 150.0), tau=(1e-4, 1e-4, 1e-4))
for _p in (1, 5):
    _neu(f'C03-GF{_p}', 'C03', f'Kraftkette G_F aus dem Brückensimulator um {_p} % falsch (Tiefpass 150 Hz, 0,1 ms)',
         'kalibrierung', _sys('V1-G0', kette=_KETTE_C), ('H3', 'H1', 'H2'),
         ('K11 bei 5 %; ' if _p == 5 else '') + 'H1, H2 unberührt (Skalenfehler fällt heraus, §8.3)',
         kalibrierung=(('p01', dict(bruecke_fehler=1 + _p / 100)),))
_neu('C04-steif', 'C04', 'steifer V1 ohne Mismatch, Kraftkette wie C03 richtig kalibriert', 'null',
     _sys('V1-G0', kette=_KETTE_C), ('H3',), 'H3 bestätigt bei richtigen Eingängen; keine Harmonische k ≤ 3 prüft den '
     'Kontakt (Kennzeichnung)')

# — Gruppe E ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_neu('E04-kette', 'E01/E04', 'gemeinsame lineare, zeitinvariante Kraftkette je Zelle (Tiefpass 200/180/220 Hz, '
     'Laufzeit 0,2/0,25/0,15 ms)', 'null',
     _sys('V1-G0', kette=Kette(f_tp=(200.0, 180.0, 220.0), tau=(2e-4, 2.5e-4, 1.5e-4))), ('H1', 'H2', 'H3'),
     'R0; K02: Superposition bleibt bei identischer Verarbeitung erhalten, dynamische Form ändert sich')
_neu('E07-verstaerkung', 'E07', 'Verstärkungsdrift aller Zellen Phase 0 → Phase 1 um 3 %', 'null', 'A4', ('H1',),
     'gegen ŷ¹ R0, gegen ŷ⁰ 3 %-Residuum; K02 mit Zusatz „Drift“', effekte=lambda x: ({'art': 'verstaerkung_p1',
                                                                                       'faktor': x},), staerke=0.03)
_neu('E07-basisdrift', 'E07', 'Drift der Einzelmodulbasis (Modul 2 +1 % in Phase 1) bei getrennten Streuungen je '
     'Laufart', 'null', 'A4', ('H1',), 'gegen ŷ¹ R0; Zusatz „Drift“; Bias b̂⁰ und b̂¹ getrennt',
     effekte=lambda x: ({'art': 'drift_basis', 'faktor': (0.0, x, 0.0)},), staerke=0.01, rauschen=_laufart)

# — Gruppe F ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_S3_PUNKTE = ((105.0, 247.0), (95.0, 230.0), (130.0, 215.0), (112.5, 251.0), (140.0, 260.0))
_neu('F01-S3', 'F01', 'fünf generische Punkte mit je sechs S₃-Bildern, identische Module, rauschfrei', 'kette', 'A4',
     ('Kette',), 'K16: gleiche F_min − ⟨N⟩, |N_k|, γ₁; Phasenregel arg N_k → arg N_k + k·φ_ref',
     plan=(('pruef', tuple(_S3_PUNKTE)),), ebenen=('H', 'Z'))
_neu('F03-S3ungleich', 'F03', 'S₃-Bilder bei 1 % Massenungleichheit von Modul 2', 'kette',
     _sys('A4', m=(0.65 * 0.4 / 3, 0.65 * 0.4 / 3 * 1.01, 0.65 * 0.4 / 3)), ('Kette', 'E3'),
     'modellfreier Vergleich weicht ab (≈ 0,015 N in N₁), die Superpositionsvorhersage nicht',
     plan=(('pruef', tuple(_S3_PUNKTE)),))

# — Gruppe H ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_neu('H01-zelt', 'H01', 'symmetrisches Zelt (A4, identische Module)', 'null', 'A4', ('H2',),
     'K10; Schätzer nicht regulär, Δφ* = 0 in einem Teil der Kampagnen')
_neu('H03-phase', 'H03', 'Profilphase von Modul 2 im Kombinationsbetrieb um 0,5° anders als im Einzelbetrieb',
     'statistisch', 'V1-G0', ('H2', 'H1'), '0,5° deutlich oberhalb der Auflösung von H2',
     effekte=lambda x: ({'art': 'phasenversatz_k', 'modul': 2, 'grad': x},), staerke=0.5)
_neu('H-fehlend', 'H01', 'fehlende Schnittpunkte: alle Läufe von S118 und S140 mit Störung (G8)', 'regelpfad', 'A4',
     ('H2', 'H1'), 'H2 mit fehlenden Punkten nach der Vollständigkeitsregel; H1 der Punkte nicht auswertbar',
     effekte=({'art': 'ereignis', 'ereignis': 'stoerung', 'auswahl': {'konfiguration': 'S118'}},
              {'art': 'ereignis', 'ereignis': 'stoerung', 'auswahl': {'konfiguration': 'S140'}}),
     abweichung='Ergänzung zu Gruppe H (Datenlage); Gerade und Gleichstand prüfen Einzeltests des Zeltfits')

# — Gruppe I ———————————————————————————————————————————————————————————————————————————————————————————————————————————
for _e, _ekw, _txt in (('amplitude', dict(s=0.5), 'zweite Amplitude s = 0,5'), ('frequenz', dict(f2=7.0),
                                                                               'zweite Frequenz 7 Hz')):
    _neu(f'I01-{_e}', 'I01', f'lineare Kopplung 1 % der Kombinationsläufe, {_txt}', 'statistisch', 'V1-G0',
         ('Zuordnung',), 'Klasse „∝ A“ (p = 1); K18', effekte=lambda x: ({'art': 'kopplung', 'x': x},), staerke=0.01,
         plan=(('einstellung2', _e2(_e, **_ekw)),), abweichung='Kopplung 1 % statt 0,1 %, damit die Zuordnung auf '
                                                              'Entwicklungsstufen eine Wirkung über dem Rauschen sieht')
    _neu(f'I02-{_e}', 'I02', f'quadratische Kettenkennlinie β = 2·10⁻³/N je Zelle (V1-G60h), {_txt}', 'mechanisch',
         'V1-G60h', ('Zuordnung', 'H1'), 'Klasse „∝ A²“ (p = 2); K18; H1-Wirkung ≥ 1 mN',
         effekte=lambda x: ({'art': 'kennlinie', 'beta': x},), staerke=2e-3, plan=(('einstellung2', _e2(_e, **_ekw)),))
_neu('I04-drift', 'I04', 'Verstärkungsdrift Phase 0 → 1 um 0,1 % bei zweiter Amplitude', 'null', 'V1-G0',
     ('Zuordnung',), 'Klasse „konstant“ bzw. keine Zuordnung (gegen ŷ¹ kein Residuum)',
     effekte=lambda x: ({'art': 'verstaerkung_p1', 'faktor': x},), staerke=1e-3,
     plan=(('einstellung2', _e2('amplitude', s=0.5)),))
_neu('I05-misch', 'I05', 'Kopplung 1 % und quadratische Kennlinie zusammen (V1-G60h), zweite Amplitude', 'mechanisch',
     'V1-G60h', ('Zuordnung',), 'Mischklasse; Grenzen der Zuordnung zeigen',
     effekte=({'art': 'kopplung', 'x': 0.01}, {'art': 'kennlinie', 'beta': 2e-3}),
     plan=(('einstellung2', _e2('amplitude', s=0.5)),))

# — Gruppe S ———————————————————————————————————————————————————————————————————————————————————————————————————————————
_neu('S01a-liftoff', 'S01a', 'Beginn des Einzelzell-Liftoffs (V1-G60h, Hub skaliert: kleinstes lineares Zellminimum '
     'bei F_LO,c − 2σ_c), Summe weit im Kontakt', 'regelpfad', 'V1-G60h', ('G6', 'S2'),
     'G6/S2 aus dem Zellkanal, nicht aus der Summe; nur Pfadprüfung (Abschneiden ohne Stoßdynamik)',
     staerke=-2.0, systemfunktion='s01a', ebenen=('H', 'Z'),
     abweichung='Plan: G0 und G60h mit vier Abständen; hier G60h mit −2σ als Vorgabe, Abstand einstellbar')
_neu('S02-kontrolllauf', 'S02', 'Liftoff in einem Kontrolllauf L₂ der Phase 1', 'regelpfad', 'A4', ('H1', 'H2'),
     'ŷ¹ ungültig, H1 und H2 nicht entscheidbar (Datenlage), §8.2',
     effekte=({'art': 'ereignis', 'ereignis': 'liftoff_zelle', 'zelle': 2,
               'auswahl': {'konfiguration': 'L2', 'phase': 1, 'nummer': 1}},))
_neu('S06-saettigung', 'S06', 'Übersteuerung von Zelle 3 in einem Kombinationslauf (S120) und einem Einzelmodullauf',
     'regelpfad', 'A4', ('G5',), 'G5 aus dem Rohkanal; Lauf ungültig, Summe unauffällig',
     effekte=({'art': 'ereignis', 'ereignis': 'saettigung', 'zelle': 3,
               'auswahl': {'konfiguration': 'S120', 'phase': 1, 'nummer': 0}},
              {'art': 'ereignis', 'ereignis': 'saettigung', 'zelle': 3,
               'auswahl': {'konfiguration': 'L1', 'phase': 0, 'nummer': 2}}), ebenen=('H', 'Z'))
_neu('S-indexfehler', 'A9.4', 'Indexfehler (fehlender Impuls von Modul 2) in einem Kombinationslauf (S110)',
     'regelpfad', 'A4', ('G10', 'G2'), 'Lauf nach der Indexprüfung ungültig, nicht durch die Summe verdeckt',
     effekte=({'art': 'ereignis', 'ereignis': 'indexfehler', 'modul': 2,
               'auswahl': {'konfiguration': 'S110', 'phase': 1, 'nummer': 0}},), ebenen=('H', 'Z'),
     abweichung='kein eigener Planpunkt; Ergänzung nach Auftrag Etappe 5')


# — Modellbildung ——————————————————————————————————————————————————————————————————————————————————————————————————————

def _plan(sz, plan=None):
    p = kampagne.Plan() if plan is None else plan
    kw = dict(sz.plan)
    return p.mit(**kw) if kw else p


@lru_cache(maxsize=8)
def _hertz_tabelle(f_n0, zeta, konf):
    return physik.hertz_fall(f_n0=f_n0, zeta=zeta, konfigurationen=dict(konf))


def _system(sz, staerke, rausch):
    if sz.systemfunktion == 's01a':
        return _s01a_hub(staerke, rausch)
    return sz.system() if callable(sz.system) else system(sz.system)


def _effekte(sz, staerke):
    return tuple(sz.effekte(staerke)) if callable(sz.effekte) else tuple(sz.effekte)


def _rausch(sz, stufe):
    return sz.rauschen(stufe) if sz.rauschen is not None else rauschen.stufe(stufe)


def _s01a_hub(abstand_sigma, rausch):
    """Hubfaktor so, dass das kleinste lineare Zellminimum aller Konfigurationen bei 5σ_c + abstand·σ_c liegt."""
    s0 = system('V1-G60h')
    ziel = (5.0 + abstand_sigma) * rausch.sigma_zelle

    def zmin(h):
        s = s0.mit(hub=tuple(np.asarray(s0.hub) * h))
        m = Generatormodell(s, rauschen.RAUSCHFREI, kampagne.Plan())
        return wahrheit.berechne(m, kampagne.schnitt_konfigurationen(m.plan))[0]['zellminimum_min_N']

    lo, hi = 0.5, 4.0
    if not zmin(lo) > ziel > zmin(hi):
        raise ValueError('S01a: Zielminimum außerhalb des Hubbereichs')
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if zmin(mid) > ziel else (lo, mid)
    h = 0.5 * (lo + hi)
    return s0.mit(name=f'V1-G60h-hub{h:.4f}', hub=tuple(np.asarray(s0.hub) * h))


def modell(sz, stufe='L2', plan=None, staerke=None, rausch=None):
    """Generatormodell eines Szenarios (sz: Szenario oder ID). staerke: Effektstärke; ohne Angabe die Plangröße oder,
    bei einem Zielverhältnis, das Ergebnis der Nullstellensuche auf der Wahrheit."""
    sz = KATALOG[sz] if isinstance(sz, str) else sz
    rausch = _rausch(sz, stufe) if rausch is None else rausch
    p = _plan(sz, plan)
    if staerke is None:
        staerke = staerke_suchen(sz, p)[0] if sz.ziel else sz.staerke
    s = _system(sz, staerke, rausch)
    eff = _effekte(sz, staerke)
    if sz.hertz is not None:
        if p.einstellung2:
            raise ValueError('Hertz-Fall nur für Einstellung 1 tabelliert')
        konf = [(k['konfiguration']['id'], tuple(k['konfiguration']['phi_soll_grad'][1:]))
                for k in kampagne.schnitt_konfigurationen(p)]
        konf += [(f'P{a:g}_{b:g}', (a, b)) for a, b in kv.PILOTEN]
        tab = _hertz_tabelle(sz.hertz['f_n0'], sz.hertz['zeta'], tuple(konf))
        eff = eff + ({'art': 'hertz', 'tabelle': tab},)
    return Generatormodell(s, rausch, p, eff, szenario=sz.id, staerke=staerke)


def staerke_suchen(sz, plan=None, tol=1e-10, max_iter=200):
    """Effektstärke x mit r(x) = Ziel (r: größtes wahres Residuum relativ zu Δ_rel gegen beide Vorhersagen, über
    alle 147 Tests oder eine Größe), Regula falsi (Illinois) auf dem Bereich des Szenarios. Rückgabe (x, r(x))."""
    sz = KATALOG[sz] if isinstance(sz, str) else sz
    p = _plan(sz, plan)
    z = sz.ziel
    konf = kampagne.schnitt_konfigurationen(p)

    def r(x):
        m = Generatormodell(_system(sz, x, rauschen.RAUSCHFREI), rauschen.RAUSCHFREI, p, _effekte(sz, x))
        out = wahrheit.berechne(m, konf)[0]
        if z.get('groesse') is None:
            return out['r_max_rel_beide']
        g = z['groesse']
        if g.startswith('N'):
            return max(out['r_max_rel_je_groesse'][f'Re_{g}'], out['r_max_rel_je_groesse'][f'Im_{g}'])
        return out['r_max_rel_je_groesse'][g]

    lo, hi = z['bereich']
    flo, fhi = r(lo) - z['wert'], r(hi) - z['wert']
    if flo * fhi > 0:
        raise ValueError(f'{sz.id}: Ziel {z["wert"]} nicht im Bereich {z["bereich"]}')
    seite = 0
    for _ in range(max_iter):
        x = (lo * fhi - hi * flo) / (fhi - flo)
        fx = r(x) - z['wert']
        if abs(fx) <= tol * max(1.0, z['wert']):
            return x, fx + z['wert']
        if fx * fhi > 0:
            hi, fhi = x, fx
            if seite == -1:
                flo /= 2
            seite = -1
        else:
            lo, flo = x, fx
            if seite == 1:
                fhi /= 2
            seite = 1
    raise RuntimeError(f'{sz.id}: Stärkesuche konvergiert nicht')


def beschreibung(m):
    """Maschinenlesbare Beschreibung eines Generatormodells (für den Katalog-Hash und die Wahrheit)."""
    from dataclasses import asdict

    def rein(v):
        if isinstance(v, dict):
            return {k: rein(x) for k, x in v.items() if k != 'tabelle'}
        if isinstance(v, (list, tuple)):
            return [rein(x) for x in v]
        if isinstance(v, np.ndarray):
            return v.tolist()
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        if isinstance(v, float) and not np.isfinite(v):
            return str(v)
        return v
    s = asdict(m.system)
    return rein(dict(szenario=getattr(m, 'szenario', None), staerke=getattr(m, 'staerke', None), system=s,
                     rauschen=asdict(m.rausch), plan=asdict(m.plan), effekte=list(m.effekte), k_voll=m.k_voll,
                     vollausschlag_N=m.vollausschlag_N,
                     hertz=None if m.hertz is None else m.hertz['modell']))


def katalog_tabelle():
    """Katalog als Liste von dicts (ohne Funktionen) für Dokumentation und Prüfsatz."""
    out = []
    for s in KATALOG.values():
        out.append(dict(id=s.id, plan_id=s.plan_id, titel=s.titel, art=s.art, hypothesen=list(s.hypothesen),
                        erwartung=s.erwartung, staerke=s.staerke, ziel=s.ziel, ebenen=list(s.ebenen),
                        kalibrierung=[[a, b] for a, b in s.kalibrierung], abweichung=s.abweichung,
                        plan=[[a, b] for a, b in s.plan]))
    return out
