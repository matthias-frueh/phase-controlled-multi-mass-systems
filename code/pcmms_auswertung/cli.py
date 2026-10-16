"""Kommandozeile von pcmms_auswertung (AP-11, AP-12, AP-13). Alle Befehle vom Repository-Stamm:

  python3 code/pcmms_auswertung <befehl> [<unterbefehl>] [optionen]     (Hilfe: <befehl> -h)

  beispiel                    kleiner reproduzierbarer Beispieldatensatz der Schnittstelle
  regeln                      Regelprofil als JSON oder Regelmatrix
  generator                   AP-13-Generator: frische Ausgabestruktur eingang/ und getrennt wahrheit/
  ap11 kalibrierung|teil-b    AP-11: Kalibrierung aus P0-Daten; Pilotanalyse und Teil B
  ap12 stufe1|auswerten       AP-12: Rohdaten → Laufzusammenfassungen; Zusammenfassungen → Ergebnis
  harness bewerten|kampagnen|kalibrierung|pruefstand|kriterien|pruefsatz|matrix
                              AP-13: Bewertung gegen die Wahrheit, Kampagnen, c-Kalibrierung, gezielte Läufe,
                              Kriterienmatrix, Software-Prüfsatz, Auftragsliste der großen Matrix (ohne Start)
  kette                       Generator → AP-11 → (Stufe 1) → Teil B → AP-12 → Bewertung aus einer frischen Struktur

Profil: --profil ID (AF-2026-10 oder ENTW-2026-10) mit --red name=wert,… (verringerte Replikat- bzw.
Kampagnenzahlen; die Reduktion steht in der Profilkennung und in jedem Ergebnis) oder --profil-datei PFAD.
Beispiele und Laufzeiten: docs/ap11_ap12_ap13_software.md.
"""
import argparse
import json
import os
import sys

from . import beispiel, formate, regeln

BEFEHLE = {}


def befehl(name, hilfe):
    def dek(fn):
        BEFEHLE[name] = (fn, hilfe)
        return fn
    return dek


# ── gemeinsame Optionen ──────────────────────────────────────────────────────────────────────────────
def _opt_profil(ap):
    ap.add_argument('--profil', default=None, choices=sorted(regeln.PROFILE),
                    help='Regelprofil (ohne Angabe: --profil-datei nötig)')
    ap.add_argument('--red', default='', help='Reduktion name=wert,… (z. B. bootstrap_B=200,h3_mc=1000)')
    ap.add_argument('--profil-datei', default=None, help='gespeichertes Profil (regeln --ausgabe)')


def _profil(a):
    if a.profil_datei:
        return regeln.lade_profil(a.profil_datei)
    if not a.profil:
        raise SystemExit('Regelprofil fehlt: --profil ID oder --profil-datei PFAD (kein stiller Vorgabewert)')
    p = regeln.profil(a.profil)
    if a.red:
        red = {}
        for teil in a.red.split(','):
            k, v = teil.split('=')
            red[k.strip()] = int(v)
        p = p.mit_reduktion(**red)
    return p


def _opt_plan(ap):
    ap.add_argument('--n0', type=int, default=20, help='Einzelmodulläufe je Modul in Phase 0 (P0.8)')
    ap.add_argument('--n-pilot', type=int, default=20, help='Läufe je Pilotkonfiguration')
    ap.add_argument('--n-bloecke', type=int, default=24, help='Blöcke n in Phase 1')
    ap.add_argument('--n-zyklen', type=int, default=100, help='Zyklen im Auswertefenster')
    ap.add_argument('--n-min', type=int, default=None, help='n_min für Teil B (Vorgabe: n − 2)')


def _plan(a):
    from .generator import kampagne
    return kampagne.Plan(n0=a.n0, n_pilot=a.n_pilot, n_bloecke=a.n_bloecke, n_zyklen=a.n_zyklen)


def _json(obj):
    return formate.json_text(obj)


# ── Bestand ──────────────────────────────────────────────────────────────────────────────────────────
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


# ── Generator ────────────────────────────────────────────────────────────────────────────────────────
@befehl('generator', 'AP-13-Generator: P0-Daten, Rohläufe (Z) oder Zusammenfassungen (H), Wahrheit getrennt')
def _generator(ap, argv):
    ap.add_argument('--szenario', required=True)
    ap.add_argument('--stufe', required=True, help='Präzisionsstufe L0–L5')
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--ebene', choices=('Z', 'H'), required=True)
    ap.add_argument('--ausgabe', required=True, help='frisches Zielverzeichnis')
    _opt_plan(ap)
    a = ap.parse_args(argv)
    from .harness import dateien
    p = dateien.generator_schreiben(a.ausgabe, a.szenario, a.stufe, _plan(a), a.seed, a.ebene, a.n_min)
    print(f'Generator {a.szenario} {a.stufe} Seed {a.seed} Ebene {a.ebene}: eingang/ unter {p["eingang"]}, '
          f'Wahrheit getrennt unter {p["wahrheit_dir"]}')
    return 0


# ── AP-11 ────────────────────────────────────────────────────────────────────────────────────────────
@befehl('ap11', 'AP-11: kalibrierung (P0.1/P0.2/P0.4/P0.5) oder teil-b (Pilotanalyse und Teil B)')
def _ap11(ap, argv):
    sp = ap.add_subparsers(dest='was', required=True)
    k = sp.add_parser('kalibrierung')
    k.add_argument('--p0', required=True)
    k.add_argument('--band', type=float, nargs=2, required=True, metavar=('F_UNTEN', 'F_OBEN'),
                   help='Anpassungsband der 1-FG-Anpassung in Hz (Regel p0.4.band: Eingabe, kein Vorgabewert)')
    k.add_argument('--ausgabe', required=True)
    t = sp.add_parser('teil-b')
    t.add_argument('--zusammenfassungen', required=True)
    t.add_argument('--kalibrierung', required=True)
    t.add_argument('--planangaben', required=True)
    t.add_argument('--werkzeug8', required=True, help='Datei aus „harness kalibrierung“ oder „testvorgabe“')
    t.add_argument('--ausgabe', required=True)
    t.add_argument('--pilot', required=True, help='Ausgabepfad der Pilotgrößen')
    _opt_profil(t)
    a = ap.parse_args(argv)
    from .harness import dateien
    if a.was == 'kalibrierung':
        kal = dateien.ap11_kalibrierung(a.p0, a.ausgabe, a.band)
        p04 = kal['p0_4']
        print(f'Kalibrierung {a.ausgabe}: f₁ = {p04.get("f_1_hz")} Hz, Moden {len(p04.get("moden", []))}, '
              f'Δδ = {kal["p0_5"]["delta_delta_grad"]}°')
    else:
        tb = dateien.ap11_teil_b(a.zusammenfassungen, a.kalibrierung, a.planangaben, _profil(a), a.werkzeug8,
                                 a.ausgabe, a.pilot)
        print(f'Teil B {a.ausgabe}: k_max = {tb["nr2"]["k_max"]}, n_min = {tb["nr2"]["n_min"]}, c_H1 = '
              f'{tb["nr10"]["c_H1"]} ({tb["nr10"]["c_H1_herkunft"]})')
    return 0


# ── AP-12 ────────────────────────────────────────────────────────────────────────────────────────────
@befehl('ap12', 'AP-12: stufe1 (Rohläufe → Zusammenfassungen) oder auswerten (Zusammenfassungen → Ergebnis)')
def _ap12(ap, argv):
    sp = ap.add_subparsers(dest='was', required=True)
    s = sp.add_parser('stufe1')
    s.add_argument('--manifest', required=True)
    s.add_argument('--kalibrierung', required=True)
    s.add_argument('--ausgabe', required=True)
    e = sp.add_parser('auswerten')
    e.add_argument('--zusammenfassungen', required=True)
    e.add_argument('--kalibrierung', required=True)
    e.add_argument('--teil-b', required=True)
    e.add_argument('--ausgabe', required=True)
    e.add_argument('--seed', type=int, default=None, help='Bootstrap-Seed (Vorgabe: Teil B)')
    _opt_profil(e)
    a = ap.parse_args(argv)
    from .harness import dateien
    if a.was == 'stufe1':
        tab = dateien.ap12_stufe1(a.manifest, a.kalibrierung, a.ausgabe)
        print(f'Stufe 1: {len(tab)} Laufzusammenfassungen → {a.ausgabe}')
    else:
        from . import auswertung
        erg = auswertung.auswerten(a.zusammenfassungen, a.kalibrierung, a.teil_b, _profil(a), seed=a.seed)
        auswertung.schreibe_ergebnis(a.ausgabe, erg, erg['herkunft']['kennung'] or formate.synth_kennung('ERGEBNIS'))
        print(erg['text'])
    return 0


# ── Harness ──────────────────────────────────────────────────────────────────────────────────────────
@befehl('harness', 'AP-13-Harness: bewerten, kampagnen, kalibrierung, pruefstand, kriterien, pruefsatz, matrix')
def _harness(ap, argv):
    sp = ap.add_subparsers(dest='was', required=True)
    b = sp.add_parser('bewerten')
    b.add_argument('--ergebnis', required=True)
    b.add_argument('--wahrheit', required=True)
    b.add_argument('--ausgabe', default=None)
    k = sp.add_parser('kampagnen')
    k.add_argument('--szenario', required=True)
    k.add_argument('--stufe', required=True)
    k.add_argument('--kampagnen', type=int, required=True)
    k.add_argument('--seed', type=int, required=True)
    k.add_argument('--ausgabe', required=True)
    k.add_argument('--prozesse', type=int, default=1)
    k.add_argument('--werkzeug8', default='testvorgabe')
    k.add_argument('--rolle', default='pruefung')
    _opt_profil(k)
    _opt_plan(k)
    c = sp.add_parser('kalibrierung')
    c.add_argument('--szenario', required=True, help='Szenario mit exakter Superposition (N01 …)')
    c.add_argument('--stufe', required=True)
    c.add_argument('--kampagnen-kal', type=int, required=True)
    c.add_argument('--kampagnen-pruef', type=int, required=True)
    c.add_argument('--seed', type=int, required=True)
    c.add_argument('--ausgabe', required=True)
    c.add_argument('--prozesse', type=int, default=1)
    _opt_profil(c)
    _opt_plan(c)
    p = sp.add_parser('pruefstand')
    p.add_argument('--ausgabe', required=True)
    p.add_argument('--schritte', default=None, help='Auswahl, kommagetrennt (Vorgabe: alle)')
    p.add_argument('--konfiguration', default=None, help='JSON mit Abweichungen von harness.pruefstand.STANDARD')
    p.add_argument('--prozesse', type=int, default=4)
    r = sp.add_parser('kriterien')
    r.add_argument('--pruefstand', required=True)
    r.add_argument('--ausgabe', required=True, help='Markdown-Datei')
    r.add_argument('--kompakt', default=None, help='zusätzlich kompakte JSON-Zusammenfassung (Pfad ohne Endung)')
    q = sp.add_parser('pruefsatz')
    g = q.add_mutually_exclusive_group(required=True)
    g.add_argument('--schreiben')
    g.add_argument('--pruefen')
    m = sp.add_parser('matrix')
    m.add_argument('--ausgabe', required=True)
    m.add_argument('--kampagnen', type=int, required=True)
    m.add_argument('--stufen', default='L0,L1,L2,L3,L4,L5')
    m.add_argument('--seed', type=int, required=True)
    a = ap.parse_args(argv)
    from .harness import dateien, kalibrierung, kampagnen, kriterien, pruefsatz, pruefstand
    if a.was == 'bewerten':
        print(_json(dateien.bewerten(a.ergebnis, a.wahrheit, a.ausgabe)))
    elif a.was == 'kampagnen':
        w8 = dateien.lies_werkzeug8(a.werkzeug8) if a.werkzeug8 != 'testvorgabe' else None
        lauf = kampagnen.ausfuehren(a.szenario, a.stufe, _profil(a), a.kampagnen, a.seed, a.rolle, _plan(a), a.n_min,
                                    w8, prozesse=a.prozesse)
        pf = kampagnen.schreibe(a.ausgabe, lauf)
        rt = kampagnen.raten(lauf)
        print(f'{a.kampagnen} Kampagnen {a.szenario} {a.stufe} ({lauf["meta"]["laufzeit_s"]} s); Wahrheit '
              f'{rt["wahrheit"]["klasse"]}; {pf["csv"]}')
        for n, x in rt['raten'].items():
            if x['zaehler']:
                print(f'  {n}: {x["rate"]:.3f} ± {x["mc_se"]:.3f} ({x["zaehler"]}/{x["nenner"]})')
    elif a.was == 'kalibrierung':
        prof = _profil(a)
        kal = kalibrierung.kalibrieren(a.szenario, a.stufe, prof, a.kampagnen_kal, a.kampagnen_pruef, a.seed,
                                       _plan(a), a.n_min, a.prozesse)
        os.makedirs(a.ausgabe, exist_ok=True)
        kenn = formate.synth_kennung('W8', a.szenario, a.stufe, a.seed)
        formate.schreibe_objekt(os.path.join(a.ausgabe, 'werkzeug8'), formate.kopf('werkzeug8', kenn),
                                kal['werkzeug8'])
        formate.schreibe_objekt(os.path.join(a.ausgabe, 'kalibrierung_c'), formate.kopf('bewertung', kenn),
                                pruefstand._kurz_kal(kal))
        pr = kal['pruefung'] or {}
        print(f'c_H1 = {kal["c_H1"]["wert"]} ± {kal["c_H1"]["se"]} (c_B = {kal["c_H1"]["c_B"]:.4f}), Prüfrate '
              f'{pr.get("rate")} ± {pr.get("mc_se")} ({pr.get("zaehler")}/{pr.get("nenner")}), gepoolt '
              f'{kal["gepoolt"]}; H2-Intervall {kal["h2"].get("schluessel")}; P(H1 und H2 bestätigt) = '
              f'{kal["gemeinsame_bestaetigung"]["rate"]:.3f} ± {kal["gemeinsame_bestaetigung"]["mc_se"]:.3f}')
        print(f'  {kal["meta"]["lesart"]}; Werkzeug-8-Datei {os.path.join(a.ausgabe, "werkzeug8")}.json')
    elif a.was == 'pruefstand':
        kf = json.loads(a.konfiguration) if a.konfiguration else None
        out = pruefstand.ausfuehren(a.ausgabe, kf, a.schritte.split(',') if a.schritte else None, a.prozesse)
        print(f'Prüfstand {a.ausgabe}/pruefstand.json: Schritte {list(out["schritte"])}; Laufzeiten {out["laufzeit_s"]}')
    elif a.was == 'kriterien':
        _, ps = formate.lies_objekt(a.pruefstand, 'bewertung')
        z = kriterien.bewerten(ps)
        kopf = (f'Kriterienmatrix aus {os.path.basename(a.pruefstand)} (Profil {ps["profil"]}, Code '
                f'{ps["code_version"]["git"]})')
        with open(a.ausgabe, 'w', encoding='utf-8') as f:
            f.write(kriterien.markdown(z, kopf))
        if a.kompakt:
            formate.schreibe_objekt(a.kompakt, formate.kopf('bewertung', formate.synth_kennung('PRUEFSTAND-KOMPAKT')),
                                    pruefstand.kompakt(ps))
        print(f'{a.ausgabe}: ' + ', '.join(f'{k}: {v}' for k, v in kriterien.zaehlung(z).items()))
    elif a.was == 'pruefsatz':
        if a.schreiben:
            ps = pruefsatz.schreiben(a.schreiben)
            print(f'Prüfsatz {a.schreiben}.json: SHA-256 {ps["sha256_gesamt"][:16]}…')
        else:
            r = pruefsatz.pruefen(a.pruefen)
            print(_json(r))
            return 0 if r['gleich'] else 1
    elif a.was == 'matrix':
        from .generator import szenarien
        stufen = a.stufen.split(',')
        auftr = [dict(szenario=s, stufe=st, kampagnen=a.kampagnen, seed_basis=a.seed, rolle='pruefung')
                 for s in szenarien.KATALOG for st in stufen]
        sek = 5.0 * a.kampagnen * len(auftr)
        formate.schreibe_objekt(a.ausgabe, formate.kopf('bewertung', formate.synth_kennung('MATRIX', a.seed)),
                                dict(auftraege=auftr, gestartet=False, schaetzung_kernstunden=round(sek / 3600, 1),
                                     hinweis='Auftragsliste der großen Matrix; nicht gestartet (Auftrag Etappe 5). '
                                             'Schätzung mit 5 s je Kampagne (B = 1000, Ebene H, A4), ohne '
                                             'Kalibrier- und Prüfsimulationen von c je Stufe'))
        print(f'{len(auftr)} Aufträge × {a.kampagnen} Kampagnen, geschätzt {sek / 3600:.0f} Kernstunden; '
              f'nicht gestartet → {a.ausgabe}.json')
    return 0


# ── Kette ────────────────────────────────────────────────────────────────────────────────────────────
@befehl('kette', 'eine Kampagne aus einer frischen Ausgabestruktur vollständig auswerten (Dateien)')
def _kette(ap, argv):
    ap.add_argument('--szenario', required=True)
    ap.add_argument('--stufe', required=True)
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--ebene', choices=('Z', 'H'), required=True)
    ap.add_argument('--ausgabe', required=True)
    ap.add_argument('--werkzeug8', default='testvorgabe')
    ap.add_argument('--band', type=float, nargs=2, required=True, metavar=('F_UNTEN', 'F_OBEN'),
                    help='Anpassungsband der 1-FG-Anpassung in AP-11, Hz (Regel p0.4.band: Eingabe; '
                         'Entwicklungsläufe: 20 600)')
    _opt_profil(ap)
    _opt_plan(ap)
    a = ap.parse_args(argv)
    from .harness import dateien
    r = dateien.kette_dateien(a.ausgabe, a.szenario, a.stufe, _profil(a), _plan(a), a.seed, a.ebene, a.n_min,
                              a.werkzeug8, a.band)
    print(r['ergebnis']['text'])
    bw = r['bewertung']
    print(f'Wahrheit: Klasse {bw["klasse"]} (r_max/Δ_rel = {bw["r_max_rel"]:.3g}); Erwartung: {bw["erwartung"]}')
    print(f'Dateien unter {a.ausgabe}: eingang/, ergebnis/, wahrheit/')
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
