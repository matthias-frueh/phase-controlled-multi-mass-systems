"""
einzugsgebiete.py – Attraktorkarten (Einzugsgebiete) des V1-Kandidaten für die Laufarten der Präregistrierung:
Endzustand nach einem Wurf auf den Kontaktast, je Wurfphase t₀ und Wurfgeschwindigkeit Δv, mit Grenzen per
Bisektion (Abnahme AP-03: Einzugsgebiet für alle Laufarten, auch Einzelmodul-, Schnitt- und Pilotläufe).

Das Einzugsgebiet des Kontaktasts ist nicht monoton (Satelliteninsel der Referenz, tests/test_ereignisloeser.py;
am Kandidaten ebenso). Das Skript gibt deshalb keine Schwelle aus, sondern die Karte Endzustand(t₀, Δv) mit
nummerierten Attraktoren und je Wurfphase die Δv-Intervalle. Das kleinste |Δv| mit Hüpfen je Vorzeichen ist
nur die untere Einhüllende der Karte.

Modell (ereignisloeser.py, 1 FG): Kelvin-Voigt-Kontakt N = −K·x − C·ẋ, Ablösung bei N = 0, Aufsetzen bei x = 0;
ideales Egg-Profil (THOLD = 0,65), keine Kippfreiheitsgrade. V1-Kandidat: Restmasse m₀ = 0,350 kg, drei Module
je 0,100 kg (M = 0,650 kg, μ = 0,4615), Hub 8 mm Spitze-Spitze je bewegtem Modul, f = 10 Hz, K = 1,5·10⁶ N/m,
C = 2ζ·√(K·M) mit ζ = 0,05 (Vorgabe), g = 9,81 m/s². Gegenstück Hunt-Crossley (--law hc): hc_aequivalent(),
n = 1,5, gleiche Tangentensteifigkeit in der Ruhelage, gleiche Stoßzahl bei 0,5 m/s (Zuordnung angenommen).
Laufarten (Phasen (φ₁, φ₂, φ₃), Hub je Modul): L1 (0°, 0°, 0°), (8, 0, 0) mm, Module 2 und 3 geparkt, Masse an
Bord; 21 Schnittpunkte (0°, φ₂, 240°), φ₂ = 100° … 140° in 2°-Schritten; Piloten (110°, 250°), (130°, 230°),
(110°, 252°); zum Vergleich synchron (0°, 0°) und (0°, 180°). L2 und L3 sind im 1-FG-Modell dieselbe Karte wie
L1, um τ_j = φ_j/(360°·f) in t₀ verschoben (gleiche Modulmasse und gleicher Hub; die Lage des Moduls wirkt erst
über Kippmoden): --pruefung rechnet das an einer Stichprobe nach.

Methode: Start auf dem Kontaktast zur Wurfphase t₀ (kontaktorbit; Hunt-Crossley: Newton ab dem verschobenen
Kelvin-Voigt-Orbit, siehe kontaktast()), dann Geschwindigkeitsstoß Δv (Stoßimpuls M·Δv). Lauf über n₀ Perioden
(Kelvin-Voigt 80, Hunt-Crossley 60), danach Klassifikation über die letzten 20 Perioden:
  Kontaktast  λ = 0 im Fenster und Poincaré-Schnitt gleich dem Orbit (|Δx| < 1e-9 m, |Δẋ| < 1e-6 m/s; Hunt-
              Crossley 1e-6 m, 1e-3 m/s, weil seine Dämpfung um die Ruhelage klein ist). Am Kontaktast zieht
              die Periodenabbildung mit |μ| = e^{−ζω_n·T} zusammen (ζ = 0,05: 5·10⁻⁴ je Periode), 20 Perioden
              ohne Abheben schließen ein späteres Abheben aus.
  Hüpfen      λ > 0 und Periode p (Poincaré-Schnitt wiederkehrend auf 1e-5 m/s und 1e-7 m über 10 Perioden).
              Der Hüpforbit zieht nur mit |μ| ≈ e (Stoßzahl; ζ = 0,05: 0,86, ζ = 0,02: 0,94) zusammen; ohne
              Wiederkehr wird um je n₀ Perioden verlängert, höchstens auf 800 (Hunt-Crossley 120). P2-Orbits
              mit einem Aufsetzer je Doppelperiode brauchen bei ζ = 0,02 bis zu 480 Perioden.
  irregulär   ohne Wiederkehr bis zum Höchstwert (Status „nicht eingeschwungen“).
Attraktor-Signatur: (p, Aufsetzer je p Perioden, λ, F_max); gleiche Signaturen (λ auf 0,05 Prozentpunkte, F_max
auf 0,5 N bzw. 0,1 %) werden je Laufart zu einem Attraktor zusammengefasst und nach Häufigkeit nummeriert
(K Kontaktast, H1, H2, … Hüpfzustände, X irregulär). Je Hüpfattraktor Newton-Schießverfahren auf den p-fachen
Poincaré-Schnitt mit Floquet-Multiplikatoren; dessen Werte stehen in der Attraktortabelle. Grenzen: zwischen
in Δv benachbarten Rasterpunkten mit verschiedenem Endzustand rekursive Bisektion, bis die Klammer ≤ 0,005 m/s
breit ist (Raster 0,05: vier Schritte, Breite 0,003125 m/s); liegt ein dritter Zustand dazwischen, werden beide
Grenzen verfolgt. Inseln schmaler als das Raster zwischen gleichen Nachbarn bleiben unentdeckt (am Kandidaten
findet ein 0,01-Raster bei L1 oberhalb 0,6 m/s zusätzliche Hüpfbänder, --dv-schritt 0.01).

Ausgaben (--out data/einzugsgebiete_v1_kandidat.csv):
  <out>                  eine Zeile je Rasterzelle mit allen Konfigurationsparametern, t0_T, dv_m_s, impuls_Ns,
                         attraktor, zustand, periode, aufsetzer_je_periode, lambda_pct, F_max_N, stossspitze_N
                         (Fenster), F_max_lauf_N und stossspitze_lauf_N (ganzer Lauf einschließlich Einschwingen),
                         perioden, status. Bei Hunt-Crossley ist F_max_N einer Kontaktast-Zelle ein Fensterwert des
                         noch abklingenden Einschwingens (|μ| = 0,79 je Periode), nicht der Orbit; den Orbitwert
                         nennt <out>_attraktoren.csv.
  <out>_grenzen.csv      Bisektionsklammern (dv_links, dv_rechts, Attraktor links und rechts)
  <out>_attraktoren.csv  Signatur je Attraktor und Laufart (Newton-Werte, |μ|_max, Aufsetzphase, Zellenzahl)
  <out>_intervalle.csv   je Wurfphase die Δv-Intervalle gleichen Endzustands (Rand = äußerster gerechneter Punkt)
  <out>_kennwerte.csv    je Laufart: Anteil Hüpfen, kleinstes |Δv| mit Hüpfen je Vorzeichen (untere Einhüllende,
                         keine Schwelle), Wurfphasen mit Rückkehr-Inseln oberhalb des ersten Hüpfwurfs, größte
                         Stoßspitze im Hüpfzustand und im Einschwingen

Aufruf (aus dem Repository-Wurzelverzeichnis):
  python3 code/einzugsgebiete.py --pruefung
          Abgleich mit den bekannten Werten (V1 synchron, t₀ = 0, Ruhelage und Kontaktast) und L1/L2/L3-Stichprobe
  python3 code/einzugsgebiete.py --raster voll --laufart alle --out data/einzugsgebiete_v1_kandidat.csv
          16 Wurfphasen × Δv = −1,00 … +1,00 m/s (Schritt 0,05), 27 Laufarten, Grenzen per Bisektion
  python3 code/einzugsgebiete.py --raster grob --laufart empfindlichkeit --zeta 0.02 0.1 0.2 \
          --out data/einzugsgebiete_v1_kandidat_zeta.csv
          8 Wurfphasen × Δv-Schritt 0,1 für L1, (120°, 240°), (100°, 240°), (140°, 240°), Pilot (110°, 252°), synchron
  python3 code/einzugsgebiete.py --raster grob --laufart hc --law hc --dv-min 0.1 --keine-grenzen \
          --out data/einzugsgebiete_v1_kandidat_hc.csv
          Hunt-Crossley für L1, (120°, 240°), synchron, Δv = +0,1 … +1,0 m/s
  python3 code/einzugsgebiete.py --raster grob --dv-schritt 0.01 --keine-grenzen --laufart L1 S100 S120 S140 \
          P110-252 --out data/einzugsgebiete_v1_kandidat_fein.csv
          Feinprüfung: 8 Wurfphasen × Δv-Schritt 0,01 ohne Bisektion
  python3 code/einzugsgebiete.py --zusammenfassung data/einzugsgebiete_v1_kandidat.csv
          Attraktoren, Kennwerte und Intervalltabellen (Markdown) aus vorhandenen Dateien
Optionen: --laufart (alle | pflicht | empfindlichkeit | hc | L1 L2 L3 | S100 … S140 | P110-250 P130-230 P110-252 |
synchron | 0-180), --zeta (mehrere Werte), --law kv|hc, --raster voll|grob, --dv-schritt und --wurfphasen (Raster
frei), --dv-min, --dv-max, --keine-grenzen, --prozesse (Vorgabe 3), --fortschritt (Datei, eine Zeile je fertiger
Wurfphase), --start orbit|ruhe.

Rechenzeit (drei Prozesse): Kelvin-Voigt ≈ 6 ms je Periode, eine Zelle 0,5 s (Kontaktast, 80 Perioden) bis
1–3 s (Hüpfen, 160–480 Perioden); volles Raster (17 712 Zellen und 1 239 Bisektionsläufe) 63 min,
Empfindlichkeit (drei ζ, sechs Laufarten, grobes Raster mit Grenzen, 4 126 Läufe) 15 min, Hunt-Crossley
(240 Zellen, solve_ivp, ≈ 0,15 s je Periode im Dauerkontakt) 9 min, Feinprüfung (8 040 Zellen) 24 min,
--pruefung 25 s (ein Prozess).

Matthias Früh · PCMMS · Oktober 2026
"""
import argparse
import csv
import math
import multiprocessing as mp
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ereignisloeser as el  # noqa: E402
from finesweep import THOLD  # noqa: E402

HUB = 8e-3                                          # Hub Spitze-Spitze je bewegtem Modul [m]
SCHNITT = tuple(float(p) for p in np.arange(100.0, 140.0 + 1e-9, 2.0))
PILOTEN = ((110.0, 250.0), (130.0, 230.0), (110.0, 252.0))
GRENZ_TOL = 0.005                                   # Breite der Bisektionsklammer [m/s]
FENSTER = 20                                        # Auswertefenster [Perioden]
LAUF = {'kv': dict(n0=80, n_ext=80, n_max=800, tol_x=1e-9, tol_v=1e-6),
        'hc': dict(n0=60, n_ext=60, n_max=120, tol_x=1e-6, tol_v=1e-3)}
TOL_P = dict(tol_v=1e-5, tol_x=1e-7)                # Wiederkehr des Hüpforbits
GLEICH_LAMBDA, GLEICH_F_ABS, GLEICH_F_REL = 0.05, 0.5, 1e-3


# ── Laufarten ─────────────────────────────────────────────────────────────────
def laufarten():
    """Schlüssel → (Name, Gruppe, Phasen (φ₁, φ₂, φ₃) [°], Hub je Modul [m]). L2 und L3 nur für --pruefung."""
    L = {'L1': ('L1', 'einzel', (0.0, 0.0, 0.0), (HUB, 0.0, 0.0)),
         'L2': ('L2', 'einzel', (0.0, 120.0, 240.0), (0.0, HUB, 0.0)),
         'L3': ('L3', 'einzel', (0.0, 120.0, 240.0), (0.0, 0.0, HUB))}
    for p2 in SCHNITT:
        L[f'S{p2:g}'] = (f'Schnitt ({p2:g}°,240°)', 'schnitt', (0.0, p2, 240.0), (HUB,) * 3)
    for p2, p3 in PILOTEN:
        L[f'P{p2:g}-{p3:g}'] = (f'Pilot ({p2:g}°,{p3:g}°)', 'pilot', (0.0, p2, p3), (HUB,) * 3)
    L['synchron'] = ('synchron (0°,0°)', 'synchron', (0.0, 0.0, 0.0), (HUB,) * 3)
    L['0-180'] = ('(0°,180°)', 'zweiergruppe', (0.0, 0.0, 180.0), (HUB,) * 3)
    return L


MENGEN = {'alle': ['L1'] + [f'S{p:g}' for p in SCHNITT] + ['P110-250', 'P130-230', 'P110-252', 'synchron', '0-180'],
          'pflicht': ['L1'] + [f'S{p:g}' for p in SCHNITT] + ['P110-250', 'P130-230', 'P110-252'],
          'empfindlichkeit': ['L1', 'S120', 'S100', 'S140', 'P110-252', 'synchron'],
          'hc': ['L1', 'S120', 'synchron']}


def system(schluessel, zeta=0.05, law='kv'):
    """System des V1-Kandidaten für eine Laufart; bei law = 'hc' das Hunt-Crossley-Gegenstück (n = 1,5)."""
    _, _, phis, hub = laufarten()[schluessel]
    sy = el.kandidat(phis[1], phis[2], zeta=zeta).mit(phis=phis, hub=hub)
    return el.hc_aequivalent(sy, zeta, 1.5, 0.5) if law == 'hc' else sy


def konfiguration(schluessel, zeta, law):
    """Konfigurationsspalten einer Laufart (je Zeile der CSV-Dateien wiederholt)."""
    name, _, phis, hub = laufarten()[schluessel]
    base, sy = system(schluessel, zeta, 'kv'), system(schluessel, zeta, law)
    kv = law == 'kv'
    return {'laufart': name, 'phi1_deg': phis[0], 'phi2_deg': phis[1], 'phi3_deg': phis[2],
            'hub1_mm': 1e3 * hub[0], 'hub2_mm': 1e3 * hub[1], 'hub3_mm': 1e3 * hub[2], 'm0_kg': sy.m0,
            'm_modul_kg': float(sy.m[0]), 'M_kg': sy.M, 'f_Hz': sy.f, 'profil': f'egg THOLD={THOLD:g}',
            'gesetz': 'Kelvin-Voigt' if kv else 'Hunt-Crossley', 'K_N_m': base.K, 'zeta': zeta,
            'C_Ns_m': base.C if kv else '', 'hc_n': '' if kv else sy.n, 'hc_Kh_N_m_n': '' if kv else sy.K,
            'hc_alpha_s_m': '' if kv else sy.alpha, 'g_m_s2': sy.g}


def kontaktast(schluessel, zeta, law, t0):
    """Startzustand auf dem Kontaktast zur Zeit t0. Kelvin-Voigt geschlossen (kontaktorbit). Hunt-Crossley: Newton ab
    dem Kelvin-Voigt-Orbit, um die Differenz der statischen Einfederungen verschoben (so startet inzwischen auch
    ereignisloeser.startzustand(…, 'orbit'); vorher begann es in der Ruhelage und fand den Kontaktast am Kandidaten
    an 5 von 24 Wurfphasen nicht)."""
    kv = system(schluessel, zeta, 'kv')
    z = el.startzustand(kv, 'orbit', t0)
    if law == 'kv':
        return z
    hc = system(schluessel, zeta, 'hc')
    o = el.newton(hc, z + np.array([hc.ruhelage() - kv.ruhelage(), 0.0]), t0, iters=12)
    if not o['konvergiert'] or el.simulate(hc, *o['z'], t0, 1)['tflug'][0] > 0:
        raise ValueError('kein Kontaktast gefunden')
    return o['z']


# ── eine Zelle ────────────────────────────────────────────────────────────────
def zelle(sy, z0, t0, dv, law='kv', z_orbit=None):
    """Wurf Δv zur Zeit t0 auf den Startzustand z0; Endzustand mit Kenngrößen (siehe Modul-Docstring). z_orbit:
    Kontaktast zur Phase t0 als Vergleich (Vorgabe z0, also Start auf dem Kontaktast)."""
    par, T = LAUF[law], sy.T
    z_orbit = z0 if z_orbit is None else z_orbit
    r = el.simulate(sy, z0[0], z0[1] + dv, t0, par['n0'])
    n, fmax_lauf, sp_lauf = par['n0'], -np.inf, -np.inf
    while True:
        fmax_lauf = max(fmax_lauf, float(r['Fmax'].max()))
        a = r['aufsetzer'][np.isfinite(r['aufsetzer'][:, 1])]
        if a.size:
            sp_lauf = max(sp_lauf, float(a[:, 5].max()))
        nr = len(r['D1'])
        k = el.kenngroessen(r, nr - FENSTER, nr)
        p = 0
        if k['liftoff'] == 0.0:
            if abs(r['PX'][-1] - z_orbit[0]) < par['tol_x'] and abs(r['PV'][-1] - z_orbit[1]) < par['tol_v']:
                p = 1
        else:
            p = el.periode(r, n_last=10, **TOL_P)[0]
        if p > 0 or n >= par['n_max']:
            break
        r = el.simulate(sy, r['PX'][-1], r['PV'][-1], t0 + n * T, par['n_ext'])
        n += par['n_ext']
    nr = len(r['D1'])
    w = FENSTER if p <= 0 else p * math.ceil(FENSTER / p)
    k = el.kenngroessen(r, nr - w, nr)
    a = r['aufsetzer'][np.isfinite(r['aufsetzer'][:, 1])]
    win = a[a[:, 0] >= t0 + (n - w) * T - 1e-12] if a.size else a
    kontakt = k['liftoff'] == 0.0
    zustand = 'Kontaktast' if (kontakt and p > 0) else ('Hüpfen' if p > 0 else 'irregulär')
    phasen = np.mod(win[:, 0] / T, 1.0) if win.size else np.zeros(0)
    return dict(dv=float(dv), zustand=zustand, periode=p if p > 0 else -1,
                aufsetzer=k['aufsetzer_je_periode'], lam=k['liftoff'], F_max=k['F_max'],
                stoss=float(win[:, 5].max()) if win.size else float('nan'),
                F_max_lauf=fmax_lauf, stoss_lauf=sp_lauf if np.isfinite(sp_lauf) else float('nan'),
                perioden=n, status='eingeschwungen' if p > 0 else 'nicht eingeschwungen',
                px=float(r['PX'][-1]), pv=float(r['PV'][-1]), t_end=t0 + n * T,
                aufsetzphasen=sorted(set(np.round(phasen, 4).tolist())))


def gleich(a, b):
    """Gleicher Endzustand zweier Zellen (Signatur p, Aufsetzer je p Perioden, λ, F_max)."""
    if a['zustand'] != b['zustand']:
        return False
    if a['zustand'] != 'Hüpfen':
        return True
    if a['periode'] != b['periode'] or round(a['aufsetzer'] * a['periode']) != round(b['aufsetzer'] * b['periode']):
        return False
    tol_f = max(GLEICH_F_ABS, GLEICH_F_REL * max(a['F_max'], b['F_max']))
    return abs(a['lam'] - b['lam']) < GLEICH_LAMBDA and abs(a['F_max'] - b['F_max']) < tol_f


def grenzen(sy, z0, t0, lo, hi, law, z_orbit=None, tol=GRENZ_TOL):
    """Rekursive Bisektion zwischen zwei Zellen mit verschiedenem Endzustand; Rückgabe (Klammern, neue Zellen)."""
    if gleich(lo, hi):
        return [], []
    if hi['dv'] - lo['dv'] <= tol + 1e-12:
        return [(lo, hi)], []
    mid = zelle(sy, z0, t0, round(0.5 * (lo['dv'] + hi['dv']), 10), law, z_orbit)
    k1, c1 = grenzen(sy, z0, t0, lo, mid, law, z_orbit, tol)
    k2, c2 = grenzen(sy, z0, t0, mid, hi, law, z_orbit, tol)
    return k1 + k2, c1 + [mid] + c2


def zeile(auftrag):
    """Eine Wurfphase einer Laufart: alle Δv des Rasters, danach die Grenzen. Für multiprocessing."""
    schluessel, zeta, law, t0_T, dvs, mit_grenzen, start = auftrag
    sy = system(schluessel, zeta, law)
    t0 = t0_T * sy.T
    t_start = time.time()
    try:
        z_orbit = kontaktast(schluessel, zeta, law, t0)
    except (ValueError, RuntimeError):
        return dict(auftrag=auftrag, zellen=[], klammern=[], extra=[], kein_kontaktast=True, sekunden=0.0)
    z0 = z_orbit if start == 'orbit' else el.startzustand(sy, 'std', t0)
    zellen = [zelle(sy, z0, t0, dv, law, z_orbit) for dv in dvs]
    klammern, extra = [], []
    if mit_grenzen:
        for lo, hi in zip(zellen[:-1], zellen[1:]):
            k, c = grenzen(sy, z0, t0, lo, hi, law, z_orbit)
            klammern += k
            extra += c
    return dict(auftrag=auftrag, zellen=zellen, klammern=klammern, extra=extra, kein_kontaktast=False,
                z0=(float(z0[0]), float(z0[1])), sekunden=time.time() - t_start)


# ── Attraktoren je Laufart ────────────────────────────────────────────────────
def attraktoren(ergebnisse, sy):
    """Fasst die Endzustände aller Zellen (Raster und Bisektion) einer Laufart zusammen, nummeriert sie nach
    Häufigkeit im Raster und verfeinert jeden Hüpfattraktor mit Newton. Rückgabe Liste der Attraktoren."""
    gruppen = []                                    # je Gruppe: Vertreter, Rasterzellen, alle Zellen
    for e in ergebnisse:
        for c, im_raster in [(c, True) for c in e['zellen']] + [(c, False) for c in e['extra']]:
            for g in gruppen:
                if gleich(g['rep'], c):
                    break
            else:
                g = dict(rep=c, n_raster=0, mitglieder=[])
                gruppen.append(g)
            g['mitglieder'].append(c)
            g['n_raster'] += int(im_raster)
    hop = sorted([g for g in gruppen if g['rep']['zustand'] == 'Hüpfen'], key=lambda g: -g['n_raster'])
    for i, g in enumerate(hop, 1):
        g['label'] = f'H{i}'
    for g in gruppen:
        if g['rep']['zustand'] == 'Kontaktast':
            g['label'] = 'K'
        elif g['rep']['zustand'] == 'irregulär':
            g['label'] = 'X'
        for c in g['mitglieder']:
            c['attraktor'] = g['label']
    for g in gruppen:
        rep = g['rep']
        g.update(periode=rep['periode'], aufsetzer=rep['aufsetzer'], lam=rep['lam'], F_max=rep['F_max'],
                 stoss=rep['stoss'], mu=float('nan'), newton='', phasen=rep['aufsetzphasen'])
        if rep['zustand'] == 'Kontaktast' and sy.gesetz == 'kv':
            _, mu, _ = el.kontaktorbit(sy)
            g.update(mu=float(np.abs(mu).max()), newton='geschlossen')
        elif rep['zustand'] == 'Kontaktast' and ergebnisse:
            e0 = ergebnisse[0]
            o = el.newton(sy, e0['z0'], e0['auftrag'][3] * sy.T, iters=12)
            g.update(mu=float(np.abs(o['mu']).max()), newton='konvergiert' if o['konvergiert'] else 'nicht konvergiert')
        elif rep['zustand'] == 'Hüpfen':
            p = rep['periode']
            try:
                o = el.newton(sy, (rep['px'], rep['pv']), rep['t_end'], p)
            except (RuntimeError, np.linalg.LinAlgError):
                o = dict(konvergiert=False)
            if o['konvergiert']:
                w = p * math.ceil(FENSTER / p)
                r = el.simulate(sy, *o['z'], rep['t_end'], w)
                k = el.kenngroessen(r)
                a = r['aufsetzer'][np.isfinite(r['aufsetzer'][:, 1])]
                g.update(lam=k['liftoff'], F_max=k['F_max'], aufsetzer=k['aufsetzer_je_periode'],
                         stoss=float(a[:, 5].max()) if a.size else float('nan'),
                         mu=float(np.abs(o['mu']).max()), newton='konvergiert',
                         phasen=sorted(set(np.round(np.mod(a[:p * 4, 0] / sy.T, 1.0), 4).tolist())))
            else:
                g['newton'] = 'nicht konvergiert'
    order = {'K': 0, 'X': 99}
    return sorted(gruppen, key=lambda g: order.get(g['label'], int(g['label'][1:]) if g['label'][0] == 'H' else 50))


def intervalle(e):
    """Δv-Intervalle gleichen Attraktors einer Wurfphase aus Raster- und Bisektionszellen."""
    zs = sorted(e['zellen'] + e['extra'], key=lambda c: c['dv'])
    out = []
    for c in zs:
        if out and out[-1]['attraktor'] == c['attraktor']:
            out[-1]['dv_bis'] = c['dv']
            out[-1]['punkte'] += 1
        else:
            out.append(dict(attraktor=c['attraktor'], dv_von=c['dv'], dv_bis=c['dv'], punkte=1))
    return out


def kennwerte(ergebnisse, gruppen):
    """Kennwerte einer Laufart: Anteile, untere Einhüllende des Hüpfens je Vorzeichen, Rückkehr-Inseln."""
    raster = [c for e in ergebnisse for c in e['zellen']]
    alle = [(e['auftrag'][3], c) for e in ergebnisse for c in e['zellen'] + e['extra']]
    n = len(raster)
    out = dict(zellen=n, anteil_huepfen_pct=100.0 * sum(c['zustand'] == 'Hüpfen' for c in raster) / max(n, 1),
               anteil_irregulaer_pct=100.0 * sum(c['zustand'] == 'irregulär' for c in raster) / max(n, 1),
               anteil_kontaktast_pct=100.0 * sum(c['zustand'] == 'Kontaktast' for c in raster) / max(n, 1))
    for vz, name in ((1, 'pos'), (-1, 'neg')):
        nicht_k = [(abs(c['dv']), t) for t, c in alle if c['zustand'] != 'Kontaktast' and vz * c['dv'] > 0]
        m = min(nicht_k) if nicht_k else (float('nan'), float('nan'))
        out[f'dv_huepf_min_{name}'] = vz * m[0] if nicht_k else float('nan')
        out[f't0_T_huepf_min_{name}'] = m[1]
        inseln = []
        for e in ergebnisse:
            zs = [c for c in e['zellen'] + e['extra'] if vz * c['dv'] > 0]
            erst = [abs(c['dv']) for c in zs if c['zustand'] != 'Kontaktast']
            if erst and any(c['zustand'] == 'Kontaktast' and abs(c['dv']) > min(erst) for c in zs):
                inseln.append(e['auftrag'][3])
        out[f'inseln_{name}'] = ';'.join(f'{t:.4f}' for t in sorted(inseln))
        out[f'n_inseln_{name}'] = len(inseln)
    hg = [g for g in gruppen if g['label'][0] == 'H']
    out['attraktoren'] = ' '.join(g['label'] for g in gruppen)
    out['stossspitze_max_N'] = max((g['stoss'] for g in hg), default=float('nan'))
    out['F_max_lauf_max_N'] = max(c['F_max_lauf'] for c in raster) if raster else float('nan')
    out['stossspitze_lauf_max_N'] = np.nanmax([c['stoss_lauf'] for c in raster]) \
        if raster and np.isfinite([c['stoss_lauf'] for c in raster]).any() else float('nan')
    return out


# ── Ausgabe ───────────────────────────────────────────────────────────────────
def _f(x, nd=6):
    if isinstance(x, str):
        return x
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return ''
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f'{x:.{nd}g}'


def schreiben(pfad, zeilen):
    if not zeilen:
        return
    with open(pfad, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(zeilen[0].keys()), lineterminator='\n')
        w.writeheader()
        for z in zeilen:
            w.writerow({k: _f(v) for k, v in z.items()})


def raster(art, dv_min=None, dv_max=None, schritt=None, n_t=None):
    """Wurfphasen t₀/T und Wurfgeschwindigkeiten Δv [m/s] des vollen bzw. groben Rasters (oder frei gewählt)."""
    n_v, s_v = (16, 0.05) if art == 'voll' else (8, 0.1)
    n_t, schritt = n_t or n_v, schritt or s_v
    lo = -1.0 if dv_min is None else dv_min
    hi = 1.0 if dv_max is None else dv_max
    k0, k1 = int(round(lo / schritt)), int(round(hi / schritt))
    return [i / n_t for i in range(n_t)], [round(k * schritt, 10) for k in range(k0, k1 + 1)]


def rechnen(a):
    schl = [s for x in a.laufart for s in (MENGEN[x] if x in MENGEN else [x])]
    unbekannt = [s for s in schl if s not in laufarten()]
    if unbekannt:
        raise SystemExit(f'unbekannte Laufart: {", ".join(unbekannt)}')
    t0s, dvs = raster(a.raster, a.dv_min, a.dv_max, a.dv_schritt, a.wurfphasen)
    mit_grenzen = not a.keine_grenzen
    auftraege = [(s, z, a.law, t, dvs, mit_grenzen, a.start) for z in a.zeta for s in schl for t in t0s]
    t_beginn = time.time()
    res = []
    fort = open(a.fortschritt, 'a', encoding='utf-8') if a.fortschritt else None
    with mp.Pool(a.prozesse) as pool:
        for i, e in enumerate(pool.imap_unordered(zeile, auftraege), 1):
            res.append(e)
            if fort:
                s, z, _, t = e['auftrag'][:4]
                fort.write(f'{i}/{len(auftraege)} {s} zeta={z:g} t0/T={t:.4f} {e["sekunden"]:.1f} s '
                           f'(gesamt {time.time() - t_beginn:.0f} s)\n')
                fort.flush()
    zellen_csv, grenzen_csv, attr_csv, int_csv, kw_csv = [], [], [], [], []
    for z in a.zeta:
        for s in schl:
            erg = sorted([e for e in res if e['auftrag'][0] == s and e['auftrag'][1] == z],
                         key=lambda e: e['auftrag'][3])
            sy = system(s, z, a.law)
            kopf = konfiguration(s, z, a.law)
            kopf['start'] = 'Kontaktast' if a.start == 'orbit' else 'Ruhelage'
            gruppen = attraktoren([e for e in erg if not e['kein_kontaktast']], sy)
            for e in erg:
                t0_T = e['auftrag'][3]
                if e['kein_kontaktast']:
                    for dv in dvs:
                        zellen_csv.append({**kopf, 't0_T': t0_T, 'dv_m_s': dv, 'impuls_Ns': sy.M * dv,
                                           'attraktor': '', 'zustand': '', 'periode': '', 'aufsetzer_je_periode': '',
                                           'lambda_pct': '', 'F_max_N': '', 'stossspitze_N': '', 'F_max_lauf_N': '',
                                           'stossspitze_lauf_N': '', 'perioden': 0, 'status': 'kein Kontaktast'})
                    continue
                for c in e['zellen']:
                    zellen_csv.append({**kopf, 't0_T': t0_T, 'dv_m_s': c['dv'], 'impuls_Ns': sy.M * c['dv'],
                                       'attraktor': c['attraktor'], 'zustand': c['zustand'], 'periode': c['periode'],
                                       'aufsetzer_je_periode': c['aufsetzer'], 'lambda_pct': c['lam'],
                                       'F_max_N': c['F_max'], 'stossspitze_N': c['stoss'],
                                       'F_max_lauf_N': c['F_max_lauf'], 'stossspitze_lauf_N': c['stoss_lauf'],
                                       'perioden': c['perioden'], 'status': c['status']})
                for lo, hi in e['klammern']:
                    grenzen_csv.append({'laufart': kopf['laufart'], 'gesetz': kopf['gesetz'], 'zeta': z, 't0_T': t0_T,
                                        'dv_links': lo['dv'], 'dv_rechts': hi['dv'], 'breite': hi['dv'] - lo['dv'],
                                        'attraktor_links': lo['attraktor'], 'attraktor_rechts': hi['attraktor']})
                for iv in intervalle(e):
                    int_csv.append({'laufart': kopf['laufart'], 'gesetz': kopf['gesetz'], 'zeta': z, 't0_T': t0_T,
                                    **iv})
            for g in gruppen:
                attr_csv.append({'laufart': kopf['laufart'], 'gesetz': kopf['gesetz'], 'zeta': z,
                                 'attraktor': g['label'], 'zustand': g['rep']['zustand'], 'periode': g['periode'],
                                 'aufsetzer_je_periode': g['aufsetzer'], 'lambda_pct': g['lam'],
                                 'F_max_N': g['F_max'], 'stossspitze_N': g['stoss'], 'mu_max': g['mu'],
                                 'newton': g['newton'], 'aufsetzphasen_T': ';'.join(f'{x:.4f}' for x in g['phasen']),
                                 'zellen_raster': g['n_raster']})
            kw = kennwerte([e for e in erg if not e['kein_kontaktast']], gruppen)
            kw_csv.append({'laufart': kopf['laufart'], 'gesetz': kopf['gesetz'], 'zeta': z,
                           'wurfphasen_ohne_kontaktast': sum(e['kein_kontaktast'] for e in erg), **kw})
    stamm = os.path.splitext(a.out)[0]
    schreiben(a.out, zellen_csv)
    if mit_grenzen:
        schreiben(stamm + '_grenzen.csv', grenzen_csv)
    schreiben(stamm + '_attraktoren.csv', attr_csv)
    schreiben(stamm + '_intervalle.csv', int_csv)
    schreiben(stamm + '_kennwerte.csv', kw_csv)
    n_lauf = sum(len(e['zellen']) + len(e['extra']) for e in res)
    print(f'{len(zellen_csv)} Rasterzellen, {n_lauf} Läufe mit Bisektion, {time.time() - t_beginn:.0f} s mit '
          f'{a.prozesse} Prozess{"en" if a.prozesse != 1 else ""}; geschrieben: {a.out} und Begleitdateien')
    if fort:
        fort.close()


def _de(x, nd=3, vz=False):
    """Zahl mit Dezimalkomma; NaN als Gedankenstrich."""
    if x != x:
        return '–'
    return (f'{x:+.{nd}f}' if vz else f'{x:.{nd}f}').replace('.', ',').replace('-', '−')


def _phase(t0):
    return f'{t0 * 16:.0f}/16' if abs(t0 * 16 - round(t0 * 16)) < 1e-9 else _de(t0, 4)


def zusammenfassung(pfad):
    """Markdown-Tabellen aus vorhandenen Ausgabedateien (Attraktoren, Kennwerte, Intervalle je Wurfphase)."""
    import pandas as pd
    stamm = os.path.splitext(pfad)[0]
    at = pd.read_csv(stamm + '_attraktoren.csv', keep_default_na=False, na_values=[''])
    kw = pd.read_csv(stamm + '_kennwerte.csv', keep_default_na=False, na_values=[''])
    iv = pd.read_csv(stamm + '_intervalle.csv', keep_default_na=False, na_values=[''])
    print('| Laufart | ζ | Attraktor | p | Aufsetzer je Periode | λ [%] | F_max [N] | Stoßspitze [N] | |μ|max '
          '| Aufsetzphase t/T | Rasterzellen |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for _, r in at.iterrows():
        ph = str(r.aufsetzphasen_T).replace('.', ',').replace(';', '; ') if r.aufsetzphasen_T == r.aufsetzphasen_T \
            else '–'
        print(f'| {r.laufart} | {_de(r.zeta, 2)} | {r.attraktor} | {r.periode} | {_de(r.aufsetzer_je_periode, 2)} | '
              f'{_de(r.lambda_pct)} | {_de(r.F_max_N, 2)} | {_de(r.stossspitze_N, 1)} | {_de(r.mu_max, 4)} | {ph} | '
              f'{r.zellen_raster} |')
    print()
    print('| Laufart | ζ | Kontaktast [%] | Hüpfen [%] | irregulär [%] | kleinstes Δv > 0 ohne Rückkehr (t₀/T) | '
          'kleinstes Δv < 0 ohne Rückkehr (t₀/T) | Wurfphasen mit Rückkehr-Inseln + / − | Stoßspitze Attraktor max [N] '
          '| F_max im Lauf max [N] |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for _, r in kw.iterrows():
        pos = f'{_de(r.dv_huepf_min_pos, 3, True)} ({_phase(r.t0_T_huepf_min_pos)})' \
            if r.dv_huepf_min_pos == r.dv_huepf_min_pos else '–'
        neg = f'{_de(r.dv_huepf_min_neg, 3, True)} ({_phase(r.t0_T_huepf_min_neg)})' \
            if r.dv_huepf_min_neg == r.dv_huepf_min_neg else '–'
        print(f'| {r.laufart} | {_de(r.zeta, 2)} | {_de(r.anteil_kontaktast_pct, 1)} | {_de(r.anteil_huepfen_pct, 1)} '
              f'| {_de(r.anteil_irregulaer_pct, 1)} | {pos} | {neg} | {r.n_inseln_pos} / {r.n_inseln_neg} | '
              f'{_de(r.stossspitze_max_N, 1)} | {_de(r.F_max_lauf_max_N, 1)} |')
    for (lauf, zeta), d in iv.groupby(['laufart', 'zeta'], sort=False):
        print(f'\n{lauf}, ζ = {_de(zeta, 2)}\n\n| t₀/T | Endzustand über Δv [m/s] |\n|---|---|')
        for t0, dd in d.groupby('t0_T'):
            folge = ' · '.join(f'{r.attraktor} {_de(r.dv_von, 3, True)} … {_de(r.dv_bis, 3, True)}'
                               if r.dv_von != r.dv_bis else f'{r.attraktor} {_de(r.dv_von, 3, True)}'
                               for _, r in dd.iterrows())
            print(f'| {_phase(t0)} | {folge} |')


def pruefung():
    """Abgleich mit den bekannten Werten und Stichprobe zur Gleichheit von L1, L2, L3 bis auf τ_j."""
    sy = el.kandidat()
    print('V1 synchron, t₀ = 0 (Referenz: Ruhelage 0,25 m/s kehrt zurück, 0,30 m/s hüpft mit λ ≈ 97,99 %, '
          'Stoßspitze ≈ 483,7 N)')
    z_orbit = el.startzustand(sy, 'orbit', 0.0)
    for start in ('std', 'orbit'):
        z0 = el.startzustand(sy, start, 0.0)
        for dv in (0.25, 0.30):
            c = zelle(sy, z0, 0.0, dv, z_orbit=z_orbit)
            print(f'  Start {"Ruhelage " if start == "std" else "Kontaktast"} Δv = {dv:.2f}: {c["zustand"]}, '
                  f'P{c["periode"]}, λ = {c["lam"]:.4f} %, Stoßspitze {c["stoss"]:.2f} N, F_max im Lauf '
                  f'{c["F_max_lauf"]:.2f} N, {c["perioden"]} Perioden')
    print('L1 bei t₀ gegen L2 bei t₀ + T/3 (φ₂ = 120°) und L3 bei t₀ + 2T/3 (φ₃ = 240°):')
    s1, s2, s3 = system('L1'), system('L2'), system('L3')
    dmax = 0.0
    for th in (0.0, 2 / 16, 12 / 16):               # Hüpfbänder und Rückkehr-Inseln der L1-Karte
        zs = [el.startzustand(s, 'orbit', (th + d) * s.T) for s, d in ((s1, 0), (s2, 1 / 3), (s3, 2 / 3))]
        for dv in (-0.55, -0.3, 0.45, 0.6):
            cs = [zelle(s, z, (th + d) * s.T, dv) for s, z, d in zip((s1, s2, s3), zs, (0, 1 / 3, 2 / 3))]
            d_l = max(abs(c['lam'] - cs[0]['lam']) for c in cs)
            d_f = max(abs(c['F_max'] - cs[0]['F_max']) for c in cs)
            dmax = max(dmax, d_f)
            print(f'  t₀/T = {th:.4f}, Δv = {dv:+.2f}: ' + ' | '.join(f'{c["zustand"]} λ {c["lam"]:.4f} % '
                  f'F_max {c["F_max"]:.3f} N' for c in cs) + f'  (Abweichung λ {d_l:.1e} %, F_max {d_f:.1e} N, '
                  f'gleich: {all(c["zustand"] == cs[0]["zustand"] for c in cs)})')
    print(f'  größte Abweichung F_max {dmax:.1e} N')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--raster', choices=('voll', 'grob'), default='voll')
    ap.add_argument('--laufart', nargs='+', default=['alle'])
    ap.add_argument('--zeta', type=float, nargs='+', default=[0.05])
    ap.add_argument('--law', choices=('kv', 'hc'), default='kv')
    ap.add_argument('--dv-min', type=float)
    ap.add_argument('--dv-max', type=float)
    ap.add_argument('--keine-grenzen', action='store_true', help='ohne Bisektion der Grenzen')
    ap.add_argument('--dv-schritt', type=float, help='Δv-Schritt [m/s] statt 0,05 (voll) bzw. 0,1 (grob)')
    ap.add_argument('--wurfphasen', type=int, help='Zahl der Wurfphasen statt 16 (voll) bzw. 8 (grob)')
    ap.add_argument('--start', choices=('orbit', 'ruhe'), default='orbit')
    ap.add_argument('--prozesse', type=int, default=3)
    ap.add_argument('--fortschritt', help='Fortschrittsdatei')
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'data', 'einzugsgebiete_v1_kandidat.csv'))
    ap.add_argument('--pruefung', action='store_true', help='Abgleich mit bekannten Werten, L1/L2/L3')
    ap.add_argument('--zusammenfassung', metavar='CSV', help='Tabellen aus vorhandenen Dateien')
    a = ap.parse_args()
    if a.pruefung:
        pruefung()
    elif a.zusammenfassung:
        zusammenfassung(a.zusammenfassung)
    else:
        if a.prozesse < 1 or any(z < 0 for z in a.zeta) or (a.dv_schritt is not None and a.dv_schritt <= 0) \
                or (a.wurfphasen is not None and a.wurfphasen < 1):
            ap.error('--prozesse ≥ 1, --zeta ≥ 0, --dv-schritt > 0 und --wurfphasen ≥ 1')
        rechnen(a)


if __name__ == '__main__':
    main()
