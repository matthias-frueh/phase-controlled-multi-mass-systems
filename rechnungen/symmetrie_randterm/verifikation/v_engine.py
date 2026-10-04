"""
v_engine.py - unabhaengig geschriebene Pruef-Engine des Gegenpruefers (P2, symmetrie_randterm/verifikation).

Bewusst NICHT aus sr_engine.py / finesweep.py uebernommen. Unterschiede zur Referenz-Arithmetik:
  * Profil analytisch als q, dq/dt, d2q/dt2 (Phasenbruch s = t/T - floor(t/T)), Phasen in Grad:
    tau_k = (phi_k/360) * T  (statt radians()/(2 pi f)).
  * Zwei Formulierungen waehlbar:
      form='frame': Zustand (z_f, v_f) wie die Referenz:  v_f' = -g + F_c(z_f,v_f)/M - abar(t)
      form='com'  : Zustand (z_S, v_S) des Schwerpunkts:   v_S' = -g + F_c(z_S - qbar, v_S - qbardot)/M
                    (z_f = z_S - qbar).  Hier schliesst das RK4-gewichtete Kraftmittel die Impulsbilanz
                    algebraisch exakt (kein Simpson-Defekt der vorgegebenen Beschleunigung).
  * Profiltabellen je Periode vorab berechnet (t = t0 + j*dt + {0, dt/2, dt}, j = 0..L-1), d.h. die
    Zeit wird periodisch reduziert -> andere Rundung als t = i*dt der Referenz.
Kontaktgesetz wie Modell: F = -K z_f - C v_f, nur wenn z_f < 0 und F > 0, sonst 0.
Je Periode werden ausgewertet: Linksrechteck (Stufe-1-Kraft), RK4-gewichtet, F^2, F^3, min, max,
Liftoff-Zaehler (F < 1e-9), DFT k=1..KMAX (absoluter Zeitbezug, e^{-i k w t}), v_S am Periodenbeginn.
SI-Einheiten.
"""
import numpy as np

M, G = 0.650, 9.81
MG = M * G
FHZ = 10.0
T = 1.0 / FHZ
RTOP = 0.005
TH = 0.65
TF = 1.0 - TH
RBOT = RTOP * TF / TH
K0, C0 = 1.0e4, 16.0
WH = np.pi / (TH * T)
WF = np.pi / (TF * T)
KMAX = 6


def prof(t):
    """Ein Modul, unverschoben: (q, qd, qdd) zur Zeit t (Array)."""
    t = np.asarray(t, float)
    s = t / T - np.floor(t / T)
    hold = s < TH
    xh = WH * s * T
    xf = WF * (s - TH) * T
    q = np.where(hold, RTOP * np.sin(xh), -RBOT * np.sin(xf))
    qd = np.where(hold, RTOP * WH * np.cos(xh), -RBOT * WF * np.cos(xf))
    qdd = np.where(hold, -RTOP * WH ** 2 * np.sin(xh), RBOT * WF ** 2 * np.sin(xf))
    return q, qd, qdd


def pbar(t, tau2, tau3):
    """Mittel der drei Module (Phasen 0, tau2, tau3): (qbar, qbar', qbar'')."""
    a = prof(t)
    b = prof(t - tau2)
    c = prof(t - tau3)
    return tuple((a[i] + b[i] + c[i]) / 3.0 for i in range(3))


def run(phi2, phi3, n_cyc, dt=5e-5, t0=0.0, z0=None, v0=None, form='frame', K=K0, C=C0,
        keep_last=False, store=None):
    """phi2, phi3 in Grad (Arrays). t0 Startzeit (Skalar/Array). z0, v0: Anfangszustand der jeweiligen
    Formulierung (frame: z_f, v_f; com: z_S, v_S); Standard = statisches Gleichgewicht des Rahmens in Ruhe
    (frame: z_f=-Mg/K, v_f=0; com: daraus umgerechnet). Rueckgabe: dict mit (Zyklus, Punkt)-Arrays."""
    phi2 = np.atleast_1d(np.asarray(phi2, float))
    phi3 = np.atleast_1d(np.asarray(phi3, float))
    n = phi2.size
    tau2 = phi2 / 360.0 * T
    tau3 = phi3 / 360.0 * T
    t0 = np.broadcast_to(np.asarray(t0, float), (n,)).copy()
    L = int(round(T / dt))
    assert abs(L * dt - T) < 1e-13
    j = np.arange(L)
    ta = t0[None, :] + j[:, None] * dt
    q1, qd1, a1 = pbar(ta, tau2, tau3)
    q2, qd2, a2 = pbar(ta + 0.5 * dt, tau2, tau3)
    q4, qd4, a4 = pbar(ta + dt, tau2, tau3)
    qs0, qds0, _ = pbar(t0, tau2, tau3)            # Profil am Periodenbeginn (periodisch)
    if z0 is None:
        zf0, vf0 = np.full(n, -MG / K), np.zeros(n)
        if form == 'frame':
            x, v = zf0, vf0
        else:
            x, v = zf0 + qs0, vf0 + qds0
    else:
        x = np.broadcast_to(np.asarray(z0, float), (n,)).copy()
        v = np.broadcast_to(np.asarray(v0, float), (n,)).copy()
    kk = np.arange(1, KMAX + 1)
    w = 2 * np.pi * FHZ
    Ebas = np.exp(-1j * w * (j[:, None] * dt) * kk[None, :])        # (L, KMAX)
    Eoff = np.exp(-1j * w * t0[:, None] * kk[None, :])               # (n, KMAX)
    keys = ('S1', 'SW', 'S2', 'S3', 'Fmin', 'Fmax', 'LO', 'vS', 'x', 'v')
    out = {k_: np.empty((n_cyc, n)) for k_ in keys}
    out['DFT'] = np.empty((n_cyc, n, KMAX), complex)
    F1b = np.empty((L, n))
    FWb = np.empty((L, n))
    if store is not None:
        ca, cb = store
        ser = np.empty(((cb - ca) * L, n))
        serw = np.empty(((cb - ca) * L, n))
        vS_ca = None
    h, hh = dt, 0.5 * dt
    frame = (form == 'frame')
    for c in range(n_cyc):
        out['x'][c] = x
        out['v'][c] = v
        out['vS'][c] = (v + qds0) if frame else v
        for i in range(L):
            if frame:
                zf, vf = x, v
            else:
                zf, vf = x - q1[i], v - qd1[i]
            F = -K * zf - C * vf
            f1 = np.where((zf < 0.0) & (F > 0.0), F, 0.0)
            k1x = v
            k1v = (-G + f1 / M - a1[i]) if frame else (-G + f1 / M)
            xb = x + hh * k1x; vb = v + hh * k1v
            if frame:
                zf, vf = xb, vb
            else:
                zf, vf = xb - q2[i], vb - qd2[i]
            F = -K * zf - C * vf
            f2 = np.where((zf < 0.0) & (F > 0.0), F, 0.0)
            k2x = vb
            k2v = (-G + f2 / M - a2[i]) if frame else (-G + f2 / M)
            xb = x + hh * k2x; vb = v + hh * k2v
            if frame:
                zf, vf = xb, vb
            else:
                zf, vf = xb - q2[i], vb - qd2[i]
            F = -K * zf - C * vf
            f3 = np.where((zf < 0.0) & (F > 0.0), F, 0.0)
            k3x = vb
            k3v = (-G + f3 / M - a2[i]) if frame else (-G + f3 / M)
            xb = x + h * k3x; vb = v + h * k3v
            if frame:
                zf, vf = xb, vb
            else:
                zf, vf = xb - q4[i], vb - qd4[i]
            F = -K * zf - C * vf
            f4 = np.where((zf < 0.0) & (F > 0.0), F, 0.0)
            k4x = vb
            k4v = (-G + f4 / M - a4[i]) if frame else (-G + f4 / M)
            x = x + h * (k1x + 2 * k2x + 2 * k3x + k4x) / 6.0
            v = v + h * (k1v + 2 * k2v + 2 * k3v + k4v) / 6.0
            F1b[i] = f1
            FWb[i] = (f1 + 2 * f2 + 2 * f3 + f4) / 6.0
        out['S1'][c] = F1b.sum(0)
        out['SW'][c] = FWb.sum(0)
        out['S2'][c] = (F1b ** 2).sum(0)
        out['S3'][c] = (F1b ** 3).sum(0)
        out['Fmin'][c] = F1b.min(0)
        out['Fmax'][c] = F1b.max(0)
        out['LO'][c] = (F1b < 1e-9).sum(0)
        out['DFT'][c] = (F1b.T @ Ebas) * Eoff
        if store is not None and ca <= c < cb:
            ser[(c - ca) * L:(c - ca + 1) * L] = F1b
            serw[(c - ca) * L:(c - ca + 1) * L] = FWb
    out['L'] = L
    out['dt'] = dt
    out['xend'] = x
    out['vend'] = v
    out['vSend'] = (v + qds0) if frame else v
    if store is not None:
        out['ser'] = ser      # Stufe-1-Kraft (Linksrechteck-Abtastwerte)
        out['serw'] = serw    # RK4-gewichtete Kraft je Schritt
        out['vS_ca'] = out['vS'][ca]
    return out


def window(out, c_a, c_b):
    """Fensterauswertung ueber Zyklen c_a..c_b-1 (ganze Perioden). Liefert dict je Punkt."""
    L = out['L']
    N = (c_b - c_a) * L
    s1 = out['S1'][c_a:c_b].sum(0); sw = out['SW'][c_a:c_b].sum(0)
    s2 = out['S2'][c_a:c_b].sum(0); s3 = out['S3'][c_a:c_b].sum(0)
    m1 = s1 / N; mw = sw / N
    var = s2 / N - m1 ** 2
    m3 = s3 / N - 3 * m1 * s2 / N + 2 * m1 ** 3
    gam = m3 / var ** 1.5
    lo = out['LO'][c_a:c_b].sum(0) / N * 100.0
    fmin = out['Fmin'][c_a:c_b].min(0); fmax = out['Fmax'][c_a:c_b].max(0)
    dft = out['DFT'][c_a:c_b].sum(0) * 2.0 / N if 'DFT' in out else None
    vS_a = out['vS'][c_a]
    vS_b = out['vS'][c_b] if c_b < out['vS'].shape[0] else out['vSend']
    Tw = (c_b - c_a) * T
    R = M * (vS_b - vS_a) / Tw
    return dict(N1=m1, NW=mw, gam=gam, lam=lo, Fmin=fmin, Fmax=fmax, Nk=dft, dvS=vS_b - vS_a, R=R,
                Q=m1 - mw, E=mw - MG - R, Tw=Tw)
