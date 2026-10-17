"""AP-12 Stufe 2: H3 (1-FG-Kontaktmodell, Fassung K) nach Präreg §3, §8.5, §8.7, §9.3 und A9.7.

Vorhersage N̂_k⁽ʲ⁾ = G_F,Σ⁽ʲ⁾(kω)·m_j·H(kω)·a_k⁽ʲ⁾ ausschließlich aus der Kalibrierung (AP-11): H(ω) aus f_n, ζ (1 FG,
H hängt nicht von M ab), G_F,Σ⁽ʲ⁾ = Σ_c w_cj·G_F,c mit den statischen Anteilen w_cj von Modul j an Zelle c (P0.1),
a_k = −(kω)²·x_k,mess/G_x(kω) (P0.5), m_j (P0.2). Monte Carlo mit 10 000 Ziehungen (normativ) aus den Kovarianzen
von (f_n, ζ), der Kette, x_k,mess, G_x, m_j und f; Vorhersage und u(ŷ) sind Mittel und Standardabweichung von Real-
und Imaginärteil (ν = ∞). Die statischen Anteile w_cj gehen ohne Ziehung ein (Entwicklungsvereinfachung).
Messung: Mittel der gültigen Phase-1-Kontrollläufe Lⱼ (k = 1 … 3), Var_A aus Bootstrap B¹ⱼ; ν_eff = (n_A − 1)·u⁴/Var_A².
PB3: [r ± t(0,95; ν)·u] ⊂ ±δ_H3·|N̂| für alle 18 Tests, je Modul ≥ n_min gültige Kontrollläufe; falsifiziert, wenn an
einem Test |r| − c·u > Relevanzgrenze (c = t(1 − 0,05/36; ν_eff)); Zusatz bei |z| > c. Eine Harmonische prüft den
Kontakt nur, wenn |N̂ − G_F·m_j·a_k| > δ_H3·|N̂|; sonst prüft H3 Masse, Profil und Kalibrierung (Fassung K).
"""
import numpy as np
from scipy import stats

from . import anpassung, bootstrap as bs
from .regeln import RegelOffen


def vorhersage_mc(eing, f_hz, u_f_hz, rng, n, ks=(1, 2, 3)):
    """MC-Fortpflanzung (A9.7). eing: anpassung.h3_eingaenge(kal). Rückgabe dict mit N_hat (3, k), u_re, u_im,
    starr (G_F·m·a ohne H), kontaktanteil |H − 1|/|H|."""
    ks = np.asarray(ks)
    p05 = eing['p05']
    gx = p05['G_x']
    getrennt = p05['getrennte_sensoren']
    m = eing['m_j'][None, :] + eing['u_m_j'][None, :] * rng.standard_normal((n, 3))
    fz = rng.multivariate_normal(eing['fn_zeta'], eing['kov_fn_zeta'], size=n)
    f = f_hz + u_f_hz * rng.standard_normal(n)
    fk = f[:, None] * ks[None, :]                                        # (n, k)
    H = anpassung.h1fg(fk, fz[:, :1], fz[:, 1:2])
    # Kette je Zelle
    Gc = np.empty((n, 3, ks.size), complex)
    for c, b in enumerate(eing['bruecke']):
        P = rng.multivariate_normal(b['p'], b['kovarianz'], size=n)
        P[:, 2] = np.abs(P[:, 2])
        Gc[:, c] = P[:, :1] * np.exp(-2j * np.pi * fk * P[:, 1:2]) / (1 + 1j * fk * P[:, 2:3])
    w = eing['zellanteile']                                              # (Zelle, Modul)
    Gs = np.einsum('cj,nck->njk', w, Gc)                                 # (n, Modul, k)
    # Profil: x_mess mit Streuung, G_x mit Datenblattunsicherheit
    nsens = 3 if getrennt else 1
    gain = gx['gain'] + gx['u_gain'] * rng.standard_normal((n, nsens))
    tau = gx['tau'] + gx['u_tau'] * rng.standard_normal((n, nsens))
    ftp = gx['f_tp'] + gx['u_f_tp'] * rng.standard_normal((n, nsens))
    a = np.empty((n, 3, ks.size), complex)
    for j, mod in enumerate(p05['module']):
        xm = mod['x_mess_m'][ks - 1]
        x = xm[None] + (mod['u_x_mess_re'][ks - 1][None] * rng.standard_normal((n, ks.size)) +
                        1j * mod['u_x_mess_im'][ks - 1][None] * rng.standard_normal((n, ks.size)))
        s = j if getrennt else 0
        Gx = gain[:, s:s + 1] * np.exp(-2j * np.pi * fk * tau[:, s:s + 1]) / (1 + 1j * fk / ftp[:, s:s + 1])
        a[:, j] = -(2 * np.pi * fk) ** 2 * x / Gx
    N = Gs * m[:, :, None] * H[:, None, :] * a
    starr = Gs * m[:, :, None] * a
    return dict(N_hat=N.mean(0), u_re=N.real.std(0, ddof=1), u_im=N.imag.std(0, ddof=1), starr=starr.mean(0),
                kontaktanteil=np.abs(H - 1).mean(0) / np.abs(H).mean(0), n_mc=int(n), ks=ks.tolist())


def h3_auswerten(L1, idxB1, vor, profil, n_min):
    """L1: Liste je Modul der Summenharmonischen gültiger Phase-1-Kontrollläufe (n_j, K); idxB1: Indexmatrizen;
    vor: vorhersage_mc; n_min aus Teil B."""
    ks = np.asarray(vor['ks'])
    gruende = []
    try:
        delta = float(profil.wert('h3.delta'))
        relevanz = profil.wert('h3.relevanz')
        fassung = profil.wert('h3.fassung')
    except RegelOffen as e:
        delta = relevanz = fassung = None
        gruende.append(('Verfahren', e.grund))
    if fassung not in (None, 'K'):
        raise RegelOffen(profil.regeln['ni.fassung_I'])
    mH = profil.wert('h3.m')
    tests = []
    for j in range(3):
        nA = L1[j].shape[0]
        if nA < max(n_min, 2):
            gruende.append(('Datenlage', f'Modul {j + 1}: {nA} < n_min = {n_min} gültige Kontrollläufe'))
        y = L1[j][:, ks - 1].mean(0) if nA else np.full(ks.size, np.nan + 0j)
        if nA >= 2:
            C = bs.zaehlmatrix(idxB1[j], nA)
            yb = (C @ L1[j][:, ks - 1]) / nA
            vA = np.stack([yb.real.var(0, ddof=1), yb.imag.var(0, ddof=1)], -1)
        else:
            vA = np.full((ks.size, 2), np.nan)
        for kk in range(ks.size):
            Nh = vor['N_hat'][j, kk]
            for q, (wert, mess, uv) in enumerate(((Nh.real, y[kk].real, vor['u_re'][j, kk]),
                                                  (Nh.imag, y[kk].imag, vor['u_im'][j, kk]))):
                r = mess - wert
                u = np.sqrt(vA[kk, q] + uv ** 2)
                nu = (nA - 1) * u ** 4 / vA[kk, q] ** 2 if vA[kk, q] > 0 else np.inf
                teq = stats.t.ppf(0.95, nu) if np.isfinite(nu) else stats.norm.ppf(0.95)
                c = stats.t.ppf(1 - 0.05 / (2 * mH), nu) if np.isfinite(nu) else stats.norm.ppf(1 - 0.05 / (2 * mH))
                D = None if delta is None else delta * abs(Nh)
                tests.append(dict(modul=j + 1, k=int(ks[kk]), teil='Re' if q == 0 else 'Im', vorhersage=float(wert),
                                  u_vorhersage=float(uv), messung=float(mess), r=float(r), u=float(u), nu=float(nu),
                                  z=float(r / u) if u > 0 else float('nan'), t_eq=float(teq), c=float(c),
                                  Delta=None if D is None else float(D),
                                  pb3=None if D is None else bool(r - teq * u >= -D and r + teq * u <= D),
                                  relevant=None if D is None else bool(abs(r) - c * u > D)))
    # Kontaktprüfung je Harmonischer (Teil B Nr. 7)
    kontakt = []
    for j in range(3):
        for kk in range(ks.size):
            Nh = vor['N_hat'][j, kk]
            abst = abs(Nh - vor['starr'][j, kk])
            kontakt.append(dict(modul=j + 1, k=int(ks[kk]), abstand_N=float(abst),
                                kontaktanteil=float(vor['kontaktanteil'][kk]),
                                prueft_kontakt=None if delta is None else bool(abst > delta * abs(Nh))))
    if any(k for k, _ in gruende if k in ('Verfahren', 'Datenlage')):
        ausgang = 'nicht entscheidbar'
    elif any(t['relevant'] for t in tests):
        ausgang = 'falsifiziert'
    elif all(t['pb3'] for t in tests):
        ausgang = 'bestätigt'
    else:
        ausgang = 'nicht entscheidbar'
        weit = any(t['t_eq'] * t['u'] >= t['Delta'] for t in tests if not t['pb3'])
        gruende.append(('Präzision' if weit else 'Graubereich', 'PB3 nicht für alle 18 Tests erfüllt'))
    zus = []
    if any(abs(t['z']) > t['c'] for t in tests if np.isfinite(t['z'])):
        txt = profil.wert('h1.zusaetze')
        zus.append(txt['bestaetigt'] if ausgang == 'bestätigt' else txt['nicht_entscheidbar']
                   if ausgang == 'nicht entscheidbar' else 'Abweichung nachgewiesen')
    pk = [k for k in kontakt if k['prueft_kontakt']]
    kennz = ('Fassung K: H3 prüft Masse, Profil und Kalibrierung; keine Harmonische k ≤ 3 prüft den Kontakt'
             if not pk else 'Fassung K: den Kontakt prüfen nur ' + ', '.join(f'Modul {k["modul"]} k = {k["k"]}'
                                                                              for k in pk))
    rang = ['Datenlage', 'Verfahren', 'Drift', 'Graubereich', 'Präzision']
    klassen = sorted({k for k, _ in gruende}, key=rang.index)
    return dict(ausgang=ausgang, grund=klassen[0] if (ausgang == 'nicht entscheidbar' and klassen) else None,
                gruende=[dict(klasse=k, text=t) for k, t in gruende], zusaetze=zus, tests=tests, kontakt=kontakt,
                kennzeichnung=kennz, delta_H3=delta, relevanz=relevanz, fassung=fassung, n_mc=vor['n_mc'],
                hinweis='Eine Bestätigung mit ±10 % ist keine Bestätigung des Kontaktgesetzes oder -modells (§8.7)')
