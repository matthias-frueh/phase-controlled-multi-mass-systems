"""AP-13 (Werkzeug 8) als Datenlieferant: synthetische Kalibrier- und Profildaten, Laufzusammenfassungen (Ebene H),
Rohzeitreihen (Ebene Z) und die getrennt abgelegte Wahrheit.

Physik über die vorhandenen Werkzeuge: lineare Summe und 3-FG-Zellkräfte aus `code/auslegung.py` (Klasse Aufbau),
Abgleich der Summe mit `code/linear_solver.py`, ein nichtlinearer Kontaktfall mit dem ereignisgenauen Löser
`code/ereignisloeser.py` (1 FG). AP-11 und AP-12 importieren dieses Paket nicht.
"""
