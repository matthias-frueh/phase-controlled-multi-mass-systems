"""Kalibrier- und Prüfsimulation von Werkzeug 8 (Präreg §5.4, §8.3, §8.4, §8.6, A9.5, A9.11; Plan AP-13 1.2, 2.4, 2.5).

Reihenfolge (Plan 1.2, Betriebsart „geplant“, hier bei gegebener Laufzahl):
  1. Kalibriersimulation (Rolle kalibrierung_c): Kampagnen mit exakter Superposition, ausgewertet von AP-12 mit
     Teil B ohne Rauschbias (b̂ = 0) und Platzhalter-c; z hängt nicht von c ab.
  2. Rauschbias b̂_i⁰, b̂_i¹ (F_min − ⟨N⟩, Summe und je Zelle) als Mittel der Rohresiduen; u(b̂) aus dem MC-Fehler und
     bei mehreren Rauschvarianten der halben Spannweite (Rechteck, /√3) (Regel h1.bias_u).
  3. c (H1) = 95-%-Quantil von max_{i,q}|z⁰_iq| über die 147 Tests mit derselben Biaskorrektur; c (H1Z) ebenso über
     441 Tests. Bootstrap-Standardfehler des Quantils über die Kampagnen. Gewertet werden Kampagnen mit allen Tests.
  4. Überdeckung der H2-Intervalle jedes Typs gegen den Bezugswert (Regel h2.ueberdeckung_bezug) und Wahl des Typs
     nach der Rückfallkette (Regel h2.intervallkette): Perzentil, BCa, Perzentil 0,96 … 0,99, sonst keiner.
  5. Prüfsimulation (Rolle pruefung_c, unabhängige Seeds) mit den kalibrierten Werten in Teil B: Anteil der
     Kampagnen mit mindestens einem |z⁰| > c; über 0,069 gilt das Quantil aus beiden Simulationen (Poolen).
  6. Gemeinsame Bestätigungswahrscheinlichkeit P(H1 und H2 bestätigt | exakt) in der Prüfsimulation mit den
     endgültigen Werten (nach einem Poolen neu ausgewertet). Sie ist eine andere Größe als die Überdeckung.

Weniger Kampagnen als normativ (1000 je Simulation) sind Entwicklungsdiagnostik; das steht am Ergebnis und in der
Herkunft der Werte für Teil B. Eine Kalibrierung „bestanden“ gibt es hier nicht.
"""
import warnings

import numpy as np
from scipy import stats

from .. import formate, konventionen as kv, regeln as rg, zeltfit
from . import kampagnen as kpn, metriken


def _z(r, v, bias, u_bias):
    r = np.array(r, float)
    v = np.array(v, float)
    r[..., 0] = r[..., 0] - bias
    v[..., 0] = v[..., 0] + np.asarray(u_bias, float) ** 2
    with np.errstate(divide='ignore', invalid='ignore'):
        return r / np.sqrt(v)


def rauschbias(laeufe, feld='r0'):
    """b̂ und u(b̂) je Punkt (Summe: feld r0/r1; Zellen: rz0/rz1) aus einer oder mehreren Kalibrierläufen
    (Rauschvarianten). Rückgabe dict(bias, u, je_variante, n)."""
    je = []
    for lauf in laeufe:
        X = np.stack([b['felder'][feld][..., 0] for b in lauf['befunde']])
        n = np.isfinite(X).sum(0)
        with np.errstate(invalid='ignore', divide='ignore'), warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)               # Punkte mit weniger als zwei Werten
            mu = np.nanmean(X, 0)
            se = np.nanstd(X, 0, ddof=1) / np.sqrt(n)
        je.append(dict(mittel=mu, u_mc=se, n=n))
    M = np.stack([j['mittel'] for j in je])
    U = np.stack([j['u_mc'] for j in je])
    if len(je) == 1:
        b, u = M[0], U[0]
        spann = np.zeros_like(b)
    else:
        lo, hi = M.min(0), M.max(0)
        b = (lo + hi) / 2
        spann = (hi - lo) / 2
        u = np.sqrt(np.mean(U ** 2, 0) + spann ** 2 / 3)
    return dict(bias=b, u=u, halbe_spannweite=spann, je_variante=je, n_varianten=len(je))


def max_abs_z(befunde, art, bias, u_bias):
    """max|z⁰| je Kampagne mit Biaskorrektur; art 'H1' (r0, v0) oder 'H1Z' (rz0, vz0). Rückgabe (Werte, vollständig)."""
    fr, fv = ('r0', 'v0') if art == 'H1' else ('rz0', 'vz0')
    w, voll = [], []
    for b in befunde:
        z = _z(b['felder'][fr], b['felder'][fv], bias, u_bias)
        ok = np.isfinite(z)
        voll.append(bool(ok.all()))
        w.append(float(np.abs(z[ok]).max()) if ok.any() else np.nan)
    return np.array(w), np.array(voll)


def c_bestimmen(befunde, art, bias, u_bias, q=0.95, seed=0):
    w, voll = max_abs_z(befunde, art, bias, u_bias)
    qq = metriken.quantil(w[voll], q, seed=seed)
    return dict(c=qq['wert'], se=qq['se'], n_vollstaendig=int(voll.sum()), n=len(befunde), q=q,
                ausgeschlossen=int((~voll).sum()), werte=w, vollstaendig=voll)


# ── H2: Bezugswert und Überdeckung ───────────────────────────────────────────────────────────────────
def h2_bezug(wahr, W_ids, profil):
    """Bezugswert der Überdeckung je Kampagnenfenster: Wert des Schätzers an den rauschfreien Kurven
    (Entwicklungsprüffall „schaetzer_rauschfrei“): Δφ*_ref = φ*(F_mess) − φ*(F_ŷ) auf den Sollabszissen von W."""
    art = profil.wert('h2.ueberdeckung_bezug')
    if art != 'schaetzer_rauschfrei':
        raise ValueError(f'Bezugswert {art!r} nicht umgesetzt')
    idx = [wahr['schnitt'].index(k) for k in W_ids]
    phi = np.asarray(kv.SCHNITT_PHI2, float)[idx]
    F = wahr['F']
    s = profil.wert('h2.suchschritt_grad')
    fit = {k: float(zeltfit.zeltfit(phi[None], F[k][idx][None], schritt=s)['phi_stern'][0])
           for k in ('F_mess', 'F_yhat0', 'F_yhat1')}
    return fit['F_mess'] - fit['F_yhat0'], fit['F_mess'] - fit['F_yhat1']


def h2_ueberdeckung(lauf, profil):
    """Überdeckung je Intervalltyp (getrennt gegen ŷ⁰ und ŷ¹) mit MC-Fehler und gewählter Typ nach der
    Rückfallkette. Ein Typ gilt, wenn beide Überdeckungen die Schwelle erreichen (Regel harness.ueberdeckung_beide)."""
    m = lauf['meta']
    kw = dict(szenario=m['szenario'], stufe=m['stufe'], profil=m['profil'],
              normativ=rg.NORMATIVE_ZAHLEN['kampagnen_kalibrierung'])
    try:
        schwelle = profil.wert('h2.ueberdeckung')
        profil.wert('h2.ueberdeckung_bezug')
        kette_ = profil.wert('h2.intervallkette')
    except rg.RegelOffen as e:
        return dict(typ=None, grund=e.grund, ueberdeckung={})
    cache, treffer = {}, {}
    for b in lauf['befunde']:
        W = tuple(b['H2']['W_ids'])
        if not W or not b['H2']['intervalle']:
            continue
        if W not in cache:
            cache[W] = h2_bezug(lauf['wahrheit'], list(W), profil)
        ref = cache[W]
        for typ, ivs in b['H2']['intervalle'].items():
            t = treffer.setdefault(typ, [[], []])
            for s in (0, 1):
                a, bb = ivs[s] if ivs[s] is not None else (None, None)
                if a is None or bb is None:
                    continue
                t[s].append(bool(a - 1e-12 <= ref[s] <= bb + 1e-12))
    ub = {}
    for typ, (t0, t1) in sorted(treffer.items()):
        ub[typ] = dict(yhat0=metriken.rate(sum(t0), len(t0), f'Überdeckung {typ} gegen ŷ⁰', **kw),
                       yhat1=metriken.rate(sum(t1), len(t1), f'Überdeckung {typ} gegen ŷ¹', **kw))

    def erreicht(typ):
        u = ub.get(typ)
        return bool(u and u['yhat0']['rate'] is not None and u['yhat1']['rate'] is not None and
                    u['yhat0']['rate'] >= schwelle and u['yhat1']['rate'] >= schwelle)
    if kette_ != 'a':
        return dict(typ=None, grund=f'Rückfallkette {kette_!r} nicht umgesetzt', ueberdeckung=ub)
    folge = ['perzentil_0.95', 'bca_0.95'] + [f'perzentil_{x:.2f}' for x in (0.96, 0.97, 0.98, 0.99)]
    gewaehlt = next((t for t in folge if erreicht(t)), None)
    typ, niveau = (gewaehlt.rsplit('_', 1)[0], float(gewaehlt.rsplit('_', 1)[1])) if gewaehlt else ('keiner', None)
    return dict(typ=typ, niveau=niveau, schluessel=gewaehlt, schwelle=schwelle, ueberdeckung=ub, folge=folge,
                bezug=dict(art=profil.wert('h2.ueberdeckung_bezug'), werte={','.join(k): v for k, v in cache.items()}))


# ── Werte für Teil B (nr4, nr10) ─────────────────────────────────────────────────────────────────────
def werkzeug8(bias0, bias1, biasz0, biasz1, c1, cz, h2, n_kal, n_pruef, profil_id, pruefung=None, gepoolt=False):
    red = n_kal < rg.NORMATIVE_ZAHLEN['kampagnen_kalibrierung']
    herk = (f'Kalibriersimulation (AP-13) mit {n_kal} Kampagnen' + (' (reduziert: Entwicklungsdiagnostik)' if red else '')
            + f', Profil {profil_id}')
    if pruefung is None:
        pr = ''
    elif pruefung['rate'] is None:
        pr = f'; Prüfrate nicht bestimmbar (keine der {n_pruef} Prüfkampagnen mit allen Tests)'
    else:
        pr = (f'; Prüfrate {pruefung["rate"]:.4f} ± {pruefung["mc_se"]:.4f} aus {pruefung["nenner"]} vollständigen von '
              f'{n_pruef} Kampagnen' + ('; gepooltes Quantil (Prüfrate > 0,069)' if gepoolt else ''))
    c_txt = (f': q95 von max|z⁰| über 147 Tests, n = {c1["n_vollstaendig"]}' if c1['c'] is not None else
             ': nicht bestimmbar (keine Kalibrierkampagne mit allen Tests)')
    return dict(c_H1=c1['c'], c_H1_herkunft=herk + c_txt + pr,
                c_H1Z=cz['c'], c_H1Z_herkunft=herk + f': q95 von max|z⁰| über 441 Tests, n = {cz["n_vollstaendig"]}',
                bias0=bias0['bias'], bias1=bias1['bias'], u_bias0=bias0['u'], u_bias1=bias1['u'],
                bias0_zellen=biasz0['bias'], bias1_zellen=biasz1['bias'], u_bias0_zellen=biasz0['u'],
                u_bias1_zellen=biasz1['u'], bias_herkunft=herk + ': Mittel der Rohresiduen von F_min − ⟨N⟩',
                h2_intervall=None if h2.get('typ') is None else dict(
                    typ=h2['typ'], niveau=h2.get('niveau'), quelle=herk,
                    ueberdeckung={k: dict(yhat0=v['yhat0']['rate'], yhat1=v['yhat1']['rate'])
                                  for k, v in h2['ueberdeckung'].items()}),
                pruefrate=None if pruefung is None else dict(rate=pruefung['rate'], mc_se=pruefung['mc_se'],
                                                             n=pruefung['nenner'], gepoolt=gepoolt),
                reduziert=red)


def kalibrieren(sid, stufe, profil, n_kal, n_pruef, seed_basis, plan=None, n_min=None, prozesse=1,
                rauschvarianten=None, fortschritt=None, k_max=None):
    """Kalibrier- und Prüfsimulation an einem Szenariopunkt mit exakter Superposition (vgl. N01/N02)."""
    try:
        profil.wert('h1.c_rauschmodelle')
        c_regel = None
    except rg.RegelOffen as e:
        c_regel = e.grund
    var = rauschvarianten or [None]
    kal = [kpn.ausfuehren(sid, stufe, profil, n_kal, seed_basis, 'kalibrierung_c', plan, n_min, None, rv,
                          prozesse=prozesse, fortschritt=fortschritt, k_max=k_max) for rv in var]
    b0, b1 = rauschbias(kal, 'r0'), rauschbias(kal, 'r1')
    bz0, bz1 = rauschbias(kal, 'rz0'), rauschbias(kal, 'rz1')
    alle = [b for lauf in kal for b in lauf['befunde']]
    c1 = c_bestimmen(alle, 'H1', b0['bias'], b0['u'], seed=seed_basis)
    c1_roh = c1
    cz = c_bestimmen(alle, 'H1Z', bz0['bias'], bz0['u'], seed=seed_basis + 1)
    h2 = h2_ueberdeckung(kal[0], profil)
    nu = max(2, (plan.n_bloecke if plan is not None else 20) - 1)
    cB = float(stats.t.ppf(1 - 0.05 / 294, nu))
    w8 = werkzeug8(b0, b1, bz0, bz1, c1, cz, h2, len(alle), n_pruef, profil.id)
    if c_regel:
        w8.update(c_H1=None, c_H1Z=None, c_H1_herkunft=f'offen: {c_regel}', c_H1Z_herkunft=f'offen: {c_regel}')
    # Prüfsimulation
    pr = kpn.ausfuehren(sid, stufe, profil, n_pruef, seed_basis, 'pruefung_c', plan, n_min, w8, var[0],
                        prozesse=prozesse, fortschritt=fortschritt, k_max=k_max)
    kw = dict(szenario=sid, stufe=stufe, profil=profil.id, normativ=rg.NORMATIVE_ZAHLEN['kampagnen_pruefung'])
    zp = np.array([np.abs(b['felder']['z0'][np.isfinite(b['felder']['z0'])]).max() if np.isfinite(
        b['felder']['z0']).any() else np.nan for b in pr['befunde']])
    vp = np.array([bool(np.isfinite(b['felder']['z0']).all()) for b in pr['befunde']])
    pruefung = None
    gepoolt = False
    if w8['c_H1'] is not None:
        pruefung = metriken.rate(int((zp[vp] > w8['c_H1']).sum()), int(vp.sum()),
                                 'Prüfrate: Anteil mit mindestens einem |z⁰| > c (exakt)', **kw)
        schwelle = profil.wert('h1.c_pruefschwelle')
        if pruefung['rate'] is not None and pruefung['rate'] > schwelle:
            gepoolt = True
            pool = np.r_[c1['werte'][c1['vollstaendig']], zp[vp]]
            c1 = dict(c1, c=float(np.quantile(pool, 0.95)), n_vollstaendig=int(pool.size), gepoolt=True)
        w8 = werkzeug8(b0, b1, bz0, bz1, c1, cz, h2, len(alle), n_pruef, profil.id, pruefung, gepoolt)
        if gepoolt:
            pr = kpn.ausfuehren(sid, stufe, profil, n_pruef, seed_basis, 'pruefung_c', plan, n_min, w8, var[0],
                                prozesse=prozesse, fortschritt=fortschritt, k_max=k_max)
    rp = kpn.raten(pr)
    gemeinsam = rp['raten']['H1 und H2 bestätigt']
    restbias = None if w8['bias0'] is None else _restbias(pr['befunde'], w8)
    return dict(
        meta=dict(szenario=sid, stufe=stufe, profil=profil.id, profil_sha256=profil.sha256(), seed_basis=seed_basis,
                  n_kalibrierung=len(alle), n_pruefung=n_pruef, rauschvarianten=len(var),
                  reduziert=bool(len(alle) < rg.NORMATIVE_ZAHLEN['kampagnen_kalibrierung'] or
                                 n_pruef < rg.NORMATIVE_ZAHLEN['kampagnen_pruefung']) or profil.reduziert,
                  lesart=('Entwicklungsdiagnostik: weniger Kampagnen oder Replikate als normativ; keine '
                          'Kalibrierabnahme' if (len(alle) < 1000 or n_pruef < 1000 or profil.reduziert) else
                          'normative Kampagnenzahl'),
                  code_version=formate.code_version()),
        c_H1=dict(wert=c1['c'], se=c1['se'], n=c1['n_vollstaendig'], ausgeschlossen=c1['ausgeschlossen'],
                  gepoolt=gepoolt, c_B=cB, regel=c_regel),
        c_H1Z=dict(wert=cz['c'], se=cz['se'], n=cz['n_vollstaendig'], ausgeschlossen=cz['ausgeschlossen'],
                   c_B=float(stats.t.ppf(1 - 0.05 / 882, nu))),
        rauschbias=dict(b0=b0['bias'], u_b0=b0['u'], b1=b1['bias'], u_b1=b1['u'], halbe_spannweite0=b0['halbe_spannweite'],
                        n_varianten=b0['n_varianten'],
                        verhaeltnis_zu_u_c=dict(
                            b0=_verh(b0['bias'], kal), b1=_verh(b1['bias'], kal, 'u0'))),
        pruefung=pruefung, pruefschwelle=profil.wert('h1.c_pruefschwelle'), gepoolt=gepoolt, restbias=restbias,
        h2=h2, gemeinsame_bestaetigung=gemeinsam, werkzeug8=w8, raten_pruefung=rp,
        zmax=dict(kalibrierung=c1_roh['werte'], kalibrierung_vollstaendig=c1_roh['vollstaendig'], pruefung=zp,
                  pruefung_vollstaendig=vp),
        laeufe=dict(kalibrierung=[l['meta'] for l in kal], pruefung=pr['meta']))


def _restbias(befunde, w8):
    """K13: Restbias nach Korrektur in der Prüfsimulation, |E[r(F_min)] − b̂| relativ zum Median von u_c je Punkt
    (Soll ≤ 0,1, Plan K13 [Vorschlag]); dazu der MC-Fehler dieses Verhältnisses."""
    out = {}
    for feld, vfeld, b in (('r0', 'v0', w8['bias0']), ('r1', 'v1', w8['bias1'])):
        X = np.stack([x['felder'][feld][:, 0] for x in befunde]) - np.asarray(b, float)
        U = np.sqrt(np.stack([x['felder'][vfeld][:, 0] for x in befunde]))
        n = np.isfinite(X).sum(0)
        with np.errstate(invalid='ignore', divide='ignore'), warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            mu, se = np.nanmean(X, 0), np.nanstd(X, 0, ddof=1) / np.sqrt(n)
            um = np.nanmedian(U, 0)
            v, sv = np.abs(mu) / um, se / um
        out['yhat0' if feld == 'r0' else 'yhat1'] = dict(max_verhaeltnis=float(np.nanmax(v)),
                                                         mc_se_verhaeltnis=float(np.nanmax(sv)), soll=0.1,
                                                         n=int(n.max()) if n.size else 0)
    return out


def _verh(b, kal, feld='u0'):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        u = np.nanmedian(np.stack([x['felder'][feld][:, 0] for lauf in kal for x in lauf['befunde']]), 0)
    with np.errstate(invalid='ignore', divide='ignore'):
        return float(np.nanmax(np.abs(b) / u))
