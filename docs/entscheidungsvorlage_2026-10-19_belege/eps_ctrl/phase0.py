# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 3.1 und 5.4.
# Zweck: Modul. Phase 0 auf Ebene der Teststatistik ⟨N⟩: σ̂_ref (Summe, Zellen) aus Leave-one-out-Werten gleich
#   getakteter Referenzläufe, s_d der anderen Läufe gegen die Interpolation, F-Test nach A9.8, ε_ctrl = 3·σ̂.
# Annahmen: ⟨N⟩ normal, σ = 1 (Summe), Zellen σ/√3 unabhängig, keine Drift; Anordnung n_ref Referenzläufe mit je
#   „je“ anderen Läufen dazwischen (Generator: 61 R, je 2; Variante 42 R ebenfalls je 2).
# Seed: vom Aufrufer (numpy-Generator). Laufzeit: Modul.
# Herkunft: Nachprüfung 1. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Phase-0-Teststatistik: σ̂_ref (Summe, Zellen), s_d, F-Test (A9.8), ε_ctrl; σ = 1 für ⟨N⟩ (Summe), Zellen σ/√3."""
import numpy as np


def layout(n_ref, je):
    """Zeitpositionen: Referenzläufe im Abstand je+1, dazwischen je andere Läufe (β = 1/(je+1) … je/(je+1))."""
    be = np.tile(np.arange(1, je + 1) / (je + 1.0), n_ref - 1)
    ai = np.repeat(np.arange(n_ref - 1), je)
    return be, ai


def simuliere(nsim, rng, n_ref=61, je=2, ftest=True, krit=None, block=20000):
    """Rückgabe dict mit eps, sref, sref_c (nsim×3), sd, F, betr (bool), krit."""
    be, ai = layout(n_ref, je)
    nrm = np.sqrt(1.5 / (1 + be ** 2 + (1 - be) ** 2))
    out = {k: [] for k in ('sref', 'sref_c', 'sd', 'F')}
    for s0 in range(0, nsim, block):
        m = min(block, nsim - s0)
        Rc = rng.standard_normal((m, n_ref, 3)) / np.sqrt(3)        # Zellen
        Oc = rng.standard_normal((m, ai.size, 3)) / np.sqrt(3)
        R, O = Rc.sum(-1), Oc.sum(-1)
        loo = R[:, 1:-1] - 0.5 * (R[:, :-2] + R[:, 2:])
        looc = Rc[:, 1:-1] - 0.5 * (Rc[:, :-2] + Rc[:, 2:])
        d = (O - ((1 - be) * R[:, ai] + be * R[:, ai + 1])) * nrm
        sref = loo.std(1, ddof=1)
        sd = d.std(1, ddof=1)
        out['sref'].append(sref); out['sref_c'].append(looc.std(1, ddof=1))
        out['sd'].append(sd); out['F'].append(sd ** 2 / sref ** 2)
    o = {k: np.concatenate(v) for k, v in out.items()}
    if ftest:
        if krit is None:
            krit = float(np.quantile(o['F'], 0.95))
        o['betr'] = o['F'] > krit
    else:
        o['betr'] = np.zeros(nsim, bool)
    o['krit'] = krit
    o['eps'] = 3 * np.where(o['betr'], o['sd'], o['sref'])
    return o
