"""Start vom Repository-Stamm: python3 code/pcmms_auswertung <befehl> … (oder PYTHONPATH=code python3 -m
pcmms_auswertung <befehl> …)."""
import os
import sys

if __package__ in (None, ''):                                   # als Verzeichnis gestartet
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pcmms_auswertung.cli import main
else:
    from .cli import main

if __name__ == '__main__':
    sys.exit(main())
