# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.1 (Tabelle MAD(D_F) an S120).
# Zweck: Nachbildung der Fünftel-Differenz D_F an allen Schnittpunkten und Piloten mit der Generatorstruktur und
#   den Parametern der Stufe L1, Varianten getrennt nach Laufgrößen (Sollphase, Indexversatz, δ, Amplitude).
# Eingaben: Code des Repositorys; Argument 1 = System (A4, V1-G0), 2 = Läufe je Punkt, 3 = Ausgabe (Standard
#   df_mc_<System>.json hier).
# Seed: default_rng(20261019). Die übernommenen Ausgaben haben N = 30 000 je Punkt und Variante (Feld "N" in
#   df_mc_*.json); der Standardwert im Skript ist 100 000.
# Laufzeit: 276 s (A4) bzw. 294 s (V1-G0) bei N = 30 000, siehe df_mc_*.out. Nicht neu gerechnet; Aufrufbarkeit mit N = 200
#   geprüft (README).
# Aufruf: PCMMS_REPO=<auszug 0f63187> python3 -B df_mc.py A4 30000 > df_mc_A4.out  (ebenso V1-G0 30000 > df_mc_V1G0.out)
# Herkunft: Nachprüfung 6. Geändert: Code-Pfad, Ausgabepfad als optionales Argument 3.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: Nachbildung der Fünftel-Differenz D_F (F_min − ⟨N⟩, k ≤ k_max) eines Kombinationslaufs auf Ebene H nach
# generator/ebene_h.py Z. 47–63, 154–158, 177–178 (Rauschmodell L1, rauschen.stufe), rauschfreie Struktur aus
# generator/systeme.antworten (N01: identische Module, Δδ = 0, keine Effekte). Statistikebene, keine Kampagne.
# Varianten schalten die Laufgrößen getrennt: Amplitude A, Phasenrest δ (nicht erfasst), Indexversatz (erfasst).
# Aufruf: python3 -B df_mc.py [System] [N] [Ausgabe.json]
import sys, json, time
import numpy as np
import os
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(HIER, '..', '..', '..'))   # Kopf
sys.path.insert(0, os.path.join(REPO, 'code'))
from pcmms_auswertung.generator import systeme
from pcmms_auswertung import vorhersage as vh, konventionen as kv

name = sys.argv[1] if len(sys.argv) > 1 else 'A4'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
s = systeme.system(name)
ant = systeme.antworten(s, k_voll=s.k_max)
K = s.k_max
E = ant.Ns_kraft[:, :K]                                    # (Modul, k) Summenharmonische, Bezug eigener Index
k = np.arange(1, K + 1)
Nz, nf, f, fs = 100, 20, 10.0, 6400.0
sz = 0.02 / np.sqrt(3)
sh = sz * np.sqrt(2.0 / (fs * Nz / f))
s_rausch = np.sqrt(15.0) * sh                              # je Re/Im der Summe in einem Fünftel (3 Zellen, √5)
PAR = dict(amp=0.003, delta=0.03, versatz=0.05, jitter=0.2)   # L1 (rauschen.py Z. 21–26, 52)
VAR = {'soll (nur Jitter + weiß)': dict(amp=0, delta=0, versatz=0),
       'nur Indexversatz 0,05° (erfasst)': dict(amp=0, delta=0),
       'nur δ 0,03° (nicht erfasst)': dict(amp=0, versatz=0),
       'nur Amplitude 0,3 %': dict(delta=0, versatz=0),
       'Phase gesamt (Versatz + δ)': dict(amp=0),
       'Generator L1 vollständig': dict()}
rad = np.pi / 180

def mad(x):
    return 1.4826 * np.median(np.abs(x - np.median(x)))

def df_ziehen(phi2, phi3, p, rng, n):
    A = 1 + p['amp'] * rng.standard_normal((n, 3))
    dl = p['delta'] * rng.standard_normal((n, 3))
    off = np.zeros((n, 3)); off[:, 1:] = p['versatz'] * rng.standard_normal((n, 2))
    phi = np.array([0.0, phi2, phi3])
    out = []
    for fu in range(2):
        jit = np.zeros((n, 3, nf)); jit[:, 1:, :] = p['jitter'] * rng.standard_normal((n, 2, nf))
        z = np.exp(-1j * rad * (phi[None, :, None] + off[:, :, None] + jit))     # (n, 3, nf)
        Zf = np.empty((n, 3, K), complex); P = np.ones_like(z)
        for i in range(K):
            P = P * z; Zf[:, :, i] = P.mean(-1)
        fak = A[:, :, None] * np.exp(-1j * k[None, None, :] * rad * dl[:, :, None])
        Nk = np.einsum('njk,jk->nk', fak * Zf, E)
        Nk = Nk + s_rausch * (rng.standard_normal(Nk.shape) + 1j * rng.standard_normal(Nk.shape))
        out.append(vh.fmin_rel_viele(Nk))
    return out[1] - out[0]

if __name__ == '__main__':
    rng = np.random.default_rng(20261019)
    res = {}
    t0 = time.time()
    pts = [(float(p2), kv.SCHNITT_PHI3) for p2 in kv.SCHNITT_PHI2] + list(kv.PILOTEN)
    for vn, ab in VAR.items():
        p = dict(PAR, **ab)
        res[vn] = []
        for (p2, p3) in pts:
            d = df_ziehen(p2, p3, p, rng, N)
            res[vn].append(dict(phi=[p2, p3], mad=float(mad(d)), sd=float(d.std()),
                                q=[float(x) for x in np.quantile(np.abs(d), [0.5, 0.9, 0.99, 0.999])]))
        print(f'{vn}: fertig {time.time()-t0:.0f} s', flush=True)
    json.dump(dict(system=name, N=N, sh=sh, s_rausch=s_rausch, par=PAR, res=res),
              open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HIER, f'df_mc_{name}.json'), 'w'), indent=1)
