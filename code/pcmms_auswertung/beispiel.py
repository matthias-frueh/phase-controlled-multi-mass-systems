"""Kleiner, vollständig reproduzierbarer Beispieldatensatz der Schnittstelle (docs/ap11_ap12_ap13_schnittstellen.md).

Zwei Rohläufe der Ebene Z (ein Referenzlauf und ein Einzelmodullauf L₁, je 6 Zyklen bei 10 Hz) mit analytisch
vorgegebenen Zellkräften (Harmonische k = 1 … 3), dazu Manifest, statische Kalibrierung, Regelprofil, ein Beispiel
für Bootstrap-Indizes und die Wahrheit in einem getrennten Verzeichnis. Keine Physik, kein Rauschen: Der Datensatz
zeigt das Format; die Kette rechnet mit den Generatoren von AP-13. Gleiche Seeds ergeben bitgleiche Dateien.

Aufruf: python3 code/pcmms_auswertung beispiel --ausgabe <verzeichnis>
"""
import os

import numpy as np

from . import formate, konventionen, regeln, rohdaten

F = 10.0
KMAX = 3
N_ZYKLEN = 6
F_TAKT = 1e6                                      # Zeitgeber der Indeximpulse (§5.1: Quantisierung ≤ 0,01°)
EMPF = 1e-6                                       # N je ADC-Einheit
NULLPUNKT = np.array([120000.0, -80000.0, 45000.0])
F0 = np.array([2.1255, 2.1255, 2.1255])          # statische Zelllasten [N]
# Zellharmonische des laufenden Moduls 1 (Bezug: eigener Indeximpuls), k = 1, 2, 3 [N]
A_ZELLEN = np.array([[1.30 * np.exp(-0.40j), 0.43 * np.exp(1.10j), 0.18 * np.exp(-2.00j)],
                     [0.02 * np.exp(0.30j), 0.01 * np.exp(-0.70j), 0.004 * np.exp(0.90j)],
                     [-0.02 * np.exp(0.30j), -0.01 * np.exp(-0.70j), -0.004 * np.exp(0.90j)]])
KENNUNG = formate.synth_kennung('BEISPIEL', '2026-10')


def abtastrate():
    """A6 für f = 10 Hz und k_max = 3, auf 10 Hz aufgerundet (keine pauschale Abtastrate)."""
    return float(np.ceil(konventionen.abtastrate_a6(F, KMAX) / 10.0) * 10.0)


def _lauf(lauf_id, laufart, modul, position, t_start):
    fs = abtastrate()
    t_rampe, t_e = 0.2, 0.1
    t_fenster = t_rampe + t_e
    dauer = t_fenster + (N_ZYKLEN + 0.5) / F
    n = int(np.floor(dauer * fs))
    t0 = 0.25 / fs                                 # Unterabtastversatz
    t = t0 + np.arange(n) / fs
    kraft = np.repeat(F0[:, None], n, 1)
    idx = {}
    if laufart == 'L':
        ti = rohdaten.index_quantisiert(t_fenster + np.arange(N_ZYKLEN + 1) / F, F_TAKT)
        idx = {f'index_modul{j}': (ti if j == modul else np.zeros(0)) for j in (1, 2, 3)}
        rampe = np.clip((t - 0.0) / t_rampe, 0, 1)
        th = 2 * np.pi * F * (t - ti[0])
        k = np.arange(1, KMAX + 1)
        kraft = kraft + rampe * np.real(A_ZELLEN @ np.exp(1j * np.outer(k, th)))
    else:
        idx = {f'index_modul{j}': np.zeros(0) for j in (1, 2, 3)}
    adc = np.rint(NULLPUNKT[:, None] + kraft / EMPF).astype(np.int64)
    inhalt = dict(
        lauf=dict(lauf_id=lauf_id, laufart=laufart, modul=modul, einstellung=1,
                  konfiguration=dict(id='L1' if laufart == 'L' else 'R', gruppe='einzel' if laufart == 'L' else
                                     'referenz', phi_soll_grad=None),
                  phase=0, block=None, messtag=1, position=position, kontrollsatz=None, t_start=t_start),
        erfassung=dict(f_soll=F, f_s=fs, t0=t0, adc=dict(bits=24, vollausschlag=2 ** 23 - 1), f_takt=F_TAKT,
                       kanaele=[dict(name='kraft_adc', art='kraft', einheit='ADC', zellen=[1, 2, 3])]
                       + [dict(name=f'index_modul{j}', art='index', einheit='s', modul=j) for j in (1, 2, 3)]
                       + [dict(name='temperatur_zellen', art='temperatur', einheit='°C')]),
        protokoll=dict(t_rampe_ende=t_rampe, t_e=t_e, n_zyklen_fenster=N_ZYKLEN, stoerung=False,
                       aufzeichnung_ok=True, park_ok=True if laufart == 'L' else None, bediener='synthetisch',
                       notizen='Beispieldatensatz der Schnittstelle'),
        umgebung=dict(luftdruck_hPa=1013.0, lufttemperatur_C=21.0, feuchte_pct=45.0, versorgung_V=24.0),
        einstellungen=dict(verstaerkung='fest', filter='analog, gleich in allen Kraftkanälen', firmware='synthetisch',
                           kalibrier_ids=['SYNTH-BEISPIEL-KAL']),
        generator=dict(programm='pcmms_auswertung.beispiel', seed=None, szenario='Beispiel'))
    daten = dict(kraft_adc=adc, temperatur_zellen=np.full((3, 2), 22.0), t_temperatur=np.array([0.0, dauer]),
                 uebersteuerung=np.zeros(3, bool), **idx)
    return inhalt, daten


def kalibrierung_beispiel():
    """Statische Kalibrierung (P0.1) der drei Zellen und Massen (P0.2) als Minimalbeispiel des Formats."""
    return dict(
        zellen=[dict(zelle=c + 1, nullpunkt_adc=float(NULLPUNKT[c]), empfindlichkeit_N_je_adc=EMPF,
                     u_empfindlichkeit_rel=1e-4, kennlinie_quadratisch=0.0, umrechnung='linear') for c in range(3)],
        g=dict(wert=9.81, u=1e-5, quelle='Beispielwert (synthetisch)'),
        p0_2=dict(konvention='b', M_kg=float(F0.sum() / 9.81), u_M_kg=1e-5, m_j_kg=[0.1, 0.1, 0.1],
                  u_m_j_kg=[1e-5] * 3, F_c_stat=F0.tolist()),
        m_L=dict(wert_kg=0.0, u_kg=0.0, quelle='Vorgabe (synthetisch), keine Messung'),
        hinweis='Nur das Format; vollständige Kalibrierung liefert AP-11 (anpassung.py)')


def wahrheit_beispiel():
    """Analytische Harmonische der Mittelkurven (k = 1 … 3): L₁ Zellen und Summe, Referenzlauf null."""
    return dict(L1=dict(Nk_zellen=A_ZELLEN, Nk_summe=A_ZELLEN.sum(0), N_mittel_zellen=F0, N_mittel=F0.sum()),
                R=dict(N_mittel_zellen=F0, N_mittel=F0.sum()),
                hinweis='rauschfrei; Stufe 1 trifft diese Werte bis auf den Interpolationsfehler von A6 '
                        '((π·k·f/f_s)²/2 ≤ 10⁻³ relativ) und die Quantisierung (10⁻⁶ N)')


def erzeugen(ausgabe):
    """Schreibt eingang/ (Rohläufe, Manifest, Kalibrierung, Regelprofil, Bootstrap-Indizes) und wahrheit/."""
    ein = os.path.join(ausgabe, 'eingang')
    laeufe_dir = os.path.join(ein, 'laeufe')
    os.makedirs(laeufe_dir, exist_ok=True)
    zeilen = []
    for lid, art, modul, pos, ts in (('B-R-001', 'R', None, 0, 0.0), ('B-L1-001', 'L', 1, 1, 20.0)):
        inhalt, daten = _lauf(lid, art, modul, pos, ts)
        zeilen.append(rohdaten.schreibe_rohlauf(laeufe_dir, inhalt, daten, KENNUNG))
    rohdaten.schreibe_manifest(laeufe_dir, zeilen, KENNUNG)
    formate.schreibe(os.path.join(ein, 'kalibrierung'), formate.kopf('kalibrierung', KENNUNG),
                     inhalt=kalibrierung_beispiel())
    regeln.schreibe_profil(os.path.join(ein, 'regelprofil'), regeln.profil('ENTW-2026-10'))
    # Bootstrap-Indizes nach Plan 2.6 c (Format): Zeilen Replikate, Spalten gezogene Läufe der Quelle
    ss = np.random.SeedSequence(20261016)
    kinder = ss.spawn(2)
    idx = {'A/L1': np.random.Generator(np.random.PCG64(kinder[0])).integers(0, 1, size=(4, 1)),
           'B0/modul1': np.random.Generator(np.random.PCG64(kinder[1])).integers(0, 1, size=(4, 1))}
    formate.schreibe(os.path.join(ein, 'bootstrap_indizes'),
                     formate.kopf('bootstrap_indizes', KENNUNG, seed=20261016, B=4,
                                  ordnung='gültige Läufe der Quelle in aufsteigender Position der Laufreihenfolge'),
                     {k.replace('/', '__'): v for k, v in idx.items()})
    w = wahrheit_beispiel()
    formate.schreibe(os.path.join(ausgabe, 'wahrheit', 'wahrheit'), formate.kopf('wahrheit', KENNUNG),
                     {f'{a}__{b}': np.asarray(v) for a, d in w.items() if isinstance(d, dict) for b, v in d.items()},
                     inhalt=dict(hinweis=w['hinweis']))
    return dict(eingang=ein, wahrheit=os.path.join(ausgabe, 'wahrheit'), manifest=zeilen)
