"""AP-12 Stufe 2: Nullkontrolle (§8.8, A9.8), Zuordnung (§8.10, A9.13) und Kontrolle E3 (§8.10, A2.7, A9.13).
Keine dieser Auswertungen ändert einen Ausgang oder schließt einen Lauf aus.

Nullkontrolle: Welch-Satterthwaite-t-Test von Δ⟨N⟩ aller Kombinationsläufe der Phase 1 (gültig bis auf G1) gegen
Δ⟨N⟩ der Referenzläufe der Phase 1 (leave-one-out), zweiseitig, α = 0,05; Differenz, 95-%-Intervall, Lage zu ±ε_ctrl
mit Vermerk und genau eine der beiden Aussagen (Regel h0.sammeltest); keine Gleichheitsaussage.

Zuordnung (Regeln zuordnung.*, offen; dreiwertig nur im Entwicklungsprofil): an den Punkten I für Re/Im N₁…N₃ die
Residuen r (Haupteinstellung) und r′ (Einstellung 2) gegen (ŷ⁰, ŷ⁰′) und (ŷ¹, ŷ¹′);
χ²_p = Σ (r′ − s^p·r)²/(u′² + s^{2p}·u²), p = 0, 1, 2, m = 6·N_I Terme, gegen das 95-%-Quantil von χ²(m); Klasse p,
wenn χ²_p darunter und die beiden anderen darüber, gegen beide Vorhersagepaare dieselbe. s = Σⱼ|N̄′₁⁽ʲ⁾|/Σⱼ|N̄₁⁽ʲ⁾|
aus den Einzelmodulläufen (Regel zuordnung.s_formel, technisch). Auslöser: an einem Punkt von I ein |z⁰| > c mit
gleichsinnigem |z¹| > c.

E3 (Regeln e3.*, offen; dreiwertig nur im Entwicklungsprofil): Modulzeiger Ĉₖ = T(kω)⁻¹·(N₁,ₖ, N₂,ₖ, N₃,ₖ)ᵀ mit
T_cj = g_c·G_F,c(kω)·w_cj·H(kω) (Statik der Dreipunktlagerung aus P0.1, Kette, 1 FG; Kippmoden vernachlässigt,
gültig für k·f weit unter der Kippmode). E3a: Δφⱼ^Z = (arg Ĉ₁,₁ − arg Ĉⱼ,₁) − φ̄ⱼ^P (j = 2, 3), daneben k = 2.
E3b: q_Z = |R₋₁ − R̂₋₁|/|R̂₊₁| am Triphasik-Punkt aus der ersten Harmonischen des Kippmoments
(M_x = Σ y_c·N_c,1, M_y = −Σ x_c·N_c,1; R₊₁ = (M_x + iM_y)/2, R₋₁ = (M̄_x + iM̄_y)/2). Unsicherheit aus Bootstrap A/B,
Ziehungen von Δδⱼ (je Modul eine) und der Quantisierung der Zeitstempel (Rechteck).
"""
import numpy as np
from scipy import stats

from . import anpassung, bootstrap as bs, konventionen as kv, vorhersage as vh
from .regeln import RegelOffen


# ── Nullkontrolle ────────────────────────────────────────────────────────────────────────────────────
def nullkontrolle(dN_komb, dN_ref_loo, eps_ctrl, profil):
    x, y = np.asarray(dN_komb, float), np.asarray(dN_ref_loo, float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    if x.size < 2 or y.size < 2:
        return dict(pruefbar=False, grund='zu wenige Kombinations- oder Referenzläufe')
    d = x.mean() - y.mean()
    vx, vy = x.var(ddof=1) / x.size, y.var(ddof=1) / y.size
    se = np.sqrt(vx + vy)
    nu = (vx + vy) ** 2 / (vx ** 2 / (x.size - 1) + vy ** 2 / (y.size - 1))
    regel = profil.wert('h0.sammeltest')
    t = stats.t.ppf(1 - regel['alpha'] / 2, nu)
    L, U = d - t * se, d + t * se
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
def uebertragung(kal, f_hz, ks=(1, 2)):
    """T(kω) (k, Zelle, Modul) aus P0.1 (Zelllagen, relative Verstärkungen), Kette und 1-FG-Übertragung."""
    p01, p04 = kal['p0_1'], kal['p0_4']
    w = anpassung.zellanteile(p01)
    if w is None:
        return None
    g = np.asarray(p01['laststellen']['g'], float)
    ks = np.asarray(ks)
    G = anpassung.gf_wert(p01['bruecke'], ks * f_hz)                    # (Zelle, k)
    e = p04['einfreiheitsgrad']
    H = anpassung.h1fg(ks * f_hz, e['f_n_hz'], e['zeta'])
    return np.einsum('c,ck,cj,k->kcj', g, G, w, H)


def moment(Nz1, xy):
    """R₊₁, R₋₁ der ersten Harmonischen des Kippmoments aus den Zellzeigern (…, 3) und Zelllagen (3, 2)."""
    Mx = (Nz1 * xy[:, 1]).sum(-1)
    My = -(Nz1 * xy[:, 0]).sum(-1)
    return (Mx + 1j * My) / 2, (np.conj(Mx) + 1j * np.conj(My)) / 2


def e3_auswerten(K, E0, idxA, idxB0, T, xy, dd, u_dd, phi_mess, triphasik, profil, rng, u_quant_grad, kmax=2):
    """K: id → dict(Xz (n, 3, Kv) Zellharmonische, Z, nz); E0: Einzelmodul-Zellharmonische Phase 0 je Modul
    (n_j, 3, Kv); T: (k, Zelle, Modul); xy: Zelllagen (3, 2); dd, u_dd: Δδⱼ und u(Δδⱼ); phi_mess: id → φ̄ⱼ^P (3)."""
    T = np.asarray(T)
    kond = np.linalg.cond(T)
    if not np.all(np.isfinite(kond)) or np.any(kond > 1e12):
        return dict(status='nicht auswertbar: T(kω) singulär oder schlecht konditioniert (Zell- und Modullagen '
                           'trennen die Module nicht)', bewertung=None, kondition=np.asarray(kond).tolist())
    Tinv = np.linalg.inv(T)                                             # (k, Modul, Zelle)
    Nbar0 = np.stack([e.mean(0) for e in E0])                           # (Modul, Zelle, Kv)
    B = idxA[next(iter(idxA))].shape[0]
    zieh_dd = np.asarray(dd)[None, :] + np.asarray(u_dd)[None, :] * rng.standard_normal((B, 3))
    erg = []
    for kid, d in K.items():
        X = d['Xz'][..., :kmax]
        n = X.shape[0]
        C = bs.zaehlmatrix(idxA[kid], n)
        yb = (C @ X.reshape(n, -1)).reshape(-1, 3, kmax) / n
        rb = (C @ d['Z'][..., :kmax].reshape(n, -1)).reshape(-1, 3, kmax) / (C @ d['nz'])[:, None, None]
        y = X.mean(0)
        rho = vh.zeiger_mittel(d['Z'], d['nz'])
        Ch = np.einsum('kjc,ck->jk', Tinv, y)                           # (Modul, k)
        Chb = np.einsum('kjc,bck->bjk', Tinv, yb)
        phiP = -np.degrees(np.angle(rho[:, 0])) + np.asarray(dd)
        phiPb = -np.degrees(np.angle(rb[:, :, 0])) + zieh_dd
        res = {}
        for j in (1, 2):
            dz = kv.wickel_grad(np.degrees(np.angle(Ch[0, 0]) - np.angle(Ch[j, 0])) - phiP[j])
            dzb = kv.wickel_grad(np.degrees(np.angle(Chb[:, 0, 0]) - np.angle(Chb[:, j, 0])) - phiPb[:, j])
            d2 = kv.wickel_grad((np.degrees(np.angle(Ch[0, 1]) - np.angle(Ch[j, 1])) - 2 * phiP[j]) / 2) \
                if kmax >= 2 else None
            u = float(np.sqrt(np.var(dzb, ddof=1) + u_quant_grad ** 2))
            res[f'modul{j + 1}'] = dict(delta_phi_Z_grad=float(dz), u_grad=u,
                                        delta_phi_Z_k2_grad=None if d2 is None else float(d2))
        erg.append(dict(id=kid, e3a=res, amplitude=np.abs(Ch[:, 0]).tolist()))
    # E3b am Triphasik-Punkt
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
        Rpb, Rmb = moment(yb[..., 0], xy)
        Rphb, Rmhb = moment(yhb[..., 0], xy)
        qb = np.abs(Rmb - Rmhb) / np.abs(Rphb)
        e3b = dict(id=triphasik, q_Z=q, u_q_Z=float(np.std(qb, ddof=1)), verhaeltnis_messung=float(abs(Rm) / abs(Rp)),
                   verhaeltnis_vorhersage=float(abs(Rmh) / abs(Rph)))
    out = dict(e3a=erg, e3b=e3b, T_hinweis='T aus Statik (P0.1), Kette und 1 FG; Kippmoden vernachlässigt')
    try:
        sw = profil.wert('e3.schwellen')
        profil.wert('e3.pruefzahl')
    except RegelOffen as e:
        out['status'] = f'nur beschreibend: {e.grund}'
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
