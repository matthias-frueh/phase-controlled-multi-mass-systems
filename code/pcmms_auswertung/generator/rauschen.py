"""Rauschmodelle des Generators, getrennt nach Laufart (Plan AP-13, Abschnitt 2.2), und Präzisionsstufen L0–L5.

Komponenten je Lauf: weißes Sensorrauschen je Zelle (σ je Abtastwert; auf Ebene H über Re/Im N_k mit
σ·√(2/(f_s·T_a)) und ⟨N_c⟩ mit σ/√(f_s·T_a)), Lauf-zu-Lauf-Streuung der Amplitude und ein nicht erfasster
Phasenrest Encoder ↔ Masse je bewegtem Modul (getrennt für Einzelmodul- und Kombinationsläufe), Jitter je Zyklus
der Module 2 und 3 gegen Modul 1 (über die gemessenen Zeiger ρⱼₖ erfasst), ein erfasster Versatz der Laufmittel der
Indexphasen (prüft G2), Nullpunktdrift über die Zeit (prüft H0 über die Interpolation) und Drift innerhalb eines
Laufs (prüft G4). Die Stufen sind ein Raster, keine Erwartung für eine Apparatur (Plan 2.2).
"""
from dataclasses import dataclass, replace

import numpy as np

SIGMA_SUMME_REF = 20e-3          # N je Abtastwert der Summe (Plan 2.2: 1–20 mN; P2-Statistik L0: σ_h = 0,11 mN)
F_S_REF = 6400.0                 # Abtastrate der P2-Rechnung für die Umrechnung auf Harmonische (Ebene H)


@dataclass(frozen=True)
class Rauschmodell:
    name: str = 'L0'
    sigma_zelle: float = SIGMA_SUMME_REF / np.sqrt(3)    # N je Abtastwert und Zelle, unabhängig je Zelle
    f_s_bezug: float = F_S_REF
    amp: tuple = (('L', 0.0), ('K', 0.0))                # relative Amplitudenstreuung je bewegtem Modul
    phase_grad: tuple = (('L', 0.02), ('K', 0.02))       # nicht erfasster Phasenrest je bewegtem Modul [°]
    jitter_grad: float = 0.2                             # je Zyklus, Module 2, 3 gegen Modul 1 (erfasst) [°]
    index_versatz_grad: float = 0.05                     # Laufmittel der Indexphase gegen Soll (erfasst) [°]
    nullpunkt_drift_N_je_s: float = 0.0
    lauf_drift_N: float = 0.0                            # lineare Drift von ⟨N⟩ über einen Lauf (Summe) [N]
    t_phi_s: tuple = (0.6, 0.05)                         # Einregelzeit der Phasen: Mittel, Streuung [s]
    f_streuung_hz: float = 1e-5
    temperatur_C: tuple = (22.0, 0.005)                  # Zelltemperatur und Streuung innerhalb eines Laufs

    def a(self, laufart):
        return dict(self.amp)['L' if laufart == 'L' else 'K']

    def p(self, laufart):
        return dict(self.phase_grad)['L' if laufart == 'L' else 'K']

    def sigma_h(self, T_a):
        """Streuung von Re und Im einer Zellharmonischen (Ebene H)."""
        return self.sigma_zelle * np.sqrt(2.0 / (self.f_s_bezug * T_a))

    def sigma_mittel(self, T_a):
        return self.sigma_zelle / np.sqrt(self.f_s_bezug * T_a)

    def mit(self, **kw):
        return replace(self, **kw)


def stufe(name, **kw):
    """Präzisionsstufen L0–L5 wie die P2-Statistik und die AP-08-Kontrolle (Amplitude / Phase je bewegtem Modul)."""
    werte = {'L0': (0.0, 0.02), 'L1': (0.003, 0.03), 'L2': (0.01, 0.10), 'L3': (0.03, 0.30), 'L4': (0.06, 0.60),
             'L5': (0.10, 1.00)}
    if name not in werte:
        raise KeyError(f'Stufe {name!r} unbekannt (L0–L5)')
    a, p = werte[name]
    r = Rauschmodell(name=name, amp=(('L', a), ('K', a)), phase_grad=(('L', p), ('K', p)))
    return r.mit(**kw) if kw else r


def getrennt(name, amp_L, amp_K, phase_L, phase_K, **kw):
    """Rauschmodell mit getrennten Streuungen für Einzelmodul- (L) und Kombinationsläufe (K)."""
    return Rauschmodell(name=name, amp=(('L', amp_L), ('K', amp_K)), phase_grad=(('L', phase_L), ('K', phase_K)),
                        **kw)


RAUSCHFREI = Rauschmodell(name='rauschfrei', sigma_zelle=0.0, amp=(('L', 0.0), ('K', 0.0)),
                          phase_grad=(('L', 0.0), ('K', 0.0)), jitter_grad=0.0, index_versatz_grad=0.0,
                          t_phi_s=(0.6, 0.0), f_streuung_hz=0.0, temperatur_C=(22.0, 0.0))
