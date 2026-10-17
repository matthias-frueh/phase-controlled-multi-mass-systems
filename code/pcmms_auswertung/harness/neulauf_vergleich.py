"""Alt-Neu-Vergleich und Bericht der AP-13-Neuläufe (harness.neulauf): kompakte Ergebnisse, Kampagnenübersicht und
Tabellen für K12, K19 und die ausgewählten E3-Punkte. Liest nur Auftragsliste, Checkpoints, Altstandsauszug und die
historische kompakte Datei; rechnet keine Kampagne neu.

E3: Nenner sind alle Kampagnen eines Punktes. Kampagnen ohne dreiwertige Bewertung stehen getrennt mit Grund und werden
nicht als „unbestimmt“ gezählt. Die „alte Lesart“ bewertet dieselben neuen Kampagnen mit u ohne T-Anteil (gleiche
Replikate, T und Zelllagen fest; Diagnose aus kontrollen.e3_auswerten) nach derselben Regel – eine Gegenprobe, ob die
Änderung der Raten allein aus der T-Unsicherheit folgt. Sie ersetzt keine alten Einzelbefunde; Übergänge je Kampagne
werden nicht berichtet, weil der Altlauf keine Einzelbefunde von E3 gespeichert hat.
"""
import csv
import json
import os
import re

import numpy as np
from scipy import stats

from .. import formate
from . import kampagnen, neulauf, planung

KATEGORIEN = ('auffällig', 'unauffällig', 'unbestimmt')
OHNE = 'ohne dreiwertige Bewertung'
KONTROLLEN = ('H1: bestätigt', 'H1: falsifiziert', 'H1: nicht entscheidbar', 'H2: bestätigt', 'H2: falsifiziert',
              'H2: nicht entscheidbar', 'H1 und H2 bestätigt')
GROESSEN = ('F_min', 'Re N1', 'Im N1', 'Re N2', 'Im N2', 'Re N3', 'Im N3')


def _rate(z, n):
    p = z / n if n else None
    return dict(zaehler=int(z), nenner=int(n), rate=p, mc_se=None if not n else float(np.sqrt(p * (1 - p) / n)))


def _zn(r):
    return None if r is None else f'{r["zaehler"]}/{r["nenner"]}'


def _ohne_grund(b):
    """Klasse und Wortlaut des Grundes einer Kampagne ohne dreiwertige E3-Bewertung."""
    e = b.get('E3')
    if e is None:
        return 'keine E3-Auswertung', b.get('E3_grund') or 'keine E3-Auswertung (Grund nicht gespeichert)'
    s = e.get('status') or ''
    if s.startswith('nicht auswertbar'):
        return 'nicht auswertbar (T singulär oder schlecht konditioniert)', s
    if s.startswith('nur beschreibend'):
        return 'Regel offen (nur beschreibend)', s
    if s.startswith('nur numerisch'):
        if 'unvollständig' in s:
            return 'T-Beschreibung unvollständig', s
        if 'T-Ziehungen unzulässig' in s:
            return 'unzulässige T-Ziehungen', s
        if 'Unsicherheit von T fehlt' in s:
            return 'T-Beschreibung fehlt', s
        return 'nur numerisch (sonstiger Grund)', s
    return 'ohne Bewertung (sonstiger Status)', s


def _pruefgroessen(e3, spalte):
    A = np.asarray(e3['e3a'], float).reshape(-1, 3)
    p = [(x, u, 'phase_grad') for x, u in zip(A[:, 0], A[:, spalte])]
    if e3.get('e3b') is not None:
        b = np.asarray(e3['e3b'], float)
        p.append((b[0], b[spalte], 'q_tol'))
    return p


def bewerten(e3, spalte, schwellen):
    """Dreiwertige E3-Bewertung aus den gespeicherten Prüfgrößen nach der Regel von kontrollen.e3_auswerten
    (Spalte 1: u mit T-Anteil, 2: u ohne T-Anteil); None ohne Prüfgrößen oder bei nicht endlichen Werten."""
    if not e3 or e3.get('e3a') is None:
        return None
    p = _pruefgroessen(e3, spalte)
    if not p or not np.all(np.isfinite([[x, u] for x, u, _ in p])):
        return None
    zB = float(stats.norm.ppf(1 - 0.05 / len(p)))
    auff = any(x - zB * u > schwellen[s] for x, u, s in p)
    unauff = all(x + 1.645 * u <= schwellen[s] for x, u, s in p)
    return 'auffällig' if auff else ('unauffällig' if unauff else 'unbestimmt')


def _verteilung(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not x.size:
        return None
    q = np.quantile(x, [0.25, 0.5, 0.75])
    return dict(n=int(x.size), q25=float(q[0]), median=float(q[1]), q75=float(q[2]), max=float(x.max()))


def _zaehle(werte):
    out = {}
    for w in werte:
        out[w] = out.get(w, 0) + 1
    return dict(sorted(out.items()))


def begrenzend(e3, schwellen):
    """Welche Prüfgrößen (E3a-Phasen, E3b-Moment) die Bewertung bestimmen: bei „auffällig“ die über der Schwelle
    (x − z_B·u > s), bei „unbestimmt“ die, die „unauffällig“ verfehlen (x + 1,645·u > s). Rückgabe 'E3a', 'E3b',
    'beide' oder None."""
    if not e3 or e3.get('bewertung') not in ('auffällig', 'unbestimmt'):
        return None
    p = _pruefgroessen(e3, 1)
    zB = float(stats.norm.ppf(1 - 0.05 / len(p)))
    if e3['bewertung'] == 'auffällig':
        f = {s for x, u, s in p if x - zB * u > schwellen[s]}
    else:
        f = {s for x, u, s in p if x + 1.645 * u > schwellen[s]}
    return {frozenset({'phase_grad'}): 'E3a', frozenset({'q_tol'}): 'E3b'}.get(frozenset(f), 'beide' if f else None)


def e3_punkt(lauf, schwellen):
    """E3 eines Szenariopunkts: Raten über alle Kampagnen, Gründe ohne dreiwertige Bewertung, Diagnose der
    Unsicherheiten, der bestimmenden Prüfgrößen und der T-Ziehungen, alte Lesart (u ohne T-Anteil) und die Gegenprobe
    der Regel."""
    bf = lauf['befunde']
    n = len(bf)
    bew = [(b.get('E3') or {}).get('bewertung') for b in bf]
    raten = {k: _rate(sum(x == k for x in bew), n) for k in KATEGORIEN}
    raten[OHNE] = _rate(sum(x is None for x in bew), n)
    gruende = {}
    for b, x in zip(bf, bew):
        if x is None:
            kl, txt = _ohne_grund(b)
            g = gruende.setdefault(kl, dict(zaehler=0, wortlaute={}))
            g['zaehler'] += 1
            g['wortlaute'][txt] = g['wortlaute'].get(txt, 0) + 1
    gruende = {kl: dict(_rate(g['zaehler'], n), wortlaute=g['wortlaute']) for kl, g in sorted(gruende.items())}
    nach = [bewerten(b.get('E3'), 1, schwellen) for b in bf]
    alt_l = [bewerten(b.get('E3'), 2, schwellen) for b in bf]
    geprueft = [(x, y) for x, y in zip(bew, nach) if x is not None]
    alte_lesart = {k: _rate(sum(x == k for x in alt_l), n) for k in KATEGORIEN}
    alte_lesart[OHNE] = _rate(sum(x is None for x in alt_l), n)
    bestimmend = {k: _zaehle(begrenzend(b.get('E3'), schwellen) for b, x in zip(bf, bew) if x == k)
                  for k in ('auffällig', 'unbestimmt')}
    e3s = [b['E3'] for b in bf if b.get('E3')]
    A = [np.asarray(e['e3a'], float).reshape(-1, 3) for e in e3s if e.get('e3a') is not None]
    A = np.concatenate(A) if A else np.zeros((0, 3))
    Q = np.array([np.asarray(e['e3b'], float) for e in e3s if e.get('e3b') is not None]).reshape(-1, 3)
    with np.errstate(divide='ignore', invalid='ignore'):
        unsicherheit = dict(
            e3a=dict(n_pruefgroessen=int(A.shape[0]), abs_delta_phi_grad=_verteilung(A[:, 0]),
                     u_grad=_verteilung(A[:, 1]), u_ohne_T_grad=_verteilung(A[:, 2]),
                     verhaeltnis_u_zu_u_ohne_T=_verteilung(A[:, 1] / A[:, 2])),
            e3b=dict(n=int(Q.shape[0]), q_Z=_verteilung(Q[:, 0]), u_q_Z=_verteilung(Q[:, 1]),
                     u_q_Z_ohne_T=_verteilung(Q[:, 2]), verhaeltnis_u_zu_u_ohne_T=_verteilung(Q[:, 1] / Q[:, 2])),
            schwellen=schwellen)
    t = [e.get('t') or {} for e in e3s]
    gez = [x for x in t if x.get('gezogen')]
    n_zieh = sum(int(x['B']) for x in gez)
    n_ung = sum(int(round(x['anteil_ungueltig'] * x['B'])) for x in gez)
    gr_z = {}
    for x in gez:
        for k, c in (x.get('gruende') or {}).items():
            gr_z[k] = gr_z.get(k, 0) + int(c)
    ziehungen = dict(
        kampagnen_mit_ziehungen=_rate(len(gez), n), B=sorted({int(x['B']) for x in gez}),
        ohne_ziehungen=_zaehle(x.get('grund') or 'keine T-Diagnose (E3 nicht ausgewertet)' for x in t
                               if not x.get('gezogen')),
        kampagnen_mit_unzulaessigen=_rate(sum(x['anteil_ungueltig'] > 0 for x in gez), n),
        unzulaessige_ziehungen=_rate(n_ung, n_zieh) if n_zieh else None, gruende_unzulaessig=dict(sorted(gr_z.items())),
        anteil_w_gespiegelt=_verteilung([x.get('anteil_w_gespiegelt') for x in gez]),
        unvollstaendig=_zaehle(s for x in gez for s in x.get('unvollstaendig') or []),
        nicht_gezogen=_zaehle(s for x in gez for s in x.get('nicht_gezogen') or []),
        naeherungen=_zaehle(s for x in gez for s in x.get('naeherungen') or []),
        modell=_zaehle(x.get('modell') for x in gez), format=_zaehle(x.get('format') for x in gez))
    return dict(n=n, raten=raten, ohne_dreiwertige_bewertung=gruende, alte_lesart=alte_lesart,
                gegenprobe_regel=dict(geprueft=len(geprueft), gleich=sum(x == y for x, y in geprueft)),
                bestimmende_pruefgroessen=bestimmend,
                unsicherheit=unsicherheit, t_ziehungen=ziehungen, bewertungen=bew, alte_lesart_je_kampagne=alt_l)


def _zmax(lauf):
    zp, vp = [], []
    for b in lauf['befunde']:
        z = np.asarray(b['felder']['z0'], float)
        f = np.isfinite(z)
        zp.append(float(np.abs(z[f]).max()) if f.any() else np.nan)
        vp.append(bool(f.all()))
    return np.array(zp), np.array(vp)


def kontrollen(lauf, alt):
    """H1/H2, Gültigkeit und Abbrüche neu gegen alt (Zähler/Nenner), dazu Seeds bzw. Kohorte und Wahrheit."""
    r = kampagnen.raten(lauf)
    neu = {k: _rate(r['raten'][k]['zaehler'], r['raten'][k]['nenner']) for k in KONTROLLEN}
    alt_r = {k: alt['raten'].get(k) or _rate(0, lauf['meta']['n']) for k in KONTROLLEN}
    gn, ga = r['gueltigkeit'], alt.get('gueltigkeit') or {}
    ln = next((v['nenner'] for v in gn.values()), sum(b['gueltigkeit']['n_laeufe'] for b in lauf['befunde']))
    la = next((v['nenner'] for v in ga.values()), None)
    for g in sorted(set(gn) | set(ga)):                          # eine nur einseitig auftretende Regel: Zähler 0
        neu[f'ungültig {g}'] = _rate(gn[g]['zaehler'], gn[g]['nenner']) if g in gn else _rate(0, ln)
        alt_r[f'ungültig {g}'] = ga.get(g) or (None if la is None else _rate(0, la))
    neu.update({f'Abbruch {s}': _rate(v['zaehler'], v['nenner']) for s, v in r['abbruch'].items()})
    alt_r.update({f'Abbruch {s}': v for s, v in (alt.get('abbruch') or {}).items()})
    zeilen = {k: dict(alt=alt_r.get(k), neu=neu.get(k),
                      gleich=None if alt_r.get(k) is None or neu.get(k) is None else
                      _zn(alt_r[k]) == _zn(neu[k])) for k in sorted(set(neu) | set(alt_r))}
    out = dict(raten=zeilen, alle_gleich=all(z['gleich'] is not False for z in zeilen.values()),
               wahrheit=dict(alt=(alt.get('wahrheit') or {}).get('klasse'), neu=lauf['wahrheit']['klasse']))
    if 'seeds' in (alt.get('meta') or {}) and alt['meta']['seeds'] is not None:
        out['seeds_gleich_alt'] = lauf['meta']['seeds'] == alt['meta']['seeds']
    if 'zmax_pruefung' in alt:                                    # N01-A4/L1: Kohorte über max|z⁰| je Kampagne
        zp, vp = _zmax(lauf)
        za = np.array([np.nan if x is None else x for x in alt['zmax_pruefung']], float)
        ko = dict(art='max|z⁰| je Prüfkampagne (Rolle pruefung_c) gegen zmax.pruefung des Altlaufs', n=int(zp.size),
                  n_alt=int(za.size))
        if zp.size == za.size:
            gl = (zp == za) | (np.isnan(zp) & np.isnan(za))
            d = np.abs(zp - za)
            ko.update(bitgleich=int(gl.sum()), max_abs_differenz=float(np.nanmax(d)) if np.isfinite(d).any() else 0.0,
                      vollstaendig_gleich=bool(np.array_equal(vp, np.asarray(alt['zmax_pruefung_vollstaendig']))))
        out['kohorte'] = ko
    return out


def k12(ps, alt):
    """Planungsschritt: simulierte, übersprungene und wegen der Aufrufgrenze nicht gerechnete Kandidaten; Kandidaten
    mit Plan, n_max, c, H2-Intervall und gemeinsamer Bestätigung; Suchergebnis; alt daneben."""
    pl = ps['schritte']['planung']
    paare = {(p['k'], p['N_z']): p for p in pl.get('paare', [])}
    n_kand = len(planung.kandidaten_ordnen(ps['konfiguration']['planung_kandidaten'], [20]))

    def zaehlung(aufrufe):
        ng = [x for x in aufrufe if str(x.get('grund', '')).startswith('nicht simuliert')]
        return dict(aufrufe=len(aufrufe), aufrufe_simuliert=sum(1 for x in aufrufe if x['kandidaten']),
                    kandidaten_simuliert=sum(1 for x in aufrufe for c in x['kandidaten'] if 'uebersprungen' not in c),
                    kandidaten_uebersprungen=sum(1 for x in aufrufe for c in x['kandidaten'] if 'uebersprungen' in c),
                    aufrufe_nicht_gerechnet_aufrufgrenze=len(ng),
                    kandidaten_nicht_gerechnet_aufrufgrenze=len(ng) * n_kand,
                    aufrufe_ohne_kandidaten_sonst=sum(1 for x in aufrufe if not x['kandidaten'] and x not in ng))

    def kandidaten(aufrufe, neu):
        z = []
        for x in aufrufe:
            for c in x['kandidaten']:
                ps_ = c.get('plan_simuliert') or {}
                p = paare.get((x['k'], x['N_z']), {}) if neu else {}
                z.append(dict(k=x['k'], N_z=x['N_z'], n_min=c['n_min'], n0=c['n0'], reserve_r=c['reserve_r'],
                              uebersprungen=c.get('uebersprungen'), plan_simuliert=ps_ or None,
                              n_max=p.get('n_max'), T_e=p.get('T_e'), T_a=p.get('T_a'), T_lauf_pilot=p.get('T_lauf'),
                              p_hat=p.get('p_hat'), c_H1=c.get('c_H1'), intervalltyp_H2=c.get('intervalltyp_H2'),
                              pruefrate_c=c.get('pruefrate_c'),
                              gemeinsam=None if c.get('nenner') is None else _rate(c['zaehler'], c['nenner']),
                              erfuellt=c.get('erfuellt'), kappa=x.get('kappa')))
        return z
    return dict(neu=dict(zaehlung=zaehlung(pl['aufrufe']), kandidaten=kandidaten(pl['aufrufe'], True),
                         suche=pl['suche'], paare=pl.get('paare'), zeit=pl['zeit'],
                         fenster=[x.get('fenster') for x in pl['aufrufe'] if x.get('fenster')]),
                alt=dict(zaehlung=zaehlung(alt['aufrufe']), kandidaten=kandidaten(alt['aufrufe'], False),
                         suche=alt['suche'], plan_simuliert=alt['plan_simuliert'], zeit=alt['zeit']),
                hinweis='Je Kandidat 4 Kalibrier- und 4 Prüfkampagnen: Entwicklungsdiagnostik, keine Power-Aussage')


def k19(erg, alt):
    rv = erg['ergebnis']
    raten = {}
    for k, x in rv['raten'].items():
        a = alt['raten'].get(k) or {}
        raten[k] = dict(Z_alt=a.get('Z'), H_alt=a.get('H'), innerhalb_2se_alt=a.get('innerhalb_2se'),
                        Z_neu=_rate(x['Z']['zaehler'], x['Z']['nenner']), H_neu=_rate(x['H']['zaehler'],
                                                                                        x['H']['nenner']),
                        innerhalb_2se_neu=x['innerhalb_2se'])
    vb = {}
    for e in ('Z', 'H'):
        xs = [x for x in rv['verarbeitung'][e] if x]
        ver = {}
        for x in xs:
            for v, c in x['versionen'].items():
                ver[v] = ver.get(v, 0) + int(c)
        vb[e] = dict(versionen=dict(sorted(ver.items())), kampagnen_mit_angabe=len(xs),
                     mittel_bedeutung=sorted({b for x in xs for b in x['mittel_bedeutung'].values()}),
                     alte_bedeutung=sorted({b for x in xs for b in x['alte_bedeutung']}))
    return dict(n=rv['n'], seeds=rv['seeds'], u_c_median=dict(alt=alt['u_c_median'], neu=rv['u_c_median']),
                u_c_relativ=dict(alt=alt['u_c_relativ'], neu=rv['u_c_relativ']),
                u_c_innerhalb_5_prozent=dict(alt=alt['u_c_innerhalb_5_prozent'], neu=rv['u_c_innerhalb_5_prozent']),
                gleich_alt={e: all(rv['u_c_median'][e][g] == alt['u_c_median'][e][g] for g in GROESSEN)
                            for e in ('Z', 'H')},
                raten=raten, alle_raten_innerhalb_2se_neu=all(x['innerhalb_2se_neu'] is not False
                                                               for x in raten.values()),
                ausgaenge=rv['ausgaenge'], verarbeitung=vb, meta=erg['meta'], lesart=rv['lesart'])


def e3_alt(alt_raten, n):
    """E3-Raten des Altlaufs über alle n Kampagnen des Altlaufs: nicht aufgetretene Kategorien mit Zähler 0; ohne
    dreiwertige Bewertung = n − Summe der drei Kategorien."""
    out = {k: _rate((alt_raten.get(f'E3: {k}') or {}).get('zaehler', 0), n) for k in KATEGORIEN}
    out[OHNE] = _rate(n - sum(out[k]['zaehler'] for k in KATEGORIEN), n)
    return out


def _vergleich_e3(neu, alt):
    return {k: dict(alt=alt[k], neu=neu['raten'][k], aenderung=None if alt[k]['rate'] is None or
                    neu['raten'][k]['rate'] is None else neu['raten'][k]['rate'] - alt[k]['rate'])
            for k in KATEGORIEN + (OHNE,)}


# ── Laden und Schreiben ───────────────────────────────────────────────────────────────────────────────
def laden(pfad=neulauf.AUFTRAG, ausgabe=None):
    """Auftragsliste, passende Checkpoints (Schlüssel wie bei der Rechnung) und Ergebnisse je Auftrag."""
    a = neulauf.lies_auftrag(pfad)
    prof, _ = neulauf.pruefe_gemeinsam(a)
    erg = {}
    for job in a['auftraege']:
        w8, w8_sha = neulauf.werkzeug8_laden(a, job.get('werkzeug8'))
        sd = neulauf.seeds(job, a['gemeinsam']['seed_basis'])
        ziel = neulauf.verzeichnis(a, job, ausgabe)
        s = neulauf.checkpoint(ziel, neulauf.schluessel(a, job, prof, w8_sha, sd))
        if not s:
            raise neulauf.AuftragFehler(f'{job["id"]}: kein passender Checkpoint in {ziel}')
        name = {'planung': 'pruefstand', 'ebenen_verrauscht': 'ebenen'}.get(
            job['art'], f'kampagnen_{job.get("szenario")}_{job.get("stufe")}_{job.get("rolle")}')
        erg[job['id']] = dict(auftrag=job, checkpoint=s,
                              daten=formate.lies_objekt(os.path.join(ziel, name), 'bewertung')[1])
    return a, prof, erg


def zusammenstellen(a, prof, erg, auszug, historisch, auftrag_sha256=None):
    """Kompakte Ergebnisse mit Herkunft; prüft die Übereinstimmung von Auszug und historischer kompakter Datei."""
    hs = historisch['schritte']
    for pid, x in auszug['e3'].items():                            # Auszug ↔ versionierte kompakte Datei
        if x['ort'].endswith('raten_pruefung'):
            h = hs['kalibrierung_a4']['raten_pruefung']
        else:
            schritt, unter = x['ort'].split('.', 2)[1:]
            h = hs[schritt][unter]['raten']
        if {k: _zn(v) for k, v in x['raten'].items()} != h:
            raise neulauf.AuftragFehler(f'{pid}: Altstandsauszug ≠ historische kompakte Datei')
    sw = prof.wert('e3.schwellen')
    e3, ck = {}, {}
    for jid, x in erg.items():
        job = x['auftrag']
        if job['art'] != 'kampagnen':
            continue
        pid = f'{job["szenario"]}/{job["stufe"]}'
        alt = auszug['e3'][pid]
        p = e3_punkt(x['daten'], sw)
        k = kontrollen(x['daten'], alt)
        m = x['daten']['meta']
        ea = e3_alt(alt['raten'], int(alt['meta'].get('n') or alt['meta'].get('n_pruefung')))
        e3[pid] = dict(auftrag=jid, rolle=m['rolle'], werkzeug8=m['werkzeug8_quelle'],
                       werkzeug8_meta=m['werkzeug8'], werkzeug8_sha256=m['werkzeug8_sha256'],
                       vergleich=_vergleich_e3(p, ea),
                       alte_lesart_gleich_alt=all(_zn(p['alte_lesart'][c]) == _zn(ea[c]) for c in KATEGORIEN + (OHNE,)),
                       **{q: v for q, v in p.items() if q not in ('bewertungen', 'alte_lesart_je_kampagne')},
                       kontrollen=k, laufzeit_s=x['checkpoint']['laufzeit_s'], seed_basis=m['seed_basis'],
                       seeds_sha256=formate.sha256_json(m['seeds']))
        ck[pid] = p
    j12 = next(x for x in erg.values() if x['auftrag']['art'] == 'planung')
    j19 = next(x for x in erg.values() if x['auftrag']['art'] == 'ebenen_verrauscht')
    gits = sorted({x['checkpoint']['git'] for x in erg.values()} | {x['checkpoint']['git_ende'] for x in erg.values()})
    umgebungen = [x['checkpoint']['schluessel']['umgebung'] for x in erg.values()]
    out = dict(
        kennung=a['kennung'], herkunft=dict(
            rechen_commit=gits, rechencode_sha256=sorted({x['checkpoint']['schluessel']['rechencode']
                                                          for x in erg.values()}),
            auftrag_sha256=auftrag_sha256,
            profil=prof.id, profil_sha256=prof.sha256(), gemeinsam=a['gemeinsam'], werkzeug8=a['werkzeug8'],
            umgebung=umgebungen[0] if all(u == umgebungen[0] for u in umgebungen) else umgebungen,
            altlauf=auszug['quelle'], bericht_code=formate.code_version()),
        laufzeit_s={jid: x['checkpoint']['laufzeit_s'] for jid, x in erg.items()},
        zeitraum=dict(start=min(x['checkpoint']['start'] for x in erg.values()),
                      ende=max(x['checkpoint']['ende'] for x in erg.values())),
        umfang=dict(e3_pruefkampagnen=sum(v['n'] for v in e3.values()), e3_punkte=len(e3),
                    k19_kampagnen_je_ebene=j19['daten']['ergebnis']['n'], kalibrierkampagnen=0),
        k12=k12(j12['daten'], auszug['k12']), k19=k19(j19['daten'], auszug['k19']), e3=e3,
        laufzeit_alt_s=auszug['laufzeit_s'])
    return out, ck


def _f(x, d=3):
    return '–' if x is None else f'{x:.{d}f}'


def _rz(r, d=3):
    if r is None:
        return '–'
    return f'{r["zaehler"]}/{r["nenner"]} ({_f(r["rate"], d)} ± {_f(r["mc_se"], d)})'


def tabellen(z):
    """Markdown-Tabellen je Abschnitt (Schlüssel k12, k19, e3, e3_gruende, e3_diagnose, e3_kontrollen)."""
    t = {}
    k = z['k12']
    zn, za = k['neu']['zaehlung'], k['alt']['zaehlung']
    zl = ['| Zählung | alt | neu |', '|---|---:|---:|']
    for key, txt in (('aufrufe', 'Aufrufe des Haken (Paare k, N_z)'), ('aufrufe_simuliert', 'davon simuliert'),
                     ('kandidaten_simuliert', 'Kandidaten simuliert'), ('kandidaten_uebersprungen',
                                                                        'Kandidaten übersprungen (n > n_max)'),
                     ('aufrufe_nicht_gerechnet_aufrufgrenze', 'Aufrufe nicht gerechnet (Aufrufgrenze 2)'),
                     ('kandidaten_nicht_gerechnet_aufrufgrenze', 'Kandidaten nicht gerechnet (Aufrufgrenze)'),
                     ('aufrufe_ohne_kandidaten_sonst', 'Aufrufe ohne Kandidaten aus anderem Grund')):
        zl.append(f'| {txt} | {za[key]} | {zn[key]} |')
    zl += ['', '| Kandidat | Stand | N_z | T_a [s] | T_e [s] | T_Lauf [s] | Messtage | n = n_min + r | n_max | c_H1 | '
           'H2-Intervall | P(H1 ∧ H2) | erfüllt |', '|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|']
    alt_k = {(c['k'], c['n_min'], c['n0']): c for c in k['alt']['kandidaten']}
    pa = k['alt']['plan_simuliert']
    for c in k['neu']['kandidaten']:
        p = c['plan_simuliert'] or {}
        name = f'k = {c["k"]}, n_min = {c["n_min"]}, n₀ = {c["n0"]}'
        a = alt_k.get((c['k'], c['n_min'], c['n0']))
        if a:
            zl.append(f'| {name} | alt | {pa["n_zyklen"]} | – | – | {_f(pa["T_lauf_s"], 0)} | {pa["tage"]} | '
                      f'{a["n_min"]} + {a["reserve_r"]} | – | {_f(a["c_H1"])} | {a["intervalltyp_H2"] or "–"} | '
                      f'{_rz(a["gemeinsam"], 2)} | {"ja" if a["erfuellt"] else "nein"} |')
        zl.append(f'| {name} | neu | {p.get("n_zyklen", "–")} | {_f(p.get("T_a_s"), 1)} | {_f(c["T_e"], 1)} | '
                  f'{_f(p.get("T_lauf_s"), 1)} | {p.get("tage", "–")} | {c["n_min"]} + {c["reserve_r"]} '
                  f'(n_Blöcke {p.get("n_bloecke", "–")}) | {c["n_max"] if c["n_max"] is not None else "–"} | '
                  f'{_f(c["c_H1"])} | {c["intervalltyp_H2"] or "–"} | {_rz(c["gemeinsam"], 2)} | '
                  f'{"ja" if c["erfuellt"] else ("übersprungen" if c["uebersprungen"] else "nein")} |')
    zl += ['', f'Suchergebnis alt: {k["alt"]["suche"]["ergebnis"]} ({k["alt"]["suche"].get("grund", "")}); '
               f'neu: {k["neu"]["suche"]["ergebnis"]} ({k["neu"]["suche"].get("grund", "")}).']
    t['k12'] = '\n'.join(zl)
    k = z['k19']
    zl = ['| Größe | Z alt | H alt | rel. alt | Z neu | H neu | rel. neu |', '|---|---:|---:|---:|---:|---:|---:|']
    for g in GROESSEN:
        ua, un = k['u_c_median']['alt'], k['u_c_median']['neu']
        zl.append(f'| {g} | {ua["Z"][g]:.6g} | {ua["H"][g]:.6g} | {100 * k["u_c_relativ"]["alt"][g]:+.2f} % | '
                  f'{un["Z"][g]:.6g} | {un["H"][g]:.6g} | {100 * k["u_c_relativ"]["neu"][g]:+.2f} % |')
    zl += ['', f'Alle |rel.| ≤ 5 %: alt {"ja" if k["u_c_innerhalb_5_prozent"]["alt"] else "nein"}, neu '
               f'{"ja" if k["u_c_innerhalb_5_prozent"]["neu"] else "nein"}. u_c-Mediane neu bitgleich alt: Ebene Z '
               f'{_ja(k["gleich_alt"]["Z"])}, Ebene H {_ja(k["gleich_alt"]["H"])}.', '',
           '| Ausgang | Z alt | H alt | Z neu | H neu | innerhalb 2 SE alt / neu |', '|---|---|---|---|---|---|']
    for key, x in k['raten'].items():
        zl.append(f'| {key} | {_zn(x["Z_alt"])} | {_zn(x["H_alt"])} | {_rz(x["Z_neu"], 2)} | {_rz(x["H_neu"], 2)} | '
                  f'{_ja(x["innerhalb_2se_alt"])} / {_ja(x["innerhalb_2se_neu"])} |')
    t['k19'] = '\n'.join(zl)
    zl = ['| Punkt | Rolle, n | Werkzeug 8 | auffällig alt → neu | unauffällig alt → neu | unbestimmt alt → neu | '
          f'{OHNE} neu |', '|---|---|---|---|---|---|---|']
    for pid, x in z['e3'].items():
        v = x['vergleich']
        zl.append(f'| {pid} | {x["rolle"]}, {x["n"]} | {x["werkzeug8"]} | ' + ' | '.join(
            f'{_rz(v[c]["alt"], 3)} → {_rz(v[c]["neu"], 3)}; Δ {_d(v[c]["aenderung"])}' for c in KATEGORIEN) +
            f' | {_zn(v[OHNE]["neu"])} |')
    t['e3'] = '\n'.join(zl)
    zl = [f'| Punkt | {OHNE} | Grund (Klasse) | Anzahl |', '|---|---|---|---:|']
    for pid, x in z['e3'].items():
        g = x['ohne_dreiwertige_bewertung']
        if not g:
            zl.append(f'| {pid} | {_zn(x["raten"][OHNE])} | – | 0 |')
        for kl, r in g.items():
            zl.append(f'| {pid} | {_zn(x["raten"][OHNE])} | {kl} | {r["zaehler"]} |')
    t['e3_gruende'] = '\n'.join(zl)
    zl = ['| Punkt | Kampagnen mit T-Ziehungen | unzulässige Ziehungen | Median u E3a mit / ohne T-Anteil [°] | '
          'u/u ohne T (E3a): Median, Max. | Median u(q_Z) mit / ohne T-Anteil |', '|---|---|---|---|---|---|']
    for pid, x in z['e3'].items():
        u, tz = x['unsicherheit'], x['t_ziehungen']
        ua, ub = u['e3a'], u['e3b']
        v = ua['verhaeltnis_u_zu_u_ohne_T']
        zl.append(f'| {pid} | {_zn(tz["kampagnen_mit_ziehungen"])} | {_zn(tz["unzulaessige_ziehungen"])} | '
                  f'{_m(ua["u_grad"], 4)} / {_m(ua["u_ohne_T_grad"], 4)} | '
                  f'{_m(v, 4)}, {_mx(v)} | '
                  f'{_m(ub["u_q_Z"], 6)} / {_m(ub["u_q_Z_ohne_T"], 6)} |')
    t['e3_diagnose'] = '\n'.join(zl)
    zl = ['| Punkt | historisch auff. / unauff. / unbest. | alte Lesart nachgerechnet (u ohne T-Anteil) | gleich | '
          'bestimmend bei „auffällig“ | bestimmend bei „unbestimmt“ |', '|---|---|---|---|---|---|']
    for pid, x in z['e3'].items():
        al, v = x['alte_lesart'], x['vergleich']
        b = x['bestimmende_pruefgroessen']
        zl.append(f'| {pid} | ' + ' / '.join(str(v[c]['alt']['zaehler']) for c in KATEGORIEN) + ' | ' +
                  ' / '.join(str(al[c]['zaehler']) for c in KATEGORIEN) + f' | {_ja(x["alte_lesart_gleich_alt"])} | '
                  f'{_bestimmend(b["auffällig"])} | {_bestimmend(b["unbestimmt"])} |')
    t['e3_lesart'] = '\n'.join(zl)
    zl = ['| Punkt | H1 bestätigt alt / neu | H2 bestätigt alt / neu | H1 ∧ H2 alt / neu | ungültig G1, G4 alt / neu | '
          'Kontrollen gleich | Seeds bzw. Kohorte |', '|---|---|---|---|---|---|---|']
    for pid, x in z['e3'].items():
        r = x['kontrollen']['raten']
        g = '; '.join(f'{_zn(r[q]["alt"])} / {_zn(r[q]["neu"])}' for q in ('ungültig G1', 'ungültig G4') if q in r)
        ko = x['kontrollen'].get('kohorte')
        sd = (f'max|z⁰| bitgleich {ko.get("bitgleich", "–")}/{ko["n"]}' if ko else
              ('Seeds gleich' if x['kontrollen'].get('seeds_gleich_alt') else 'Seeds verschieden'))
        zl.append(f'| {pid} | {_zn(r["H1: bestätigt"]["alt"])} / {_zn(r["H1: bestätigt"]["neu"])} | '
                  f'{_zn(r["H2: bestätigt"]["alt"])} / {_zn(r["H2: bestätigt"]["neu"])} | '
                  f'{_zn(r["H1 und H2 bestätigt"]["alt"])} / {_zn(r["H1 und H2 bestätigt"]["neu"])} | {g or "–"} | '
                  f'{_ja(x["kontrollen"]["alle_gleich"])} | {sd} |')
    t['e3_kontrollen'] = '\n'.join(zl)
    return t


def _d(x, d=3):
    return '–' if x is None else f'{x:+.{d}f}'


def _bestimmend(d):
    return '–' if not d else ', '.join(f'{k} {v}' for k, v in d.items())


def _ja(x):
    return '–' if x is None else ('ja' if x else 'nein')


def _m(v, d=3):
    return '–' if not v else f'{v["median"]:.{d}f}'


def _mx(v, d=3):
    return '–' if not v else f'{v["max"]:.{d}f}'


def kampagnenuebersicht(pfad, erg, ck):
    """Eine Zeile je E3-Kampagne mit den Größen, aus denen sich Zähler, Nenner und Gründe nachzählen lassen."""
    with open(pfad, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['punkt', 'kampagne', 'seed', 'E3_bewertung', 'E3_ohne_bewertung_klasse', 'E3_ohne_bewertung_grund',
                    'E3_alte_lesart_u_ohne_T', 'pruefgroessen', 'u_E3a_median_grad', 'u_E3a_ohne_T_median_grad',
                    'abs_dphi_max_grad', 'q_Z', 'u_q_Z', 'u_q_Z_ohne_T', 'T_gezogen', 'T_B', 'T_anteil_unzulaessig',
                    'H1', 'H2', 'H1Z', 'H4', 'max_abs_z0', 'laeufe', 'laeufe_ungueltig'])
        for x in erg.values():
            job = x['auftrag']
            if job['art'] != 'kampagnen':
                continue
            pid = f'{job["szenario"]}/{job["stufe"]}'
            p = ck[pid]
            zp, _ = _zmax(x['daten'])
            for i, b in enumerate(x['daten']['befunde']):
                e = b.get('E3') or {}
                A = np.asarray(e.get('e3a') if e.get('e3a') is not None else np.zeros((0, 3)), float).reshape(-1, 3)
                q = None if e.get('e3b') is None else np.asarray(e['e3b'], float)
                t = e.get('t') or {}
                w.writerow([pid, i, b['seed'], e.get('bewertung') or '',
                            *((_ohne_grund(b)[0], _ohne_grund(b)[1]) if p['bewertungen'][i] is None else ('', '')),
                            p['alte_lesart_je_kampagne'][i] or '', A.shape[0] + (q is not None),
                            _g(np.median(A[:, 1]) if A.size else None), _g(np.median(A[:, 2]) if A.size else None),
                            _g(A[:, 0].max() if A.size else None), _g(None if q is None else q[0]),
                            _g(None if q is None else q[1]), _g(None if q is None else q[2]),
                            t.get('gezogen', ''), t.get('B', ''), _g(t.get('anteil_ungueltig')),
                            b['H1']['ausgang'], b['H2']['ausgang'], b['H1Z']['ausgang'], b['H4']['ausgang'],
                            _g(zp[i]), b['gueltigkeit']['n_laeufe'], b['gueltigkeit']['n_ungueltig']])


def _g(x):
    return '' if x is None or not np.isfinite(x) else f'{float(x):.6g}'


def bericht_einsetzen(pfad, tab):
    """Ersetzt in der Markdown-Datei die Blöcke <!-- tabelle:NAME --> … <!-- /tabelle --> durch die Tabellen."""
    with open(pfad, encoding='utf-8') as f:
        text = f.read()
    for name, inhalt in tab.items():
        muster = re.compile(rf'(<!-- tabelle:{name} -->).*?(<!-- /tabelle -->)', re.S)   # Blöcke nicht geschachtelt
        text = muster.sub(lambda m: f'{m.group(1)}\n{inhalt}\n{m.group(2)}', text)
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write(text)


def schreiben(pfad=neulauf.AUFTRAG, ausgabe=None, doku=None):
    """ergebnisse.json, kampagnen_e3.csv und die Tabellen in bericht.md (falls vorhanden) unter doku."""
    doku = doku or os.path.join(neulauf.WURZEL, neulauf.DOKU_REL)
    a, prof, erg = laden(pfad, ausgabe)
    with open(os.path.join(neulauf.WURZEL, a['altlauf']['auszug']), encoding='utf-8') as f:
        auszug = json.load(f)
    hist_pfad = os.path.join(neulauf.WURZEL, a['altlauf']['kompakt'])
    if neulauf.git_blob(hist_pfad) != a['altlauf']['git_blob']:
        raise neulauf.AuftragFehler('historische kompakte Datei verändert')
    with open(hist_pfad, encoding='utf-8') as f:
        hist = json.load(f)['inhalt']
    z, ck = zusammenstellen(a, prof, erg, auszug, hist, formate.sha256_datei(pfad))
    formate.schreibe_objekt(os.path.join(doku, 'ergebnisse'), formate.kopf(
        'bewertung', formate.synth_kennung(neulauf.KENNUNG, 'ERGEBNISSE')), z)
    kampagnenuebersicht(os.path.join(doku, 'kampagnen_e3.csv'), erg, ck)
    tab = tabellen(z)
    if os.path.exists(os.path.join(doku, 'bericht.md')):
        bericht_einsetzen(os.path.join(doku, 'bericht.md'), tab)
    return z, tab
