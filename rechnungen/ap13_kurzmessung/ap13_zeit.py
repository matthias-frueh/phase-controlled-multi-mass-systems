"""AP-13 Laufzeitmessung (nur Planungszahl, keine Registrierungszahl).

Misst mit den vorhandenen Werkzeugen (code/auslegung.py, code/ereignisloeser.py) die Bausteine einer
synthetischen Kampagne:
 (a) Aufbau des V1-Kandidaten (3-FG, G0) und stationäre Lösung für Schnitt, Piloten, Einzelmodulläufe;
 (b) Kampagne auf Ebene der Harmonischen (wie P2 s2 / AP-08-Kontrolle), V1-Kandidat statt A4-Beispiel,
     Bootstrap B = 200 und B = 1000 (Skalierung auf 10 000 linear);
 (c) ein Lauf auf Zeitreihenebene (f_s = 6,4 kHz, 100 Zyklen, Summe + 3 Zellen, Jitter je Zyklus,
     weißes Rauschen) mit der Verarbeitungskette A9.4 (Segmentierung, Resampling auf 2000, Mittel, DFT);
 (d) ereignisgenauer Löser: Kontaktast (Kelvin-Voigt), Wurf in den Hüpfzustand (160 Perioden),
     Hunt-Crossley-Kontaktast per Newton (solve_ivp) an einem Schnittpunkt.
Aufruf: python3 ap13_zeit.py
"""
import time
import numpy as np
from scipy.stats import t as tdist
import auslegung as A
import ereignisloeser as EL

rng = np.random.default_rng(13)
out = []


def zeit(name, fn, rep=1):
    t0 = time.perf_counter()
    for _ in range(rep):
        r = fn()
    dt = (time.perf_counter() - t0) / rep
    out.append((name, dt))
    print(f'{name:70s} {dt * 1e3:10.1f} ms', flush=True)
    return r


# (a) Auslegungswerkzeug
a = zeit('(a1) Aufbau() V1-Kandidat G0 (3-FG, K = 1,5e6, zeta = 0,05)', lambda: A.Aufbau(), rep=5)
KMAX = a.kmax_standard()
print('k_max (Vorgabe max(k_b, 3)) =', KMAX)
SCH = A.SCHNITT
phi = np.r_[np.c_[np.zeros(21), SCH, np.full(21, 240.0)], np.array([[0, p2, p3] for p2, p3 in A.PILOTEN])]
zeit('(a2) loesen(): 21 Schnittpunkte + 3 Piloten, k <= k_max', lambda: a.loesen(phi, kmax=KMAX), rep=5)
w = np.eye(3)
r1 = zeit('(a3) loesen(): 3 Einzelmodulläufe', lambda: a.loesen(np.zeros((3, 3)), w=w, kmax=KMAX, kout=KMAX), rep=5)
Nk_mod = np.array([r1['Nk'][j] for j in range(3)])          # (3, K), Summe, eigener Takt (phi = 0)
zeit('(a4) Aufbau G60h + loesen (Schnitt, Piloten, Einzel)',
     lambda: A.Aufbau(geometrie_name='G60h').loesen(np.r_[phi, np.zeros((3, 3))],
                                                     w=np.r_[np.ones((24, 3)), w], kmax=KMAX), rep=3)

# (b) Kampagne auf Ebene der Harmonischen (Rauschmodell wie P2-Stufe L2: 1 %/0,1° je Modul, sigma_h 0,11 mN)
SIG_H, SIG_AMP, SIG_PH = 0.11e-3, 0.01, 0.10
N, N0, N1, NTH = 20, 20, 21, 2000
k = np.arange(1, KMAX + 1)
PHI = np.radians(phi[:21])
E = np.exp(-1j * PHI[:, :, None] * k[None, None, :])
th = 2 * np.pi * np.arange(NTH) / NTH
COS, SIN = np.cos(np.outer(k, th)), np.sin(np.outer(k, th))
masks = []
for i in range(21):
    Ni = (Nk_mod * E[i]).sum(0) / 2
    cv = Ni.real @ COS - Ni.imag @ SIN
    masks.append(cv < cv.min() + 0.3)


def qvec(Nc, m):
    o = [((Nc.real @ COS[:, m] - Nc.imag @ SIN[:, m]) / 1).min(-1)]
    for kk in range(3):
        o += [Nc[..., kk].real, Nc[..., kk].imag]
    return np.stack(o, -1)


def runs_single(n):
    eps = rng.normal(0, SIG_AMP, (3, n, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (3, n, 1)))
    wn = SIG_H * (rng.standard_normal((3, n, KMAX)) + 1j * rng.standard_normal((3, n, KMAX)))
    return Nk_mod[:, None, :] / 2 * (1 + eps) * np.exp(-1j * k * dl) + wn


def runs_comb(n):
    eps = rng.normal(0, SIG_AMP, (21, n, 3, 1))
    dl = np.radians(rng.normal(0, SIG_PH, (21, n, 3, 1)))
    mods = Nk_mod / 2 * (1 + eps) * np.exp(-1j * k * dl) * E[:, None, :, :]
    wn = SIG_H * (rng.standard_normal((21, n, KMAX)) + 1j * rng.standard_normal((21, n, KMAX)))
    return mods.sum(2) + wn


def boot(X, nb):
    n = X.shape[1]
    W = rng.multinomial(n, np.full(n, 1.0 / n), size=(X.shape[0], nb)) / n
    return np.einsum('gbn,gnk->gbk', W, X)


def kampagne(B):
    S0, S1, Y = runs_single(N0), runs_single(N1), runs_comb(N)
    yh0 = np.einsum('jk,ijk->ik', S0.mean(1), E)
    yh1 = np.einsum('jk,ijk->ik', S1.mean(1), E)
    Yb, S0b, S1b = boot(Y, B), boot(S0, B), boot(S1, B)
    yh0b = np.einsum('jbk,ijk->ibk', S0b, E)
    yh1b = np.einsum('jbk,ijk->ibk', S1b, E)
    Ybar = Y.mean(1)
    z = np.empty((2, 21, 7))
    for i in range(21):
        m = masks[i]
        qm = qvec(Ybar[i], m)
        vA = qvec(Yb[i], m).var(0, ddof=1)
        for s, (yh, yhb) in enumerate(((yh0, yh0b), (yh1, yh1b))):
            vB = qvec(yhb[i], m).var(0, ddof=1)
            z[s, i] = (qm - qvec(yh[i], m)) / np.sqrt(vA + vB)
    return np.abs(z).max()


for B in (200, 1000):
    zeit(f'(b) Kampagne Harmonische, 21 Punkte x 7 Größen, n = n0 = 20, n1 = 21, B = {B}',
         lambda: kampagne(B), rep=20 if B == 200 else 5)

# (c) ein Lauf auf Zeitreihenebene: Summe + 3 Zellen, f_s = 6,4 kHz, 100 Zyklen, Jitter 56 µs je Zyklus
F, FS, NZ = 10.0, 6400, 100
NS = int(FS / F)                     # 640 Abtastwerte je Zyklus
Fzk = np.array([r1['Fzk'][j] for j in range(3)]) / 2     # (Modul, Zelle, K)
kz = np.arange(1, KMAX + 1)


def lauf_zeitreihe(phis=(0.0, 120.0, 240.0), sig=20e-3, jit=0.2):
    off = rng.uniform(0, 1)                                            # Sub-Sample-Versatz der Abtastung
    t = (np.arange(NZ * NS) + off) / FS
    cyc = np.minimum((t * F).astype(int), NZ - 1)
    dphi = np.c_[np.zeros(NZ), rng.normal(0, jit, (NZ, 2))]            # Modul 1 definiert theta
    ph = np.radians(np.asarray(phis)[None, :] + dphi)                  # (NZ, 3)
    ew = np.exp(1j * 2 * np.pi * F * np.outer(t, kz))                  # (NS*NZ, K)
    cells = np.zeros((3, t.size))
    for j in range(3):
        ej = np.exp(-1j * np.outer(ph[:, j], kz))[cyc]                 # (NS*NZ, K)
        cells += 2 * np.real((ew * ej) @ Fzk[j].T).T
    cells += sig / np.sqrt(3) * rng.standard_normal(cells.shape)
    # Verarbeitung A9.4: Index von Modul 1 bei t = c/F + Sub-Sample-Versatz; Resampling auf 2000 Stützstellen
    tg = (np.arange(NZ)[:, None] + np.arange(NTH)[None, :] / NTH) / F
    sig4 = np.r_[cells, cells.sum(0, keepdims=True)]
    mk = np.empty((4, KMAX), complex)
    for ch in range(4):
        y = np.interp(tg[1:].ravel(), t, sig4[ch]).reshape(NZ - 1, NTH)    # nur vollständige Zyklen
        mc = y.mean(0)
        mk[ch] = 2 * np.fft.rfft(mc)[1:KMAX + 1] / NTH
    return mk


zeit('(c) ein Lauf Zeitreihe (Summe + 3 Zellen, 6,4 kHz, 100 Zyklen) inkl. Kette A9.4', lauf_zeitreihe, rep=10)

# (d) ereignisgenauer Löser
sy = EL.kandidat(0.0, 0.0, zeta=0.05)
zs = zeit('(d1) Kontaktast Kelvin-Voigt geschlossen (Kandidat synchron)', lambda: EL.kontaktorbit(sy)[0], rep=5)
zeit('(d2) Wurf 0,4 m/s aus dem Kontaktast, 160 Perioden (Kelvin-Voigt)',
     lambda: EL.wurf(sy, 0.4, 0.0, z=zs), rep=2)
syc = EL.kandidat(120.0, 240.0, zeta=0.05)
zeit('(d3) 150 Perioden Kontaktast Kelvin-Voigt (Triphasik)',
     lambda: EL.simulate(syc, *EL.kontaktorbit(syc)[0], 0.0, 150), rep=2)
hc = EL.hc_aequivalent(syc, 0.05)
zh = zeit('(d4) Hunt-Crossley-Kontaktast per Newton (Triphasik, solve_ivp)',
          lambda: EL.startzustand(hc, 'orbit'), rep=1)
zeit('(d5) Hunt-Crossley 10 Perioden im Dauerkontakt (solve_ivp)',
     lambda: EL.simulate(hc, zh[0], zh[1], 0.0, 10), rep=1)

print()
for n_, d in out:
    print(f'{n_};{d:.4f}')
