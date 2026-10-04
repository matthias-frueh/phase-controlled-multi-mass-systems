"""
v5_fensterbedarf.py - Gegenpruefung RT-05 (Fensterbedarf fuer |delta_w| < eps = 1e-4).
Eigene RK4-Engine, Formulierung 'com' (Schwerpunkt direkt integriert), Standardstart, 400 Perioden;
letzte Periode (39,9-40 s) gespeichert. v_S(t) innerhalb der Periode exakt aus der diskreten Impulsbilanz:
  v_S(t_i) = v_S(t_0) + dt * sum_{j<i} (-g + F_RK4,j / M).
Zusaetzlich: Kontrolle der Fensterformel durch direkte Fensterung (beliebige Lage) eines 10-s-Abschnitts.
Groessen: v_S,max, v_S,rms, max|a_S| = max|N - Mg|/M, sigma_v (v_S an Periodenbeginnen 30-40 s).
Formeln wie Gruppe (a) T = 2 v_max/(eps g); rms: sqrt(2) v_rms/(eps g); (b-i) sqrt(2) sigma_v/(eps g);
(b-ii) max|a_S| dt_b/(eps g).
"""
import sys, time, numpy as np
import v_engine as ve

EPS, g, M, MG = 1e-4, ve.G, ve.M, ve.MG
PTS = [('HS', 0.0, 208.421), ('S0', 0.0, 0.0), ('L1', 157.3, 264.0), ('K1', 110.0, 234.0)]
if len(sys.argv) > 1 and sys.argv[1] == 'lauf':
    t1 = time.time()
    o = ve.run([p[1] for p in PTS], [p[2] for p in PTS], 400, form='com', store=(300, 400))
    print(f'Lauf {time.time() - t1:.0f} s')
    np.savez('v5_fensterbedarf.npz', ser=o['ser'], serw=o['serw'], vS=o['vS'], vSend=o['vSend'], L=o['L'])
    sys.exit()
r = np.load('v5_fensterbedarf.npz')
L = int(r['L']); dt = ve.T / L
F1 = r['ser']; FW = r['serw']; vS0 = r['vS'][300]
# v_S-Reihe 30-40 s
acc = -g + FW / M
vS = vS0[None, :] + dt * np.vstack([np.zeros((1, len(PTS))), np.cumsum(acc, 0)[:-1]])
print(f'Kontrolle v_S-Rekonstruktion: |v_S(40 s) rekonstruiert - Engine| = '
      f'{np.max(np.abs(vS0 + dt * acc.sum(0) - r["vSend"])):.1e} m/s')
print(f'eps = {EPS:g}, eps*Mg = {EPS * MG * 1e3:.3f} mN')
print('Punkt  v_S,max  v_S,rms  (a)T_worst  (a)T_rms  sigma_v      (b-i)T     max|a_S|  (b-ii)T(100us)  mittl.|a_S|')
for j, (nm, p2, p3) in enumerate(PTS):
    last = slice((399 - 300) * L, (400 - 300) * L)
    v1 = vS[last, j]
    vmax = np.max(np.abs(v1)); vrms = np.std(v1)
    sig = np.std(r['vS'][300:400, j])
    amax = np.max(np.abs(F1[last, j] - MG)) / M
    amean = np.mean(np.abs(F1[last, j] - MG)) / M
    print(f'{nm:4s} {vmax:8.4f} {vrms:8.4f} {2 * vmax / (EPS * g):9.1f} s {np.sqrt(2) * vrms / (EPS * g):8.1f} s '
          f'{sig:9.2e} {np.sqrt(2) * sig / (EPS * g):9.2e} s {amax:8.2f} {amax * 1e-4 / (EPS * g):9.3f} s '
          f'{amean:8.2f}')
# direkte Pruefung: Fenstermittel ueber zufaellig gelegte Fenster der Laenge T_w (nicht phasenstarr) auf 30-40 s
rng = np.random.default_rng(1)
print('\nDirekte Fensterung (Mittel der RK4-gewichteten Kraft) mit Zufallsstart; (i) Laenge = ganze Perioden,')
print('(ii) Laenge = T_w + U*T, U gleichverteilt (nicht phasenstarr); 2000 Fenster je T_w; |delta| in ppm:')
for j, (nm, p2, p3) in enumerate(PTS):
    cs = np.concatenate([[0.0], np.cumsum(FW[:, j])])
    out = []
    for Twin, frei in ((1.0, False), (5.0, False), (1.0, True), (2.0, True), (5.0, True)):
        if frei:
            n = (np.round((Twin + rng.random(2000) * ve.T) / dt)).astype(int)
        else:
            n = np.full(2000, int(round(Twin / dt)))
        st = rng.integers(0, F1.shape[0] - n.max(), 2000)
        mean = (cs[st + n] - cs[st]) / n
        d = (mean - MG) / MG * 1e6
        out.append(f'{"frei" if frei else "ganz"} T_w={Twin:g}s: max {np.max(np.abs(d)):.0f}, rms {np.sqrt(np.mean(d ** 2)):.0f}, '
                   f'Schranke 2v_max/(gT) {2 * np.max(np.abs(vS[:, j])) / (g * Twin) * 1e6:.0f}')
    print(f'  {nm}: ' + ' | '.join(out))

# ---- Periodenstruktur der Zyklusbeginn-Geschwindigkeit (eigener 155-s-Lauf, v3_randterm_frame.npz) -------------
print('\nPeriodenstruktur v_S(Periodenbeginn), eigener 155-s-Lauf (frame), Zyklen 300-1550:')
r3 = np.load('v3_randterm_frame.npz')
for j, nm in [(0, 'HS'), (2, 'S0')]:
    v = r3['vS'][300:1550, j]
    print(f'  {nm}: sigma_v (alle Zyklen) = {np.std(v):.2e} m/s')
    for p in (1, 2, 3):
        subs = [v[k::p] for k in range(p)]
        print(f'     Periode {p}: Teilfolgen-Mittel {np.round([s.mean() for s in subs], 5)}, Teilfolgen-std '
              + ' '.join('%.2e' % s.std() for s in subs) + ' m/s')
    for n in (100, 101, 200, 500):
        dv = v[n:] - v[:-n]
        rms = np.sqrt(np.mean(dv ** 2)); mx = np.max(np.abs(dv))
        print(f'     phasenstarres Fenster n = {n} Perioden: rms|dv_S| = {rms:.2e}, max = {mx:.2e} m/s -> '
              f'|delta_w| rms {rms / (g * n * ve.T) * 1e6:.2f} ppm, max {mx / (g * n * ve.T) * 1e6:.2f} ppm; '
              f'noetiges T_w fuer eps (max) = {mx / (EPS * g):.2f} s')
