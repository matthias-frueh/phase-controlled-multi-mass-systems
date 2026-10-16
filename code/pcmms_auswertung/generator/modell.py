"""Generatormodell: System, Rauschmodell, Kampagnenplan und Effekte eines Szenarios.

Effekte (Liste von dicts mit Schlüssel „art“), bekannte Störungen des Generators; die Auswertung kennt sie nicht:
  kopplung            {x, harmonische=None}: Kombinationsläufe, alle Modulantworten × (1 − x) (Kopplung fester
                      relativer Stärke, A2.6, Plan A04)
  phasenversatz_k     {modul, grad}: nicht erfasster Phasenversatz eines Moduls nur in Kombinationsläufen (A06, H03)
  modul_k             {modul, faktor}: Amplitudenabweichung eines Moduls nur in Kombinationsläufen (H04)
  drift_basis         {faktor}: Phase 1, alle Läufe mit bewegten Modulen, Modulantwort × (1 + faktor[j])
                      (Drift der Einzelmodulbasis; ŷ¹ folgt, ŷ⁰ nicht)
  verstaerkung_p1     {faktor}: Phase 1, Zellverstärkung × (1 + faktor[c]) in allen Läufen (LTI je Phase, E07)
  kennlinie           {beta}: quadratische Kettenkennlinie N_c = F_c + β_c·F_c² im Zeitbereich (A2.6, A02, I02)
  hertz               {tabelle}: Kombinations- und Einzelantworten aus dem ereignisgenauen Löser (physik.hertz_fall)
  offset_k            {N}: zusätzliche statische Last nur in Kombinationsläufen (S04: H0, G1, S1)
  ereignis            {ereignis: saettigung|indexfehler|stoerung|lauf_drift|aufzeichnung|park|liftoff_zelle,
                      laeufe: [Positionen] oder auswahl: {konfiguration, phase, laufart, nummer}, zelle, modul,
                      wert}: Einzelereignisse für Gültigkeits- und Abbruchregeln (nummer: n-ter passender Lauf)
"""
from dataclasses import dataclass, field

import numpy as np

from . import rauschen
from .kampagne import Plan
from .systeme import antworten


@dataclass
class Generatormodell:
    system: object
    rausch: rauschen.Rauschmodell = field(default_factory=rauschen.Rauschmodell)
    plan: Plan = field(default_factory=Plan)
    effekte: tuple = ()
    k_voll: int = 60
    vollausschlag_N: float = 50.0          # Übersteuerung je Zelle (G5), Rechenannahme
    hertz: object = None                    # Tabelle aus physik.hertz_fall, wenn ein Effekt „hertz“ gilt
    szenario: object = None                 # Szenario-ID (Katalog), nur zur Herkunft
    staerke: object = None                  # Effektstärke des Szenarios, nur zur Herkunft

    def __post_init__(self):
        self._ant = {1: antworten(self.system, k_voll=self.k_voll)}
        e2 = self.plan.einstellung2
        if e2:
            if e2['art'] == 'amplitude':
                self._ant[2] = antworten(self.system, hub_faktor=e2['s'], k_voll=self.k_voll)
            elif e2['art'] == 'frequenz':
                self._ant[2] = antworten(self.system, f=e2['f2'], k_voll=self.k_voll)
            else:
                raise ValueError(f'Einstellung 2: Art {e2["art"]!r} unbekannt')
        for e in self.effekte:
            if e['art'] == 'hertz' and self.hertz is None:
                self.hertz = e['tabelle']

    def antwort(self, einstellung=1):
        return self._ant[einstellung]

    @property
    def delta_delta_grad(self):
        """Δδⱼ = δⱼ − δ₁ (Präreg A1), wie P0.5 sie misst."""
        d = np.asarray(self.system.delta_profil_grad, float)
        return d - d[0]

    def index_soll_grad(self, phi_profil):
        """Sollwert der Indexphase φⱼ,soll^P − Δδⱼ (A1: die Regelung stellt die Indexphase ein)."""
        return np.asarray(phi_profil, float) - self.delta_delta_grad

    def effekte_art(self, art):
        return [e for e in self.effekte if e['art'] == art]

    def ereignis_positionen(self, eff, laeufe):
        """Positionen der Läufe eines Ereignisses (Liste „laeufe“ oder Auswahl nach Konfiguration, Phase, Laufart)."""
        if 'laeufe' in eff:
            return list(eff['laeufe'])
        a = eff['auswahl']
        pos = [l['position'] for l in laeufe
               if l['konfiguration']['id'] == a.get('konfiguration', l['konfiguration']['id'])
               and l['phase'] == a.get('phase', l['phase']) and l['laufart'] == a.get('laufart', l['laufart'])]
        if 'nummer' in a:
            return [pos[a['nummer']]] if len(pos) > a['nummer'] else []
        return pos
