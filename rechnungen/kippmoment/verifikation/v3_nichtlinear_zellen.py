"""
v3_nichtlinear_zellen.py – Gegenprüfung KM-07 (Einzelzell-Liftoff, nichtlinear) mit eigener Implementierung:
Zellkoordinaten w_j (Formfunktionen, vf_modell.Geom), eigenes RK4, Anregung bei jedem Teilschritt direkt aus
dem analytischen Egg-Profil (keine Tabelle), Zellkraft einseitig je Zelle wie Engine:
    F_j = −(K/3) w_j − (C/3) ẇ_j, falls w_j < 0 und F_j > 0, sonst 0;  Stichprobe am Schrittanfang (wie Engine).
Auswertung 10 s nach 5 s Burn-in; Liftoff = Anteil F < 1e-9.

Aufruf:  python3 v3_nichtlinear_zellen.py <teil> [dt_us]
  teil = A : 3-FG-Fälle REF (μ=1 G0 T/Z, μ=0,462 G0 T/Z, μ=1 G60h T), Standardstart und Start auf dem
             linearen Orbit (lineare periodische Lösung bei t = 0, im Frequenzbereich berechnet)
  teil = B : μ = 1, G0 entkoppelt: Einmassenschwinger je Zelle (M/3, K/3, C/3) mit Phasen 0/120/240° und
             Startverzögerung 0 oder T (Ruhe bis zur Freigabe) -> alle 8 Paritätskombinationen der Summe
  teil = C : STEIF μ = 1, G0, T (Standardstart) – chaotischer Fall der Gruppe
  teil = D : Empfindlichkeit gegen die ANNAHME Rahmenträgheit: REF μ = 0,462, G0, T, ρ_f/R_c = 0,35/0,6/0,7071
"""
import sys
import json
import numpy as np
from scipy.stats import skew
from vf_modell import Geom, a_egg, zell_koeff, MG3, K_REF, C_REF, K_STEIF, C_STEIF, GRAV, M_TOT

R = 0.10
T = 0.1


def rk4_zellen(Minv, Gw, Nexc, phis, K, C, w0, v0, dt, T_sim=15.0, T_burn=5.0, delay=None):
    """n Fälle gleichzeitig. Minv (n,3,3), Gw (n,3), Nexc (n,3 Module,3 Zellen) = m_i h_i N_j(X_i),
    phis (n,3) in Grad, w0/v0 (n,3). delay (n,3): Zelle j bleibt bis t = delay in Ruhe (nur Teil B, 1-FG)."""
    n = Minv.shape[0]
    tau = np.radians(np.asarray(phis, float)) / (2 * np.pi * 10.0)      # (n,3)
    k3, c3 = K / 3.0, C / 3.0
    gW = GRAV * Gw

    def exc(t):
        s = a_egg(t - tau)                                              # (n,3 Module)
        return np.einsum('ni,nij->nj', s, Nexc)                         # (n,3 Zellen)

    def rhs(w, v, e):
        F = -k3 * w - c3 * v
        F = np.where((w < 0.0) & (F > 0.0), F, 0.0)
        acc = np.einsum('njk,nk->nj', Minv, -gW + F - e)
        return acc, F

    n_steps = int(round(T_sim / dt)); n_burn = int(round(T_burn / dt))
    rec = np.empty((n_steps - n_burn, n, 3))
    w = np.array(w0, float); v = np.array(v0, float)
    e0 = exc(0.0)
    for i in range(n_steps):
        t = i * dt
        eh = exc(t + 0.5 * dt); e1 = exc(t + dt)
        a1, F = rhs(w, v, e0)
        a2, _ = rhs(w + 0.5 * dt * v, v + 0.5 * dt * a1, eh)
        a3, _ = rhs(w + 0.5 * dt * (v + 0.5 * dt * a1), v + 0.5 * dt * a2, eh)
        # Ortsableitungen: k1w = v, k2w = v + dt/2·a1, k3w = v + dt/2·a2, k4w = v + dt·a3
        k2w = v + 0.5 * dt * a1; k3w = v + 0.5 * dt * a2
        a4, _ = rhs(w + dt * k3w, v + dt * a3, e1)
        wn = w + dt * (v + 2 * k2w + 2 * k3w + (v + dt * a3)) / 6.0
        vn = v + dt * (a1 + 2 * a2 + 2 * a3 + a4) / 6.0
        if delay is not None:
            hold = t + dt <= delay + 1e-12
            wn = np.where(hold, w, wn); vn = np.where(hold, v, vn)
        w, v = wn, vn
        e0 = e1
        if i >= n_burn:
            rec[i - n_burn] = F
    return rec


def stat(F, label):
    N = F.sum(1)
    d = dict(fall=label, lam_zellen=[round(100 * float(np.mean(F[:, j] < 1e-9)), 4) for j in range(3)],
             lam_summe=round(100 * float(np.mean(N < 1e-9)), 4), N_min=round(float(N.min()), 4),
             N_max=round(float(N.max()), 4), N_mean=round(float(N.mean()), 5), N_skew=round(float(skew(N)), 4),
             Fz_max3=[round(3 * float(F[:, j].max()), 3) for j in range(3)],
             Fz_skew=[round(float(skew(F[:, j])), 4) for j in range(3)])
    return d


def lin_orbit_start(geo, phi, K, C):
    """Zustand der linearen periodischen Lösung bei t = 0 (Zellkoordinaten)."""
    kmax = 400
    from vf_modell import c_egg
    c = c_egg(kmax); c[0] = 0
    k = np.arange(kmax + 1); w = 2 * np.pi * 10.0 * k
    ph = np.radians(phi)
    P = (geo.Nm.T * geo.m[None, :]) @ np.exp(-1j * np.outer(ph, k)) * c[None, :]
    W = np.zeros_like(P)
    for kk in range(1, kmax + 1):
        D = -w[kk] ** 2 * geo.Mw + (1j * w[kk] * C / 3 + K / 3) * np.eye(3)
        W[:, kk] = np.linalg.solve(D, -P[:, kk])
    w_st = -3 * geo.F0 / K
    return w_st + 2 * np.real(W.sum(1)), 2 * np.real((1j * w[None, :] * W).sum(1))


if __name__ == '__main__':
    teil = sys.argv[1] if len(sys.argv) > 1 else 'A'
    dt = float(sys.argv[2]) * 1e-6 if len(sys.argv) > 2 else 50e-6
    out = []
    if teil in ('A', 'C', 'D'):
        RHO = [None] * 10
        if teil == 'D':
            K, C = K_REF, C_REF
            cases = [(0.462, 'G0', (0, 120, 240))] * 3
            RHO = [0.35 * R, 0.6 * R, R / np.sqrt(2)]
        elif teil == 'A':
            K, C = K_REF, C_REF
            cases = [(1.0, 'G0', (0, 120, 240)), (1.0, 'G0', (0, 110, 240)), (0.462, 'G0', (0, 120, 240)),
                     (0.462, 'G0', (0, 110, 240)), (1.0, 'G60h', (0, 120, 240))]
        else:
            K, C = K_STEIF, C_STEIF
            cases = [(1.0, 'G0', (0, 120, 240)), (1.0, 'G0', (0, 110, 240))]
        GK = {'G0': dict(R_m=R, psi0=0.0), 'G60h': dict(R_m=R / 2, psi0=60.0)}
        geos = [Geom(mu, R_c=R, rho_f=RHO[i], **GK[g]) for i, (mu, g, ph) in enumerate(cases)]
        Minv = np.stack([np.linalg.inv(g.Mw) for g in geos]); Gw = np.stack([g.Gw for g in geos])
        Nexc = np.stack([g.m[:, None] * g.Nm for g in geos]); phis = np.array([ph for _, _, ph in cases], float)
        starts = {'standard': (np.stack([-3 * g.F0 / K for g in geos]), np.zeros((len(geos), 3)))}
        if teil == 'A':
            ws, vs = zip(*[lin_orbit_start(g, ph, K, C) for g, (_, _, ph) in zip(geos, cases)])
            starts['lin_orbit'] = (np.stack(ws), np.stack(vs))
        for sname, (w0, v0) in starts.items():
            rec = rk4_zellen(Minv, Gw, Nexc, phis, K, C, w0, v0, dt)
            for i, (mu, g, ph) in enumerate(cases):
                d = stat(rec[:, i, :], f'{"STEIF" if teil == "C" else "REF"} mu={mu} {g} {ph} rho_f={geos[i].rho_f/R:.4f}R_c {sname} dt={dt*1e6:.0f}us')
                Fz = rec[:, i, :]
                d['periodizitaet_T'] = round(float(np.max(np.abs(Fz[-5 * 2000:] - Fz[-6 * 2000:-2000]))), 4) if abs(dt - 50e-6) < 1e-12 else None
                out.append(d); print(json.dumps(d, ensure_ascii=False))
            np.save(f'v3_teil{teil}_{sname}_dt{dt*1e6:.0f}_reihen3s.npy', rec[:int(3.0 / dt)])
    elif teil == 'B':
        # Einmassenschwinger je Zelle: Masse M/3, Feder K/3, Dämpfer C/3, ein Modul m = M/3 (μ = 1, G0)
        combos = [(ph, d) for d in (0.0, T) for ph in (0.0, 120.0, 240.0)]
        n = len(combos)
        m = M_TOT / 3
        Minv = np.tile(np.eye(3) / m, (n, 1, 1))     # 3 Spalten identisch belegt (nur Spalte 0 genutzt)
        Gw = np.full((n, 3), m)
        Nexc = np.zeros((n, 3, 3)); Nexc[:, 0, :] = m * np.eye(3)[0]    # nur Modul 0 wirkt auf Zelle 0
        Nexc[:, 0, :] = 0; Nexc[:, 0, 0] = m
        phis = np.array([[ph, 0, 0] for ph, d in combos], float)
        w0 = np.full((n, 3), -3 * MG3 / K_REF); v0 = np.zeros((n, 3))
        delay = np.array([[d, d, d] for ph, d in combos])
        rec = rk4_zellen(Minv, Gw, Nexc, phis, K_REF, C_REF, w0, v0, dt, delay=delay)
        Fc = rec[:, :, 0]                                  # Zelle 0 jedes Einzelschwingers
        for i, (ph, d) in enumerate(combos):
            x = Fc[:, i]
            print(json.dumps(dict(einzel=f'phi={ph:.0f} delay={d:.1f}', lam=round(100 * float(np.mean(x < 1e-9)), 4),
                                  Fmax3=round(3 * float(x.max()), 4), skew=round(float(skew(x)), 4),
                                  per_T=round(float(np.max(np.abs(x[-5 * 2000:] - x[-6 * 2000:-2000]))), 3),
                                  per_2T=round(float(np.max(np.abs(x[-5 * 2000:] - x[-7 * 2000:-4000]))), 3))))
        for p1 in (0, 1):
            for p2 in (0, 1):
                for p3 in (0, 1):
                    idx = [p1 * 3 + 0, p2 * 3 + 1, p3 * 3 + 2]
                    F = Fc[:, idx]
                    d = stat(F, f'Summe aus Einzelschwingern, Verzögerungen (T·) = ({p1},{p2},{p3})')
                    out.append(d); print(json.dumps(d, ensure_ascii=False))
        np.save(f'v3_teilB_dt{dt*1e6:.0f}_reihen3s.npy', Fc[:int(3.0 / dt)])
    with open(f'v3_nichtlinear_teil{teil}_dt{dt*1e6:.0f}.json', 'w') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
