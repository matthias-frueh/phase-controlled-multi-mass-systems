"""
plot_figures.py – Abbildungen für README und docs aus den Simulationsdaten in data/.

Erzeugt in docs/figures/ je eine helle und eine dunkle Fassung:
  zeltkurve_{light,dark}.png      F_min entlang φ₃ = 240° aus finesweep_2deg_120_240.csv
  phasenkarten_{light,dark}.png   Schiefe und Liftoff-Anteil aus sweep_19x19.csv
  wellenformen_{light,dark}.png   N(t) über drei Perioden für drei Phasenlagen
                                  (gerechnet mit finesweep.run, ca. 30 s)
  prinzipskizze_{light,dark}.png  Schema des Modells und Bewegungsprofil der Module
                                  (Zeichnung aus den Profilparametern der Engine, keine Simulation)

Aufruf (aus beliebigem Verzeichnis):  python3 code/plot_figures.py
Zeltkurve, Phasenkarten und Wellenformen zeigen Simulationsausgaben, keine Messdaten.
Die Prinzipskizze ist ein Schema und kein Ergebnis.

Matthias Früh · PCMMS · September 2026 · Prinzipskizze ergänzt im November 2026
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, Normalize
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = os.path.join(HERE, '..', 'docs', 'figures')
sys.path.insert(0, HERE)
import finesweep  # noqa: E402  (vektorisierte Engine, identische Parameter)

MG = finesweep.MG
N_GRID = 19
STEP = 360.0 / N_GRID

# ── Farben: zwei Fassungen, gleiche Rampen ───────────────────────────────────
THEMES = {
    'light': dict(surface='#fcfcfb', ink='#0b0b0b', ink2='#52514e', muted='#898781',
                  grid='#e1e0d9', axis='#c3c2b7', series='#2a78d6', mid='#f0efec',
                  seq=['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b'],
                  div=['#184f95', '#6da7ec', '#f0efec', '#ef9a98', '#e34948']),
    'dark': dict(surface='#1a1a19', ink='#ffffff', ink2='#c3c2b7', muted='#898781',
                 grid='#2c2c2a', axis='#383835', series='#3987e5', mid='#383835',
                 seq=['#0d366b', '#104281', '#1c5cab', '#2a78d6', '#3987e5', '#6da7ec', '#9ec5f4'],
                 div=['#6da7ec', '#256abf', '#383835', '#a83a3a', '#e66767']),
}

comma = FuncFormatter(lambda v, _: f'{v:g}'.replace('.', ','))


def style_axes(ax, th):
    ax.set_facecolor(th['surface'])
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(th['axis'])
        ax.spines[side].set_linewidth(1)
    ax.tick_params(colors=th['muted'], labelsize=9, length=3, width=1)
    ax.xaxis.label.set_color(th['ink2'])
    ax.yaxis.label.set_color(th['ink2'])


def new_figure(th, size):
    fig = plt.figure(figsize=size, facecolor=th['surface'])
    return fig


def title(fig, th, main, sub):
    fig.text(0.02, 0.97, main, color=th['ink'], fontsize=12, fontweight='bold',
             ha='left', va='top')
    fig.text(0.02, 0.915, sub, color=th['ink2'], fontsize=9, ha='left', va='top')


def fmt(v, nd):
    return f'{v:.{nd}f}'.replace('.', ',')


# ── 1 · Zeltkurve ────────────────────────────────────────────────────────────
def plot_tent(th, path):
    df = pd.read_csv(os.path.join(DATA, 'finesweep_2deg_120_240.csv'))
    line = df[np.isclose(df.phi3_deg, 240.0)].sort_values('phi2_deg')
    x, y = line.phi2_deg.values, line.F_min.values

    fig = new_figure(th, (7.2, 4.2))
    title(fig, th, 'F_min entlang φ₃ = 240° (2°-Feinsweep)',
          'Simulation, K = 10⁴ N/m, ζ ≈ 0,1 – die Höhe der Spitze hängt von K ab, ihre Lage bei 120° nicht')
    ax = fig.add_axes([0.10, 0.13, 0.86, 0.68])
    style_axes(ax, th)
    ax.grid(axis='y', color=th['grid'], linewidth=1)
    ax.set_axisbelow(True)

    ax.axhline(MG, color=th['axis'], linewidth=1)
    ax.text(141, MG, 'M·g = 6,3765 N', color=th['muted'], fontsize=8.5, va='center', ha='left')

    ax.plot(x, y, color=th['series'], linewidth=2, solid_capstyle='round', solid_joinstyle='round',
            zorder=3)
    ax.scatter(x, y, s=22, color=th['series'], edgecolors=th['surface'], linewidths=1.5, zorder=4)

    i_pk, i_end = int(np.argmax(y)), len(x) - 1
    ax.text(x[i_pk], y[i_pk] + 0.3, f'{fmt(y[i_pk], 4)} N', color=th['ink'], fontsize=9, ha='center')
    ax.text(x[0] + 1.0, y[0] - 0.45, f'{fmt(y[0], 2)} N', color=th['ink'], fontsize=9, ha='left',
            va='center')
    ax.text(x[i_end] + 1.2, y[i_end], f'{fmt(y[i_end], 2)} N', color=th['ink'], fontsize=9,
            ha='left', va='center')

    ax.set_xlim(99, 149)
    ax.set_ylim(0, 7.0)
    ax.set_xticks(range(100, 141, 10))
    ax.set_xlabel('φ₂ [°]')
    ax.set_ylabel('F_min [N]')
    ax.yaxis.set_major_formatter(comma)
    fig.savefig(path, dpi=150, facecolor=th['surface'])
    plt.close(fig)


# ── 2 · Phasenkarten ─────────────────────────────────────────────────────────
def grid_from(df, col):
    g = np.full((N_GRID, N_GRID), np.nan)
    for _, r in df.iterrows():
        i2 = int(round(r.phi2_deg / STEP)) % N_GRID
        i3 = int(round(r.phi3_deg / STEP)) % N_GRID
        g[i3, i2] = r[col]
    return g


def plot_maps(th, path):
    df = pd.read_csv(os.path.join(DATA, 'sweep_19x19.csv'))
    skew_g, lift_g = grid_from(df, 'F_skew'), grid_from(df, 'liftoff')
    edges = np.arange(N_GRID + 1) * STEP - STEP / 2   # Zellen zentriert auf den Rasterpunkten

    div = LinearSegmentedColormap.from_list('div', th['div'])
    seq = LinearSegmentedColormap.from_list('seq', th['seq'])

    fig = new_figure(th, (10.4, 5.2))
    title(fig, th, 'Phasenkarten des 19×19-Grobsweeps',
          'Simulation, K = 10⁴ N/m – im Liftoff-Bereich hängt der Wert einzelner Punkte von der '
          'Startbedingung ab; Ringe: (120°, 240°) und (240°, 120°)')
    panels = [
        ('Schiefe γ₁', skew_g, div, TwoSlopeNorm(vmin=-0.5, vcenter=0.0, vmax=2.0), [-0.5, 0, 1, 2]),
        ('Liftoff-Anteil [%]', lift_g, seq, Normalize(0, 80), [0, 20, 40, 60, 80]),
    ]
    for k, (name, g, cmap, norm, ticks) in enumerate(panels):
        ax = fig.add_axes([0.06 + k * 0.49, 0.10, 0.36, 0.72])
        style_axes(ax, th)
        m = ax.pcolormesh(edges, edges, g, cmap=cmap, norm=norm, edgecolors=th['surface'],
                          linewidth=0.5)
        for p2, p3 in [(120, 240), (240, 120)]:
            ax.scatter([p2], [p3], s=90, facecolors='none', edgecolors=th['ink'], linewidths=1.5)
        ax.set_xlim(edges[0], edges[-1])
        ax.set_ylim(edges[0], edges[-1])
        ax.set_aspect('equal')
        ax.set_xticks([0, 120, 240, 360 - STEP])
        ax.set_xticklabels(['0', '120', '240', '341'])
        ax.set_yticks([0, 120, 240, 360 - STEP])
        ax.set_yticklabels(['0', '120', '240', '341'])
        ax.set_xlabel('φ₂ [°]')
        ax.set_ylabel('φ₃ [°]')
        ax.set_title(name, color=th['ink'], fontsize=10, loc='left', pad=6)
        cax = fig.add_axes([0.06 + k * 0.49 + 0.375, 0.10, 0.012, 0.72])
        cb = fig.colorbar(m, cax=cax, ticks=ticks)
        cb.outline.set_visible(False)
        cb.ax.tick_params(colors=th['muted'], labelsize=8.5, length=0)
        cb.ax.yaxis.set_major_formatter(comma)
    fig.savefig(path, dpi=150, facecolor=th['surface'])
    plt.close(fig)


# ── 3 · Wellenformen ─────────────────────────────────────────────────────────
REGIMES = [((0.0, 0.0), 'synchron (0°, 0°)'),
           ((151.579, 265.263), 'Übergang (151,6°, 265,3°)'),
           ((120.0, 240.0), 'triphasisch (120°, 240°)')]


def compute_series():
    n = int(0.3 / finesweep.DT)
    out, series = finesweep.run([p[0][0] for p in REGIMES], [p[0][1] for p in REGIMES],
                                store_series=True, series_len=n)
    return np.arange(n) * finesweep.DT, series, out


def plot_waves(th, path, t, series, out):
    fig = new_figure(th, (7.2, 6.3))
    title(fig, th, 'Kontaktkraft N(t) über drei Anregungsperioden',
          'Simulation, K = 10⁴ N/m, 10 Hz, Ausschnitt nach 5 s Einschwingen – gleiche y-Achse in allen Feldern')
    h, top = 0.225, 0.83
    for j, (_, name) in enumerate(REGIMES):
        ax = fig.add_axes([0.10, top - (j + 1) * h - j * 0.035, 0.86, h])
        style_axes(ax, th)
        ax.grid(axis='y', color=th['grid'], linewidth=1)
        ax.set_axisbelow(True)
        ax.axhline(MG, color=th['axis'], linewidth=1)
        ax.plot(t * 1e3, series[:, j], color=th['series'], linewidth=1.6, solid_joinstyle='round')
        ax.set_xlim(0, 300)
        ax.set_ylim(0, 45)
        ax.set_yticks([0, 20, 40])
        lift = out['liftoff'][j]
        ax.text(0.99, 0.93, f'{name} · Liftoff {fmt(lift, 1)} %', transform=ax.transAxes,
                ha='right', va='top', color=th['ink'], fontsize=9)
        if j < len(REGIMES) - 1:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel('t [ms]')
        if j == 1:
            ax.set_ylabel('N [N]')
    fig.text(0.965, top + 0.005, 'Linie: M·g = 6,3765 N', color=th['muted'], fontsize=8.5, ha='right',
             va='bottom')
    fig.savefig(path, dpi=150, facecolor=th['surface'])
    plt.close(fig)


# ── 4 · Prinzipskizze ────────────────────────────────────────────────────────
SKETCH_PHASES = (0.0, 120.0, 240.0)   # Beispiel der Skizze: triphasische Konfiguration (φ₁ = 0 ist der Bezug)
SKETCH_POSE = 100.0                   # Zyklusphase [°] der links gezeichneten Stellung
SKETCH_DASHES = ['-', (0, (5, 2.2)), (0, (1.2, 1.8))]


def egg_weg(t):
    """Weg einer Modulmasse relativ zum Rahmen [m] zur Zeit t [s]: das Egg-Profil der Engine, zweifach
    integriert. finesweep.z_egg_zdd ist seine zweite Ableitung; der Nullpunkt liegt am Beginn der Haltephase.
    Oben der langsame Bogen (Halteanteil THOLD, Radius RTOP), unten der schnelle (TFAST, RBOT)."""
    u = np.mod(t, finesweep.T_CYC) / finesweep.T_CYC
    return np.where(u < finesweep.THOLD,
                    finesweep.RTOP * np.sin(np.pi * u / finesweep.THOLD),
                    -finesweep.RBOT * np.sin(np.pi * (u - finesweep.THOLD) / finesweep.TFAST))


def check_egg_weg(n=20000):
    """Gegenprobe zur Skizze: Die zweite Differenz von egg_weg muss die Profilbeschleunigung der Engine
    ergeben (außerhalb der beiden Nahtstellen des Profils). Bricht bei Abweichung ab."""
    h = finesweep.T_CYC / n
    t = (np.arange(n) + 0.5) * h
    u = t / finesweep.T_CYC
    innen = (u > 2.0 / n) & (u < 1.0 - 2.0 / n) & (np.abs(u - finesweep.THOLD) > 2.0 / n)
    d2 = (egg_weg(t + h) - 2.0 * egg_weg(t) + egg_weg(t - h)) / h**2
    a = finesweep.z_egg_zdd(t)
    err = np.abs(d2 - a)[innen].max() / np.abs(a).max()
    if not err < 1e-5:
        raise AssertionError(f'egg_weg passt nicht zu finesweep.z_egg_zdd (relative Abweichung {err:.1e})')
    return err


def sketch_weg_mm(theta_deg):
    """Weg der drei Module [mm] bei Zyklusphase theta [°] für SKETCH_PHASES; Feld (..., 3)."""
    th = np.asarray(theta_deg, float)[..., None] - np.asarray(SKETCH_PHASES)
    return 1e3 * egg_weg(th / 360.0 * finesweep.T_CYC)


def _feder(ax, x, y0, y1, color, n=4, b=0.17):
    """Zickzack-Feder von (x, y0) nach (x, y1)."""
    e = 0.14 * (y1 - y0)
    yy = np.linspace(y0 + e, y1 - e, 2 * n + 1)
    xx = x + b * np.array([0.0] + [(-1.0) ** k for k in range(2 * n - 1)] + [0.0])
    ax.plot(np.r_[x, xx, x], np.r_[y0, yy, y1], color=color, linewidth=1.3, solid_joinstyle='miter')


def _daempfer(ax, x, y0, y1, color, b=0.17):
    """Dämpfersymbol (Topf mit Kolben) von (x, y0) nach (x, y1)."""
    ym, h = 0.5 * (y0 + y1), 0.20 * (y1 - y0)
    kw = dict(color=color, linewidth=1.3, solid_capstyle='butt')
    ax.plot([x, x], [y0, ym - h], **kw)
    ax.plot([x - b, x - b, x + b, x + b], [ym + h, ym - h, ym - h, ym + h], **kw)
    ax.plot([x - 0.72 * b, x + 0.72 * b], [ym + 0.15 * h, ym + 0.15 * h], **kw)
    ax.plot([x, x], [ym + 0.15 * h, y1], **kw)


def _pfeil(ax, xy_from, xy_to, color, lw=1.8, style='-|>', scale=13):
    ax.annotate('', xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle=style, color=color, linewidth=lw, shrinkA=0, shrinkB=0,
                                mutation_scale=scale))


def plot_sketch(th, path):
    check_egg_weg()
    fig = new_figure(th, (10.4, 4.6))
    hub_mm = 1e3 * (finesweep.RTOP + finesweep.RBOT)
    p2, p3 = (fmt(p, 0) for p in SKETCH_PHASES[1:])
    title(fig, th, 'Prinzipskizze: drei Module, gleiches Profil, einstellbare Phase',
          f'Links ein Schema (nicht maßstäblich), rechts das Egg-Profil des Referenzsatzes (Hub {fmt(hub_mm, 2)} mm) '
          f'am Beispiel ({p2}°, {p3}°) – kein Simulationsergebnis')

    # links: Modell
    fig.text(0.02, 0.815, 'Modell', color=th['ink'], fontsize=10, ha='left', va='top')
    ax = fig.add_axes([0.02, 0.03, 0.43, 0.75])
    ax.set_xlim(0, 10)
    ax.set_ylim(0.2, 8.6)
    ax.set_aspect('equal')
    ax.axis('off')
    line = th['ink2']

    y_g, y_f0, y_f1 = 1.2, 2.6, 8.3                       # Unterlage, Rahmen unten, Rahmen oben
    ax.plot([0.8, 9.2], [y_g, y_g], color=th['ink'], linewidth=1.6)
    for xi in np.arange(1.0, 9.21, 0.41):
        ax.plot([xi, xi - 0.28], [y_g, y_g - 0.32], color=th['muted'], linewidth=1)
    ax.text(9.2, y_g - 0.5, 'Unterlage', color=th['muted'], fontsize=8.5, ha='right', va='top')

    ax.add_patch(Rectangle((1.3, y_f0), 7.4, y_f1 - y_f0, facecolor=th['mid'], edgecolor=th['ink'],
                           linewidth=1.6, joinstyle='round'))
    ax.text(1.5, y_f1 - 0.18, 'Körper', color=th['ink2'], fontsize=9, ha='left', va='top')

    y_p = y_g + 0.07                                      # Fußplatte: liegt auf, ist nicht befestigt
    ax.plot([4.15, 5.85], [y_p, y_p], color=line, linewidth=2.2, solid_capstyle='butt')
    _feder(ax, 4.55, y_p, y_f0, line)
    _daempfer(ax, 5.45, y_p, y_f0, line)
    ax.text(6.1, 0.5 * (y_g + y_f0), 'Kontakt K, C\neinseitig: nur Druck', color=th['ink2'], fontsize=8.5,
            ha='left', va='center', linespacing=1.35)
    _pfeil(ax, (3.55, y_g + 0.04), (3.55, y_f0 - 0.06), th['series'], lw=2.2, scale=15)
    ax.text(3.37, 0.5 * (y_g + y_f0), 'N(t)', color=th['ink'], fontsize=10, fontweight='bold',
            ha='right', va='center')

    _pfeil(ax, (5.0, 3.85), (5.0, y_f0 + 0.12), line)
    ax.text(5.22, 3.3, 'M·g', color=th['ink'], fontsize=9.5, ha='left', va='center')

    w = sketch_weg_mm(SKETCH_POSE)
    names = [('Modul 1', 'Bezug'), ('Modul 2', 'φ₂'), ('Modul 3', 'φ₃')]
    for k, xc in enumerate((2.75, 5.0, 7.25)):
        ax.plot([xc, xc], [5.0, 7.75], color=th['muted'], linewidth=1)   # Führung
        yc = 6.2 + 0.16 * w[k]
        ax.add_patch(Rectangle((xc - 0.62, yc - 0.4), 1.24, 0.8, facecolor=th['series'],
                               edgecolor=th['surface'], linewidth=1, zorder=3))
        ax.text(xc, yc, str(k + 1), color='#ffffff', fontsize=10, fontweight='bold', ha='center',
                va='center', zorder=4)
        _pfeil(ax, (xc + 0.9, 5.55), (xc + 0.9, 7.15), line, lw=1, style='<|-|>', scale=9)
        ax.text(xc, 4.72, names[k][0], color=th['ink'], fontsize=8.5, ha='center', va='top')
        ax.text(xc, 4.3, names[k][1], color=th['ink2'], fontsize=8.5, ha='center', va='top')

    # rechts: Bewegungsprofil
    fig.text(0.535, 0.815, 'Bewegungsprofil der Module: Weg relativ zum Körper', color=th['ink'],
             fontsize=10, ha='left', va='top')
    ax = fig.add_axes([0.535, 0.15, 0.435, 0.53])
    style_axes(ax, th)
    ax.grid(axis='y', color=th['grid'], linewidth=1)
    ax.set_axisbelow(True)
    ax.axhline(0.0, color=th['axis'], linewidth=1)
    theta = np.linspace(0.0, 360.0, 1441)
    curves = sketch_weg_mm(theta)
    labels = ['Modul 1', f'Modul 2 (φ₂ = {p2}°)', f'Modul 3 (φ₃ = {p3}°)']
    for k in range(3):
        ax.plot(theta, curves[:, k], color=th['series'], linewidth=2, linestyle=SKETCH_DASHES[k],
                label=labels[k], zorder=3)
    ax.plot([SKETCH_POSE, SKETCH_POSE], [-3.05, 5.75], color=th['muted'], linewidth=1,
            linestyle=(0, (1, 2.5)), zorder=2)
    ax.scatter([SKETCH_POSE] * 3, w, s=26, color=th['series'], edgecolors=th['surface'], linewidths=1.5,
               zorder=4)
    ax.text(SKETCH_POSE + 4, 5.78, 'Stellung links', color=th['muted'], fontsize=8, ha='left', va='center')

    hold = 360.0 * finesweep.THOLD
    for x0, x1, txt in [(0.0, hold, f'Modul 1: Haltephase {fmt(100 * finesweep.THOLD, 0)} %'),
                        (hold, 360.0, f'schnelle Phase {fmt(100 * finesweep.TFAST, 0)} %')]:
        ax.plot([x0 + 1.5, x1 - 1.5], [-3.6, -3.6], color=th['muted'], linewidth=1)
        for xe in (x0 + 1.5, x1 - 1.5):
            ax.plot([xe, xe], [-3.78, -3.42], color=th['muted'], linewidth=1)
        ax.text(0.5 * (x0 + x1), -4.0, txt, color=th['ink2'], fontsize=8, ha='center', va='top')

    ax.set_xlim(0, 360)
    ax.set_ylim(-4.9, 6.3)
    ax.set_xticks([0, 120, 240, 360])
    ax.set_yticks([-1e3 * finesweep.RBOT, 0.0, 1e3 * finesweep.RTOP])
    ax.set_yticklabels([fmt(-1e3 * finesweep.RBOT, 2), '0', fmt(1e3 * finesweep.RTOP, 0)])
    ax.set_xlabel('Zyklusphase [°]')
    ax.set_ylabel('Weg [mm]')
    leg = ax.legend(loc='lower left', bbox_to_anchor=(-0.01, 1.0), ncol=3, frameon=False, fontsize=8.5,
                    handlelength=2.6, columnspacing=1.4, borderaxespad=0.2)
    for txt in leg.get_texts():
        txt.set_color(th['ink2'])
    fig.savefig(path, dpi=150, facecolor=th['surface'])
    plt.close(fig)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t, series, out = compute_series()
    for mode, th in THEMES.items():
        plot_tent(th, os.path.join(OUT, f'zeltkurve_{mode}.png'))
        plot_maps(th, os.path.join(OUT, f'phasenkarten_{mode}.png'))
        plot_waves(th, os.path.join(OUT, f'wellenformen_{mode}.png'), t, series, out)
        plot_sketch(th, os.path.join(OUT, f'prinzipskizze_{mode}.png'))
    print('Abbildungen geschrieben nach', os.path.normpath(OUT))
