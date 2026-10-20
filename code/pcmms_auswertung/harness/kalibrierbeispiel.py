"""Kalibrierbeispiel (Auftrag vom 20.10.2026, Abschnitt 9): startfreies, ausführbares Beispiel der normativen
Kalibrier- und Prüfsimulation (Präreg §8.4, §8.6, A9.11) mit der echten API: harness.kalibrierung.kalibrieren mit den
Mengen G und A, Nachziehen bis |A| = soll_A mit technischem Versuchslimit, Prüfrate und Pool-Regel, H2-Auswahl,
E3-Kriterien, Reservebedingung und Zeitbilanz. Es gibt keinen zweiten Kalibrieralgorithmus; das Beispiel ersetzt nur
den Kampagnenlauf durch einen mit Checkpoints je Partie.

Betriebsarten:
- trockenlauf (Vorgabe): Konfiguration lesen und prüfen, Auftragsliste mit Seeds, Profil-, Verfahrens-, Plan- und
  Modellstände, Kostenabschätzung. Es wird keine Kampagne gerechnet.
- demonstration: sehr kleiner Funktionstest (Konfiguration mit "modus": "demonstration", wenige Kampagnen und
  reduzierte Replikate). Alle Ausgaben tragen dauerhaft KENNZEICHNUNG_DEMO; sie sind nie Werte für ein Teil B.
- gross: die normative Rechnung. Sie verlangt ausdrücklich bestaetigung=BESTAETIGUNG und eine Konfiguration mit
  "modus": "gross". Im Auftrag vom 20.10.2026 wird sie nicht aufgerufen (Ressourcenentscheidung des Autors).

Sicherungen: Ein Ausgabeverzeichnis mit Ergebnissen oder Checkpoints einer anderen Konfiguration wird nicht
überschrieben; Checkpoints mit anderem Schlüssel (Profil, Plan, Verfahren, Szenario, Seeds, Werkzeug-8-Eingang,
Codestand) werden abgelehnt, nicht vermischt. Es werden keine weiteren Systeme oder Diagnosen automatisch gestartet.
"""
import json
import math
import os

from .. import formate, regeln, verfahren as vf
from ..generator import kampagne as kp, szenarien
from . import kalibrierung, kampagnen as kpn

SCHEMA = 'pcmms-kalibrierbeispiel-1'
KENNZEICHNUNG_DEMO = 'Demonstration, synthetisch, nicht kalibriert'
KENNZEICHNUNG_GROSS = 'normative Kalibrier- und Prüfsimulation (synthetisch; Abnahme nur bei abgeschlossenem |A|)'
BESTAETIGUNG = 'grosse Kalibrierung starten'
MODI = ('demonstration', 'gross')
PFLICHT = ('schema', 'modus', 'szenario', 'stufe', 'profil', 'plan', 'n_min', 'verfahren', 'seed_basis', 'soll_A',
           'prozesse', 'partie')
# Größengrenzen der Demonstration (oberhalb davon ist es keine Demonstration): Kampagnen, Plan (Phase-0-Laufzahlen
# einschließlich der Referenzläufe, Blöcke, Messtage, Fensterlänge, keine Zusatz-, Prüf- oder Einstellung-2-
# Konfigurationen) und Replikate; ref_abstand nach unten begrenzt (kleinere Abstände bedeuten mehr Referenzläufe)
DEMO_GRENZEN = dict(soll_A=5, n_bloecke=4, n0=20, n_pilot=20, ref_min_p0=42, n_zyklen=100, tage=2, bootstrap_B=200,
                    h2_replikate=200, h3_mc=200, e3_mc=200, eps_ctrl_datensaetze=300)
DEMO_UNTERGRENZEN = dict(ref_abstand=12)
DEMO_PLAN_AUS = ('zusatz', 'pruef', 'einstellung2')                 # in der Demonstration nicht erlaubt
# Vorgabe der Kostenabschätzung je Modus: Demonstration mit reduzierten Replikaten (PR #23: 5–8 s je Kampagne bei
# B = 1000); große Rechnung mit den normativen Replikatzahlen (B = 10 000): 82 s je Kampagne nach dem Belegpaket der
# Entscheidungsvorlage (A4: 45,5 Kernstunden für 1000 + 1000 Kampagnen; Softwaredoku §5: 78 s bei n = 20)
SEKUNDEN_JE_KAMPAGNE = dict(demonstration=7.5, gross=82.0)


class BeispielFehler(ValueError):
    pass


def lies(pfad):
    with open(pfad, encoding='utf-8') as f:
        k = json.load(f)
    return pruefen(k)


def pruefen(k):
    """Konfiguration prüfen; Rückgabe mit aufgelöstem Profil, Plan und Verfahren (Schlüssel _profil, _plan, …)."""
    fehl = [x for x in PFLICHT if x not in k]
    if fehl:
        raise BeispielFehler(f'Konfiguration: Felder fehlen: {fehl}')
    if k['schema'] != SCHEMA:
        raise BeispielFehler(f'Konfiguration: Schema {k["schema"]!r} statt {SCHEMA!r}')
    if k['modus'] not in MODI:
        raise BeispielFehler(f'Konfiguration: modus {k["modus"]!r} ({", ".join(MODI)})')
    if k['szenario'] not in szenarien.KATALOG:
        raise BeispielFehler(f'Konfiguration: Szenario {k["szenario"]!r} nicht im Katalog')
    prof = regeln.profil(k['profil'])
    if regeln.ist_historisch(prof):
        raise BeispielFehler('Konfiguration: historisches Profil; das Beispiel verlangt den Regelstand 2026-11')
    red = dict(k.get('reduktion') or {})
    if red:
        prof = prof.mit_reduktion(**red)
    try:
        plan = kp.plan_aus_dict(dict(k['plan'], p0_anordnung=k['plan'].get('p0_anordnung', 'p07')))
    except (TypeError, ValueError) as e:
        raise BeispielFehler(f'Konfiguration: Plan ungültig ({e})') from None
    if k['verfahren'] not in ('zustand', 'statisch'):
        raise BeispielFehler('Konfiguration: verfahren „zustand“ (ablauf-4) oder „statisch“')
    v = vf.ZUSTAND if k['verfahren'] == 'zustand' else vf.STATISCH
    if not 1 <= int(k['prozesse']) <= 4:
        raise BeispielFehler('Konfiguration: 1 bis 4 Prozesse (Arbeitsvorgabe: höchstens vier, je ein BLAS-Thread)')
    if int(k['partie']) < 1 or int(k['soll_A']) < 1:
        raise BeispielFehler('Konfiguration: partie ≥ 1 und soll_A ≥ 1')
    if int(k['n_min']) < 1 or int(k['n_min']) > plan.n_bloecke:
        raise BeispielFehler(f'Konfiguration: 1 ≤ n_min ≤ n_bloecke ({k["n_min"]}, {plan.n_bloecke})')
    if k['modus'] == 'demonstration':
        werte = dict(soll_A=int(k['soll_A']), **{x: getattr(plan, x) for x in ('n_bloecke', 'n0', 'n_pilot',
                                                                                 'ref_min_p0', 'n_zyklen', 'tage')},
                     **{x: prof.zahl(x) for x in ('bootstrap_B', 'h2_replikate', 'h3_mc', 'e3_mc',
                                                  'eps_ctrl_datensaetze')})
        zu_gross = [f'{x} = {v}' for x, v in werte.items() if not 1 <= int(v) <= DEMO_GRENZEN[x]]
        zu_gross += [f'{x} = {getattr(plan, x)}' for x, u in DEMO_UNTERGRENZEN.items() if getattr(plan, x) < u]
        zu_gross += [f'{x} = {getattr(plan, x)!r}' for x in DEMO_PLAN_AUS if getattr(plan, x)]
        if zu_gross:
            raise BeispielFehler(f'Demonstration zu groß ({", ".join(zu_gross)}; Grenzen {DEMO_GRENZEN}, '
                                 f'mindestens {DEMO_UNTERGRENZEN}, ohne {", ".join(DEMO_PLAN_AUS)})')
    else:
        if int(k['soll_A']) != regeln.NORMATIVE_ZAHLEN['kampagnen_kalibrierung'] or prof.reduziert:
            raise BeispielFehler('modus „gross“: soll_A = 1000 und keine Reduktion (sonst ist es keine normative '
                                 'Kalibrierung; niedrigere Sollzahlen ersetzen die Abnahme nicht)')
    out = dict(k, _profil=prof, _plan=plan, _verfahren=v)
    return out


def _schluessel(k, rolle, variante):
    """Identität eines Kampagnenlaufs ohne den Werkzeug-8-Eingang (die Pool-Neuberechnung der Prüfung läuft mit
    denselben Seeds und anderen Werten; sie steht daneben, nicht an ihrer Stelle)."""
    return formate.sha256_json(dict(szenario=k['szenario'], stufe=k['stufe'], profil=k['_profil'].sha256(),
                                    plan=kp.plan_dict(k['_plan']), n_min=k['n_min'],
                                    verfahren=k['_verfahren'].kennung(), seed_basis=k['seed_basis'], rolle=rolle,
                                    variante=variante, code=formate.code_version()))


def konfig_sha(k):
    return formate.sha256_json({x: k[x] for x in PFLICHT + ('reduktion',) if x in k})


def auftragsliste(k):
    """Rollen, Seeds der ersten Partien und Versuchslimit je Rolle (die Kalibrierung zieht nach, bis |A| = soll_A)."""
    soll = int(k['soll_A'])
    limit = int(math.ceil(float(k['_profil'].wert('harness.nachziehen')['versuchslimit_faktor']) * soll))
    rollen = []
    for rolle in ('kalibrierung_c', 'pruefung_c'):
        seeds = [kpn.kampagnen_seed(k['seed_basis'], rolle, k['szenario'], k['stufe'], i) for i in range(min(soll, 5))]
        rollen.append(dict(rolle=rolle, soll_A=soll, versuchslimit=limit, erste_seeds=seeds, partie=int(k['partie']),
                           hinweis='Seeds fortlaufend nach Index; Nachziehen setzt die Folge fort'))
    rollen.append(dict(rolle='pruefung_c (Pool-Neuberechnung)', bedingt='nur wenn die Prüfrate 0,069 übersteigt',
                       soll_A=soll, versuchslimit=limit))
    return rollen


def kosten(k, sekunden=None):
    s = float(sekunden or k.get('sekunden_je_kampagne') or SEKUNDEN_JE_KAMPAGNE[k['modus']])
    soll = int(k['soll_A'])
    limit = int(math.ceil(float(k['_profil'].wert('harness.nachziehen')['versuchslimit_faktor']) * soll))
    n_min, n_max = 2 * soll, 3 * limit                              # ohne bzw. mit Pool-Neuberechnung und Limit
    return dict(kampagnen_min=n_min, kampagnen_max=n_max, sekunden_je_kampagne=s,
                kernstunden_min=round(n_min * s / 3600, 2), kernstunden_max=round(n_max * s / 3600, 2),
                wandstunden_min=round(n_min * s / 3600 / int(k['prozesse']), 2),
                wandstunden_max=round(n_max * s / 3600 / int(k['prozesse']), 2),
                hinweis='Schätzung aus der Laufzeit je Kampagne; vor einer großen Rechnung mit einer kleinen '
                        'Laufzeitprobe ersetzen')


def trockenlauf(k):
    """Alles außer Rechnen: geprüfte Konfiguration, Stände, Auftragsliste, Kosten. Startet keine Kampagne."""
    prof, plan, v = k['_profil'], k['_plan'], k['_verfahren']
    return dict(betriebsart='trockenlauf', kennzeichnung=KENNZEICHNUNG_DEMO if k['modus'] == 'demonstration'
                else KENNZEICHNUNG_GROSS, gerechnet=False, konfiguration_sha256=konfig_sha(k),
                profil=dict(id=prof.id, sha256=prof.sha256(), stand=regeln.stand(prof)),
                verfahren=v.kennung(), plan=kp.plan_dict(plan),
                modell=dict(szenario=k['szenario'], stufe=k['stufe'], rauschmodell='Szenario (Katalog)',
                            hinweis='Planungs- und Kalibriermodell aus Phase 0 siehe harness.planung (Teil d)'),
                code_version=formate.code_version(), auftragsliste=auftragsliste(k), kosten=kosten(k),
                ausfuehrung=('python3 -m pcmms_auswertung.cli harness kalibrierbeispiel --konfig <datei> --ausfuehren '
                             '--ausgabe <leeres Verzeichnis>'
                             + ('' if k['modus'] == 'demonstration' else f' --bestaetigung "{BESTAETIGUNG}"')))


class Checkpoints:
    """Kampagnenlauf mit Checkpoints je Partie (Ersatz für kampagnen.ausfuehren, gleiche Signatur und Rückgabe)."""

    def __init__(self, k, verzeichnis):
        self.k, self.dir = k, os.path.join(verzeichnis, 'checkpoints')
        os.makedirs(self.dir, exist_ok=True)
        self.geladen, self.gerechnet = 0, 0

    def __call__(self, sid, stufe, profil, n, seed_basis, rolle='pruefung', plan=None, n_min=None, werkzeug8=None,
                 rausch=None, start=0, **kw):
        variante = 'Szenario' if rausch is None else rausch.name
        basis = _schluessel(self.k, rolle, variante)
        w8 = 'ohne' if werkzeug8 is None else formate.sha256_json(werkzeug8)[:10]
        key = f'{basis}/{w8}'
        p = int(self.k['partie'])
        teile = []
        for s in range(start, start + n, p):
            m = min(p, start + n - s)
            pfad = os.path.join(self.dir, f'{rolle}_{basis[:12]}_{w8}_{s:06d}_{m:04d}')
            andere = [f for f in os.listdir(self.dir) if f.startswith(f'{rolle}_') and f'_{s:06d}_' in f
                      and not f.startswith(f'{rolle}_{basis[:12]}_')]
            if andere:
                raise BeispielFehler(f'inkompatibler Checkpoint {andere[0]} (anderer Schlüssel): nicht vermischt')
            if os.path.exists(pfad + '.json'):
                _, lauf = formate.lies_objekt(pfad, 'bewertung')
                if lauf['meta'].get('checkpoint_schluessel') != key:
                    raise BeispielFehler(f'Checkpoint {pfad}: Schlüssel passt nicht')
                self.geladen += 1
            else:
                lauf = kpn.ausfuehren(sid, stufe, profil, m, seed_basis, rolle, plan, n_min, werkzeug8, rausch,
                                      start=s, **kw)
                lauf['meta']['checkpoint_schluessel'] = key
                formate.schreibe_objekt(pfad, formate.kopf('bewertung', formate.synth_kennung('KALBSP', rolle, s)),
                                        lauf)
                self.gerechnet += 1
            teile.append(lauf)
        meta = dict(teile[0]['meta'], n=n, seeds=[x for t in teile for x in t['meta']['seeds']],
                    laufzeit_s=round(sum(t['meta']['laufzeit_s'] for t in teile), 2), partien=len(teile))
        if start:
            meta['start'] = int(start)
        return dict(teile[0], meta=meta, befunde=[b for t in teile for b in t['befunde']])


def ausfuehren(k, verzeichnis, bestaetigung=None):
    """Rechnet die Kalibrierung mit Checkpoints. Demonstration: nur mit modus „demonstration“; groß: nur mit
    bestaetigung == BESTAETIGUNG. Rückgabe des Ergebnisses (auch als ergebnis.json im Verzeichnis)."""
    if k['modus'] == 'gross' and bestaetigung != BESTAETIGUNG:
        raise BeispielFehler(f'große Kalibrierung: ausdrücklicher Parameter --bestaetigung "{BESTAETIGUNG}" fehlt; '
                             'nichts gerechnet')
    os.makedirs(verzeichnis, exist_ok=True)
    marke = os.path.join(verzeichnis, 'konfiguration.json')
    sha = konfig_sha(k)
    if os.path.exists(marke):
        with open(marke, encoding='utf-8') as f:
            alt = json.load(f)
        if alt.get('konfiguration_sha256') != sha:
            raise BeispielFehler(f'{verzeichnis} enthält Ergebnisse einer anderen Konfiguration: nicht überschrieben')
    else:
        with open(marke, 'w', encoding='utf-8') as f:
            json.dump(dict(konfiguration_sha256=sha, konfiguration={x: k[x] for x in k if not x.startswith('_')}), f,
                      ensure_ascii=False, indent=1)
    cp = Checkpoints(k, verzeichnis)
    r = kalibrierung.kalibrieren(k['szenario'], k['stufe'], k['_profil'], int(k['soll_A']), int(k['soll_A']),
                                 int(k['seed_basis']), plan=k['_plan'], n_min=int(k['n_min']),
                                 prozesse=int(k['prozesse']), verfahren=k['_verfahren'], soll_A=int(k['soll_A']),
                                 ausfuehren=cp)
    kenn = KENNZEICHNUNG_DEMO if k['modus'] == 'demonstration' else KENNZEICHNUNG_GROSS
    w8 = dict(r['werkzeug8'] or {}, kennzeichnung=kenn)                 # ohne Werte bei |A| = 0
    nz = r['mengen']['nachziehen']
    abgeschlossen = all((x or {}).get('status') == 'abgeschlossen' for x in nz['kalibrierung'] + [nz['pruefung']])
    out = dict(kennzeichnung=kenn, gerechnet=True, konfiguration_sha256=sha, betriebsart=k['modus'],
               abgeschlossen=bool(abgeschlossen and k['modus'] == 'gross'),
               status=('nicht abgeschlossen' if not abgeschlossen else
                       ('Demonstration: keine Kalibrierung' if k['modus'] == 'demonstration'
                        else 'abgeschlossen (|A| erreicht); Kriterien siehe raten')),
               werkzeug8=w8, c_H1=r['c_H1'], c_H1Z=r['c_H1Z'], pruefung=r['pruefung'], gepoolt=r['gepoolt'],
               h2=dict(typ=r['h2'].get('typ'), schluessel=r['h2'].get('schluessel')),
               gemeinsame_bestaetigung=r['gemeinsame_bestaetigung'], mengen=r['mengen'], e3=r.get('e3'),
               reserve_ziel=r.get('reserve_ziel'), zeitbilanz=r.get('zeitbilanz'), meta=r['meta'],
               checkpoints=dict(geladen=cp.geladen, gerechnet=cp.gerechnet),
               platzhalter=[] if abgeschlossen else ['Werte aus nicht abgeschlossenen Mengen: nur Diagnose'])
    formate.schreibe_objekt(os.path.join(verzeichnis, 'ergebnis'),
                            formate.kopf('bewertung', formate.synth_kennung('KALBSP', k['szenario'], k['modus'])),
                            out)
    return out
