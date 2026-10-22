#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCMMS Ballon — Drift-Auswertung
================================
Misst die ZIELGROESSE des Experiments: die vertikale NETTO-DRIFT eines
auftriebskompensierten Ballons (Steigung der Hoehe ueber Zeit) und prueft, ob
sich die festen Phasen-Bedingungen von den Kontrollen (Vibration aus / zufaellige
Phase) unterscheiden — UEBER der Eigendrift und der Run-zu-Run-Streuung.

Ehrliche Linie (wie im PCMMS-Framework):
  * gemessen wird die Drift, NICHT eine Kraft;
  * eine Phase zaehlt nur, wenn ihr Drift-Mittel die Run-zu-Run-Streuung der
    Kontrollen klar uebersteigt UND ueber viele Runs reproduzierbar ist;
  * ein Null-Ergebnis ist ein vollwertiges, dokumentiertes Resultat.

DATENFORMAT
-----------
Eine CSV pro Run, zwei Spalten mit Kopfzeile:
    t_s,h_m
    0.0,1.024
    0.5,1.025
    ...
  t_s = Zeit in Sekunden, h_m = Hoehe in Metern (Drift wird in mm/s berichtet).

ORDNERSTRUKTUR (--data DIR)
---------------------------
  DIR/off/*.csv          <- Kontrolle: Vibration aus
  DIR/random/*.csv       <- Kontrolle: zufaellige Phase
  DIR/phase_090/*.csv    <- Messbedingung
  DIR/phase_270/*.csv    <- Messbedingung
Der Ordnername ist der Bedingungsname. Bedingungen in --controls gelten als
Kontrollen, alle anderen als aktive Phasen.

BENUTZUNG
---------
  python3 pcmms_drift_analyse.py --data ./messdaten
  python3 pcmms_drift_analyse.py --demo            # synthetische Demo-Daten
Optionen: --out plot.png  --target 1.0 (mm/s Zielgroesse)  --controls off,random  --robust
"""

import argparse, os, sys, glob, tempfile
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy import stats as _scipy_stats
except Exception:
    _scipy_stats = None


# --------------------------------------------------------------------------- #
#  Laden & Fit
# --------------------------------------------------------------------------- #
def load_run_csv(path):
    """Liest (t_s, h_m). Akzeptiert Kopfzeile 't_s,h_m' oder zwei Zahlenspalten."""
    try:
        d = np.genfromtxt(path, delimiter=",", names=True)
        if d.dtype.names and "t_s" in d.dtype.names and "h_m" in d.dtype.names:
            t = np.asarray(d["t_s"], float); h = np.asarray(d["h_m"], float)
        else:
            raise ValueError
    except Exception:
        d = np.genfromtxt(path, delimiter=",", skip_header=0)
        d = np.atleast_2d(d)
        # falls erste Zeile Text war -> NaN -> entfernen
        if np.isnan(d[0]).any():
            d = d[1:]
        t = d[:, 0].astype(float); h = d[:, 1].astype(float)
    m = np.isfinite(t) & np.isfinite(h)
    return t[m], h[m]


def drift_ols(t, h):
    """OLS-Steigung b (Drift) und Standardfehler. Rueckgabe in m/s."""
    n = len(t)
    if n < 3:
        return np.nan, np.nan
    tm = t.mean()
    Stt = np.sum((t - tm) ** 2)
    if Stt <= 0:
        return np.nan, np.nan
    b = np.sum((t - tm) * (h - h.mean())) / Stt
    a = h.mean() - b * tm
    resid = h - (a + b * t)
    s2 = np.sum(resid ** 2) / (n - 2)
    se = np.sqrt(s2 / Stt)
    return b, se


def drift_theilsen(t, h):
    """Robuste Steigung (Theil-Sen), unempfindlicher gegen Boeen/Ausreisser. m/s."""
    if _scipy_stats is not None:
        b, _, lo, hi = _scipy_stats.theilslopes(h, t)
        se = (hi - lo) / (2 * 1.96)  # grobe SE aus 95%-Intervall
        return b, se
    # Fallback: Median aller paarweisen Steigungen (kleine n)
    sl = []
    for i in range(len(t)):
        for j in range(i + 1, len(t)):
            if t[j] != t[i]:
                sl.append((h[j] - h[i]) / (t[j] - t[i]))
    sl = np.array(sl)
    return (np.median(sl), np.std(sl) / np.sqrt(max(len(sl), 1))) if len(sl) else (np.nan, np.nan)


# --------------------------------------------------------------------------- #
#  Bedingungen einsammeln
# --------------------------------------------------------------------------- #
def collect(data_dir, robust=False):
    """-> dict: bedingung -> list von (drift_m_s, se_m_s) je Run."""
    out = {}
    subs = sorted(d for d in os.listdir(data_dir)
                  if os.path.isdir(os.path.join(data_dir, d)))
    for cond in subs:
        files = sorted(glob.glob(os.path.join(data_dir, cond, "*.csv")))
        runs = []
        for f in files:
            t, h = load_run_csv(f)
            b, se = (drift_theilsen if robust else drift_ols)(t, h)
            if np.isfinite(b):
                runs.append((b, se))
        if runs:
            out[cond] = runs
    return out


def summarize(runs):
    """Mittelwert/SD/SE der Drift ueber die Runs einer Bedingung (m/s)."""
    b = np.array([r[0] for r in runs], float)
    n = len(b)
    mean = b.mean()
    sd = b.std(ddof=1) if n >= 2 else 0.0
    se = sd / np.sqrt(n) if n >= 2 else (runs[0][1] if np.isfinite(runs[0][1]) else 0.0)
    return dict(n=n, mean=mean, sd=sd, se=se, vals=b)


# --------------------------------------------------------------------------- #
#  Analyse + Verdikt
# --------------------------------------------------------------------------- #
def analyse(conds, controls, target_mm_s, ksigma=2.0):
    MM = 1000.0  # m/s -> mm/s
    ctrl_names = [c for c in conds if c in controls]
    act_names = [c for c in conds if c not in controls]

    print("=" * 74)
    print("PCMMS — DRIFT-AUSWERTUNG")
    print("=" * 74)
    if not ctrl_names:
        print("WARNUNG: keine Kontroll-Bedingungen gefunden "
              "(erwartet z. B. 'off', 'random'). Verdikt ohne Rauschboden.")
    # Pool der Kontroll-Runs = Rausch-/Eigendrift-Boden
    ctrl_vals = np.concatenate([summarize(conds[c])["vals"] for c in ctrl_names]) \
        if ctrl_names else np.array([])
    ctrl_mean = ctrl_vals.mean() if ctrl_vals.size else 0.0
    ctrl_sd = ctrl_vals.std(ddof=1) if ctrl_vals.size >= 2 else 0.0

    print("\nBedingungen (Drift = Steigung Hoehe/Zeit, in mm/s):")
    print(f"{'Bedingung':<14}{'n':>3}{'Drift':>11}{'± SE':>9}{'Streuung SD':>13}   Typ")
    print("-" * 74)
    summ = {}
    for c in conds:
        s = summarize(conds[c]); summ[c] = s
        typ = "Kontrolle" if c in controls else "aktiv"
        print(f"{c:<14}{s['n']:>3}{s['mean']*MM:>11.3f}{s['se']*MM:>9.3f}"
              f"{s['sd']*MM:>13.3f}   {typ}")

    print("-" * 74)
    print(f"Kontroll-Pool: Mittel {ctrl_mean*MM:+.3f} mm/s "
          f"(ideal ~0), Run-zu-Run-Streuung SD = {ctrl_sd*MM:.3f} mm/s, "
          f"n = {ctrl_vals.size}")
    print(f"Nachweis-Schwelle (Rauschboden): |Drift - Kontrolle| > "
          f"{ksigma:.0f}·SD = {ksigma*ctrl_sd*MM:.3f} mm/s\n")

    # Pro aktive Bedingung bewerten
    print("VERDIKT je aktiver Phase:")
    print("-" * 74)
    any_detect = False
    for c in act_names:
        s = summ[c]
        diff = s["mean"] - ctrl_mean
        comb_se = np.sqrt(s["se"] ** 2 + (ctrl_sd / np.sqrt(max(ctrl_vals.size, 1))) ** 2)
        clears = (ctrl_sd > 0) and (abs(diff) > ksigma * ctrl_sd)
        z = diff / comb_se if comb_se > 0 else float("nan")
        # optionaler Welch-Test
        p_txt = ""
        if _scipy_stats is not None and ctrl_vals.size >= 2 and s["n"] >= 2:
            tstat, p = _scipy_stats.ttest_ind(s["vals"], ctrl_vals, equal_var=False)
            p_txt = f", Welch p = {p:.3f}"
        verdict = "UNTERSCHIED ggue. Kontrolle" if clears else "NICHT vom Rauschen trennbar"
        if clears:
            any_detect = True
        print(f"  {c:<12}  Δ = {diff*MM:+.3f} mm/s "
              f"({abs(diff)/ctrl_sd:.1f}·SD)" if ctrl_sd > 0 else
              f"  {c:<12}  Δ = {diff*MM:+.3f} mm/s")
        print(f"               z ≈ {z:+.2f}{p_txt}  ->  {verdict}")
    if not act_names:
        print("  (keine aktiven Phasen-Bedingungen gefunden)")

    # Power / Planung (zwei-Gruppen, alpha=0.05 zweiseitig, Power 0.80)
    print("\n" + "-" * 74)
    z_a, z_b = 1.95996, 0.84162
    if ctrl_sd > 0:
        delta = target_mm_s / 1000.0
        n_grp = 2.0 * (z_a + z_b) ** 2 * (ctrl_sd ** 2) / (delta ** 2)
        print(f"Planung: um eine Drift von {target_mm_s:.2f} mm/s sicher zu trennen, "
              f"braucht es")
        print(f"         ~{int(np.ceil(n_grp))} Runs je Gruppe "
              f"(zwei-Gruppen, Power 0,80) bei der aktuellen Streuung.")
    else:
        print("Planung: zu wenige Kontroll-Runs fuer eine Streuungs-/Power-Abschaetzung.")

    print("\n" + "=" * 74)
    if any_detect:
        print("ERGEBNIS: Mindestens eine Phase hebt sich vom Rausch-/Eigendrift-Boden ab.")
        print("          -> als Kandidat dokumentieren, mit mehr Runs absichern (Multi-")
        print("             vergleich: Schwelle pro Phase strenger setzen, z. B. 3·SD).")
    else:
        print("ERGEBNIS: Keine Phase ueberschreitet den Rausch-/Eigendrift-Boden.")
        print("          -> Null-Ergebnis. Vollwertig und dokumentationswuerdig:")
        print("             bei dieser Streuung war ein groesserer Effekt nicht vorhanden.")
    print("=" * 74)

    return summ, ctrl_mean, ctrl_sd, ctrl_names, act_names


# --------------------------------------------------------------------------- #
#  Plots
# --------------------------------------------------------------------------- #
def make_plots(data_dir, conds, summ, ctrl_mean, ctrl_sd, controls, out_png, demo=False):
    MM = 1000.0
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.0, 8.6),
                                   gridspec_kw=dict(height_ratios=[1.15, 1.0]))
    cmap = plt.get_cmap("tab10")
    color = {c: cmap(i % 10) for i, c in enumerate(conds)}

    # (1) Hoehe ueber Zeit, alle Runs
    seen = set()
    for c in conds:
        files = sorted(glob.glob(os.path.join(data_dir, c, "*.csv")))
        for f in files:
            t, h = load_run_csv(f)
            if len(t) < 2:
                continue
            lbl = c if c not in seen else None
            seen.add(c)
            ax1.plot(t, (h - h[0]) * 100.0, color=color[c], lw=1.0, alpha=0.8, label=lbl)
    ax1.set_xlabel("Zeit  t  [s]")
    ax1.set_ylabel("relative Hoehe  Δh  [cm]")
    ax1.set_title("Hoehenverlauf je Run" + ("  (synthetische Demo-Daten)" if demo else ""))
    ax1.grid(True, alpha=0.25)
    ax1.legend(fontsize=8, ncol=2, frameon=False)

    # (2) Drift je Bedingung mit Fehlerbalken + Kontrollband
    names = list(conds.keys())
    xs = np.arange(len(names))
    means = np.array([summ[c]["mean"] for c in names]) * MM
    ses = np.array([summ[c]["se"] for c in names]) * MM
    cols = [("#444444" if c in controls else color[c]) for c in names]

    if ctrl_sd > 0:
        ax2.axhspan((ctrl_mean - 2 * ctrl_sd) * MM, (ctrl_mean + 2 * ctrl_sd) * MM,
                    color="#888888", alpha=0.15, label="Kontrolle ±2·SD")
    ax2.axhline(ctrl_mean * MM, color="#888888", lw=1.0, ls="--", label="Kontroll-Mittel")
    ax2.axhline(0.0, color="k", lw=0.6, alpha=0.5)
    for x, m, e, col in zip(xs, means, ses, cols):
        ax2.errorbar(x, m, yerr=e, fmt="o", color=col, capsize=4, ms=7)
    ax2.set_xticks(xs); ax2.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
    ax2.set_ylabel("Netto-Drift  [mm/s]")
    ax2.set_title("Drift je Bedingung (Mittel ± SE) gegen den Kontrollband")
    ax2.grid(True, axis="y", alpha=0.25)
    ax2.legend(fontsize=8, frameon=False)

    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    print(f"\nPlot gespeichert: {out_png}")


# --------------------------------------------------------------------------- #
#  Demo-Daten (synthetisch)
# --------------------------------------------------------------------------- #
def make_demo(dirpath, seed=42):
    """Erzeugt synthetische Hoehen-Logs. NUR Illustration der Methode!"""
    rng = np.random.default_rng(seed)
    T, dt = 120.0, 0.5            # 120 s, 2 Hz Abtastung
    t = np.arange(0, T, dt)
    n_runs = 6
    sigma_env = 0.6e-3            # Eigendrift-Streuung (m/s) ~ Luftstroemungen
    meas_noise = 1.0e-3           # Mess-Rauschen je Sample (m) ~ VL53L1X
    true = {                      # "wahre" Drift je Bedingung (m/s)
        "off":       0.0,
        "random":    0.0,
        "phase_090": +1.5e-3,
        "phase_270": -1.2e-3,
    }
    for cond, td in true.items():
        os.makedirs(os.path.join(dirpath, cond), exist_ok=True)
        for r in range(n_runs):
            env_drift = rng.normal(0, sigma_env)        # zufaellige Eigendrift je Run
            slope = td + env_drift
            h0 = 1.0 + rng.normal(0, 0.02)
            h = h0 + slope * t + rng.normal(0, meas_noise, size=t.size)
            arr = np.column_stack([t, h])
            np.savetxt(os.path.join(dirpath, cond, f"run{r+1}.csv"),
                       arr, delimiter=",", header="t_s,h_m", comments="", fmt="%.4f")
    return list(true.keys())


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="PCMMS Ballon — Drift-Auswertung")
    ap.add_argument("--data", help="Ordner mit Unterordnern je Bedingung")
    ap.add_argument("--demo", action="store_true", help="synthetische Demo-Daten verwenden")
    ap.add_argument("--out", default="drift_auswertung.png", help="Plot-Dateiname (PNG)")
    ap.add_argument("--target", type=float, default=1.0, help="Zielgroesse in mm/s (Power)")
    ap.add_argument("--controls", default="off,random", help="Kontroll-Bedingungen, kommagetrennt")
    ap.add_argument("--robust", action="store_true", help="robuste Steigung (Theil-Sen)")
    args = ap.parse_args()

    controls = set(s.strip() for s in args.controls.split(",") if s.strip())

    if args.demo:
        data_dir = tempfile.mkdtemp(prefix="pcmms_demo_")
        make_demo(data_dir)
        print(f"[DEMO] synthetische Daten in {data_dir}")
        print("[DEMO] ACHTUNG: kein reales Ergebnis — nur zur Veranschaulichung.\n")
    elif args.data:
        data_dir = args.data
    else:
        print("Bitte --data DIR angeben oder --demo verwenden. (-h fuer Hilfe)")
        sys.exit(1)

    conds = collect(data_dir, robust=args.robust)
    if not conds:
        print("Keine CSV-Daten gefunden. Erwartet: DIR/<bedingung>/*.csv")
        sys.exit(1)

    summ, cmean, csd, cnames, anames = analyse(conds, controls, args.target)
    make_plots(data_dir, conds, summ, cmean, csd, controls, args.out, demo=args.demo)


if __name__ == "__main__":
    main()
