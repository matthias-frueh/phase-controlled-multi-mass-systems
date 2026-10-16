"""Kommandozeile von pcmms_auswertung (AP-11, AP-12, AP-13). Alle Befehle vom Repository-Stamm:

  python3 code/pcmms_auswertung beispiel --ausgabe DIR        Beispieldatensatz der Schnittstelle
  python3 code/pcmms_auswertung regeln --profil ID [--ausgabe DATEI] [--matrix]
                                                              Regelprofil als JSON bzw. Regelmatrix

Weitere Befehle (Generator, AP-11, AP-12, Harness, Kette) beschreibt docs/ap11_ap12_ap13_software.md.
"""
import argparse
import os
import sys

from . import beispiel, formate, regeln

BEFEHLE = {}


def befehl(name, hilfe):
    def dek(fn):
        BEFEHLE[name] = (fn, hilfe)
        return fn
    return dek


@befehl('beispiel', 'kleiner reproduzierbarer Beispieldatensatz der Schnittstelle')
def _beispiel(ap, argv):
    ap.add_argument('--ausgabe', required=True)
    a = ap.parse_args(argv)
    r = beispiel.erzeugen(a.ausgabe)
    print(f'Beispiel in {a.ausgabe}: {len(r["manifest"])} Rohläufe, Manifest, Kalibrierung, Regelprofil, '
          'Bootstrap-Indizes; Wahrheit getrennt unter wahrheit/')
    for z in r['manifest']:
        print(f'  {z["lauf_id"]}: {z["daten"]} SHA-256 {z["sha256_daten"][:16]}…')
    return 0


@befehl('regeln', 'Regelprofil ausgeben (JSON) oder Regelmatrix drucken')
def _regeln(ap, argv):
    ap.add_argument('--profil', default='ENTW-2026-10', choices=sorted(regeln.PROFILE))
    ap.add_argument('--ausgabe', help='Pfad ohne Endung für <pfad>.json')
    ap.add_argument('--matrix', action='store_true', help='Regelmatrix (Markdown) auf die Standardausgabe')
    a = ap.parse_args(argv)
    p = regeln.profil(a.profil)
    if a.matrix:
        sys.stdout.write(regeln.matrix_markdown())
    if a.ausgabe:
        h = regeln.schreibe_profil(a.ausgabe, p)
        print(f'{a.ausgabe}.json: Profil {p.id}, SHA-256 Inhalt {p.sha256()[:16]}…, Datei {h["json"][:16]}…')
    if not (a.matrix or a.ausgabe):
        k = p.kurz()
        print(f'Profil {p.id}: {len(k["wirksam"])} wirksame Regeln, {len(k["offen"])} offen, '
              f'{len(k["nicht_implementiert"])} nicht implementiert; SHA-256 {k["sha256"][:16]}…')
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ('-h', '--help') or argv[0] not in BEFEHLE:
        print(__doc__.strip())
        print('\nBefehle:')
        for n, (_, h) in sorted(BEFEHLE.items()):
            print(f'  {n:<12} {h}')
        return 0 if (not argv or argv[0] in ('-h', '--help')) else 2
    fn, hilfe = BEFEHLE[argv[0]]
    ap = argparse.ArgumentParser(prog=f'pcmms_auswertung {argv[0]}', description=hilfe)
    try:
        return fn(ap, argv[1:])
    except formate.FormatFehler as e:
        print(f'Formatfehler: {e}', file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())
