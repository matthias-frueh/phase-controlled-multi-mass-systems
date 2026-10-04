"""z3_km10_identifizierbarkeit.py - Gegenpruefung KM-10 (Identifizierbarkeit Modulamplitude/-phase aus drei Zellkraeften).

Eigener Rechenweg:
 (1) Uebertragungsmatrizen T(kw) und Konditionszahlen aus dem eigenen Modell zm (Lagrange, unabhaengig).
 (2) Rueckrechnung g_hat = T_nom^{-1} F_mess fuer Einzelstoerungen (wie KM-10) plus tangentiale Zelllage.
 (3) Jacobi-Rang-Analyse: 15 Parameter (Modulskala eps_i, Modulphase delta_i, Zellverstaerkung gamma_j,
     radiale und tangentiale Zelllage r_j, t_j) gegen verschiedene Beobachtungsmengen (Triphasik-Lauf mit
     k = 1 | k = 1,2 | k = 1..5, plus drei Einzelmodullaeufe, plus statische Gewichtsstuecke an fuenf Stellen
     wie Praereg A9.2 P0.1). Rang, Singulaerwerte, Nullraum.
 (4) Rauschfortpflanzung: Standardunsicherheit von Amplitude und Phase je Modul aus weissem Zellrauschen.
"""
import numpy as np
import zm

np.set_printoptions(linewidth=160, precision=4, suppress=True)
CASES = [('STARR', None, None, 0.462), ('STEIF', zm.K_ST, zm.C_ST, 0.462),
         ('REF', zm.K_REF, zm.C_REF, 1.0), ('REF', zm.K_REF, zm.C_REF, 0.462)]
GEOS = {'G0': dict(Rm=zm.R_C, psi0=0.0), 'G60h': dict(Rm=zm.R_C / 2, psi0=60.0)}

print('=== (1) Konditionszahl von T(k w), k = 1, 2, 4, 5 ===')
for lab, K, C, mu in CASES:
    for gn, gk in GEOS.items():
        geo = zm.Geo(mu=mu, **gk)
        conds = [np.linalg.cond(geo.T(zm.OMEGA * k, K, C)) for k in (1, 2, 4, 5)]
        sv = np.linalg.svd(geo.T(zm.OMEGA * 2, K, C), compute_uv=False)
        print(f' {lab:5s} mu={mu:5.3f} {gn:4s}: cond = {np.round(conds, 3)}  (Singulaerwerte k=2: {np.round(sv, 3)})')


def measure(geo_true, K, C, phi=(0, 120, 240), hub=(1, 1, 1), dphase=(0, 0, 0), gains=(1, 1, 1), kmax=5):
    g = zm.module_phasors(geo_true, phi, kmax, hub=hub, extra_phase_deg=dphase)
    return zm.cell_phasors(geo_true, g, K, C, gains=gains)


print('\n=== (2) Rueckrechnung der Modulzeiger mit nominaler T (Triphasik-Punkt); je Modul d|g|/|g| [%] / d arg [deg] ===')
for lab, K, C, mu in CASES[:3]:
    for gn, gk in GEOS.items():
        geo0 = zm.Geo(mu=mu, **gk)
        g0 = zm.module_phasors(geo0, (0, 120, 240), 5)
        print(f'--- {lab} mu={mu} {gn}')
        tests = {
            'Masse M2 +1 %': dict(geo=zm.Geo(mu=mu, masses=geo0.m * np.array([1, 1.01, 1]), **gk)),
            'Hub M2 +1 %': dict(hub=(1, 1.01, 1)),
            'Phase M2 +1 deg': dict(dphase=(0, 1, 0)),
            'Zellverst. Z2 +1 %': dict(gains=(1, 1.01, 1)),
            'Zelle 2 radial +1 mm': dict(geo=zm.Geo(mu=mu, cell_shift=[[0, 0], [1e-3*np.cos(2*np.pi/3), 1e-3*np.sin(2*np.pi/3)], [0, 0]], **gk)),
            'Zelle 2 tangential +1 mm': dict(geo=zm.Geo(mu=mu, cell_shift=[[0, 0], [-1e-3*np.sin(2*np.pi/3), 1e-3*np.cos(2*np.pi/3)], [0, 0]], **gk)),
        }
        for name, kw in tests.items():
            gtrue = kw.pop('geo', geo0)
            if name.startswith('Masse'):
                gtrue.Mf = geo0.Mf
                gtrue.Jf = geo0.Jf
                gtrue.Mq = np.diag([gtrue.Mf, gtrue.Jf, gtrue.Jf]) + (gtrue.Bm * gtrue.m) @ gtrue.Bm.T
            F = measure(gtrue, K, C, **kw)
            line = f'  {name:26s}'
            for k in (1, 2):
                gh = np.linalg.solve(geo0.T(zm.OMEGA * k, K, C), F[:, k])
                r = gh / g0[:, k]
                line += ' | k=%d: ' % k + '  '.join(f'M{i+1} {100*(abs(r[i])-1):+.3f}/{np.degrees(np.angle(r[i])):+.3f}' for i in range(3))
            print(line)

# ---------------- (3) Jacobi-Rang-Analyse ----------------
print('\n=== (3) Rang der Jacobimatrix d(Beobachtung)/d(Parameter), 15 Parameter ===')
PN = ['eps1', 'eps2', 'eps3', 'del1', 'del2', 'del3', 'gam1', 'gam2', 'gam3', 'r1', 'r2', 'r3', 't1', 't2', 't3']


def observe(p, gk, mu, K, C, ks, single_runs, weights):
    eps, dele, gam, rr, tt = p[0:3], p[3:6], p[6:9], p[9:12], p[12:15]
    ang = np.radians([0, 120, 240])
    shift = np.stack([rr * np.cos(ang) - tt * np.sin(ang), rr * np.sin(ang) + tt * np.cos(ang)], axis=1)
    geo = zm.Geo(mu=mu, cell_shift=shift, **gk)
    obs = []
    runs = [((0, 120, 240), (1, 1, 1))]
    if single_runs:
        runs += [((0, 0, 0), tuple(1.0 if j == i else 0.0 for j in range(3))) for i in range(3)]
    for phi, on in runs:
        hub = (1 + eps) * np.array(on)
        g = zm.module_phasors(geo, phi, max(ks), hub=hub, extra_phase_deg=np.degrees(dele))
        F = zm.cell_phasors(geo, g, K, C, gains=1 + gam)
        for k in ks:
            obs += list(F[:, k].real) + list(F[:, k].imag)
    if weights:   # statisches Gewichtsstueck 1 N an bekannten Stellen: Mitte, ueber jeder Zelle (nominal), zwei Modulachsen
        pts = [(0, 0)] + [(zm.R_C*np.cos(a), zm.R_C*np.sin(a)) for a in ang] + \
              [(0.5*zm.R_C*np.cos(a+np.pi/3), 0.5*zm.R_C*np.sin(a+np.pi/3)) for a in ang[:2]]
        for (x, y) in pts:
            Fw = np.linalg.solve(geo.Bc, np.array([1.0, x, y]))
            obs += list((1 + gam) * Fw)
    return np.array(obs)


def jac(gk, mu, K, C, ks, single_runs, weights, h=1e-7):
    p0 = np.zeros(15)
    f0 = observe(p0, gk, mu, K, C, ks, single_runs, weights)
    J = np.zeros((f0.size, 15))
    for i in range(15):
        dp = np.zeros(15)
        dp[i] = h
        J[:, i] = (observe(p0 + dp, gk, mu, K, C, ks, single_runs, weights)
                   - observe(p0 - dp, gk, mu, K, C, ks, single_runs, weights)) / (2 * h)
    # Spalten auf vergleichbare Einheiten: eps, gam in 1 %, delta in 1 deg, r/t in 1 mm
    scale = np.array([1e-2]*3 + [np.radians(1)]*3 + [1e-2]*3 + [1e-3]*6)
    return J * scale


SETS = [('Triphasik, k=1', (1,), False, False), ('Triphasik, k=1,2', (1, 2), False, False),
        ('Triphasik, k=1..5', (1, 2, 3, 4, 5), False, False),
        ('Triphasik k=1,2 + 3 Einzelmodullaeufe', (1, 2), True, False),
        ('... + statische Gewichte (P0.1)', (1, 2), True, True)]
for lab, K, C, mu in (CASES[0], CASES[1]):
    for gn, gk in GEOS.items():
        print(f'--- {lab} mu={mu} {gn}')
        for sname, ks, sr, wt in SETS:
            J = jac(gk, mu, K, C, ks, sr, wt)
            s = np.linalg.svd(J, compute_uv=False)
            tol = s[0] * 1e-6
            rank = int((s > tol).sum())
            _, _, Vt = np.linalg.svd(J)
            null = Vt[rank:]
            desc = []
            # Nullraum in lesbarer Form: Basis mit groessten Komponenten
            for v in null[:6]:
                idx = np.argsort(-np.abs(v))[:4]
                desc.append(' '.join(f'{v[i]:+.2f}{PN[i]}' for i in idx if abs(v[i]) > 0.05))
            print(f'  {sname:40s}: Beob. {J.shape[0]:3d}, Rang {rank:2d}/15, kleinster Singulaerwert>tol {s[rank-1]:.2e} '
                  f'(groesster {s[0]:.2e}); Nullraum-Dim {15-rank}')
            for d_ in desc:
                print(f'      Nullrichtung: {d_}')

# ---------------- (4) Rauschfortpflanzung ----------------
print('\n=== (4) Modulzeiger aus Zellen: Standardunsicherheit bei weissem Zellrauschen ===')
for sigA in (0.024e-3, 0.156e-3):       # sigma der Harmonischen-Amplitude 2|c| je Zelle und Lauf (z4)
    for lab, K, C, mu in (CASES[0], CASES[1]):
        for gn, gk in GEOS.items():
            geo = zm.Geo(mu=mu, **gk)
            g = zm.module_phasors(geo, (0, 120, 240), 2)
            for k in (1, 2):
                Ti = np.linalg.inv(geo.T(zm.OMEGA * k, K, C))
                # 2|c| hat Std sigA -> komplexer Koeffizient c: Re/Im je sigA/2/sqrt(2)*sqrt(2)= sigA/2 ... (siehe Protokoll)
                s_c = sigA / 2.0                   # Std von Re(c) und Im(c) je Zelle
                cov_diag = (np.abs(Ti) ** 2).sum(1) * s_c ** 2   # Var(Re) = Var(Im) je Modul
                amp = 2 * np.abs(g[:, k])
                s_amp = 2 * np.sqrt(cov_diag)
                s_ph = np.degrees(np.sqrt(cov_diag) / np.abs(g[:, k]))
                print(f'  sigma_A={sigA*1e3:.3f} mN {lab:5s} {gn:4s} k={k}: Modulamplitude {amp[0]:.4f} N, '
                      f'u(Amplitude) {s_amp.max()*1e3:.4f} mN, u(Phase) {s_ph.max():.5f} deg')

# ---------------- (3b) nur Modul- und Verstaerkungsparameter (Zelllagen als exakt bekannt) ----------------
print('\n=== (3b) Rang nur fuer {eps, delta, gamma} (9 Parameter, Zelllagen bekannt) ===')
sub = list(range(9))
for lab, K, C, mu in (CASES[0], CASES[1]):
    for gn, gk in GEOS.items():
        for sname, ks, sr, wt in SETS[:4]:
            J = jac(gk, mu, K, C, ks, sr, wt)[:, sub]
            s = np.linalg.svd(J, compute_uv=False)
            rank = int((s > s[0] * 1e-6).sum())
            _, _, Vt = np.linalg.svd(J)
            nd = []
            for v in Vt[rank:][:4]:
                idx = np.argsort(-np.abs(v))[:4]
                nd.append(' '.join(f'{v[i]:+.2f}{PN[i]}' for i in idx if abs(v[i]) > 0.05))
            print(f'  {lab:5s} {gn:4s} {sname:40s}: Rang {rank}/9, kleinster SW {s[min(rank,9)-1]:.2e}; Null: {" | ".join(nd)}')

# Restfehler, wenn das Muster einer Zellverstaerkung Z2 +1 % (G60h, STARR) nur mit Modulparametern (eps, delta) erklaert wird
print('\n=== (3c) G60h STARR: Zellverstaerkung Z2 +1 % mit reinem Modulfehler-Modell (eps_i, delta_i) angepasst ===')
gk = GEOS['G60h']
for ks in ((1,), (1, 2), (1, 2, 4, 5)):
    J = jac(gk, 0.462, None, None, ks, False, False)
    target = J[:, 7]                      # Wirkung von gam2 = +1 %
    A = J[:, 0:6]                         # eps, delta
    x, *_ = np.linalg.lstsq(A, target, rcond=None)
    res = target - A @ x
    print(f'  k={ks}: angepasst eps={np.round(x[:3],3)} %, delta={np.round(x[3:6],3)} deg; '
          f'Rest/Signal = {np.linalg.norm(res)/np.linalg.norm(target):.3f}; max Rest {np.abs(res).max()*1e3:.2f} mN '
          f'(Zellzeiger-Komponente; Signal max {np.abs(target).max()*1e3:.2f} mN)')
