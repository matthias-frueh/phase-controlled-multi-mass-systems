"""AP-12 Stufe 2: Nullkontrolle (§8.8, A9.8), Zuordnung (§8.10, A9.13) und Kontrolle E3 (§8.10, A2.7, A9.13).
Keine dieser Auswertungen ändert einen Ausgang oder schließt einen Lauf aus.

Nullkontrolle: Welch-Satterthwaite-t-Test von Δ⟨N⟩ aller Kombinationsläufe der Phase 1 (gültig bis auf G1) gegen
Δ⟨N⟩ der Referenzläufe der Phase 1 (leave-one-out), zweiseitig, α = 0,05; Differenz, 95-%-Intervall, Lage zu ±ε_ctrl
mit Vermerk und genau eine der beiden Aussagen (Regel h0.sammeltest); keine Gleichheitsaussage. Ist der Test nicht
definiert (beide Stichprobenvarianzen null: Welch-Satterthwaite 0/0) oder eine Rechengröße nicht endlich, lautet das
Ergebnis „nicht prüfbar“ mit Grund, Differenz und Stichprobenzahlen, ohne Testaussage und ohne Ersatzstreuung.

Zuordnung (Regeln zuordnung.*, offen; dreiwertig nur im Entwicklungsprofil): an den Punkten I für Re/Im N₁…N₃ die
Residuen r (Haupteinstellung) und r′ (Einstellung 2) gegen (ŷ⁰, ŷ⁰′) und (ŷ¹, ŷ¹′);
χ²_p = Σ (r′ − s^p·r)²/(u′² + s^{2p}·u²), p = 0, 1, 2, m = 6·N_I Terme, gegen das 95-%-Quantil von χ²(m); Klasse p,
wenn χ²_p darunter und die beiden anderen darüber, gegen beide Vorhersagepaare dieselbe. s = Σⱼ|N̄′₁⁽ʲ⁾|/Σⱼ|N̄₁⁽ʲ⁾|
aus den Einzelmodulläufen (Regel zuordnung.s_formel, technisch). Auslöser: an einem Punkt von I ein |z⁰| > c mit
gleichsinnigem |z¹| > c.

E3 (Regeln e3.*, offen; dreiwertig nur im Entwicklungsprofil): Modulzeiger Ĉₖ = T(kω)⁻¹·(N₁,ₖ, N₂,ₖ, N₃,ₖ)ᵀ mit
T_cj = g_c·G_F,c(kω)·w_cj·H(kω) (Statik der Dreipunktlagerung aus P0.1, Kette, 1 FG; Kippmoden vernachlässigt,
gültig für k·f weit unter der Kippmode). E3a: Δφⱼ^Z = (arg Ĉ₁,₁ − arg Ĉⱼ,₁) − φ̄ⱼ^P (j = 2, 3), daneben k = 2:
Δφⱼ^{Z,2} = wickel(arg Ĉ₁,₂ − arg Ĉⱼ,₂ − 2·φ̄ⱼ^P)/2 (erst auf Ebene der Harmonischen modulo 360°, dann halbiert; Werte
in (−90°, 90°], lokaler Bezug zur Encoder-Profilphase, aus k = 2 allein nur bis auf 180° bestimmt).
E3b: q_Z = |R₋₁ − R̂₋₁|/|R̂₊₁| am Triphasik-Punkt aus der ersten Harmonischen des Kippmoments
(M_x = Σ y_c·N_c,1, M_y = −Σ x_c·N_c,1; R₊₁ = (M_x + iM_y)/2, R₋₁ = (M̄_x + iM̄_y)/2). Unsicherheit aus Bootstrap A/B,
Ziehungen von Δδⱼ (je Modul eine), der Quantisierung der Zeitstempel (Rechteck) und aus der Unsicherheit von T
(A9.13): je Replikat ein Parametersatz (g, x, y aus P0.1, Kette je Zelle, f_n und ζ aus P0.4) für alle Konfigurationen
und beide Harmonischen; E3b zieht nur die Zelllagen, gemeinsam für Messung und Vorhersage. Ohne Beschreibung der
Unsicherheit von T (Teil B nr5) gibt es nur numerische Diagnostik, keine dreiwertige Aussage.
"""
import time

import numpy as np
from scipy import stats

from . import anpassung, bootstrap as bs, konventionen as kv, vorhersage as vh
from .regeln import RegelOffen


# ── Nullkontrolle ────────────────────────────────────────────────────────────────────────────────────
def nullkontrolle(dN_komb, dN_ref_loo, eps_ctrl, profil):
    x, y = np.asarray(dN_komb, float), np.asarray(dN_ref_loo, float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    basis = dict(n_komb=int(x.size), n_ref=int(y.size), eps_ctrl=eps_ctrl)
    def mittel(v):          # identische Werte: Mittel = Wert, Varianz null (nicht der Rundungsrest der Mittelbildung)
        return float(v[0]) if np.all(v == v[0]) else float(v.mean())

    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        if x.size and y.size:
            basis['differenz'] = mittel(x) - mittel(y)
        if x.size < 2 or y.size < 2:
            return dict(pruefbar=False, grund='zu wenige Kombinations- oder Referenzläufe', **basis)
        d = mittel(x) - mittel(y)
        vx, vy = (0.0 if np.all(v == v[0]) else v.var(ddof=1) / v.size for v in (x, y))
        if not (np.isfinite(d) and np.isfinite(vx) and np.isfinite(vy)):
            return dict(pruefbar=False, grund='nicht endliche Rechengröße (Mittel oder Varianz): Welch-Test nicht '
                                              'auswertbar, keine Testaussage', **basis)
        if vx + vy == 0.0:
            return dict(pruefbar=False, grund='Stichprobenvarianzen beider Gruppen null: Welch-Satterthwaite 0/0, '
                                              'Test nicht definiert; keine Testaussage und keine Gleichheitsaussage',
                        **basis)
        se = np.sqrt(vx + vy)
        nu = (vx + vy) ** 2 / (vx ** 2 / (x.size - 1) + vy ** 2 / (y.size - 1))
        regel = profil.wert('h0.sammeltest')
        t = stats.t.ppf(1 - regel['alpha'] / 2, nu) if np.isfinite(nu) and nu > 0 else np.nan
        L, U = d - t * se, d + t * se
    if not (np.isfinite(L) and np.isfinite(U)):
        return dict(pruefbar=False, grund=f'nicht endliches Intervall (ν = {float(nu):g}): Welch-Test nicht '
                                          'auswertbar, keine Testaussage', nu=float(nu), **basis)
    unterschied = bool(L > 0 or U < 0)
    return dict(pruefbar=True, differenz=float(d), intervall=[float(L), float(U)], nu=float(nu), n_komb=int(x.size),
                n_ref=int(y.size), eps_ctrl=eps_ctrl,
                lage=None if eps_ctrl is None else ('innerhalb ±ε_ctrl' if (L >= -eps_ctrl and U <= eps_ctrl) else
                                                    'nicht innerhalb ±ε_ctrl'),
                vermerk=regel['vermerk'], aussage=regel['aussagen'][0 if unterschied else 1])


# ── Zuordnung ────────────────────────────────────────────────────────────────────────────────────────
def kraftskala(N0, N2):
    """s = Σⱼ|N̄′₁⁽ʲ⁾|/Σⱼ|N̄₁⁽ʲ⁾| (Summenharmonische der Einzelmodulmittel, Modul × k)."""
    return float(np.abs(np.asarray(N2)[:, 0]).sum() / np.abs(np.asarray(N0)[:, 0]).sum())


def chi2_klassen(r, u, r2, u2, s):
    out = {}
    for p in (0, 1, 2):
        out[p] = float(np.sum((r2 - s ** p * r) ** 2 / (u2 ** 2 + s ** (2 * p) * u ** 2)))
    return out


def zuordnung(paare, ausgeloest, profil, N_I):
    """paare: dict 'yhat0'/'yhat1' → dict(r, u, r2, u2 (je (N_I, 6)), s); ausgeloest: Auslöser erfüllt (bool)."""
    m = 6 * N_I
    q95 = float(stats.chi2.ppf(0.95, m))
    werte = {k: dict(s=v['s'], chi2=chi2_klassen(np.ravel(v['r']), np.ravel(v['u']), np.ravel(v['r2']),
                                                  np.ravel(v['u2']), v['s'])) for k, v in paare.items()}
    out = dict(m=m, quantil95=q95, werte=werte, ausgeloest=bool(ausgeloest))
    try:
        profil.wert('zuordnung.regel')
        profil.wert('zuordnung.ausloeser')
        regel_ok = True
    except RegelOffen as e:
        regel_ok = False
        out['status'] = f'nur numerisch: {e.grund}'
    if not regel_ok:
        return out
    if not ausgeloest:
        out['ergebnis'] = 'keine Abweichung an den Punkten I nachgewiesen'
        out['hinweis'] = 'kein Nachweis, dass dort keine Abweichung besteht'
        return out
    klassen = {}
    for k, v in werte.items():
        unter = [p for p, x in v['chi2'].items() if x < q95]
        klassen[k] = unter[0] if len(unter) == 1 else None
    if klassen.get('yhat0') is not None and klassen.get('yhat0') == klassen.get('yhat1'):
        out['ergebnis'] = f'Klasse p = {klassen["yhat0"]}'
        out['klasse'] = klassen['yhat0']
    else:
        out['ergebnis'] = 'nicht zuordenbar'
        out['klasse'] = None
    out['klassen_je_paar'] = klassen
    out['status'] = 'Entwicklungsprofil (dreiwertig nur als Entwicklungsprüffall)'
    return out


# ── E3 ───────────────────────────────────────────────────────────────────────────────────────────────
T_MODELL = 'e3_T-0.2'                   # T_cj(kω) = g_c·G_F,c(kω)·w_cj·H(kω): Statik P0.1, Kette, 1 FG
T_FORMAT = 'e3_T_unsicherheit-0.1'      # Unsicherheitsbeschreibung von T in Teil B nr5 (A9.3 Nr. 5)
KOND_MAX = 1e12                         # T(kω) mit größerer Kondition gilt als singulär (wie beim Nennwert)
T_NAEHERUNGEN = (
    'Parameterziehungen normalverteilt mit den Kovarianzen der Anpassungen; je Replikat ein Parametersatz für alle '
    'Konfigurationen und beide Harmonischen',
    'getrennte Kalibriermessungen ohne Kreuzkovarianz im Format (P0.1-Laststellen, Brückenanpassung je Kanal, '
    'statistischer Anteil von P0.4) werden als unabhängig gezogen; ein gemeinsamer Fehler aller Kanäle (gleicher Faktor '
    'aller Zellen) hebt sich in den relativen Modulphasen auf, kanalweise verschiedene gemeinsame Ursachen deckt das '
    'nicht ab',
    'Kette → (f_n, ζ) linear über die Verschiebungen je Störrichtung der Kette aus P0.4 (Neuanpassung bei 1σ, '
    'kovarianz_kette = Σ d·dᵀ): gemeinsame Ziehung ohne Doppelzählung, gültig für kleine Kettenunsicherheiten',
    'Tiefpassparameter w der Kette wie in der H3-Fortpflanzung betragsgespiegelt (|w|); Anteil berichtet',
)


def zellanteile_aus_lagen(x, y, module_m):
    """Baryzentrische Anteile w_cj (Zelle, Modul) der Modullagen im Zelldreieck (wie anpassung.zellanteile)."""
    B = np.c_[np.ones(3), np.c_[x, y]]
    return np.array([np.linalg.solve(B.T, np.r_[1.0, mp]) for mp in np.asarray(module_m)]).T


def t_aus_parametern(g, x, y, module_m, kette_p, f_n, zeta, f_hz, ks=(1, 2)):
    """T(kω) (k, Zelle, Modul) aus einem Parametersatz: relative Zellverstärkungen g, Zelllagen x, y, Modullagen,
    Kettenparameter je Zelle (anpassung.gf_modell) und f_n, ζ der 1-FG-Übertragung."""
    ks = np.asarray(ks)
    w = zellanteile_aus_lagen(x, y, module_m)
    G = np.array([anpassung.gf_modell(p, ks * f_hz) for p in kette_p])     # (Zelle, k)
    H = anpassung.h1fg(ks * f_hz, f_n, zeta)
    return np.einsum('c,ck,cj,k->kcj', np.asarray(g, float), G, w, H)


def uebertragung(kal, f_hz, ks=(1, 2)):
    """T(kω) (k, Zelle, Modul) aus P0.1 (Zelllagen, relative Verstärkungen), Kette und 1-FG-Übertragung (Nennwert)."""
    p01, p04 = kal['p0_1'], kal['p0_4']
    if anpassung.zellanteile(p01) is None:
        return None
    ls, e = p01['laststellen'], p04['einfreiheitsgrad']
    return t_aus_parametern(ls['g'], ls['x_m'], ls['y_m'], p01['module_nominal_m'], [b['p'] for b in p01['bruecke']],
                            e['f_n_hz'], e['zeta'], f_hz, ks)


def t_beschreibung(kal, f_hz, ks=(1, 2)):
    """Unsicherheitsbeschreibung von T für Teil B nr5 aus der Kalibrierung (AP-11): Nennwerte und Kovarianzen von
    (g, x, y) aus P0.1, Kettenparameter je Zelle, (f_n, ζ) aus P0.4 mit statistischem Anteil und Verschiebungen je
    Störrichtung der Kette; nicht gezogene Eingänge, unvollständige Teile und Näherungen. None ohne T-Modell."""
    p01, p04 = kal['p0_1'], kal['p0_4']
    ls, e = p01['laststellen'], p04['einfreiheitsgrad']
    if not ls.get('bestimmbar') or p01.get('module_nominal_m') is None:
        return None
    h_gezogen = bool(e.get('identifizierbar'))
    unvollstaendig = []
    if h_gezogen and e.get('kette_richtungen') is None:
        unvollstaendig.append('P0.4 ohne Verschiebungen von (f_n, ζ) je Störrichtung der Kette (Kalibrierung vor '
                              'anpassung-0.2): f_n, ζ nicht ohne Doppelzählung der Kette ziehbar')
    nicht = ['Modullagen (Konstruktion, module_nominal_m) als bekannt angenommen wie in A2.7; keine Unsicherheit im '
             'Kalibrierformat',
             'Kippmoden: im T-Modell nicht enthalten (Modellgrenze, A2.7)']
    if not h_gezogen:
        nicht.append('f_n, ζ (P0.4 nicht identifizierbar): H(kω) nominal. H ist bei kω ein gemeinsamer komplexer Faktor '
                     'aller Zellen und Module und hebt sich in E3a (relative Modulphasen) exakt auf; E3b enthält T '
                     'nicht; die berichteten Amplituden |Ĉⱼ,₁| tragen keine H-Unsicherheit')
    return dict(format=T_FORMAT, modell=T_MODELL, f_hz=float(f_hz), ks=[int(k) for k in ks],
                gxy=dict(wert=np.r_[ls['g'], ls['x_m'], ls['y_m']].astype(float),
                         kovarianz=np.asarray(ls['kovarianz_g_x_y'], float),
                         ordnung='g₁ g₂ g₃ (relativ), x₁ x₂ x₃ [m], y₁ y₂ y₃ [m] (P0.1 Laststellen)'),
                kette=[dict(zelle=c + 1, modell=b['modell'], p=np.asarray(b['p'], float),
                            kovarianz=np.asarray(b['kovarianz'], float)) for c, b in enumerate(p01['bruecke'])],
                fn_zeta=dict(wert=np.array([e['f_n_hz'], e['zeta']], float), gezogen=h_gezogen,
                             kovarianz_statistisch=np.asarray(e['kovarianz_statistisch'], float),
                             kette_richtungen=e.get('kette_richtungen')),
                module_nominal_m=np.asarray(p01['module_nominal_m'], float),
                nicht_gezogen=nicht, unvollstaendig=unvollstaendig, naeherungen=list(T_NAEHERUNGEN))


def _faktor(C):
    """F mit F·Fᵀ = C für eine symmetrische positiv semidefinite Kovarianz (Eigenzerlegung; Nullkovarianz → 0)."""
    C = np.asarray(C, float)
    C = 0.5 * (C + C.T)
    lam, V = np.linalg.eigh(C)
    if lam.size and lam.min() < -1e-9 * max(float(np.abs(lam).max()), 1e-300):
        raise ValueError(f'Kovarianz nicht positiv semidefinit (kleinster Eigenwert {lam.min():.3g})')
    return V * np.sqrt(np.clip(lam, 0.0, None))


def t_ziehungen(beschr, rng, B):
    """B Ziehungen von T(kω) und den Zelllagen aus der Unsicherheitsbeschreibung (Teil B nr5), je Replikat ein
    Parametersatz für alle Konfigurationen und beide Harmonischen. Feste Reihenfolge der Zufallszahlen: (g, x, y),
    Kette je Zelle und Spalte (Cholesky wie P0.4), statistischer Anteil von (f_n, ζ). Unzulässige Ziehungen (g_c ≤ 0,
    f_n ≤ 0 oder ζ ≤ 0, Zelldreieck entartet, T nicht endlich oder Kondition > 10¹²) werden weder ersetzt noch
    ausgewählt, sondern gekennzeichnet; ihr Anteil steht im Ergebnis."""
    t0 = time.perf_counter()
    ks, f = beschr['ks'], float(beschr['f_hz'])
    unvollstaendig = list(beschr.get('unvollstaendig', []))
    th = np.asarray(beschr['gxy']['wert'], float)[None] + rng.standard_normal((B, 9)) @ _faktor(
        beschr['gxy']['kovarianz']).T
    kette = beschr['kette']
    P = np.repeat(np.stack([np.asarray(k['p'], float) for k in kette])[None], B, 0)        # (B, Zelle, 3)
    xi = []
    for c, idx, L in anpassung.kette_cholesky([dict(p=k['p'], kovarianz=k['kovarianz']) for k in kette]):
        if not idx:
            continue
        e = rng.standard_normal((B, len(idx)))
        P[:, c, idx] += e @ L.T
        xi += [((c, col), e[:, col]) for col in range(len(idx))]
    fz = beschr['fn_zeta']
    FZ = np.repeat(np.asarray(fz['wert'], float)[None], B, 0)
    if fz['gezogen'] and not unvollstaendig:
        rr = fz.get('kette_richtungen') or []
        if [(int(r['zelle']) - 1, int(r['spalte'])) for r in rr] != [k for k, _ in xi]:
            unvollstaendig.append('Störrichtungen der Kette in P0.4 passen nicht zur Brückenanpassung')
        else:
            for r, (_, e) in zip(rr, xi):
                FZ += e[:, None] * np.asarray(r['d_fn_zeta'], float)[None]
            FZ += rng.standard_normal((B, 2)) @ _faktor(fz['kovarianz_statistisch']).T
    gespiegelt = (P[:, :, 2] < 0).any(1)
    P[:, :, 2] = np.abs(P[:, :, 2])
    g, x, y = th[:, :3], th[:, 3:6], th[:, 6:9]
    gruende = {'g_c ≤ 0': (g <= 0).any(1), 'f_n ≤ 0 oder ζ ≤ 0': (FZ <= 0).any(1),
               'Zelldreieck entartet': np.zeros(B, bool), 'T nicht endlich': np.zeros(B, bool),
               'Kondition > 10¹²': np.zeros(B, bool)}
    T = np.full((B, len(ks), 3, 3), np.nan + 1j * np.nan)
    ok = ~(gruende['g_c ≤ 0'] | gruende['f_n ≤ 0 oder ζ ≤ 0'])
    mod = beschr['module_nominal_m']
    for b in np.flatnonzero(ok):
        try:
            T[b] = t_aus_parametern(g[b], x[b], y[b], mod, P[b], FZ[b, 0], FZ[b, 1], f, ks)
        except np.linalg.LinAlgError:
            gruende['Zelldreieck entartet'][b] = True
    fin = ok & ~gruende['Zelldreieck entartet'] & np.isfinite(T).all((1, 2, 3))
    gruende['T nicht endlich'] = ok & ~gruende['Zelldreieck entartet'] & ~fin
    kond = np.full(B, np.inf)
    if fin.any():
        kond[fin] = np.linalg.cond(T[fin]).max(-1)
    gruende['Kondition > 10¹²'] = fin & (kond > KOND_MAX)
    gueltig = fin & (kond <= KOND_MAX)
    return dict(T=T, xy=np.stack([x, y], -1), gueltig=gueltig, B=int(B),
                gruende={k: int(v.sum()) for k, v in gruende.items() if v.sum()},
                anteil_ungueltig=float(1 - gueltig.mean()), anteil_w_gespiegelt=float(gespiegelt.mean()),
                parameter=dict(g=g, x=x, y=y, kette=P, fn_zeta=FZ), unvollstaendig=unvollstaendig,
                nicht_gezogen=list(beschr.get('nicht_gezogen', [])), naeherungen=list(beschr.get('naeherungen', [])),
                format=beschr['format'], modell=beschr['modell'], laufzeit_s=round(time.perf_counter() - t0, 4))


def moment(Nz1, xy):
    """R₊₁, R₋₁ der ersten Harmonischen des Kippmoments aus den Zellzeigern (…, 3) und Zelllagen (…, 3, 2)."""
    Mx = (Nz1 * xy[..., 1]).sum(-1)
    My = -(Nz1 * xy[..., 0]).sum(-1)
    return (Mx + 1j * My) / 2, (np.conj(Mx) + 1j * np.conj(My)) / 2


def e3_auswerten(K, E0, idxA, idxB0, T, xy, dd, u_dd, phi_mess, triphasik, profil, rng, u_quant_grad, kmax=2,
                 T_zieh=None):
    """K: id → dict(Xz (n, 3, Kv) Zellharmonische, Z, nz); E0: Einzelmodul-Zellharmonische Phase 0 je Modul
    (n_j, 3, Kv); T: Nennwert (k, Zelle, Modul); xy: Zelllagen (3, 2); dd, u_dd: Δδⱼ und u(Δδⱼ); phi_mess: id → φ̄ⱼ^P
    (3). T_zieh: Ergebnis von t_ziehungen mit so vielen Ziehungen wie Bootstrap-Replikaten (Replikat b verwendet T_b
    und die Zelllagen von b für alle Konfigurationen, Messung und Vorhersage); None: keine Unsicherheitsbeschreibung,
    nur numerische Diagnostik mit festem T, keine dreiwertige Aussage. Je Prüfgröße steht zusätzlich u ohne T-Anteil
    (dieselben Replikate, T und Zelllagen fest) als Diagnose; die Bewertung nutzt sie nicht."""
    T = np.asarray(T)
    kond = np.linalg.cond(T)
    if not np.all(np.isfinite(kond)) or np.any(kond > KOND_MAX):
        return dict(status='nicht auswertbar: T(kω) singulär oder schlecht konditioniert (Zell- und Modullagen '
                           'trennen die Module nicht)', bewertung=None, kondition=np.asarray(kond).tolist())
    Tinv = np.linalg.inv(T)                                             # (k, Modul, Zelle)
    Nbar0 = np.stack([e.mean(0) for e in E0])                           # (Modul, Zelle, Kv)
    B = idxA[next(iter(idxA))].shape[0]
    zieh_dd = np.asarray(dd)[None, :] + np.asarray(u_dd)[None, :] * rng.standard_normal((B, 3))
    if T_zieh is not None:
        if T_zieh['B'] != B:
            raise ValueError(f'E3: {T_zieh["B"]} T-Ziehungen für {B} Bootstrap-Replikate')
        gb = T_zieh['gueltig']
        Tinv_b = np.full((B,) + Tinv.shape, np.nan + 1j * np.nan)
        Tinv_b[gb] = np.linalg.inv(T_zieh['T'][gb][:, :Tinv.shape[0]])
        xy_b = np.where(gb[:, None, None], T_zieh['xy'], np.nan)
    else:
        Tinv_b = np.broadcast_to(Tinv, (B,) + Tinv.shape)
        xy_b = np.broadcast_to(np.asarray(xy, float), (B, 3, 2))
    erg = []
    for kid, d in K.items():
        X = d['Xz'][..., :kmax]
        n = X.shape[0]
        C = bs.zaehlmatrix(idxA[kid], n)
        yb = (C @ X.reshape(n, -1)).reshape(-1, 3, kmax) / n
        rb = (C @ d['Z'][..., :kmax].reshape(n, -1)).reshape(-1, 3, kmax) / (C @ d['nz'])[:, None, None]
        y = X.mean(0)
        rho = vh.zeiger_mittel(d['Z'], d['nz'])
        Ch = np.einsum('kjc,ck->jk', Tinv[:kmax], y)                    # (Modul, k)
        Chb = np.einsum('bkjc,bck->bjk', Tinv_b[:, :kmax], yb)
        Chb_fest = None if T_zieh is None else np.einsum('kjc,bck->bjk', Tinv[:kmax], yb)   # Diagnose: T fest
        phiP = -np.degrees(np.angle(rho[:, 0])) + np.asarray(dd)
        phiPb = -np.degrees(np.angle(rb[:, :, 0])) + zieh_dd
        res = {}
        for j in (1, 2):
            dz = kv.wickel_grad(np.degrees(np.angle(Ch[0, 0]) - np.angle(Ch[j, 0])) - phiP[j])
            dzb = kv.wickel_grad(np.degrees(np.angle(Chb[:, 0, 0]) - np.angle(Chb[:, j, 0])) - phiPb[:, j])
            d2 = kv.wickel_grad(np.degrees(np.angle(Ch[0, 1]) - np.angle(Ch[j, 1])) - 2 * phiP[j]) / 2 \
                if kmax >= 2 else None                                  # erst modulo 360°, dann halbieren
            u = float(np.sqrt(np.nanvar(dzb, ddof=1) + u_quant_grad ** 2))
            if Chb_fest is None:
                u_fest = u
            else:
                dzf = kv.wickel_grad(np.degrees(np.angle(Chb_fest[:, 0, 0]) - np.angle(Chb_fest[:, j, 0])) -
                                     phiPb[:, j])
                u_fest = float(np.sqrt(np.var(dzf, ddof=1) + u_quant_grad ** 2))
            res[f'modul{j + 1}'] = dict(delta_phi_Z_grad=float(dz), u_grad=u, u_ohne_T_grad=u_fest,
                                        delta_phi_Z_k2_grad=None if d2 is None else float(d2))
        erg.append(dict(id=kid, e3a=res, amplitude=np.abs(Ch[:, 0]).tolist()))
    # E3b am Triphasik-Punkt: Zelllagen je Replikat gemeinsam für Messung und Vorhersage, T kommt nicht vor
    e3b = None
    if triphasik in K:
        d = K[triphasik]
        X = d['Xz'][..., :1]
        n = X.shape[0]
        rho = vh.zeiger_mittel(d['Z'], d['nz'])
        yhat = vh.vorhersage(Nbar0[..., :1], rho[:, :1], zellen=True)   # (Zelle, 1)
        Rp, Rm = moment(X.mean(0)[:, 0], xy)
        Rph, Rmh = moment(yhat[:, 0], xy)
        q = float(abs(Rm - Rmh) / abs(Rph))
        C = bs.zaehlmatrix(idxA[triphasik], n)
        yb = (C @ X.reshape(n, -1)).reshape(-1, 3, 1) / n
        rb = (C @ d['Z'][..., :1].reshape(n, -1)).reshape(-1, 3, 1) / (C @ d['nz'])[:, None, None]
        Nb = np.stack([(bs.zaehlmatrix(idxB0[j], E0[j].shape[0]) @ E0[j][..., :1].reshape(E0[j].shape[0], -1))
                       .reshape(-1, 3, 1) / E0[j].shape[0] for j in range(3)], 1)
        yhb = np.einsum('bjck,bjk->bck', Nb, rb)
        Rpb, Rmb = moment(yb[..., 0], xy_b)
        Rphb, Rmhb = moment(yhb[..., 0], xy_b)
        qb = np.abs(Rmb - Rmhb) / np.abs(Rphb)
        if T_zieh is None:
            u_q_fest = float(np.nanstd(qb, ddof=1))
        else:
            Rpf, Rmf = moment(yb[..., 0], xy)
            Rphf, Rmhf = moment(yhb[..., 0], xy)
            u_q_fest = float(np.std(np.abs(Rmf - Rmhf) / np.abs(Rphf), ddof=1))
        e3b = dict(id=triphasik, q_Z=q, u_q_Z=float(np.nanstd(qb, ddof=1)), u_q_Z_ohne_T=u_q_fest,
                   verhaeltnis_messung=float(abs(Rm) / abs(Rp)), verhaeltnis_vorhersage=float(abs(Rmh) / abs(Rph)))
    out = dict(e3a=erg, e3b=e3b, T_hinweis='T aus Statik (P0.1), Kette und 1 FG; Kippmoden vernachlässigt',
               u_ohne_T_hinweis='u_ohne_T_grad, u_q_Z_ohne_T: Diagnose aus denselben Replikaten mit festem T(kω) und '
                                'festen Zelllagen (Lesart vor Korrektur E); nicht Teil der Bewertung',
               k2_hinweis='k = 2: Abweichung gegen 2·φ̄ⱼ^P auf Ebene der Harmonischen modulo 360°, dann halbiert; '
                          'Werte in (−90°, 90°], lokaler Bezug zur Encoder-Profilphase; die Profilphase ist aus k = 2 '
                          'nur bis auf 180° bestimmt (keine Auflösung einer globalen 180°-Mehrdeutigkeit); zusätzliche '
                          'Diagnose, die Bewertung nutzt k = 1')
    if T_zieh is None:
        out['t_unsicherheit'] = dict(gezogen=False, grund='keine Unsicherheitsbeschreibung von T (Teil B nr5)')
        grund_num = ('Unsicherheit von T fehlt (Teil B ohne nr5.unsicherheit, A9.3 Nr. 5): u ohne T-Anteil, keine '
                     'dreiwertige Aussage aus festem T')
    else:
        out['t_unsicherheit'] = dict(gezogen=True, **{k: T_zieh[k] for k in (
            'format', 'modell', 'B', 'anteil_ungueltig', 'gruende', 'anteil_w_gespiegelt', 'unvollstaendig',
            'nicht_gezogen', 'naeherungen')})                         # Laufzeit nur in t_ziehungen (Reproduzierbarkeit)
        n_ung = int(B - T_zieh['gueltig'].sum())
        grund_num = ('Unsicherheitsbeschreibung von T unvollständig: ' + '; '.join(T_zieh['unvollstaendig'])
                     if T_zieh['unvollstaendig'] else
                     f'{n_ung} von {B} T-Ziehungen unzulässig ({T_zieh["gruende"]}); u nur aus den zulässigen '
                     'Ziehungen, keine dreiwertige Aussage' if n_ung else None)
    try:
        sw = profil.wert('e3.schwellen')
        profil.wert('e3.pruefzahl')
    except RegelOffen as e:
        out.update(status=f'nur beschreibend: {e.grund}', bewertung=None)
        return out
    if grund_num:
        out.update(status=f'nur numerisch: {grund_num}', bewertung=None)
        return out
    m = 2 * len(erg) + (1 if e3b else 0)
    zB = float(stats.norm.ppf(1 - 0.05 / m))
    pruef = []
    for e in erg:
        for v in e['e3a'].values():
            pruef.append((abs(v['delta_phi_Z_grad']), v['u_grad'], sw['phase_grad']))
    if e3b:
        pruef.append((e3b['q_Z'], e3b['u_q_Z'], sw['q_tol']))
    auff = any(x - zB * u > s for x, u, s in pruef)
    unauff = all(x + 1.645 * u <= s for x, u, s in pruef)
    out.update(z_B=zB, m=m, bewertung='auffällig' if auff else ('unauffällig' if unauff else 'unbestimmt'),
               status='Entwicklungsprofil (dreiwertig nur als Entwicklungsprüffall)')
    return out
