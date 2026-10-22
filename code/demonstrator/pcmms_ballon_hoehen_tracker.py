#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCMMS Ballon — Video-Hoehen-Tracker
===================================
Verfolgt einen farbigen Ballon (oder Marker am Ballon) in einem Video und
schreibt die VERTIKALE HOEHE ueber Zeit als CSV — im exakten Format, das
`pcmms_drift_analyse.py` erwartet:

    t_s,h_m
    0.000,0.0123
    0.033,0.0125
    ...

Damit schliesst sich die Kette:  Video -> Hoehen-CSV -> Drift-Auswertung.

EHRLICHE LINIE (wie im PCMMS-Framework)
---------------------------------------
* Gemessen wird eine HOEHE, daraus die Drift (Steigung) — keine Kraft.
* Die Drift-Auswertung nutzt Theil-Sen / OLS und braucht nur die STEIGUNG.
  Folglich ist der Hoehen-Nullpunkt belanglos; entscheidend sind allein
  (a) der Massstab Meter/Pixel und (b) das Vorzeichen (hoch = groesser h).
* Ein Null-Ergebnis (keine Drift ueber der Kontroll-Streuung) ist ein
  vollwertiges, dokumentiertes Resultat.

ACHSENKONVENTION
----------------
Bildkoordinaten zaehlen y von OBEN nach UNTEN. Hoehe zaehlt nach OBEN.
Deshalb:  h_px_aufwaerts = (Bildhoehe - y_pixel);  h_m = h_px_aufwaerts * mpp
Steigt der Ballon (y_pixel sinkt), waechst h. Korrekt.

KALIBRIERUNG (drei Wege — einer reicht)
---------------------------------------
1) --balloon-diam-m D   EINFACHSTE: aus dem bekannten Ballon-DURCHMESSER.
                        mpp wird automatisch aus dem Median-Radius der
                        Detektion bestimmt:  mpp = D / (2 * median_radius_px).
                        Kein Pixelmessen noetig.
2) --ref-meters M --ref-pixels P
                        Referenzobjekt bekannter Laenge: mpp = M / P.
                        P misst man einmalig in einem beliebigen Foto-Viewer
                        an einem Standbild (siehe --info).
3) --mpp X              Massstab direkt in Meter pro Pixel.

FARBE
-----
--color {red,orange,yellow,green,cyan,blue,magenta}   (Default: red)
oder eigener HSV-Bereich:  --hsv-lower H,S,V --hsv-upper H,S,V
(OpenCV-HSV: H 0..180, S/V 0..255). Rot nutzt automatisch zwei Bereiche.

PYDROID3 / HEADLESS
-------------------
Kein cv2.imshow noetig. Optionale Kontrolle:
  --info            Standbilder + Bildmasse ausgeben (zum Kalibrieren), dann Ende.
  --preview OUT.mp4 annotiertes Video schreiben (Kreis + Hoehe), ohne Fenster.

BENUTZUNG
---------
  python3 pcmms_ballon_hoehen_tracker.py video.mp4 --balloon-diam-m 0.30
  python3 pcmms_ballon_hoehen_tracker.py video.mp4 --ref-meters 0.50 --ref-pixels 412
  python3 pcmms_ballon_hoehen_tracker.py video.mp4 --mpp 0.00121 --color green
  python3 pcmms_ballon_hoehen_tracker.py video.mp4 --info

Optionen (Auszug):
  --out CSV          Ausgabedatei (Default: <video>_hoehe.csv)
  --debug-csv CSV    Zusatz-CSV mit frame,t_s,x_px,y_px,radius_px,detektiert
  --smooth N         Median-Glaettungsfenster in Frames (ungerade; Default 5)
  --min-radius R     Mindest-Radius einer gueltigen Detektion in px (Default 4)
  --max-speed V      Ausreisser-Grenze in px/s (Default 4000); groessere
                     Spruenge zwischen Frames werden verworfen
  --use-msec / --no-msec   Zeit aus Container-Zeitstempeln (gut bei
                     schwankender Bildrate von Handyvideos) statt frame/fps.
                     Default: msec, falls plausibel/monoton, sonst frame/fps.
"""

import argparse
import os
import sys
import csv

import numpy as np

try:
    import cv2
except ImportError:
    sys.exit("Fehler: OpenCV fehlt.  Installation:  pip install opencv-python-headless")


# ----------------------------------------------------------------------------
# Farb-Presets (OpenCV-HSV: H 0..180, S/V 0..255). Jeder Eintrag ist eine Liste
# von (lower, upper)-Paaren; Rot braucht zwei wegen Hue-Umlauf bei 0/180.
# ----------------------------------------------------------------------------
COLOR_PRESETS = {
    "red":     [((0, 120, 70),  (10, 255, 255)),
                ((170, 120, 70), (180, 255, 255))],
    "orange":  [((8, 120, 70),  (22, 255, 255))],
    "yellow":  [((22, 100, 70), (38, 255, 255))],
    "green":   [((38, 80, 60),  (85, 255, 255))],
    "cyan":    [((85, 80, 60),  (100, 255, 255))],
    "blue":    [((100, 100, 60), (130, 255, 255))],
    "magenta": [((140, 80, 70), (170, 255, 255))],
}


def _triple(s):
    """'H,S,V' -> (H,S,V) als ints."""
    parts = [int(round(float(x))) for x in s.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Bitte drei Werte: H,S,V")
    return tuple(parts)


def build_ranges(args):
    """Liefert die Liste der (lower,upper)-HSV-Paare als np.uint8-Arrays."""
    if args.hsv_lower is not None and args.hsv_upper is not None:
        pairs = [(args.hsv_lower, args.hsv_upper)]
    else:
        pairs = COLOR_PRESETS[args.color]
    return [(np.array(lo, np.uint8), np.array(hi, np.uint8)) for lo, hi in pairs]


def detect(frame_bgr, ranges, min_radius):
    """
    Groesste farbige Kontur im Frame finden.
    Rueckgabe: (x, y, radius) in Pixeln oder None.
    """
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = None
    for lo, hi in ranges:
        m = cv2.inRange(hsv, lo, hi)
        mask = m if mask is None else (mask | m)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    (x, y), radius = cv2.minEnclosingCircle(c)
    if radius < min_radius:
        return None
    return float(x), float(y), float(radius)


def rolling_median(a, w):
    """Zentrierte Median-Glaettung, randerhaltend. w wird auf ungerade gezwungen."""
    a = np.asarray(a, float)
    if w is None or w <= 1 or a.size == 0:
        return a
    if w % 2 == 0:
        w += 1
    pad = w // 2
    ap = np.pad(a, pad, mode="edge")
    out = np.empty_like(a)
    for i in range(a.size):
        out[i] = np.median(ap[i:i + w])
    return out


def info_mode(video_path):
    """Bildmasse + Standbilder (erstes / mittleres Frame) zum Kalibrieren ausgeben."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        sys.exit(f"Fehler: Video {video_path} nicht zu oeffnen.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    print(f"Video      : {video_path}")
    print(f"Bildrate   : {fps:.3f} FPS")
    print(f"Frames     : {n}")
    print(f"Aufloesung : {w} x {h}  (Breite x Hoehe, Pixel)")
    if n > 0 and fps > 0:
        print(f"Dauer      : {n / fps:.2f} s")

    base = os.path.splitext(os.path.basename(video_path))[0]
    saved = []
    for tag, idx in (("first", 0), ("mid", max(0, n // 2))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, fr = cap.read()
        if ok:
            outp = f"{base}_frame_{tag}.png"
            cv2.imwrite(outp, fr)
            saved.append(outp)
    cap.release()
    if saved:
        print("Standbilder:", ", ".join(saved))
        print("Tipp: in einem Foto-Viewer die Pixel-Laenge eines bekannten")
        print("      Objekts ausmessen -> --ref-pixels P  (mit --ref-meters M).")


def track(args):
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        sys.exit(f"Fehler: Video {args.video} nicht zu oeffnen.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    H_img = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if H_img == 0:
        # Fallback: aus erstem Frame bestimmen
        ok, fr = cap.read()
        if not ok:
            sys.exit("Fehler: kein Frame lesbar.")
        H_img = fr.shape[0]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    ranges = build_ranges(args)

    # --- Pass 1: pro Frame detektieren, Rohdaten sammeln -------------------
    frames, t_frame, t_msec, ys, xs, radii = [], [], [], [], [], []
    idx = 0
    n_det = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        d = detect(fr, ranges, args.min_radius)
        if d is not None:
            x, y, r = d
            frames.append(idx)
            t_frame.append(idx / fps if fps > 0 else float(idx))
            t_msec.append(msec / 1000.0 if msec and msec > 0 else np.nan)
            xs.append(x); ys.append(y); radii.append(r)
            n_det += 1
        idx += 1
    cap.release()

    if n_det == 0:
        sys.exit("Keine Detektion. Farbe/--min-radius pruefen (oder --info nutzen).")

    frames = np.array(frames)
    t_frame = np.array(t_frame, float)
    t_msec = np.array(t_msec, float)
    xs = np.array(xs, float); ys = np.array(ys, float); radii = np.array(radii, float)

    # --- Zeitbasis waehlen --------------------------------------------------
    use_msec = args.use_msec
    msec_ok = bool(np.all(np.isfinite(t_msec))) and bool(np.all(np.diff(t_msec) >= -1e-6))
    why = ""
    if args.use_msec is None:
        use_msec = msec_ok
        why = "Container-Zeitstempel" if use_msec else "frame/fps"
    else:
        why = "Container-Zeitstempel (erzwungen)" if use_msec else "frame/fps (erzwungen)"
        if use_msec and not np.all(np.isfinite(t_msec)):
            print("Warnung: msec unvollstaendig -> fuelle Luecken aus frame/fps.")
            t_msec = np.where(np.isfinite(t_msec), t_msec, t_frame)
    t = t_msec if use_msec else t_frame
    t = t - t[0]  # auf Null beginnen lassen (Nullpunkt egal fuer Drift)

    # --- Ausreisser verwerfen (zu schnelle Vertikalspruenge) ---------------
    keep = np.ones(t.size, bool)
    if args.max_speed and args.max_speed > 0 and t.size > 1:
        for i in range(1, t.size):
            dt = t[i] - t[i - 1]
            if dt > 0 and abs(ys[i] - ys[i - 1]) / dt > args.max_speed:
                keep[i] = False
    t, ys, xs, radii, frames = t[keep], ys[keep], xs[keep], radii[keep], frames[keep]
    n_drop = int((~keep).sum())

    # --- Massstab mpp bestimmen --------------------------------------------
    med_r = float(np.median(radii)) if radii.size else 0.0
    if args.balloon_diam_m is not None:
        if med_r <= 0:
            sys.exit("Median-Radius 0 — Durchmesser-Kalibrierung nicht moeglich.")
        mpp = args.balloon_diam_m / (2.0 * med_r)
        cal = f"Ballon-Durchmesser {args.balloon_diam_m:.3f} m / (2*{med_r:.1f}px Median)"
    elif args.ref_meters is not None and args.ref_pixels is not None:
        if args.ref_pixels <= 0:
            sys.exit("--ref-pixels muss > 0 sein.")
        mpp = args.ref_meters / args.ref_pixels
        cal = f"Referenz {args.ref_meters:.3f} m / {args.ref_pixels:.1f} px"
    elif args.mpp is not None:
        mpp = args.mpp
        cal = "direkt vorgegeben"
    else:
        sys.exit("Keine Kalibrierung. Einen Weg waehlen: "
                 "--balloon-diam-m | (--ref-meters & --ref-pixels) | --mpp")

    # --- Glaetten (Median) und Achsenspiegelung -> Hoehe in Meter ----------
    ys_s = rolling_median(ys, args.smooth)
    h_m = (H_img - ys_s) * mpp   # nach OBEN positiv

    # --- Hauptausgabe: t_s,h_m (exakt drift_analyse-Format) ----------------
    out = args.out or (os.path.splitext(args.video)[0] + "_hoehe.csv")
    with open(out, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["t_s", "h_m"])
        for ti, hi in zip(t, h_m):
            wr.writerow([f"{ti:.3f}", f"{hi:.5f}"])

    # --- optionale Debug-CSV ------------------------------------------------
    if args.debug_csv:
        with open(args.debug_csv, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["frame", "t_s", "x_px", "y_px", "y_px_smooth", "radius_px"])
            for fr_, ti, xi, yi, yis, ri in zip(frames, t, xs, ys, ys_s, radii):
                wr.writerow([int(fr_), f"{ti:.3f}", f"{xi:.2f}", f"{yi:.2f}",
                             f"{yis:.2f}", f"{ri:.2f}"])

    # --- optionales annotiertes Vorschau-Video (headless) ------------------
    if args.preview:
        _write_preview(args, ranges, mpp, H_img)

    # --- Bericht ------------------------------------------------------------
    span = (t[-1] - t[0]) if t.size > 1 else 0.0
    print("Tracking abgeschlossen.")
    print(f"  Detektionen     : {n_det}  (Ausreisser verworfen: {n_drop})")
    print(f"  Zeitbasis       : {why}")
    print(f"  Massstab (mpp)  : {mpp:.6g} m/px   [{cal}]")
    if med_r > 0:
        print(f"  Ballon ~        : {2*med_r*mpp*100:.1f} cm scheinbarer Durchmesser")
    print(f"  Hoehenspanne    : {np.nanmax(h_m)-np.nanmin(h_m):.3f} m ueber {span:.2f} s")
    print(f"  CSV             : {out}")
    if args.debug_csv:
        print(f"  Debug-CSV       : {args.debug_csv}")
    print("\nWeiter:  python3 pcmms_drift_analyse.py --data <ORDNER>")
    print("  (CSV in off/ random/ phase_xxx/ einsortieren — pro Run eine Datei.)")


def _write_preview(args, ranges, mpp, H_img):
    """Annotiertes Video schreiben (Kreis + Hoehe), ohne Fenster."""
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(args.preview, fourcc, fps if fps > 0 else 25.0, (w, h))
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        d = detect(fr, ranges, args.min_radius)
        if d is not None:
            x, y, r = d
            cv2.circle(fr, (int(x), int(y)), int(r), (0, 255, 0), 2)
            cv2.circle(fr, (int(x), int(y)), 3, (0, 0, 255), -1)
            hm = (H_img - y) * mpp
            cv2.putText(fr, f"h={hm:.3f} m", (int(x) + 8, int(y) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        vw.write(fr)
    cap.release()
    vw.release()
    print(f"  Vorschau-Video  : {args.preview}")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="PCMMS Ballon Video-Hoehen-Tracker (Video -> t_s,h_m CSV).")
    ap.add_argument("video", help="Eingabe-Videodatei")
    ap.add_argument("--info", action="store_true",
                    help="Bildmasse + Standbilder ausgeben (Kalibrierung), dann Ende")

    g = ap.add_argument_group("Kalibrierung (einen Weg waehlen)")
    g.add_argument("--balloon-diam-m", type=float, default=None,
                   help="Bekannter Ballon-DURCHMESSER in m -> mpp automatisch")
    g.add_argument("--ref-meters", type=float, default=None,
                   help="Referenzlaenge in m (zusammen mit --ref-pixels)")
    g.add_argument("--ref-pixels", type=float, default=None,
                   help="zugehoerige Pixel-Laenge (zusammen mit --ref-meters)")
    g.add_argument("--mpp", type=float, default=None,
                   help="Massstab direkt in Meter pro Pixel")

    c = ap.add_argument_group("Farbe")
    c.add_argument("--color", choices=sorted(COLOR_PRESETS.keys()), default="red",
                   help="Farb-Preset (Default: red)")
    c.add_argument("--hsv-lower", type=_triple, default=None,
                   help="eigener HSV-Unterwert 'H,S,V'")
    c.add_argument("--hsv-upper", type=_triple, default=None,
                   help="eigener HSV-Oberwert 'H,S,V'")

    p = ap.add_argument_group("Verarbeitung / Ausgabe")
    p.add_argument("--out", default=None, help="Ausgabe-CSV (Default: <video>_hoehe.csv)")
    p.add_argument("--debug-csv", default=None, help="Zusatz-CSV mit Pixel-Rohdaten")
    p.add_argument("--preview", default=None, help="annotiertes Video schreiben (.mp4)")
    p.add_argument("--smooth", type=int, default=5,
                   help="Median-Glaettung in Frames (ungerade; Default 5; 1=aus)")
    p.add_argument("--min-radius", type=float, default=4.0,
                   help="Mindest-Radius einer Detektion in px (Default 4)")
    p.add_argument("--max-speed", type=float, default=4000.0,
                   help="Ausreisser-Grenze in px/s (Default 4000; 0=aus)")
    m = p.add_mutually_exclusive_group()
    m.add_argument("--use-msec", dest="use_msec", action="store_true", default=None,
                   help="Zeit aus Container-Zeitstempeln erzwingen")
    m.add_argument("--no-msec", dest="use_msec", action="store_false",
                   help="Zeit aus frame/fps erzwingen")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.info:
        info_mode(args.video)
        return
    track(args)


if __name__ == "__main__":
    main()
