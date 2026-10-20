"""Simulationsverfahren einer synthetischen Kampagne: Bindung der Phase-0-Größen und Ablauf der Phase 1.

Bindung (teil_b.phase0_satz):
  plan        Gültigkeitsmasken, σ_Δ, σ̂_ref, ε_ctrl, p̂, Streuungen und Kovarianzen der Phase 0 bei k_max und N_z des
              tatsächlich verwendeten Plans (ab teil_b-0.3, Vorgabe).
  historisch  vorläufiger Satz bei k der Pilotgrößen wie bis teil_b-0.2 (PR #20 bis #22); nur ausdrücklich, zur
              Nachrechnung historischer Ergebnisse, im Teil B als nicht qualifizierend gekennzeichnet.

Ablauf der Phase 1:
  statisch    der gezogene Laufplan wird ohne Ablaufentscheidungen gemessen (Generator ebene_h.erzeuge); Gültigkeit
              entscheidet die Auswertung offline (bis PR #22, Vorgabe des Harness).
  zustand     zustandsbehafteter Ablauf mit Wiederholungen, Alarmbehandlung, Halt und fortgeschriebener Messzeit
              (ablauf.Ablauf, Optionen ablauf.Ablaufoptionen); Phase 0 wie im Laufplan. Mit allen Optionen aus
              entstehen dieselben Laufzusammenfassungen wie bei „statisch“.

Fassung des zustandsbehafteten Ablaufs (fassung): „ablauf-4“ (Vorgabe, Auftrag vom 20.10.2026) oder „ablauf-3“
(Stand von PR #23, nur zur Nachrechnung historischer Ergebnisse). Die Fassung steht als ablauf_version in der Kennung;
die Kennung der Fassung ablauf-3 ist dieselbe wie bis PR #23.

Die Kennung (kennung()) gehört in die Herkunft jeder Kampagne und in Checkpoint-Schlüssel; ein Checkpoint eines anderen
Verfahrens wird nicht übernommen. Ein angefordertes Verfahren wird nie stillschweigend durch ein anderes ersetzt.
"""
from dataclasses import asdict, dataclass

from .ablauf import FASSUNGEN as ABLAUF_FASSUNGEN, VERSION as ABLAUF_VERSION, Ablaufoptionen

VERSION = 'verfahren-1'
BINDUNGEN = ('plan', 'historisch')
ABLAEUFE = ('statisch', 'zustand')


@dataclass(frozen=True)
class Verfahren:
    bindung: str = 'plan'
    ablauf: str = 'statisch'
    optionen: object = None
    fassung: str = None

    def __post_init__(self):
        if self.bindung not in BINDUNGEN:
            raise ValueError(f'Bindung {self.bindung!r} unbekannt ({", ".join(BINDUNGEN)})')
        if self.ablauf not in ABLAEUFE:
            raise ValueError(f'Ablauf {self.ablauf!r} unbekannt ({", ".join(ABLAEUFE)})')
        if self.ablauf == 'zustand' and not isinstance(self.optionen, Ablaufoptionen):
            raise ValueError('Ablauf „zustand“ verlangt ablauf.Ablaufoptionen')
        if self.ablauf == 'statisch' and self.optionen is not None:
            raise ValueError('Ablauf „statisch“ hat keine Ablaufoptionen')
        if self.ablauf == 'statisch':
            if self.fassung is not None:
                raise ValueError('Ablauf „statisch“ hat keine Ablauffassung')
        elif self.fassung is None:
            object.__setattr__(self, 'fassung', ABLAUF_VERSION)
        elif self.fassung not in ABLAUF_FASSUNGEN:
            raise ValueError(f'Ablauffassung {self.fassung!r} unbekannt ({", ".join(ABLAUF_FASSUNGEN)})')

    def kennung(self):
        return dict(version=VERSION, bindung=self.bindung, ablauf=self.ablauf,
                    ablauf_version=self.fassung if self.ablauf == 'zustand' else None,
                    optionen=None if self.optionen is None else asdict(self.optionen))


HISTORISCH = Verfahren('historisch', 'statisch')
STATISCH = Verfahren('plan', 'statisch')
ZUSTAND = Verfahren('plan', 'zustand', Ablaufoptionen())
ZUSTAND_HISTORISCH = Verfahren('plan', 'zustand', Ablaufoptionen(), 'ablauf-3')     # Stand PR #23
STANDARD = STATISCH


def oder_standard(v):
    return STANDARD if v is None else v


def aus_kennung(k):
    """Verfahren aus seiner Kennung (Prüfung der Version)."""
    if k.get('version') != VERSION:
        raise ValueError(f'Verfahrenskennung der Version {k.get("version")} ≠ {VERSION}')
    return Verfahren(k['bindung'], k['ablauf'], None if k.get('optionen') is None else Ablaufoptionen(**k['optionen']),
                     k.get('ablauf_version'))
