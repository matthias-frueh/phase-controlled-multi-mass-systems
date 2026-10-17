"""Kampagnenplan nach Präreg §5.2, §6, A9.2 und A9.12: Phase 0 (P0.7 Referenzläufe, P0.8 Einzelmodulläufe,
Pilotläufe, bei Einstellung 2 Lⱼ′) und Phase 1 (Blöcke mit Kontrollsätzen, Referenzlauf nach der zwölften
Konfiguration, Messtage mit Aufwärm- und Schlussreferenzlauf). Die Reihenfolge der Phase 1 zieht ein gesäter
Generator nach der Regel von §6, bis Werkzeug 7 (AP-10) vorliegt. Wiederholungen ungültiger Läufe sind nicht
abgebildet (Gültigkeit entscheidet die Auswertung offline).

Phase 0: P0.7 verlangt mindestens 42 Referenzläufe, „je einer nach zwölf anderen Läufen“. Bei wenigen anderen Läufen
reicht der Abstand 12 dafür nicht; der Generator setzt dann einen Referenzlauf nach je ⌊n_andere/41⌋ (höchstens
12) anderen Läufen (Entwicklungsannahme, Präreg legt die Phase-0-Reihenfolge nicht fest).
"""
from dataclasses import dataclass, replace

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

    def mit(self, **kw):
        return replace(self, **kw)


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
    abstand = max(1, min(plan.ref_abstand, len(andere) // (plan.ref_min_p0 - 1)))
    ref = _konf('R', 'referenz')
    neu(ref, 0, None, 1)
    for i, spec in enumerate(andere):
        neu(spec, 0, None, 1)
        if (i + 1) % abstand == 0:
            neu(ref, 0, None, 1)
    if laeufe[-1]['laufart'] != 'R':
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
