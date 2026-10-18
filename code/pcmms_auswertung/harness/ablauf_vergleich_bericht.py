"""Berichtsteil der begrenzten Entwicklungsrechnung (harness.ablauf_vergleich): Auswertung der Checkpoints zu
maschinenlesbaren Ergebnissen (ergebnisse.json, CSV) und Berichtstabellen (bericht.md zwischen den Markierungen
<!-- tabelle:NAME --> … <!-- /tabelle -->). Gehört nicht zum Rechencode der Checkpoints; die Zahlen folgen allein aus den
gespeicherten Befunden. Kampagnenanteile mit 95-%-Wilson-Intervall; Läufe derselben Kampagne zählen nicht als
unabhängige Kampagnen. Keine Power- oder 0,95-Qualifikationsaussage.
"""
import csv
import os
import re

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
        n = sum(1 for b in erg['alle'] if f'{b["art"]}/{b["ebene"]}/{b["variante"]}' == k)
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
    spalten = ('szenario', 'variante', 'index', 'seed', 'art', 'ebene', 'vollstaendig', 'auswertbar', 'min_gueltig',
               'konfig_laeufe', 'konfig_ungueltig', 'konfig_g4', 'p_hat', 'sigma_F_mN', 'k', 'arbeitspunkt', 'status',
               'halt', 'zusaetzlich', 'zeit_realisiert_s', 'zeit_geplant_s', 'laufzeit_s')
    with open(os.path.join(doku, 'kampagnen.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(spalten)
        for b in sorted(erg['alle'], key=lambda b: (b['art'], b['szenario'], b['variante'], b['ebene'], b['index'])):
            ab = b.get('ablauf') or {}
            w.writerow([b['szenario'], b['variante'], b['index'], b['seed'], b['art'], b['ebene'], int(b['vollstaendig']),
                        b['auswertbar']['n'], b['auswertbar']['min_gueltig'], b['phase1']['konfig_laeufe'],
                        b['phase1']['konfig_ungueltig'], b['phase1']['konfig_g4'], repr(b['teil_b']['p_hat']),
                        repr(1e3 * b['teil_b']['sigma_delta_K']['F']), b['teil_b']['k'], b['teil_b']['arbeitspunkt'],
                        ab.get('status', 'statisch'), ab.get('halt') or '', (ab.get('laufzahl') or {}).get('zusaetzlich', 0),
                        (ab.get('messzeit_s') or {}).get('realisiert_laeufe', ''),
                        (ab.get('messzeit_s') or {}).get('geplant_laeufe', ''), b['laufzeit_s']])
    bpfad = os.path.join(doku, 'bericht.md')
    if os.path.exists(bpfad):
        with open(bpfad, encoding='utf-8') as f:
            text = f.read()
        with open(bpfad, 'w', encoding='utf-8') as f:
            f.write(einsetzen(text, t))
    return dict(ergebnisse=f'{av.DOKU_REL}/ergebnisse.json', kampagnen=len(erg['alle']), pr22=erg['pr22']['gleich'],
                laufzeiten=erg['laufzeiten']['kernstunden'])


def einsetzen(text, tabellen):
    """Tabellen zwischen <!-- tabelle:NAME --> und der nächsten <!-- /tabelle --> einsetzen; der Text außerhalb der
    Markierungen bleibt unverändert, auch bei leeren Markierungspaaren."""
    for name, tab in tabellen.items():
        text = re.sub(rf'(<!-- tabelle:{name} -->\n).*?(<!-- /tabelle -->)',
                      lambda m, tab=tab: m.group(1) + tab + '\n' + m.group(2), text, flags=re.S)
    return text
