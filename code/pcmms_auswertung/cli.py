"""Kommandozeile von pcmms_auswertung (AP-11, AP-12, AP-13). Alle Befehle vom Repository-Stamm:

  python3 code/pcmms_auswertung <befehl> [<unterbefehl>] [optionen]     (Hilfe: <befehl> -h)

  beispiel                    kleiner reproduzierbarer Beispieldatensatz der Schnittstelle
  regeln                      Regelprofil als JSON oder Regelmatrix
  generator                   AP-13-Generator: frische Ausgabestruktur eingang/ und getrennt wahrheit/
  ap11 kalibrierung|teil-b    AP-11: Kalibrierung aus P0-Daten; Pilotanalyse und Teil B
  ap12 stufe1|auswerten       AP-12: Rohdaten → Laufzusammenfassungen; Zusammenfassungen → Ergebnis
  harness bewerten|kampagnen|kalibrierung|pruefstand|kriterien|pruefsatz|matrix|neulauf|diagnose-e3b-g4
                              AP-13: Bewertung gegen die Wahrheit, Kampagnen, c-Kalibrierung, gezielte Läufe,
                              Kriterienmatrix, Software-Prüfsatz, Auftragsliste der großen Matrix (ohne Start),
                              gezielte Neuläufe K12/K19/E3 mit Checkpoints und Alt-Neu-Vergleich, Diagnose E3b/G4
  kette                       Generator → AP-11 → (Stufe 1) → Teil B → AP-12 → Bewertung aus einer frischen Struktur

Profil: --profil ID (aktuell AF-2026-11 oder ENTW-2026-11; historisch AF-2026-10 oder ENTW-2026-10) mit
--red name=wert,… (verringerte Replikat- bzw.
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


VERFAHREN = ('statisch', 'zustand', 'historisch')


def _opt_verfahren(ap):
    ap.add_argument('--verfahren', choices=VERFAHREN, default='statisch',
                    help='Phase-0-Bindung und Ablauf der Phase 1: statisch (Bindung an k_max des Plans, Laufplan ohne '
                         'Ablaufentscheidungen; Vorgabe), zustand (Ablauf mit Wiederholungen nach A9.12), historisch '
                         '(Bindung an k der Pilotgrößen wie bis PR #22, nur zur Nachrechnung)')


def _verfahren(a):
    from . import verfahren as vf
    return dict(statisch=vf.STATISCH, zustand=vf.ZUSTAND, historisch=vf.HISTORISCH)[a.verfahren]


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
    ap.add_argument('--profil', default=regeln.STANDARD, choices=sorted(regeln.PROFILE))
    ap.add_argument('--ausgabe', help='Pfad ohne Endung für <pfad>.json')
    ap.add_argument('--matrix', action='store_true', help='Regelmatrix (Markdown) auf die Standardausgabe')
    ap.add_argument('--stand', default='2026-11', choices=('2026-11', '2026-10'),
                    help='Regelstand der Matrix (2026-10: historisch)')
    a = ap.parse_args(argv)
    p = regeln.profil(a.profil)
    if a.matrix:
        sys.stdout.write(regeln.matrix_markdown(a.stand))
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
@befehl('harness', 'AP-13-Harness: bewerten, kampagnen, kalibrierung, pruefstand, kriterien, pruefsatz, '
                   'ablauf-pruefsatz, matrix, neulauf, diagnose-e3b-g4, ablauf-vergleich')
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
    _opt_verfahren(k)
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
    _opt_verfahren(c)
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
    qa = sp.add_parser('ablauf-pruefsatz', help='Prüfsatz des zustandsbehafteten Phase-1-Ablaufs '
                                                '(harness.ablauf_pruefsatz)')
    ga = qa.add_mutually_exclusive_group(required=True)
    ga.add_argument('--schreiben')
    ga.add_argument('--pruefen')
    qa.add_argument('--fassung', default='ablauf-3', choices=('ablauf-3', 'ablauf-4'),
                    help='Stand beim Schreiben: ablauf-3 (historisch, PR #23) oder ablauf-4 (Regelstand 2026-11); '
                         '--pruefen liest den Stand aus der Datei')
    kb = sp.add_parser('kalibrierbeispiel', help='Beispiel der großen Kalibrierung (harness.kalibrierbeispiel): '
                                                 'Vorgabe Trockenlauf; rechnet nur mit --ausfuehren')
    kb.add_argument('--konfig', required=True, help='JSON nach Schema pcmms-kalibrierbeispiel-1')
    kb.add_argument('--ausgabe', default=None, help='Ergebnis- und Checkpointverzeichnis (für --ausfuehren)')
    kb.add_argument('--ausfuehren', action='store_true', help='rechnen (Demonstration; groß nur mit --bestaetigung)')
    kb.add_argument('--bestaetigung', default=None, help='für modus „gross“ genau: "grosse Kalibrierung starten"')
    m = sp.add_parser('matrix')
    m.add_argument('--ausgabe', required=True)
    m.add_argument('--kampagnen', type=int, required=True)
    m.add_argument('--stufen', default='L0,L1,L2,L3,L4,L5')
    m.add_argument('--seed', type=int, required=True)
    n = sp.add_parser('neulauf', help='gezielte Neuläufe nach Auftragsliste (harness.neulauf)')
    n.add_argument('--auftrag', default=None, help='Auftragsliste (Vorgabe: docs/ap13_neulaeufe_2026-10-17/'
                                                    'auftrag.json)')
    n.add_argument('--nur', default=None, help='nur diese Auftrags-IDs, kommagetrennt')
    n.add_argument('--prozesse', type=int, default=None, help='Arbeitsprozesse je Auftrag (Vorgabe: Auftragsliste)')
    n.add_argument('--ausgabe', default=None, help='Checkpoint-Verzeichnis (Vorgabe: Auftragsliste)')
    g = n.add_mutually_exclusive_group()
    g.add_argument('--vorbereiten', default=None, metavar='VOLLSTAENDIGE_AUSGABE',
                   help='Auftragsliste, Werkzeug-8-Dateien und Altstandsauszug aus der vollständigen Ausgabe des '
                        'Altlaufs (Pfad ohne Endung) erzeugen')
    g.add_argument('--bericht', action='store_true', help='Alt-Neu-Vergleich aus den Checkpoints schreiben')
    d = sp.add_parser('diagnose-e3b-g4', help='Diagnose E3b und G4 mit Pilotreserve (harness.diagnose_e3b_g4)')
    d.add_argument('--auftrag', default=None, help='Auftragsliste (Vorgabe: docs/e3b_g4_diagnose_2026-10-17/'
                                                    'auftrag.json)')
    d.add_argument('--nur', default=None, help='nur diese Auftrags-IDs, kommagetrennt')
    d.add_argument('--startsatz', action='store_true', help='nur der Startsatz (je System Kampagnen 0–3, volle Ketten)')
    d.add_argument('--prozesse', type=int, default=None, help='Arbeitsprozesse je Auftrag (Vorgabe: Auftragsliste)')
    d.add_argument('--ausgabe', default=None, help='Checkpoint-Verzeichnis (Vorgabe: Auftragsliste)')
    d.add_argument('--e3-checkpoints', default=None, help='nur mit --vorbereiten: Checkpoints der Neuläufe von PR #21 '
                                                          '(Vorgabe: deren Auftragsliste)')
    gd = d.add_mutually_exclusive_group()
    gd.add_argument('--vorbereiten', default=None, metavar='VOLLSTAENDIGE_AUSGABE',
                    help='Auftragsliste, Werkzeug 8 V1-G60h (aus der vollständigen Ausgabe des Altlaufs, Pfad ohne '
                         'Endung) und E3-Auszug erzeugen')
    gd.add_argument('--bericht', action='store_true', help='Auswertung, kompakte Ergebnisse und Berichtstabellen '
                                                           'aus den Checkpoints schreiben')
    v = sp.add_parser('ablauf-vergleich', help='begrenzte Entwicklungsrechnung zu k-Konsistenz und Wiederholungsablauf '
                                               '(harness.ablauf_vergleich)')
    v.add_argument('--auftrag', default=None, help='Auftragsliste (Vorgabe: docs/ap13_kmax_wiederholungen_2026-10-17/'
                                                    'auftrag.json)')
    v.add_argument('--nur', default=None, help='nur diese Auftrags-IDs, kommagetrennt')
    v.add_argument('--startsatz', action='store_true', help='nur der Startsatz (Seeds 0 und 1 je System und Variante)')
    v.add_argument('--prozesse', type=int, default=None, help='Arbeitsprozesse je Auftrag (Vorgabe: Auftragsliste)')
    v.add_argument('--ausgabe', default=None, help='Checkpoint-Verzeichnis (Vorgabe: Auftragsliste)')
    v.add_argument('--korrektur', action='store_true', help='Korrekturrunde vom 18.10.2026 (eigene Auftragsliste '
                                                            'auftrag_korrektur_2026-10-18.json und Checkpoints)')
    gv = v.add_mutually_exclusive_group()
    gv.add_argument('--vorbereiten', action='store_true', help='Auftragsliste schreiben (vor den Rechnungen committen)')
    gv.add_argument('--bericht', action='store_true', help='Ergebnisse und Berichtstabellen aus den Checkpoints')
    a = ap.parse_args(argv)
    from .harness import dateien, kalibrierung, kampagnen, kriterien, pruefsatz, pruefstand
    if a.was == 'bewerten':
        print(_json(dateien.bewerten(a.ergebnis, a.wahrheit, a.ausgabe)))
    elif a.was == 'kampagnen':
        w8 = dateien.lies_werkzeug8(a.werkzeug8) if a.werkzeug8 != 'testvorgabe' else None
        lauf = kampagnen.ausfuehren(a.szenario, a.stufe, _profil(a), a.kampagnen, a.seed, a.rolle, _plan(a), a.n_min,
                                    w8, prozesse=a.prozesse, verfahren=_verfahren(a))
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
                                       _plan(a), a.n_min, a.prozesse, verfahren=_verfahren(a))
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
    elif a.was == 'ablauf-vergleich':
        from .harness import ablauf_vergleich as av
        pfad = a.auftrag or (av.KORREKTUR_AUFTRAG if a.korrektur else av.AUFTRAG)
        if a.vorbereiten:
            x = av.vorbereiten_korrektur() if a.korrektur else av.vorbereiten()
            print(f'Auftragsliste {pfad}: {len(x["auftraege"])} Aufträge, {x["budget"]}')
        elif a.bericht:
            from .harness import ablauf_vergleich_bericht as avb
            print(_json(avb.schreiben_korrektur(pfad, a.ausgabe) if a.korrektur else avb.schreiben(pfad, a.ausgabe)))
        else:
            nur = a.nur.split(',') if a.nur else None
            if a.startsatz:
                nur = [j['id'] for j in av.lies_auftrag(pfad)['auftraege'] if j['id'].endswith('-start')]
            print(_json(av.ausfuehren(pfad, nur, a.prozesse, a.ausgabe)))
    elif a.was == 'ablauf-pruefsatz':
        from .harness import ablauf_pruefsatz
        if a.schreiben:
            ps = ablauf_pruefsatz.schreiben(a.schreiben, fassung=a.fassung)
            print(f'Ablauf-Prüfsatz {a.schreiben}.json: SHA-256 {ps["sha256_gesamt"][:16]}…')
        else:
            r = ablauf_pruefsatz.pruefen(a.pruefen)
            print(_json(r))
            return 0 if r['gleich'] else 1
    elif a.was == 'kalibrierbeispiel':
        from .harness import kalibrierbeispiel as kb
        k = kb.lies(a.konfig)
        if not a.ausfuehren:
            print(_json(kb.trockenlauf(k)))
            return 0
        if not a.ausgabe:
            print('kalibrierbeispiel --ausfuehren verlangt --ausgabe')
            return 2
        r = kb.ausfuehren(k, a.ausgabe, a.bestaetigung)
        print(_json({x: r[x] for x in ('kennzeichnung', 'status', 'abgeschlossen', 'checkpoints', 'konfiguration_sha256')}))
    elif a.was == 'matrix':
        from .generator import szenarien
        stufen = a.stufen.split(',')
        auftr = [dict(szenario=s, stufe=st, kampagnen=a.kampagnen, seed_basis=a.seed, rolle='pruefung')
                 for s in szenarien.KATALOG for st in stufen]
        sek = 7.5 * a.kampagnen * len(auftr)
        formate.schreibe_objekt(a.ausgabe, formate.kopf('bewertung', formate.synth_kennung('MATRIX', a.seed)),
                                dict(auftraege=auftr, gestartet=False, schaetzung_kernstunden=round(sek / 3600, 1),
                                     hinweis='Auftragsliste der großen Matrix; nicht gestartet (Auftrag Etappe 5). '
                                             'Schätzung mit 7,5 s je Kampagne und Kern (gemessen im Prüfstand: A4, '
                                             'Ebene H, B = 1000; V1-Systeme etwa 10–11 s), ohne Kalibrier- und '
                                             'Prüfsimulationen von c je Stufe'))
        print(f'{len(auftr)} Aufträge × {a.kampagnen} Kampagnen, geschätzt {sek / 3600:.0f} Kernstunden; '
              f'nicht gestartet → {a.ausgabe}.json')
    elif a.was == 'neulauf':
        from .harness import neulauf
        pfad = a.auftrag or neulauf.AUFTRAG
        if a.vorbereiten:
            r = neulauf.vorbereiten(a.vorbereiten)
            print(f'Auftragsliste {pfad}: {len(r["auftraege"])} Aufträge, {r["umfang"]["e3_pruefkampagnen"]} '
                  'E3-Prüfkampagnen; Werkzeug 8 ' + ', '.join(r['werkzeug8']))
        elif a.bericht:
            from .harness import neulauf_vergleich
            z, _ = neulauf_vergleich.schreiben(pfad, a.ausgabe)
            print(f'Alt-Neu-Vergleich: {z["umfang"]}; Laufzeiten {z["laufzeit_s"]}')
        else:
            print(_json(neulauf.ausfuehren(pfad, a.nur.split(',') if a.nur else None, a.prozesse, a.ausgabe)))
    elif a.was == 'diagnose-e3b-g4':
        from .harness import diagnose_e3b_g4 as dg
        pfad = a.auftrag or dg.AUFTRAG
        if a.vorbereiten:
            r = dg.vorbereiten(a.vorbereiten, a.e3_checkpoints)
            print(f'Auftragsliste {pfad}: {len(r["auftraege"])} Aufträge, {r["umfang"]["neue_kampagnen"]} neue '
                  f'Kampagnen, {r["e3"]["n"]} E3-Kampagnen im Auszug; Zielpiloten '
                  + ', '.join(f'{s}: {v["zielpilot"]["phi"]}' for s, v in r['systeme'].items()))
        elif a.bericht:
            from .harness import diagnose_e3b_g4_bericht as db
            z = db.schreiben(pfad, a.ausgabe)
            print(f'Diagnose E3b/G4: {z["umfang"]}')
        else:
            nur = a.nur.split(',') if a.nur else None
            if a.startsatz:
                nur = [j['id'] for j in dg.lies_auftrag(pfad)['auftraege'] if j['voll']]
            print(_json(dg.ausfuehren(pfad, nur, a.prozesse, a.ausgabe)))
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
