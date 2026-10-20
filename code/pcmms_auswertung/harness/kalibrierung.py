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

Profilstand 2026-11 (Regeln harness.mengen, harness.nachziehen, h1.c_rauschmodelle, Auftrag vom 20.10.2026): b̂, u(b̂),
c (H1, H1Z), Prüfrate, Restbias und H2-Überdeckung beziehen sich auf die Auswertungsmenge A (harness.mengen), P(H1
und H2 bestätigt) auf G; b̂ mittelt die Rohresiduen mit den tatsächlich realisierten gültigen Laufzahlen der
Kampagnen in A. c ist das Quantil des Standardmodells (erste Rauschvariante, Fassung (a)); die übrigen Varianten
geben c als Sensitivität und gehen über die halbe Spannweite in u(b̂) ein. Mit soll_A wird je Rolle und Variante bis
|A| = soll_A nachgezogen, höchstens bis zum technischen Versuchslimit; sonst „nicht abgeschlossen“. Historische
Profile rechnen unverändert (alle Kampagnen, vollständige Tests für c).
"""
import warnings

import numpy as np
from scipy import stats

from .. import formate, konventionen as kv, regeln as rg, zeltfit
from . import kampagnen as kpn, mengen, metriken, reserve as rs


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


def _lauf(sid, stufe, profil, n, seed_basis, rolle, plan, n_min, w8, rv, prozesse, fortschritt, k_max, verfahren,
          soll_A, ausfuehren=None):
    """Kampagnen einer Rolle und Rauschvariante; mit soll_A nachgezogen bis |A| = soll_A (harness.nachziehen).
    ausfuehren: Ersatz für kampagnen.ausfuehren mit derselben Signatur (etwa mit Checkpoints je Partie)."""
    lauf = ausfuehren or kpn.ausfuehren
    if soll_A is None:
        return lauf(sid, stufe, profil, n, seed_basis, rolle, plan, n_min, w8, rv, prozesse=prozesse,
                    fortschritt=fortschritt, k_max=k_max, verfahren=verfahren)
    regel = profil.wert('harness.nachziehen')
    teile = []

    def laufe(start, k):
        teile.append(lauf(sid, stufe, profil, k, seed_basis, rolle, plan, n_min, w8, rv, prozesse=prozesse,
                          fortschritt=fortschritt, k_max=k_max, verfahren=verfahren, start=start))
        return teile[-1]['befunde']
    nz = mengen.nachziehen(laufe, int(soll_A), float(regel['versuchslimit_faktor']), start_n=n)
    meta = dict(teile[0]['meta'], n=nz['G'], seeds=[x for t in teile for x in t['meta']['seeds']],
                laufzeit_s=round(sum(t['meta']['laufzeit_s'] for t in teile), 2),
                nachziehen={k: v for k, v in nz.items() if k != 'befunde'})
    return dict(teile[0], meta=meta, befunde=nz['befunde'])


def kalibrieren(sid, stufe, profil, n_kal, n_pruef, seed_basis, plan=None, n_min=None, prozesse=1,
                rauschvarianten=None, fortschritt=None, k_max=None, verfahren=None, soll_A=None, ausfuehren=None,
                quelle=None, c_planung=False):
    """Kalibrier- und Prüfsimulation an einem Szenariopunkt mit exakter Superposition (vgl. N01/N02); verfahren wie
    harness.kampagnen.ausfuehren (alle Kampagnen der Kalibrierung und Prüfung mit demselben Verfahren). soll_A:
    Sollzahl der Auswertungsmenge je Rolle und Variante mit Nachziehen (nur Profilstand 2026-11; n_kal, n_pruef sind
    dann die erste Partie). ausfuehren: Ersatz für kampagnen.ausfuehren (Checkpoints des Kalibrierbeispiels).
    quelle (Teil d2): Modellquelle ohne Szenario (generator.phase0_modell.Modellquelle); die Kampagnen kommen dann aus
    harness.phase0_rechnungen.ausfuehren_quelle, sid und stufe sind nur Kennzeichnung. c_planung: die Prüfsimulation
    rechnet mit c_B statt mit dem kalibrierten c (Planung nach planung.teil_b_werte; kein Poolen). Im Regelstand
    2026-11 mit mehreren Rauschvarianten gilt für c die Regel h1.c_rauschmodelle ('a': Quantil des Standardmodells,
    der ersten Variante, die übrigen als Sensitivität; 'b': größtes Quantil); historisch wie bisher gepoolt."""
    neu = 'harness.mengen' in profil.regeln and profil.hat('harness.mengen')     # Profilstand 2026-11
    if soll_A is not None and not ('harness.nachziehen' in profil.regeln and profil.hat('harness.nachziehen')):
        raise ValueError('kalibrieren: Nachziehen (soll_A) verlangt die Regel harness.nachziehen (Profilstand 2026-11)')
    try:
        c_fassung = profil.wert('h1.c_rauschmodelle')
        c_regel = None
    except rg.RegelOffen as e:
        c_fassung, c_regel = None, e.grund
    if neu and c_fassung not in ('a', 'b'):
        raise ValueError(f'h1.c_rauschmodelle {c_fassung!r} nicht umgesetzt (Fassungen (a), (b))')
    var = rauschvarianten or [None]
    if quelle is not None:
        if ausfuehren is not None:
            raise ValueError('kalibrieren: quelle und ausfuehren schließen sich aus')
        from . import phase0_rechnungen

        def ausfuehren(sid_, stufe_, *a, **kw):
            return phase0_rechnungen.ausfuehren_quelle(quelle, *a, **kw)
    kw_l = dict(prozesse=prozesse, fortschritt=fortschritt, k_max=k_max, verfahren=verfahren, soll_A=soll_A,
                ausfuehren=ausfuehren)
    kal = [_lauf(sid, stufe, profil, n_kal, seed_basis, 'kalibrierung_c', plan, n_min, None, rv, **kw_l)
           for rv in var]
    mengen_kal = [mengen.aufteilen(l['befunde']) for l in kal] if neu else None
    kal_A = [dict(l, befunde=mengen.in_A(l['befunde'])) for l in kal] if neu else kal
    b0, b1 = rauschbias(kal_A, 'r0'), rauschbias(kal_A, 'r1')
    bz0, bz1 = rauschbias(kal_A, 'rz0'), rauschbias(kal_A, 'rz1')
    alle = kal_A[0]['befunde'] if neu else [b for lauf in kal for b in lauf['befunde']]
    c1 = c_bestimmen(alle, 'H1', b0['bias'], b0['u'], seed=seed_basis)
    c_var = None
    if len(kal) > 1 and not rg.ist_historisch(profil) and c_regel is None:
        c1, c_var = c_nach_regel(kal_A, c_fassung, b0, seed_basis)
    c1_roh = c1
    cz = c_bestimmen(alle, 'H1Z', bz0['bias'], bz0['u'], seed=seed_basis + 1)
    c_sens = None
    if neu and len(var) > 1:
        c_sens = [dict(variante=getattr(rv, 'name', None) or 'Szenario',
                       c_H1=c_bestimmen(l['befunde'], 'H1', b0['bias'], b0['u'], seed=seed_basis)['c'],
                       c_H1Z=c_bestimmen(l['befunde'], 'H1Z', bz0['bias'], bz0['u'], seed=seed_basis + 1)['c'],
                       n_A=len(l['befunde'])) for rv, l in zip(var, kal_A)]
    h2 = h2_ueberdeckung(kal_A[0], profil)
    nu = max(2, (plan.n_bloecke if plan is not None else 20) - 1)
    cB = float(stats.t.ppf(1 - 0.05 / 294, nu))
    w8 = werkzeug8(b0, b1, bz0, bz1, c1, cz, h2, len(alle), n_pruef, profil.id)
    if c_regel:
        w8.update(c_H1=None, c_H1Z=None, c_H1_herkunft=f'offen: {c_regel}', c_H1Z_herkunft=f'offen: {c_regel}')
    if c_planung:                                                       # Planung mit c_B (§8.4, A9.2)
        cBZ_ = float(stats.t.ppf(1 - 0.05 / 882, nu))
        w8.update(c_H1=cB, c_H1Z=cBZ_, c_H1_herkunft=f'c_B = t(1 − 0,05/294; {nu}) (Planung, §8.4, A9.2)',
                  c_H1Z_herkunft=f'c_B = t(1 − 0,05/882; {nu}) (Planung)')
    if quelle is not None:
        w8['modellquelle'] = quelle.kennung()['beschreibung'].get('name')
    # Prüfsimulation
    pr = _lauf(sid, stufe, profil, n_pruef, seed_basis, 'pruefung_c', plan, n_min, w8, var[0], **kw_l)
    kw = dict(szenario=sid, stufe=stufe, profil=profil.id, normativ=rg.NORMATIVE_ZAHLEN['kampagnen_pruefung'])
    pr_A = mengen.in_A(pr['befunde']) if neu else pr['befunde']
    zp = np.array([np.abs(b['felder']['z0'][np.isfinite(b['felder']['z0'])]).max() if np.isfinite(
        b['felder']['z0']).any() else np.nan for b in pr_A])
    vp = np.array([bool(np.isfinite(b['felder']['z0']).all()) for b in pr_A], bool)
    pruefung = None
    gepoolt = False
    if w8['c_H1'] is not None and c_planung:
        pruefung = metriken.rate(int((zp[vp] > w8['c_H1']).sum()), int(vp.sum()),
                                 'Anteil mit mindestens einem |z⁰| > c_B (Planung, exakt)', **kw)
    elif w8['c_H1'] is not None:
        pruefung = metriken.rate(int((zp[vp] > w8['c_H1']).sum()), int(vp.sum()),
                                 'Prüfrate: Anteil mit mindestens einem |z⁰| > c (exakt)', **kw)
        schwelle = profil.wert('h1.c_pruefschwelle')
        if pruefung['rate'] is not None and pruefung['rate'] > schwelle:
            gepoolt = True
            pool = np.r_[c1['werte'][c1['vollstaendig']], zp[vp]]
            c1 = dict(c1, c=float(np.quantile(pool, 0.95)), n_vollstaendig=int(pool.size), gepoolt=True)
        w8 = werkzeug8(b0, b1, bz0, bz1, c1, cz, h2, len(alle), n_pruef, profil.id, pruefung, gepoolt)
        if quelle is not None:
            w8['modellquelle'] = quelle.kennung()['beschreibung'].get('name')
        if gepoolt:
            pr = _lauf(sid, stufe, profil, n_pruef, seed_basis, 'pruefung_c', plan, n_min, w8, var[0], **kw_l)
            pr_A = mengen.in_A(pr['befunde']) if neu else pr['befunde']
    rp = kpn.raten(pr)
    gemeinsam = rp['raten']['H1 und H2 bestätigt']                  # Nenner: alle begonnenen Kampagnen (G)
    if neu:
        w8['e3_kriterien'] = _e3_kriterien(pr_A)['kriterien']
    restbias = None if w8['bias0'] is None or not pr_A else _restbias(pr_A, w8)
    return dict(
        meta=dict(szenario=sid, stufe=stufe, profil=profil.id, profil_sha256=profil.sha256(), seed_basis=seed_basis,
                  n_kalibrierung=len(alle), n_pruefung=n_pruef, rauschvarianten=len(var),
                  verfahren=pr['meta']['verfahren'],
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
        mengen=None if not neu else dict(kalibrierung=mengen_kal, pruefung=mengen.aufteilen(pr['befunde']),
                                         hinweis='P(H1 und H2 bestätigt) mit Nenner G; c, Prüfrate, b̂, u(b̂), Restbias '
                                                 'und H2-Überdeckung über A',
                                         nachziehen=dict(kalibrierung=[l['meta'].get('nachziehen') for l in kal],
                                                         pruefung=pr['meta'].get('nachziehen'))),
        c_sensitivitaet=c_sens,
        reserve_ziel=_reserve_ziel(pr['befunde'], profil, n_min) if neu else None,
        e3=_e3_kriterien(pr_A) if neu else None,
        zeitbilanz=_zeitbilanz(pr['befunde'], profil, plan) if neu else None,
        zmax=dict(kalibrierung=c1_roh['werte'], kalibrierung_vollstaendig=c1_roh['vollstaendig'], pruefung=zp,
                  pruefung_vollstaendig=vp),
        laeufe=dict(kalibrierung=[l['meta'] for l in kal], pruefung=pr['meta']),
        **({} if c_var is None else dict(c_varianten=c_var)),
        **({} if not c_planung else dict(c_planung='c_B')),
        **({} if quelle is None else dict(modellquelle=quelle.kennung())))


def c_nach_regel(kal, regel, b0, seed):
    """c bei mehreren Rauschvarianten nach Regel h1.c_rauschmodelle: 'a' Quantil des Standardmodells (erste Variante),
    'b' größtes Quantil über die Varianten; die Quantile je Variante als Sensitivität. Rückgabe (c-dict, je
    Variante)."""
    je = [c_bestimmen(l['befunde'], 'H1', b0['bias'], b0['u'], seed=seed) for l in kal]
    if regel == 'a':
        c = je[0]
    elif regel == 'b':
        c = max((x for x in je if x['c'] is not None), key=lambda x: x['c'], default=je[0])
    else:
        raise ValueError(f'Regel h1.c_rauschmodelle = {regel!r} nicht umgesetzt (a, b)')
    return dict(c, regel=regel), [dict(rauschmodell=l['meta'].get('rauschmodell'), c=x['c'], se=x['se'],
                                       n=x['n_vollstaendig']) for l, x in zip(kal, je)]


def _e3_kriterien(befunde):
    """E3-Kriterien von A9.11 je Prüfgröße aus der Prüfsimulation (Menge A, exakte Superposition): Raten „auffällig“
    und „unauffällig“ mit Zähler und Nenner; als Kriterienbefund für Teil B (nr10.e3_kriterien) nur bei der
    normativen Kampagnenzahl, sonst None je Kriterium (nicht ausgewiesen). Die Modellprüfung ist nicht umgesetzt
    (None); die dafür nötigen Größen stehen in den Kurzbefunden (Σ̂, ŝ, ρ̂, ν, n_A, n₀ⱼ)."""
    bf = [b for b in befunde if (b.get('E3') or {}).get('regelstand') == '2026-11']
    voll = len(bf) >= rg.NORMATIVE_ZAHLEN['kampagnen_pruefung']
    raten, krit = {}, dict(herkunft=f'Prüfsimulation (AP-13), {len(bf)} Kampagnen der Menge A'
                                    + ('' if voll else ' – reduziert: Kriterien nicht ausgewiesen (None)'))
    for g in ('E3a', 'E3b'):
        u = [((b['E3'].get('pruefgroessen') or {}).get(g) or {}).get('urteil') for b in bf]
        ra = metriken.rate(sum(x == 'auffällig' for x in u), len(u), f'P({g} auffällig | exakt)')
        ru = metriken.rate(sum(x == 'unauffällig' for x in u), len(u), f'P({g} unauffällig | exakt)')
        raten[g] = dict(auffaellig=ra, unauffaellig=ru)
        krit[g] = dict(auffaellig=bool(ra['rate'] <= 0.05) if voll and ra['rate'] is not None else None,
                       unauffaellig=bool(ru['rate'] >= 0.8) if voll and ru['rate'] is not None else None,
                       modellpruefung=None)
    return dict(raten=raten, kriterien=krit)


def _ist_ablauf4(befunde):
    return bool(befunde) and all((b.get('ablauf') or {}).get('gueltig_je_schnittpunkt') is not None for b in befunde)


def _reserve_ziel(befunde, profil, n_min):
    """Bedingung planung.reserve_ziel in der Prüfsimulation (nur mit ablauf-4 und gegebenem n_min)."""
    if n_min is None or not _ist_ablauf4(befunde):
        return dict(geprueft=False, grund='nur mit Ablauf ablauf-4 und gegebenem n_min')
    return dict(rs.bedingung(befunde, int(n_min), profil.wert('planung.reserve_ziel')), geprueft=True)


def _zeitbilanz(befunde, profil, plan):
    if plan is None or not _ist_ablauf4(befunde):
        return None
    return rs.zeitbilanz(befunde, float(plan.T_lauf), profil.wert('planung.zeitformel'))


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
