"""Werkzeug 4 (AP-11): Anpassverfahren für P0.1, P0.2, P0.4 und P0.5 (Präreg §5.2, A9.2, A9.7).

Eingang sind Messprotokolle der Phase 0 (Schema p0_messung; in dieser Stufe synthetisch). Ausgang ist eine gehashte
Kalibrierung (Schema kalibrierung) mit Werten, Unsicherheiten, Kovarianzen und Diagnosen; Stufe 1 liest daraus die
Umrechnung der Zellen, H3 und E3 lesen die übrigen Größen. Kein Parameter entsteht aus Kraftdaten der
Einzelmodulläufe (§5.2, A9.7); die Kalibrierung trägt die SHA-256 ihrer Eingänge.

P0.1  Kennlinie je Zelle (Ausgleich Rohwert = a₀ + a₁·F + a₂·F² + h·Richtung): Nullpunkt, Empfindlichkeit
      s = 1/a₁, quadratischer Anteil β = a₂/a₁ und Umkehrspanne 2h/a₁ (berichtet; die Umrechnung in Stufe 1 ist
      linear, Regel verarbeitung.kennlinie). Laststellen: Dreipunktlagerung Bᵀ·(ΔN/g) = W·(1, x, y) ist linear in
      (1/g_c, x_c/g_c, y_c/g_c); Rang und Kondition der Matrix der ΔN entscheiden über die Bestimmbarkeit, bei
      Rangabfall bleiben Verstärkungen und Lagen unbestimmt (kein Optimiererwert). Fehler in den Regressoren
      (errors in variables, linearisiert): Cov(θ_a, θ_b) = u²·(θ_aᵀθ_b)·(AᵀA)⁻¹. Brückensimulator: G_F je Zelle als
      Tiefpass erster Ordnung mit Laufzeit und Verstärkung (Entwicklungsmodell, Regel p0.gf_modell) mit Kovarianz und
      χ²; Widerspruch zur statischen Kalibrierung (G_F(f → 0) ≠ 1) wird gemeldet, nicht wegnormiert.
P0.2  M = Σ_c F̄_c,stat/g (Konvention b), m_j, μ; träge Masse M + m_L nur mit angegebenem m_L.
P0.4  Kette herausgerechnet (T_c/G_F,c), Summe aus den Zellen; 1-FG-Anpassung der Summe bei mittiger Anregung in
      (f_n, ζ) (H(ω) hängt nur von f_n und ζ ab, A9.7), gewichtet mit der Varianz des H1-Schätzers je Real- und
      Imaginärteil (1 − γ²)/(2·n·γ²)·|T|² (Regel p0.4.gewichtung), Kovarianz aus der Jacobi-Matrix zuzüglich der
      linear fortgepflanzten Unsicherheit der Kette (Neuanpassung je Kettenparameter), χ²-Diagnose,
      Lage von f_n zum Band; K = (M + m_L)·ω_n², C = 2ζ·(M + m_L)·ω_n. Linearität: zweite Amplitude (Parameter und
      Übertragung). Moden aus allen Zellkanälen mit gemeinsamen Polen (Σ_m (a + iωb)/(ω_m² − ω² + 2iζ_mω_mω), variable
      Projektion), Modellordnung nach χ²; 1-FG-Prüfung der Summe bei exzentrischer Anregung. Betriebslastprüfung:
      Schein-Oberwellen = Zellharmonische − T_h·Referenz.
P0.5  je Modul Zyklen zwischen eigenen Indeximpulsen, je Zyklus Ausgleich der Harmonischen (θ = 0 am Index), Mittel
      und Streuung über die Zyklen, Korrektur um G_x (Datenblatt, Unsicherheit linearisiert), a_k = −(kω)²·x_k,
      Δδⱼ = arg x₁⁽¹⁾ − arg x₁⁽ʲ⁾ mit u(Δδⱼ); Anforderung u(Δδⱼ) ≤ 0,1° als Prüfung, nicht als Zusage.
"""
import numpy as np
from scipy import optimize, stats

from . import formate, konventionen as kv

VERSION = 'anpassung-0.2'        # 0.2: P0.4 kette_richtungen (Korrektur E)


def _sha_eingang(obj):
    return formate.sha256_json(obj)


def _ols(X, y, w=None):
    """Gewichteter Ausgleich; Rückgabe (beta, Kovarianz bei bekannter Gewichtung, χ², Freiheitsgrade, Rang)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    sw = np.ones(len(y)) if w is None else np.sqrt(np.asarray(w, float))
    Xw, yw = X * sw[:, None], y * sw
    beta, _, rang, _ = np.linalg.lstsq(Xw, yw, rcond=None)
    r = yw - Xw @ beta
    dof = len(y) - X.shape[1]
    cov = np.linalg.pinv(Xw.T @ Xw)
    return beta, cov, float(r @ r), dof, int(rang)


# ── P0.1 ─────────────────────────────────────────────────────────────────────────────────────────────
def p01_zelle(e):
    """Kennlinie einer Zelle aus Laststufen auf- und absteigend."""
    F, d, y = (np.asarray(e[x], float) for x in ('last_N', 'richtung', 'adc'))
    X = np.c_[np.ones_like(F), F, F ** 2, d * (F > 0)]
    beta, cov0, chi2, dof, rang = _ols(X, y)
    if rang < 4 or dof < 1:
        return dict(bestimmbar=False, diagnose=f'Kennlinie nicht bestimmbar (Rang {rang}, Freiheitsgrade {dof})')
    s2 = chi2 / dof
    cov = cov0 * s2
    a0, a1, a2, h = beta
    u = np.sqrt(np.diag(cov))
    s = 1.0 / a1
    u_s_rel_stat = u[1] / abs(a1)
    u_last = float(e.get('u_last_rel', 0.0))
    # Linearitätsspanne: größte Abweichung der Geraden über den Lastbereich [N]
    bl, _, _, _, _ = _ols(np.c_[np.ones_like(F), F, d * (F > 0)], y)
    lin = float(np.max(np.abs((y - np.c_[np.ones_like(F), F, d * (F > 0)] @ bl) * s)))
    return dict(bestimmbar=True, nullpunkt_adc=float(a0), u_nullpunkt_adc=float(u[0]), empfindlichkeit_N_je_adc=float(s),
                u_empfindlichkeit_rel=float(np.hypot(u_s_rel_stat, u_last)), u_empfindlichkeit_rel_statistisch=float(
                    u_s_rel_stat), beta_je_N=float(a2 / a1), u_beta_je_N=float(np.hypot(u[2] / a1, a2 * u[1] / a1 ** 2)),
                umkehrspanne_N=float(2 * h / a1), u_umkehrspanne_N=float(2 * u[3] / abs(a1)),
                linearitaetsspanne_N=lin, sigma_adc=float(np.sqrt(s2)), freiheitsgrade=int(dof),
                kriechen='nicht im Datensatz', umrechnung='linear')


def p01_laststellen(ls, zellen_nominal=None, rang_tol=1e-9, kond_max=1e8):
    """Relative Zellverstärkungen g_c und Zelllagen (x_c, y_c) aus bekannten Lasten an bekannten Orten."""
    o = np.asarray(ls['orte_m'], float)
    A = np.asarray(ls['delta_N'], float)
    W = float(ls['last_N'])
    uN = float(ls['u_N'])
    P = A.shape[0]
    sv = np.linalg.svd(A, compute_uv=False)
    # Rang gegen das Rauschen: ein Singulärwert in Höhe des Rauschens (u·√P) gilt als null
    rang = int((sv > max(rang_tol * sv[0], 10 * uN * np.sqrt(P))).sum())
    kond = float(sv[0] / sv[-1]) if sv[-1] > 0 else float('inf')
    diag = dict(stellen=P, rang=rang, singulaerwerte=sv.tolist(), kondition=kond,
                rang_regel='Singulärwerte über max(10⁻⁹·σ₁, 10·u·√P)')
    if P < 3 or rang < 3 or kond > kond_max:
        _, _, Vt = np.linalg.svd(A)
        return dict(bestimmbar=False, **diag, nullraum=Vt[-1].tolist(),
                    diagnose=('Verstärkungen und Zelllagen nicht bestimmbar: ' +
                              (f'nur {P} Laststellen' if P < 3 else f'Rang {rang} < 3' if rang < 3 else
                               f'Kondition {kond:.3g} > {kond_max:g}') +
                              ' (Laststellen auf einer Geraden oder zu wenige); keine Werte ausgegeben'))
    rhs = [W * np.ones(P), W * o[:, 0], W * o[:, 1]]
    th = [np.linalg.lstsq(A, b, rcond=None)[0] for b in rhs]          # h = 1/g, u = x/g, v = y/g
    G = np.linalg.inv(A.T @ A)
    C = np.zeros((9, 9))
    for i in range(3):
        for j in range(3):
            C[3 * i:3 * i + 3, 3 * j:3 * j + 3] = uN ** 2 * float(th[i] @ th[j]) * G
    h, uu, vv = th
    g, x, y = 1 / h, uu / h, vv / h
    J = np.zeros((9, 9))                                                # (g, x, y) nach (h, u, v)
    for c in range(3):
        J[c, c] = -1 / h[c] ** 2
        J[3 + c, c], J[3 + c, 3 + c] = -uu[c] / h[c] ** 2, 1 / h[c]
        J[6 + c, c], J[6 + c, 6 + c] = -vv[c] / h[c] ** 2, 1 / h[c]
    Cg = J @ C @ J.T
    E = np.stack([A @ th[i] - rhs[i] for i in range(3)], 1)            # (P, 3)
    S = uN ** 2 * np.array([[th[i] @ th[j] for j in range(3)] for i in range(3)])
    chi2 = float(np.einsum('pi,ij,pj->', E, np.linalg.inv(S), E))
    dof = 3 * (P - 3)
    p = float(stats.chi2.sf(chi2, dof)) if dof > 0 else float('nan')
    u = np.sqrt(np.diag(Cg))
    out = dict(bestimmbar=True, **diag, g=g.tolist(), u_g=u[:3].tolist(), x_m=x.tolist(), u_x_m=u[3:6].tolist(),
               y_m=y.tolist(), u_y_m=u[6:].tolist(), kovarianz_g_x_y=Cg, chi2=chi2, freiheitsgrade=dof, p_wert=p,
               modell_passt=bool(dof == 0 or p >= 1e-3),
               ziel=dict(lage_m=1e-4, verstaerkung_rel=1e-3,
                         lage_erreicht=bool(max(u[3:].max(), 0) <= 1e-4),
                         verstaerkung_erreicht=bool((u[:3] / np.abs(g)).max() <= 1e-3)))
    if zellen_nominal is not None:
        out['abweichung_von_nominal_m'] = (np.c_[x, y] - np.asarray(zellen_nominal, float)).tolist()
    return out


def gf_modell(p, f):
    """G_F(f) = g·e^{−i2πfτ}/(1 + i·f·w), p = (g, τ, w = 1/f_tp)."""
    g, tau, w = p
    f = np.asarray(f, float)
    return g * np.exp(-2j * np.pi * f * tau) / (1 + 1j * f * w)


def _gf_anpassen(f, y, sd, x0, frei_w):
    def res(q):
        p = q if frei_w else np.r_[q, 0.0]
        d = (gf_modell(p, f) - y) / sd
        return np.r_[d.real, d.imag]
    lo, hi = ([0, -1e-2, 0], [np.inf, 1e-2, 1.0]) if frei_w else ([0, -1e-2], [np.inf, 1e-2])
    q0 = x0 if frei_w else x0[:2]
    r = optimize.least_squares(res, q0, bounds=(lo, hi), x_scale=[1, 1e-4, 1e-3][:len(q0)], xtol=1e-14, ftol=1e-14,
                               gtol=1e-14, max_nfev=2000)
    cov = np.zeros((3, 3))
    cov[:len(q0), :len(q0)] = np.linalg.pinv(r.jac.T @ r.jac)
    p = r.x if frei_w else np.r_[r.x, 0.0]
    return p, cov, float(2 * r.cost), 2 * f.size - len(q0)


def p01_bruecke(br):
    """Kette je Zelle aus dem Brückensimulator: Anpassung von gf_modell (g, τ, w = 1/f_tp) mit Kovarianz und χ².
    Liegt der Tiefpass weit über den Messfrequenzen, sind τ und w nicht trennbar (beide nur Phase in erster Ordnung):
    dann gilt das Modell ohne Tiefpass (w = 0), wenn das volle Modell χ² nicht nachweisbar senkt (Regel
    p0.gf_modell)."""
    f = np.asarray(br['f_hz'], float)
    Gm = np.asarray(br['G'])
    urel = float(br['u_rel'])
    out = []
    for c in range(Gm.shape[0]):
        y = Gm[c]
        sd = urel * np.abs(y)
        ph = np.unwrap(np.angle(y))
        tau0 = max(-np.polyfit(2 * np.pi * f[:4], ph[:4], 1)[0], 0.0)
        x0 = [abs(y[0]), tau0, 1e-4]
        p3, c3, chi3, dof3 = _gf_anpassen(f, y, sd, x0, True)
        p2, c2, chi2_, dof2 = _gf_anpassen(f, y, sd, x0, False)
        rho = c3[1, 2] / np.sqrt(c3[1, 1] * c3[2, 2]) if c3[1, 1] > 0 and c3[2, 2] > 0 else 1.0
        p_f = float(stats.chi2.sf(max(chi2_ - chi3, 0.0), 1))
        reduziert = bool(p_f > 0.01 or abs(rho) > 0.995)
        p, cov, chi2, dof = (p2, c2, chi2_, dof2) if reduziert else (p3, c3, chi3, dof3)
        u = np.sqrt(np.diag(cov))
        g = p[0]
        wid = bool(abs(g - 1) > max(3 * u[0], 1e-6))
        out.append(dict(modell='laufzeit' if reduziert else 'tiefpass1_laufzeit', p=p.tolist(), kovarianz=cov,
                        g=float(g), u_g=float(u[0]), tau_s=float(p[1]), u_tau_s=float(u[1]),
                        f_tp_hz=float(1 / p[2]) if p[2] > 0 else float('inf'), w=float(p[2]), u_w=float(u[2]),
                        tiefpass_bestimmbar=not reduziert, korrelation_tau_w_voll=float(rho),
                        p_tiefpass=p_f, chi2=chi2, freiheitsgrade=dof, p_wert=float(stats.chi2.sf(chi2, dof)),
                        modell_passt=bool(stats.chi2.sf(chi2, dof) >= 1e-3), statik_widerspruch=wid,
                        diagnose=('G_F(f → 0) = {:.5f} ± {:.1e} widerspricht der statischen Kalibrierung (1); '
                                  'Wert unverändert übernommen'.format(g, u[0])) if wid else ''))
    return out


def kette_cholesky(bruecke):
    """Je Zelle (Zelle, Parameterindizes mit positiver Varianz, Cholesky-Faktor ihrer Kovarianz) der Brückenanpassung;
    gemeinsame Grundlage der Störrichtungen (kette_richtungen, P0.4) und der T-Ziehungen von E3 (Reihenfolge Zelle,
    dann Spalte)."""
    out = []
    for c, b in enumerate(bruecke):
        C = np.asarray(b['kovarianz'], float)
        idx = [i for i in range(3) if C[i, i] > 0]
        L = np.linalg.cholesky(C[np.ix_(idx, idx)] + 1e-30 * np.eye(len(idx))) if idx else np.zeros((0, 0))
        out.append((c, idx, L))
    return out


def kette_richtungen(bruecke, f):
    """Unabhängige Störrichtungen von G_F (Zelle, f) aus den Kovarianzen der Brückenanpassung (Cholesky je Zelle):
    Liste von (Zelle, δG(f)) mit δG = G(p + L·e_i) − G(p)."""
    out = []
    for c, idx, L in kette_cholesky(bruecke):
        if not idx:
            continue
        G0 = gf_modell(bruecke[c]['p'], f)
        for col in range(len(idx)):
            pp = np.array(bruecke[c]['p'], float)
            pp[idx] += L[:, col]
            out.append((c, gf_modell(pp, f) - G0))
    return out


def gf_wert(bruecke, f):
    """G_F (Zelle, f) aus den Anpassungen der Brücke."""
    return np.array([gf_modell(b['p'], f) for b in bruecke])


def gf_ziehungen(bruecke, f, rng, n):
    """Ziehungen von G_F(f) (n, Zelle, f) aus der Kovarianz der Anpassung (für H3, A9.7)."""
    out = np.empty((n, len(bruecke), np.size(f)), complex)
    for c, b in enumerate(bruecke):
        P = rng.multivariate_normal(b['p'], b['kovarianz'], size=n)
        P[:, 2] = np.abs(P[:, 2])
        for i in range(n):
            out[i, c] = gf_modell(P[i], f)
    return out


def p01_superposition(sup, kmax=8):
    """Superpositionsfehler der Elektronik: Antwort(1 + 2) − Antwort(1) − Antwort(2)."""
    e = np.asarray(sup['antwort12']) - np.asarray(sup['antwort1']) - np.asarray(sup['antwort2'])
    Ek = kv.harmonische(e, kmax)
    return dict(max_abs=float(np.abs(e).max()), harmonische_abs=np.abs(Ek).tolist(), einheit=sup.get('einheit', 'N'),
                schwelle='≤ 0,3·u_c,erw (Nachweis in Teil B; u_c,erw erst nach P0.11)')


def p01_auswerten(m):
    zellen = [p01_zelle(e) for e in m['einzeln']]
    out = dict(zellen=zellen, laststellen=p01_laststellen(m['laststellen'], m.get('zellen_nominal_m')),
               bruecke=p01_bruecke(m['bruecke']), superposition=p01_superposition(m['superposition']),
               zellen_nominal_m=np.asarray(m['zellen_nominal_m'], float).tolist(),
               module_nominal_m=None if m.get('module_nominal_m') is None else np.asarray(
                   m['module_nominal_m'], float).tolist())
    q = m.get('querkraft')
    if q is not None:
        out['querkraft'] = dict(kraft_N=q['kraft_N'], delta_summe_N=q['delta_summe_N'], u_N=q['u_N'],
                                schwelle='≤ 0,1·Δ_q (Δ_q erst aus P0.11)')
    return out


# ── P0.2 ─────────────────────────────────────────────────────────────────────────────────────────────
def p02_auswerten(m):
    F = np.asarray(m['F_c_stat_N'], float)
    n = F.shape[0]
    Fm = F.mean(0)
    uF = np.maximum(F.std(0, ddof=1) / np.sqrt(n) if n > 1 else 0 * Fm, float(m['u_F_N']) / np.sqrt(n))
    g, ug = float(m['g']['wert']), float(m['g']['u'])
    S = Fm.sum()
    M = S / g
    uM = M * np.hypot(np.sqrt((uF ** 2).sum()) / S, ug / g)
    mj = np.asarray(m['m_j_kg'], float)
    umj = np.broadcast_to(np.asarray(m['u_m_j_kg'], float), (3,)).astype(float)
    out = dict(konvention='b', M_kg=float(M), u_M_kg=float(uM), statische_last_N=float(S),
               F_c_stat_N=Fm.tolist(), u_F_c_stat_N=uF.tolist(), m_j_kg=mj.tolist(), u_m_j_kg=umj.tolist(),
               mu=float(mj.sum() / M), g=dict(wert=g, u=ug, quelle=m['g'].get('quelle', '')), luft=m.get('luft'),
               gesamtwaegung=m.get('gesamtwaegung'), gesamtwaegung_grund=m.get('gesamtwaegung_grund'))
    mL = m.get('m_L')
    if mL is None:
        out.update(m_L=None, M_traege_kg=None,
                   diagnose='m_L nicht angegeben: träge Masse M + m_L offen; K und C werden nicht angegeben, '
                            'f_n und ζ schon (H(ω) hängt nur von f_n und ζ ab, A9.7)')
    else:
        out.update(m_L=dict(wert_kg=float(mL['wert_kg']), u_kg=float(mL['u_kg']), quelle=mL.get('quelle', '')),
                   M_traege_kg=float(M + mL['wert_kg']), u_M_traege_kg=float(np.hypot(uM, mL['u_kg'])))
    return out


# ── P0.4 ─────────────────────────────────────────────────────────────────────────────────────────────
def h1fg(f, f_n, zeta):
    """1-FG-Übertragung äußere Kraft → Auflagekraft, nur von f_n und ζ abhängig."""
    r = np.asarray(f, float) / f_n
    return (1 + 2j * zeta * r) / (1 - r ** 2 + 2j * zeta * r)


KOHAERENZ_MIN = 0.5                    # Regel p0.4.kohaerenz_min (technisch): Linien darunter tragen kein Signal


def _kanaele_mechanisch(d, G):
    """Zellen ohne Kette und Summe aus den Zellen; Varianzen je Real- und Imaginärteil. Linien mit Kohärenz unter
    KOHAERENZ_MIN erhalten unendliche Varianz (kein Gewicht); die Summe gilt dort als nicht gemessen."""
    T = np.asarray(d['T'])
    g2 = np.asarray(d['kohaerenz'], float)
    ok = g2 >= KOHAERENZ_MIN
    with np.errstate(divide='ignore', invalid='ignore'):
        var = np.where(ok, (1 - g2) / (2 * d['n_mittel'] * np.where(ok, g2, 1.0)) * np.abs(T) ** 2, np.inf)
    var = np.maximum(var, 1e-300)
    Tc = T[:3] / G
    vc = var[:3] / np.abs(G) ** 2
    vs = vc.sum(0)
    return Tc, vc, Tc.sum(0), vs


def _fit_1fg(f, T, var, x0=None):
    sd = np.sqrt(var)

    def res(p):
        d = (h1fg(f, p[0], p[1]) - T) / sd
        return np.r_[d.real, d.imag]
    if x0 is None:
        best = None
        for fn in np.geomspace(f.min() / 3, f.max() * 3, 120):
            for z in np.geomspace(0.003, 1.0, 30):
                c = float(np.sum(res((fn, z)) ** 2))
                if best is None or c < best[0]:
                    best = (c, fn, z)
        x0 = [best[1], best[2]]
    r = optimize.least_squares(res, x0, bounds=([1e-6, 1e-5], [np.inf, 5.0]),
                               x_scale=[x0[0], x0[1]], xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=5000)
    J = r.jac
    JTJ = J.T @ J
    cov = np.linalg.pinv(JTJ)
    chi2 = float(2 * r.cost)
    dof = 2 * f.size - 2
    return r.x, cov, chi2, dof, float(np.linalg.cond(JTJ))


def _chi2_mit_kette(res, var, richtungen):
    """χ² eines komplexen Residuums mit Kovarianz diag(var) je Real- und Imaginärteil plus Σ δT·δTᵀ der Kette."""
    ok = np.isfinite(var)
    r = np.r_[res.real[ok], res.imag[ok]]
    V = np.diag(np.r_[var[ok], var[ok]])
    for d in richtungen:
        v = np.r_[d.real[ok], d.imag[ok]]
        V += np.outer(v, v)
    return float(r @ np.linalg.solve(V, r))


def _modalfit(f, kanaele, M, start):
    """Gemeinsame Pole (f_m, ζ_m) für alle Kanäle, Residuen a + iωb je Kanal und Mode (variable Projektion)."""
    w = 2 * np.pi * f

    def basis(p):
        cols = []
        for m in range(M):
            wm, z = 2 * np.pi * p[2 * m], p[2 * m + 1]
            B = 1 / (wm ** 2 - w ** 2 + 2j * z * wm * w)
            cols += [B, 1j * w * B]
        return np.array(cols).T                                         # (F, 2M) komplex

    def res(p):
        Bm = basis(p)
        out = []
        for T, var in kanaele:
            sd = np.sqrt(var)
            X = np.r_[Bm.real / sd[:, None], Bm.imag / sd[:, None]]
            y = np.r_[T.real / sd, T.imag / sd]
            c = np.linalg.lstsq(X, y, rcond=None)[0]
            out.append(y - X @ c)
        return np.concatenate(out)
    lo = np.ravel([[f.min() / 4, 1e-4] for _ in range(M)])
    hi = np.ravel([[f.max() * 4, 2.0] for _ in range(M)])
    x0 = np.clip(np.ravel(start), lo * 1.0001, hi * 0.9999)
    r = optimize.least_squares(res, x0, bounds=(lo, hi), x_scale=np.abs(x0), xtol=1e-12, ftol=1e-12, gtol=1e-12,
                               max_nfev=4000)
    chi2 = float(2 * r.cost)
    npar = 2 * M + 2 * M * len(kanaele)
    dof = 2 * f.size * len(kanaele) - npar
    cov = np.linalg.pinv(r.jac.T @ r.jac)
    return r.x, cov, chi2, dof


def p04_moden(f, kanaele, f_n, zeta, M_max=3):
    """Modellordnung 0 … M_max (0: frequenzunabhängige Statik) nach χ²; Rückgabe gewählte Moden und Verlauf."""
    verlauf = []
    # M = 0: konstante Übertragung je Kanal (starre Auflage im Band)
    chi0, dof0 = 0.0, 0
    for T, var in kanaele:
        sd = np.sqrt(var)
        X = np.r_[np.ones(f.size) / sd, np.zeros(f.size)][:, None]
        X = np.c_[X, np.r_[np.zeros(f.size), np.ones(f.size) / sd]]
        y = np.r_[T.real / sd, T.imag / sd]
        b, _, c2, d, _ = _ols(X, y)
        chi0 += c2
        dof0 += d
    verlauf.append(dict(M=0, chi2=chi0, freiheitsgrade=dof0, p_wert=float(stats.chi2.sf(chi0, dof0))))
    gewaehlt = dict(M=0, pole=[], kovarianz=None)
    start = [[f_n, zeta]]
    vorher = (chi0, dof0)
    for M in range(1, M_max + 1):
        p, cov, chi2, dof = _modalfit(f, kanaele, M, start)
        verlauf.append(dict(M=M, chi2=chi2, freiheitsgrade=dof, p_wert=float(stats.chi2.sf(chi2, dof)),
                            pole=p.reshape(M, 2).tolist()))
        dchi, ddof = vorher[0] - chi2, vorher[1] - dof
        p_f = float(stats.f.sf((dchi / ddof) / (chi2 / dof), ddof, dof)) if ddof > 0 and chi2 > 0 else 0.0
        verlauf[-1]['p_verbesserung'] = p_f
        if p_f > 0.01:                                                  # zusätzliche Mode nicht nachweisbar
            break
        gewaehlt = dict(M=M, pole=p.reshape(M, 2), kovarianz=cov, chi2=chi2, freiheitsgrade=dof)
        vorher = (chi2, dof)
        if stats.chi2.sf(chi2, dof) >= 1e-3:
            break
        # nächste Mode: Startwert an der größten Restabweichung
        T_sum = sum(np.abs(T) for T, _ in kanaele)
        cand = f[np.argsort(T_sum)[::-1]]
        bek = p.reshape(M, 2)[:, 0]
        neu = next((c for c in cand if np.all(np.abs(c - bek) > 0.05 * bek)), f[len(f) // 2])
        start = list(p.reshape(M, 2)) + [[neu, zeta]]
    moden = []
    if gewaehlt['M'] > 0:
        P, C = gewaehlt['pole'], gewaehlt['kovarianz']
        for m in np.argsort(P[:, 0]):
            moden.append(dict(f_hz=float(P[m, 0]), u_f_hz=float(np.sqrt(C[2 * m, 2 * m])), zeta=float(P[m, 1]),
                              u_zeta=float(np.sqrt(C[2 * m + 1, 2 * m + 1]))))
    return moden, verlauf


def p04_auswerten(m, p01, p02, band_hz, amplituden=None, kmax=None, f=None):
    """P0.4 mit festgelegtem Frequenzband band_hz = (f_lo, f_hi) (Teil B; kein stiller Vorgabewert)."""
    if band_hz is None:
        raise ValueError('P0.4: Anpassungsband nicht angegeben (Teil B, Werkzeug 4)')
    fa = np.asarray(m['f_hz'], float)
    sel = (fa >= band_hz[0]) & (fa <= band_hz[1])
    if sel.sum() < 5:
        raise ValueError(f'P0.4: weniger als 5 Frequenzlinien im Band {band_hz}')
    fs = fa[sel]
    G = gf_wert(p01['bruecke'], fs)
    daten = m['daten']
    amps = sorted({d['amplitude'] for d in daten.values()}) if amplituden is None else list(amplituden)
    out = dict(band_hz=list(band_hz), frequenzlinien=int(sel.sum()), amplituden=amps, kette='aus P0.1 (Brücke)')
    fits = {}
    for amp in amps:
        d = daten[f'mitte@{amp:g}']
        dsel = {k: (np.asarray(v)[..., sel] if k in ('T', 'kohaerenz') else v) for k, v in d.items()}
        Tc, vc, Ts, vs = _kanaele_mechanisch(dsel, G)
        x, cov_stat, chi2, dof, kond = _fit_1fg(fs, Ts, vs)
        # Unsicherheit der Kette (Brücke) linear fortgepflanzt: Neuanpassung je unabhängiger Störrichtung
        richt = kette_richtungen(p01['bruecke'], fs)
        dX, dT = [], []
        for c, dG in richt:
            Gp = G.copy()
            Gp[c] = G[c] + dG
            Tp = _kanaele_mechanisch(dsel, Gp)[2]
            dT.append(Tp - Ts)
            dX.append(_fit_1fg(fs, Tp, vs, x0=x)[0] - x)
        cov_gf = sum(np.outer(v, v) for v in dX) if dX else np.zeros((2, 2))
        chi2_k = _chi2_mit_kette(Ts - h1fg(fs, *x), vs, dT)
        cov = cov_stat + cov_gf
        pw = float(stats.chi2.sf(chi2_k, dof))
        u = np.sqrt(np.diag(cov))
        diag = []
        if not (band_hz[0] <= x[0] <= band_hz[1]):
            diag.append(f'f_n = {x[0]:.4g} Hz außerhalb des Anpassungsbands {band_hz}')
        if u[0] > 0.2 * x[0] or u[1] > x[1] or kond > 1e12:
            diag.append('f_n und ζ nicht identifizierbar (Unsicherheit über 20 % bzw. 100 % oder Kondition '
                        f'{kond:.2g}); Band erweitern')
        if pw < 1e-3:
            diag.append(f'1-FG-Modell der Summe passt nicht (χ²/ν = {chi2_k / dof:.3g} mit Kettenunsicherheit, '
                        f'p = {pw:.2g})')
        rid = [(c, col) for c, idx, _ in kette_cholesky(p01['bruecke']) for col in range(len(idx))]
        fits[amp] = dict(f_n_hz=float(x[0]), u_f_n_hz=float(u[0]), zeta=float(x[1]), u_zeta=float(u[1]),
                         kovarianz_fn_zeta=cov, kovarianz_statistisch=cov_stat, kovarianz_kette=cov_gf,
                         # Verschiebung von (f_n, ζ) je Störrichtung der Kette (kovarianz_kette = Σ d·dᵀ); erlaubt
                         # gemeinsame Ziehungen von Kette und 1 FG ohne Doppelzählung (E3, A9.13)
                         kette_richtungen=[dict(zelle=c + 1, spalte=col, d_fn_zeta=[float(v[0]), float(v[1])])
                                           for (c, col), v in zip(rid, dX)],
                         korrelation=float(cov[0, 1] / (u[0] * u[1])) if u.all() else None,
                         chi2=chi2, chi2_mit_kette=chi2_k, freiheitsgrade=dof, p_wert=pw, kondition=kond,
                         identifizierbar=not any('nicht identifizierbar' in s for s in diag), diagnose=diag)
    a1 = amps[0]
    haupt = fits[a1]
    out['einfreiheitsgrad'] = haupt
    out['einfreiheitsgrad_je_amplitude'] = {f'{a:g}': v for a, v in fits.items()}
    # träge Masse, K und C
    if p02.get('M_traege_kg') is not None and haupt['identifizierbar']:
        Mt, uMt = p02['M_traege_kg'], p02['u_M_traege_kg']
        wn = 2 * np.pi * haupt['f_n_hz']
        K = Mt * wn ** 2
        Cc = 2 * haupt['zeta'] * Mt * wn
        J = np.array([[Mt * 2 * wn * 2 * np.pi, 0, wn ** 2],
                      [2 * haupt['zeta'] * Mt * 2 * np.pi, 2 * Mt * wn, 2 * haupt['zeta'] * wn]])
        Cin = np.zeros((3, 3))
        Cin[:2, :2] = haupt['kovarianz_fn_zeta']
        Cin[2, 2] = uMt ** 2
        CKC = J @ Cin @ J.T
        out['K_C'] = dict(K_N_je_m=float(K), C_Ns_je_m=float(Cc), kovarianz=CKC, M_traege_kg=Mt,
                          u_K=float(np.sqrt(CKC[0, 0])), u_C=float(np.sqrt(CKC[1, 1])))
    else:
        out['K_C'] = dict(K_N_je_m=None, C_Ns_je_m=None,
                          diagnose='K, C nicht angegeben: ' + ('m_L fehlt (träge Masse offen)'
                                                               if p02.get('M_traege_kg') is None else
                                                               'f_n, ζ nicht identifizierbar'))
    # Linearität (zwei Amplituden)
    if len(amps) >= 2:
        a2 = amps[1]
        f1, f2 = fits[a1], fits[a2]
        z_fn = (f2['f_n_hz'] - f1['f_n_hz']) / np.hypot(f1['u_f_n_hz'], f2['u_f_n_hz'])
        z_ze = (f2['zeta'] - f1['zeta']) / np.hypot(f1['u_zeta'], f2['u_zeta'])
        chi, dof = 0.0, 0
        for name in {k.split('@')[0] for k in daten}:
            k1, k2 = f'{name}@{a1:g}', f'{name}@{a2:g}'
            if k1 in daten and k2 in daten:
                c1 = _kanaele_mechanisch({k: (np.asarray(v)[..., sel] if k in ('T', 'kohaerenz') else v)
                                          for k, v in daten[k1].items()}, G)
                c2 = _kanaele_mechanisch({k: (np.asarray(v)[..., sel] if k in ('T', 'kohaerenz') else v)
                                          for k, v in daten[k2].items()}, G)
                dT = c1[0] - c2[0]
                v = c1[1] + c2[1]
                chi += float((dT.real ** 2 / v + dT.imag ** 2 / v).sum())
                dof += 2 * dT.size
        p_lin = float(stats.chi2.sf(chi, dof))
        out['linearitaet'] = dict(amplituden=[a1, a2], z_f_n=float(z_fn), z_zeta=float(z_ze), chi2=chi,
                                  freiheitsgrade=dof, p_wert=p_lin, linear=bool(p_lin >= 0.01 and abs(z_fn) < 3
                                                                                and abs(z_ze) < 3),
                                  regel='gleich innerhalb der Unsicherheit: p ≥ 0,01 und |z| < 3 (technisch)')
    # Moden aus allen Zellkanälen (alle Orte, erste Amplitude)
    kan = []
    for key, d in daten.items():
        if d['amplitude'] != a1:
            continue
        Tc, vc, _, _ = _kanaele_mechanisch({k: (np.asarray(v)[..., sel] if k in ('T', 'kohaerenz') else v)
                                            for k, v in d.items()}, G)
        kan += [(Tc[c], vc[c]) for c in range(3) if np.isfinite(vc[c]).all()]
    moden, verlauf = p04_moden(fs, kan, haupt['f_n_hz'], haupt['zeta'])
    for mo in moden:
        mo['im_band'] = bool(band_hz[0] <= mo['f_hz'] <= band_hz[1])
    out['moden'] = [mo for mo in moden if mo['im_band']]
    out['moden_ausserhalb_band'] = [mo for mo in moden if not mo['im_band']]
    moden = out['moden']
    out['modellordnung'] = verlauf
    out['f_1_hz'] = moden[0]['f_hz'] if moden else None
    out['f_1_hinweis'] = ('niedrigste in N oder einer Zellkraft sichtbare Mode im Band (A1)' if moden else
                          f'keine Mode im Band {band_hz}: f₁ > {band_hz[1]:g} Hz (untere Schranke); Moden außerhalb '
                          'des Bands sind extrapoliert und nicht bestimmt')
    # 1-FG-Prüfung der Summe bei exzentrischer Anregung: ganzes Band und Bereich (b) der Auswertung (f ≤ f₁/2)
    f1 = out['f_1_hz'] if out['f_1_hz'] is not None else band_hz[1]
    unten = fs <= f1 / 2
    Hs = h1fg(fs, haupt['f_n_hz'], haupt['zeta'])
    exz = {}
    for key, d in daten.items():
        if d['amplitude'] != a1 or key.startswith('mitte'):
            continue
        dsel = {k: (np.asarray(v)[..., sel] if k in ('T', 'kohaerenz') else v) for k, v in d.items()}
        _, _, Ts, vs = _kanaele_mechanisch(dsel, G)
        if not np.isfinite(vs).all():
            exz[key] = dict(pruefbar=False, grund='Summe nicht aus allen Zellen messbar (Kohärenz unter '
                                                  f'{KOHAERENZ_MIN:g} in einer Zelle)')
            continue
        dT = Ts - Hs
        dK = []
        for c, dG in kette_richtungen(p01['bruecke'], fs):
            Gp = G.copy()
            Gp[c] = G[c] + dG
            dK.append(_kanaele_mechanisch(dsel, Gp)[2] - Ts)
        c_band = _chi2_mit_kette(dT, vs, dK)
        e = dict(chi2_band=c_band, freiheitsgrade_band=2 * fs.size, p_wert_band=float(stats.chi2.sf(c_band,
                                                                                                    2 * fs.size)))
        if unten.any():
            rel = np.abs(dT[unten]) / np.abs(Hs[unten])
            c_b = _chi2_mit_kette(dT[unten], vs[unten], [x[unten] for x in dK])
            e.update(chi2_b=c_b, freiheitsgrade_b=int(2 * unten.sum()),
                     p_wert_b=float(stats.chi2.sf(c_b, 2 * unten.sum())), max_rel_abweichung_b=float(
                         rel.max()), u_rel_typisch_b=float(np.median(np.sqrt(vs[unten]) / np.abs(Hs[unten]))))
        exz[key] = e
    out['summe_exzentrisch'] = exz
    i_hub = int(np.argmin([abs(mo['f_hz'] - haupt['f_n_hz']) for mo in moden])) if moden else None
    kipp = [mo for i, mo in enumerate(moden) if i != i_hub]
    gruende = []
    if haupt['p_wert'] < 1e-3:
        gruende.append('Summe bei mittiger Anregung (ganzes Band)')
    gruende += [f'Summe bei Anregung {k} im Bereich f ≤ f₁/2 (max. relative Abweichung '
                f'{v["max_rel_abweichung_b"]:.2g})' for k, v in exz.items() if v.get('p_wert_b', 1.0) < 1e-3]
    hinweise = [f'Summe bei Anregung {k}: Abweichung vom 1-FG-Modell im ganzen Band nachweisbar (Kopplung Hub–Kippen '
                f'nahe den Moden), nicht im Bereich f ≤ f₁/2' for k, v in exz.items()
                if v.get('p_wert_band', 1.0) < 1e-3 and v.get('p_wert_b', 1.0) >= 1e-3]
    hinweise += [f'Summe bei Anregung {k}: {v["grund"]}' for k, v in exz.items() if not v.get('pruefbar', True)]
    out['einfreiheitsgrad_ausreichend'] = dict(
        summe=not gruende, gruende=gruende, hinweise=hinweise,
        hubmode_hz=None if i_hub is None else moden[i_hub]['f_hz'], kippmoden_hz=[mo['f_hz'] for mo in kipp],
        bewertung=('1-FG-Modell der Summe unzureichend: ' + '; '.join(gruende)) if gruende else
        ('Summe folgt dem 1-FG-Modell im Bereich f ≤ f₁/2' + ('; Kippmoden nur in den Zellkräften' if kipp else '')))
    # Betriebslastprüfung (Schein-Oberwellen)
    bl = m.get('betriebslast')
    if bl:
        rows = {}
        for key, e in bl.items():
            for h, ob in e['oberwellen'].items():
                fh = int(h) * e['f_hz']
                if kmax is not None and f is not None and fh > kmax * f + 1e-9:
                    continue
                schein = np.asarray(ob['zellen']) - np.asarray(ob['T_h']) * ob['referenz']
                rows[f'{key}/h{h}'] = dict(f_hz=float(fh), schein_N=np.abs(schein).tolist())
        out['betriebslast'] = dict(schein_oberwellen=rows, max_schein_N=max(max(r['schein_N']) for r in rows.values())
                                   if rows else None,
                                   schwelle='≤ p0.klirr_faktor·u_c,erw (offen; Faktor im Entwicklungsprofil 0,3)')
    return out


# ── P0.5 ─────────────────────────────────────────────────────────────────────────────────────────────
def gx_modell(gx, f):
    f = np.asarray(f, float)
    w = 0.0 if not np.isfinite(gx['f_tp']) else 1.0 / gx['f_tp']
    return gx['gain'] * np.exp(-2j * np.pi * f * gx['tau']) / (1 + 1j * f * w)


def _gx_ableitungen(gx, f):
    """∂ ln G_x/∂(gain, τ, f_tp)."""
    f = np.asarray(f, float)
    d_gain = np.ones_like(f) / gx['gain'] + 0j
    d_tau = -2j * np.pi * f
    d_ftp = (1j * f / gx['f_tp'] ** 2) / (1 + 1j * f / gx['f_tp'])
    return d_gain, d_tau, d_ftp


def p05_modul(mod, f_nominal, K):
    """Harmonische des Wegs bezogen auf den eigenen Indeximpuls (ohne G_x-Korrektur), Mittel und Streuung."""
    t, x, idx = (np.asarray(mod[k], float) for k in ('t_s', 'weg_m', 'index_s'))
    idx = idx[(idx >= t[0]) & (idx <= t[-1])]
    if idx.size < 3:
        return dict(bestimmbar=False, diagnose='weniger als zwei vollständige Zyklen zwischen Indeximpulsen')
    per = np.diff(idx)
    fq = 1.0 / per.mean()
    if abs(fq / f_nominal - 1) > 0.05:
        return dict(bestimmbar=False, diagnose=f'Indexfrequenz {fq:.4g} Hz weicht von {f_nominal:g} Hz ab')
    w = 2 * np.pi * fq
    k = np.arange(1, K + 1)
    X = []
    for a, b in zip(idx[:-1], idx[1:]):
        s = (t >= a) & (t < b)
        th = w * (t[s] - a)
        A = np.c_[np.ones(s.sum()), np.cos(np.outer(th, k)), -np.sin(np.outer(th, k))]
        c = np.linalg.lstsq(A, x[s], rcond=None)[0]
        X.append(c[1:K + 1] + 1j * c[K + 1:])
    X = np.array(X)
    n = X.shape[0]
    Xm = X.mean(0)
    u_re, u_im = X.real.std(0, ddof=1) / np.sqrt(n), X.imag.std(0, ddof=1) / np.sqrt(n)
    return dict(bestimmbar=True, n_zyklen=int(n), f_hz=float(fq), u_f_hz=float(fq * per.std(ddof=1) / per.mean() /
                                                                                np.sqrt(n)),
                x_mess=Xm, u_x_mess_re=u_re, u_x_mess_im=u_im)


def p05_auswerten(m, K=None):
    """P0.5 (oder P0.5′): x_k, a_k mit Unsicherheit, Δδⱼ und u(Δδⱼ), G_x aus dem Datenblatt."""
    K = int(m.get('k_voll', 12) if K is None else K)
    gx = m['G_x_datenblatt']
    mods = [p05_modul(mod, float(m['f_hz']), K) for mod in m['module']]
    if not all(mo['bestimmbar'] for mo in mods):
        return dict(bestimmbar=False, module=mods, diagnose='; '.join(mo.get('diagnose', '') for mo in mods))
    fq = float(np.mean([mo['f_hz'] for mo in mods]))
    k = np.arange(1, K + 1)
    G = gx_modell(gx, k * fq)
    dg = _gx_ableitungen(gx, k * fq)
    ug = (gx['u_gain'], gx['u_tau'], gx['u_f_tp'])
    getrennt = bool(m.get('getrennte_sensoren', False))
    wk = 2 * np.pi * fq * k
    out_mod = []
    for j, mo in enumerate(mods):
        x = mo['x_mess'] / G
        # Kovarianz (Re, Im) je k: Statistik + G_x (δx = −x·Σ ∂lnG·δp)
        c_stat = np.stack([mo['u_x_mess_re'] ** 2, mo['u_x_mess_im'] ** 2], -1) / np.abs(G)[:, None] ** 2
        c_gx_re, c_gx_im, c_gx_reim = (np.zeros(K) for _ in range(3))
        for d, u in zip(dg, ug):
            v = -x * d * u
            c_gx_re += v.real ** 2
            c_gx_im += v.imag ** 2
            c_gx_reim += v.real * v.imag
        u_re = np.sqrt(c_stat[:, 0] + c_gx_re)
        u_im = np.sqrt(c_stat[:, 1] + c_gx_im)
        a = -(wk ** 2) * x
        phi1 = np.angle(x[0])
        u_arg_stat = float(np.sqrt((np.sin(phi1) * np.sqrt(c_stat[0, 0])) ** 2 + (np.cos(phi1) * np.sqrt(c_stat[0, 1]))
                                   ** 2) / abs(x[0]))
        u_arg_gx = float(np.sqrt((2 * np.pi * fq * gx['u_tau']) ** 2 + (np.imag(dg[2][0]) * gx['u_f_tp']) ** 2))
        out_mod.append(dict(modul=j + 1, n_zyklen=mo['n_zyklen'], f_hz=mo['f_hz'], x_m=x, u_x_re_m=u_re,
                            u_x_im_m=u_im, a_m_s2=a, u_a_re=wk ** 2 * u_re, u_a_im=wk ** 2 * u_im,
                            x_mess_m=mo['x_mess'], u_x_mess_re=mo['u_x_mess_re'], u_x_mess_im=mo['u_x_mess_im'],
                            arg_x1_grad=float(np.degrees(phi1)), u_arg_x1_stat_grad=float(np.degrees(u_arg_stat)),
                            u_arg_x1_gx_grad=float(np.degrees(u_arg_gx))))
    ziel = 0.1
    dd, udd = [], []
    for j in range(3):
        d = kv.wickel_grad(out_mod[0]['arg_x1_grad'] - out_mod[j]['arg_x1_grad'])
        if j == 0:
            dd.append(0.0)
            udd.append(0.0)
            continue
        u2 = out_mod[0]['u_arg_x1_stat_grad'] ** 2 + out_mod[j]['u_arg_x1_stat_grad'] ** 2
        if getrennt:                                                    # getrennte Wegkanäle: G_x-Phase je Modul
            u2 += 2 * out_mod[0]['u_arg_x1_gx_grad'] ** 2
        dd.append(float(d))
        udd.append(float(np.sqrt(u2)))
    return dict(bestimmbar=True, f_hz=fq, u_f_hz=float(np.sqrt(np.mean([mo['u_f_hz'] ** 2 for mo in mods]) / 3)),
                k_voll=K, G_x=dict(gx), getrennte_sensoren=getrennt, module=out_mod,
                delta_delta_grad=dd, u_delta_delta_grad=udd,
                anforderung_u_delta_delta=dict(grenze_grad=ziel, erfuellt=bool(max(udd) <= ziel),
                                               hinweis='prüfbare Anforderung (P0.5, Tab. F), keine Zusage'),
                parkposition='nicht im Datensatz')


# ── Kalibrierung ─────────────────────────────────────────────────────────────────────────────────────
def kalibrieren(messung, band_hz, kmax=None, f=None):
    """Alle Schritte; Rückgabe der Inhalt der Kalibrierung (Stufe 1 liest 'zellen')."""
    p01 = p01_auswerten(messung['p01'])
    p02 = p02_auswerten(messung['p02'])
    p04 = p04_auswerten(messung['p04'], p01, p02, band_hz, kmax=kmax, f=f)
    p05 = p05_auswerten(messung['p05'])
    p05s = p05_auswerten(messung['p05_strich']) if 'p05_strich' in messung else None
    zellen = []
    for c, z in enumerate(p01['zellen']):
        if not z['bestimmbar']:
            raise ValueError(f'P0.1: Kennlinie der Zelle {c + 1} nicht bestimmbar')
        zellen.append(dict(zelle=c + 1, nullpunkt_adc=z['nullpunkt_adc'], empfindlichkeit_N_je_adc=z[
            'empfindlichkeit_N_je_adc'], u_empfindlichkeit_rel=z['u_empfindlichkeit_rel'],
            kennlinie_quadratisch=z['beta_je_N'], umrechnung='linear'))
    eingang = {k: _sha_eingang(v) for k, v in messung.items()}
    return dict(version=VERSION, zellen=zellen, g=p02['g'], p0_1=p01, p0_2=p02, p0_4=p04, p0_5=p05,
                p0_5_strich=p05s, m_L=p02['m_L'],
                hinterlegung=dict(eingang_sha256=eingang,
                                  hinweis='P0.1–P0.4 vor der Auswertung von P0.8-Kraftdaten, P0.5 je Frequenz '
                                          '(§5.2); Zeitstempel nicht in der Datei (Reproduzierbarkeit)'),
                band_hz=list(band_hz))


def schreibe_kalibrierung(pfad, inhalt, kennung):
    return formate.schreibe_objekt(pfad, formate.kopf('kalibrierung', kennung, version=VERSION), inhalt)


def lies_kalibrierung(pfad):
    return formate.lies_objekt(pfad, 'kalibrierung')


def lies_p0(pfad):
    return formate.lies_objekt(pfad, 'p0_messung')


def zellanteile(p01):
    """Statische Anteile w_cj der Kraft von Modul j an Zelle c aus Zelllagen (P0.1) und Modullagen (Konstruktion)."""
    ls = p01['laststellen']
    if not ls.get('bestimmbar') or p01.get('module_nominal_m') is None:
        return None
    Z = np.c_[ls['x_m'], ls['y_m']]
    B = np.c_[np.ones(3), Z]
    return np.array([np.linalg.solve(B.T, np.r_[1.0, mp]) for mp in np.asarray(p01['module_nominal_m'])]).T


def h3_eingaenge(kal, ks=(1, 2, 3)):
    """Eingänge der H3-Vorhersage (A9.7) ausschließlich aus der Kalibrierung."""
    p01, p02, p04, p05 = kal['p0_1'], kal['p0_2'], kal['p0_4'], kal['p0_5']
    fehl = []
    if not p05.get('bestimmbar'):
        fehl.append('P0.5 nicht bestimmbar')
    if not p04['einfreiheitsgrad']['identifizierbar']:
        fehl.append('P0.4: f_n, ζ nicht identifizierbar')
    w = zellanteile(p01)
    if w is None:
        fehl.append('Zellanteile der Module (P0.1 Laststellen oder Modullagen) fehlen')
    return dict(fehlend=fehl, m_j=np.asarray(p02['m_j_kg']), u_m_j=np.asarray(p02['u_m_j_kg']),
                fn_zeta=np.array([p04['einfreiheitsgrad']['f_n_hz'], p04['einfreiheitsgrad']['zeta']]),
                kov_fn_zeta=np.asarray(p04['einfreiheitsgrad']['kovarianz_fn_zeta']), bruecke=p01['bruecke'],
                zellanteile=w, p05=p05, ks=list(ks),
                kontakt_hinweis='H(kω) aus f_n, ζ (1 FG); Kippmoden: ' + str(p04['einfreiheitsgrad_ausreichend']))
