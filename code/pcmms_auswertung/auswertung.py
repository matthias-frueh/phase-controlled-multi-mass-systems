"""AP-12 (Werkzeug 6): öffentliche Trennstelle nach Plan AP-13, Abschnitt 2.6 c.

    laufzusammenfassung(laufdatei, kalibrierung, teil_b) -> Laufzusammenfassung        Stufe 1, A9.4 Schritte 1–6
    auswerten(zusammenfassungen, kalibrierung, teil_b, regeln, seed=None, bootstrap_indizes=None) -> Ergebnis
    auswerten_manifest(manifest, kalibrierung, teil_b, regeln, seed=None) -> Ergebnis   Stufe 1 + 2

Stufe 2 braucht keine Zeitreihen. Sie liest nur die Laufzusammenfassungen, die Kalibrierung (Umrechnung ist in Stufe 1
erfolgt; H3 und E3 lesen Kalibriergrößen), Teil B und das Regelprofil – nie die Generatorwahrheit (Schema
pcmms.wahrheit wird von den Lesefunktionen abgewiesen). Ablauf: Gültigkeit G1–G10 und Abbruchregeln (offline),
Kontaktast und Auswertbarkeit je Konfiguration, ŷ⁰ (Teil B nr3) und ŷ¹ (gültige Kontrollläufe), Bootstrap A/B,
H1 mit Sensitivitätsvarianten, H1Z, H2, H3 (Fassung K), H4, Nullkontrolle, Zuordnung, E3, Bericht.
"""
import time

import numpy as np

from . import (bootstrap as bs, formate, gueltigkeit, h1, h2 as h2m, h3 as h3m, h4 as h4m, kontrollen,
               konventionen as kv, regeln as rg, stufe1, vorhersage as vh, zusammenfassung as zf)
from . import anpassung, bericht, teil_b as teil_b_mod

VERSION = 'auswertung-0.2'       # 0.2: Korrekturen B, D und E
laufzusammenfassung = stufe1.laufzusammenfassung


def _profil(regeln):
    if isinstance(regeln, rg.Regelprofil):
        return regeln
    if isinstance(regeln, str) and regeln.split('+')[0] in rg.PROFILE:
        return rg.profil(regeln)
    return rg.lade_profil(regeln)


def _hash_objekt(obj):
    sk, felder = formate.zerlege(obj)
    return formate.sha256_json(dict(skelett=sk, npz=formate.sha256_bytes(formate.npz_bytes(felder))
                                    if felder else None))


G4_LJ_REGEL = dict(schwelle='n_abhaengig', vergleich='pooling')


def _g4_2026_11(tb, profil):
    """G4-Modus, Schwellen je Konfiguration und Lⱼ-Schwellen aus Teil B nr2.g4 im Profilstand 2026-11 (g4.verfahren,
    g4.lj). Historische Profile: (None, None, None). Fehlt der Block in Teil B, bleiben die Größen leer und G4 der
    betroffenen Läufe ist „nicht prüfbar“ (kein stiller Rückgriff auf die Regel je Laufart)."""
    if 'g4.verfahren' not in profil.regeln or not profil.hat('g4.verfahren'):
        return None, None, None
    from . import g4
    modus = profil.wert('g4.verfahren')
    if modus not in g4.MODI:
        raise ValueError(f'g4.verfahren {modus!r} nicht umgesetzt ({", ".join(g4.MODI)})')
    if profil.wert('g4.lj') != G4_LJ_REGEL:
        raise ValueError(f'g4.lj {profil.wert("g4.lj")!r} nicht umgesetzt ({G4_LJ_REGEL})')
    blk = tb['nr2'].get('g4') or {}
    konfig = blk.get(modus) if modus in ('b_plus', 'd') else None
    lj = {g: dict(N=v['N'], F=v['F']) for g, v in ((blk.get('lj') or {}).get('n_abhaengig') or {}).items()}
    return modus, konfig, lj


def _schwellen(tb, profil):
    n2 = tb['nr2']
    st = n2.get('sigma_tol_grad') or {}
    g4m, g4k, g4l = _g4_2026_11(tb, profil)
    return gueltigkeit.Schwellen(
        f_soll=n2['f'], kmax=n2['k_max'], delta_phi_tol_grad=profil.wert('g2.delta_phi_tol_grad'),
        sigma_tol_grad={int(k): v for k, v in st.items()} if st else None, sigma_delta=n2.get('sigma_delta'),
        F_LO_zellen=n2.get('F_LO_zellen'), delta_delta_grad=n2['delta_delta_grad'], delta_f_tol=n2.get('delta_f_tol'),
        eps_ctrl=n2.get('eps_ctrl'), sigma_ref=n2.get('sigma_ref'), sigma_ref_zellen=n2.get('sigma_ref_zellen'),
        g4_faktor=profil.wert('g4.faktor'), alarm_faktor=profil.wert('h0.alarm_faktor'), T_P0=n2.get('T_P0'),
        Delta_T=n2.get('Delta_T'), g4_modus=g4m, g4_konfig=g4k, g4_lj=g4l)


def _quellen(t1, pr, konf):
    """Gültige Läufe je Konfiguration und je Kontrollmodul (Phase 1), sortiert nach Position."""
    gueltig = pr['gueltig']
    pos = t1.spalte('position', int)
    lauf = {}
    for c in konf:
        sel = [i for i, k in enumerate(t1.koepfe) if k['laufart'] == 'K' and k['konfiguration']['id'] == c['id']
               and gueltig[i]]
        lauf[c['id']] = sorted(sel, key=lambda i: pos[i])
    kontroll = {}
    for e in (1, 2):
        for j in (1, 2, 3):
            sel = [i for i, k in enumerate(t1.koepfe) if k['laufart'] == 'L' and k['modul'] == j
                   and k['einstellung'] == e and gueltig[i]]
            kontroll[(e, j)] = sorted(sel, key=lambda i: pos[i])
    return lauf, kontroll


def _online_gueltig(v):
    """Gültigkeit eines Versuchs nach den Entscheidungen des Ablaufs (G2–G10, Nullpunktalarm, feststehendes G1)."""
    return bool(v.get('gueltig')) and v.get('g1') is not True


def _x_strich_gegenprobe(t1, pr, v4=False):
    """X′ des zustandsbehafteten Ablaufs offline nachgeprüft: Die einschließenden gültigen Referenzläufe gleichen dem
    Bezug des Ablaufs, „vorgesehen“ (R₂/R₃ desselben G1-Falls) folgt allein aus den Köpfen, und ein S1 an X′ setzt die
    vorgesehene Klammer voraus. Auf ein nach G2–G10 gültiges X′ folgt unmittelbar das R₃ seines Falls (sonst hätte ein
    anderer Versuch die Klammer unterbrochen); ausgenommen ist ein Halt an X′ selbst vor R₃ (andere Regel als S1).
    ablauf-4 (Z1): R₃ folgt auch auf ein nach G2–G10 ungültiges X′, außer bei einem Halt an X′."""
    ka, kb = pr['g1_klammer'] if pr.get('g1_klammer') is not None else (None, None)
    abw = []
    for i, k in enumerate(t1.koepfe):
        v = k['versuch']
        if v.get('rolle') != 'X_strich':
            continue
        if i + 1 < len(t1.koepfe) and (v4 or set(pr['gruende'][i]) <= {'G1'}) and v.get('halt') in (None, 'S1'):
            w = t1.koepfe[i + 1]['versuch']
            if w.get('rolle') != 'R3' or w.get('bezug_versuch') != v.get('bezug_versuch'):
                abw.append(f'{v["id"]}: auf X′ folgt {w.get("id")} ({w.get("rolle")}), nicht R₃ des Falls '
                           f'{v.get("bezug_versuch")}')
        a, b = (-1, -1) if ka is None else (int(ka[i]), int(kb[i]))
        vorgesehen = gueltigkeit.x_strich_klammer(t1.koepfe, i, a, b)
        if v.get('g1_bezug') is not None:
            off = [t1.koepfe[a]['versuch']['id'] if a >= 0 else None, t1.koepfe[b]['versuch']['id'] if b >= 0 else None]
            if off != list(v['g1_bezug']):
                abw.append(f'{v["id"]}: Bezug offline {off} ≠ Ablauf {v["g1_bezug"]}')
            if bool((v.get('g1_klammer') or {}).get('vorgesehen')) != vorgesehen:
                abw.append(f'{v["id"]}: Klammer R₂/R₃ offline {"vorgesehen" if vorgesehen else "unvollständig"}')
        if v.get('halt') == 'S1' and not vorgesehen:
            abw.append(f'{v["id"]}: S1 ohne vorgesehene Klammer R₂/R₃')
    if abw:
        raise formate.FormatFehler('X′ offline ≠ Ablauf: ' + '; '.join(abw[:5]))


def _w_satz_ende(t1, V, pos, h, ks):
    """Ende des Kontrollsatzes ks einer Wiederaufnahme nach Versuch h, offline wie im Ablauf: der erste Versuch mit der
    Kennung ks, nach dem kein Mitglied mehr aussteht und kein später gemessener Versuch mit der Kennung ks schon
    ausgelöst war. Eine Kontroll- oder S3-Wiederholung löst ihr Lauf aus, ein X′ der gültige Referenzlauf, der den
    G1-Verstoß seines Falls feststellt (der erste nach dem Fall); ein erst nach dem Ende ausgelöstes X′ eines Mitglieds
    verlängert den Kontrollsatz nicht. None ohne Versuch mit der Kennung ks."""
    W = [j for j in range(h + 1, len(V)) if V[j].get('kontrollsatz') == ks]

    def ausloeser(j):
        v = V[j]
        if v.get('rolle') == 'wiederaufnahme_kontrolle':
            return h
        if v.get('rolle') == 'X_strich':
            i = pos.get(v.get('bezug_versuch'), h)
            return next((k for k in range(i + 1, j) if t1.koepfe[k]['laufart'] == 'R' and _online_gueltig(V[k])), h)
        return pos.get(v.get('bezug_versuch'), h)
    return next((m for m in W if all(ausloeser(j) > m for j in W if j > m)), None)


def _folgen_gegenprobe(t1, abl):
    """ablauf-4 offline: R₁ folgt unmittelbar auf seinen Lauf (also nie über eine Unterbrechung); auf R₂ folgt (nach
    nicht reproduzierten Alarmwiederholungen von R₂) das X′ desselben Falls, außer bei einem Halt (Z1, geschlossene
    Folge); nach einem Halt beginnt die Wiederaufnahme mit dem Aufwärmen (Tageswechsel), dem Bezugslauf (Nullpunkthalt)
    oder dem Kontrollsatz; R₂, X′ und R₃ zu einem Lauf von vor der Wiederaufnahme kommen erst nach dem Ende von deren
    Kontrollsatz (_w_satz_ende; verworfene Folgeläufe und neue Folge, H1); jeder Bezugswechsel nennt einen gültigen
    Referenzlauf ohne Nullpunktalarm als neuen Bezug."""
    V = [k['versuch'] for k in t1.koepfe]
    pos = {v['id']: i for i, v in enumerate(V)}
    abw = []
    for i, v in enumerate(V):
        if v.get('rolle') == 'R1' and (i == 0 or V[i - 1]['id'] != v.get('bezug_versuch')):
            abw.append(f'{v["id"]}: R₁ folgt nicht unmittelbar auf {v.get("bezug_versuch")}')
        if v.get('rolle') == 'R2':
            j = i + 1
            while j < len(V) and V[j].get('rolle') == 'alarmwiederholung' \
                    and V[j].get('bezug_versuch') == V[j - 1]['id']:
                j += 1
            if j < len(V) and not V[j - 1].get('halt') and (V[j].get('rolle') != 'X_strich'
                                                            or V[j].get('bezug_versuch') != v.get('bezug_versuch')):
                abw.append(f'{v["id"]}: auf R₂ folgt {V[j]["id"]} ({V[j].get("rolle")}), nicht X′ des Falls '
                           f'{v.get("bezug_versuch")}')
    for w in abl.get('wiederaufnahmen') or []:
        h = pos.get(w.get('nach_versuch'))
        if h is None or h + 1 >= len(V):
            continue
        erwartet = 'aufwaermen' if w['tageswechsel'] else ('bezugslauf' if w['bezugseroeffnung'] else
                                                          'wiederaufnahme_kontrolle')
        if V[h + 1].get('rolle') != erwartet:
            abw.append(f'Wiederaufnahme {w["nummer"]}: erster Versuch {V[h + 1]["id"]} ({V[h + 1].get("rolle")}), '
                       f'erwartet {erwartet}')
        ende = _w_satz_ende(t1, V, pos, h, w['kontrollsatz'])
        for j in range(h + 1, len(V)):
            v = V[j]
            if v.get('rolle') in ('R2', 'X_strich', 'R3') and pos.get(v.get('bezug_versuch'), len(V)) <= h \
                    and ende is not None and j < ende:
                abw.append(f'{v["id"]}: {v["rolle"]} zu {v["bezug_versuch"]} vor dem Ende des Kontrollsatzes '
                           f'{w["kontrollsatz"]}')
    for b in abl.get('bezugswechsel') or []:
        j = pos.get(b['neu'])
        if j is None or not V[j].get('gueltig') or V[j].get('alarm'):
            abw.append(f'Bezugswechsel {b}: neuer Bezug kein gültiger Referenzlauf ohne Alarm')
    if abw:
        raise formate.FormatFehler('Folgen offline ≠ ablauf-4: ' + '; '.join(abw[:5]))


def _s2_gegenprobe(ab, abl):
    """S2-Bilanz offline (gueltigkeit.abbruchregeln aus den S2-Versuchen und den im Ablaufstand protokollierten
    Wiederaufnahmen) gegen den Ablauf: dieselben S2-Versuche, dieselben maßgeblichen S2 und „Phase 1 beendet“ genau
    dann, wenn der Ablauf nach S2 abgebrochen hat (bei Ablauf mit Halten). Der Status allein ersetzt die Prüfung nicht."""
    bil = ab.get('S2_bilanz') or {}
    online = abl.get('s2_bilanz')
    abw = []
    if bil.get('s2') and online is None:
        abw.append('Ablaufstand ohne S2-Bilanz')
    elif online is not None:
        if list(online.get('s2') or []) != list(bil.get('s2') or []):
            abw.append(f'S2-Versuche offline {bil.get("s2")} ≠ Ablauf {online.get("s2")}')
        if list(online.get('massgeblich') or []) != list(bil.get('massgeblich') or []):
            abw.append(f'maßgebliche S2 offline {bil.get("massgeblich")} ≠ Ablauf {online.get("massgeblich")}')
    if (abl.get('optionen') or {}).get('halt', True):
        beendet = abl.get('status') == 'abgebrochen' and (abl.get('halt') or {}).get('regel') == 'S2'
        if bool(bil.get('beendet')) != beendet:
            abw.append(f'Phase 1 nach S2 beendet: offline {bool(bil.get("beendet"))}, Ablauf {abl.get("status")}')
    if abw:
        raise formate.FormatFehler('S2-Bilanz offline ≠ Ablauf: ' + '; '.join(abw))


def datenlage(tab, tb, prof):
    """Gültigkeit (offline), Abbruchregeln, gültige Läufe je Konfiguration und Kontrollmodul, ŷ¹-Gültigkeit, Kontaktast
    und Auswertbarkeit der Phase 1 – ohne Bootstrap (auch für Zähl- und Ablaufdiagnosen des Harness).

    Läufe des zustandsbehafteten Ablaufs (Köpfe mit „versuch“): Die offline geprüfte Gültigkeit muss den Entscheidungen
    des Ablaufs gleichen, je Konfiguration und Block ist höchstens ein Versuch gültig (kein Doppelbeitrag), und ein
    angehaltener oder abgebrochener Ablauf sperrt alle Ausgänge (Datenlage)."""
    n2 = tb['nr2']
    n_min = int(n2['n_min'])
    konf = n2['konfigurationen']
    t1 = tab.auswahl(tab.spalte('phase', int) == 1).sortiert()
    # Gültigkeit und Abbruch (offline)
    sw = _schwellen(tb, prof)
    pr = gueltigkeit.pruefe(t1, sw)
    ab = gueltigkeit.abbruchregeln(t1, pr)
    lauf, kontroll = _quellen(t1, pr, konf)
    d = t1.daten
    E0 = [np.asarray(e['Nk_zellen']) for e in tb['nr3']['einzel0']]
    E1 = [d['Nk_zellen'][kontroll[(1, j)]] for j in (1, 2, 3)]
    Nbar0 = np.stack([e.mean(0) for e in E0])
    Nbar1 = np.stack([e.mean(0) if e.shape[0] else np.full(E0[0].shape[1:], np.nan + 0j) for e in E1])
    # ŷ¹ gültig? (Liftoff in einem Kontrolllauf, ausgenommen G5/G8/G10-ungültige)
    reg = pr['regeln']
    lift_kontroll = [t1.koepfe[i]['lauf_id'] for i, k in enumerate(t1.koepfe) if k['laufart'] == 'L'
                     and k['einstellung'] == 1 and reg['G6'][i] is True
                     and not any(reg[g][i] is True for g in ('G5', 'G8', 'G10'))]
    yhat1_gueltig = not lift_kontroll and all(e.shape[0] >= 2 for e in E1)
    sperren_alle = []
    if ab['S2_phase_beendet']:
        sperren_alle.append(('Datenlage', 'Phase 1 nach zweitem S2 als abgebrochene Kampagne beendet (§9.2)'))
    sperren_y1 = [] if yhat1_gueltig else [('Datenlage', 'ŷ¹ ungültig: ' + (
        f'Einzelzell-Liftoff in Kontrollläufen {lift_kontroll}' if lift_kontroll else 'zu wenige gültige Kontrollläufe'))]
    # Kontaktast und Auswertbarkeit
    reserve = prof.wert('kontaktast.reserve')
    info = {}
    for c in konf:
        idx = lauf[c['id']]
        alle = [i for i, k in enumerate(t1.koepfe) if k['konfiguration']['id'] == c['id']]
        lift = [t1.koepfe[i]['lauf_id'] for i in alle if reg['G6'][i] is True
                and not any(reg[g][i] is True for g in ('G5', 'G8', 'G10'))]
        e = dict(n_gueltig=len(idx), n_laeufe=len(alle), liftoff=lift)
        if idx and c['einstellung'] == 1:
            rho = vh.zeiger_mittel(d['zeiger'][idx], d['n_zyklen'][idx] if 'n_zyklen' in d else
                                   t1.spalte('n_zyklen', int)[idx])
            ok_a, mn = vh.kontaktast(Nbar0, rho, n2['N_s_zellen'], n2['F_c_stat'], reserve)
            e.update(bedingung_a=ok_a, min_zelle_vorhersage=mn.tolist())
            e['kontaktast'] = bool(ok_a and not lift)
        else:
            e['kontaktast'] = bool(idx) and not lift
        e['auswertbar'] = bool(e['kontaktast'] and len(idx) >= n_min)
        info[c['id']] = e
    for i in ab['S2']:
        kid = t1.koepfe[i]['konfiguration']['id']
        if kid in info:
            info[kid]['auswertbar'] = False
            info[kid]['s2'] = True
    auswertbar = {k for k, v in info.items() if v['auswertbar']}
    zustand = any('versuch' in k for k in t1.koepfe)
    abl = tab.meta.get('ablauf')
    if zustand:
        if abl is None:
            raise formate.FormatFehler('Läufe des zustandsbehafteten Ablaufs ohne Ablaufstand (meta „ablauf“)')
        abw = [k['lauf_id'] for i, k in enumerate(t1.koepfe) if _online_gueltig(k['versuch']) != bool(pr['gueltig'][i])]
        if abw:
            raise formate.FormatFehler(f'Gültigkeit offline ≠ Entscheidung des Ablaufs für {abw[:5]}'
                                       + (f' und {len(abw) - 5} weitere' if len(abw) > 5 else ''))
        zahl = {}
        for i, k in enumerate(t1.koepfe):
            if k['laufart'] == 'K' and pr['gueltig'][i]:
                zahl[(k['konfiguration']['id'], k['block'])] = zahl.get((k['konfiguration']['id'], k['block']), 0) + 1
        doppelt = sorted(x for x, c in zahl.items() if c > 1)
        if doppelt:
            raise formate.FormatFehler(f'mehr als ein gültiger Versuch je Konfiguration und Block: {doppelt[:5]}')
        v4 = abl.get('version') == 'ablauf-4'
        _x_strich_gegenprobe(t1, pr, v4=v4)
        if v4:
            _folgen_gegenprobe(t1, abl)
        _s2_gegenprobe(ab, abl)
        if abl.get('status') != 'abgeschlossen':
            sperren_alle.append(('Datenlage', f'Phase 1 {abl.get("status")}: {(abl.get("ende") or {}).get("grund")} '
                                              '(keine abgeschlossene Kampagne)'))
    return dict(t1=t1, sw=sw, pr=pr, ab=ab, lauf=lauf, kontroll=kontroll, d=d, E0=E0, E1=E1, Nbar0=Nbar0, Nbar1=Nbar1,
                reg=reg, yhat1_gueltig=yhat1_gueltig, sperren_alle=sperren_alle, sperren_y1=sperren_y1, info=info,
                auswertbar=auswertbar, lift_kontroll=lift_kontroll, ablauf=abl if zustand else None)


def auswerten(zusammenfassungen, kalibrierung, teil_b, regeln, seed=None, bootstrap_indizes=None):
    """Stufe 2: Ergebnis (dict) aus Laufzusammenfassungen (LaufTabelle oder Pfad), Kalibrierung, Teil B und Regeln."""
    t_start = time.perf_counter()
    tab = zusammenfassungen if isinstance(zusammenfassungen, zf.LaufTabelle) else zf.LaufTabelle.lesen(
        zusammenfassungen)
    kal = kalibrierung if isinstance(kalibrierung, dict) else anpassung.lies_kalibrierung(kalibrierung)[1]
    tb = teil_b if isinstance(teil_b, dict) else formate.lies_objekt(teil_b, 'teil_b')[1]
    prof = _profil(regeln)
    if tab.meta.get('datenart') not in (None, 'synthetisch'):
        raise formate.FormatFehler('AP-12 verarbeitet in dieser Stufe nur synthetische Daten')
    n2, n4 = tb['nr2'], tb['nr4']
    kmax, K, f = int(n2['k_max']), int(tab.k_voll), float(n2['f'])
    n_min = int(n2['n_min'])
    konf = n2['konfigurationen']
    schnitt = [c['id'] for c in konf if c['gruppe'] == 'schnitt']
    seed = tb.get('seed_bootstrap') if seed is None else seed
    dl = datenlage(tab, tb, prof)
    t1, sw, pr, ab, lauf, kontroll, d = (dl[x] for x in ('t1', 'sw', 'pr', 'ab', 'lauf', 'kontroll', 'd'))
    E0, E1, Nbar0, Nbar1, reg = (dl[x] for x in ('E0', 'E1', 'Nbar0', 'Nbar1', 'reg'))
    yhat1_gueltig, sperren_alle, sperren_y1 = dl['yhat1_gueltig'], dl['sperren_alle'], dl['sperren_y1']
    info, auswertbar = dl['info'], dl['auswertbar']
    # Indexmatrizen
    e2 = n2.get('einstellung2')
    reihenfolge = bs.quellen_reihenfolge([c['id'] for c in konf], einstellung2=bool(e2))
    groessen = {f'A/{c["id"]}': len(lauf[c['id']]) for c in konf}
    groessen.update({f'B1/modul{j}': len(kontroll[(1, j)]) for j in (1, 2, 3)})
    if e2:
        groessen.update({f"B1′/modul{j}": len(kontroll[(2, j)]) for j in (1, 2, 3)})
    if bootstrap_indizes is None:
        B = prof.zahl('bootstrap_B')
        idx = bs.indexmatrizen(seed, groessen, B, reihenfolge)
        idx_quelle = f'SeedSequence({seed}).spawn, Reihenfolge Plan 2.6 c'
    else:
        idx = {k.replace('__', '/'): np.asarray(v) for k, v in bootstrap_indizes.items()}
        B = int(next(iter(idx.values())).shape[0])
        idx_quelle = 'übergeben'
    B0 = {k: np.asarray(v)[:B] for k, v in tb['nr3']['indizes'].items()}
    if any(v.shape[0] < B for v in B0.values()):
        raise formate.FormatFehler('Teil B: B⁰ⱼ hat weniger Replikate als die Auswertung verlangt')
    idxB0 = [B0[f'B0/modul{j}'] for j in (1, 2, 3)]
    idxB1 = [idx.get(f'B1/modul{j}') for j in (1, 2, 3)]
    # H1 und H1Z
    P = len(schnitt)
    q = {x: np.full((P, 4, 7), np.nan) for x in ('y', 'y0', 'y1', 'varA0', 'varA1', 'varB0', 'varB1')}
    nA = np.full(P, np.nan)
    for i, kid in enumerate(schnitt):
        if kid not in auswertbar or not yhat1_gueltig:
            continue
        ii = lauf[kid]
        X, Z, nz = d['Nk_zellen'][ii], d['zeiger'][ii], t1.spalte('n_zyklen', int)[ii]
        rho = vh.zeiger_mittel(Z, nz)
        q['y'][i] = bs._q4(X.mean(0), kmax)
        q['y0'][i] = bs._q4(vh.vorhersage(Nbar0, rho, zellen=True), kmax)
        q['y1'][i] = bs._q4(vh.vorhersage(Nbar1, rho, zellen=True), kmax)
        v = bs.h1_varianzen(X, Z, nz, Nbar0, Nbar1, E0, E1, idx[f'A/{kid}'], idxB0, idxB1, rho, kmax)
        for name in ('varA0', 'varA1', 'varB0', 'varB1'):
            q[name][i] = v[name]
        nA[i] = len(ii)
    nB0 = min(e.shape[0] for e in E0)
    nB1 = min(e.shape[0] for e in E1) if E1 else 0
    sperren_bias = []
    if n4.get('bias0') is None or n4.get('bias1') is None:
        sperren_bias.append(('Verfahren', 'Rauschbias b̂⁰/b̂¹ fehlt in Teil B (Werkzeug 8)'))
        b0 = b1 = ub0 = ub1 = np.zeros(P)
    else:
        b0, b1 = np.asarray(n4['bias0'], float), np.asarray(n4['bias1'], float)
        ub0, ub1 = np.asarray(n4['u_bias0'], float), np.asarray(n4['u_bias1'], float)
    D = np.asarray(n4['Delta'], float)
    T0 = h1.tests_bilden(q['y'][:, 0], q['y0'][:, 0], q['varA0'][:, 0], q['varB0'][:, 0], nA, nB0, b0, ub0, delta=D)
    T1 = h1.tests_bilden(q['y'][:, 0], q['y1'][:, 0], q['varA1'][:, 0], q['varB1'][:, 0], nA, nB1, b1, ub1, delta=D)
    voll = all(k in auswertbar for k in schnitt)
    c_H1 = tb['nr10'].get('c_H1')
    sperren_h1 = sperren_alle + sperren_y1 + sperren_bias
    H1 = h1.entscheiden(T0, T1, np.asarray(n4['Delta'], float), np.asarray(n4['Delta_rel'], float), c_H1, voll, prof,
                        sperren_h1, 'H1')
    H1.update(tests0=T0, tests1=T1, c_herkunft=tb['nr10'].get('c_H1_herkunft'), d_fassung=n4.get('d_fassung'),
              faktor=n4.get('faktor'), punkte=schnitt, groessen=list(kv.GROESSEN_H1), bias=dict(
                  b0=b0, b1=b1, u_b0=ub0, u_b1=ub1, herkunft=n4.get('bias_herkunft')))
    sens = {}
    for name, D in (('faktor_0_1', n4['Delta_sens_0_1']), ('fassung_A', n4['Delta_sens_A'])):
        s = h1.entscheiden(T0, T1, np.asarray(D, float), np.asarray(D, float), c_H1, voll, prof, sperren_h1, name)
        sens[name] = dict(ausgang=s['ausgang'], grund=s['grund'], zusaetze=s['zusaetze'], Delta=np.asarray(D))
    # H1Z
    h1z = n4.get('h1z') or {}
    sperren_z = list(sperren_alle + sperren_y1)
    if h1z.get('Delta_c') is None:
        sperren_z.append(('Verfahren', 'Grenzen von H1Z offen (Regel h1z.grenzen)'))
        Dc = Dcr = np.full(7, np.nan)
    else:
        Dc, Dcr = np.asarray(h1z['Delta_c'], float), np.asarray(h1z['Delta_c_rel'], float)
    if n4.get('bias0_zellen') is None:
        sperren_z.append(('Verfahren', 'Rauschbias je Zelle fehlt in Teil B (Werkzeug 8)'))
        bz0 = bz1 = ubz0 = ubz1 = np.zeros((P, 3))
    else:
        bz0, bz1 = np.asarray(n4['bias0_zellen'], float), np.asarray(n4['bias1_zellen'], float)
        ubz0, ubz1 = np.asarray(n4['u_bias0_zellen'], float), np.asarray(n4['u_bias1_zellen'], float)
    nAz = np.repeat(nA[:, None], 3, 1)
    Dz = None if np.isnan(Dc).all() else Dc
    Tz0 = h1.tests_bilden(q['y'][:, 1:], q['y0'][:, 1:], q['varA0'][:, 1:], q['varB0'][:, 1:], nAz, nB0, bz0, ubz0,
                          delta=Dz)
    Tz1 = h1.tests_bilden(q['y'][:, 1:], q['y1'][:, 1:], q['varA1'][:, 1:], q['varB1'][:, 1:], nAz, nB1, bz1, ubz1,
                          delta=Dz)
    H1Z = h1.entscheiden(Tz0, Tz1, Dc, Dcr, tb['nr10'].get('c_H1Z'), voll, prof, sperren_z, 'H1Z')
    H1Z.update(tests0=Tz0, tests1=Tz1, c_herkunft=tb['nr10'].get('c_H1Z_herkunft'), regel=h1z.get('regel'))
    # H2
    n6 = tb['nr6']
    sperren_h2 = list(sperren_alle + sperren_y1)
    W_ids = n6.get('W_ids') or []
    if not n6.get('W'):
        sperren_h2.append(('Verfahren', n6.get('grund', 'Fitfenster fehlt in Teil B')))
    elif not n6['W']['ausreichend']:
        sperren_h2.append(('Datenlage', 'weniger als zwei Punkte auf einer Seite des Fitfensters'))
    fehl = [k for k in W_ids if k not in auswertbar]
    if fehl:
        try:
            prof.wert('h2.vollstaendigkeit')
            sperren_h2.append(('Datenlage', f'Punkte von W nicht auswertbar: {fehl}'))
        except rg.RegelOffen as e:
            sperren_h2.append(('Verfahren', f'Punkte von W nicht auswertbar {fehl}; {e.grund}'))
    if W_ids and not fehl and yhat1_gueltig:
        KW = [dict(Nk=d['Nk_summe'][lauf[k]], Z=d['zeiger'][lauf[k]], nz=t1.spalte('n_zyklen', int)[lauf[k]])
              for k in W_ids]
        H2 = h2m.h2_auswerten(KW, [e.sum(1) for e in E0], [e.sum(1) for e in E1], [idx[f'A/{k}'] for k in W_ids],
                              idxB0, idxB1, kmax, float(n2['delta_delta_grad'][1]), prof, tb['nr10'].get(
                                  'h2_intervall'), dict(W_ids=W_ids, **(n6.get('W') or {})), sperren_h2)
    else:
        rang = ['Datenlage', 'Verfahren', 'Drift', 'Graubereich', 'Präzision']
        kl = sorted({k for k, _ in sperren_h2}, key=rang.index) or ['Datenlage']
        H2 = dict(ausgang='nicht entscheidbar', grund=kl[0], gruende=[dict(klasse=k, text=t) for k, t in sperren_h2],
                  zusaetze=[], W=dict(W_ids=W_ids))
    # H3 (Fassung K) aus der Kalibrierung
    eing = anpassung.h3_eingaenge(kal)
    if eing['fehlend'] or sperren_alle:
        H3 = dict(ausgang='nicht entscheidbar', grund='Verfahren' if eing['fehlend'] else 'Datenlage',
                  gruende=[dict(klasse='Verfahren', text=x) for x in eing['fehlend']] +
                  [dict(klasse=k, text=t) for k, t in sperren_alle], zusaetze=[])
        vor3 = None
    else:
        rng = bs.mc_strom(seed, reihenfolge, 'H3')
        p05 = kal['p0_5']
        vor3 = h3m.vorhersage_mc(eing, p05['f_hz'], p05['u_f_hz'], rng, prof.zahl('h3_mc'))
        H3 = h3m.h3_auswerten([e.sum(1) for e in E1], idxB1, vor3, prof, n_min)
    # H4
    H4 = h4m.h4_auswerten(tb['nr8']['V'], {k: dict(Nk=d['Nk_summe'][lauf[k]]) for k in auswertbar},
                          {k: idx[f'A/{k}'] for k in auswertbar}, kmax, prof, auswertbar)
    if sperren_alle:
        H4.update(ausgang='nicht entscheidbar', grund='Datenlage')
    # Nullkontrolle
    art = t1.spalte('laufart', object)
    nicht_g1 = np.array([not any(reg[g][i] is True for g in gueltigkeit.REGELN_G if g != 'G1')
                         for i in range(len(t1))])
    ref_gueltig = np.flatnonzero((art != 'R') | pr['gueltig'])
    loo = gueltigkeit.sigma_ref(t1.auswahl(ref_gueltig), phase=1).get('loo')
    H0 = kontrollen.nullkontrolle(pr['delta_N'][(art == 'K') & nicht_g1], [] if loo is None else loo,
                                  n2.get('eps_ctrl'), prof)
    H0['g1_verletzt'] = [t1.koepfe[i]['lauf_id'] for i in range(len(t1)) if reg['G1'][i] is True]
    # Zuordnung
    zu = None
    if e2:
        zu = _zuordnung(e2, t1, d, lauf, kontroll, auswertbar, tb, T0, T1, schnitt, c_H1, idx, B0, kmax, prof,
                        Nbar0, Nbar1)
    # E3 (Regelstand 2026-11: Prüfmenge schnitt21_triphasik = alle 21 Schnittpunkte, auch nicht auswertbare, und der
    # Triphasik-Punkt; Kriterien von A9.11 aus Teil B nr10.e3_kriterien, sofern Werkzeug 8 sie ausweist; historische
    # Profile lesen punkte und kriterien nicht)
    E3 = None
    nr5 = tb['nr5']
    T = nr5.get('T')
    if T is not None and kal['p0_1']['laststellen'].get('bestimmbar'):
        ls = kal['p0_1']['laststellen']
        xy = np.c_[ls['x_m'], ls['y_m']]
        try:
            prof.wert('e3.pruefmenge')
        except rg.RegelOffen:
            pass
        KE = {k: dict(Xz=d['Nk_zellen'][lauf[k]], Z=d['zeiger'][lauf[k]], nz=t1.spalte('n_zyklen', int)[lauf[k]])
              for k in schnitt if k in auswertbar}
        if KE:
            uq = 360.0 * f / float(n2.get('f_takt', 1e6)) * np.sqrt(2 / 12)
            beschr = nr5.get('unsicherheit')
            tz = (kontrollen.t_ziehungen(beschr, bs.mc_strom(seed, reihenfolge, 'E3/T'), int(B)) if beschr
                  else None)
            E3 = kontrollen.e3_auswerten(KE, E0, {k: idx[f'A/{k}'] for k in KE}, idxB0, np.asarray(T), xy,
                                         n2['delta_delta_grad'], n2['u_delta_delta_grad'], None, 'S120', prof,
                                         bs.mc_strom(seed, reihenfolge, 'E3'), uq, T_zieh=tz, punkte=list(schnitt),
                                         kriterien=(tb.get('nr10') or {}).get('e3_kriterien'))
    # beschreibend: A und F_max je Schnittpunkt mit Vorhersage
    beschr = {}
    for kid in schnitt:
        if kid in auswertbar:
            ii = lauf[kid]
            rho = vh.zeiger_mittel(d['zeiger'][ii], t1.spalte('n_zyklen', int)[ii])
            km = kv.kenngroessen(d['Nk_summe'][ii].mean(0)[:kmax])
            kp = kv.kenngroessen(vh.vorhersage(Nbar0[:, :, :kmax].sum(1), rho[:, :kmax]))
            beschr[kid] = dict(A_messung=float(km['A']), A_yhat0=float(kp['A']), F_max_messung=float(km['F_max_rel']),
                               F_max_yhat0=float(kp['F_max_rel']))
    vb = zf.verarbeitungsstand(tab.koepfe)
    vb0 = (tb.get('nr1') or {}).get('phase0_verarbeitung')
    vb['teil_b_phase0'] = vb0 or 'nicht angegeben (Teil B vor Korrektur B erstellt)'
    vb['alte_bedeutung'] = sorted(set(vb['alte_bedeutung']) | set((vb0 or {}).get('alte_bedeutung', [])) |
                                  (set() if vb0 else {'Teil B ohne Verarbeitungsstand'}))
    erg = dict(
        version=VERSION,
        herkunft=dict(zusammenfassungen_sha256=formate.sha256_bytes(formate.npz_bytes(tab.daten)), verarbeitung=vb,
                      koepfe_sha256=formate.sha256_json(tab.koepfe), kalibrierung_sha256=formate.sha256_json(kal),
                      teil_b_sha256=_hash_objekt(tb), profil=prof.kurz(), seed=seed, B=int(B),
                      bootstrap_indizes=idx_quelle, n_mc_h3=prof.zahl('h3_mc'), reduziert=prof.reduziert,
                      code_version=formate.code_version(), kennung=tab.meta.get('kennung'),
                      laufzeit_s=round(time.perf_counter() - t_start, 3), pilot_suche=n2.get('pilot_suche'),
                      teil_b=teil_b_mod.einordnen(tb), ablauf=dl['ablauf']),
        gueltigkeit=dict(n_laeufe=len(t1), n_ungueltig=int((~pr['gueltig']).sum()),
                         gruende={t1.koepfe[i]['lauf_id']: pr['gruende'][i] for i in np.flatnonzero(~pr['gueltig'])},
                         nicht_pruefbar={g: len(v) for g, v in pr['nicht_pruefbar'].items()},
                         abbruch=dict(S2=[t1.koepfe[i]['lauf_id'] for i in ab['S2']],
                                      S2_phase_beendet=ab['S2_phase_beendet'],
                                      S4=[t1.koepfe[i]['lauf_id'] for i in ab['S4']],
                                      S1_kandidaten=[t1.koepfe[i]['lauf_id'] for i in ab['S1_kandidaten']],
                                      S1=ab['S1'], hinweis=ab['hinweis']),
                         S3=gueltigkeit.s3_pruefung(_mit_phase0(t1, E0), np.r_[np.ones(sum(e.shape[0] for e in E0),
                                                                                       bool), pr['gueltig']], kmax)),
        konfigurationen=info, n_auswertbar=len(auswertbar), yhat1_gueltig=yhat1_gueltig,
        H1=H1, H1_sensitivitaet=sens, H1Z=H1Z, H2=H2, H3=H3, H4=H4, H0=H0, zuordnung=zu, E3=E3,
        beschreibend=beschr,
        offene_regeln=prof.kurz()['offen'], nicht_implementiert=prof.kurz()['nicht_implementiert'])
    erg['text'] = bericht.text(erg)
    return erg


def _mit_phase0(t1, E0):
    """Kontrolltabelle für S3: Phase-0-Einzelmodulläufe aus Teil B (als Läufe der Phase 0) und die Phase-1-Läufe."""
    koepfe, daten = [], {n: [] for n in zf.DATENFELDER}
    K = t1.k_voll
    leer = zf.leere_daten(K)
    for j, e in enumerate(E0):
        for r in range(e.shape[0]):
            koepfe.append(dict(lauf_id=f'TB-L{j + 1}-{r}', laufart='L', modul=j + 1, einstellung=1,
                               konfiguration=dict(id=f'L{j + 1}', gruppe='einzel', phi_soll_grad=None), phase=0,
                               block=None, messtag=None, position=-1, kontrollsatz=None, t_start=0.0, t_ende=0.0,
                               f_soll=0.0, f_mittel=0.0, n_zyklen=0, n_fuenftel=0, k_voll=K, n_theta=kv.N_THETA,
                               stoerung=False, aufzeichnung_ok=True, park_ok=True, fehlende_kanaele=[],
                               hash_rohdatei=None, version_stufe1='teil_b', kalibrier_hash=None, ebene='H'))
            for n in zf.DATENFELDER:
                daten[n].append(leer[n])
            daten['Nk_zellen'][-1] = e[r]
            daten['Nk_summe'][-1] = e[r].sum(0)
    tb = zf.LaufTabelle(koepfe, {n: np.stack(v) for n, v in daten.items()})
    return zf.LaufTabelle(tb.koepfe + t1.koepfe, {n: np.concatenate([tb.daten[n], t1.daten[n]]) for n in
                                                  zf.DATENFELDER})


def _zuordnung(e2, t1, d, lauf, kontroll, auswertbar, tb, T0, T1, schnitt, c, idx, B0, kmax, prof, Nbar0, Nbar1):
    """Residuen an den Punkten I bei beiden Einstellungen und die Zuordnung (kontrollen.zuordnung)."""
    pI = e2['punkte_I']
    E0s = [np.asarray(x['Nk_zellen']) for x in (tb['nr3'].get('einzel0_strich') or [])]
    E1s = [d['Nk_zellen'][kontroll[(2, j)]] for j in (1, 2, 3)]
    if len(E0s) != 3 or any(e.shape[0] < 2 for e in E0s) or any(e.shape[0] < 2 for e in E1s):
        return dict(ergebnis='nicht durchgeführt', grund='Einzelmodulläufe bei Einstellung 2 fehlen')
    N0s, N1s = np.stack([e.mean(0) for e in E0s]), np.stack([e.mean(0) for e in E1s])
    idxB0s = [B0[f"B0′/modul{j}"] for j in (1, 2, 3)]
    idxB1s = [idx[f"B1′/modul{j}"] for j in (1, 2, 3)]
    paare = {'yhat0': dict(r=[], u=[], r2=[], u2=[]), 'yhat1': dict(r=[], u=[], r2=[], u2=[])}
    ausgeloest = False
    fehlend = []
    for p in pI:
        i = schnitt.index(f'S{p:g}')
        kid2 = zf.konfig_id('K', (0.0, p, kv.SCHNITT_PHI3), einstellung=2, gruppe='identifizierbarkeit')
        ii = lauf.get(kid2, [])
        if f'S{p:g}' not in auswertbar or len(ii) < 2:
            fehlend.append(p)
            continue
        X, Z, nz = d['Nk_zellen'][ii], d['zeiger'][ii], t1.spalte('n_zyklen', int)[ii]
        rho = vh.zeiger_mittel(Z, nz)
        y = bs._q4(X.mean(0), kmax)[0]
        v = bs.h1_varianzen(X, Z, nz, N0s, N1s, E0s, E1s, idx[f'A/{kid2}'], idxB0s, idxB1s, rho, kmax)
        for key, T, Nb in (('yhat0', T0, N0s), ('yhat1', T1, N1s)):
            yh = bs._q4(vh.vorhersage(Nb, rho, zellen=True), kmax)[0]
            vv = v['varA0' if key == 'yhat0' else 'varA1'][0] + v['varB0' if key == 'yhat0' else 'varB1'][0]
            paare[key]['r'].append(T['r'][i, 1:])
            paare[key]['u'].append(T['u'][i, 1:])
            paare[key]['r2'].append((y - yh)[1:])
            paare[key]['u2'].append(np.sqrt(vv[1:]))
        if c is not None:
            z0, z1 = T0['z'][i], T1['z'][i]
            if np.any((np.abs(z0) > c) & (np.abs(z1) > c) & (np.sign(z0) == np.sign(z1))):
                ausgeloest = True
    if fehlend:
        return dict(ergebnis='nicht durchgeführt', grund=f'Punkte I nicht auswertbar: {fehlend}')
    s0 = kontrollen.kraftskala(Nbar0.sum(1), N0s.sum(1))
    s1 = kontrollen.kraftskala(Nbar1.sum(1), N1s.sum(1))
    for key, s in (('yhat0', s0), ('yhat1', s1)):
        paare[key] = {k: np.array(v) for k, v in paare[key].items()}
        paare[key]['s'] = s
    out = kontrollen.zuordnung(paare, ausgeloest, prof, len(pI))
    out['punkte_I'] = list(pI)
    return out


def auswerten_manifest(manifest, kalibrierung, teil_b, regeln, seed=None):
    """Stufe 1 + 2 (End-zu-End): Rohdateien des Manifests (SHA-256 geprüft) → Ergebnis."""
    kal = kalibrierung if isinstance(kalibrierung, dict) else anpassung.lies_kalibrierung(kalibrierung)[1]
    tb = teil_b if isinstance(teil_b, dict) else formate.lies_objekt(teil_b, 'teil_b')[1]
    tab = stufe1.manifest_auswerten(manifest, kal, tb)
    return auswerten(tab, kal, tb, regeln, seed=seed)


def schreibe_ergebnis(pfad, erg, kennung):
    return formate.schreibe_objekt(pfad, formate.kopf('ergebnis', kennung, version=VERSION), erg)


def lies_ergebnis(pfad):
    return formate.lies_objekt(pfad, 'ergebnis')
