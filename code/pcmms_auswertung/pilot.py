"""Werkzeug 5 (AP-11): Pilotskript nach Präreg §5.4, §8.8, A9.2 und A9.8.

Das Skript gibt nur Pilotgrößen aus: Streuungen je Pilotkonfiguration, gepoolte s_q mit ν_p und oberer
80-%-Vertrauensgrenze, σ_tol, σ_Δ je Laufart, σ̂_ref, σ̂_ref,c, σ_c, σ_Σ, F_LO, ε_ctrl mit Prüfgröße und kritischem
Wert (A9.8), T_φ, Rauschkovarianzen je Laufart, p̂, Rampen- und Einschwinginformation und den Stand der Suche nach
k_max, T_a, n_min und n₀ in der festen Reihenfolge von A9.2. Superpositionsresiduen der Piloten, Vorhersagen an den
Pilotkonfigurationen und Hypothesenentscheidungen werden weder berechnet noch gespeichert (§5.4).

Reihenfolge der Schwellen (A9.2): (1) G2–G10 auf die Phase-0-Läufe mit σ_tol und σ_Δ aus allen Läufen der
jeweiligen Art, (2) ε_ctrl aus den danach gültigen Läufen, (3) G1; p̂ ist der Anteil der danach ungültigen
Pilotläufe; alle Streuungen stammen aus den gültigen Läufen.

Suche (A9.2): Für k = k_b, k_b − 1, …, 3 und je k für T_a = N_z/f mit N_z = 1, 2, …, solange T_e + T_a ≤ T_e,P + T_a,P:
(i) s_q(T_a) aus den auf die ersten N_z Zyklen gekürzten Pilotläufen, (ii) T_e = max(T_φ, 10·max τ_m) für die
Moden bis k·f, aufgerundet auf ganze Sekunden, und T_Lauf, (iii) Planungssimulation (AP-13; Haken `planung`),
(iv) Rauschbias (in der Planung), (v) n = n_min + r ≤ n_max. Das erste Paar, das (v) erfüllt, legt k_max, T_a, n_min
und n₀ fest; gibt es keines, lautet das Ergebnis regulär „kein zulässiger Arbeitspunkt unter diesen Annahmen“.
Ohne angebundene Planung liefert das Skript die vorbereitenden Größen und kennzeichnet die Planung als offen.
"""
import math

import numpy as np
from scipy import stats

from . import formate, gueltigkeit, konventionen as kv, zufall

VERSION = 'pilot-0.1'
VERBOTEN_TEIL = ('residu', 'yhat', 'vorhersage', 'superposition', 'bestaetigt', 'falsifiziert', 'entscheid', 'ausgang')
VERBOTEN_NAME = ('r', 'z', 'r0', 'r1', 'z0', 'z1', 'h1', 'h2', 'h3', 'h4', 'h1z')


def _rms(x):
    x = np.asarray(x, float)
    return float(np.sqrt(np.mean(x ** 2)))


def obere_grenze(s, nu, niveau=0.8):
    """Obere 80-%-Vertrauensgrenze einer Streuung s mit ν Freiheitsgraden: s·√(ν/χ²_{0,2}(ν)) (A9.2)."""
    return float(s * np.sqrt(nu / stats.chi2.ppf(1 - niveau, nu)))


def groessen_lauf(tab, k):
    """Je Lauf: F_min − ⟨N⟩ (k ≤ k), Re/Im N₁…N₃, γ₁ der Summe und dieselben H1-Größen je Zelle."""
    Ns = tab.daten['Nk_summe'][:, :k]
    Nz = tab.daten['Nk_zellen'][:, :, :k]
    return dict(summe=kv.h1_vektor(Ns), gamma1=kv.schiefe(Ns), zellen=kv.h1_vektor(Nz))


def streuungen(tab, maske, k):
    """s je Pilotkonfiguration, gepoolt (quadratisches Mittel) mit ν_p und oberer 80-%-Grenze."""
    ids = np.array(tab.konfig_ids())
    g = groessen_lauf(tab, k)
    je, nus = {}, []
    s_summe, s_gamma, s_zellen = [], [], []
    for kid in sorted(set(ids[maske])):
        m = maske & (ids == kid)
        n = int(m.sum())
        if n < 2:
            continue
        je[kid] = dict(n=n, s_summe=g['summe'][m].std(0, ddof=1).tolist(),
                       s_gamma1=float(np.std(g['gamma1'][m], ddof=1)),
                       s_zellen=g['zellen'][m].std(0, ddof=1).tolist())
        nus.append(n - 1)
        s_summe.append(g['summe'][m].std(0, ddof=1))
        s_gamma.append(np.std(g['gamma1'][m], ddof=1))
        s_zellen.append(g['zellen'][m].std(0, ddof=1))
    if not nus:
        return dict(je_konfiguration=je, nu_p=0, s_q=None, diagnose='keine Pilotkonfiguration mit ≥ 2 gültigen Läufen')
    nu = int(sum(nus))
    sq = np.sqrt(np.mean(np.array(s_summe) ** 2, 0))
    sz = np.sqrt(np.mean(np.array(s_zellen) ** 2, 0))
    sg = float(np.sqrt(np.mean(np.array(s_gamma) ** 2)))
    return dict(je_konfiguration=je, nu_p=nu, groessen=list(kv.GROESSEN_H1),
                s_q=dict(zip(kv.GROESSEN_H1, sq.tolist())), s_q_oben80=dict(zip(kv.GROESSEN_H1, [
                    obere_grenze(x, nu) for x in sq])), s_gamma1=sg, s_gamma1_oben80=obere_grenze(sg, nu),
                s_q_zellen=sz.tolist(), s_q_zellen_oben80=[[obere_grenze(x, nu) for x in zeile] for zeile in sz])


def kovarianzen(tab, maske, K):
    """Rauschkovarianzen je Laufart der gültigen Läufe: Vektor (⟨N_c⟩, Re N_c,k, Im N_c,k; c = 1 … 3, k ≤ K) nach
    Abzug des Mittels je Konfiguration (Pilotläufe gepoolt, Einzelmodulläufe je Modul, Referenzläufe)."""
    d = tab.daten
    v = np.concatenate([d['N_mittel_zellen'], d['Nk_zellen'][:, :, :K].real.reshape(len(tab), -1),
                        d['Nk_zellen'][:, :, :K].imag.reshape(len(tab), -1)], 1)
    gr = np.array([gueltigkeit.g4_gruppe(k) for k in tab.koepfe])
    ids = np.array(tab.konfig_ids())
    out = {}
    for g in sorted(set(gr[maske])):
        m = maske & (gr == g)
        X = v[m].copy()
        for kid in set(ids[m]):
            mm = ids[m] == kid
            X[mm] -= X[mm].mean(0)
        dof = int(m.sum() - len(set(ids[m])))
        if dof < 1:
            continue
        out[str(g)] = dict(kovarianz=(X.T @ X) / dof, freiheitsgrade=dof,
                      ordnung='⟨N_c⟩ (3), Re N_c,k (3·K), Im N_c,k (3·K), c-major, k = 1 … K')
    return out


def eps_ctrl_test(tab, gueltig, sig_ref, n_sim, seed, faktor=3.0):
    """A9.8: d = Δ⟨N⟩·√(1,5/(1 + β² + (1 − β)²)) der gültigen Pilot- und Einzelmodulläufe, F = s_d²/σ̂_ref²,
    kritischer Wert = 95-%-Quantil von F in n_sim simulierten Datensätzen derselben Laufanordnung."""
    art = tab.spalte('laufart', object)
    ph = tab.spalte('phase', int)
    pos = tab.spalte('position', int)
    t = 0.5 * (tab.spalte('t_start', float) + tab.spalte('t_ende', float))
    sel = (ph == 0) & gueltig
    ref = np.flatnonzero(sel & (art == 'R'))
    ref = ref[np.argsort(pos[ref])]
    oth = np.flatnonzero(sel & (art != 'R'))
    # Laufanordnung: einschließende Referenzläufe und β je anderem Lauf
    pr = pos[ref]
    a_i, b_i, be = [], [], []
    for i in oth:
        j = np.searchsorted(pr, pos[i])
        if j == 0 or j == pr.size:
            continue
        a, b = ref[j - 1], ref[j]
        a_i.append(np.flatnonzero(ref == a)[0])
        b_i.append(np.flatnonzero(ref == b)[0])
        be.append((t[i] - t[a]) / (t[b] - t[a]))
    a_i, b_i, be = np.array(a_i), np.array(b_i), np.array(be)
    use = np.array([i for i in oth if 0 < np.searchsorted(pr, pos[i]) < pr.size])
    if use.size < 2 or ref.size < 3:
        return dict(pruefbar=False, diagnose='zu wenige gültige Läufe für den ε_ctrl-Test')
    norm = np.sqrt(1.5 / (1 + be ** 2 + (1 - be) ** 2))
    Nref, Noth = tab.daten['N_mittel'][ref], tab.daten['N_mittel'][use]
    d = (Noth - ((1 - be) * Nref[a_i] + be * Nref[b_i])) * norm
    s_d = float(d.std(ddof=1))
    if sig_ref <= 0:                                                     # rauschfreie Daten: Grenzfall
        return dict(pruefbar=False, F=None, kritisch=None, n_sim=0, s_d=s_d, n_laeufe=int(use.size),
                    betrieb_streut_staerker=bool(s_d > 0), sigma_betr=s_d if s_d > 0 else None,
                    eps_ctrl=float(faktor * s_d), quelle='3·σ̂_betr' if s_d > 0 else '3·σ̂_ref (= 0, rauschfrei)',
                    diagnose='σ̂_ref = 0 (rauschfreie Daten): F-Test nicht definiert')
    F = s_d ** 2 / sig_ref ** 2

    # Simulation: ⟨N⟩ normalverteilt, gleiche Streuung in allen Laufarten
    tr = t[ref]
    bref = (tr[1:-1] - tr[:-2]) / (tr[2:] - tr[:-2])
    rng = zufall.strom(seed, 'eps_ctrl')
    Fs = np.empty(n_sim)
    block = 2000
    for s0 in range(0, n_sim, block):
        m = min(block, n_sim - s0)
        R = rng.standard_normal((m, ref.size))
        O = rng.standard_normal((m, use.size))
        loo = R[:, 1:-1] - ((1 - bref) * R[:, :-2] + bref * R[:, 2:])
        dd = (O - ((1 - be) * R[:, a_i] + be * R[:, b_i])) * norm
        Fs[s0:s0 + m] = dd.var(1, ddof=1) / loo.var(1, ddof=1)
    krit = float(np.quantile(Fs, 0.95))
    groesser = bool(F > krit)
    return dict(pruefbar=True, F=float(F), kritisch=krit, n_sim=int(n_sim), s_d=s_d, n_laeufe=int(use.size),
                betrieb_streut_staerker=groesser, sigma_betr=s_d if groesser else None,
                eps_ctrl=float(faktor * (s_d if groesser else sig_ref)),
                quelle='3·σ̂_betr' if groesser else '3·σ̂_ref')


def einschwingzeit(T_phi, moden, kmax, f):
    """T_e = max(T_φ, 10·max_m τ_m), τ_m = 1/(2π·ζ_m·f_m) für alle Moden bis k_max·f, aufgerundet (§6)."""
    taus = [1 / (2 * np.pi * mo['zeta'] * mo['f_hz']) for mo in moden if mo['f_hz'] <= kmax * f]
    return float(math.ceil(max([T_phi] + [10 * x for x in taus]) - 1e-12)), taus


def n_max(T_lauf, p_hat, zeit):
    """Größtes n mit ((N_K + N_I + 8)·n + 18·d)·T_Lauf/(1 − p̂) ≤ T_verfügbar (§5.3 c)."""
    a = zeit['N_K'] + zeit.get('N_I', 0) + 8
    n = math.floor((zeit['T_verfuegbar'] * (1 - p_hat) / T_lauf - 18 * zeit['d']) / a)
    return max(n, 0)


def _validitaet(tab, sw0, kmax, profil, seed, n_sim):
    """Schritte (1)–(3) der Reihenfolge der Schwellen."""
    art = tab.spalte('laufart', object)
    sw = gueltigkeit.Schwellen(**{**sw0.__dict__, 'kmax': kmax})
    sw.sigma_delta = gueltigkeit.sigma_delta(tab, kmax)
    pr1 = gueltigkeit.pruefe(tab, sw, regeln=('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10'))
    g1 = pr1['gueltig']
    sr = gueltigkeit.sigma_ref(tab.auswahl(np.flatnonzero((art != 'R') | g1)))
    if sr['sigma_ref'] is None:
        return sw, pr1, sr, dict(pruefbar=False, diagnose='weniger als drei gültige Referenzläufe'), pr1
    eps = eps_ctrl_test(tab, g1, sr['sigma_ref'], n_sim, seed, profil.wert('h0.eps_faktor'))
    sw.eps_ctrl = eps.get('eps_ctrl')
    sw.sigma_ref, sw.sigma_ref_zellen = sr['sigma_ref'], sr['sigma_ref_zellen']
    pr = gueltigkeit.pruefe(tab, sw)
    return sw, pr1, sr, eps, pr


def pilot_auswerten(tab, kal, profil, f_soll, zeit=None, seed=0, planung=None, tabelle_fuer=None, N_z_raster=None,
                    kennung=None):
    """Pilotanalyse der Phase-0-Läufe bei f (LaufTabelle tab). kal: Kalibrierung (Δδ, Moden); zeit: dict mit T_park,
    T_ramp, T_ab, T_eP, T_aP, T_verfuegbar, d, N_K, N_I (Teil B; ohne Angabe bleibt n_max offen); planung: Haken der
    AP-13-Planungssimulation (k, N_z, Größen) → dict(n_min, n0, …) oder None; tabelle_fuer: N_z → LaufTabelle der auf
    die ersten N_z Zyklen gekürzten Phase-0-Läufe. N_z_raster: verringertes Raster (Reduktion, im Ergebnis
    gekennzeichnet)."""
    tab = tab.auswahl(tab.spalte('phase', int) == 0).sortiert()
    art = tab.spalte('laufart', object)
    grp = np.array([k['konfiguration']['gruppe'] for k in tab.koepfe])
    pil = (art == 'K') & (grp == 'pilot')
    if not pil.any():
        raise ValueError('keine Pilotläufe in der Tabelle')
    p05, p04 = kal['p0_5'], kal['p0_4']
    dd = np.asarray(p05['delta_delta_grad'], float)
    moden = p04['moden']
    f1 = p04['f_1_hz']
    f1_schranke = f1 is None
    if f1 is None:
        f1 = p04['band_hz'][1]
    k_b = int(math.floor(f1 / (2 * f_soll)))
    K_voll = int(tab.koepfe[0]['k_voll'])
    n_sim = profil.zahl('eps_ctrl_datensaetze')
    # σ_c, σ_Σ, F_LO aus den Referenzläufen; σ_tol aus allen Pilotläufen
    ref = art == 'R'
    sig_c = np.sqrt(np.mean(tab.daten['sigma_roh_zellen'][ref] ** 2, 0))
    sig_S = _rms(tab.daten['sigma_roh_summe'][ref])
    fak_lo = profil.wert('g6.faktor')
    F_LO = fak_lo * sig_c
    sig_tol = {j: float(profil.wert('g2.sigma_tol') * np.median(tab.daten['sigma_grad'][pil, j - 1])) for j in (2, 3)}
    sw0 = gueltigkeit.Schwellen(f_soll=f_soll, kmax=3, delta_phi_tol_grad=profil.wert('g2.delta_phi_tol_grad'),
                                sigma_tol_grad=sig_tol, F_LO_zellen=F_LO, delta_delta_grad=dd,
                                g4_faktor=profil.wert('g4.faktor'), alarm_faktor=profil.wert('h0.alarm_faktor'))
    out = dict(version=VERSION, f_soll=f_soll, k_voll=K_voll, f_1_hz=f1, f_1_untere_schranke=f1_schranke, k_b=k_b,
               sigma_c=sig_c.tolist(), sigma_summe=sig_S, F_LO_zellen=F_LO.tolist(), F_LO_summe=fak_lo * sig_S,
               sigma_tol_grad=sig_tol, profil=profil.kurz())
    # T_φ und Rampe
    tphi = tab.daten['t_phi'][pil]
    out['T_phi_s'] = float(np.nanmax(tphi)) if np.isfinite(tphi).any() else None
    k_start = min(k_b, K_voll)
    # Validität mit k = k_start (G4 mit F_min − ⟨N⟩ hängt von k ab; je k neu in der Suche). Ohne zulässiges k
    # (k_b < 3) werden die Pilotgrößen mit k = 3 bestimmt und die Suche endet regulär ohne Arbeitspunkt.
    k_val = max(k_start, 3)
    sw, pr1, sr, eps, pr = _validitaet(tab, sw0, k_val, profil, seed, n_sim)
    out['sigma_ref'] = dict(sigma_ref=sr['sigma_ref'], sigma_ref_zellen=sr['sigma_ref_zellen'], n=sr['n'],
                            werte=sr['werte'], mindestzahl=profil.wert('h0.referenzlaeufe_min'),
                            ausreichend=bool(sr['n'] >= profil.wert('h0.referenzlaeufe_min')))
    out['eps_ctrl'] = {k: v for k, v in eps.items()}
    out['sigma_delta'] = sw.sigma_delta
    g6p = [int(i) for i in np.flatnonzero(pil) if pr['regeln']['G6'][i] is True]
    out['rampe'] = dict(liftoff_pilotlaeufe=[tab.koepfe[i]['lauf_id'] for i in g6p], T_ramp_verdoppeln=bool(g6p),
                        hinweis='Liftoff im ganzen Lauf einschließlich Rampe (min_roh); Lage in Rampe oder Fenster '
                                'ist aus der Laufzusammenfassung nicht trennbar')
    gp = pr['gueltig']
    out['gueltigkeit'] = dict(n_laeufe=len(tab), n_ungueltig=int((~gp).sum()),
                              gruende={tab.koepfe[i]['lauf_id']: pr['gruende'][i] for i in np.flatnonzero(~gp)},
                              nicht_pruefbar={g: len(v) for g, v in pr['nicht_pruefbar'].items()},
                              regeln_angewandt='G2–G10, dann ε_ctrl, dann G1 (A9.2)')
    out['p_hat'] = float((~gp[pil]).mean())
    out['p_hat_hinweis'] = ('untere Schranke: ' + ', '.join(sorted(pr['nicht_pruefbar'])) + ' nicht prüfbar'
                            if pr['nicht_pruefbar'] else 'alle Regeln geprüft')
    out['kovarianzen'] = kovarianzen(tab, gp, k_val)
    out['streuungen_volles_fenster'] = streuungen(tab, gp & pil, k_val)
    out['k_pilotgroessen'] = k_val
    if k_start < 3:
        out['suche'] = dict(ergebnis='kein zulässiger Arbeitspunkt unter diesen Annahmen',
                            grund=f'k_b = {k_b} < 3 (f₁ = {f1:g} Hz, f = {f_soll:g} Hz)')
    else:
        out['suche'] = suche(tab, kal, profil, f_soll, k_start, out, zeit, planung, tabelle_fuer, N_z_raster, seed,
                             sw0, n_sim)
    out['kennung'] = kennung
    pruefe_ausgabe(out)
    return out


def suche(tab, kal, profil, f, k_start, basis, zeit, planung, tabelle_fuer, N_z_raster, seed, sw0, n_sim):
    """Die Abfolge der Suche nach k_max, T_a, n_min, n₀ (A9.2)."""
    moden = kal['p0_4']['moden']
    Nz_voll = int(tab.koepfe[0]['n_zyklen'])
    schritte = []
    if zeit is None:
        return dict(ergebnis='offen', grund='Zeitangaben (T_park, T_ramp, T_ab, T_e,P, T_a,P, T_verfügbar, d, N_K) '
                                            'fehlen: n_max nicht bestimmbar', schritte=schritte)
    T_phi = basis['T_phi_s'] or 0.0
    reduktion = None
    for k in range(k_start, 2, -1):
        T_e, taus = einschwingzeit(T_phi, moden, k, f)
        Nz_max = int(math.floor((zeit['T_eP'] + zeit['T_aP'] - T_e) * f + 1e-9))
        if tabelle_fuer is None:
            raster = [Nz_voll] if Nz_voll <= Nz_max else []
            reduktion = f'keine gekürzten Zusammenfassungen: nur N_z = {Nz_voll}'
        elif N_z_raster is not None:
            raster = [n for n in N_z_raster if n <= Nz_max]
            reduktion = f'N_z-Raster {list(N_z_raster)} statt 1, 2, … (Reduktion)'
        else:
            raster = list(range(1, Nz_max + 1))
        for Nz in raster:
            if tabelle_fuer is None or Nz == Nz_voll:
                t = tab
            else:
                t = tabelle_fuer(Nz)
                t = t.auswahl(t.spalte('phase', int) == 0).sortiert()
            sw, _, _, eps, pr = _validitaet(t, sw0, k, profil, seed, n_sim)
            art = t.spalte('laufart', object)
            grp = np.array([kk['konfiguration']['gruppe'] for kk in t.koepfe])
            pil = (art == 'K') & (grp == 'pilot')
            p_hat = float((~pr['gueltig'][pil]).mean())
            st = streuungen(t, pr['gueltig'] & pil, k)
            T_a = Nz / f
            T_lauf = zeit['T_park'] + zeit['T_ramp'] + T_e + T_a + zeit['T_ab']
            nmax = n_max(T_lauf, p_hat, zeit)
            schritt = dict(k=k, N_z=Nz, T_a=T_a, T_e=T_e, T_lauf=T_lauf, p_hat=p_hat, n_max=nmax,
                           s_q=st['s_q'], s_q_oben80=st['s_q_oben80'], nu_p=st['nu_p'])
            if planung is None:
                schritt['planung'] = 'offen: AP-13-Planungssimulation nicht angebunden'
                schritte.append(schritt)
                return dict(ergebnis='offen', grund='Planungssimulation (P(H1 und H2 bestätigt | exakt) ≥ 0,8) nicht '
                                                    'angebunden; nur vorbereitende Pilotgrößen', schritte=schritte,
                            reduktion=reduktion)
            pl = planung(dict(k=k, N_z=Nz, T_a=T_a, s_q=st, kovarianzen=kovarianzen(t, pr['gueltig'], k),
                              p_hat=p_hat, n_max=nmax, tabelle=t, gueltig=pr['gueltig'], kal=kal, f=f))
            schritt['planung'] = {kk: v for kk, v in pl.items() if kk not in ('details',)}
            schritte.append(schritt)
            if pl.get('n_min') is None:
                continue
            r = math.ceil(pl['n_min'] * p_hat / (1 - p_hat)) + profil.wert('planung.reserve')
            n = pl['n_min'] + r
            schritt.update(reserve_r=r, n=n, erfuellt=bool(n <= nmax))
            if n <= nmax:
                return dict(ergebnis='festgelegt', k_max=k, N_z=Nz, T_a=T_a, T_e=T_e, T_lauf=T_lauf,
                            n_min=pl['n_min'], n0=pl['n0'], reserve_r=r, n=n, n_max=nmax, p_hat=p_hat, schritte=schritte,
                            reduktion=reduktion, planung_quelle=pl.get('quelle'))
    return dict(ergebnis='kein zulässiger Arbeitspunkt unter diesen Annahmen',
                grund='kein Paar (k, T_a) erfüllt n = n_min + r ≤ n_max', schritte=schritte, reduktion=reduktion)


def pruefe_ausgabe(obj, pfad=''):
    """Die Pilotausgabe enthält keine Residuen-, Vorhersage- oder Entscheidungsfelder (§5.4)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl == 'profil':                                          # Regelprofil: Beschreibung, keine Daten
                continue
            if any(x in kl for x in VERBOTEN_TEIL) or str(k) in VERBOTEN_NAME:   # Namen exakt (Gruppe „R“ erlaubt)
                raise ValueError(f'Pilotausgabe: unzulässiges Feld {pfad}/{k}')
            pruefe_ausgabe(v, f'{pfad}/{k}')
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            pruefe_ausgabe(v, f'{pfad}/{i}')


def schreibe_pilot(pfad, out, kennung):
    pruefe_ausgabe(out)
    return formate.schreibe_objekt(pfad, formate.kopf('pilot', kennung, version=VERSION), out)


def lies_pilot(pfad):
    return formate.lies_objekt(pfad, 'pilot')
