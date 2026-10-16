"""AP-12: knappe Textfassung eines Ergebnisses (Ausgänge, Gründe, Zusätze, Grenzwerte und Herkunft). Die
maschinenlesbare Fassung ist das Ergebnis-Objekt selbst; diese Zeilen fassen es nur zusammen."""


def _ausgang(h):
    if h is None:
        return 'nicht ausgewertet'
    s = h.get('ausgang', '–')
    if h.get('grund'):
        s += f' (Grund: {h["grund"]})'
    if h.get('zusaetze'):
        s += '; ' + '; '.join(h['zusaetze'])
    return s


def text(erg):
    hk = erg['herkunft']
    z = [f'Ergebnis {hk.get("kennung")} – synthetisch, keine Registrierung',
         f'Profil {hk["profil"]["profil_id"]} (SHA-256 {hk["profil"]["sha256"][:12]}…), Seed {hk["seed"]}, '
         f'B = {hk["B"]}, H3-MC = {hk["n_mc_h3"]}' + (' – REDUZIERT (Entwicklungsdiagnostik)' if hk['reduziert']
                                                    else ''),
         *([f'Pilotskript: {hk["pilot_suche"]["ergebnis"]} ({hk["pilot_suche"].get("grund")}); Teil B mit den '
            'Planwerten der synthetischen Kampagne (Stressprüfung, keine zulässige Planung)']
           if (hk.get('pilot_suche') or {}).get('ergebnis', '').startswith('kein zulässiger') else []),
         *([f'Laufzusammenfassungen mit ⟨N⟩ in alter Bedeutung (Phasenmittel, vor Korrektur B): '
            f'{", ".join(hk["verarbeitung"]["alte_bedeutung"])} – nicht neu berechnet']
           if (hk.get('verarbeitung') or {}).get('alte_bedeutung') else []),
         f'Läufe Phase 1: {erg["gueltigkeit"]["n_laeufe"]}, ungültig {erg["gueltigkeit"]["n_ungueltig"]}; '
         f'auswertbare Konfigurationen {erg["n_auswertbar"]}; ŷ¹ gültig: {erg["yhat1_gueltig"]}',
         f'H1: {_ausgang(erg["H1"])}; max|z⁰| = {erg["H1"].get("max_abs_z0")}; c = {erg["H1"].get("c")} '
         f'({erg["H1"].get("c_herkunft")})']
    for name, s in erg.get('H1_sensitivitaet', {}).items():
        z.append(f'  Sensitivität {name}: {_ausgang(s)} (ohne Wirkung auf den Ausgang)')
    z.append(f'H1Z: {_ausgang(erg["H1Z"])}')
    h2 = erg['H2']
    z.append(f'H2: {_ausgang(h2)}' + (f'; Δφ*⁰ = {h2["delta_phi0"]:.3f}°, Δφ*¹ = {h2["delta_phi1"]:.3f}°, Intervall '
                                     f'{h2.get("intervall_gewaehlt")}' if 'delta_phi0' in h2 else ''))
    z.append(f'H3: {_ausgang(erg["H3"])}' + (f' – {erg["H3"]["kennzeichnung"]}' if 'kennzeichnung' in erg['H3']
                                            else ''))
    z.append(f'H4: {_ausgang(erg["H4"])}')
    h0 = erg['H0']
    if h0.get('pruefbar'):
        z.append(f'Nullkontrolle: Differenz {h0["differenz"]:.3g} N, 95 % [{h0["intervall"][0]:.3g}, '
                 f'{h0["intervall"][1]:.3g}] N, {h0["lage"]} ({h0["vermerk"]}); {h0["aussage"]}')
    zu = erg.get('zuordnung')
    if zu:
        z.append(f'Zuordnung: {zu.get("ergebnis", zu.get("status", "–"))}')
    e3 = erg.get('E3')
    if e3:
        z.append(f'E3: {e3.get("bewertung") or e3.get("status", "–")}')
    ab = erg['gueltigkeit']['abbruch']
    if ab['S2'] or ab['S4']:
        z.append(f'Abbruchregeln (offline): S2 {ab["S2"]}, S4 {ab["S4"]}; Phase 1 beendet: {ab["S2_phase_beendet"]}')
    z.append(f'Offene Regeln: {len(erg["offene_regeln"])}; nicht implementiert: {len(erg["nicht_implementiert"])}')
    return '\n'.join(z)
