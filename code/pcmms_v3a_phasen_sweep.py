"""
═══════════════════════════════════════════════════════════════════════════════
  PCMMS – v3a Mehrmodul-Phasensweep  (lokal ausführbar, Checkpoint-fest)
═══════════════════════════════════════════════════════════════════════════════

  Zweck
  ─────
  Sweep über (φ₂, φ₃) ∈ [0°, 360°)² für ein Drei-Modul-System mit
  geglättetem Egg-Profil und unilateralem Kontakt. Pro Phasenpunkt werden
  vier Observablen aus der Wellenform F_c(t) berechnet:
     · ⟨F⟩         (Sanity gegen Theorem ⟨F⟩ = Mg)
     · Schiefe     (Hauptobservable nach v3b §3.1)
     · Liftoff-Anteil
     · Spitzenkraftverhältnis  (F_max − Mg) / (Mg − F_min)
  Am Ende werden drei Heatmaps erzeugt.

  Bewegungsgleichung am Rahmen
  ────────────────────────────
     M·z̈_f = −M·g + F_c(z_f, ż_f) − (M/3)·[z̈_egg(t)
                                          + z̈_egg(t−τ₂)
                                          + z̈_egg(t−τ₃)]
     mit τₖ = φₖ / (2π·f)

  Checkpointing
  ─────────────
  Nach jedem Punkt wird das Ergebnis an die Output-CSV angehängt. Bei
  Neustart liest das Skript die CSV, identifiziert schon berechnete
  Punkte und rechnet nur die fehlenden. Sicher gegen Stromausfall,
  Absturz, manuelles Anhalten (Ctrl-C).

  Konfiguration
  ─────────────
  Alle Parameter stehen weiter unten im Block "KONFIGURATION".
  Auflösung N_GRID anpassbar:
     13  → 169 Punkte ·    schnelles Tasten   (~ 15–25 min)
     19  → 361 Punkte ·    Standard            (~ 30–60 min)
     25  → 625 Punkte ·    fein                (~ 60–120 min)
     37  → 1369 Punkte ·   sehr fein           (mehrere Stunden)
  Zeiten grob, je nach Rechner.

  Aufruf
  ──────
     python3 pcmms_v3a_phasen_sweep.py

  Resultate werden in OUT_DIR abgelegt:
     · sweep_<N_GRID>x<N_GRID>.csv       – Rohdaten, fortlaufend
     · sweep_<N_GRID>x<N_GRID>_heat.png  – Heatmaps am Ende
     · sweep_<N_GRID>x<N_GRID>_log.txt   – Lauf-Logbuch

  Plot-only-Modus
  ───────────────
  Wenn der Sweep abgeschlossen ist (oder nur ein Teil), kann das Skript
  ohne Neuberechnung die Plots aktualisieren. Dafür im Block KONFIGURATION
  PLOT_ONLY = True setzen und nochmal ausführen.

  Matthias Früh · Mai 2026 · prä-experimentell · Grundlagenforschung
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import csv
import time
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')      # auf Headless-Setups; bei Bedarf entfernen
import matplotlib.pyplot as plt
from scipy.stats import skew

# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURATION  – anpassen falls gewünscht
# ══════════════════════════════════════════════════════════════════════════════

# Auflösung des Phasenrasters (siehe Header)
N_GRID = 19

# Plot-only Modus (überspringt Simulation, plottet nur aus CSV)
PLOT_ONLY = False

# Output-Verzeichnis
OUT_DIR = os.path.join(os.path.expanduser('~'), 'pcmms_outputs_v3a_sweep')

# ── Systemparameter (konsistent mit v3a geglättet) ────────────────────────────
M       = 0.650            # kg     Gesamtmasse (drei Module à M/3)
G       = 9.81             # m/s²
MG      = M * G            # 6.3765 N

F_HZ    = 10.0             # Hz     Zyklusfrequenz
T_CYC   = 1.0 / F_HZ       # 0.1 s

RTOP    = 0.005            # m      Hold-Radius (oben)
THOLD   = 0.65             # –      Hold-Anteil pro Zyklus
TFAST   = 1.0 - THOLD      # 0.35
RBOT    = RTOP * TFAST / THOLD   # 2.692 mm – C¹-stetig

K       = 10000.0          # N/m    Kontakt-Steifigkeit
C_DAMP  = 16.0             # N·s/m  Kontakt-Dämpfung (ζ ≈ 0.1)

# ── Numerik ───────────────────────────────────────────────────────────────────
DT      = 5e-5             # s      Zeitschritt (fein wegen steifer Feder)
T_SIM   = 15.0             # s      Simulationsdauer pro Punkt
T_BURN  = 5.0              # s      Burn-in (vor der Auswertung)
N_STEPS = int(T_SIM / DT)
N_BURN  = int(T_BURN / DT)

# ── Status-Anzeige ────────────────────────────────────────────────────────────
PRINT_EVERY = 1            # jeden wievielten Punkt auf der Konsole anzeigen

# ══════════════════════════════════════════════════════════════════════════════
# MODELL
# ══════════════════════════════════════════════════════════════════════════════

def z_egg_zdd(t_in):
    """Beschleunigung der geglätteten Egg-Trajektorie zur Zeit t_in.
    Modulo-Operation macht die Funktion zyklisch."""
    phi = (t_in % T_CYC) / T_CYC
    if phi < THOLD:
        s = phi / THOLD
        return -RTOP * (math.pi / (THOLD * T_CYC))**2 * math.sin(math.pi * s)
    s = (phi - THOLD) / TFAST
    return RBOT * (math.pi / (TFAST * T_CYC))**2 * math.sin(math.pi * s)

def total_zdd_egg(t_in, tau2, tau3):
    """Mittel der drei phasenversetzten Egg-Beschleunigungen."""
    return (z_egg_zdd(t_in)
          + z_egg_zdd(t_in - tau2)
          + z_egg_zdd(t_in - tau3)) / 3.0

def F_contact_unilateral(z, zd):
    """Unilateraler Feder-Dämpfer-Kontakt: nur Druck, kein Zug."""
    F = -K * z - C_DAMP * zd
    if z >= 0.0 or F <= 0.0:
        return 0.0
    return F

# ══════════════════════════════════════════════════════════════════════════════
# RK4-INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════

def rhs(z, zd, t_in, tau2, tau3):
    """Rechte Seite der Bewegungsgleichung. Gibt (dz/dt, dżdt, F_c) zurück."""
    zdd_egg = total_zdd_egg(t_in, tau2, tau3)
    Fc = F_contact_unilateral(z, zd)
    return zd, -G + Fc / M - zdd_egg, Fc

def rk4_step(z, zd, t_in, tau2, tau3):
    """Ein RK4-Schritt der Länge DT. Gibt (z_new, zd_new, F_c) zurück."""
    k1z, k1d, Fc = rhs(z,                zd,                t_in,           tau2, tau3)
    k2z, k2d, _  = rhs(z + 0.5*DT*k1z,   zd + 0.5*DT*k1d,   t_in + 0.5*DT,  tau2, tau3)
    k3z, k3d, _  = rhs(z + 0.5*DT*k2z,   zd + 0.5*DT*k2d,   t_in + 0.5*DT,  tau2, tau3)
    k4z, k4d, _  = rhs(z + DT*k3z,       zd + DT*k3d,       t_in + DT,      tau2, tau3)
    z_new  = z  + DT * (k1z + 2*k2z + 2*k3z + k4z) / 6.0
    zd_new = zd + DT * (k1d + 2*k2d + 2*k3d + k4d) / 6.0
    return z_new, zd_new, Fc

# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION EINES SWEEP-PUNKTES
# ══════════════════════════════════════════════════════════════════════════════

def simulate_point(phi2_deg, phi3_deg):
    """Simuliert einen Punkt im (φ₂, φ₃)-Raum, liefert vier Observablen."""
    phi2 = math.radians(phi2_deg)
    phi3 = math.radians(phi3_deg)
    tau2 = phi2 / (2 * math.pi * F_HZ)
    tau3 = phi3 / (2 * math.pi * F_HZ)

    # F_c-Werte nur ab Burn-in speichern – spart Speicher
    F_eval = np.empty(N_STEPS - N_BURN, dtype=np.float64)

    z, zd = -MG / K, 0.0     # Startwert: statisches Gleichgewicht
    for i in range(N_STEPS):
        t_in = i * DT
        z, zd, Fc = rk4_step(z, zd, t_in, tau2, tau3)
        if i >= N_BURN:
            F_eval[i - N_BURN] = Fc

    F_mean = float(np.mean(F_eval))
    F_skew = float(skew(F_eval))
    F_max  = float(np.max(F_eval))
    F_min  = float(np.min(F_eval))
    liftoff = float(np.mean(F_eval < 1e-9)) * 100.0
    if (MG - F_min) > 1e-6:
        peak_ratio = (F_max - MG) / (MG - F_min)
    else:
        peak_ratio = float('nan')

    return dict(F_mean=F_mean, F_skew=F_skew, F_max=F_max, F_min=F_min,
                liftoff=liftoff, peak_ratio=peak_ratio)

# ══════════════════════════════════════════════════════════════════════════════
# CHECKPOINT-LOGIK
# ══════════════════════════════════════════════════════════════════════════════

CSV_HEADER = ['phi2_deg', 'phi3_deg', 'F_mean', 'F_skew',
              'liftoff', 'F_max', 'F_min', 'peak_ratio']

def csv_path():
    return os.path.join(OUT_DIR, f'sweep_{N_GRID}x{N_GRID}.csv')

def load_done_points():
    """Liest CSV, gibt Set der schon berechneten (phi2, phi3)-Tupel (gerundet)."""
    path = csv_path()
    if not os.path.exists(path):
        return set(), []
    done = set()
    rows = []
    with open(path, 'r', newline='') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            p2 = float(row['phi2_deg'])
            p3 = float(row['phi3_deg'])
            done.add((round(p2, 3), round(p3, 3)))
            rows.append({k: float(v) for k, v in row.items()})
    return done, rows

def append_to_csv(phi2, phi3, result):
    """Hängt eine Zeile an die CSV. Erzeugt Header falls Datei neu."""
    path = csv_path()
    file_exists = os.path.exists(path)
    with open(path, 'a', newline='') as fh:
        writer = csv.writer(fh)
        if not file_exists:
            writer.writerow(CSV_HEADER)
        writer.writerow([
            f'{phi2:.3f}', f'{phi3:.3f}',
            f'{result["F_mean"]:.6f}', f'{result["F_skew"]:.6f}',
            f'{result["liftoff"]:.4f}',
            f'{result["F_max"]:.6f}', f'{result["F_min"]:.6f}',
            f'{result["peak_ratio"]:.6f}',
        ])

def write_log(msg):
    path = os.path.join(OUT_DIR, f'sweep_{N_GRID}x{N_GRID}_log.txt')
    with open(path, 'a') as fh:
        fh.write(msg + '\n')

# ══════════════════════════════════════════════════════════════════════════════
# HEATMAP-PLOT
# ══════════════════════════════════════════════════════════════════════════════

def plot_heatmaps():
    """Liest CSV und erzeugt drei Heatmaps + eine Δ⟨F⟩-Karte als Sanity."""
    done, rows = load_done_points()
    if len(rows) == 0:
        print('Keine Daten in der CSV.')
        return
    expected = N_GRID * N_GRID
    print(f'  CSV enthält {len(rows)} von {expected} erwarteten Punkten.')

    # Raster aufbauen
    phis = np.linspace(0.0, 360.0, N_GRID, endpoint=False)
    skew_grid    = np.full((N_GRID, N_GRID), np.nan)
    liftoff_grid = np.full((N_GRID, N_GRID), np.nan)
    peak_grid    = np.full((N_GRID, N_GRID), np.nan)
    dF_grid      = np.full((N_GRID, N_GRID), np.nan)

    for row in rows:
        # Index per ungefährer Übereinstimmung – robust gegen Rundungsfehler
        i2 = int(round(row['phi2_deg'] / (360.0 / N_GRID))) % N_GRID
        i3 = int(round(row['phi3_deg'] / (360.0 / N_GRID))) % N_GRID
        skew_grid[i3, i2]    = row['F_skew']
        liftoff_grid[i3, i2] = row['liftoff']
        peak_grid[i3, i2]    = row['peak_ratio']
        dF_grid[i3, i2]      = row['F_mean'] - MG

    # Plot
    COL = dict(bg='#090b0e', panel='#0d1117', grid='#1a2230',
               text='#c0cad8', muted='#3a4a5e')
    fig = plt.figure(figsize=(15, 12), facecolor=COL['bg'])
    fig.suptitle(f'PCMMS v3a Mehrmodul – Phasensweep {N_GRID}×{N_GRID}'
                 f'   ({len(rows)} / {expected} Punkte)',
                 color=COL['text'], fontsize=12, fontfamily='monospace', y=0.995)

    panels = [
        ('Schiefe der F_c-Wellenform', skew_grid, 'inferno'),
        ('Liftoff-Anteil [%]',         liftoff_grid, 'viridis'),
        ('Spitzenkraftverhältnis',     peak_grid, 'plasma'),
        ('Δ⟨F⟩ = ⟨F⟩ − Mg  [N]  (Sanity)', dF_grid, 'coolwarm'),
    ]
    for k, (ttl, data, cmap) in enumerate(panels):
        ax = fig.add_subplot(2, 2, k + 1)
        if 'Δ' in ttl:
            vmax = np.nanmax(np.abs(data))
            im = ax.imshow(data, origin='lower', cmap=cmap,
                           extent=[0, 360, 0, 360],
                           vmin=-vmax if vmax > 0 else -1e-3,
                           vmax= vmax if vmax > 0 else  1e-3,
                           interpolation='nearest', aspect='equal')
        else:
            im = ax.imshow(data, origin='lower', cmap=cmap,
                           extent=[0, 360, 0, 360],
                           interpolation='nearest', aspect='equal')
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(colors=COL['muted'], labelsize=8)
        ax.set_xlabel('φ₂ [°]', color=COL['muted'], fontsize=9)
        ax.set_ylabel('φ₃ [°]', color=COL['muted'], fontsize=9)
        ax.set_facecolor(COL['panel'])
        ax.tick_params(colors=COL['muted'], labelsize=8)
        for sp in ax.spines.values():
            sp.set_color(COL['grid'])
        ax.set_title(ttl, color=COL['text'], fontsize=10, fontfamily='monospace')

    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, f'sweep_{N_GRID}x{N_GRID}_heat.png')
    plt.savefig(out_png, dpi=130, facecolor=COL['bg'])
    plt.close()
    print(f'  → {out_png}')

    # Globale Statistik
    s_min, s_max = np.nanmin(skew_grid), np.nanmax(skew_grid)
    l_min, l_max = np.nanmin(liftoff_grid), np.nanmax(liftoff_grid)
    p_min, p_max = np.nanmin(peak_grid), np.nanmax(peak_grid)
    d_min, d_max = np.nanmin(dF_grid), np.nanmax(dF_grid)
    print('\nSpannweiten über das gerasterte (φ₂, φ₃)-Feld:')
    print(f'  Schiefe:               [{s_min:+.4f}, {s_max:+.4f}]   Δ = {s_max-s_min:.4f}')
    print(f'  Liftoff-Anteil [%]:    [{l_min:6.2f},  {l_max:6.2f}]   Δ = {l_max-l_min:.2f}')
    print(f'  Spitzenkraftverhältnis [{p_min:.3f}, {p_max:.3f}]   Δ = {p_max-p_min:.3f}')
    print(f'  Δ⟨F⟩ [N]:              [{d_min:+.3e}, {d_max:+.3e}]')

# ══════════════════════════════════════════════════════════════════════════════
# HAUPTROUTINE
# ══════════════════════════════════════════════════════════════════════════════

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print('═' * 76)
    print(f'  PCMMS v3a Mehrmodul-Phasensweep   N_GRID = {N_GRID}'
          f'   →  {N_GRID*N_GRID} Punkte')
    print('═' * 76)
    print(f'  Output-Verzeichnis: {OUT_DIR}')
    print(f'  CSV: sweep_{N_GRID}x{N_GRID}.csv')
    print(f'  T_SIM = {T_SIM} s   Burn-in = {T_BURN} s   dt = {DT} s')
    print(f'  Mg = {MG:.4f} N   Egg: RTOP={RTOP*1000:.2f} mm, RBOT={RBOT*1000:.2f} mm')
    print('═' * 76)

    if PLOT_ONLY:
        print('  PLOT_ONLY = True  – überspringe Simulation, plotte nur.')
        plot_heatmaps()
        return

    done, _ = load_done_points()

    # Punktegitter aufbauen
    phis = np.linspace(0.0, 360.0, N_GRID, endpoint=False)
    all_points = [(round(float(p2), 3), round(float(p3), 3))
                  for p2 in phis for p3 in phis]

    remaining = [p for p in all_points if p not in done]
    n_done = len(all_points) - len(remaining)

    print(f'\n  Schon berechnet: {n_done} / {len(all_points)}')
    print(f'  Noch zu rechnen: {len(remaining)} Punkte\n')

    if len(remaining) == 0:
        print('  Sweep ist komplett. Erzeuge nur Plots.')
        plot_heatmaps()
        return

    write_log(f'Sweep gestartet: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    write_log(f'  N_GRID={N_GRID}, T_SIM={T_SIM}, DT={DT}')
    write_log(f'  Resume nach {n_done} Punkten')

    t_start_total = time.time()
    t_acc = 0.0
    for j, (p2, p3) in enumerate(remaining):
        t_a = time.time()
        try:
            res = simulate_point(p2, p3)
        except KeyboardInterrupt:
            print('\n  KeyboardInterrupt – Sweep angehalten. Fortschritt gesichert.')
            write_log(f'Angehalten bei Punkt {j+1}/{len(remaining)}')
            return
        except Exception as e:
            print(f'\n  Fehler bei (φ₂={p2}, φ₃={p3}): {e}')
            write_log(f'Fehler bei (φ₂={p2}, φ₃={p3}): {e}')
            continue
        elapsed = time.time() - t_a
        t_acc += elapsed
        append_to_csv(p2, p3, res)

        if (j + 1) % PRINT_EVERY == 0 or j + 1 == len(remaining):
            t_avg = t_acc / (j + 1)
            eta = t_avg * (len(remaining) - j - 1)
            print(f'  [{j+1:>5}/{len(remaining)}]  '
                  f'(φ₂={p2:>6.2f}°, φ₃={p3:>6.2f}°)  '
                  f'skew={res["F_skew"]:+.3f}  '
                  f'liftoff={res["liftoff"]:5.1f}%  '
                  f'peakR={res["peak_ratio"]:6.3f}  '
                  f'[{elapsed:4.1f}s,  ETA {eta/60:5.1f} min]')

    t_total = time.time() - t_start_total
    print(f'\n  Sweep abgeschlossen in {t_total/60:.1f} min.')
    write_log(f'Sweep beendet: {time.strftime("%Y-%m-%d %H:%M:%S")}'
              f'  Gesamtdauer: {t_total/60:.1f} min')

    print('\n  Erzeuge Heatmaps ...')
    plot_heatmaps()

if __name__ == '__main__':
    main()
