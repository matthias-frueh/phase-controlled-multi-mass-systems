# Kurzmessungen zum Plan des Pipelinetests (AP-13)

Stand 02.10.2026 (Skripte und gespeicherte Ausgaben), übernommen 04.10.2026. Grundlage für Abschnitt 4.1 von
[`docs/plan_ap13_pipelinetest.md`](../../docs/plan_ap13_pipelinetest.md). **Nur Planungszahlen** (Laufzeiten,
Plausibilität der Bausteine), keine Registrierungszahlen, keine Messdaten. Laufzeiten wurden auf vier Kernen mit
einem Thread je Prozess gemessen (Python 3.11, numpy 2.4.6, scipy 1.17.1); Wiederholungen streuen um etwa ±20 %.

Start aus diesem Verzeichnis:

```bash
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=../../code python3 <skript>.py
```

| Skript | Inhalt | Ausgabe | Dauer |
|---|---|---|---|
| `ap13_zeit.py` | Bausteine einer synthetischen Kampagne mit den vorhandenen Werkzeugen: Aufbau des V1-Kandidaten (3 FG), Kampagne auf Ebene der Harmonischen (B = 200 und 1000), ein Lauf auf Zeitreihenebene (6,4 kHz) mit Kette A9.4, ereignisgenauer Löser (Kontaktast, Wurf, Hunt-Crossley) | `ap13_zeit_ausgabe.txt` | ≈ 10 s |
| `ap13_zeit_check.py` | Plausibilität: max\|z\| bei exakter Superposition (200 Kampagnen), Zeitreihe ohne Rauschen gegen Harmonische; liest `ap13_zeit.py` | `ap13_zeit_check_ausgabe.txt` | ≈ 15 s |
| `h1_rho_z.py` | Kampagne Ebene H mit Bootstrap A nach A9.5 (ȳ, ρⱼₖ, ŷ je Replikat), n = 20/40/80, B = 1000; Lauf Ebene Z bei 6,4 und 8,5 kHz; liest `ap13_zeit.py` | `h1_rho_z_ausgabe.txt` | ≈ 1 min |
| `zelt_schnell.py` | exakter Zeltfit nach A9.6 (Kandidatenverfahren) gegen das Vollraster mit derselben RSS-Funktion und gegen `m_zelt2.py`; Laufzeiten je 1000 Fits | `zelt_schnell_ausgabe.txt` | ≈ 2 min |
| `m_zelt2.py` | unabhängig geschriebene Vollraster-Fassung des Zeltfits nach A9.6 (Gegenprüfung); wird von `zelt_schnell.py` eingelesen | `m_zelt2_ausgabe.txt` | ≈ 1 min |
| `zelt_gleichstand.py` | die 571 Abweichungen zwischen Kandidatenverfahren und unabhängiger Fassung mit explizitem `lstsq` nachgerechnet; importiert `zelt_schnell` | `zelt_gleichstand_ausgabe.txt` | ≈ 1 min |
| `h2_kampagne.py` | H2-Kampagne nach A9.6 auf Ebene H (V1-G0, L2, B = 1000, drei Fits je Replikat, Jackknife für BCa, Vollraster zum Vergleich); importiert `zelt_schnell` | `h2_kampagne_ausgabe.txt` | ≈ 2 min |
| `s4_kopie.py a:45,50,55` | Kopie von [`../statistik/s4_identifizierbarkeit.py`](../statistik/s4_identifizierbarkeit.py) mit reinem Hertz-Kontakt bei f_n0 = 45, 50 und 55 Hz (Stressszenario A07) | `hertz_45.txt`, `hertz_50.txt`, `hertz_55.txt`, `s4_identifizierbarkeit_hertz_*.csv` | Minuten |

Abhängigkeiten: `code/auslegung.py`, `code/ereignisloeser.py`, `code/linear_solver.py`, `code/finesweep.py`; numpy,
scipy, pandas. Reihenfolge: `m_zelt2.py` und `zelt_schnell.py` liegen für `zelt_gleichstand.py` und `h2_kampagne.py`
im selben Verzeichnis; `ap13_zeit.py` wird von `ap13_zeit_check.py` und `h1_rho_z.py` eingelesen.

Übernahme: Pfade auf dieses Verzeichnis umgestellt (vorher getrennte Ordner), Umgebungsbegriffe in Docstrings ersetzt;
Rechenweg und Zahlen unverändert. In `zelt_schnell_ausgabe.txt` ist in einer Warnzeile der damalige absolute Pfad durch
den Dateinamen ersetzt. Code-Stand der Werkzeuge bei der Messung: 02./03.10.2026, vor PR #14 (`auslegung.py` rechnete
PB1 noch nach der Fassung vom 25.09.2026; Laufzeiten davon unberührt).

Grenzen: Die Zahlen dienen der Budgetplanung von Werkzeug 8, nicht der Kalibrierung; Rauschmodelle sind Annahmen
(Stufen L0–L5 wie in [`../statistik/`](../statistik/PROTOKOLL.md)).
