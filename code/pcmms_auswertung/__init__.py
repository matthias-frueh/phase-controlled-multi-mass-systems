"""pcmms_auswertung – Anpassverfahren und Pilotanalyse (AP-11, Werkzeuge 4 und 5), Auswertung (AP-12, Werkzeug 6)
und Generator mit Pipelinetest (AP-13, Werkzeug 8) der Präregistrierung v2 (Entwicklungsversion).

Erste Softwarestufe, an synthetischen Daten geprüft; keine Messdaten, keine registrierte Fassung. Aufbau:

  formate, konventionen, regeln, zusammenfassung   Schnittstellen (Etappe 1)
  generator/                                       AP-13 als Datenlieferant (Etappe 2)
  anpassung, pilot                                 AP-11 (Etappe 3)
  stufe1, teil_b, auswertung und Teilmodule         AP-12 Stufe 1 und Stufe 2 (Etappe 4)
  referenz/                                        unabhängige Referenz für H1 und den Zeltfit
  harness/                                         AP-13 Pipelinetest, Kalibrierung, Planung (Etappe 5)

Aufruf vom Repository-Stamm: python3 code/pcmms_auswertung --help (Kommandozeile in cli.py).
Dokumentation: docs/ap11_ap12_ap13_software.md, docs/ap11_ap12_ap13_schnittstellen.md,
docs/ap11_ap12_ap13_regelmatrix.md.
"""
from .formate import PAKET_VERSION as __version__  # noqa: F401
