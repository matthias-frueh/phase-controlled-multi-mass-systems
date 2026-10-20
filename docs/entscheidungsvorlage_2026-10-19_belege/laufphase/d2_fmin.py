# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 5.1 (F_min-Faktor 1,96–2,76 bei L0, 1,05–1,27 bei L1).
# Zweck: d2 auf F_min − ⟨N⟩ des Laufmittels erweitert: Faktor je Punkt für L0 und L1 (Monte Carlo).
# Eingaben: Code des Repositorys (generator/systeme, vorhersage). Seed: default_rng(5); n = 20 000 je Punkt.
# Laufzeit: gemessen 10 s Wandzeit, 10 s CPU (ein Prozess, ein Thread, 20.10.2026). Aufruf: PCMMS_REPO=<auszug 0f63187> python3 -B d2_fmin.py > d2_fmin.out
# Herkunft: Nachprüfung 6. Geändert: Code-Pfad.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: d2 auf F_min − ⟨N⟩ (k ≤ k_max) des Laufmittels erweitert: Faktor √(Var gesamt / Var ohne erfassten Anteil) je
# Punkt, Stufen L0/L1, Struktur aus generator/systeme.antworten, Laufgrößen wie ebene_h.py (Versatz 0,05°, Jitter 0,2°
# je Zyklus über N_z = 100, δ und Amplitude je Stufe, weißes Rauschen der Summe je Re/Im √3·σ_h).
import sys
import numpy as np
import os
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(HIER, '..', '..', '..'))   # Kopf
sys.path.insert(0, os.path.join(REPO, 'code'))
from pcmms_auswertung.generator import systeme
from pcmms_auswertung import vorhersage as vh
rng = np.random.default_rng(5)
rad = np.pi / 180
sz = 0.02 / np.sqrt(3); sh = sz * np.sqrt(2.0 / (6400.0 * 10.0))
n, Nz = 20000, 100
for name in ('A4', 'V1-G0'):
    s = systeme.system(name); K = s.k_max
    E = systeme.antworten(s, k_voll=K).Ns_kraft[:, :K]; k = np.arange(1, K + 1)
    for st, (a, p) in (('L0', (0.0, 0.02)), ('L1', (0.003, 0.03))):
        out = []
        for p2, p3 in ((100.0, 240.0), (110.0, 240.0), (118.0, 240.0), (120.0, 240.0), (130.0, 240.0), (110.0, 250.0), (130.0, 230.0)):
            phi = np.array([0.0, p2, p3])
            A = 1 + a * rng.standard_normal((n, 3)); dl = p * rng.standard_normal((n, 3))
            off = np.zeros((n, 3)); off[:, 1:] = 0.05 * rng.standard_normal((n, 2))
            jm = np.zeros((n, 3)); jm[:, 1:] = 0.2 / np.sqrt(Nz) * rng.standard_normal((n, 2))     # Laufmittel des Jitters
            w = np.sqrt(3) * sh * (rng.standard_normal((n, K)) + 1j * rng.standard_normal((n, K)))
            def F(capt):
                ph = phi[None] + dl + (off + jm if capt else 0.0)
                Z = np.exp(-1j * rad * ph[:, :, None] * k[None, None, :]) * A[:, :, None]
                return vh.fmin_rel_viele(np.einsum('njk,jk->nk', Z, E) + w)
            v1, v0 = F(True).var(), F(False).var()
            out.append(f'({p2:g},{p3:g}) {np.sqrt(v1/v0):.2f}')
        print(f'{name} {st}: F_min-Faktor ' + '; '.join(out))
