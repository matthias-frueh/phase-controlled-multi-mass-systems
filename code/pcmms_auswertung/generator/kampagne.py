"""Kampagnenplan nach Präreg §5.2, §6, A9.2 und A9.12: Phase 0 (P0.7 Referenzläufe, P0.8 Einzelmodulläufe,
Pilotläufe, bei Einstellung 2 Lⱼ′) und Phase 1 (Blöcke mit Kontrollsätzen, Referenzlauf nach der zwölften
Konfiguration, Messtage mit Aufwärm- und Schlussreferenzlauf). Die Reihenfolge der Phase 1 zieht ein gesäter
Generator nach der Regel von §6, bis Werkzeug 7 (AP-10) vorliegt. Dieser Laufplan ist die geplante Reihenfolge; im
statischen Ablauf wird er unverändert gemessen (Gültigkeit entscheidet die Auswertung offline). Wiederholungen,
eingefügte Referenzläufe, Halt und verschobene Zeiten führt der zustandsbehaftete Ablauf (ablauf.py) aus, mit demselben
Generator für die Wiederholungsplätze.

Phase 0 (P0.7, Anordnung der Referenzläufe, Plan.p0_anordnung):
  p07         Arbeitsfestlegung vom 20.10.2026 (Regel p0.anordnung): mindestens 42 Referenzläufe, höchstens zwölf andere
              Läufe zwischen zwei Referenzläufen („nach zwölf“ als größter Abstand); die Referenzläufe stehen am Anfang,
              am Ende und möglichst gleichmäßig dazwischen. Bei 120 anderen Läufen sind das 42 Referenzläufe mit
              Abständen von zwei oder drei Läufen. Vorgabe.
  historisch  Anordnung bis PR #23: ein Referenzlauf nach je ⌊n_andere/41⌋ (höchstens 12) anderen Läufen, also bei
              120 anderen Läufen 61 Referenzläufe im Abstand 2. Zur Nachrechnung historischer Ergebnisse; gespeicherte
              Pläne ohne das Feld p0_anordnung stammen aus dieser Zeit (plan_aus_dict).
Ohne übergebenen Plan wählen die Einstiege der Harness und die CLI die Anordnung nach dem Regelprofil (plan_vorgabe):
'historisch' unter den historischen Profilen (AF/ENTW-2026-10), sonst 'p07'. Ein übergebener Plan gilt, wie er ist.
"""
import math
from dataclasses import asdict, dataclass, replace

import numpy as np

from .. import konventionen as kv
from .. import zusammenfassung as zf


@dataclass(frozen=True)
class Plan:
    n0: int = 20                    # P0.8 je Modul
    n_pilot: int = 20               # je Pilotkonfiguration
    n_bloecke: int = 20             # Phase 1: n Blöcke
    tage: int = 1                   # d Messtage der Phase 1
    zusatz: bool = False            # (0°, 0°) und (0°, 180°)
    pruef: tuple = ()               # weitere Konfigurationen (φ₂, φ₃) der Gruppe „pruef“ (Prüffälle)
    pruef_bilder: bool = True       # je Prüfkonfiguration alle sechs S₃-Bilder (kv.s3_bilder)
    einstellung2: object = None     # dict(art='amplitude'|'frequenz', s=…, f2=…, punkte_I=(…), n0_strich=…, L_strich=True)
    n_zyklen: int = 100             # Zyklen im Auswertefenster (T_a·f)
    T_lauf: float = 17.0            # s je Lauf (T_park + T_ramp + T_e + T_a + T_ab)
    ref_abstand: int = 12
    ref_min_p0: int = 42
    tag_pause: float = 43200.0      # s zwischen Messtagen
    phase_pause: float = 86400.0    # s zwischen Phase 0 und Phase 1
    p0_anordnung: str = 'p07'       # 'p07' (Arbeitsfestlegung 20.10.2026) oder 'historisch' (bis PR #23)

    def __post_init__(self):
        if self.p0_anordnung not in P0_ANORDNUNGEN:
            raise ValueError(f'Phase-0-Anordnung {self.p0_anordnung!r} unbekannt ({", ".join(P0_ANORDNUNGEN)})')

    def mit(self, **kw):
        return replace(self, **kw)


P0_ANORDNUNGEN = ('p07', 'historisch')


def plan_dict(plan):
    """Plan als dict für Herkunft und Prüfsummen. Die historische Anordnung erscheint wie in den gespeicherten Plänen
    bis PR #23 ohne das Feld p0_anordnung (bitgleiche Herkunft historischer Ergebnisse)."""
    d = asdict(plan)
    if d.get('p0_anordnung') == 'historisch':
        d.pop('p0_anordnung')
    return d


def plan_vorgabe(profil=None, **kw):
    """Plan mit der Phase-0-Anordnung des Regelprofils: 'historisch' unter historischen Profilen (regeln.ist_historisch),
    sonst die Vorgabe 'p07'; ohne Profil 'p07'. kw: übrige Planfelder; eine ausdrückliche p0_anordnung gilt."""
    from .. import regeln
    if 'p0_anordnung' not in kw and profil is not None and regeln.ist_historisch(profil):
        kw['p0_anordnung'] = 'historisch'
    return Plan(**kw)


def plan_aus_dict(d):
    """Plan aus einem gespeicherten dict; fehlt p0_anordnung, stammt der Plan aus der Zeit bis PR #23 (historisch)."""
    d = dict(d)
    d.setdefault('p0_anordnung', 'historisch')
    return Plan(**d)


def p0_referenzplaetze(n_andere, plan):
    """Nach wie vielen anderen Läufen jeweils ein Referenzlauf folgt (Liste der Abschnittslängen); vor dem ersten
    Abschnitt steht ein Referenzlauf. p07: ≥ ref_min_p0 Referenzläufe, Abschnitte ≤ ref_abstand, gleichmäßig."""
    if n_andere == 0:
        return []
    n_ref = max(plan.ref_min_p0, math.ceil(n_andere / plan.ref_abstand) + 1)
    n_ref = min(n_ref, n_andere + 1)
    return [len(x) for x in np.array_split(np.arange(n_andere), n_ref - 1)]


def _konf(laufart, gruppe, phi=None, modul=None, einstellung=1):
    return dict(laufart=laufart, modul=modul, einstellung=einstellung,
                konfiguration=dict(id=zf.konfig_id(laufart, phi, modul, einstellung, gruppe), gruppe=gruppe,
                                   phi_soll_grad=None if phi is None else [float(x) for x in phi]))


def schnitt_konfigurationen(plan):
    out = [_konf('K', 'schnitt', (0.0, p2, kv.SCHNITT_PHI3)) for p2 in kv.SCHNITT_PHI2]
    if plan.zusatz:
        out += [_konf('K', 'zusatz', (0.0, 0.0, 0.0)), _konf('K', 'zusatz', (0.0, 0.0, 180.0))]
    for p2, p3 in plan.pruef:
        for _, (q2, q3), _ in kv.s3_bilder(p2, p3) if plan.pruef_bilder else [(None, (p2, p3), None)]:
            k = _konf('K', 'pruef', (0.0, float(q2), float(q3)))
            if k['konfiguration']['id'] not in [x['konfiguration']['id'] for x in out]:
                out.append(k)
    if plan.einstellung2:
        out += [_konf('K', 'identifizierbarkeit', (0.0, p2, kv.SCHNITT_PHI3), einstellung=2)
                for p2 in plan.einstellung2['punkte_I']]
    return out


def konfigurationsliste(plan):
    """Konfigurationsliste von Teil B in der Reihenfolge von §6 (Schnitt aufsteigend, Zusatz, Punkte I bei
    Einstellung 2); bestimmt die Reihenfolge der Bootstrap-Ziehungen."""
    return [k['konfiguration']['id'] for k in schnitt_konfigurationen(plan)]


def laufplan(plan, rng):
    """Liste der Läufe mit Kopfdaten (ohne Messwerte) in Laufreihenfolge."""
    e2 = plan.einstellung2
    laeufe = []

    def neu(spec, phase, block, messtag, kontrollsatz=None):
        pos = len(laeufe)
        d = dict(spec)
        d.update(phase=phase, block=block, messtag=messtag, position=pos, kontrollsatz=kontrollsatz)
        d['lauf_id'] = f'{phase}-{pos:05d}-{d["konfiguration"]["id"]}'
        laeufe.append(d)

    # Phase 0
    einzel = [_konf('L', 'einzel', modul=j) for _ in range(plan.n0) for j in (1, 2, 3)]
    piloten = [_konf('K', 'pilot', (0.0, p2, p3)) for _ in range(plan.n_pilot) for p2, p3 in kv.PILOTEN]
    strich = ([_konf('L', 'einzel', modul=j, einstellung=2) for _ in range(e2.get('n0_strich', 20)) for j in (1, 2, 3)]
              if e2 else [])
    andere = []
    quellen = [einzel, piloten, strich]
    while any(quellen):
        for q in quellen:
            if q:
                andere.append(q.pop(0))
    ref = _konf('R', 'referenz')
    neu(ref, 0, None, 1)
    if plan.p0_anordnung == 'historisch':
        abstand = max(1, min(plan.ref_abstand, len(andere) // (plan.ref_min_p0 - 1)))
        for i, spec in enumerate(andere):
            neu(spec, 0, None, 1)
            if (i + 1) % abstand == 0:
                neu(ref, 0, None, 1)
        if laeufe[-1]['laufart'] != 'R':
            neu(ref, 0, None, 1)
    else:
        it = iter(andere)
        for laenge in p0_referenzplaetze(len(andere), plan):
            for _ in range(laenge):
                neu(next(it), 0, None, 1)
            neu(ref, 0, None, 1)
    # Phase 1
    konf = schnitt_konfigurationen(plan)
    kontroll = [ref] + [_konf('L', 'einzel', modul=j) for j in (1, 2, 3)]
    if e2 and e2.get('L_strich', True):
        kontroll += [_konf('L', 'einzel', modul=j, einstellung=2) for j in (1, 2, 3)]
    tage = np.array_split(np.arange(plan.n_bloecke), plan.tage)
    ks = 0
    for t, bloecke in enumerate(tage, start=1):
        neu(ref, 1, None, t)                                         # letzter Aufwärm-Referenzlauf
        for b in bloecke:
            if b == bloecke[0]:
                ks += 1
                for i in rng.permutation(len(kontroll)):
                    neu(kontroll[i], 1, int(b) + 1, t, ks)
            for n_k, i in enumerate(rng.permutation(len(konf)), start=1):
                neu(konf[i], 1, int(b) + 1, t)
                if n_k == 12:
                    neu(ref, 1, int(b) + 1, t)
            ks += 1
            for i in rng.permutation(len(kontroll)):
                neu(kontroll[i], 1, int(b) + 1, t, ks)
        neu(ref, 1, None, t)                                         # Schlussreferenzlauf
    # Zeiten
    t, tag_alt, phase_alt = 0.0, 1, 0
    for l in laeufe:
        if l['phase'] != phase_alt:
            t += plan.phase_pause
            phase_alt, tag_alt = l['phase'], l['messtag']
        elif l['messtag'] != tag_alt:
            t += plan.tag_pause
            tag_alt = l['messtag']
        l['t_start'], l['t_ende'] = t, t + plan.T_lauf
        t += plan.T_lauf
    return laeufe


def zaehlung(laeufe):
    """Läufe je Phase und Laufart (zur Kontrolle gegen A9.12: (N_K + N_I + 8)·n + 8·d bzw. (N_K + 5)·n + 5·d)."""
    out = {}
    for l in laeufe:
        key = (l['phase'], l['laufart'], l['einstellung'])
        out[key] = out.get(key, 0) + 1
    return out
