"""AP-13-Kriterienmatrix (Plan AP-13 1.3; Präreg A9.11 einschließlich Zuordnung, H1Z und E3) mit Status je Kriterium.

Status:
  geprüft                         mit normativer Kampagnenzahl bewertet oder deterministisch vollständig geprüft
  nur probeweise gerechnet        mit weniger Kampagnen oder Replikaten bzw. mit Entwicklungsannahmen gerechnet
  fehlt                           Szenario oder Verfahren in dieser Stufe nicht umgesetzt oder nicht gerechnet
  fachlich offen                  das Kriterium selbst oder seine Lesart ist offen (§12)
  in diesem Modell nicht prüfbar  der Generator oder das Modell kann den Fall nicht darstellen

Es gibt keine Gesamtampel: Die Matrix zählt nur die Status. Ein Soll „erfüllt“ wird bei reduzierter Kampagnenzahl
nur als Punktschätzer mit MC-Fehler berichtet, nicht als Abnahme.
"""
from ..regeln import NORMATIVE_ZAHLEN

STATUS = ('geprüft', 'nur probeweise gerechnet', 'fehlt', 'fachlich offen', 'in diesem Modell nicht prüfbar')

KRITERIEN = [
    ('K01', 'P(H1 falsifiziert | exakte Superposition) ≤ 0,05 je Stufe, beide Betriebsarten', 'Plan 1.3; A9.11',
     ['N01-A4', 'N03-ungleich', 'N03-N3bindet', 'N04-laufart', 'N01-V1G0', 'N01-V1G60h']),
    ('K02', 'P(H1 falsifiziert | LTI-Artefakt oder Drift der Einzelmodulbasis) ≤ 0,05', 'Plan 1.3; A9.11',
     ['E04-kette', 'E07-verstaerkung', 'E07-basisdrift', 'I04-drift']),
    ('K03', 'P(H1 falsifiziert | größte wahre Abweichung < Δ_rel) ≤ 0,05', 'Plan 1.3; A9.11', ['A04-R1', 'A06-phase']),
    ('K04', 'P(H1 bestätigt | eine Größe genau an ±Δ_q) ≤ 0,05', 'Plan 1.3; A9.11',
     ['N05-F', 'N05-N2', 'N05-N3', 'A04-R2']),
    ('K05', 'P(H1 bestätigt | exakt) ≥ 0,8 bei geplanter Laufzahl', '§5.4; Plan 1.3', ['N01-A4']),
    ('K06', 'P(H1 bestätigt | exakt) nicht fallend mit der Präzision (L5 → L0)', 'Plan 1.3; A9.11', ['N01-A4']),
    ('K07', 'P(H1 falsifiziert | Kopplung mit Residuum ≥ 2·Δ_rel) ≥ 0,8', 'A9.11; Plan 1.3', ['A04-R4']),
    ('K08', '– entfallen (Prüfrate von c nur berichtet, K15)', 'Plan 1.3', []),
    ('K09', 'H2 entscheidbar bei u_c,erw 0,3–1 mN (Lesart offen)', 'A9.11; Plan 1.3', ['N01-A4']),
    ('K10', 'Überdeckung des gewählten H2-Intervalls ≥ 0,936, auch beim symmetrischen Zelt', '§8.6, A9.6, A9.11',
     ['N01-A4', 'H01-zelt']),
    ('K11', 'P(H3 bestätigt | Mismatch über PB3) ≤ 0,05', 'Plan 1.3', ['C03-GF5']),
    ('K12', 'Planung nach §5.4 (n_min, n₀) mit Startwert und dokumentiertem Rechenweg', '§5.4, A9.2', ['N01-A4']),
    ('K13', 'Rauschbias: nach Korrektur |E[r(F_min)] − b̂| ≤ 0,1·u_c,erw für ŷ⁰ und ŷ¹', '§5.4, A9.5; Plan K13',
     ['N01-A4']),
    ('K14', 'Quantil für ε_ctrl aus 10 000 simulierten Datensätzen (A9.8)', 'A9.8', ['N01-A4']),
    ('K15', 'Berichtsgrößen ohne Bedingung (Rate „nicht entscheidbar“ je Grund, Zusätze, H4, Prüfrate von c, '
            'Sensitivitäten)', 'A9.11', ['alle']),
    ('K16', 'S₃: gleiche Bilder (10⁻⁹ N, 10⁻⁶°), ungleiche Module: Vorhersage exakt, Bildvergleich weicht ab',
     'Plan 1.3', ['F01-S3', 'F03-S3ungleich']),
    ('K17', 'Vorzeichen-Inversionstest S = N₊ + N₋ − 2Mg', 'Plan 1.3 (Option)', []),
    ('K18', 'Zuordnung: Trefferquote ≥ 0,8 (0,1 % Kopplung p = 1; Kette ≥ 1 mN p = 2)', 'A9.11; Plan K18',
     ['I01-amplitude', 'I01-frequenz', 'I02-amplitude', 'I02-frequenz']),
    ('K19', 'Ebenen Z und H konsistent (u_c-Mediane 5 %, Raten 2 MC-SE)', 'Plan 2.3', ['N01-A4']),
    ('K20', 'Einfrieren von Katalog, Kriterien, Seeds und Prüfdatensatz vor Teil A', 'Plan 1.3', []),
    ('K21', 'P(H1 falsifiziert | Hertz-Kontakt mit Residuum ≥ 2·Δ_rel) ≥ 0,8', '§12 Nr. 8; A9.11', ['A07-hertz50']),
    ('H1Z', 'H1Z: P(falsifiziert | exakt oder LTI) ≤ 0,05; Bestätigung und Prüfrate von c berichtet', 'A9.11',
     ['N01-A4', 'E04-kette']),
    ('E3', 'E3: P(auffällig | exakt) ≤ 0,05 und P(unauffällig | exakt) ≥ 0,8; Raten bei 0,1°/0,3° Phasenversatz',
     'A9.11', ['N01-A4', 'N01-V1G0']),
    ('Zuordnung', 'Zuordnung (A9.11): Raten falscher Klasse und „nicht zuordenbar“, auch Hertz und lastabhängige '
                  'Kopplung', 'A9.11', ['I05-misch', 'I02-amplitude']),
]


def _rate(sz, schluessel):
    if sz is None:
        return None
    return sz.get('raten', {}).get(schluessel)


def _fmt(r):
    if r is None or r.get('rate') is None:
        return '—'
    return f'{r["rate"]:.3f} ± {r["mc_se"]:.3f} ({r["zaehler"]}/{r["nenner"]})'


def _alle_szen(ps):
    s = ps['schritte']
    out = {}
    for teil in ('szenarien_a4', 'szenarien_v1', 'eigene', 'k06'):
        out.update(s.get(teil) or {})
    return out


def bewerten(ps):
    """Kriterienmatrix aus der Zusammenfassung von harness.pruefstand (Liste von dict)."""
    s = ps['schritte']
    sz = _alle_szen(ps)
    st = ps['konfiguration']['stufe']
    kal = s.get('kalibrierung_a4')
    n_norm = NORMATIVE_ZAHLEN['kampagnen_pruefung']
    zeilen = []

    def zeile(kid, status, befund, grund=''):
        k = next(x for x in KRITERIEN if x[0] == kid)
        zeilen.append(dict(id=kid, kriterium=k[1], quelle=k[2], szenarien=k[3], status=status, befund=befund,
                           grund=grund))

    def raten_text(ids, schl):
        t = []
        for sid in ids:
            r = _rate(sz.get(f'{sid}/{st}'), schl)
            if r is not None:
                t.append(f'{sid}: {_fmt(r)}')
        return '; '.join(t)

    def probe_status(ids, schl):
        rs = [_rate(sz.get(f'{x}/{st}'), schl) for x in ids]
        rs = [r for r in rs if r is not None]
        if not rs:
            return 'fehlt', ''
        normativ = all(r['nenner'] >= n_norm for r in rs) and '+red(' not in ps['profil']
        return ('geprüft' if normativ else 'nur probeweise gerechnet'), ''

    # K01
    t = []
    if kal:
        t.append(f'N01-A4 (Prüfsimulation mit kalibriertem c): {_fmt(kal["raten_pruefung"].get("H1: falsifiziert"))}')
    t.append(raten_text(['N03-ungleich', 'N03-N3bindet', 'N04-laufart'], 'H1: falsifiziert'))
    zeile('K01', probe_status(['N03-ungleich', 'N03-N3bindet'], 'H1: falsifiziert')[0] if (kal or sz) else 'fehlt',
          '; '.join(x for x in t if x), 'nur Stufe ' + st + ' und Betriebsart „Raster“ mit Entwicklungsplan; '
          'V1-Systeme siehe Kalibrierung V1')
    zeile('K02', probe_status(['E04-kette', 'E07-verstaerkung', 'E07-basisdrift'], 'H1: falsifiziert')[0],
          raten_text(['E04-kette', 'E07-verstaerkung', 'E07-basisdrift', 'I04-drift'], 'H1: falsifiziert'),
          'E04-kette mit Testvorgabe für c (eigenes System)')
    zeile('K03', probe_status(['A04-R1', 'A06-phase'], 'H1: falsifiziert')[0],
          raten_text(['A04-R1', 'A06-phase'], 'H1: falsifiziert'))
    zeile('K04', probe_status(['N05-F', 'N05-N2', 'N05-N3', 'A04-R2'], 'H1: bestätigt')[0],
          raten_text(['N05-F', 'N05-N2', 'N05-N3', 'A04-R2'], 'H1: bestätigt'),
          'N05-N1 (Kopplung an N₁ genau an Δ_q) ist nicht konstruierbar (Befund Etappe 2)')
    zeile('K05', 'nur probeweise gerechnet' if kal else 'fehlt',
          f'P(H1 bestätigt | exakt) = {_fmt((kal or {}).get("raten_pruefung", {}).get("H1: bestätigt"))} '
          f'bei n = {ps["konfiguration"]["plan"]["n_bloecke"]}, n_min = {ps["konfiguration"]["n_min"]}',
          'Laufzahl nicht nach §5.4 geplant (Entwicklungsplan)')
    k06 = s.get('k06') or {}
    if k06:
        txt = '; '.join(f'{k.split("/")[1]}: {_fmt(v["raten"].get("H1: bestätigt"))}' for k, v in sorted(k06.items()))
        zeile('K06', 'nur probeweise gerechnet', txt, 'Stufen ' + ', '.join(sorted(x.split('/')[1] for x in k06)) +
              ' mit Testvorgabe (b̂ = 0, c_B); nicht alle Stufen L0–L5')
    else:
        zeile('K06', 'fehlt', '', 'Präzisionsreihe nicht gerechnet')
    zeile('K07', probe_status(['A04-R4'], 'H1: falsifiziert')[0], raten_text(['A04-R4'], 'H1: falsifiziert'))
    zeile('K08', 'fachlich offen', 'entfallen; Prüfrate von c steht unter K15', 'Plan 1.3 (K08 entfallen)')
    zeile('K09', 'fachlich offen',
          f'N01-A4 (Prüfsimulation): P(H2 bestätigt | exakt) = '
          f'{_fmt((kal or {}).get("raten_pruefung", {}).get("H2: bestätigt"))}',
          'Lesart „entscheidbar“ offen (Regel h2.lesart_entscheidbar)')
    t = []

    def ueb(name, h):
        u = h.get('ueberdeckung') or {}
        teile = [f'{k}: ŷ⁰ {_fmt(u[k]["yhat0"])}, ŷ¹ {_fmt(u[k]["yhat1"])}' for k in ('perzentil_0.95', 'bca_0.95')
                 if k in u]
        g = h.get('schluessel')
        if g and g not in ('perzentil_0.95', 'bca_0.95') and g in u:
            teile.append(f'{g}: ŷ⁰ {_fmt(u[g]["yhat0"])}, ŷ¹ {_fmt(u[g]["yhat1"])}')
        return f'{name}: ' + '; '.join(teile) + f' → gewählt {g or "keiner"}'
    if kal and kal['h2'].get('ueberdeckung'):
        t.append(ueb('N01-A4', kal['h2']))
    hz = sz.get(f'H01-zelt/{st}', {}).get('h2_ueberdeckung')
    if hz and hz.get('ueberdeckung'):
        t.append(ueb('H01-zelt (symmetrisches Zelt)', hz))
    zeile('K10', 'nur probeweise gerechnet' if t else 'fehlt', '; '.join(t),
          'Bezugswert der Überdeckung offen (§12); Entwicklungsprüffall „Schätzer an den rauschfreien Kurven“; '
          'Fenstervarianten w = 8° nicht gerechnet')
    zeile('K11', probe_status(['C03-GF5'], 'H3: bestätigt')[0], raten_text(['C03-GF5', 'C03-GF1', 'C04-steif'],
                                                                          'H3: bestätigt'),
          'H3 Fassung K, δ_H3 = 10 % (Entwicklungsprüffall); C03 mit Testvorgabe für c')
    pl = s.get('planung')
    zeile('K12', 'nur probeweise gerechnet' if pl else 'fehlt',
          '' if not pl else f'Suche: {pl["suche"].get("ergebnis")}; {len(pl["aufrufe"])} Aufrufe der Planung, '
                            f'Kandidaten n_min {ps["konfiguration"]["planung_kandidaten"]}',
          'Planungssimulation mit wenigen Kampagnen je Kandidat; Rauschmodell des Szenarios auf die obere '
          '80-%-Grenze skaliert; Startwert aus der Auslegungsgrenze nicht automatisch gesetzt')
    rb = (kal or {}).get('restbias')
    zeile('K13', 'nur probeweise gerechnet' if rb else 'fehlt',
          '' if not rb else '; '.join(f'{k}: max |E[r] − b̂|/u_c = {v["max_verhaeltnis"]:.3f} '
                                      f'(MC-Fehler {v["mc_se_verhaeltnis"]:.3f}, Soll ≤ 0,1)' for k, v in rb.items()),
          'u(b̂) nur aus dem MC-Fehler (eine Rauschvariante); Rauschmodellvarianten N04 nicht kombiniert')
    zeile('K14', 'nur probeweise gerechnet', f'A9.8-Simulation im Pilotskript; im Prüfstand mit '
          f'{ps["konfiguration"]["profil_reduktion"].get("eps_ctrl_datensaetze", 10000)} Datensätzen; '
          'ein Lauf mit 10 000 Datensätzen im normativen Einzellauf', 'Quantil je Kampagne, keine Ratenprüfung')
    zeile('K15', 'nur probeweise gerechnet' if sz else 'fehlt',
          'Raten „nicht entscheidbar“ je Grund, Zusätze, H4, Sensitivitäten und Prüfrate von c je Szenario in '
          'der Prüfstandsausgabe', '')
    s3 = s.get('s3')
    if s3:
        f1, f3 = s3.get('F01-S3', {}), s3.get('F03-S3ungleich', {})
        zeile('K16', 'geprüft' if (f1.get('bilder_gleich') and f1.get('vorhersage_exakt') and
                                   f3.get('vorhersage_exakt') and not f3.get('bilder_gleich')) else
              'nur probeweise gerechnet',
              f'F01: |N_k| {f1["maximum"]["betrag_N"]:.1e} N, γ₁ {f1["maximum"]["gamma1"]:.1e}, Phase '
              f'{f1["maximum"]["phase_grad"]:.1e}°, F_min − ⟨N⟩ {f1["maximum"]["F_min_rel_N"]:.1e} N '
              f'(Rasterschranke {max(p["F_min_rasterschranke_N"] for p in f1["punkte"]):.1e} N); F03: '
              f'Bildvergleich |N_k| {f3["maximum"]["betrag_N"]:.3f} N, Vorhersage {f3["maximum"]["vorhersage_N"]:.1e} N',
              'rauschfrei auf Ebene H; F_min nur bis auf die N_θ-Rasterschranke (Befund: 10⁻⁹ N für F_min nicht '
              'erreichbar, A1); Ebene Z und F02 (mit Rauschen) nicht gerechnet')
    else:
        zeile('K16', 'fehlt', '', 'S₃-Prüfung nicht gerechnet')
    zeile('K17', 'fehlt', '', 'Gruppe G (Vorzeichen-Inversionstest) nicht im Katalog; Antrieb offen (Plan 5.4)')
    zeile('K18', probe_status(['I01-amplitude', 'I02-amplitude'], 'Zuordnung: Klasse p = 1')[0]
          if sz.get(f'I01-amplitude/{st}') else 'fehlt',
          '; '.join(f'{x}: ' + ', '.join(f'{k.split(": ", 1)[1]} {_fmt(v)}' for k, v in
                                         sz[f'{x}/{st}']['raten'].items() if k.startswith('Zuordnung'))
                    for x in ('I01-amplitude', 'I01-frequenz', 'I02-amplitude', 'I02-frequenz') if f'{x}/{st}' in sz),
          'Zuordnungsregel und Kriterium offen (§12); Entwicklungsprüffall (a); I03 und I06 fehlen')
    eb = s.get('ebenen')
    if eb:
        rf, rv = eb['rauschfrei'], eb['verrauscht']
        rel = max(abs(v) for v in rv['u_c_relativ'].values())
        zeile('K19', 'nur probeweise gerechnet',
              f'rauschfrei gleich: {rf["gleich"]} (max |ΔN_k| {rf["abweichung"]["Nk_zellen"]:.1e} N); verrauscht '
              f'{rv["n"]} Kampagnen je Ebene: max |Δu_c|/u_c = {rel:.3f}',
              'nur N01-A4 auf einer Stufe; L0, L2, L4 nach Plan nicht gerechnet')
    else:
        zeile('K19', 'fehlt', '', 'Ebenenvergleich nicht gerechnet')
    zeile('K20', 'fachlich offen', 'Software-Prüfsatz gehasht (tests/fixtures/ap13_pruefsatz.json)',
          'Einfrieren von Teil A ist nicht Gegenstand dieser Stufe; kein Einfrieren, keine Registrierung')
    a07 = sz.get(f'A07-hertz50/{st}')
    if a07:
        kl = a07['wahrheit']['klasse']
        zeile('K21', 'nur probeweise gerechnet' if kl == 'R4' else 'in diesem Modell nicht prüfbar',
              f'A07-hertz50: Klasse {kl}, r_max/Δ_rel = {a07["wahrheit"]["r_max_rel"]:.2f}; '
              f'P(falsifiziert) = {_fmt(a07["raten"].get("H1: falsifiziert"))}',
              '' if kl == 'R4' else 'kein Punkt ≥ 2·Δ_rel im Kontaktast mit diesem Szenario; berichtet nach K15')
    else:
        zeile('K21', 'fehlt', '', 'A07 nicht gerechnet')
    zeile('H1Z', 'nur probeweise gerechnet' if kal else 'fehlt',
          f'N01-A4: P(H1Z falsifiziert) = {_fmt((kal or {}).get("raten_pruefung", {}).get("H1Z: falsifiziert"))}, '
          f'bestätigt {_fmt((kal or {}).get("raten_pruefung", {}).get("H1Z: bestätigt"))}; ' +
          raten_text(['E04-kette'], 'H1Z: falsifiziert'),
          'Grenzen von H1Z: Entwicklungsprüffall Δ_q/3; Prüfrate von c_H1Z nicht gesondert simuliert')
    from ..regeln import HISTORISCH
    e3_hist = ps['profil'].split('+')[0] in HISTORISCH
    e3_befund = ('; '.join(f'{x}: ' + ', '.join(f'{k.split(": ", 1)[1]} {_fmt(v)}' for k, v in
                                               sz[f'{x}/{st}']['raten'].items() if k.startswith('E3'))
                           for x in ('N03-ungleich', 'A06-phase') + (() if e3_hist else ('E3b-amp05', 'E3b-amp10'))
                           if f'{x}/{st}' in sz) +
                 ('' if not kal else '; N01-A4: ' + ', '.join(f'{k.split(": ", 1)[1]} {_fmt(v)}' for k, v in
                                                              kal['raten_pruefung'].items() if k.startswith('E3'))))
    if e3_hist:
        zeile('E3', 'fachlich offen', e3_befund,
              'Schwellen, Prüfmenge und Rückfall von E3 offen (§12); Phasenversatzszenarien 0,1°/0,3° fehlen')
    else:                               # Regelstand 2026-11: Regeln festgelegt, Kriterien nicht abgenommen
        zeile('E3', 'nur probeweise gerechnet' if e3_befund else 'fehlt', e3_befund,
              'Regelstand 2026-11: Option B mit Rückfall je Prüfgröße, m = 43 fest (e3.grenzen); Randgültigkeit nur '
              'auf Statistikebene (Quadratur unter Gauß-, Wishart- und Unabhängigkeitsannahmen); Kriterien von A9.11 '
              'nicht mit normativer Kampagnenzahl, Modellprüfung von E3b nicht ausgeführt (keine Kalibrierabnahme); '
              'Phasenversatzszenarien 0,1°/0,3° fehlen; Amplitudenänderung 0,5 %/1 % (E3b-amp05/-amp10) nur als '
              'Funktionsnachweis')
    zeile('Zuordnung', 'fachlich offen',
          '; '.join(f'{x}: ' + ', '.join(f'{k.split(": ", 1)[1]} {_fmt(v)}' for k, v in
                                         sz[f'{x}/{st}']['raten'].items() if k.startswith('Zuordnung'))
                    for x in ('I05-misch', 'I02-amplitude') if f'{x}/{st}' in sz),
          'Kriterium der Zuordnung offen (§12: feste Anker oder Zuordnungsgrenze); Hertz und lastabhängige '
          'Kopplung als Zuordnungsszenarien fehlen')
    return zeilen


def zaehlung(zeilen):
    z = {s: 0 for s in STATUS}
    for x in zeilen:
        z[x['status']] += 1
    return z


def markdown(zeilen, kopf=''):
    z = zaehlung(zeilen)
    t = [kopf, '', '| Nr. | Kriterium | Status | Befund (Rate ± MC-Fehler (Zähler/Nenner)) | Einschränkung |',
         '|---|---|---|---|---|']
    def zelle(v):
        return (v or '—').replace('|', '\\|')
    for x in zeilen:
        t.append(f'| {x["id"]} | {zelle(x["kriterium"])} | {x["status"]} | {zelle(x["befund"])} | {zelle(x["grund"])} |')
    t += ['', 'Zählung der Status: ' + ', '.join(f'{k}: {v}' for k, v in z.items()) + '.',
          '', 'Keine Gesamtampel: Die Prüffälle sind unvollständig und die Kampagnenzahlen reduziert; kein Kriterium '
              'gilt damit als abgenommen.']
    return '\n'.join(t) + '\n'
