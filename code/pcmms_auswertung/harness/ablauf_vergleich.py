"""Begrenzte Entwicklungsrechnung zu k-Konsistenz und Wiederholungsablauf (Auftrag vom 17.10.2026, Teil C).

Vergleich (schlank, ohne Hypothesenbootstrap): N01-A4, N01-V1G0 und N01-V1G60h mit je zehn gemeinsamen Seeds – den
ersten zehn der G4-Diagnose von PR #22 (zufall.unterseed(20261017, 'diagnose_g4', Szenario, 'L1', i), i = 0 … 9) – in
drei Varianten:
  historisch      Bindung der Phase-0-Größen an k der Pilotgrößen, statischer Laufplan (Rechnung wie PR #22)
  k_konsistent    Bindung an k_max und N_z des Plans, statischer Laufplan
  wiederholungen  Bindung an den Plan, zustandsbehafteter Ablauf mit allen Optionen (ablauf.py)
Der zustandsbehaftete Ablauf verwendet für die ursprünglichen Versuche dieselben Ziehungen wie der Laufplan (ebene_h
.Vorrat); die drei Varianten teilen also Phase 0 und die Ziehungen der geplanten Läufe, Unterschiede folgen aus k
(historisch → k_konsistent) und aus dem Ablauf (k_konsistent → wiederholungen). Je Kampagne: Teil B (σ_Δ, p̂, ε_ctrl,
Arbeitspunkt), Gültigkeit und Auswertbarkeit nach auswertung.datenlage, Ablaufbericht. Dazu wenige volle Ketten mit
Stufe 2 (Nullfall, Artefaktfall, Ebene Z/Stufe 1), Regelpfadfälle und eine echte Fortsetzung aus einem Ablaufstand.

Checkpoint je Auftrag wie harness.neulauf: Rechencode (ohne Kommandozeile und Berichtsteil), Auftrag, gemeinsame
Einstellungen, Profil, Werkzeug 8, Seeds, Verfahren der Variante, Bibliotheken; gerechnet wird nur aus einem sauberen
Git-Stand.
"""
import json
import os
import shutil
import tempfile
import time

import numpy as np

from .. import ablauf, auswertung, formate, gueltigkeit, regeln, verfahren as vf
from ..generator import kampagne as kp, szenarien
from . import kampagnen, kette, neulauf

DOKU_REL = 'docs/ap13_kmax_wiederholungen_2026-10-17'
AUFTRAG = os.path.join(neulauf.WURZEL, DOKU_REL, 'auftrag.json')
AUSGABE = '/tmp/pcmms-ablauf-vergleich-20261017'
KENNUNG = 'ABLAUF-VERGLEICH-20261017'
NICHT_RECHENCODE = neulauf.NICHT_RECHENCODE + ('harness/diagnose_e3b_g4_bericht.py',
                                               'harness/ablauf_vergleich_bericht.py')
AUSGANGSSTAND = '2ab6d2818a80e67aaa927de00060f99167ed8c25'
SEED_BASIS = 20261017
STUFE = 'L1'
SYSTEME = ('N01-A4', 'N01-V1G0', 'N01-V1G60h')
VARIANTEN = dict(historisch=vf.HISTORISCH, k_konsistent=vf.STATISCH, wiederholungen=vf.ZUSTAND)
N_SEEDS = 10
N_START = 2                 # Startsatz je System und Variante (vorab festgelegt): Laufzeit, Hochrechnung
FORTSETZUNG_BIS = 300       # technische Unterbrechung nach so vielen Phase-1-Versuchen (echte Fortsetzung)

Fehler = neulauf.AuftragFehler


def vergleichs_seeds(sid, n=N_SEEDS):
    """Die ersten n Seeds der G4-Diagnose von PR #22 (gleiche Kampagnen, historisch nachrechenbar)."""
    return [kampagnen.kampagnen_seed(SEED_BASIS, 'diagnose_g4', sid, STUFE, i) for i in range(n)]


def zusatz_seed(sid, i=0):
    return kampagnen.kampagnen_seed(SEED_BASIS, 'ablauf_voll', sid, STUFE, i)


def profil_und_plan(g):
    prof = regeln.profil(g['profil']).mit_reduktion(**g['profil_reduktion'])
    if prof.sha256() != g['profil_sha256']:
        raise Fehler(f'Profil-Hash {prof.sha256()} ≠ {g["profil_sha256"]}')
    return prof, kp.Plan(**g['plan'])


# ── eine Kampagne ─────────────────────────────────────────────────────────────────────────────────────────
def _regelzahl(pr, idx):
    out = {}
    for i in idx:
        for g in pr['gruende'][i]:
            out[g] = out.get(g, 0) + 1
    return out


def befund(tab, tb, dl, bericht=None):
    """Schlanker Befund einer Kampagne aus Tabelle, Teil B und Datenlage (keine Wahrheit, kein Bootstrap)."""
    n2 = tb['nr2']
    t1, pr = dl['t1'], dl['pr']
    art = t1.spalte('laufart', object)
    k_ids = np.flatnonzero(art == 'K')
    schnitt = [c['id'] for c in n2['konfigurationen'] if c['gruppe'] == 'schnitt']
    info = dl['info']
    nicht = [c for c in schnitt if not info[c]['auswertbar']]
    g4 = [i for i in k_ids if 'G4' in pr['gruende'][i]]
    out = dict(
        teil_b=dict(k_max=int(n2['k_max']), bindung=n2['phase0_bindung']['modus'], k=n2['phase0_bindung'].get('k'),
                    k_pilotgroessen=n2['phase0_bindung'].get('k_pilotgroessen'),
                    sigma_delta_K=dict(n2['sigma_delta']['K']), p_hat=float(n2['p_hat']), eps_ctrl=n2['eps_ctrl'],
                    n=int(n2['n']), n_min=int(n2['n_min']), arbeitspunkt=n2['arbeitspunkt']['status'],
                    r_soll=n2['arbeitspunkt'].get('r_soll'),
                    n0_gueltig=[len(e['lauf_ids']) for e in tb['nr3']['einzel0']]),
        phase1=dict(n_laeufe=len(t1), n_ungueltig=int((~pr['gueltig']).sum()), regeln=_regelzahl(pr, range(len(t1))),
                    konfig_laeufe=int(k_ids.size), konfig_ungueltig=int((~pr['gueltig'][k_ids]).sum()),
                    konfig_g4=len(g4), konfig_regeln=_regelzahl(pr, k_ids),
                    S2=len(dl['ab']['S2']), S4=len(dl['ab']['S4'])),
        auswertbar=dict(n=len(schnitt) - len(nicht), von=len(schnitt), nicht=nicht,
                        min_gueltig=int(min(info[c]['n_gueltig'] for c in schnitt)),
                        n_gueltig={c: int(info[c]['n_gueltig']) for c in schnitt}),
        kontrollen=dict(gueltig_je_modul=[len(dl['kontroll'][(1, j)]) for j in (1, 2, 3)],
                        yhat1_gueltig=bool(dl['yhat1_gueltig'])),
        sperren=[t for _, t in dl['sperren_alle']],
        vollstaendig=bool(not nicht and dl['yhat1_gueltig'] and not dl['sperren_alle']))
    if bericht is not None:
        out['ablauf'] = dict(ablauf.kurz(bericht), rollen=bericht['rollen'],
                             auswahl_status={k: v['status'] for k, v in bericht['auswahl'].items()
                                             if v['status'] != 'gueltig'},
                             halte=bericht['halte'])
    return out


def kampagne(auftrag):
    """Eine Kampagne (Arbeitsprozess). auftrag = (Szenario, Variante, Index, Seed, Art, Ebene, gemeinsam, Werkzeug 8).
    Art: schlank (Datenlage), voll (dazu Stufe 2), fortsetzung (Ablauf bis FORTSETZUNG_BIS Versuche, Stand in einer
    Datei, Fortsetzung aus der Datei; Vergleich mit dem ununterbrochenen Ablauf)."""
    sid, variante, idx, seed, art, ebene, g, w8 = auftrag
    prof, plan = profil_und_plan(g)
    v = VARIANTEN[variante]
    n_min = g['n_min']
    t0 = time.perf_counter()
    tmp = tempfile.mkdtemp(prefix='pcmms-ablauf-') if (ebene == 'Z' or art == 'fortsetzung') else None
    try:
        zus = {}
        if v.ablauf == 'zustand':
            if art == 'fortsetzung':
                r0 = kette.kampagne_ablauf(sid, STUFE, plan, seed, prof, w8, n_min, v, bis=FORTSETZUNG_BIS)
                if r0['ablauf'].status != 'unterbrochen':
                    raise Fehler(f'{sid}/{idx}: Fortsetzung: Ablauf vor {FORTSETZUNG_BIS} Versuchen beendet')
                pfad = os.path.join(tmp, 'ablaufstand')
                ablauf.speichern(pfad, r0['ablauf'])
                zus['stand'] = dict(versuche=len(r0['ablauf'].z['versuche']),
                                    sha256=formate.sha256_datei(pfad + '.json'))
                r = kette.kampagne_ablauf(sid, STUFE, plan, seed, prof, w8, n_min, v, zustand=ablauf.laden(pfad))
                ganz = kette.kampagne_ablauf(sid, STUFE, plan, seed, prof, w8, n_min, v)
                ta, tb_ = kette.ablauf_tabelle(ganz), kette.ablauf_tabelle(r)
                zus['gleich_ununterbrochen'] = bool(
                    len(ta) == len(tb_) and all(np.array_equal(ta.daten[f], tb_.daten[f], equal_nan=True)
                                                for f in ta.daten)
                    and formate.sha256_json(ta.koepfe) == formate.sha256_json(tb_.koepfe))
                try:
                    kette.kampagne_ablauf(sid, STUFE, plan, seed, prof, w8, n_min,
                                          vf.Verfahren('plan', 'zustand', ablauf.Ablaufoptionen(aufwaermen=False)),
                                          zustand=ablauf.laden(pfad))
                    zus['andere_optionen_zurueckgewiesen'] = False
                except ablauf.AblaufFehler as e:
                    zus['andere_optionen_zurueckgewiesen'] = 'anderer Kennung' in str(e)
            else:
                r = kette.kampagne_ablauf(sid, STUFE, plan, seed, prof, w8, n_min, v, ebene=ebene,
                                          verzeichnis=None if tmp is None else os.path.join(tmp, 'z'))
            tab, tb, kal = kette.ablauf_tabelle(r), r['teil_b'], r['kalibrierung']
            ber = r['ablauf'].bericht()
        else:
            if ebene != 'H':
                raise Fehler('statischer Ablauf nur auf Ebene H')
            m, laeufe, tab = kette.kampagne_erzeugen(sid, STUFE, plan, seed)
            _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
            tb, _ = kette.teil_b_erzeugen(tab, kal, m, prof, w8 or kette.testvorgabe_werkzeug8(), seed, n_min,
                                          kennung=formate.synth_kennung('KETTE', sid, STUFE, seed), verfahren=v)
            ber = None
        dl = auswertung.datenlage(tab, tb, prof)
        out = dict(szenario=sid, variante=variante, index=int(idx), seed=int(seed), art=art, ebene=ebene,
                   verfahren=v.kennung(), **befund(tab, tb, dl, ber))
        out.update(zus)
        if art == 'voll':
            erg = auswertung.auswerten(tab, kal, tb, prof)
            kb = kampagnen.kurzbefund(erg, tb, seed, ber)
            out['voll'] = {k: kb[k] for k in ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3_grund', 'n_auswertbar',
                                              'yhat1_gueltig')}
            out['voll']['E3'] = None if kb['E3'] is None else dict(bewertung=kb['E3']['bewertung'],
                                                                   status=kb['E3']['status'])
            out['voll']['herkunft_ablauf'] = erg['herkunft'].get('ablauf')
            out['voll']['datenlage_gleich'] = bool(erg['n_auswertbar'] == out['auswertbar']['n'])
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
    out['laufzeit_s'] = round(time.perf_counter() - t0, 3)
    return out


# ── Auftragsliste, Ausführung ─────────────────────────────────────────────────────────────────────────────
def lies_auftrag(pfad=AUFTRAG):
    with open(pfad, encoding='utf-8') as f:
        return json.load(f)


def schluessel(a, job, prof, w8_sha):
    return dict(rechencode=neulauf.rechencode_sha256(NICHT_RECHENCODE), auftrag=formate.sha256_json(job),
                gemeinsam=formate.sha256_json(a['gemeinsam']), profil_sha256=prof.sha256(), werkzeug8=w8_sha,
                seeds=formate.sha256_json(job['seeds']), verfahren=VARIANTEN[job['variante']].kennung(),
                umgebung=neulauf.umgebung())


def _rechne(job, a, w8, prozesse):
    auftraege = [(job['szenario'], job['variante'], i, s, job['art'], job['ebene'], a['gemeinsam'], w8)
                 for i, s in zip(job['indizes'], job['seeds'])]
    if prozesse > 1 and len(auftraege) > 1:
        return kampagnen._parallel(auftraege, prozesse, fn=kampagne)
    return [kampagne(x) for x in auftraege]


def _seeds_pruefen(job):
    if job['seedregel'] == 'vergleich':
        soll = [vergleichs_seeds(job['szenario'])[i] for i in job['indizes']]
    else:
        soll = [zusatz_seed(job['szenario'], i) for i in job['indizes']]
    if job['seeds'] != soll:
        raise Fehler(f'{job["id"]}: Seed-Ableitung ergibt andere Seeds als die Auftragsliste')


def ausfuehren(pfad=AUFTRAG, nur=None, prozesse=None, ausgabe=None, protokoll=print, streng=True):
    """Aufträge der Liste der Reihe nach (bis zu `prozesse` Arbeitsprozesse mit einem BLAS-Thread); passende
    Checkpoints werden übernommen, abweichende beiseitegelegt. Rückgabe {id: Status}."""
    a = lies_auftrag(pfad)
    prof, _ = profil_und_plan(a['gemeinsam'])
    git = formate.git_stand()
    if streng and (git is None or git.endswith('+geändert')):
        raise Fehler(f'Arbeitsbaum nicht sauber ({git}): Treiber und Auftragsliste vor den Rechnungen committen')
    P = int(prozesse or a['gemeinsam']['prozesse'])
    status = {}
    for job in a['auftraege']:
        if nur and job['id'] not in nur:
            continue
        _seeds_pruefen(job)
        w8, w8_sha = neulauf.werkzeug8_laden(a, job.get('werkzeug8'))
        key = schluessel(a, job, prof, w8_sha)
        ziel = os.path.join(ausgabe or a['gemeinsam']['ausgabe'], job['id'])
        s = neulauf.checkpoint(ziel, key)
        if s:
            protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]}: Checkpoint passt (Code {s["git"]}, '
                      f'{s["laufzeit_s"]} s) – übernommen')
            status[job['id']] = 'übernommen'
            continue
        if os.path.exists(ziel):
            beiseite = f'{ziel}.verworfen-{time.strftime("%Y%m%dT%H%M%S")}'
            shutil.move(ziel, beiseite)
            protokoll(f'{job["id"]}: Checkpoint fehlt, ist unvollständig oder passt nicht – beiseitegelegt: {beiseite}')
        os.makedirs(ziel)
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]}: {len(job["seeds"])} Kampagnen …')
        t0, start = time.perf_counter(), formate.zeitstempel()
        befunde = _rechne(job, a, w8, P)
        git_ende = formate.git_stand()
        if streng and git_ende != git:
            raise Fehler(f'{job["id"]}: Code während der Rechnung geändert ({git} → {git_ende})')
        meta = dict(auftrag=job['id'], szenario=job['szenario'], variante=job['variante'], art=job['art'],
                    ebene=job['ebene'], indizes=job['indizes'], seeds=job['seeds'], profil=prof.id,
                    profil_sha256=prof.sha256(), werkzeug8=job.get('werkzeug8'), werkzeug8_sha256=w8_sha,
                    verfahren=VARIANTEN[job['variante']].kennung(), plan=a['gemeinsam']['plan'],
                    n_min=a['gemeinsam']['n_min'], code_version=formate.code_version())
        name = f'ablauf_{job["id"]}'
        formate.schreibe_objekt(os.path.join(ziel, name), formate.kopf('bewertung', formate.synth_kennung(
            KENNUNG, job['id'])), dict(meta=meta, befunde=befunde))
        dateien = [name + x for x in ('.json', '.npz') if os.path.exists(os.path.join(ziel, name + x))]
        s = dict(auftrag=job['id'], schluessel=key, dateien={d: formate.sha256_datei(os.path.join(ziel, d))
                                                             for d in dateien},
                 git=git, git_ende=git_ende, start=start, ende=formate.zeitstempel(),
                 laufzeit_s=round(time.perf_counter() - t0, 1), prozesse=P,
                 kernsekunden=round(sum(b['laufzeit_s'] for b in befunde), 1))
        with open(os.path.join(ziel, 'schluessel.json'), 'w', encoding='utf-8') as f:
            f.write(formate.json_text(s))
        protokoll(f'[{time.strftime("%H:%M:%S")}] {job["id"]} fertig ({s["laufzeit_s"]} s, {s["kernsekunden"]} '
                  'Kernsekunden)')
        status[job['id']] = 'gerechnet'
    return status


def lies_ergebnisse(a, ausgabe=None):
    """Befunde aller Aufträge aus passenden Checkpoints: {Auftrags-ID: Befunde} und die Checkpoint-Angaben."""
    prof, _ = profil_und_plan(a['gemeinsam'])
    out, cp = {}, {}
    for job in a['auftraege']:
        _, w8_sha = neulauf.werkzeug8_laden(a, job.get('werkzeug8'))
        ziel = os.path.join(ausgabe or a['gemeinsam']['ausgabe'], job['id'])
        s = neulauf.checkpoint(ziel, schluessel(a, job, prof, w8_sha))
        if not s:
            raise Fehler(f'{job["id"]}: kein passender Checkpoint in {ziel} (zuerst harness ablauf-vergleich rechnen)')
        _, v = formate.lies_objekt(os.path.join(ziel, f'ablauf_{job["id"]}'), 'bewertung')
        out[job['id']] = v['befunde']
        cp[job['id']] = {k: s[k] for k in ('git', 'start', 'ende', 'laufzeit_s', 'prozesse', 'kernsekunden', 'dateien')}
    return out, cp


# ── Auftragsliste (einmalig) ──────────────────────────────────────────────────────────────────────────────
def _job(id_, sid, variante, indizes, art='schlank', ebene='H', seedregel='vergleich', werkzeug8=None):
    seeds = ([vergleichs_seeds(sid)[i] for i in indizes] if seedregel == 'vergleich'
             else [zusatz_seed(sid, i) for i in indizes])
    return dict(id=id_, szenario=sid, variante=variante, indizes=list(indizes), seeds=seeds, art=art, ebene=ebene,
                seedregel=seedregel, werkzeug8=werkzeug8)


def auftragsliste():
    """Vergleich (3 Systeme × 10 Seeds × 3 Varianten, Startsatz je System und Variante die Seeds 0 und 1), volle
    Ketten, Regelpfadfälle und die Fortsetzung; Werkzeug 8 A4 aus PR #21 nur als Testwert für die vollen Ketten."""
    jobs = []
    for sid in SYSTEME:
        for v in VARIANTEN:
            jobs.append(_job(f'{sid}-{v}-start', sid, v, range(N_START)))
    for sid in SYSTEME:
        for v in VARIANTEN:
            jobs.append(_job(f'{sid}-{v}-rest', sid, v, range(N_START, N_SEEDS)))
    for v in ('k_konsistent', 'wiederholungen'):
        jobs.append(_job(f'voll-N01-A4-{v}', 'N01-A4', v, [0], 'voll', werkzeug8='A4'))
        jobs.append(_job(f'voll-A04-R4-{v}', 'A04-R4', v, [0], 'voll', seedregel='zusatz', werkzeug8='A4'))
    jobs.append(_job('voll-Z-N01-A4-wiederholungen', 'N01-A4', 'wiederholungen', [0], 'voll', 'Z', werkzeug8='A4'))
    jobs.append(_job('voll-Z-A04-R4-wiederholungen', 'A04-R4', 'wiederholungen', [0], 'voll', 'Z', 'zusatz',
                     werkzeug8='A4'))
    for sid in ('S06-saettigung', 'H-fehlend', 'S02-kontrolllauf'):
        jobs.append(_job(f'regelpfad-{sid}', sid, 'wiederholungen', [0], seedregel='zusatz'))
    jobs.append(_job('fortsetzung-N01-V1G60h', 'N01-V1G60h', 'wiederholungen', [0], 'fortsetzung'))
    return jobs


def vorbereiten(doku=None):
    """Schreibt die Auftragsliste (einmalig, vor den Rechnungen zu committen)."""
    doku = doku or os.path.join(neulauf.WURZEL, DOKU_REL)
    os.makedirs(doku, exist_ok=True)
    prof = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=1000, h3_mc=1000, eps_ctrl_datensaetze=1000)
    w8_datei = 'docs/ap13_neulaeufe_2026-10-17/werkzeug8_A4'
    _, w8 = formate.lies_objekt(os.path.join(neulauf.WURZEL, w8_datei), 'werkzeug8')
    jobs = auftragsliste()
    n_kampagnen = sum(len(j['seeds']) * (2 if j['art'] == 'fortsetzung' else 1) for j in jobs)
    n_voll = sum(len(j['seeds']) for j in jobs if j['art'] == 'voll')
    a = dict(
        anweisung='ANWEISUNG_Claude_Code_AP13_kmax_Wiederholungen_2026-10-17', ausgangsstand=AUSGANGSSTAND,
        gemeinsam=dict(ausgabe=AUSGABE, prozesse=4, blas_threads_je_prozess=1, stufe=STUFE,
                       plan=dict(n0=20, n_pilot=20, n_bloecke=24), n_min=18, profil=prof.id,
                       profil_reduktion=dict(bootstrap_B=1000, h3_mc=1000, eps_ctrl_datensaetze=1000),
                       profil_sha256=prof.sha256(), seed_basis=SEED_BASIS,
                       seed_ableitung=dict(vergleich="zufall.unterseed(20261017, 'diagnose_g4', Szenario, 'L1', i) – "
                                                     'die ersten zehn Seeds der G4-Diagnose von PR #22',
                                           zusatz="zufall.unterseed(20261017, 'ablauf_voll', Szenario, 'L1', i)"),
                       zufallsstroeme=dict(p0="zufall.strom(seed, 'p0') (P0-Kalibrierdaten)",
                                           generator="zufall.strom(seed, 'generator') (geplante Läufe, Vorrat)",
                                           versuch="zufall.strom(seed, 'generator_versuch', Versuchsnummer)",
                                           ebene_z="zufall.strom(seed, 'generator_z_versuch', Kennung)",
                                           reihenfolge="zufall.strom(seed, 'reihenfolge') (Laufplan, danach "
                                                       'Wiederholungsplätze)',
                                           bootstrap="zufall.unterseed(seed, 'bootstrap') (Stufe 2) und "
                                                     "zufall.unterseed(seed, 'teil_b') (B⁰-Replikate)",
                                           eps_ctrl='Kampagnenseed (pilot.pilot_auswerten, in der Bindung von '
                                                    'Teil B vermerkt)'),
                       varianten={k: v.kennung() for k, v in VARIANTEN.items()}, fortsetzung_bis=FORTSETZUNG_BIS),
        werkzeug8=dict(A4=dict(datei=w8_datei, inhalt_sha256=formate.sha256_json(w8),
                               art='Testwert: Kalibrierung von PR #21 mit dem alten Ablauf, keine Kalibrierung des '
                                   'neuen Ablaufs')),
        budget=dict(kampagnenausfuehrungen=n_kampagnen, davon_voll=n_voll, grenze_kampagnen=120, grenze_voll=12,
                    grenze_prozesse=4, grenze_kernstunden=4.0,
                    zaehlung='je (System, Seed, Variante) eine Ausführung; Fortsetzung zählt doppelt (unterbrochen '
                             'und ununterbrochen)'),
        auftraege=jobs)
    if n_kampagnen > 120 or n_voll > 12:
        raise Fehler(f'Budget überschritten: {n_kampagnen} Kampagnen, {n_voll} volle')
    with open(os.path.join(doku, 'auftrag.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text(a))
    return a
