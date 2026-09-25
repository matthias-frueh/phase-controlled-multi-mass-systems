"""
linear_solver.py – exakte stationäre Lösung der Referenz-Engine im liftoff-freien Bereich.

Solange der Körper nicht abhebt, ist das Modell der Engine linear:

    M·ẍ + C·ẋ + K·x = −μ·M·ā(t),     N(t) = M·g − K·x − C·ẋ

mit ā(t) = [a(t) + a(t−τ₂) + a(t−τ₃)]/3 der mittleren Beschleunigung der drei Module, τₖ = φₖ/(2π·f)
und μ dem Anteil der Masse, der sich mit den Modulen bewegt (Engine: μ = 1, masseloser Rahmen).
Im eingeschwungenen Zustand gilt für jede Harmonische k der Anregungsfrequenz f

    N_k = μ·M · H(kω) · P_k · (1 + e^{−ikφ₂} + e^{−ikφ₃}) / 3,     H(ω) = (K + iωC) / (K − Mω² + iωC)

mit P_k den Fourier-Koeffizienten des Bewegungsprofils. Die Phasenlage wirkt nur über den Faktor
(1 + e^{−ikφ₂} + e^{−ikφ₃})/3; bei (120°, 240°) verschwindet er für alle k, die kein Vielfaches von 3
sind (wie beim Massenausgleich des Dreizylindermotors). Die Kontaktsteifigkeit wirkt nur über H.

Bleiben N(t) > 0 und die Auflagerkoordinate z(t) < 0, existiert ein Kontaktast (valid = True): eine
periodische Lösung ohne Abheben. Streng folgt nur die Umkehrung: Erreicht die lineare Lösung N ≤ 0
(F_min_lin ≤ 0), hebt der Körper ab, und nur die RK4-Engine liefert die Wellenform; dort gibt das Skript
nur F_min_lin aus. Existiert ein Kontaktast, kann die Engine je nach Anfangszustand trotzdem auf einem
abhebenden Zustand landen: Bei der Referenz sind die sechs kleinen Satelliteninseln des Kontaktasts
bistabil, die beiden Hauptgebiete um (120°, 240°) und (240°, 120°) in allen Proben nicht (412 Rasterpunkte
der Datensätze vom Standardstart; 280 Punkte × 7 Starts im 3°-Raster um (120°, 240°) mit --contact --grid;
zwei Würfe mit ż₀ = 3 m/s mit --contact).
Kein Rasterpunkt der drei Datensätze liegt in einer Insel; dort stimmen lineare Klassifikation und Engine
überein (--validate). Die Spalte liftoff = 0 bedeutet deshalb „auf dem Kontaktast“.

Aufruf:
  python3 linear_solver.py --validate                 Abgleich mit allen drei Datensätzen in data/ (Exit-Code 1 bei Abweichung)
  python3 linear_solver.py --harmonics                Anteil der zweiten Harmonischen an Zeltsteigung und Karte
  python3 linear_solver.py --contact [--long] [--grid] Kontaktast: Anteile, Gebiete, Bistabilität der Inseln,
                                                      Monostabilität des Hauptgebiets (RK4)
  python3 linear_solver.py --section                  21-Punkt-Schnitt φ₂ = 100° … 140° bei φ₃ = 240° mit |N_k|
  python3 linear_solver.py --point 120 240            Observablen an einem Punkt
  python3 linear_solver.py --ktable                   F_min(120°, 240°) über K (ζ fest und C fest), Band um
                                                      3f = f_n, RK4-Gegenprobe bei 23 000 N/m (ca. 30 s)
  python3 linear_solver.py --map karte.csv --step 2   Karte über [0°, 360°)², Anteil liftoff-freier Punkte
Optionen für --section, --point und --map: --K, --C oder --zeta, --mu, --rigid (starre Auflage), --sinus
(Sinusprofil), --f (Anregungsfrequenz bei gleichem Hub).

Rechenzeit: ca. 1 ms je Punkt (Engine: ca. 2 s). Stichproben wie in der Engine (Δt = 50 µs, 2000 je
Periode), damit F_min, F_max und Schiefe direkt mit den CSV-Werten vergleichbar sind. Das Spektrum wird
auf einem achtfach feineren Raster gebildet; feinere Raster ändern die Observablen um weniger als 1e-6.
Abgleich mit der RK4-Engine (--validate): alle 851 Punkte der drei Datensätze richtig als liftoff-frei
oder abhebend klassifiziert, Observablen der 442 liftoff-freien Punkte auf ≤ 6e-6 gleich.

Matthias Früh · PCMMS · September 2026
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import skew

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
sys.path.insert(0, HERE)
from finesweep import (M, MG, F_HZ, T_CYC, RTOP, RBOT, K, C_DAMP, DT,  # noqa: E402
                       z_egg_zdd)

N_PER = int(round(T_CYC / DT))          # 2000 Stichproben je Periode wie in der Engine
OVERSAMPLE = 8                          # feineres Raster für das Spektrum des Profils
SINUS_AMPLITUDE = (RTOP + RBOT) / 2     # aus sweep_7x7_sinus.csv rekonstruiert (data/README.md)
OMEGA = 2 * np.pi * F_HZ


def sinus_zdd(t, amplitude=SINUS_AMPLITUDE):
    return -amplitude * OMEGA**2 * np.sin(OMEGA * t)


def profile_spectrum(profile='egg', oversample=OVERSAMPLE, n=None):
    """Fourier-Koeffizienten P_k der Profilbeschleunigung auf einem Raster mit N_PER·oversample (oder n)
    Punkten je Periode."""
    n = N_PER * oversample if n is None else n
    t = np.arange(n) * (T_CYC / n)
    a = z_egg_zdd(t) if profile == 'egg' else sinus_zdd(t)
    P = np.fft.rfft(a)
    # Gleichanteil exakt null: Über einen Zyklus gilt ∫a dt = (2π/T)·(RBOT/TFAST − RTOP/THOLD) = 0, weil
    # RBOT = RTOP·TFAST/THOLD (beim Sinus trivial). Die Abtastung liefert nur Rundungsreste; damit ist
    # ⟨N⟩ = M·g in der linearen Lösung exakt und wird nicht numerisch gemittelt.
    P[0] = 0.0
    return P, n


def transfer(K_c, C_c, n_harm, h_one=(), f_hz=F_HZ):
    """H(kω) für k = 0 … n_harm−1 bei der Anregungsfrequenz f_hz; K_c = None bedeutet starre Auflage
    (H = 1). Für die Harmonischen in h_one wird H := 1 gesetzt (Diagnose ohne Kontaktresonanz; kein
    physikalisches Modell, deshalb dort nur F_min auswerten, nicht z)."""
    w = 2 * np.pi * f_hz * np.arange(n_harm)
    if K_c is None:
        return np.ones(n_harm, complex), np.zeros(n_harm, complex)
    den = K_c - M * w**2 + 1j * w * C_c
    H, Y = (K_c + 1j * w * C_c) / den, -1.0 / den     # Kraft- und Nachgiebigkeitsübertragung
    H[list(h_one)] = 1.0
    return H, Y


def solve(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', oversample=OVERSAMPLE,
          chunk=256, h_one=(), f_hz=F_HZ):
    """Stationäre Lösung für beliebig viele Phasenpunkte. Gibt ein Dict mit Arrays zurück
    (Spalten wie in den CSV-Dateien der Engine, dazu valid und F_min_lin). f_hz ändert die
    Anregungsfrequenz bei gleichem Hub; die Profilbeschleunigung skaliert dann mit (f_hz/10 Hz)²."""
    phi2 = np.atleast_1d(np.asarray(phi2_deg, float))
    phi3 = np.atleast_1d(np.asarray(phi3_deg, float))
    P, n = profile_spectrum(profile, oversample)
    P = P * (f_hz / F_HZ) ** 2
    k = np.arange(P.size)
    H, Y = transfer(K_c, C_c, P.size, h_one, f_hz)
    out = {c: np.empty(phi2.size) for c in
           ('F_mean', 'F_skew', 'liftoff', 'F_max', 'F_min', 'peak_ratio', 'F_min_lin', 'z_max')}
    out['valid'] = np.empty(phi2.size, bool)
    for s in range(0, phi2.size, chunk):
        sl = slice(s, s + chunk)
        comb = (1 + np.exp(-1j * np.outer(np.radians(phi2[sl]), k))
                + np.exp(-1j * np.outer(np.radians(phi3[sl]), k))) / 3
        A = P * comb
        F = MG + mu * M * np.fft.irfft(A * H, n, axis=1)[:, ::oversample]   # Stichproben wie in der Engine
        if K_c is None:
            z_max = np.full(F.shape[0], -np.inf)
        else:                                               # Auflagerkoordinate um die statische Einfederung
            z_max = (-MG / K_c + mu * M * np.fft.irfft(A * Y, n, axis=1)[:, ::oversample]).max(1)
        F_min, F_max = F.min(1), F.max(1)
        valid = (F_min > 0) & (z_max < 0)
        denom = MG - F_min
        out['F_mean'][sl] = MG                              # exakt, Gleichanteil null (profile_spectrum)
        out['F_skew'][sl] = np.where(valid, skew(F, axis=1), np.nan)
        out['liftoff'][sl] = np.where(valid, 0.0, np.nan)
        out['F_max'][sl] = np.where(valid, F_max, np.nan)
        out['F_min'][sl] = np.where(valid, F_min, np.nan)
        out['peak_ratio'][sl] = np.where(valid & (denom > 1e-6),
                                         (F_max - MG) / np.where(denom > 1e-6, denom, 1.0), np.nan)
        out['F_min_lin'][sl] = F_min
        out['z_max'][sl] = z_max
        out['valid'][sl] = valid
    out['phi2_deg'], out['phi3_deg'] = phi2, phi3
    return out


def waveform(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', oversample=OVERSAMPLE):
    """N(t) der linearen Lösung über eine Periode auf dem feinen Raster (Zeit in s, Kraft in N)."""
    P, n = profile_spectrum(profile, oversample)
    k = np.arange(P.size)
    H, _ = transfer(K_c, C_c, P.size)
    comb = (1 + np.exp(-1j * k * np.radians(phi2_deg)) + np.exp(-1j * k * np.radians(phi3_deg))) / 3
    return np.arange(n) * (T_CYC / n), MG + mu * M * np.fft.irfft(P * comb * H, n)


def contact_map(step=1.0, K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', h_one=(), per_step=10):
    """Lineares F_min und z_max auf dem Raster φ₂, φ₃ ∈ {0, step, …} (360/step ganzzahlig). Eine
    Phasenverschiebung um i·step ist dort eine zyklische Verschiebung des Zeitsignals um i·per_step
    Stichproben; so kostet die 1°-Karte Sekunden. Rückgabe: Phasen [°], F_min, z_max, valid
    (Kontaktast existiert: F_min > 0 und z_max < 0), Index [i, j] ↔ (φ₂, φ₃) = (i·step, j·step)."""
    m = int(round(360.0 / step))
    if abs(m * step - 360.0) > 1e-9:
        raise ValueError('360/step muss ganzzahlig sein')
    n = m * per_step
    P, _ = profile_spectrum(profile, n=n)
    H, Y = transfer(K_c, C_c, P.size, h_one)
    h = mu * M * np.fft.irfft(P * H, n) / 3                  # Beitrag eines Moduls zu N(t) − M·g
    g = mu * M * np.fft.irfft(P * Y, n) / 3                  # Beitrag eines Moduls zu z(t) + M·g/K
    Rh = np.stack([np.roll(h, i * per_step) for i in range(m)])
    Rg = np.stack([np.roll(g, i * per_step) for i in range(m)])
    F_min, z_max = np.empty((m, m)), np.empty((m, m))
    for i in range(m):
        F_min[i] = MG + ((h + Rh[i])[None, :] + Rh).min(1)
        z_max[i] = (-np.inf if K_c is None else -MG / K_c + ((g + Rg[i])[None, :] + Rg).max(1))
    return np.arange(m) * step, F_min, z_max, (F_min > 0) & (z_max < 0)


def components(valid):
    """Zusammenhängende Gebiete einer periodischen Karte (4er-Nachbarschaft, Ränder verbunden).
    Gibt je Gebiet (Anzahl Punkte, Liste der Indizes) zurück, größte zuerst."""
    from scipy import ndimage
    lab, n = ndimage.label(valid)
    parent = list(range(n + 1))

    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for x, y in ((lab[0, :], lab[-1, :]), (lab[:, 0], lab[:, -1])):   # periodische Ränder
        for a, b in zip(x, y):
            if a and b:
                parent[root(a)] = root(b)
    roots = np.array([root(a) for a in range(n + 1)])[lab]
    out = [np.argwhere((roots == r) & valid) for r in np.unique(roots[valid])]
    return sorted(((len(c), c) for c in out), key=lambda x: -x[0])


def orbit_state(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, mu=1.0, oversample=OVERSAMPLE):
    """Zustand (z, ż) der linearen periodischen Lösung bei t = 0, als Startwert für rk4()."""
    P, n = profile_spectrum(oversample=oversample)
    k = np.arange(P.size)
    _, Y = transfer(K_c, C_c, P.size)
    comb = (1 + np.exp(-1j * k * np.radians(phi2_deg)) + np.exp(-1j * k * np.radians(phi3_deg))) / 3
    X = mu * M * P * comb * Y
    return (-MG / K_c + np.fft.irfft(X, n)[0], np.fft.irfft(1j * OMEGA * k * X, n)[0])


def c_for(K_c, zeta):
    return 2 * zeta * np.sqrt(K_c * M)


ZETA0 = C_DAMP / (2 * np.sqrt(K * M))   # Dämpfungsgrad der Referenz, 0,099228 („ζ fest“)


def rk4(phi2_deg, phi3_deg, K_c=K, C_c=C_DAMP, z0=None, v0=0.0, t_sim=15.0, t_eval=10.0, dt=DT, t0=0.0):
    """Zeitintegration wie in der Engine (RK4, Kontaktkraft aus der ersten Stufe, unilateraler
    Feder-Dämpfer-Kontakt), aber mit wählbarem K, C, Anfangszustand (z0, v0) und Startzeit t0. Ohne z0
    startet sie wie die Engine in der statischen Ruhelage bei t = 0. Gibt Liftoff-Anteil [%], F_max und
    F_min der letzten t_eval Sekunden zurück, je Phasenpunkt."""
    phi2 = np.atleast_1d(np.asarray(phi2_deg, float))
    phi3 = np.atleast_1d(np.asarray(phi3_deg, float))
    tau2, tau3 = np.radians(phi2) / OMEGA, np.radians(phi3) / OMEGA
    z = np.broadcast_to(-MG / K_c if z0 is None else z0, phi2.shape).astype(float)
    zd = np.broadcast_to(v0, phi2.shape).astype(float)
    t_start = np.broadcast_to(t0, phi2.shape).astype(float)

    def rhs(z, zd, t):
        F = -K_c * z - C_c * zd
        Fc = np.where((z >= 0.0) | (F <= 0.0), 0.0, F)
        a = (z_egg_zdd(t) + z_egg_zdd(t - tau2) + z_egg_zdd(t - tau3)) / 3.0
        return zd, -MG / M + Fc / M - a, Fc

    n_steps, n_eval = int(round(t_sim / dt)), int(round(t_eval / dt))
    lift = np.zeros(phi2.size)
    F_max, F_min = np.full(phi2.size, -np.inf), np.full(phi2.size, np.inf)
    for i in range(n_steps):
        t = t_start + i * dt
        k1z, k1d, Fc = rhs(z, zd, t)
        k2z, k2d, _ = rhs(z + 0.5 * dt * k1z, zd + 0.5 * dt * k1d, t + 0.5 * dt)
        k3z, k3d, _ = rhs(z + 0.5 * dt * k2z, zd + 0.5 * dt * k2d, t + 0.5 * dt)
        k4z, k4d, _ = rhs(z + dt * k3z, zd + dt * k3d, t + dt)
        z = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6.0
        zd = zd + dt * (k1d + 2 * k2d + 2 * k3d + k4d) / 6.0
        if i >= n_steps - n_eval:
            lift += Fc < 1e-9
            F_max, F_min = np.maximum(F_max, Fc), np.minimum(F_min, Fc)
    return dict(liftoff=100.0 * lift / n_eval, F_max=F_max, F_min=F_min)


# ── Kommandos ────────────────────────────────────────────────────────────────
def validate():
    """Abgleich mit den Engine-Datensätzen: Liftoff-Klassifikation aller Punkte, Observablen aller
    liftoff-freien Punkte (Toleranz 1e-4 N bzw. dimensionslos) und Nullkontrolle |⟨F⟩ − M·g| der Engine an
    diesen Punkten (Toleranz 1e-5 N; die lineare Lösung hat ⟨F⟩ = M·g exakt)."""
    checks = [('sweep_19x19.csv', 'phi2_deg', 'phi3_deg', 'peak_ratio', 'egg'),
              ('finesweep_2deg_120_240.csv', 'phi2_deg', 'phi3_deg', 'peak_ratio', 'egg'),
              ('sweep_7x7_sinus.csv', 'phi2', 'phi3', 'asym', 'sinus')]
    ok = True
    for fname, c2, c3, ca, prof in checks:
        df = pd.read_csv(os.path.join(DATA, fname))
        r = solve(df[c2].values, df[c3].values, profile=prof)
        free = (df.liftoff == 0).values
        mis = int((r['valid'] != free).sum())
        dev = {'|F_mean−Mg|': np.abs(df.F_mean.values[free] - MG).max(),
               'F_min': np.abs(r['F_min'][free] - df.F_min.values[free]).max(),
               'F_max': np.abs(r['F_max'][free] - df.F_max.values[free]).max(),
               'F_skew': np.abs(r['F_skew'][free] - df.F_skew.values[free]).max(),
               'A': np.abs(r['peak_ratio'][free] - df[ca].values[free]).max()}
        tol = {'|F_mean−Mg|': 1e-5, 'F_min': 1e-4, 'F_max': 1e-4, 'F_skew': 1e-4, 'A': 1e-4}
        bad = [q for q in dev if not dev[q] <= tol[q]]
        ok &= (mis == 0) and not bad
        print(f'{fname}: {len(df)} Punkte, {free.sum()} liftoff-frei, Klassifikation abweichend: {mis}')
        print('   max ' + '  '.join(f'{q} {v:.1e}' for q, v in dev.items())
              + ('   OK' if not bad and mis == 0 else f'   FEHLER: {bad or "Klassifikation"}'))
    print('Ergebnis:', 'bestanden' if ok else 'NICHT bestanden')
    return ok


def ktable():
    """K-Tabelle im Werkstattbericht: F_min am triphasischen Punkt über K, das Band um 3f = f_n, in dem
    er selbst abhebt, und eine RK4-Gegenprobe darin (ca. 15 s)."""
    print(f'F_min bei (120°, 240°) [N], Referenzparameter bis auf K und C; ζ fest = {ZETA0:.6f}')
    print(f'{"K [N/m]":>10} {"3f/f_n":>7} {"ζ fest, C = 2ζ√(KM)":>20} {"C = 16 N·s/m fest":>18}')
    for K_c in [1e4, 2.3e4, 3e4, 1e5, 1e6, 1e7]:
        f_n = np.sqrt(K_c / M) / (2 * np.pi)
        vals = []
        for C_c in (c_for(K_c, ZETA0), C_DAMP):
            r = solve(120.0, 240.0, K_c, C_c)
            vals.append(f'{r["F_min"][0]:.4f}' if r['valid'][0] else f'hebt ab ({r["F_min_lin"][0]:+.3f})')
        print(f'{K_c:>10.0f} {3 * F_HZ / f_n:>7.2f} {vals[0]:>20} {vals[1]:>18}')
    r = solve(120.0, 240.0, None)
    print(f'{"starr":>10} {0:>7.2f} {r["F_min"][0]:>20.5f} {r["F_min"][0]:>18.5f}')
    Ks = np.arange(20000.0, 28001.0, 250.0)
    fmin = np.array([solve(120.0, 240.0, K_c, c_for(K_c, ZETA0))['F_min_lin'][0] for K_c in Ks])
    band = Ks[fmin <= 0]
    print(f'3f = f_n bei K = {M * (3 * OMEGA) ** 2:.0f} N/m. Lineares F_min ≤ 0 (ζ fest, Raster 250 N/m) für '
          f'K = {band.min():.0f} … {band.max():.0f} N/m, Minimum {fmin.min():+.3f} N bei K = {Ks[fmin.argmin()]:.0f}')
    r = rk4(120.0, 240.0, 23000.0, c_for(23000.0, ZETA0))
    print(f'RK4 bei K = 23000 N/m (ζ fest, Start wie Engine): Liftoff {r["liftoff"][0]:.2f} %')


def harmonics():
    """Anteil der zweiten Harmonischen an Zeltsteigung und Karte (Referenz: 2f ≈ f_n)."""
    f_n = np.sqrt(K / M) / (2 * np.pi)
    print(f'Referenz: f_n = {f_n:.2f} Hz, f/f_n = {F_HZ / f_n:.3f}, 2f/f_n = {2 * F_HZ / f_n:.3f}, '
          f'3f/f_n = {3 * F_HZ / f_n:.3f}')
    P, n = profile_spectrum()
    H, _ = transfer(K, C_DAMP, P.size)
    print('Kraftamplitude der k-ten Harmonischen für ein Modul mit voller Masse (= synchrone Phasung):')
    for k in range(1, 5):
        print(f'  k = {k}  {k * F_HZ:.0f} Hz  |H| = {abs(H[k]):.2f}  2·M·|H·P_k| = {2 * M * abs(H[k] * P[k]) / n:.3f} N')

    def slopes(**kw):
        f = [solve(p2, 240.0, **kw)['F_min_lin'][0] for p2 in (118.0, 120.0, 122.0)]
        return (f[1] - f[0]) / 2, (f[1] - f[2]) / 2

    print('Zeltsteigung entlang φ₃ = 240° [N/°], 118° → 120° und 122° → 120°:')
    print('  Referenz          {:.3f}  {:.3f}'.format(*slopes()))
    print('  |H₂| := 1         {:.3f}  {:.3f}'.format(*slopes(h_one=(2,))))
    for K_c in (3e4, 1e5, 1e6, 1e7):
        print(f'  ζ fest, K = {K_c:.0e}  ' + '{:.3f}  {:.3f}'.format(*slopes(K_c=K_c, C_c=c_for(K_c, ZETA0))))
    ref, h2 = contact_map(1.0)[1], contact_map(1.0, h_one=(2,))[1]
    print(f'Anteil mit F_min > 0 (Kontaktast), 1°-Raster: Referenz {100 * (ref > 0).mean():.2f} %, '
          f'|H₂| := 1 {100 * (h2 > 0).mean():.1f} %')


def contact(long_run=False):
    """Kontaktast: Anteil im Phasenraum (1°-Raster) für mehrere Auflagen, Gebiete bei der Referenz und
    RK4-Proben zur Bistabilität. long_run: zusätzlich 200 s bei Δt und Δt/2 (ca. 20–25 min).
    Die Bistabilität bleibt über 200 s und bei halbiertem Zeitschritt bestehen: Bei (35°, 116°) ergibt der
    Standardstart λ = 75,82 % bzw. 75,81 % (Δt = 50 bzw. 25 µs), F_max 39,49 bzw. 39,48 N; der Start auf
    dem linearen Orbit λ = 0 %, F_max 19,81 N."""
    cases = [('Referenz, K = 1e4 N/m', dict()),
             ('K = 1e6 N/m, ζ fest', dict(K_c=1e6, C_c=c_for(1e6, ZETA0))),
             ('K = 1e6 N/m, C = 16 N·s/m fest', dict(K_c=1e6, C_c=C_DAMP)),
             ('starre Auflage', dict(K_c=None, C_c=0.0)),
             ('Referenz, halbe bewegte Masse (μ = 0,5)', dict(mu=0.5))]
    print('Anteil mit Kontaktast (F_min > 0 und z < 0), 1°-Raster:')
    for name, kw in cases:
        print(f'  {name:42s} {100 * contact_map(1.0, **kw)[3].mean():6.2f} %')
    _, F_min, _, valid = contact_map(1.0)
    print('Zusammenhängende Gebiete bei der Referenz (Zentrum [°], größtes F_min):')
    for cnt, idx in components(valid):
        c = idx.mean(0)
        print(f'  {cnt:5d} Punkte ({100 * cnt / valid.size:.3f} %) um ({c[0]:.0f}°, {c[1]:.0f}°), '
              f'F_min max {F_min[tuple(idx.T)].max():.3f} N')
    probes = [('Insel (35°, 116°), Start wie Engine', 35.0, 116.0, None, 0.0),
              ('Insel (35°, 116°), Start auf dem linearen Orbit', 35.0, 116.0, *orbit_state(35.0, 116.0)),
              ('Insel (28°, 115°), Start wie Engine', 28.0, 115.0, None, 0.0),
              ('Insel (28°, 115°), Start auf dem linearen Orbit', 28.0, 115.0, *orbit_state(28.0, 115.0)),
              ('Hauptgebiet (98°, 240°), Wurf v₀ = 3 m/s', 98.0, 240.0, None, 3.0),
              ('Hauptgebiet (148°, 240°), Wurf v₀ = 3 m/s', 148.0, 240.0, None, 3.0)]
    z0 = np.array([-MG / K if p[3] is None else p[3] for p in probes])
    v0 = np.array([p[4] for p in probes])
    runs = [(15.0, DT)] + ([(200.0, DT), (200.0, DT / 2)] if long_run else [])
    for t_sim, dt in runs:
        print(f'RK4, {t_sim:.0f} s, Δt = {dt * 1e6:.0f} µs, Auswertung der letzten 10 s:')
        r = rk4([p[1] for p in probes], [p[2] for p in probes], z0=z0, v0=v0, t_sim=t_sim, dt=dt)
        for i, p in enumerate(probes):
            print(f'  {p[0]:48s} Liftoff {r["liftoff"][i]:6.2f} %  F_max {r["F_max"][i]:6.2f} N')


def main_region_probe(step=3.0):
    """Monostabilität des Hauptgebiets um (120°, 240°): jeder Rasterpunkt des Kontaktasts (Raster step)
    mit 7 Starts – Standardstart der Engine sowie ż₀ ∈ {0,5; 1,5; 3,0} m/s × t₀ ∈ {0; 0,05} s aus der
    statischen Ruhelage –, je 20 s RK4, Auswertung der letzten 4 s (ca. 6–8 min)."""
    phis, _, _, valid = contact_map(step)
    i0 = (int(round(120.0 / step)), int(round(240.0 / step)))
    idx = next(c for _, c in components(valid) if (c == i0).all(1).any())
    starts = [(0.0, 0.0)] + [(v, t) for v in (0.5, 1.5, 3.0) for t in (0.0, 0.05)]
    p2, p3 = np.repeat(phis[idx[:, 0]], len(starts)), np.repeat(phis[idx[:, 1]], len(starts))
    v0 = np.tile([s[0] for s in starts], len(idx))
    t0 = np.tile([s[1] for s in starts], len(idx))
    r = rk4(p2, p3, v0=v0, t0=t0, t_sim=20.0, t_eval=4.0)
    n_lift = int((r['liftoff'] > 0).sum())
    print(f'Hauptgebiet um (120°, 240°), {step:g}°-Raster: {len(idx)} Punkte × {len(starts)} Starts = {p2.size} '
          f'RK4-Läufe, 20 s, Auswertung der letzten 4 s: {p2.size - n_lift} enden im Kontakt, '
          f'{n_lift} mit Liftoff (max. {r["liftoff"].max():.2f} %)')


def section(K_c=K, C_c=C_DAMP, mu=1.0, profile='egg', f_hz=F_HZ, phi3=240.0, lo=100.0, hi=140.0, step=2.0):
    """Querschnitt entlang φ₂ bei festem φ₃ (Standard: der 21-Punkt-Schnitt 100° … 140° bei φ₃ = 240°):
    Observablen der linearen Lösung und Amplituden |N_k| der Harmonischen k = 1 … 3 der Kontaktkraft.
    Format der Vorhersagetabelle für gemessene K, C, μ und f."""
    p2 = np.arange(lo, hi + step / 2, step)
    r = solve(p2, phi3, K_c, C_c, mu, profile, f_hz=f_hz)
    P, n = profile_spectrum(profile)
    H, _ = transfer(K_c, C_c, 4, f_hz=f_hz)
    amp1 = 2 * mu * M * np.abs(H[:4] * P[:4]) / n * (f_hz / F_HZ) ** 2      # synchrone Phasung
    kk = np.arange(1, 4)
    comb = np.abs(1 + np.exp(-1j * np.outer(np.radians(p2), kk)) + np.exp(-1j * kk * np.radians(phi3))) / 3
    f_n = np.inf if K_c is None else np.sqrt(K_c / M) / (2 * np.pi)
    print(f'f = {f_hz:g} Hz, K = {"starr" if K_c is None else f"{K_c:.4g} N/m"}, C = {C_c:.4g} N·s/m, μ = {mu:g}, '
          f'f_n = {f_n:.2f} Hz, f/f_n = {f_hz / f_n:.3f}; |N_k| bei synchroner Phasung: '
          + ', '.join(f'k={k} {amp1[k]:.4f} N' for k in (1, 2, 3)))
    print(f'{"φ₂ [°]":>7} {"Kontakt":>8} {"F_min_lin":>10} {"F_max":>8} {"Schiefe":>8} {"A":>7} '
          f'{"|N_1|":>8} {"|N_2|":>8} {"|N_3|":>8}')
    for i, x in enumerate(p2):
        print(f'{x:>7.1f} {str(bool(r["valid"][i])):>8} {r["F_min_lin"][i]:>10.4f} {r["F_max"][i]:>8.4f} '
              f'{r["F_skew"][i]:>8.4f} {r["peak_ratio"][i]:>7.4f} '
              + ' '.join(f'{amp1[k] * comb[i, k - 1]:>8.4f}' for k in kk))
    j = int(np.argmax(r['F_min_lin']))
    if 0 < j < p2.size - 1:
        print(f'Spitze bei φ₂ = {p2[j]:g}°, F_min = {r["F_min_lin"][j]:.4f} N; Steigung links '
              f'{(r["F_min_lin"][j] - r["F_min_lin"][j - 1]) / step:.4f} N/°, rechts '
              f'{(r["F_min_lin"][j] - r["F_min_lin"][j + 1]) / step:.4f} N/°')


def params(a):
    K_c = None if a.rigid else a.K
    C_c = 0.0 if a.rigid else (c_for(a.K, a.zeta) if a.zeta is not None else a.C)
    return K_c, C_c


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--ktable', action='store_true')
    ap.add_argument('--harmonics', action='store_true')
    ap.add_argument('--contact', action='store_true')
    ap.add_argument('--long', action='store_true', help='mit --contact: zusätzlich 200 s bei Δt und Δt/2')
    ap.add_argument('--grid', action='store_true',
                    help='mit --contact: Hauptgebiet im 3°-Raster, 7 Starts je Punkt (ca. 6–8 min)')
    ap.add_argument('--point', nargs=2, type=float, metavar=('PHI2', 'PHI3'))
    ap.add_argument('--map', metavar='CSV')
    ap.add_argument('--step', type=float, default=2.0, help='Rasterweite der Karte in Grad')
    ap.add_argument('--K', type=float, default=K)
    ap.add_argument('--C', type=float, default=C_DAMP)
    ap.add_argument('--zeta', type=float, default=None, help='setzt C = 2ζ·√(K·M)')
    ap.add_argument('--mu', type=float, default=1.0, help='Anteil der bewegten Masse')
    ap.add_argument('--rigid', action='store_true')
    ap.add_argument('--sinus', action='store_true')
    ap.add_argument('--section', action='store_true', help='21-Punkt-Schnitt φ₂ = 100° … 140° bei φ₃ = 240°')
    ap.add_argument('--phi3', type=float, default=240.0, help='mit --section: festes φ₃')
    ap.add_argument('--f', type=float, default=F_HZ, help='Anregungsfrequenz bei gleichem Hub [Hz]')
    a = ap.parse_args()
    prof = 'sinus' if a.sinus else 'egg'
    if a.validate:
        sys.exit(0 if validate() else 1)
    if a.ktable:
        ktable()
    if a.harmonics:
        harmonics()
    if a.contact:
        contact(a.long)
        if a.grid:
            main_region_probe()
    if a.section:
        section(*params(a), a.mu, prof, a.f, a.phi3)
    if a.point:
        K_c, C_c = params(a)
        r = solve(*a.point, K_c, C_c, a.mu, prof, f_hz=a.f)
        for q in ('valid', 'F_mean', 'F_skew', 'F_max', 'F_min', 'peak_ratio', 'F_min_lin'):
            print(f'{q:>10}: {r[q][0]}')
    if a.map:
        K_c, C_c = params(a)
        g = np.arange(0.0, 360.0, a.step)
        P2, P3 = np.meshgrid(g, g, indexing='ij')
        r = solve(P2.ravel(), P3.ravel(), K_c, C_c, a.mu, prof, f_hz=a.f)
        cols = ['phi2_deg', 'phi3_deg', 'valid', 'F_mean', 'F_skew', 'liftoff', 'F_max', 'F_min',
                'peak_ratio', 'F_min_lin']
        pd.DataFrame({c: r[c] for c in cols}).to_csv(a.map, index=False, float_format='%.6f')
        print(f'{a.map}: {r["valid"].size} Punkte, mit Kontaktast {100 * r["valid"].mean():.1f} %')
    if not (a.validate or a.ktable or a.harmonics or a.contact or a.section or a.point or a.map):
        ap.print_help()


if __name__ == '__main__':
    main()
