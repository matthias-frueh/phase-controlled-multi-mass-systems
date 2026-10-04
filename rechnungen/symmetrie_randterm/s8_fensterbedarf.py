"""s8_fensterbedarf.py - Teil B, Aufgabe 6 (Experiment): Welche Fensterlaenge/-lage haelt den
Randterm delta_w = dv_S/(g T_w) unter eps = 1e-4 (Messaufloesung 1e-4*Mg)?
Grundlage: Referenzmodell (Engine, s6_p1.npz: eine Periode N(t), v_S(t) am Attraktor, v_S an den
Zyklusbeginnen 30-40 s) fuer HS (0,208.421), S0 (0,0), L1 (157.3,264), K1 (110,234).
Faelle:
 (a) Fenster beliebig gelegt (nicht phasenstarr), stationaer: |dv_S| <= 2 v_S,max  -> T_w >= 2 v_S,max/(eps g);
     typischer Wert mit unabhaengigen Randphasen: rms(dv_S) = sqrt(2) v_S,rms.
 (b) phasenstarr ueber ganze Perioden: Rest aus (i) Zyklus-zu-Zyklus-Streuung sigma_v von v_S bei fester
     Antriebsphase und (ii) Zeitfehler dt_b der Fenstergrenzen: dv_S = a_S(t_b) dt_b, a_S = (N - Mg)/M.
 (c) Fenster im Einschwingen: dv_S bis 0,66 m/s (Hot-Spot, Standardstart).
 (d) Synthetisch: Abtastmittel eines Signals mit Sprung bei kommensurabler und inkommensurabler Abtastrate."""
import numpy as np
import sr_engine as se

EPS = 1e-4
g = se.G
r = np.load('s6_p1.npz')
vS = r['vS_last']; F = r['F_last']; vc = r['vcom']
names = ['HS (0,208.421)', 'S0 (0,0)', 'L1 (157.3,264)', 'K1 (110,234)']
print(f'eps = {EPS:g}, g = {g} m/s^2, M = {se.M} kg, Mg = {se.MG:.4f} N; Aufloesung eps*Mg = {EPS * se.MG * 1e3:.3f} mN')
print('Punkt              v_S,max   v_S,rms  | (a) T_w,worst  T_w,rms(1s)  T_w,rms(3s) | sigma_v(Zyklus)  (b-i) T_w   '
      '| max|a_S|  (b-ii) T_w bei dt_b=100us / 1ms')
for j, nm in enumerate(names):
    vmax = np.max(np.abs(vS[:, j])); vrms = np.sqrt(np.mean((vS[:, j] - vS[:, j].mean()) ** 2))
    Ta = 2 * vmax / (EPS * g); Tr1 = np.sqrt(2) * vrms / (EPS * g)
    sig = np.std(vc[300:400, j])
    Tb1 = np.sqrt(2) * sig / (EPS * g)
    amax = np.max(np.abs(F[:, j] - se.MG)) / se.M
    Tb2 = amax * 1e-4 / (EPS * g); Tb3 = amax * 1e-3 / (EPS * g)
    print(f'{nm:18s} {vmax:7.4f}  {vrms:7.4f}  |   {Ta:8.1f} s   {Tr1:8.1f} s   {3 * Tr1:8.1f} s | {sig:9.2e} m/s   {Tb1:8.2e} s '
          f'| {amax:6.1f}    {Tb2:6.2f} s / {Tb3:6.1f} s')
print('Hinweis (b-ii): Grenze im Flug (N = 0) -> a_S = -g exakt -> T_w >= dt_b/eps (dt_b = 100 us -> 1 s).')
print(f'(c) Einschwingen am Hot-Spot (Standardstart, Fenster ab 5 s): dv_S = -0.661 m/s -> T_w >= {0.661 / (EPS * g):.0f} s;'
      f' Abklingzeit im Kontaktast 2M/C = {2 * se.M / se.C_REF:.3f} s')

# (d) synthetisches Signal: periodischer Sprung J bei t = 0 mod T, danach exponentielles Abklingen
J, tau, T = 8.0, 0.02, 0.1
exact = J * tau * (1 - np.exp(-T / tau)) / T
print('\n(d) synthetisch: f(t) = J exp(-(t mod T)/tau), J = 8 N, tau = 20 ms, T = 0,1 s; exaktes Mittel '
      f'{exact:.6f} N')
for fs in (10000.0, 10000.0 * np.pi / 3.1, 9973.0):
    for theta in (0.05, 0.5, 0.95):
        dt = 1 / fs
        n = int(round(100 * T / dt))
        t = (np.arange(n) + theta) * dt
        m = np.mean(J * np.exp(-np.mod(t, T) / tau))
        print(f'   f_s = {fs:9.2f} Hz, Startphase {theta:.2f}: Mittel - exakt = {(m - exact) * 1e3:+.4f} mN '
              f'({(m - exact) / se.MG * 1e6:+.1f} ppm von Mg); Schranke J/(2 f_s T) = {J / (2 * fs * T) * 1e3:.3f} mN')
