"""
plot_figures.py – Abbildungen für README und docs aus den Simulationsdaten in data/.

Erzeugt in docs/figures/ je eine helle und eine dunkle Fassung:
  zeltkurve_{light,dark}.png     F_min entlang φ₃ = 240° aus finesweep_2deg_120_240.csv
  phasenkarten_{light,dark}.png  Schiefe und Liftoff-Anteil aus sweep_19x19.csv
  wellenformen_{light,dark}.png  N(t) über drei Perioden für drei Phasenlagen
                                 (gerechnet mit finesweep.run, ca. 30 s)

Aufruf (aus beliebigem Verzeichnis):  python3 code/plot_figures.py
Alle Abbildungen zeigen Simulationsausgaben, keine Messdaten.

Matthias Früh · PCMMS · September 2026
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, Normalize
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


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t, series, out = compute_series()
    for mode, th in THEMES.items():
        plot_tent(th, os.path.join(OUT, f'zeltkurve_{mode}.png'))
        plot_maps(th, os.path.join(OUT, f'phasenkarten_{mode}.png'))
        plot_waves(th, os.path.join(OUT, f'wellenformen_{mode}.png'), t, series, out)
    print('Abbildungen geschrieben nach', os.path.normpath(OUT))
