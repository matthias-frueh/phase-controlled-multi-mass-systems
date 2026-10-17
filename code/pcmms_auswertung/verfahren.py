"""Simulationsverfahren einer synthetischen Kampagne: Bindung der Phase-0-Größen und Ablauf der Phase 1.

Bindung (teil_b.phase0_satz):
  plan        Gültigkeitsmasken, σ_Δ, σ̂_ref, ε_ctrl, p̂, Streuungen und Kovarianzen der Phase 0 bei k_max und N_z des
              tatsächlich verwendeten Plans (ab teil_b-0.3, Vorgabe).
  historisch  vorläufiger Satz bei k der Pilotgrößen wie bis teil_b-0.2 (PR #20 bis #22); nur ausdrücklich, zur
              Nachrechnung historischer Ergebnisse, im Teil B als nicht qualifizierend gekennzeichnet.

Ablauf der Phase 1:
  statisch    der gezogene Laufplan wird ohne Ablaufentscheidungen gemessen; Gültigkeit entscheidet die Auswertung
              offline (bis PR #22, Vorgabe des Harness).

Die Kennung (kennung()) gehört in die Herkunft jeder Kampagne und in Checkpoint-Schlüssel; ein Checkpoint eines anderen
Verfahrens wird nicht übernommen.
"""
from dataclasses import asdict, dataclass

VERSION = 'verfahren-1'
BINDUNGEN = ('plan', 'historisch')
ABLAEUFE = ('statisch',)


@dataclass(frozen=True)
class Verfahren:
    bindung: str = 'plan'
    ablauf: str = 'statisch'
    optionen: object = None

    def __post_init__(self):
        if self.bindung not in BINDUNGEN:
            raise ValueError(f'Bindung {self.bindung!r} unbekannt ({", ".join(BINDUNGEN)})')
        if self.ablauf not in ABLAEUFE:
            raise ValueError(f'Ablauf {self.ablauf!r} unbekannt ({", ".join(ABLAEUFE)})')

    def kennung(self):
        return dict(version=VERSION, bindung=self.bindung, ablauf=self.ablauf,
                    optionen=None if self.optionen is None else asdict(self.optionen))


HISTORISCH = Verfahren('historisch', 'statisch')
STATISCH = Verfahren('plan', 'statisch')
STANDARD = STATISCH


def oder_standard(v):
    return STANDARD if v is None else v
