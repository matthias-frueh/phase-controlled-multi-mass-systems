"""Gegenproben gegen die unabhängige Referenz (Plan AP-13, Abschnitt 2.6 e; Auftrag Etappe 4/5).

h1_abgleich: Produktion (h1, bootstrap, vorhersage) gegen referenz.h1_referenz mit denselben Bootstrap-Indizes;
Toleranzen nach Plan 2.6 e: Kräfte und Residuen 10⁻⁹ N + 10⁻⁹·|Wert|, u 10⁻¹² N + 10⁻⁹·u, z 10⁻⁷ + 10⁻⁹·|z|,
ν relativ 10⁻⁹; Ausgang, TOST, Relevanz, Zusatz und Drift identisch.
zeltfit_vergleich: schnelles Kandidatenverfahren gegen das unabhängig geschriebene Vollraster auf einem Vergleichssatz
(asymmetrisches und symmetrisches Zelt, verrauschte Kurven, reines Rauschen, Gerade); gleich, Gleichstand innerhalb
der Toleranzregel oder abweichend; Laufzeit beider Verfahren (maschinenabhängig, keine Abnahmeschwelle).
"""
import time

import numpy as np

from .. import auswertung, zeltfit as zfit
from ..referenz import h1_referenz, zeltfit_referenz

TOLERANZ = dict(r=(1e-9, 1e-9), u=(1e-12, 1e-9), z=(1e-7, 1e-9), nu=(0.0, 1e-9))


def referenz_eingabe(r, B, seed):
    """Gültige Läufe aus dem Ergebnis einer Kette, dieselben Indexmatrizen für Produktion und Referenz."""
    e, tb, tab = r['ergebnis'], r['teil_b'], r['tabelle']
    t1 = tab.auswahl(tab.spalte('phase', int) == 1).sortiert()
    ungueltig = set(e['gueltigkeit']['gruende'])
    schnitt = [c['id'] for c in tb['nr2']['konfigurationen'] if c['gruppe'] == 'schnitt']

    def sel(pr):
        return sorted([i for i, k in enumerate(t1.koepfe) if pr(k) and k['lauf_id'] not in ungueltig],
                      key=lambda i: t1.koepfe[i]['position'])
    lauf = {kid: sel(lambda k, kid=kid: k['laufart'] == 'K' and k['konfiguration']['id'] == kid) for kid in schnitt}
    ctr = [sel(lambda k, j=j: k['laufart'] == 'L' and k['modul'] == j and k['einstellung'] == 1) for j in (1, 2, 3)]
    rng = np.random.default_rng(seed)
    idx = {f'A/{k}': rng.integers(0, len(v), size=(B, len(v))) for k, v in lauf.items()}
    idx.update({f'B1/modul{j + 1}': rng.integers(0, len(ctr[j]), size=(B, len(ctr[j]))) for j in range(3)})
    E0 = [np.asarray(x['Nk_zellen']).sum(1) for x in tb['nr3']['einzel0']]
    d = t1.daten
    ein = dict(kmax=tb['nr2']['k_max'], punkte=schnitt,
               laeufe={k: dict(Nk=d['Nk_summe'][v], zeiger=d['zeiger'][v], nz=np.array(
                   [t1.koepfe[i]['n_zyklen'] for i in v])) for k, v in lauf.items()},
               einzel0=E0, einzel1=[d['Nk_summe'][c] for c in ctr], bias0=np.asarray(tb['nr4']['bias0']),
               bias1=np.asarray(tb['nr4']['bias1']), u_bias0=np.asarray(tb['nr4']['u_bias0']),
               u_bias1=np.asarray(tb['nr4']['u_bias1']), Delta=np.asarray(tb['nr4']['Delta']),
               Delta_rel=np.asarray(tb['nr4']['Delta_rel']), c=tb['nr10']['c_H1'],
               indizes={**idx, **{k: np.asarray(v)[:B] for k, v in tb['nr3']['indizes'].items() if k.startswith('B0/')}})
    return ein, idx


def _abw(a, b, atol, rtol):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    gleich_nan = bool(np.array_equal(np.isfinite(a), np.isfinite(b)))
    if not ok.any():
        return dict(max_abs=0.0, innerhalb=gleich_nan)
    d = np.abs(a[ok] - b[ok])
    return dict(max_abs=float(d.max()), innerhalb=bool(gleich_nan and np.all(d <= atol + rtol * np.abs(b[ok]))))


def h1_abgleich(r, profil, B=150, seed=99):
    """Abgleich einer Kampagne (Ergebnis von harness.kette.kette) mit der Referenz. B ist höchstens die Zahl der festen
    B⁰-Replikate in Teil B."""
    B = min(int(B), min(np.asarray(v).shape[0] for v in r['teil_b']['nr3']['indizes'].values()))
    ein, idx = referenz_eingabe(r, B, seed)
    e = auswertung.auswerten(r['tabelle'], r['kalibrierung'], r['teil_b'], profil, bootstrap_indizes=idx)
    ref = h1_referenz.h1_referenz(ein)
    out = {}
    for p, T in (('0', e['H1']['tests0']), ('1', e['H1']['tests1'])):
        for g, (atol, rtol) in TOLERANZ.items():
            out[f'{g}{p}'] = _abw(T[g], ref[g + p], atol, rtol)
    gleich = dict(tost0=bool(np.array_equal(e['H1']['tost0'], ref['tost0'])),
                  tost1=bool(np.array_equal(e['H1']['tost1'], ref['tost1'])),
                  relevant=bool(np.array_equal(e['H1']['relevant'], ref['relevant'])),
                  ausgang=e['H1']['ausgang'].replace('ä', 'ae') == ref['ausgang'],
                  abweichung=e['H1']['abweichung_nachgewiesen'] == ref['abweichung_nachgewiesen'],
                  drift=e['H1']['drift'] == ref['drift'])
    return dict(werte=out, gleich=gleich, B=B, ausgang=e['H1']['ausgang'],
                alle_innerhalb=bool(all(v['innerhalb'] for v in out.values()) and all(gleich.values())))


def zeltfit_testsatz(rng, n_fits):
    """Vergleichssatz: asymmetrisches und symmetrisches Zelt, verrauschte Kurven, reines Rauschen, Gerade; Fenster
    6°, 8° und 20° (7, 9, 21 Punkte), Abszissen mit Messrauschen."""
    faelle = []
    arten = ('asymmetrisch', 'symmetrisch', 'verrauscht', 'rauschen', 'gerade')
    for i in range(n_fits):
        art = arten[i % 5]
        n = (7, 9, 21)[(i // 5) % 3]
        phi = 120 - (n - 1) + 2 * np.arange(n) + 0.01 * rng.standard_normal(n)
        spitze = 120 + rng.uniform(-1.5, 1.5)
        if art == 'asymmetrisch':
            F = np.where(phi <= spitze, 0.044 * (phi - spitze), -0.031 * (phi - spitze))
        elif art == 'symmetrisch':
            F = -0.04 * np.abs(phi - spitze)
        elif art == 'verrauscht':
            F = -0.04 * np.abs(phi - spitze) + 0.004 * rng.standard_normal(n)
        elif art == 'rauschen':
            F = 0.01 * rng.standard_normal(n)
        else:
            F = 0.3 + 0.01 * phi
        faelle.append((art, phi, F))
    return faelle


def zeltfit_vergleich(n_fits, seed=5):
    rng = np.random.default_rng(seed)
    faelle = zeltfit_testsatz(rng, n_fits)
    gleich = gleichstand = 0
    abweichung = []
    je_art = {}
    t_k = t_v = 0.0
    for art, phi, F in faelle:
        t = time.perf_counter()
        k = zfit.zeltfit(phi[None], F[None])
        t_k += time.perf_counter() - t
        t = time.perf_counter()
        v = zeltfit_referenz.zeltfit_vollraster(phi, F)
        t_v += time.perf_counter() - t
        je_art.setdefault(art, [0, 0, 0])
        if abs(k['phi_stern'][0] - v['phi_stern']) < 1e-9:
            gleich += 1
            je_art[art][0] += 1
            continue
        rk, rv = zfit.rss_exakt(phi, F, k['phi_stern'][0]), zfit.rss_exakt(phi, F, v['phi_stern'])
        sst = float(((F - F.mean()) ** 2).sum())
        tol = 1e-9 * max(rk, rv) + 1e-12 * sst + 1e-28 * F.size * float((F ** 2).max())
        if abs(rk - rv) <= tol:
            gleichstand += 1
            je_art[art][1] += 1
        else:
            je_art[art][2] += 1
            abweichung.append((art, phi.size, k['phi_stern'][0], v['phi_stern'], rk, rv))
    return dict(n=n_fits, gleich=gleich, gleichstand=gleichstand, abweichung=abweichung, t_kandidat=t_k,
                t_vollraster=t_v, je_art={a: dict(gleich=x[0], gleichstand=x[1], abweichend=x[2])
                                          for a, x in je_art.items()}, seed=seed)
