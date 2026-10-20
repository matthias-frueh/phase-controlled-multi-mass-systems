"""Gezielte AP-13-Neuläufe nach den Korrekturen A–E (Auftrag vom 17.10.2026): K12 Planungshaken, K19 verrauschter
Ebenenvergleich und E3 an einer fest begrenzten Auswahl von Szenariopunkten.

Kleiner Treiber über den Produktionsfunktionen (pruefstand.ausfuehren mit dem Schritt „planung“,
ebenen.vergleich_verrauscht, kampagnen.ausfuehren). Er liest die versionierte Auftragsliste, prüft die gemeinsamen
Einstellungen gegen pruefstand.STANDARD und den Profil-Hash des Altlaufs, lädt die Werkzeug-8-Werte aus den
versionierten Dateien und führt jeden Auftrag mit Checkpoint aus. Eine Testvorgabe für Werkzeug 8 (werkzeug8=None im
Harness) gibt es nur, wo die Auftragsliste sie ausdrücklich nennt und der Altversuch sie verwendete; sonst bricht der
Treiber ab.

Checkpoint je Auftrag: <ausgabe>/<verzeichnis>/ mit den Ergebnisdateien und zuletzt schluessel.json. Wiederaufgenommen
wird nur bei gleichem Schlüssel (Rechencode, Auftrag, gemeinsame Einstellungen, Profil, Werkzeug 8, Seeds, Python/
NumPy/SciPy) und unveränderten Ergebnisdateien; ein abweichender Checkpoint wird beiseitegelegt und neu gerechnet. Der
Rechencode-Hash umfasst alle Module des Pakets außer Kommandozeile und Vergleichs-/Berichtsteil
(harness.neulauf_vergleich): Eine Korrektur am Bericht wiederholt keine Rechnung, jede andere Codeänderung schon.

vorbereiten() erzeugt einmalig aus der vollständigen Ausgabe des Altlaufs (nicht im Repository; ihre Prüfsummen stehen
in den erzeugten Dateien) die Auftragsliste, die Werkzeug-8-Dateien und den Altstandsauszug für den Vergleich.
"""
import hashlib
import json
import os
import platform
import shutil
import sys
import time

import numpy as np
import scipy

from .. import formate, regeln, verfahren as vf, zufall
from ..generator import kampagne as kp
from . import ebenen, kampagnen, kette, pruefstand

PAKET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WURZEL = os.path.dirname(os.path.dirname(PAKET))
DOKU_REL = 'docs/ap13_neulaeufe_2026-10-17'
AUFTRAG = os.path.join(WURZEL, DOKU_REL, 'auftrag.json')
HISTORISCH_REL = 'docs/ap11_ap12_ap13_pruefstand.json'
AUSGABE = '/tmp/pcmms-ap13-neulaeufe-20261017'
KENNUNG = 'AP13-NEULAUF-20261017'
NICHT_RECHENCODE = ('__main__.py', 'cli.py', 'harness/neulauf_vergleich.py')

# Altlauf (docs/ap11_ap12_ap13_pruefstand.json): Code, Profil, Git-Blob der unveränderten kompakten Datei
ALT_CODE = '7a259efe3f2f9545cd487af3d2ddb8a20a1e8b34'
ALT_PROFIL_SHA256 = '49dc74abca52b2c5e4ae8f6d2e1c53dc468205b01b9f65270b86c27e91114352'
ALT_BLOB = 'c0a6afb4e5ee8d7fc2c98984354da3b09b32efe8'

W8_FELDER = ('c_H1', 'c_H1Z', 'c_H1_herkunft', 'c_H1Z_herkunft', 'bias0', 'bias1', 'u_bias0', 'u_bias1',
             'bias0_zellen', 'bias1_zellen', 'u_bias0_zellen', 'u_bias1_zellen', 'bias_herkunft', 'h2_intervall')
W8_ARRAYS = ('bias0', 'bias1', 'u_bias0', 'u_bias1', 'bias0_zellen', 'bias1_zellen', 'u_bias0_zellen', 'u_bias1_zellen')
W8_QUELLEN = {'A4': ('kalibrierung_a4', None, 'N01-A4'), 'V1-G0': ('kalibrierung_v1', 'V1-G0', 'N01-V1G0')}

# Auswahl des Auftrags (Abschnitt 6): Szenario, Stufe, Prüfkampagnen, Rolle, Werkzeug 8, Fundort im Altlauf
E3_AUSWAHL = (('N01-A4', 'L1', 200, 'pruefung_c', 'A4', ('kalibrierung_a4', None)),
              ('A06-phase', 'L1', 30, 'pruefung', 'V1-G0', ('szenarien_v1', 'A06-phase/L1')),
              ('H03-phase', 'L1', 30, 'pruefung', 'V1-G0', ('szenarien_v1', 'H03-phase/L1')),
              ('E04-kette', 'L1', 30, 'pruefung', 'testvorgabe', ('eigene', 'E04-kette/L1')),
              ('E07-verstaerkung', 'L1', 40, 'pruefung', 'A4', ('szenarien_a4', 'E07-verstaerkung/L1')),
              ('E07-basisdrift', 'L1', 40, 'pruefung', 'A4', ('szenarien_a4', 'E07-basisdrift/L1')),
              ('N03-ungleich', 'L1', 40, 'pruefung', 'A4', ('szenarien_a4', 'N03-ungleich/L1')),
              ('N03-N3bindet', 'L1', 40, 'pruefung', 'A4', ('szenarien_a4', 'N03-N3bindet/L1')),
              ('N01-A4', 'L0', 40, 'pruefung', 'testvorgabe', ('k06', 'N01-A4/L0')),
              ('N01-A4', 'L2', 40, 'pruefung', 'testvorgabe', ('k06', 'N01-A4/L2')),
              ('N01-A4', 'L4', 40, 'pruefung', 'testvorgabe', ('k06', 'N01-A4/L4')))
K12_ZEIT = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)


class AuftragFehler(ValueError):
    """Auftragsliste, Eingänge oder Ergebnis passen nicht zusammen (keine Rechnung bzw. kein Checkpoint)."""


def umgebung():
    return dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)


def rechencode_sha256(ausgenommen=NICHT_RECHENCODE):
    """Prüfsumme aller Module des Pakets außer Kommandozeile und Vergleichs-/Berichtsteil (`ausgenommen`)."""
    teile = []
    for d, unter, dateien in os.walk(PAKET):
        unter[:] = sorted(x for x in unter if x != '__pycache__')
        for f in sorted(dateien):
            rel = os.path.relpath(os.path.join(d, f), PAKET).replace(os.sep, '/')
            if f.endswith('.py') and rel not in ausgenommen:
                teile.append([rel, formate.sha256_datei(os.path.join(d, f))])
    return formate.sha256_json(sorted(teile))


def git_blob(pfad):
    with open(pfad, 'rb') as f:
        b = f.read()
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


def _gleich(a, b):
    return formate.sha256_json(a) == formate.sha256_json(b)


# ── Auftragsliste und Eingänge ────────────────────────────────────────────────────────────────────────
def lies_auftrag(pfad=AUFTRAG):
    with open(pfad, encoding='utf-8') as f:
        a = json.load(f)
    ids = [x['id'] for x in a['auftraege']]
    if len(set(ids)) != len(ids):
        raise AuftragFehler('Auftrags-IDs nicht eindeutig')
    return a


def pruefe_gemeinsam(a):
    """Gemeinsame Einstellungen gegen pruefstand.STANDARD (Einstellungen des Altlaufs) und Profil-Hash."""
    g, st = a['gemeinsam'], pruefstand.STANDARD
    soll = dict(profil_reduktion=st['profil_reduktion'], plan=st['plan'], n_min=st['n_min'], seed_basis=st['seed'],
                hauptstufe=st['stufe'])
    ab = [k for k, v in soll.items() if not _gleich(g[k], v)]
    if ab:
        raise AuftragFehler(f'gemeinsame Einstellungen weichen von pruefstand.STANDARD ab: {ab}')
    prof = regeln.profil(g['profil']).mit_reduktion(**g['profil_reduktion'])
    if prof.sha256() != g['profil_sha256']:
        raise AuftragFehler(f'Profil-Hash {prof.sha256()} ≠ {g["profil_sha256"]} (Altlauf)')
    return prof, kp.plan_aus_dict(g['plan'])


def werkzeug8_laden(a, name):
    """Werkzeug-8-Werte eines Auftrags und ihre Inhaltsprüfsumme. (None, Prüfsumme) nur für die ausdrücklich genannte
    Testvorgabe: der Harness erzeugt sie dann wie im Altversuch selbst (werkzeug8=None)."""
    if name is None:
        return None, None
    e = a['werkzeug8'][name]
    if name == 'testvorgabe':
        h = formate.sha256_json(kette.testvorgabe_werkzeug8())
        if h != e['inhalt_sha256']:
            raise AuftragFehler('Testvorgabe des Harness weicht von der dokumentierten ab')
        return None, h
    _, w8 = formate.lies_objekt(os.path.join(WURZEL, e['datei']), 'werkzeug8')
    fehlt = [f for f in W8_FELDER if w8.get(f) is None]
    if fehlt:
        raise AuftragFehler(f'Werkzeug 8 {name}: {fehlt} fehlen – kein vollständiger Eingang')
    if 'TESTVORGABE' in str(w8['c_H1_herkunft']).upper() or 'TESTVORGABE' in str(w8['bias_herkunft']).upper():
        raise AuftragFehler(f'Werkzeug 8 {name} ist eine Testvorgabe')
    h = formate.sha256_json(w8)
    if h != e['inhalt_sha256']:
        raise AuftragFehler(f'Werkzeug 8 {name}: Inhalt {h} ≠ {e["inhalt_sha256"]} der Auftragsliste')
    return w8, h


def pruefe_werkzeug8_wahl(job):
    """Testvorgabe genau dort, wo der Altversuch sie verwendete; K19 und K12 nie (kein stiller Rückfall)."""
    w = job.get('werkzeug8')
    if job['art'] == 'planung':
        if w is not None:
            raise AuftragFehler('K12: Werkzeug 8 entsteht je Kandidat im Planungshaken, kein Eingang')
        return
    if w is None:
        raise AuftragFehler(f'{job["id"]}: Werkzeug 8 fehlt in der Auftragsliste (werkzeug8=None ergäbe still die '
                            'Testvorgabe)')
    if job['art'] == 'ebenen_verrauscht' and w == 'testvorgabe':
        raise AuftragFehler(f'{job["id"]}: K19 verlangt die A4-Werte, keine Testvorgabe')
    alt = (job.get('alt') or {}).get('werkzeug8')
    if job['art'] == 'kampagnen' and (w == 'testvorgabe') != (alt == 'TESTVORGABE'):
        raise AuftragFehler(f'{job["id"]}: Werkzeug 8 „{w}“ passt nicht zum Altversuch („{alt}“)')


def seeds(job, basis):
    """Kampagnenseeds nach der bestehenden Ableitung (Rolle, Szenario, Stufe, Index)."""
    if job['art'] == 'kampagnen':
        return [kampagnen.kampagnen_seed(basis, job['rolle'], job['szenario'], job['stufe'], i) for i in range(job['n'])]
    if job['art'] == 'ebenen_verrauscht':
        return [zufall.unterseed(basis, 'ebenen', job['szenario'], job['stufe'], i) for i in range(job['n'])]
    return []


def schluessel(a, job, prof, w8_sha, sd):
    return dict(rechencode=rechencode_sha256(), auftrag=formate.sha256_json(job),
                gemeinsam=formate.sha256_json(a['gemeinsam']), profil_sha256=prof.sha256(), werkzeug8=w8_sha,
                seeds=formate.sha256_json(sd), umgebung=umgebung())


def verzeichnis(a, job, ausgabe=None):
    return os.path.join(ausgabe or a['gemeinsam']['ausgabe'], job.get('verzeichnis', job['id']))


def checkpoint(ziel, key=None):
    """Inhalt von schluessel.json, wenn der Checkpoint vollständig ist und (falls key) zum Schlüssel passt; sonst
    None (kein Checkpoint) bzw. False (abweichend oder unvollständig)."""
    p = os.path.join(ziel, 'schluessel.json')
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        s = json.load(f)
    if key is not None and not _gleich(s.get('schluessel'), key):
        return False
    for name, h in s['dateien'].items():
        q = os.path.join(ziel, name)
        if not os.path.exists(q) or formate.sha256_datei(q) != h:
            return False
    return s


# ── Rechnungen ────────────────────────────────────────────────────────────────────────────────────────
def _planung(job, a, prof, plan, w8, w8_sha, ziel, prozesse, protokoll):
    """Schritt „planung“ von pruefstand.ausfuehren mit der Standardkonfiguration (wie harness pruefstand
    --schritte planung); die wirksamen Vorgaben werden vorher und nachher gegen die Auftragsliste geprüft."""
    e, st = job['erwartet'], pruefstand.STANDARD
    ab = [k for k in ('n_planung', 'planung_kandidaten', 'planung_max_aufrufe') if not _gleich(e[k], st[k])]
    if ab:
        raise AuftragFehler(f'K12: Vorgaben {ab} von pruefstand.STANDARD weichen von der Auftragsliste ab')
    out = pruefstand.ausfuehren(ziel, None, ['planung'], prozesse, protokoll=protokoll, verfahren=vf.HISTORISCH)
    pl = out['schritte']['planung']
    if not _gleich(pl['zeit'], e['zeit']):
        raise AuftragFehler(f'K12: Zeitangaben {pl["zeit"]} ≠ Auftragsliste {e["zeit"]}')
    kand = [c for x in pl['aufrufe'] for c in x['kandidaten']]
    if any(c['n0'] not in e['n0_kandidaten'] or c['n_min'] not in e['planung_kandidaten'] for c in kand):
        raise AuftragFehler('K12: Kandidaten außerhalb der Auftragsliste')
    if sum(1 for x in pl['aufrufe'] if x['kandidaten']) > e['planung_max_aufrufe']:
        raise AuftragFehler('K12: mehr simulierte Aufrufe als planung_max_aufrufe')
    if out['profil_sha256'] != a['gemeinsam']['profil_sha256']:
        raise AuftragFehler('K12: Profil-Hash der Ausgabe weicht ab')
    return [f for f in ('pruefstand.json', 'pruefstand.npz') if os.path.exists(os.path.join(ziel, f))]


def _ebenen(job, a, prof, plan, w8, w8_sha, ziel, prozesse, protokoll):
    """K19: ebenen.vergleich_verrauscht mit ausdrücklichem Werkzeug 8 (A4); Rohdaten der Ebene Z nur temporär."""
    if w8 is None:
        raise AuftragFehler('K19 ohne Werkzeug 8: der Harness fiele still auf die Testvorgabe zurück')
    g = a['gemeinsam']
    tmp = os.path.join(ziel, 'verrauscht_tmp')
    rv = ebenen.vergleich_verrauscht(job['szenario'], job['stufe'], prof, job['n'], g['seed_basis'], tmp, plan,
                                     g['n_min'], w8, prozesse=prozesse, verfahren=vf.HISTORISCH)
    shutil.rmtree(tmp, ignore_errors=True)
    if rv['seeds'] != job['seeds']:
        raise AuftragFehler('K19: Seeds der Rechnung ≠ Auftragsliste')
    meta = dict(szenario=job['szenario'], stufe=job['stufe'], n=job['n'], seed_basis=g['seed_basis'],
                seed_ableitung="zufall.unterseed(Basis, 'ebenen', Szenario, Stufe, i)", plan=kampagnen._plan_dict(plan),
                n_min=g['n_min'], profil=prof.id, profil_sha256=prof.sha256(), werkzeug8=job['werkzeug8'],
                werkzeug8_sha256=w8_sha, werkzeug8_herkunft=w8['c_H1_herkunft'], code_version=formate.code_version())
    formate.schreibe_objekt(os.path.join(ziel, 'ebenen'), formate.kopf('bewertung', formate.synth_kennung(
        KENNUNG, job['id'])), dict(meta=meta, ergebnis=rv))
    return [f for f in ('ebenen.json', 'ebenen.npz') if os.path.exists(os.path.join(ziel, f))]


def _kampagnen(job, a, prof, plan, w8, w8_sha, ziel, prozesse, protokoll):
    """E3: kampagnen.ausfuehren mit Rolle, Seeds und Werkzeug 8 der Auftragsliste."""
    g = a['gemeinsam']
    lauf = kampagnen.ausfuehren(job['szenario'], job['stufe'], prof, job['n'], g['seed_basis'], job['rolle'], plan,
                                g['n_min'], w8, prozesse=prozesse, verfahren=vf.HISTORISCH)
    m = lauf['meta']
    if m['seeds'] != job['seeds'] or m['rolle'] != job['rolle']:
        raise AuftragFehler(f'{job["id"]}: Rolle oder Seeds der Rechnung ≠ Auftragsliste')
    if (m['werkzeug8'] == 'TESTVORGABE') != (job['werkzeug8'] == 'testvorgabe'):
        raise AuftragFehler(f'{job["id"]}: Werkzeug 8 der Rechnung „{m["werkzeug8"]}“ ≠ Auftragsliste')
    m.update(werkzeug8_quelle=job['werkzeug8'], werkzeug8_sha256=w8_sha)
    pf = kampagnen.schreibe(ziel, lauf, kennung=formate.synth_kennung(KENNUNG, job['id']))
    return [os.path.basename(pf['objekt']) + x for x in ('.json', '.npz', '.csv')
            if os.path.exists(pf['objekt'] + x)]


RECHNER = dict(planung=_planung, ebenen_verrauscht=_ebenen, kampagnen=_kampagnen)


def ausfuehren(pfad=AUFTRAG, nur=None, prozesse=None, ausgabe=None, protokoll=print, streng=True):
    """Führt die Aufträge der Liste der Reihe nach aus (je Auftrag bis zu `prozesse` Arbeitsprozesse) und übernimmt
    passende Checkpoints. streng: nur aus einem sauberen, unveränderten Git-Stand rechnen. Rückgabe {id: Status}."""
    a = lies_auftrag(pfad)
    prof, plan = pruefe_gemeinsam(a)
    git = formate.git_stand()
    if streng and (git is None or git.endswith('+geändert')):
        raise AuftragFehler(f'Arbeitsbaum nicht sauber ({git}): Treiber und Konfiguration vor den Rechnungen '
                            'committen')
    P = int(prozesse or a['gemeinsam']['prozesse'])
    status = {}
    for job in a['auftraege']:
        if nur and job['id'] not in nur:
            continue
        if streng and formate.git_stand() != git:
            raise AuftragFehler(f'Code während der Läufe geändert ({git} → {formate.git_stand()})')
        pruefe_werkzeug8_wahl(job)
        w8, w8_sha = werkzeug8_laden(a, job.get('werkzeug8'))
        sd = seeds(job, a['gemeinsam']['seed_basis'])
        if job['art'] != 'planung' and sd != job['seeds']:
            raise AuftragFehler(f'{job["id"]}: Seed-Ableitung ergibt andere Seeds als die Auftragsliste')
        key = schluessel(a, job, prof, w8_sha, sd)
        ziel = verzeichnis(a, job, ausgabe)
        s = checkpoint(ziel, key)
        if s:
            protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]}: Checkpoint passt (Code {s["git"]}, '
                      f'{s["laufzeit_s"]} s) – übernommen')
            status[job['id']] = 'übernommen'
            continue
        if os.path.exists(ziel):
            beiseite, i = f'{ziel}.verworfen-{time.strftime("%Y%m%dT%H%M%S")}', 1
            while os.path.exists(beiseite):
                beiseite, i = f'{ziel}.verworfen-{time.strftime("%Y%m%dT%H%M%S")}-{i}', i + 1
            shutil.move(ziel, beiseite)
            protokoll(f'{job["id"]}: Checkpoint fehlt, ist unvollständig oder passt nicht – beiseitegelegt: {beiseite}')
        os.makedirs(ziel)
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]} …')
        t0, start = time.perf_counter(), formate.zeitstempel()
        dateien = RECHNER[job['art']](job, a, prof, plan, w8, w8_sha, ziel, P, protokoll)
        git_ende = formate.git_stand()
        if streng and git_ende != git:                  # kein Checkpoint aus einem während der Rechnung geänderten Stand
            raise AuftragFehler(f'{job["id"]}: Code während der Rechnung geändert ({git} → {git_ende})')
        s = dict(auftrag=job['id'], schluessel=key, dateien={d: formate.sha256_datei(os.path.join(ziel, d))
                                                             for d in dateien},
                 git=git, git_ende=git_ende, start=start, ende=formate.zeitstempel(),
                 laufzeit_s=round(time.perf_counter() - t0, 1), prozesse=P)
        with open(os.path.join(ziel, 'schluessel.json'), 'w', encoding='utf-8') as f:
            f.write(formate.json_text(s))
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]} fertig ({s["laufzeit_s"]} s)')
        status[job['id']] = 'gerechnet'
    return status


# ── einmalige Vorbereitung aus dem Altlauf ─────────────────────────────────────────────────────────────
def _rate_kurz(r):
    return None if r is None else dict(zaehler=r['zaehler'], nenner=r['nenner'], rate=r['rate'], mc_se=r['mc_se'])


def _raten_kurz(d):
    return {k: _rate_kurz(v) for k, v in (d or {}).items() if isinstance(v, dict) and 'zaehler' in v}


def _punkt_auszug(x):
    m = x['meta']
    return dict(meta={k: m.get(k) for k in ('szenario', 'stufe', 'rolle', 'n', 'seed_basis', 'seeds', 'n_min', 'plan',
                                            'werkzeug8', 'werkzeug8_herkunft', 'profil_sha256', 'code_version',
                                            'laufzeit_s', 'prozesse')},
                raten=_raten_kurz(x['raten']), gueltigkeit=_raten_kurz(x['gueltigkeit']),
                abbruch=_raten_kurz(x['abbruch']), wahrheit=x.get('wahrheit'), u_c_median=x.get('u_c_median'))


def _kal_auszug(k):
    h2 = k['h2']
    return dict(meta=k['meta'], c_H1=k['c_H1'], c_H1Z=k['c_H1Z'], pruefung=_rate_kurz(k['pruefung']),
                gepoolt=k['gepoolt'], h2=dict(typ=h2.get('typ'), niveau=h2.get('niveau'),
                                              schluessel=h2.get('schluessel'),
                                              ueberdeckung={s: {y: _rate_kurz(r) for y, r in v.items()}
                                                            for s, v in (h2.get('ueberdeckung') or {}).items()}),
                gemeinsame_bestaetigung=_rate_kurz(k['gemeinsame_bestaetigung']),
                raten=_raten_kurz(k['raten_pruefung']), gueltigkeit=_raten_kurz(k['gueltigkeit_pruefung']),
                zmax_pruefung=np.asarray(k['zmax']['pruefung'], float).tolist(),
                zmax_pruefung_vollstaendig=np.asarray(k['zmax']['pruefung_vollstaendig'], bool).tolist())


def vorbereiten(voll, doku=None, historisch=None):
    """Aus der vollständigen Ausgabe des Altlaufs (Pfad ohne Endung): Werkzeug-8-Dateien (wiederverwendet, unverändert),
    Altstandsauszug und Auftragsliste. Bricht ab, wenn die Ausgabe nicht zur historischen kompakten Datei passt."""
    doku = doku or os.path.join(WURZEL, DOKU_REL)
    historisch = historisch or os.path.join(WURZEL, HISTORISCH_REL)
    kopf, v = formate.lies_objekt(voll, 'bewertung')
    with open(historisch, encoding='utf-8') as f:
        hist = json.load(f)
    if not _gleich(pruefstand.kompakt(v), hist['inhalt']):
        raise AuftragFehler('vollständige Ausgabe ergibt nicht die historische kompakte Datei')
    if kopf['code_version']['git'] != ALT_CODE or v['profil_sha256'] != ALT_PROFIL_SHA256:
        raise AuftragFehler('Code oder Profil der vollständigen Ausgabe ≠ Altlauf')
    st = pruefstand.STANDARD
    if not _gleich(v['konfiguration'], {k: (list(x) if isinstance(x, tuple) else x) for k, x in st.items()}):
        raise AuftragFehler('Konfiguration des Altlaufs ≠ pruefstand.STANDARD')
    os.makedirs(doku, exist_ok=True)
    s = v['schritte']
    quelle = dict(datei='pruefstand.json (+ pruefstand.npz), vollständige Ausgabe des Entwicklungsprüfstands vom '
                        '16.10.2026; nicht im Repository, im Arbeitsbereich der Sitzung erhalten',
                  sha256=formate.sha256_datei(voll + '.json'), npz_sha256=formate.sha256_datei(voll + '.npz'),
                  kennung=kopf['kennung'], code_version=kopf['code_version'], profil=v['profil'],
                  profil_sha256=v['profil_sha256'],
                  historisch=dict(datei=HISTORISCH_REL, git_blob=git_blob(historisch), gleich_kompakt_der_quelle=True))
    w8_eintraege = {}
    for name, (schritt, unter, sid) in W8_QUELLEN.items():
        kal = s[schritt] if unter is None else s[schritt][unter]
        m = kal['meta']
        if (m['szenario'], m['stufe'], m['seed_basis'], m['profil_sha256']) != (sid, 'L1', st['seed'],
                                                                                ALT_PROFIL_SHA256):
            raise AuftragFehler(f'Kalibrierung {name}: Szenario, Stufe, Seed oder Profil ≠ Altlauf')
        w8 = dict(kal['werkzeug8'])
        fehlt = [f for f in W8_FELDER if w8.get(f) is None]
        if fehlt:
            raise AuftragFehler(f'Werkzeug 8 {name} im Altlauf unvollständig: {fehlt}')
        for f in W8_ARRAYS:
            w8[f] = np.asarray(w8[f], float)
        ort = f'schritte.{schritt}' + (f'.{unter}' if unter else '') + '.werkzeug8'
        herkunft = dict(art='wiederverwendet (nicht rekonstruiert)', quelle=quelle, ort=ort,
                        kalibrierung=dict(szenario=sid, stufe='L1', seed_basis=m['seed_basis'],
                                          rollen=['kalibrierung_c', 'pruefung_c'], n_kalibrierung=m['n_kalibrierung'],
                                          n_pruefung=m['n_pruefung'], profil=m['profil'],
                                          profil_sha256=m['profil_sha256'], code_version=m['code_version'],
                                          plan=st['plan'], n_min=st['n_min'], gepoolt=kal['gepoolt']))
        datei = f'werkzeug8_{name.replace("-", "")}'
        formate.schreibe_objekt(os.path.join(doku, datei), formate.kopf(
            'werkzeug8', formate.synth_kennung('W8', sid, 'L1', st['seed']), herkunft=herkunft), w8)
        _, zurueck = formate.lies_objekt(os.path.join(doku, datei), 'werkzeug8')
        if not _gleich(zurueck, kal['werkzeug8']):
            raise AuftragFehler(f'Werkzeug 8 {name}: Datei gibt die Werte des Altlaufs nicht unverändert zurück')
        w8_eintraege[name] = dict(datei=f'{DOKU_REL}/{datei}', inhalt_sha256=formate.sha256_json(zurueck),
                                  art='wiederverwendet', ort_im_altlauf=ort, c_H1=w8['c_H1'], c_H1Z=w8['c_H1Z'],
                                  h2_intervall=dict(typ=w8['h2_intervall']['typ'],
                                                    niveau=w8['h2_intervall']['niveau']),
                                  gepoolt=kal['gepoolt'])
    tv = kette.testvorgabe_werkzeug8()
    formate.schreibe_objekt(os.path.join(doku, 'werkzeug8_testvorgabe'), formate.kopf(
        'werkzeug8', formate.synth_kennung('W8', 'TESTVORGABE'), herkunft=dict(
            art='Testvorgabe des Harness (kette.testvorgabe_werkzeug8), keine Kalibriersimulation',
            aufruf='werkzeug8=None wie im Altversuch; diese Datei dokumentiert die erzeugten Werte')), tv)
    w8_eintraege['testvorgabe'] = dict(datei=f'{DOKU_REL}/werkzeug8_testvorgabe', inhalt_sha256=formate.sha256_json(tv),
                                       art='Testvorgabe', aufruf='werkzeug8=None im Harness (wie im Altversuch)')
    # Altstandsauszug: nur, was der Vergleich braucht und die kompakte Datei nicht enthält (Seeds, Mediane, MC-Fehler)
    e3 = {}
    for sid, stf, n, rolle, w, (schritt, unter) in E3_AUSWAHL:
        if unter is None:
            x = _kal_auszug(s[schritt])
        else:
            x = _punkt_auszug(s[schritt][unter])
            if (x['meta']['rolle'], x['meta']['n']) != (rolle, n):
                raise AuftragFehler(f'{sid}/{stf}: Rolle oder Kampagnenzahl ≠ Altlauf')
        e3[f'{sid}/{stf}'] = dict(ort=f'schritte.{schritt}' + (f'.{unter}' if unter else '.raten_pruefung'), **x)
    rv = s['ebenen']['verrauscht']
    pl = s['planung']
    auszug = dict(quelle=quelle, laufzeit_s=v['laufzeit_s'], e3=e3,
                  k19=dict(ort='schritte.ebenen.verrauscht', n=rv['n'], u_c_median=rv['u_c_median'],
                           u_c_relativ=rv['u_c_relativ'], u_c_innerhalb_5_prozent=rv['u_c_innerhalb_5_prozent'],
                           raten={k: dict(Z=_rate_kurz(x['Z']), H=_rate_kurz(x['H']), innerhalb_2se=x['innerhalb_2se'])
                                  for k, x in rv['raten'].items()},
                           rauschfrei=s['ebenen']['rauschfrei']),
                  k12=dict(ort='schritte.planung', suche=pl['suche'], zeit=pl['zeit'],
                           aufrufe=[{k: x for k, x in y.items() if k != 'quelle'} for y in pl['aufrufe']],
                           plan_simuliert=dict(n_zyklen=kp.Plan().n_zyklen, T_lauf_s=kp.Plan().T_lauf,
                                               tage=kp.Plan().tage,
                                               herkunft='Code 7a259ef: plan_basis.mit(n_bloecke=n + r, n0=n0); N_z, '
                                                        'T_Lauf und d aus den Vorgaben von kampagne.Plan')))
    with open(os.path.join(doku, 'altstand_auszug.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text(auszug))
    # Auftragsliste
    basis = st['seed']
    auftr = [dict(id='K12-planung', art='planung', kriterium='K12', szenario='N01-A4', stufe=st['stufe'],
                  verzeichnis='planung', werkzeug8=None,
                  aufruf='pruefstand.ausfuehren(<ausgabe>/planung, konfiguration=None, schritte=(planung,), '
                         'prozesse=4), gleichwertig mit harness pruefstand --schritte planung --prozesse 4 --ausgabe '
                         '<ausgabe>/planung',
                  erwartet=dict(n_planung=list(st['n_planung']), planung_kandidaten=list(st['planung_kandidaten']),
                                n0_kandidaten=[20], planung_max_aufrufe=st['planung_max_aufrufe'], zeit=K12_ZEIT),
                  seed_ableitung='Pilotkampagne mit Seed 20261016; je Aufruf (k, N_z) und Kandidat (n_min, n₀) '
                                 "Kalibrierung mit Basis zufall.unterseed(20261016, 'planung', n_min, n₀, k, N_z) und "
                                 'Rollen kalibrierung_c/pruefung_c',
                  hinweis='Werkzeug 8 entsteht je Kandidat in der Planungssimulation; kein Eingang')]
    j = dict(id='K19-ebenen', art='ebenen_verrauscht', kriterium='K19', szenario='N01-A4', stufe=st['stufe'],
             n=st['n_ebenen'], rolle='ebenen', werkzeug8='A4')
    j['seeds'] = seeds(j, basis)
    auftr.append(j)
    for sid, stf, n, rolle, w, (schritt, unter) in E3_AUSWAHL:
        alt = e3[f'{sid}/{stf}']
        j = dict(id=f'E3-{sid}-{stf}', art='kampagnen', kriterium='E3', szenario=sid, stufe=stf, n=n, rolle=rolle,
                 werkzeug8=w, alt=dict(ort=alt['ort'], werkzeug8='übergeben' if unter is None else
                                       alt['meta']['werkzeug8']))
        j['seeds'] = seeds(j, basis)
        if unter is not None and j['seeds'] != alt['meta']['seeds']:
            raise AuftragFehler(f'{sid}/{stf}: Seeds weichen vom Altlauf ab')
        auftr.append(j)
    a = dict(kennung=KENNUNG, anweisung='ANWEISUNG_Claude_Code_AP13_Neulaeufe_K12_K19_E3_2026-10-17',
             ausgangsstand='dd7676ec4db617fb7d5e6dbfe86eeb03ee8b04d6',
             altlauf=dict(code=ALT_CODE, kompakt=HISTORISCH_REL, git_blob=ALT_BLOB,
                          auszug=f'{DOKU_REL}/altstand_auszug.json'),
             gemeinsam=dict(profil='ENTW-2026-10', profil_reduktion=st['profil_reduktion'],
                            profil_sha256=ALT_PROFIL_SHA256, plan=st['plan'], n_min=st['n_min'], seed_basis=basis,
                            hauptstufe=st['stufe'], prozesse=4, blas_threads_je_prozess=1, ausgabe=AUSGABE),
             werkzeug8=w8_eintraege, auftraege=auftr,
             umfang=dict(e3_pruefkampagnen=sum(x[2] for x in E3_AUSWAHL), k19_kampagnen_je_ebene=st['n_ebenen'],
                         k12='Planungsschritt wie im Altlauf (höchstens 2 simulierte Aufrufe, je Kandidat 4 + 4 '
                             'Kampagnen)', kalibrierkampagnen=0,
                         hinweis='Werkzeug 8 A4 und V1-G0 wiederverwendet; keine Rekonstruktion nötig'))
    if quelle['historisch']['git_blob'] != ALT_BLOB:
        raise AuftragFehler('historische kompakte Datei verändert')
    with open(os.path.join(doku, 'auftrag.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text(a))
    return a


if __name__ == '__main__':                              # PYTHONPATH=code python3 -m pcmms_auswertung.harness.neulauf
    from ..cli import main
    sys.exit(main(['harness', 'neulauf'] + sys.argv[1:]))
