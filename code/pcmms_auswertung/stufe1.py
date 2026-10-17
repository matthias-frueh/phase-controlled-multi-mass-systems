"""AP-12 Stufe 1 (Werkzeug 6): Rohdaten → Laufzusammenfassung nach Präreg A9.4 Schritte 1–6, für alle Laufarten
identisch.

(1) Umrechnung je Zelle mit der statischen Kalibrierung (Nullpunkt, Empfindlichkeit; Regel verarbeitung.kennlinie),
    N = N₁ + N₂ + N₃. (2) Keine Softwarefilter. (3) Segmentierung am Indeximpuls des Bezugsmoduls (Modul 1 in
    Kombinationsläufen, Modul j in Lⱼ; Referenzläufe: virtueller Takt f_soll ab Fensterbeginn); Fensterbeginn
    t_rampe_ende + t_e (halber Zeitgebertakt Toleranz), die ersten n_zyklen_fenster Zyklen; nur vollständige,
    regelmäßige Zyklen (Periode im Bereich 0,5…1,5·T); eine fehlende oder überzählige Flanke zählt als Indexfehler,
    der betroffene Zyklus geht nicht ein. (4) Lineares Resampling jedes Zyklus auf N_θ = 2000 Stützstellen.
    (5) Mittelkurve je Lauf, DFT, Harmonische bis k_voll (die Bandbegrenzung auf k_max erfolgt in Stufe 2).
    (6) ⟨N⟩, Zellgrößen, Indexphasen der übrigen Module je Zyklus (φⱼ,c = 360°·(tⱼ − t₁)/T_c), Zeiger
    Σ_c e^{−ikφⱼ,c}, zirkuläres Mittel und Jitter, Fünftel, Rohextrema des ganzen Laufs aus den kalibrierten
    Rohwerten (einschließlich Rampe und Einschwingzeit, nicht aus der bandbegrenzten Kurve), Streuung der Rohwerte
    im Fenster, Übersteuerung, Temperaturen, Einregelzeit der Phasen (Regel verarbeitung.t_phi).
Fehlende Pflichtkanäle werden gemeldet und nicht ergänzt; abhängige Felder bleiben nan.

⟨N⟩ ist das Zeitmittel (A1) über die akzeptierten vollständigen Zyklusintervalle [aᵢ, bᵢ] aus den kalibrierten
Rohwerten und ihren Zeiten: N_mittel,c = Σᵢ ∫ F_c dt / Σᵢ (bᵢ − aᵢ), integriert über den linear interpolierten
Verlauf wie im Resampling (Grenzen zwischen Abtastwerten mit interpoliertem Wert); verworfene Zyklen und Lücken gehen
weder in Zähler noch Nenner ein. Für die Fünftel gilt dasselbe über die ersten bzw. letzten ⌊N_z/5⌋ akzeptierten
Zyklen. Die phasensynchrone Mittelkurve (Zyklen gleich gewichtet) und ihre Harmonischen bleiben davon getrennt.
Bis stufe1-0.1 war ⟨N⟩ der Gleichanteil dieser Mittelkurve (Phasenmittel), bei ungleichen Periodendauern eine andere
Größe; die Version steht in jeder Laufzusammenfassung (version_stufe1, zusammenfassung.MITTEL_BEDEUTUNG).
"""
import numpy as np

from . import formate, konventionen as kv, rohdaten, zusammenfassung as zf

VERSION = 'stufe1-0.2'


def zeitintegrale(t, F, grenzen):
    """∫_a^b F_c(t) dt des linear interpolierten Verlaufs (wie np.interp im Resampling, außerhalb [t₀, t_ende]
    konstant fortgesetzt) je Intervall [a, b) und Zelle. Rückgabe (Intervalle, Zellen) und die Dauern b − a."""
    a = np.array([g[0] for g in grenzen], float)
    b = np.array([g[1] for g in grenzen], float)
    dt = np.diff(t)
    C = np.concatenate([np.zeros((F.shape[0], 1)), np.cumsum(0.5 * (F[:, 1:] + F[:, :-1]) * dt, axis=1)], axis=1)

    def stamm(x):
        j = np.clip(np.searchsorted(t, x, side='right') - 1, 0, t.size - 2)
        u = np.clip(x, t[0], t[-1]) - t[j]
        Fx = F[:, j] + (F[:, j + 1] - F[:, j]) * (u / dt[j])
        return (C[:, j] + 0.5 * (F[:, j] + Fx) * u + F[:, [0]] * np.minimum(x - t[0], 0.0)
                + F[:, [-1]] * np.maximum(x - t[-1], 0.0))
    return (stamm(b) - stamm(a)).T, b - a


def _kal_zellen(kal):
    z = kal['zellen']
    if any(c.get('umrechnung', 'linear') != 'linear' for c in z):
        raise formate.FormatFehler('Stufe 1: nur lineare Umrechnung implementiert (Regel verarbeitung.kennlinie)')
    return (np.array([c['nullpunkt_adc'] for c in z], float), np.array([c['empfindlichkeit_N_je_adc'] for c in z],
                                                                       float))


def _zyklusphasen(idx_j, a, b):
    """Index von Modul j im Zyklus [a, b): Phase in Grad, nan wenn kein oder mehr als ein Impuls."""
    sel = idx_j[(idx_j >= a) & (idx_j < b)]
    if sel.size != 1:
        return np.nan, sel.size
    return 360.0 * (sel[0] - a) / (b - a), 1


def _t_phi(phasen, starts, t_rampe, s_j):
    """Einregelzeit: erster Zyklus nach Rampenende, ab dem alle Phasen innerhalb max(4σ, 0,1°) um das Mittel des
    Fensters liegen (Regel verarbeitung.t_phi); phasen über alle Zyklen ab Rampenende, Fenstermittel s_j."""
    ok = np.isfinite(phasen)
    if not ok.any() or not np.isfinite(s_j[0]):
        return np.nan
    tol = max(4 * s_j[1], 0.1)
    ab = np.abs(kv.wickel_grad(phasen - s_j[0])) <= tol
    ab[~ok] = False
    # erster Index, ab dem alle folgenden innerhalb liegen
    schlecht = np.flatnonzero(~ab)
    i0 = 0 if schlecht.size == 0 else schlecht[-1] + 1
    if i0 >= len(starts):
        return np.nan
    return float(max(starts[i0] - t_rampe, 0.0))


def laufzusammenfassung(laufdatei, kalibrierung, teil_b=None, k_voll=None, profil=None):
    """Laufzusammenfassung eines Rohlaufs (Pfad ohne Endung). kalibrierung: Inhalt (dict) oder Pfad;
    k_voll: Zahl der gespeicherten Harmonischen (Vorgabe: Teil B nr2.k_voll, sonst Regel verarbeitung.k_voll)."""
    if isinstance(kalibrierung, str):
        _, kalibrierung = formate.lies_objekt(kalibrierung, 'kalibrierung')
    if k_voll is None:
        k_voll = (teil_b or {}).get('nr2', {}).get('k_voll')
    if k_voll is None:
        from . import regeln
        k_voll = (profil or regeln.profil()).wert('verarbeitung.k_voll')
    k_voll = int(k_voll)
    kopf_datei, inhalt, daten = rohdaten.lies_rohlauf(laufdatei)
    L, E, P = inhalt['lauf'], inhalt['erfassung'], inhalt['protokoll']
    art = L['laufart']
    f_soll, fs, t0 = float(E['f_soll']), float(E['f_s']), float(E['t0'])
    T = 1.0 / f_soll
    fehlend = [c for c in rohdaten.PFLICHTKANAELE if c not in daten]
    bew = {'K': [1, 2, 3], 'L': [L['modul']], 'D1': [], 'D2': [], 'R': []}[art]
    ref = 1 if art == 'K' else (L['modul'] if art == 'L' else None)
    fehlend += [f'index_modul{j}' for j in bew if f'index_modul{j}' not in daten]
    out = zf.leere_daten(k_voll)
    n_zyklen = 0
    t_ende = L.get('t_ende')
    if 'kraft_adc' in daten:
        adc = np.asarray(daten['kraft_adc'], float)
        n0, s = _kal_zellen(kalibrierung)
        F = (adc - n0[:, None]) * s[:, None]
        t = t0 + np.arange(F.shape[1]) / fs
        if t_ende is None:
            t_ende = L['t_start'] + float(t[-1])
        voll = E['adc']['vollausschlag']
        uebersteuert = (np.abs(daten['kraft_adc']) >= voll).any(1)
        if 'uebersteuerung' in daten:
            uebersteuert |= np.asarray(daten['uebersteuerung'], bool)
        out['uebersteuert_zellen'] = uebersteuert
        out['min_roh_zellen'], out['max_roh_zellen'] = F.min(1), F.max(1)
        ts = P['t_rampe_ende'] + P['t_e']
        Nz = int(P['n_zyklen_fenster'])
        tol = 0.5 / E.get('f_takt', 1e6)
        idx_fehler = np.zeros(3, np.int64)
        if ref is not None and f'index_modul{ref}' in daten:
            idx = np.asarray(daten[f'index_modul{ref}'], float)
            sel = idx[idx >= ts - tol]
            grenzen = []
            gezaehlt, i = 0, 0
            while gezaehlt < Nz and i + 1 < sel.size:
                per = sel[i + 1] - sel[i]
                if per < 0.5 * T:                                        # überzählige Flanke
                    idx_fehler[ref - 1] += 1
                    sel = np.delete(sel, i + 1)
                    continue
                if per > 1.5 * T:                                        # fehlende Flanke(n): Zyklen fallen aus
                    m = int(round(per / T))
                    idx_fehler[ref - 1] += m - 1
                    gezaehlt += m
                else:
                    grenzen.append((sel[i], sel[i + 1]))
                    gezaehlt += 1
                i += 1
        elif ref is None:
            grenzen = [(ts + c * T, ts + (c + 1) * T) for c in range(Nz)]
        else:
            grenzen = []
        grenzen = [g for g in grenzen if g[1] <= t[-1]]
        # Phasen der übrigen Module je Zyklus
        andere = [j for j in bew if j != ref and f'index_modul{j}' in daten]
        phi = {j: np.zeros(len(grenzen)) for j in bew}
        gut = np.ones(len(grenzen), bool)
        for j in andere:
            idx_j = np.asarray(daten[f'index_modul{j}'], float)
            for c, (a, b) in enumerate(grenzen):
                p, anz = _zyklusphasen(idx_j, a, b)
                if anz != 1:
                    idx_fehler[j - 1] += abs(anz - 1)
                    gut[c] = False
                phi[j][c] = p
        grenzen = [g for g, ok in zip(grenzen, gut) if ok]
        for j in andere:
            phi[j] = phi[j][gut]
        n_zyklen = len(grenzen)
        out['index_fehler'] = idx_fehler
        if n_zyklen >= 1:
            th = np.arange(kv.N_THETA) / kv.N_THETA
            kurven = np.empty((n_zyklen, 3, kv.N_THETA))
            for c, (a, b) in enumerate(grenzen):
                tt = a + th * (b - a)
                for z in range(3):
                    kurven[c, z] = np.interp(tt, t, F[z])
            mittel = kurven.mean(0)
            Nkz = kv.harmonische(mittel, k_voll)
            out['Nk_zellen'] = Nkz
            out['Nk_summe'] = Nkz.sum(0)
            I, dauer = zeitintegrale(t, F, grenzen)                     # Zeitmittel ⟨N⟩ (A1), nicht Phasenmittel
            out['N_mittel_zellen'] = I.sum(0) / dauer.sum()
            out['N_mittel'] = float(out['N_mittel_zellen'].sum())
            nf = n_zyklen // 5
            if nf >= 1:
                for q, sl in ((0, slice(0, nf)), (1, slice(n_zyklen - nf, n_zyklen))):
                    m = kurven[sl].mean(0)
                    out['fuenftel_Nk'][q] = kv.harmonische(m, k_voll).sum(0)
                    out['fuenftel_N_mittel'][q] = float(I[sl].sum() / dauer[sl].sum())
            w = (t >= grenzen[0][0]) & (t < grenzen[-1][1])
            out['sigma_roh_zellen'] = F[:, w].std(1, ddof=1)
            out['sigma_roh_summe'] = float(F[:, w].sum(0).std(ddof=1))
            k = np.arange(1, k_voll + 1)
            zeiger = np.full((3, k_voll), np.nan + 1j * np.nan)
            pm, sg, tphi = np.full(3, np.nan), np.full(3, np.nan), np.full(3, np.nan)
            for j in bew:
                ph = phi[j]
                zeiger[j - 1] = np.exp(-1j * np.outer(np.radians(ph), k)).sum(0)
                pm[j - 1], sg[j - 1] = kv.zirkulaer_mittel_grad(ph)
            out['zeiger'], out['phi_mittel_grad'], out['sigma_grad'] = zeiger, pm, sg
            # Einregelzeit der Phasen (geregelte Module 2, 3 im Kombinationslauf)
            if art == 'K':
                idx1 = np.asarray(daten['index_modul1'], float)
                ab = idx1[(idx1 >= P['t_rampe_ende'] - tol) & (idx1 < grenzen[-1][1] + tol)]
                for j in andere:
                    idx_j = np.asarray(daten[f'index_modul{j}'], float)
                    ph_all = np.array([_zyklusphasen(idx_j, a, b)[0] for a, b in zip(ab[:-1], ab[1:])])
                    tphi[j - 1] = _t_phi(ph_all, ab[:-1], P['t_rampe_ende'], (pm[j - 1], sg[j - 1]))
            out['t_phi'] = tphi
        f_mittel = (1.0 / np.mean([b - a for a, b in grenzen])) if (grenzen and ref is not None) else f_soll
    else:
        f_mittel = f_soll
        if t_ende is None:
            t_ende = L['t_start']
    if 'temperatur_zellen' in daten:
        Tz = np.asarray(daten['temperatur_zellen'], float)
        out['temperatur_min_zellen'], out['temperatur_max_zellen'] = Tz.min(1), Tz.max(1)
    else:
        fehlend.append('temperatur_zellen')
    kopf = dict(lauf_id=L['lauf_id'], laufart=art, modul=L.get('modul'), einstellung=L['einstellung'],
                konfiguration=L['konfiguration'], phase=L['phase'], block=L.get('block'), messtag=L.get('messtag'),
                position=L['position'], kontrollsatz=L.get('kontrollsatz'), t_start=float(L['t_start']),
                t_ende=float(t_ende), f_soll=f_soll, f_mittel=float(f_mittel), n_zyklen=int(n_zyklen),
                n_fuenftel=int(n_zyklen // 5), k_voll=k_voll, n_theta=kv.N_THETA, stoerung=bool(P['stoerung']),
                aufzeichnung_ok=bool(P['aufzeichnung_ok']), park_ok=P.get('park_ok'), fehlende_kanaele=fehlend,
                hash_rohdatei=kopf_datei.get('daten', {}).get('sha256'), version_stufe1=VERSION,
                kalibrier_hash=formate.sha256_json(kalibrierung), ebene='Z')
    return zf.Laufzusammenfassung(kopf, out, meta={x: kopf_datei[x] for x in ('schema', 'datenart', 'kennung')})


def manifest_auswerten(manifest, kalibrierung, teil_b=None, k_voll=None, profil=None):
    """Alle Läufe eines Manifests (SHA-256 geprüft) → LaufTabelle."""
    k, zeilen, basis = rohdaten.lies_manifest(manifest)
    import os
    laeufe = [laufzusammenfassung(os.path.join(basis, z['lauf_id']), kalibrierung, teil_b, k_voll, profil)
              for z in zeilen]
    return zf.LaufTabelle.aus_liste(laeufe, meta=dict(kennung=k['kennung'], datenart=k['datenart']))
