"""Berichtsteil der begrenzten Entwicklungsrechnung (harness.ablauf_vergleich): Auswertung der Checkpoints zu
maschinenlesbaren Ergebnissen (ergebnisse.json, CSV) und Berichtstabellen (bericht.md zwischen den Markierungen
<!-- tabelle:NAME --> … <!-- /tabelle -->). Gehört nicht zum Rechencode der Checkpoints; die Zahlen folgen allein aus den
gespeicherten Befunden. Kampagnenanteile mit 95-%-Wilson-Intervall; Läufe derselben Kampagne zählen nicht als
unabhängige Kampagnen. Keine Power- oder 0,95-Qualifikationsaussage.

Korrekturrunde vom 18.10.2026 (schreiben_korrektur): neu gerechnete Aufträge der Korrekturrunde zusammen mit den geprüft
unberührten Werten vom Stand davor (ergebnisse.json, Auftragsliste und kampagnen.csv aus Git am Kopf VORHER, Befunde aus
den alten Checkpoints mit den dort vermerkten Prüfsummen), Herkunft je Ergebnisgruppe und Zeile, Vorher/Nachher je
Kampagne mit Ursache, Rechenumfang getrennt und zusammen.
"""
import csv
import io
import json
import os
import re
import subprocess

import numpy as np
from scipy import stats

from .. import formate
from . import ablauf_vergleich as av, neulauf

PR22_KAMPAGNEN = 'docs/e3b_g4_diagnose_2026-10-17/g4_kampagnen.csv'
VARIANTEN = tuple(av.VARIANTEN)
NAMEN = dict(historisch='historisch', k_konsistent='k-konsistent ohne Wiederholungen',
             wiederholungen='k-konsistent mit Wiederholungen')


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, c - h)), float(min(1.0, c + h))


def _anteil(k, n):
    lo, hi = wilson(k, n)
    return dict(zaehler=int(k), nenner=int(n), rate=None if n == 0 else k / n, wilson95=[lo, hi])


def _mittel_se(x):
    x = np.asarray(x, float)
    return dict(mittel=float(x.mean()), se=float(x.std(ddof=1) / np.sqrt(x.size)) if x.size > 1 else None,
                min=float(x.min()), max=float(x.max()))


def vergleich(befunde):
    """Je System und Variante: gemeinsame Vollständigkeit, Auswertbarkeit, Ausschlüsse, Teil-B-Größen, Ablauf."""
    out = {}
    for sid in av.SYSTEME:
        for v in VARIANTEN:
            bs = sorted([b for b in befunde if b['szenario'] == sid and b['variante'] == v and b['art'] == 'schlank'],
                        key=lambda b: b['index'])
            if not bs:
                continue
            g4 = [b['phase1']['konfig_g4'] / b['phase1']['konfig_laeufe'] for b in bs]
            ung = [b['phase1']['konfig_ungueltig'] / b['phase1']['konfig_laeufe'] for b in bs]
            e = dict(n=len(bs), vollstaendig=_anteil(sum(b['vollstaendig'] for b in bs), len(bs)),
                     auswertbar=_mittel_se([b['auswertbar']['n'] for b in bs]),
                     min_gueltig=_mittel_se([b['auswertbar']['min_gueltig'] for b in bs]),
                     konfig_g4_je_lauf=_mittel_se(g4), konfig_ungueltig_je_lauf=_mittel_se(ung),
                     sigma_delta_F_mN=_mittel_se([1e3 * b['teil_b']['sigma_delta_K']['F'] for b in bs]),
                     p_hat=_mittel_se([b['teil_b']['p_hat'] for b in bs]),
                     arbeitspunkt={s: sum(b['teil_b']['arbeitspunkt'] == s for b in bs)
                                   for s in sorted({b['teil_b']['arbeitspunkt'] for b in bs})},
                     k=sorted({b['teil_b']['k'] for b in bs}), k_max=sorted({b['teil_b']['k_max'] for b in bs}))
            ab = [b['ablauf'] for b in bs if b.get('ablauf')]
            if ab:
                fertig = [a for a in ab if a['status'] == 'abgeschlossen']    # Laufzahl und Messzeit nur vollständig
                e['ablauf'] = dict(                                            # gelaufener Kampagnen vergleichbar
                    nicht_abgeschlossen=_anteil(sum(a['status'] != 'abgeschlossen' for a in ab), len(ab)),
                    halt_regeln={r: sum(a['halt'] == r for a in ab) for r in sorted({a['halt'] for a in ab
                                                                                      if a['halt']})},
                    zusaetzlich=_mittel_se([a['laufzahl']['zusaetzlich'] for a in ab]),
                    zusaetzlich_abgeschlossen=_mittel_se([a['laufzahl']['zusaetzlich'] for a in fertig]) if fertig
                    else None,
                    zeit_verhaeltnis_abgeschlossen=_mittel_se([a['messzeit_s']['realisiert_laeufe'] /
                                                               a['messzeit_s']['geplant_laeufe'] for a in fertig])
                    if fertig else None,
                    anlaesse=_summe([a['anlaesse'] for a in ab]), auswahl=_summe([a['auswahl'] for a in ab]),
                    auswahl_abgeschlossen=_summe([a['auswahl'] for a in fertig]),
                    grenzen=int(sum(a['grenzen'] for a in ab)), luecken=sorted({x for a in ab for x in a['luecken']}))
            out[f'{sid}/{v}'] = e
    return out


def _summe(ds):
    out = {}
    for d in ds:
        for k, x in d.items():
            out[k] = out.get(k, 0) + x
    return dict(sorted(out.items()))


def gepaart(befunde):
    """Gepaarte Unterschiede je System: k (historisch → k_konsistent) und Ablauf (k_konsistent → wiederholungen)."""
    out = {}
    for sid in av.SYSTEME:
        idx = {(b['variante'], b['index']): b for b in befunde if b['szenario'] == sid and b['art'] == 'schlank'}
        for name, (a, b) in (('k', ('historisch', 'k_konsistent')), ('ablauf', ('k_konsistent', 'wiederholungen'))):
            paare = [(idx[(a, i)], idx[(b, i)]) for i in range(av.N_SEEDS) if (a, i) in idx and (b, i) in idx]
            if not paare:
                continue
            out[f'{sid}/{name}'] = dict(
                n=len(paare), von=a, nach=b,
                vollstaendig_vorher=sum(x['vollstaendig'] for x, _ in paare),
                vollstaendig_nachher=sum(y['vollstaendig'] for _, y in paare),
                gewonnen=sum((not x['vollstaendig']) and y['vollstaendig'] for x, y in paare),
                verloren=sum(x['vollstaendig'] and not y['vollstaendig'] for x, y in paare),
                delta_konfig_g4=_mittel_se([y['phase1']['konfig_g4'] - x['phase1']['konfig_g4'] for x, y in paare]),
                delta_auswertbar=_mittel_se([y['auswertbar']['n'] - x['auswertbar']['n'] for x, y in paare]),
                delta_min_gueltig=_mittel_se([y['auswertbar']['min_gueltig'] - x['auswertbar']['min_gueltig']
                                              for x, y in paare]),
                delta_p_hat=_mittel_se([y['teil_b']['p_hat'] - x['teil_b']['p_hat'] for x, y in paare]))
    return out


def pr22_gegenprobe(befunde):
    """Variante „historisch“ gegen die gespeicherten Kampagnenwerte von PR #22 (gleiche Seeds, gleicher Rechenweg)."""
    with open(os.path.join(neulauf.WURZEL, PR22_KAMPAGNEN), encoding='utf-8') as f:
        alt = {(r['system'], int(r['kampagne'])): r for r in csv.DictReader(f)}
    zeilen, gleich = [], 0
    for b in befunde:
        if b['variante'] != 'historisch' or b['art'] != 'schlank':
            continue
        r = alt[(b['szenario'], b['index'])]
        z = dict(system=b['szenario'], kampagne=b['index'], seed_gleich=int(r['seed']) == b['seed'],
                 phase1_ungueltig=(int(r['phase1_ungueltig']), b['phase1']['n_ungueltig']),
                 p_hat=(float(r['p_hat']), b['teil_b']['p_hat']),
                 sigma_F_mN=(float(r['sigma_F_v0_mN']), 1e3 * b['teil_b']['sigma_delta_K']['F']),
                 k_pilot=(int(r['k_pilot']), b['teil_b']['k']))
        z['gleich'] = bool(z['seed_gleich'] and z['phase1_ungueltig'][0] == z['phase1_ungueltig'][1]
                           and abs(z['p_hat'][0] - z['p_hat'][1]) < 1e-6
                           and abs(z['sigma_F_mN'][0] - z['sigma_F_mN'][1]) < 1e-5 * max(1.0, z['sigma_F_mN'][0])
                           and z['k_pilot'][0] == z['k_pilot'][1])
        gleich += z['gleich']
        zeilen.append(z)
    return dict(n=len(zeilen), gleich=gleich, zeilen=zeilen,
                hinweis='PR #22 speichert p̂ und σ_Δ,F gerundet (CSV); verglichen mit relativer Toleranz 10⁻⁵')


def laufzeiten(cp, befunde):
    ks = sum(c['kernsekunden'] for c in cp.values())
    wand = sum(c['laufzeit_s'] for c in cp.values())
    je = {}
    for b in befunde:
        key = f'{b["art"]}/{b["ebene"]}/{b["variante"]}'
        je.setdefault(key, []).append(b['laufzeit_s'])
    return dict(kernsekunden=round(ks, 1), kernstunden=round(ks / 3600, 3), wandzeit_s=round(wand, 1),
                je_art={k: _mittel_se(v) for k, v in sorted(je.items())},
                kampagnen=len(befunde), voll=sum(b['art'] == 'voll' for b in befunde))


NORMATIV_GEMESSEN_S = dict(A4=78.0, V1G0=139.0, V1G60h=68.0)   # Softwaredokument, Abschnitt 5: eine Kampagne mit
#                                                               B = 10 000, H3-MC 10 000, ε_ctrl 10 000 (statisch, n = 20)
ZUSCHLAG_ABLAUF = 1.05                                         # zusätzliche Versuche des Ablaufs (gemessen 5,4 % Laufzeit)


def neulauf_abschaetzung(lz):
    """Grobe Rechenabschätzung künftiger Neuläufe aus den gemessenen Laufzeiten (nicht gestartet): untere Spanne aus
    dieser Rechnung (B = 1000) mit linear in B skaliertem Bootstrap-Anteil, obere aus den im Softwaredokument
    gemessenen Kampagnen mit normativen Replikatzahlen und einem Zuschlag für die zusätzlichen Versuche."""
    def t(key):
        e = lz['je_art'].get(key)
        return None if e is None else e['mittel']
    schlank, voll, z = t('schlank/H/wiederholungen'), t('voll/H/wiederholungen'), t('voll/Z/wiederholungen')
    if schlank is None or voll is None:
        return None
    boot = max(voll - schlank, 0.0)                    # Stufe 2 mit B = 1000 (reduziertes Profil)
    lo = schlank + 10 * boot                           # B = 10 000 normativ: Bootstrap-Anteil etwa linear in B
    hi = max(NORMATIV_GEMESSEN_S.values()) * ZUSCHLAG_ABLAUF
    n_kal = 2000                                       # 1000 Kalibrier- und 1000 Prüfkampagnen je System (normativ)

    def kh(s):
        return round(s / 3600, 1)
    return dict(
        sekunden_je_kampagne=dict(schlank=round(schlank, 2), voll_B1000=round(voll, 2), voll_B10000_linear=round(lo, 1),
                                  voll_normativ_gemessen=NORMATIV_GEMESSEN_S, zuschlag_ablauf=ZUSCHLAG_ABLAUF,
                                  ebene_Z_voll=None if z is None else round(z, 1)),
        kalibrierung_je_system_kernstunden=[kh(n_kal * lo), kh(n_kal * hi)],
        drei_referenzsysteme_kernstunden=[kh(3 * n_kal * lo), kh(3 * n_kal * hi)],
        planungssimulation_je_kandidat_kernstunden=[kh(n_kal * lo), kh(n_kal * hi)],
        zaehldiagnose_je_1000_kampagnen_kernstunden=kh(1000 * schlank),
        ebene_Z_je_10_kampagnen_kernstunden=None if z is None else kh(10 * z),
        annahmen=('untere Spanne: Laufzeiten dieser Rechnung (Ebene H, 24 Blöcke, B = 1000) mit linear auf B = 10 000 '
                  'skaliertem Bootstrap-Anteil; obere Spanne: die im Softwaredokument (Abschnitt 5) gemessenen '
                  'Kampagnen mit normativen Replikatzahlen (68–139 s, statisch) mit 5 % Zuschlag für die zusätzlichen '
                  'Versuche; je System 1000 Kalibrier- und 1000 Prüfkampagnen (normative Zahl), ohne Wiederholung bei '
                  'Poolen; Planungssimulation je Kandidat (n_min, n₀) und Paar (k, T_a) gleich teuer wie eine '
                  'Kalibrierung; nicht gestartet'))


# ── Tabellen ──────────────────────────────────────────────────────────────────────────────────────────────
def _zahl(x, n=2):
    if x is None:
        return '–'
    return f'{x:.{n}f}'.replace('.', ',')


def _proz(x, n=1):
    return '–' if x is None else f'{100 * x:.{n}f} %'.replace('.', ',')


def _w(a):
    lo, hi = a['wilson95']
    return f'{a["zaehler"]}/{a["nenner"]} [{_proz(lo, 0)}; {_proz(hi, 0)}]'


def tabellen(erg):
    v, g = erg['vergleich'], erg['gepaart']
    zeilen = ['| System | Variante | vollständig (95-%-Wilson) | auswertbar (Mittel, min) | min. gültige Läufe '
              '(Mittel) | G4 je Konfigurationslauf | p̂ (Mittel) | σ_Δ,F [mN] |', '|---|---|---|---|---|---|---|---|']
    for key, e in v.items():
        sid, var = key.split('/')
        zeilen.append(f'| {sid} | {NAMEN[var]} | {_w(e["vollstaendig"])} | {_zahl(e["auswertbar"]["mittel"], 1)}, '
                      f'{_zahl(e["auswertbar"]["min"], 0)} | {_zahl(e["min_gueltig"]["mittel"], 1)} | '
                      f'{_proz(e["konfig_g4_je_lauf"]["mittel"], 2)} | {_zahl(e["p_hat"]["mittel"], 3)} | '
                      f'{_zahl(e["sigma_delta_F_mN"]["mittel"], 3)} |')
    t_vergleich = '\n'.join(zeilen)
    zeilen = ['| System | Unterschied | vollständig vorher → nachher | gewonnen / verloren | Δ G4-Läufe (Mittel ± SE) '
              '| Δ auswertbar | Δ min. gültige Läufe |', '|---|---|---|---|---|---|---|']
    for key, e in g.items():
        sid, name = key.split('/')
        d = e['delta_konfig_g4']
        zeilen.append(f'| {sid} | {"k" if name == "k" else "Ablauf"} ({NAMEN[e["von"]]} → {NAMEN[e["nach"]]}) | '
                      f'{e["vollstaendig_vorher"]}/{e["n"]} → {e["vollstaendig_nachher"]}/{e["n"]} | '
                      f'{e["gewonnen"]} / {e["verloren"]} | {_zahl(d["mittel"], 1)} ± {_zahl(d["se"], 1)} | '
                      f'{_zahl(e["delta_auswertbar"]["mittel"], 1)} | {_zahl(e["delta_min_gueltig"]["mittel"], 1)} |')
    t_gepaart = '\n'.join(zeilen)
    zeilen = ['| System | nicht abgeschlossen (Halt/Abbruch) | Haltregeln | abgeschlossene Kampagnen: zusätzliche Läufe '
              '(Mittel, max) | abgeschlossene: Laufzeit realisiert/geplant (Mittel, max) | abgeschlossene: Plätze '
              'gültig / ersetzt / fehlend (Grenze, spät) | angehaltene: Plätze bis zum Halt gültig / ersetzt / fehlend, '
              'nicht gemessen |',
              '|---|---|---|---|---|---|---|']

    def plaetze(au, halt=False):
        ok, er = au.get('gueltig', 0), au.get('ersetzt', 0)
        gr, sp, fh = au.get('fehlt: Grenze ausgeschöpft', 0), au.get('fehlt: spät erkannt', 0), au.get('fehlt: Halt', 0)
        if halt:
            return f'{ok} / {er} / {gr + sp + fh}, {au.get("nicht gemessen", 0)}'
        return f'{ok} / {er} / {gr + sp} ({gr}, {sp})'
    for key, e in v.items():
        if 'ablauf' not in e:
            continue
        a = e['ablauf']
        hr = ', '.join(f'{k}: {x}' for k, x in a['halt_regeln'].items()) or '–'
        za, zv = a['zusaetzlich_abgeschlossen'], a['zeit_verhaeltnis_abgeschlossen']
        rest = {k: x - a['auswahl_abgeschlossen'].get(k, 0) for k, x in a['auswahl'].items()}
        zeilen.append(f'| {key.split("/")[0]} | {_w(a["nicht_abgeschlossen"])} | {hr} | '
                      f'{_zahl(za["mittel"], 1)}, {_zahl(za["max"], 0)} | '
                      f'{_zahl(zv["mittel"], 3)}, {_zahl(zv["max"], 3)} | {plaetze(a["auswahl_abgeschlossen"])} | '
                      f'{plaetze(rest, True) if any(rest.values()) else "–"} |')
    t_ablauf = '\n'.join(zeilen)
    zeilen = ['| Anlass (Rolle: Grund) | ' + ' | '.join(s for s in av.SYSTEME) + ' |',
              '|---|' + '---|' * len(av.SYSTEME)]
    alle = sorted({k for key, e in v.items() if 'ablauf' in e for k in e['ablauf']['anlaesse']})
    for k in alle:
        werte = [str(v.get(f'{s}/wiederholungen', {}).get('ablauf', {}).get('anlaesse', {}).get(k, 0))
                 for s in av.SYSTEME]
        zeilen.append(f'| {k} | ' + ' | '.join(werte) + ' |')
    t_anlaesse = '\n'.join(zeilen)
    zeilen = ['| Auftrag | Status | zusätzliche Läufe | Auswahl | H1 | H2 | H3 | H4 | E3 | Datenlage = schlank |',
              '|---|---|---|---|---|---|---|---|---|---|']
    for b in erg['voll']:
        a = b.get('ablauf') or {}
        vo = b['voll']
        zeilen.append(f'| {b["szenario"]} {NAMEN[b["variante"]]} Ebene {b["ebene"]} | {a.get("status", "statisch")} | '
                      f'{(a.get("laufzahl") or {}).get("zusaetzlich", 0)} | '
                      f'{", ".join(f"{k}: {x}" for k, x in (a.get("auswahl") or {}).items()) or "–"} | '
                      f'{vo["H1"]["ausgang"]} | {vo["H2"]["ausgang"]} | {vo["H3"]["ausgang"]} | {vo["H4"]["ausgang"]} | '
                      f'{(vo.get("E3") or {}).get("bewertung") or (vo.get("E3") or {}).get("status") or vo["E3_grund"]}'
                      f' | {"ja" if vo["datenlage_gleich"] else "nein"} |')
    t_voll = '\n'.join(zeilen)
    zeilen = ['| Fall | Status | Halt | zusätzliche Läufe | Ersatz und Fehlen | auswertbar | vollständig |',
              '|---|---|---|---|---|---|---|']
    for b in erg['regelpfad']:
        a = b['ablauf']
        zeilen.append(f'| {b["szenario"]} | {a["status"]} | {a["halt"] or "–"} | {a["laufzahl"]["zusaetzlich"]} | '
                      f'{", ".join(f"{k}: {x}" for k, x in a["auswahl"].items())} | {b["auswertbar"]["n"]}/21 | '
                      f'{"ja" if b["vollstaendig"] else "nein"} |')
    t_regelpfad = '\n'.join(zeilen)
    lz = erg['laufzeiten']
    zeilen = ['| Art | Kampagnen | Sekunden je Kampagne (Mittel, max) |', '|---|---|---|']
    for k, e in lz['je_art'].items():
        n = sum(1 for b in erg.get('neu', erg['alle']) if f'{b["art"]}/{b["ebene"]}/{b["variante"]}' == k)
        zeilen.append(f'| {k} | {n} | {_zahl(e["mittel"], 1)}, {_zahl(e["max"], 1)} |')
    zeilen.append(f'| zusammen | {lz["kampagnen"]} | {_zahl(lz["kernsekunden"], 0)} Kernsekunden '
                  f'({_zahl(lz["kernstunden"], 3)} Kernstunden), Wandzeit {_zahl(lz["wandzeit_s"], 0)} s |')
    t_laufzeit = '\n'.join(zeilen)
    ab = erg['abschaetzung'] or {}

    def sp(x):
        return '–' if x is None else (f'{_zahl(x[0], 1)}–{_zahl(x[1], 1)}' if isinstance(x, list) else _zahl(x, 1))
    zeilen = ['| künftiger Lauf (nicht gestartet) | Kernstunden (grob) |', '|---|---|',
              f'| Kalibrier- und Prüfsimulation von c je System (1000 + 1000 Kampagnen, B = 10 000) | '
              f'{sp(ab.get("kalibrierung_je_system_kernstunden"))} |',
              f'| dasselbe für A4, V1-G0 und V1-G60h | {sp(ab.get("drei_referenzsysteme_kernstunden"))} |',
              f'| Planungssimulation je Kandidat (n_min, n₀) und Paar (k, T_a) | '
              f'{sp(ab.get("planungssimulation_je_kandidat_kernstunden"))} |',
              f'| Zähl- und Ablaufdiagnose ohne Stufe 2 je 1000 Kampagnen | '
              f'{sp(ab.get("zaehldiagnose_je_1000_kampagnen_kernstunden"))} |',
              f'| Ebene Z/Stufe 1 mit Stufe 2 (B = 1000) je 10 Kampagnen | {sp(ab.get("ebene_Z_je_10_kampagnen_kernstunden"))} |']
    t_abschaetzung = '\n'.join(zeilen)
    return dict(vergleich=t_vergleich, gepaart=t_gepaart, ablauf=t_ablauf, anlaesse=t_anlaesse, voll=t_voll,
                regelpfad=t_regelpfad, laufzeit=t_laufzeit, abschaetzung=t_abschaetzung)


def auswerten(pfad=None, ausgabe=None):
    a = av.lies_auftrag(pfad or av.AUFTRAG)
    jobs, cp = av.lies_ergebnisse(a, ausgabe)
    alle = [b for bs in jobs.values() for b in bs]
    art = {j['id']: (j['art'], j['seedregel']) for j in a['auftraege']}
    vergl = [b for jid, bs in jobs.items() if art[jid] == ('schlank', 'vergleich') for b in bs]
    voll = [b for jid, bs in jobs.items() if art[jid][0] == 'voll' for b in bs]
    regel = [b for jid, bs in jobs.items() if art[jid] == ('schlank', 'zusatz') for b in bs]
    fort = [b for jid, bs in jobs.items() if art[jid][0] == 'fortsetzung' for b in bs]
    lz = laufzeiten(cp, alle)
    erg = dict(auftrag=dict(datei=f'{av.DOKU_REL}/auftrag.json', git_blob=neulauf.git_blob(pfad or av.AUFTRAG),
                            budget=a['budget']),
               checkpoints=cp, vergleich=vergleich(vergl), gepaart=gepaart(vergl), pr22=pr22_gegenprobe(vergl),
               voll=voll, regelpfad=regel, fortsetzung=fort, laufzeiten=lz, abschaetzung=neulauf_abschaetzung(lz),
               alle=alle)
    return erg


def schreiben(pfad=None, ausgabe=None, doku=None):
    """ergebnisse.json, kampagnen.csv und die Tabellen in bericht.md (zwischen den Markierungen)."""
    doku = doku or os.path.join(neulauf.WURZEL, av.DOKU_REL)
    erg = auswerten(pfad, ausgabe)
    t = tabellen(erg)
    kompakt = {k: v for k, v in erg.items() if k != 'alle'}
    with open(os.path.join(doku, 'ergebnisse.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text(kompakt))
    _csv(os.path.join(doku, 'kampagnen.csv'), erg['alle'])
    bpfad = os.path.join(doku, 'bericht.md')
    if os.path.exists(bpfad):
        with open(bpfad, encoding='utf-8') as f:
            text = f.read()
        with open(bpfad, 'w', encoding='utf-8') as f:
            f.write(einsetzen(text, t))
    return dict(ergebnisse=f'{av.DOKU_REL}/ergebnisse.json', kampagnen=len(erg['alle']), pr22=erg['pr22']['gleich'],
                laufzeiten=erg['laufzeiten']['kernstunden'])


def _csv(pfad, alle, herkunft=False):
    """Eine Zeile je Kampagne; mit herkunft zusätzlich die Herkunft der Zeile (neu gerechnet oder übernommen)."""
    spalten = ('szenario', 'variante', 'index', 'seed', 'art', 'ebene', 'vollstaendig', 'auswertbar', 'min_gueltig',
               'konfig_laeufe', 'konfig_ungueltig', 'konfig_g4', 'p_hat', 'sigma_F_mN', 'k', 'arbeitspunkt', 'status',
               'halt', 'zusaetzlich', 'zeit_realisiert_s', 'zeit_geplant_s', 'laufzeit_s') + (('herkunft',) if herkunft else ())
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(spalten)
        for b in sorted(alle, key=lambda b: (b['art'], b['szenario'], b['variante'], b['ebene'], b['index'],
                                             b.get('herkunft', ''))):
            ab = b.get('ablauf') or {}
            w.writerow([b['szenario'], b['variante'], b['index'], b['seed'], b['art'], b['ebene'], int(b['vollstaendig']),
                        b['auswertbar']['n'], b['auswertbar']['min_gueltig'], b['phase1']['konfig_laeufe'],
                        b['phase1']['konfig_ungueltig'], b['phase1']['konfig_g4'], repr(b['teil_b']['p_hat']),
                        repr(1e3 * b['teil_b']['sigma_delta_K']['F']), b['teil_b']['k'], b['teil_b']['arbeitspunkt'],
                        ab.get('status', 'statisch'), ab.get('halt') or '', (ab.get('laufzahl') or {}).get('zusaetzlich', 0),
                        (ab.get('messzeit_s') or {}).get('realisiert_laeufe', ''),
                        (ab.get('messzeit_s') or {}).get('geplant_laeufe', ''), b['laufzeit_s']]
                       + ([b.get('herkunft', '')] if herkunft else []))


def einsetzen(text, tabellen):
    """Tabellen zwischen <!-- tabelle:NAME --> und der nächsten <!-- /tabelle --> einsetzen; der Text außerhalb der
    Markierungen bleibt unverändert, auch bei leeren Markierungspaaren."""
    for name, tab in tabellen.items():
        text = re.sub(rf'(<!-- tabelle:{name} -->\n).*?(<!-- /tabelle -->)',
                      lambda m, tab=tab: m.group(1) + tab + '\n' + m.group(2), text, flags=re.S)
    return text


# ── Korrekturrunde vom 18.10.2026 ──────────────────────────────────────────────────────────────────────
VORHER = av.KORREKTUR_VORHER                     # Kopf von PR #23 vor der Korrekturrunde (Ergebnisse vom Rechenstand
VORHER_RECHENSTAND = av.BISHER['rechenstand']    # 13f2a20, committet in f33f205)
KAMPAGNENSCHLUESSEL = ('szenario', 'variante', 'art', 'ebene', 'index')


def _git_show(rev, pfad):
    r = subprocess.run(['git', '-C', neulauf.WURZEL, 'show', f'{rev}:{pfad}'], capture_output=True, text=True)
    if r.returncode:
        raise av.Fehler(f'{pfad} am Stand {rev[:7]} nicht lesbar: {r.stderr.strip()}')
    return r.stdout


def _schluessel(b):
    return tuple(b[k] for k in KAMPAGNENSCHLUESSEL)


def vorher_lesen(ausgabe=None):
    """Stand vor der Korrektur: ergebnisse.json, Auftragsliste und kampagnen.csv aus Git (VORHER) und die Befunde je
    Kampagne aus den alten Checkpoints, geprüft gegen die in ergebnisse.json vermerkten Prüfsummen und gegen die CSV."""
    erg = json.loads(_git_show(VORHER, f'{av.DOKU_REL}/ergebnisse.json'))
    a = json.loads(_git_show(VORHER, f'{av.DOKU_REL}/auftrag.json'))
    zeilen = list(csv.DictReader(io.StringIO(_git_show(VORHER, f'{av.DOKU_REL}/kampagnen.csv'))))
    befunde = {}
    for job in a['auftraege']:
        ziel = os.path.join(ausgabe or av.AUSGABE, job['id'])
        for d, h in erg['checkpoints'][job['id']]['dateien'].items():
            if formate.sha256_datei(os.path.join(ziel, d)) != h:
                raise av.Fehler(f'{job["id"]}: alter Checkpoint {d} ≠ Prüfsumme in ergebnisse.json ({VORHER[:7]})')
        _, v = formate.lies_objekt(os.path.join(ziel, f'ablauf_{job["id"]}'), 'bewertung')
        befunde[job['id']] = v['befunde']
    alle = [b for bs in befunde.values() for b in bs]
    csv_idx = {(z['szenario'], z['variante'], z['art'], z['ebene'], int(z['index'])): z for z in zeilen}
    for b in alle:
        z = csv_idx[_schluessel(b)]
        if (int(z['vollstaendig']) != int(b['vollstaendig']) or int(z['auswertbar']) != b['auswertbar']['n']
                or z['p_hat'] != repr(b['teil_b']['p_hat'])):
            raise av.Fehler(f'alter Befund {_schluessel(b)} ≠ kampagnen.csv ({VORHER[:7]})')
    return dict(ergebnisse=erg, auftrag=a, kampagnen=zeilen, befunde=befunde, alle=alle)


def _plaetze(b):
    """Status je Platz (Konfiguration|Block); nicht aufgeführte Plätze sind im ersten Versuch gültig."""
    return dict((b.get('ablauf') or {}).get('auswahl_status') or {})


def _ursache(alt, neu, d):
    """Ursache der Unterschiede einer Kampagne aus den Angaben beider Befunde."""
    an = neu.get('ablauf') or {}
    xs = an.get('x_strich') or []
    gruende = []
    ab = next((x for x in xs if x.get('vorpruefung_ablauf_1')), None)
    if ab:
        gruende.append(f'Korrektur 1: X′ {ab["versuch"]} ({ab["konfiguration"]}, Block {ab["block"]}) hätte unter '
                       f'ablauf-1 nach der Vorprüfung gegen R₀ ein R₁ erhalten (|Δ⟨N⟩| = '
                       f'{1e3 * ab["abweichung_r0_N"]:.1f} mN > ε_ctrl); jetzt R₂/R₃, ab dort verläuft der Ablauf anders')
    offen = [x for x in xs if x.get('g1') is True and not x.get('vorgesehen')]
    if offen:
        gruende.append('Korrektur 1: X′ ' + ', '.join(x['versuch'] for x in offen) + ' mit unvollständiger Klammer: '
                       'S1 nicht prüfbar statt S1-Halt')
    if an.get('s2_waehrend_halt'):
        gruende.append(f'Korrektur 3: {an["s2_waehrend_halt"]} S2 während eines anderen Halts gezählt')
    u = d['unterschiede']
    erklaert = set()
    if 'grund' in u and 'halt' not in u and 'status' not in u:
        neu_g = u['grund'][1] or ''
        if 'X′' in neu_g:
            gruende.append('Haltgrund nennt jetzt die Klammer R₂/R₃ von X′ (Korrektur 1); Halt und Zeitpunkt gleich')
        elif 'Kontrolllauf' in neu_g:
            gruende.append('Halttext für S2 im Kontrolllauf: ŷ¹ ungültig statt Ausschluss der Konfiguration '
                           '(Korrektur 3); Halt und Zeitpunkt gleich')
        else:
            gruende.append('Haltgrund (Text) geändert; Halt und Zeitpunkt gleich')
        erklaert |= {'grund'}
        if 'sperren' in u and len(u['sperren'][0] or []) == len(u['sperren'][1] or []):
            erklaert.add('sperren')                                     # Sperrtext enthält den Haltgrund
    if d['plaetze'] and not ab and not offen:
        wechsel = sorted({f'{a} → {n}' for a, n in d['plaetze'].values()})
        gruende.append('Platzstatus aus strukturierten Angaben (Korrektur 1, kein anderer Ablauf): ' + '; '.join(wechsel))
        erklaert.add('auswahl')
    rest = (set(u) - erklaert) | ({'rollen'} if d['rollen'] else set()) | (
        {'auswahl'} if d['auswahl'] and 'auswahl' not in erklaert else set())
    if not d['gleich'] and rest and not ab and not offen and not an.get('s2_waehrend_halt'):
        gruende.append('ungeklärt: ' + ', '.join(sorted(rest)))
    return gruende


def vorher_nachher_kampagne(alt, neu):
    """Unterschiede einer Kampagne zwischen dem Stand vor der Korrektur (ablauf-1) und dem korrigierten Ablauf."""
    aa, an = alt.get('ablauf') or {}, neu.get('ablauf') or {}

    def lz(a, k):
        return (a.get('laufzahl') or {}).get(k)

    def mz(a, k):
        return (a.get('messzeit_s') or {}).get(k)
    felder = dict(status=(aa.get('status'), an.get('status')), halt=(aa.get('halt'), an.get('halt')),
                  grund=(aa.get('grund'), an.get('grund')), vollstaendig=(alt['vollstaendig'], neu['vollstaendig']),
                  auswertbar=(alt['auswertbar']['n'], neu['auswertbar']['n']),
                  min_gueltig=(alt['auswertbar']['min_gueltig'], neu['auswertbar']['min_gueltig']),
                  ausgefuehrt=(lz(aa, 'ausgefuehrt'), lz(an, 'ausgefuehrt')),
                  zusaetzlich=(lz(aa, 'zusaetzlich'), lz(an, 'zusaetzlich')),
                  laufzeit_realisiert_s=(mz(aa, 'realisiert_laeufe'), mz(an, 'realisiert_laeufe')),
                  spanne_realisiert_s=(mz(aa, 'realisiert_spanne'), mz(an, 'realisiert_spanne')),
                  konfig_g4=(alt['phase1']['konfig_g4'], neu['phase1']['konfig_g4']),
                  S2=(alt['phase1']['S2'], neu['phase1']['S2']), sperren=(alt['sperren'], neu['sperren']),
                  halte=(aa.get('halte'), an.get('halte')))
    if 'voll' in alt or 'voll' in neu:                                  # Entscheidungen der vollen Kette
        va, vn = alt.get('voll') or {}, neu.get('voll') or {}
        for k in ('H0', 'H1', 'H1Z', 'H2', 'H3', 'H4', 'E3', 'E3_grund', 'n_auswertbar', 'yhat1_gueltig',
                  'datenlage_gleich'):
            felder[f'voll_{k}'] = (va.get(k), vn.get(k))
    unterschiede = {k: list(v) for k, v in felder.items() if v[0] != v[1]}
    ra, rn = aa.get('rollen') or {}, an.get('rollen') or {}
    rollen = {r: [ra.get(r, 0), rn.get(r, 0)] for r in sorted(set(ra) | set(rn)) if ra.get(r, 0) != rn.get(r, 0)}
    sa, sn = aa.get('auswahl') or {}, an.get('auswahl') or {}
    auswahl = {s: [sa.get(s, 0), sn.get(s, 0)] for s in sorted(set(sa) | set(sn)) if sa.get(s, 0) != sn.get(s, 0)}
    pa, pn = _plaetze(alt), _plaetze(neu)
    plaetze = {p: [pa.get(p, 'gueltig'), pn.get(p, 'gueltig')] for p in sorted(set(pa) | set(pn))
               if pa.get(p, 'gueltig') != pn.get(p, 'gueltig')}
    d = dict(gleich=not (unterschiede or rollen or auswahl or plaetze), unterschiede=unterschiede, rollen=rollen,
             auswahl=auswahl, plaetze=plaetze, teil_b_gleich=alt['teil_b'] == neu['teil_b'],
             x_strich=an.get('x_strich') or [], s2_bilanz=an.get('s2_bilanz'))
    d['ursache'] = _ursache(alt, neu, d)
    return d


def vorher_nachher(vorher, neu_befunde):
    """Je neu gerechnete Kampagne des Ablaufs der Vergleich mit ihrem Gegenstück vor der Korrektur."""
    alt = {_schluessel(b): b for b in vorher['alle']}
    out = []
    for b in neu_befunde:
        a = alt.get(_schluessel(b))
        if a is None or a['seed'] != b['seed']:
            raise av.Fehler(f'kein Gegenstück mit gleichem Seed vor der Korrektur für {_schluessel(b)}')
        out.append(dict(zip(KAMPAGNENSCHLUESSEL, _schluessel(b)), seed=b['seed'], **vorher_nachher_kampagne(a, b)))
    return out


def _halt_art(a):
    """S1 nach Nullpunktalarm, S1 nach X′, S3 … aus Regel und Grund des Ablaufs."""
    if not a.get('halt'):
        return None
    g = a.get('grund') or ''
    if a['halt'] == 'S1':
        return 'S1 X′' if 'X′' in g else ('S1 Nullpunktalarm' if 'Nullpunktalarm' in g else 'S1')
    return a['halt']


def summen_ablauf(befunde):
    """Kennzahlen des Ablaufs je System (Variante mit Wiederholungen, Vergleichskampagnen) für Vorher/Nachher."""
    out = {}
    for sid in av.SYSTEME:
        bs = [b for b in befunde if b['szenario'] == sid and b['variante'] == 'wiederholungen' and b['art'] == 'schlank']
        if not bs:
            continue
        ab = [b['ablauf'] for b in bs]
        fertig = [a for a in ab if a['status'] == 'abgeschlossen']
        halte = {}
        for a in ab:
            h = _halt_art(a)
            if h:
                halte[h] = halte.get(h, 0) + 1
        au = _summe([a['auswahl'] for a in fertig])
        r = _summe([a['rollen'] for a in ab])
        xs = [x for a in ab for x in (a.get('x_strich') or [])]
        out[sid] = dict(
            n=len(bs), vollstaendig=sum(b['vollstaendig'] for b in bs), abgeschlossen=len(fertig), halte=halte,
            zusaetzlich=sum(a['laufzahl']['zusaetzlich'] for a in ab),
            zeit_verhaeltnis_abgeschlossen=None if not fertig else float(np.mean(
                [a['messzeit_s']['realisiert_laeufe'] / a['messzeit_s']['geplant_laeufe'] for a in fertig])),
            plaetze_abgeschlossen=dict(gueltig=au.get('gueltig', 0), ersetzt=au.get('ersetzt', 0),
                                       grenze=au.get('fehlt: Grenze ausgeschöpft', 0),
                                       spaet=au.get('fehlt: spät erkannt', 0),
                                       s1_nicht_pruefbar=au.get('fehlt: S1 nicht prüfbar', 0),
                                       sonst=sum(v for k, v in au.items() if k.startswith('fehlt') and k not in (
                                           'fehlt: Grenze ausgeschöpft', 'fehlt: spät erkannt',
                                           'fehlt: S1 nicht prüfbar'))),
            rollen=dict(R1=r.get('R1', 0), R2=r.get('R2', 0), X_strich=r.get('X_strich', 0), R3=r.get('R3', 0)),
            x_strich=None if not any('x_strich' in a for a in ab) else _x_strich_summe(
                xs, [b['teil_b']['eps_ctrl'] for b in bs for _ in (b['ablauf'].get('x_strich') or [])]))
    return out


def _x_strich_summe(xs, eps):
    """X′: Zahl, mit G1-Prüfung (gegen die Klammer R₂/R₃ oder nicht), gültig, S1, S1 nicht prüfbar, aus anderem Grund
    ungültig (§6), Stellen mit R₁ unter ablauf-1 und das größte Verhältnis |⟨N⟩_X′ − ⟨N⟩_R₀|/ε_ctrl."""
    geprueft = [x for x in xs if x.get('g1') in (True, False)]
    q = [x['abweichung_r0_N'] / e for x, e in zip(xs, eps) if x.get('abweichung_r0_N') is not None]
    return dict(n=len(xs), g1_geprueft=len(geprueft), klammer_r2_r3=sum(bool(x['vorgesehen']) for x in geprueft),
                gueltig=sum(x['gueltig'] for x in xs), s1=sum(x.get('halt') == 'S1' for x in xs),
                s1_nicht_pruefbar=sum(x.get('s1') == 'nicht prüfbar' for x in xs),
                andere_ungueltig=sum(x.get('g1') is None and not x['gueltig'] for x in xs),
                vorpruefung_ablauf_1=sum(bool(x.get('vorpruefung_ablauf_1')) for x in xs),
                max_verhaeltnis_eps=max(q) if q else None)


HERKUNFT_NEU = 'neu gerechnet (Korrekturrunde, ablauf-2)'
HERKUNFT_ALT = f'übernommen vom Rechenstand {VORHER_RECHENSTAND} (unberührt, geprüft)'
HERKUNFT_HIST = f'Stand ablauf-1 (Rechenstand {VORHER_RECHENSTAND}), nicht neu gerechnet'


def _herkunft(b, quelle):
    return dict(b, herkunft=quelle)


def auswerten_korrektur(pfad=None, ausgabe=None, vorher_ausgabe=None):
    """Ergebnisse nach der Korrekturrunde: neu gerechnete Aufträge (Checkpoints der Korrekturrunde) zusammen mit den
    geprüft unberührten statischen Werten und dem nicht neu gerechneten Fortsetzungsfall vor der Korrektur; dazu
    Stichprobe der statischen Varianten, Vorher/Nachher je Kampagne und je System, Rechenumfang getrennt und zusammen."""
    pfad = pfad or av.KORREKTUR_AUFTRAG
    a = av.lies_auftrag(pfad)
    jobs, cp = av.lies_ergebnisse(a, ausgabe)
    art = {j['id']: (j['art'], j['seedregel'], j['variante']) for j in a['auftraege']}
    vh = vorher_lesen(vorher_ausgabe)
    neu_vergl = [b for jid, bs in jobs.items() if art[jid] == ('schlank', 'vergleich', 'wiederholungen') for b in bs]
    stich = [b for jid, bs in jobs.items() if art[jid][:2] == ('schlank', 'vergleich') and art[jid][2] != 'wiederholungen'
             for b in bs]
    neu_voll = [b for jid, bs in jobs.items() if art[jid][0] == 'voll' for b in bs]
    neu_regel = [b for jid, bs in jobs.items() if art[jid][:2] == ('schlank', 'zusatz') for b in bs]
    alt_statisch = [b for b in vh['alle'] if b['art'] == 'schlank' and b['variante'] != 'wiederholungen']
    alt_voll_statisch = [b for b in vh['alle'] if b['art'] == 'voll' and b['variante'] != 'wiederholungen']
    alt_fort = [b for b in vh['alle'] if b['art'] == 'fortsetzung']
    alt_idx = {_schluessel(b): b for b in vh['alle']}
    stichprobe = []
    for b in stich:
        x = alt_idx[_schluessel(b)]
        abw = sorted(k for k in set(x) | set(b) if k != 'laufzeit_s' and x.get(k) != b.get(k))
        stichprobe.append(dict(zip(KAMPAGNENSCHLUESSEL, _schluessel(b)), seed=b['seed'], gleich=not abw,
                               abweichungen=abw))
    if any(not s['gleich'] for s in stichprobe):
        raise av.Fehler(f'statische Stichprobe weicht vom Stand vor der Korrektur ab: {stichprobe}')
    vergl = alt_statisch + neu_vergl
    vn = vorher_nachher(vh, neu_vergl + neu_voll + neu_regel)
    alt_wdh = [b for b in vh['alle'] if b['art'] == 'schlank' and b['variante'] == 'wiederholungen'
               and b['szenario'] in av.SYSTEME]
    lz = laufzeiten(cp, [b for bs in jobs.values() for b in bs])
    bisher = a['budget']['bisher']
    n_neu = sum(len(j['seeds']) * (2 if j['art'] == 'fortsetzung' else 1) for j in a['auftraege'])
    n_voll = sum(len(j['seeds']) for j in a['auftraege'] if j['art'] == 'voll')
    alle = ([_herkunft(b, HERKUNFT_ALT) for b in alt_statisch + alt_voll_statisch]
            + [_herkunft(b, HERKUNFT_NEU) for b in neu_vergl + neu_voll + neu_regel]
            + [_herkunft(b, HERKUNFT_HIST) for b in alt_fort]
            + [_herkunft(b, 'neu gerechnet (Stichprobe der statischen Varianten, gleich dem Stand vor der Korrektur)')
               for b in stich])
    erg = dict(
        auftrag=dict(datei=f'{av.DOKU_REL}/{os.path.basename(pfad)}', git_blob=neulauf.git_blob(pfad),
                     budget=a['budget'], urspruenglich=f'{av.DOKU_REL}/auftrag.json'),
        vorher=dict(stand=VORHER, rechenstand=VORHER_RECHENSTAND, ablauf_version='ablauf-1',
                    checkpoints=f'{av.AUSGABE} (Prüfsummen wie in ergebnisse.json am Stand {VORHER[:7]})'),
        herkunft=dict(vergleich_historisch=HERKUNFT_ALT, vergleich_k_konsistent=HERKUNFT_ALT,
                      vergleich_wiederholungen=HERKUNFT_NEU, pr22=HERKUNFT_ALT, voll_statisch=HERKUNFT_ALT,
                      voll_ablauf=HERKUNFT_NEU, regelpfad=HERKUNFT_NEU, fortsetzung=HERKUNFT_HIST,
                      abschaetzung='übernommen (Laufzeiten der Rechnung vom 17.10.2026, Rechenstand 13f2a20); mit '
                                   'den Laufzeiten der Korrekturrunde: abschaetzung_korrektur'),
        checkpoints=cp, vergleich=vergleich(vergl), gepaart=gepaart(vergl), pr22=pr22_gegenprobe(vergl),
        voll=[_herkunft(b, HERKUNFT_ALT) for b in alt_voll_statisch] + [_herkunft(b, HERKUNFT_NEU) for b in neu_voll],
        regelpfad=neu_regel, fortsetzung=[_herkunft(b, HERKUNFT_HIST) for b in alt_fort],
        stichprobe_statisch=stichprobe, vorher_nachher=vn,
        vorher_nachher_summen=dict(vorher=summen_ablauf(alt_wdh), nachher=summen_ablauf(neu_vergl)),
        laufzeiten=vh['ergebnisse']['laufzeiten'], abschaetzung=vh['ergebnisse']['abschaetzung'],
        laufzeiten_korrektur=lz, abschaetzung_korrektur=neulauf_abschaetzung(lz),
        rechenumfang=dict(bisher=bisher, korrektur=dict(ausfuehrungen=n_neu, voll=n_voll,
                                                        grenzen=dict(kampagnen=a['budget']['grenze_kampagnen'],
                                                                     voll=a['budget']['grenze_voll'])),
                          zusammen=dict(ausfuehrungen=bisher['ausfuehrungen'] + n_neu, voll=bisher['voll'] + n_voll)),
        alle=alle, neu=[b for bs in jobs.values() for b in bs])
    return erg


def _halte_text(h):
    return ', '.join(f'{k}: {v}' for k, v in sorted(h.items())) or '–'


def tabellen_korrektur(erg):
    """Zusätzliche Tabellen der Korrekturrunde: Vorher/Nachher je System und Größe, Kampagnen mit Unterschieden,
    Herkunft je Ergebnisgruppe, Rechenumfang getrennt und zusammen."""
    s0, s1 = erg['vorher_nachher_summen']['vorher'], erg['vorher_nachher_summen']['nachher']
    zeilen = ['| System | Größe | vorher (ablauf-1, Rechenstand 13f2a20) | nachher (ablauf-2) |', '|---|---|---|---|']
    for sid in av.SYSTEME:
        a, b = s0.get(sid), s1.get(sid)
        if not a or not b:
            continue

        def pl(x):
            p = x['plaetze_abgeschlossen']
            return (f'{p["ersetzt"]} / {p["grenze"] + p["spaet"] + p["s1_nicht_pruefbar"] + p["sonst"]} '
                    f'({p["grenze"]}, {p["spaet"]}, {p["s1_nicht_pruefbar"]})')
        zeilen += [f'| {sid} | gemeinsam vollständig | {a["vollstaendig"]}/{a["n"]} | {b["vollstaendig"]}/{b["n"]} |',
                   f'| {sid} | Halte | {_halte_text(a["halte"])} | {_halte_text(b["halte"])} |',
                   f'| {sid} | abgeschlossene: ersetzt / fehlend (Grenze, spät, S1 nicht prüfbar) | {pl(a)} | {pl(b)} |',
                   f'| {sid} | zusätzliche Versuche (Summe) | {a["zusaetzlich"]} | {b["zusaetzlich"]} |',
                   f'| {sid} | R₁ / R₂ / X′ / R₃ | ' + ' / '.join(str(a['rollen'][r]) for r in ('R1', 'R2', 'X_strich', 'R3'))
                   + ' | ' + ' / '.join(str(b['rollen'][r]) for r in ('R1', 'R2', 'X_strich', 'R3')) + ' |',
                   f'| {sid} | abgeschlossene: Laufzeit realisiert/geplant (Mittel) | '
                   f'{_zahl(a["zeit_verhaeltnis_abgeschlossen"], 3)} | {_zahl(b["zeit_verhaeltnis_abgeschlossen"], 3)} |']
        x = b.get('x_strich')
        if x:
            zeilen.append(f'| {sid} | X′: mit G1-Prüfung (davon Klammer R₂/R₃) / gültig / S1 / S1 nicht prüfbar / aus '
                          f'anderem Grund ungültig | – | {x["g1_geprueft"]} ({x["klammer_r2_r3"]}) / {x["gueltig"]} / '
                          f'{x["s1"]} / {x["s1_nicht_pruefbar"]} / {x["andere_ungueltig"]} |')
            zeilen.append(f'| {sid} | X′ mit R₁ der Vorprüfung unter ablauf-1 (größtes \\|Δ⟨N⟩\\|/ε_ctrl gegen R₂) | – | '
                          f'{x["vorpruefung_ablauf_1"]} ({_zahl(x["max_verhaeltnis_eps"], 2)}) |')
    t_vn = '\n'.join(zeilen)
    zeilen = ['| Kampagne | vorher → nachher | Ursache |', '|---|---|---|']
    for d in erg['vorher_nachher']:
        if d['gleich']:
            continue
        u = d['unterschiede']
        teile = [f'{k}: {v[0]} → {v[1]}' for k, v in u.items() if k in ('status', 'halt', 'vollstaendig', 'auswertbar',
                                                                       'zusaetzlich')]
        teile += [f'{r}: {v[0]} → {v[1]}' for r, v in d['rollen'].items()]
        teile += [f'{p.replace("|", " Block ")}: {v[0]} → {v[1]}' for p, v in list(d['plaetze'].items())[:4]]
        if 'grund' in u:
            teile.append('Haltgrund (Text)')
        if len(d['plaetze']) > 4:
            teile.append(f'… ({len(d["plaetze"])} Plätze)')
        name = f'{d["szenario"]} {d["art"]} Ebene {d["ebene"]} Nr. {d["index"]}'
        zeilen.append(f'| {name} | {"; ".join(teile)} | {"; ".join(d["ursache"])} |')
    t_kampagnen = '\n'.join(zeilen)
    h = erg['herkunft']
    namen = dict(vergleich_historisch='Vergleich historisch (30 Kampagnen)',
                 vergleich_k_konsistent='Vergleich k-konsistent ohne Wiederholungen (30)',
                 vergleich_wiederholungen='Vergleich k-konsistent mit Wiederholungen (30)',
                 pr22='Gegenprobe der Variante historisch gegen PR #22', voll_statisch='volle Ketten ohne Ablauf (2)',
                 voll_ablauf='volle Ketten mit Ablauf, Ebene H und Z/Stufe 1 (4)', regelpfad='Regelpfadfälle (3)',
                 fortsetzung='Fortsetzung aus einem Ablaufstand (Katalogkampagne)',
                 abschaetzung='Abschätzung künftiger Neuläufe')
    t_herkunft = '\n'.join(['| Ergebnisgruppe | Herkunft |', '|---|---|'] +
                           [f'| {namen[k]} | {v} |' for k, v in h.items()])
    r = erg['rechenumfang']
    b = r['bisher']
    t_umfang = '\n'.join([
        '| Rechnung | Kampagnenausführungen | volle Bootstrap-Auswertungen | Grenze |', '|---|---|---|---|',
        f'| bisher (PR #23 bis {VORHER[:7]}) | {b["ausfuehrungen"]} ({b["davon"]["auftragsliste"]} Auftragsliste, '
        f'{b["davon"]["diagnose"]} Diagnose, {b["davon"]["gegenproben"]} Gegenproben, {b["davon"]["abnahmelauf"]} '
        f'Abnahmelauf) | {b["voll"]} | 120 / 12 |',
        f'| Korrekturrunde 18.10.2026 (zusätzlich) | {r["korrektur"]["ausfuehrungen"]} | {r["korrektur"]["voll"]} | '
        f'{r["korrektur"]["grenzen"]["kampagnen"]} / {r["korrektur"]["grenzen"]["voll"]} |',
        f'| zusammen | {r["zusammen"]["ausfuehrungen"]} | {r["zusammen"]["voll"]} | – (zwei getrennte Budgets) |'])
    lz = erg['laufzeiten_korrektur']
    zeilen = ['| Art | Kampagnen | Sekunden je Kampagne (Mittel, max) |', '|---|---|---|']
    for k, e in lz['je_art'].items():
        n = sum(1 for b in erg['neu'] if f'{b["art"]}/{b["ebene"]}/{b["variante"]}' == k)
        zeilen.append(f'| {k} | {n} | {_zahl(e["mittel"], 1)}, {_zahl(e["max"], 1)} |')
    zeilen.append(f'| zusammen | {lz["kampagnen"]} | {_zahl(lz["kernsekunden"], 0)} Kernsekunden '
                  f'({_zahl(lz["kernstunden"], 3)} Kernstunden), Wandzeit {_zahl(lz["wandzeit_s"], 0)} s |')
    return dict(vorher_nachher=t_vn, vorher_nachher_kampagnen=t_kampagnen, herkunft=t_herkunft, rechenumfang=t_umfang,
                laufzeit_korrektur='\n'.join(zeilen))


def _tabelle_aus(text, name):
    """Inhalt zwischen <!-- tabelle:NAME --> und der nächsten <!-- /tabelle --> (ohne abschließenden Zeilenumbruch)."""
    m = re.search(rf'<!-- tabelle:{name} -->\n(.*?)\n?<!-- /tabelle -->', text, flags=re.S)
    if m is None:
        raise av.Fehler(f'Tabelle {name} nicht im Bericht am Stand {VORHER[:7]}')
    return m.group(1)


def schreiben_korrektur(pfad=None, ausgabe=None, doku=None, vorher_ausgabe=None):
    """Korrekturrunde: ergebnisse.json, kampagnen.csv (mit Herkunft je Zeile) und die Tabellen in bericht.md; der Stand
    davor bleibt über VORHER nachvollziehbar."""
    doku = doku or os.path.join(neulauf.WURZEL, av.DOKU_REL)
    erg = auswerten_korrektur(pfad, ausgabe, vorher_ausgabe)
    t = dict(tabellen(erg), **tabellen_korrektur(erg))
    alt_bericht = _git_show(VORHER, f'{av.DOKU_REL}/bericht.md')       # Laufzeiten und Abschätzung vom 17.10.2026
    t.update(laufzeit=_tabelle_aus(alt_bericht, 'laufzeit'), abschaetzung=_tabelle_aus(alt_bericht, 'abschaetzung'))
    with open(os.path.join(doku, 'ergebnisse.json'), 'w', encoding='utf-8') as f:
        f.write(formate.json_text({k: v for k, v in erg.items() if k not in ('alle', 'neu')}))
    _csv(os.path.join(doku, 'kampagnen.csv'), erg['alle'], herkunft=True)
    bpfad = os.path.join(doku, 'bericht.md')
    if os.path.exists(bpfad):
        with open(bpfad, encoding='utf-8') as f:
            text = f.read()
        with open(bpfad, 'w', encoding='utf-8') as f:
            f.write(einsetzen(text, t))
    return dict(ergebnisse=f'{av.DOKU_REL}/ergebnisse.json', kampagnen=len(erg['alle']),
                neu_gerechnet=len(erg['neu']), pr22=erg['pr22']['gleich'],
                stichprobe_gleich=all(s['gleich'] for s in erg['stichprobe_statisch']),
                vorher_nachher_gleich=sum(d['gleich'] for d in erg['vorher_nachher']),
                vorher_nachher=len(erg['vorher_nachher']), kernstunden=erg['laufzeiten_korrektur']['kernstunden'])
