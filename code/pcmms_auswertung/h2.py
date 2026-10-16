"""AP-12 Stufe 2: H2 (Lage der Zeltspitze) nach Präreg §3, §8.6, §9.3 und A9.6.

Fitfenster W aus der Vorhersage an den Sollphasen (Teil B nr6; Mittelpunkt Regel h2.mittelpunkt, Halbbreite
h2.w_grad, am Schnittrand abgeschnitten; weniger als zwei Punkte auf einer Seite: nicht entscheidbar, Datenlage).
Abszisse φ̄₂^P = −arg ρ₂₁ + Δδ₂, Ordinate F_min − ⟨N⟩ der Konfigurationsmittelkurve (k ≤ k_max) bzw. der Vorhersage
ŷ⁰, ŷ¹ mit den gemessenen Zeigern. Je Replikat b (B = 10 000) die Zeilen b von A_i (i ∈ W), B⁰ⱼ und B¹ⱼ gemeinsam:
Abszissen und ρ neu, drei Zeltfits (Messung, ŷ⁰, ŷ¹), Δφ* = φ₂* − φ̂₂*. Intervalle: Perzentil (95 %), BCa (Jackknife
über alle Läufe von W und alle Einzelmodulläufe), Perzentil mit Niveau 0,96 … 0,99; welcher Typ gilt, bestimmt die
Kalibriersimulation (Teil B nr10, Überdeckung ≥ 0,936). Entscheidung mit Äquivalenzlogik: bestätigt, wenn [a⁰, b⁰] und
[a¹, b¹] in ±δ_H2; falsifiziert, wenn beide auf derselben Seite außerhalb; sonst nicht entscheidbar.
Quantile: numpy „linear“ (Regel h2.quantil, technisch).
"""
import numpy as np
from scipy import stats

from . import bootstrap as bs, konventionen as kv, vorhersage as vh, zeltfit as zfit
from .regeln import RegelOffen

NIVEAUS = (0.96, 0.97, 0.98, 0.99)


def fenster(F_vor, phi2, profil):
    """Mittelpunkt und W aus der Vorhersage an den Sollphasen (F_vor über den 21 Schnittpunkten)."""
    mp = profil.wert('h2.mittelpunkt')
    w = float(profil.wert('h2.w_grad'))
    F_vor, phi2 = np.asarray(F_vor, float), np.asarray(phi2, float)
    if mp != 'i':
        raise RegelOffen(profil.regeln['h2.mittelpunkt'])
    imax = int(np.flatnonzero(F_vor == F_vor.max())[0])                 # bei Gleichstand der kleinere
    mitte = phi2[imax]
    W = [i for i in range(phi2.size) if abs(phi2[i] - mitte) <= w + 1e-9]
    links = sum(phi2[i] < mitte for i in W)
    rechts = sum(phi2[i] > mitte for i in W)
    return dict(mitte_index=imax, mitte_grad=float(mitte), w_grad=w, W=W, links=int(links), rechts=int(rechts),
                ausreichend=bool(links >= 2 and rechts >= 2))


def _perzentil(x, niveau):
    return [float(np.quantile(x, (1 - niveau) / 2)), float(np.quantile(x, (1 + niveau) / 2))]


def _bca(x, theta, jack, niveau=0.95):
    """BCa-Intervall: z₀ aus dem Anteil der Replikate unter θ̂ (Gleichstände zur Hälfte), a aus dem Jackknife."""
    B = x.size
    p = (np.sum(x < theta) + 0.5 * np.sum(x == theta)) / B
    if p <= 0 or p >= 1:
        return None
    z0 = stats.norm.ppf(p)
    jm = jack.mean()
    d = jm - jack
    nenner = 6 * (np.sum(d ** 2)) ** 1.5
    a = float(np.sum(d ** 3) / nenner) if nenner > 0 else 0.0
    za = stats.norm.ppf([(1 - niveau) / 2, (1 + niveau) / 2])
    q = stats.norm.cdf(z0 + (z0 + za) / (1 - a * (z0 + za)))
    return [float(np.quantile(x, q[0])), float(np.quantile(x, q[1]))]


def _fits(phiP, Fm, F0, F1):
    r = zfit.zeltfit(phiP, Fm)['phi_stern']
    r0 = zfit.zeltfit(phiP, F0)['phi_stern']
    r1 = zfit.zeltfit(phiP, F1)['phi_stern']
    return r, r0, r1


def punktwerte(K, S, kmax, dd2):
    """Abszissen und Ordinaten für die Konfigurationen K (Liste dicts mit Nk (n, K), Z (n, 3, K), nz) und die
    Einzelmodulbasis S (Nbar0, Nbar1: (Modul, K))."""
    phiP, Fm, F0, F1 = [], [], [], []
    for d in K:
        rho = vh.zeiger_mittel(d['Z'], d['nz'])
        phiP.append(vh.profilphase2(rho, [0, dd2, 0]))
        Fm.append(vh.fmin_rel_viele(d['Nk'].mean(0)[:kmax]))
        F0.append(vh.fmin_rel_viele(vh.vorhersage(S['Nbar0'][:, :kmax], rho[:, :kmax])))
        F1.append(vh.fmin_rel_viele(vh.vorhersage(S['Nbar1'][:, :kmax], rho[:, :kmax])))
    return np.array(phiP), np.array(Fm), np.array(F0), np.array(F1)


def replikate(K, E0, E1, idxA, idxB0, idxB1, kmax, dd2, block=1000):
    """Δφ*⁰ und Δφ*¹ je Replikat (gemeinsame Zeilen aller Quellen)."""
    B = idxA[0].shape[0]
    d0, d1, phm = [], [], []
    for s0 in range(0, B, block):
        sl = slice(s0, s0 + block)
        Nb0 = np.stack([(bs.zaehlmatrix(idxB0[j][sl], E0[j].shape[0]) @ E0[j][:, :kmax]) / E0[j].shape[0]
                        for j in range(3)], 1)                           # (b, Modul, K)
        Nb1 = np.stack([(bs.zaehlmatrix(idxB1[j][sl], E1[j].shape[0]) @ E1[j][:, :kmax]) / E1[j].shape[0]
                        for j in range(3)], 1)
        P, Fm, F0, F1 = [], [], [], []
        for d, ia in zip(K, idxA):
            n = d['Nk'].shape[0]
            C = bs.zaehlmatrix(ia[sl], n)
            yb = (C @ d['Nk'][:, :kmax]) / n
            rb = (C @ d['Z'][..., :kmax].reshape(n, -1)).reshape(-1, 3, kmax) / (C @ d['nz'])[:, None, None]
            P.append(vh.profilphase2(rb, [0, dd2, 0]))
            Fm.append(vh.fmin_rel_viele(yb))
            F0.append(vh.fmin_rel_viele(np.einsum('bjk,bjk->bk', Nb0, rb)))
            F1.append(vh.fmin_rel_viele(np.einsum('bjk,bjk->bk', Nb1, rb)))
        P, Fm, F0, F1 = (np.stack(x, 1) for x in (P, Fm, F0, F1))
        r, r0, r1 = _fits(P, Fm, F0, F1)
        d0.append(r - r0)
        d1.append(r - r1)
        phm.append(r)
    return np.concatenate(d0), np.concatenate(d1), np.concatenate(phm)


def jackknife(K, E0, E1, kmax, dd2):
    """Δφ*⁰, Δφ*¹ mit je einem weggelassenen Lauf (alle Läufe von W, dann alle Einzelmodulläufe der Phasen 0 und 1),
    vektorisiert: ein weggelassener Konfigurationslauf ändert nur den Punkt seiner Konfiguration, ein weggelassener
    Einzelmodullauf nur die Ordinaten der jeweiligen Vorhersage."""
    S0 = np.stack([e[:, :kmax].mean(0) for e in E0])
    S1 = np.stack([e[:, :kmax].mean(0) for e in E1])
    P, Fm, F0, F1 = punktwerte(K, dict(Nbar0=S0, Nbar1=S1), kmax, dd2)
    rho = [vh.zeiger_mittel(d['Z'], d['nz'])[:, :kmax] for d in K]
    zeilen = []                                                         # je Fall (P, Fm, F0, F1) über W
    for i, d in enumerate(K):
        n = d['Nk'].shape[0]
        X = d['Nk'][:, :kmax]
        Z = d['Z'][..., :kmax]
        nz = np.asarray(d['nz'], float)
        y = (X.sum(0)[None] - X) / (n - 1)                               # (n, K)
        r = (Z.sum(0)[None] - Z) / (nz.sum() - nz)[:, None, None]         # (n, 3, K)
        Pi = vh.profilphase2(r, [0, dd2, 0])
        Fmi = vh.fmin_rel_viele(y)
        F0i = vh.fmin_rel_viele(np.einsum('jk,njk->nk', S0, r))
        F1i = vh.fmin_rel_viele(np.einsum('jk,njk->nk', S1, r))
        for l in range(n):
            pp, fm, f0, f1 = P.copy(), Fm.copy(), F0.copy(), F1.copy()
            pp[i], fm[i], f0[i], f1[i] = Pi[l], Fmi[l], F0i[l], F1i[l]
            zeilen.append((pp, fm, f0, f1))
    rho = np.stack(rho)                                                 # (W, 3, K)
    for welche, (S, E) in enumerate(((S0, E0), (S1, E1))):
        for j in range(3):
            Ej = E[j][:, :kmax]
            nj = Ej.shape[0]
            Sj = (S[j][None] * nj - Ej) / (nj - 1)                        # (nj, K)
            Sn = np.repeat(S[None], nj, 0)
            Sn[:, j] = Sj
            Fn = vh.fmin_rel_viele(np.einsum('njk,wjk->nwk', Sn, rho))    # (nj, W)
            for l in range(nj):
                if welche == 0:
                    zeilen.append((P, Fm, Fn[l], F1))
                else:
                    zeilen.append((P, Fm, F0, Fn[l]))
    PP, FM, FF0, FF1 = (np.array([z[q] for z in zeilen]) for q in range(4))
    r, r0, r1 = _fits(PP, FM, FF0, FF1)
    return r - r0, r - r1


def entscheiden(iv0, iv1, delta):
    a0, b0 = iv0
    a1, b1 = iv1
    if -delta <= a0 and b0 <= delta and -delta <= a1 and b1 <= delta:
        return 'bestätigt'
    if (a0 > delta and a1 > delta) or (b0 < -delta and b1 < -delta):
        return 'falsifiziert'
    return 'nicht entscheidbar'


def h2_auswerten(K, E0, E1, idxA, idxB0, idxB1, kmax, dd2, profil, intervall, W_info, sperren=(),
                 bca_berechnen=True):
    """K: Konfigurationen von W (in Schnittreihenfolge); E0/E1: Einzelmodul-Summenharmonische je Modul;
    intervall: Teil B nr10 (typ, niveau, ueberdeckung, quelle) oder None; sperren: Gründe der Datenlage."""
    S = dict(Nbar0=np.stack([e.mean(0) for e in E0]), Nbar1=np.stack([e.mean(0) for e in E1]))
    P, Fm, F0, F1 = punktwerte(K, S, kmax, dd2)
    r, r0, r1 = _fits(P[None], Fm[None], F0[None], F1[None])
    th0, th1 = float(r[0] - r0[0]), float(r[0] - r1[0])
    d0, d1, phm = replikate(K, E0, E1, idxA, idxB0, idxB1, kmax, dd2)
    iv = {'perzentil_0.95': (_perzentil(d0, 0.95), _perzentil(d1, 0.95))}
    for nv in NIVEAUS:
        iv[f'perzentil_{nv:.2f}'] = (_perzentil(d0, nv), _perzentil(d1, nv))
    jack = None
    if bca_berechnen:
        j0, j1 = jackknife(K, E0, E1, kmax, dd2)
        b0, b1 = _bca(d0, th0, j0), _bca(d1, th1, j1)
        iv['bca_0.95'] = (b0, b1)
        jack = dict(n=int(j0.size))
    out = dict(phi_stern_messung=float(r[0]), phi_stern_yhat0=float(r0[0]), phi_stern_yhat1=float(r1[0]),
               delta_phi0=th0, delta_phi1=th1, abszissen=P.tolist(), F_messung=Fm.tolist(), F_yhat0=F0.tolist(),
               F_yhat1=F1.tolist(), W=W_info, intervalle={k: dict(yhat0=v[0], yhat1=v[1]) for k, v in iv.items()},
               B=int(d0.size), punktmasse0=float(np.mean(d0 == th0)), punktmasse1=float(np.mean(d1 == th1)),
               jackknife=jack)
    gruende = list(sperren)
    try:
        delta = float(profil.wert('h2.delta_grad'))
    except RegelOffen as e:
        delta = None
        gruende.append(('Verfahren', e.grund))
    if intervall is None:
        gruende.append(('Verfahren', 'Intervalltyp nicht kalibriert (Teil B nr10 fehlt)'))
        gewaehlt = None
    else:
        typ, nv = intervall['typ'], float(intervall.get('niveau', 0.95))
        schl = f'{typ}_{nv:.2f}'
        if typ == 'keiner':
            gruende.append(('Verfahren', 'kein Intervall erreicht die Überdeckung 0,936'))
            gewaehlt = None
        elif schl not in iv or iv[schl][0] is None or iv[schl][1] is None:
            gruende.append(('Verfahren', f'Intervall {schl} nicht bestimmbar'))
            gewaehlt = None
        else:
            gewaehlt = schl
    out['intervall_gewaehlt'] = gewaehlt
    out['intervall_herkunft'] = intervall
    if gruende:
        ausgang = 'nicht entscheidbar'
    else:
        ausgang = entscheiden(iv[gewaehlt][0], iv[gewaehlt][1], delta)
    zus = []
    if gewaehlt is not None:
        (a0, b0_), (a1, b1_) = iv[gewaehlt]
        if (a0 > 0 and a1 > 0) or (b0_ < 0 and b1_ < 0):
            txt = profil.wert('h1.zusaetze')
            zus.append(txt['bestaetigt'] if ausgang == 'bestätigt' else txt['nicht_entscheidbar']
                       if ausgang == 'nicht entscheidbar' else 'Abweichung nachgewiesen')
    if ausgang == 'nicht entscheidbar' and not gruende:
        gruende.append(('Präzision' if gewaehlt and max(np.diff(iv[gewaehlt][0])[0], np.diff(iv[gewaehlt][1])[0])
                        > 2 * delta else 'Graubereich', 'Intervall nicht in ±δ_H2 und nicht außerhalb'))
    rang = ['Datenlage', 'Verfahren', 'Drift', 'Graubereich', 'Präzision']
    klassen = sorted({k for k, _ in gruende}, key=rang.index)
    try:
        profil.wert('h2.drift_zusatz')
        drift_hinweis = None
    except RegelOffen as e:
        drift_hinweis = f'Drift-Zusatz bei H2 nicht definiert ({e.grund})'
    out.update(ausgang=ausgang, grund=klassen[0] if (ausgang == 'nicht entscheidbar' and klassen) else None,
               gruende=[dict(klasse=k, text=t) for k, t in gruende], zusaetze=zus, delta_H2=delta,
               drift_hinweis=drift_hinweis)
    return out
