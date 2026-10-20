"""Kampagnen aus einer Modellquelle ohne Szenario (Teil d2) und die Rechnungen R1-d, R2-d, R3-d der
Entscheidungsvorlage (Abschnitt 5.5) als Auftragslisten mit Seeds; gestartet wird nichts von selbst.

Kampagnen (ausfuehren_quelle): wie harness.kampagnen.ausfuehren, aber Generator generator.phase0_modell.erzeuge mit
dem Phase0Modell der Quelle (Struktur aus Phase 0, Parameter der Quelle oder der übergebenen Rauschvariante),
Kalibrierung P0.1–P0.5 aus der Quelle (gemessen, nicht neu erzeugt), Pilotskript, Teil B und Stufe 2 wie
harness.kette. Mit einem Verfahren „zustand“ läuft Phase 1 als Ablauf wie harness.kette.kampagne_ablauf
(Wiederholungen, Halte, simulierte Wiederaufnahme): Die Messung (MessungQuelle) bildet die Versuche aus dem Vorrat des
Strukturgenerators (generator.phase0_modell.Vorrat; ohne zusätzliche Versuche bitgleich zum statischen Generator).
Seeds: zufall.unterseed(Basis, Rolle, 'phase0', Name der Quelle, i); Rauschvarianten derselben Quelle teilen die
Seeds (gepaarte Vergleiche). Die Wahrheit der Quelle ist die ihrer Struktur bei exakter Superposition (Klasse R0),
keine Szenario-Wahrheit; nur der Harness liest sie (H2-Überdeckung).

Rechnungen (synthetische Phase-0-Daten; sie prüfen Schätz- und Dateikette, keine Apparatur):
  R1-d  Rundreise je Satz: Szenariogenerator (nur Phase 0) → Schätzer (Pilotskript, Satz bei k_max) → Vergleich mit
        den bekannten Szenarioparametern; dann Strukturmodell (Punktschätzer) → ein Phase-0-Satz → erneute Schätzung.
        Auftragsliste r1d_auftraege (Vorgabe 1000 Sätze je Szenariopunkt, N01-A4, N04-laufart, N03-ungleich × L0, L2,
        L4), Rechnung r1d_satz, Auswertung r1d_auswerten (Verhältnis zur Wahrheit, Überdeckung der oberen 80-%-Grenze).
  R2-d  Gleichheit mit dem Szenariomodell auf Ebene der Entscheidungen: je Szenariopunkt Kalibrier- und
        Prüfsimulation mit dem Szenariogenerator und mit dem Phase-0-Modell, das aus einem festen Phase-0-Satz desselben
        Szenarios geschätzt ist (Strukturmodell, Punktschätzer); dazu die Variante „bekannt“ (Szenarioparameter im
        Strukturgenerator), die bitgleich sein muss. r2d_auftraege, r2d_punkt, r2d_vergleich.
  R3-d  Planung mit dem Pilotmodell gegen das Szenario-Orakel: Pilotskript mit Planungshaken „phase0_modell“ und
        „szenario_orakel“ auf denselben Phase-0-Daten, gleiche Kandidaten und Seeds. r3d_auftraege, r3d_punkt.
"""
import time
import warnings

import numpy as np

from .. import ablauf, auswertung, formate, pilot, regeln, verfahren as vf, zufall
from .. import laufgroessen as lgm
from ..generator import ebene_h, kampagne as kp, phase0_modell as p0m, szenarien, wahrheit
from . import kampagnen, kette

VERSION = 'phase0_rechnungen-0.1'


# ── Kampagnen aus einer Modellquelle ────────────────────────────────────────────────────────────────────
def _rausch(quelle, rausch):
    return quelle.rausch if rausch is None else rausch


class MessungQuelle(kette.MessungH):
    """Messung eines Versuchs aus der Modellquelle im Ablauf „zustand“: wie kette.MessungH mit dem Vorrat des
    Strukturgenerators (Ströme „generator“ und „generator_struktur“ wie der statische Generator). Zusätzliche Versuche
    ziehen aus (seed, „generator_versuch“, i) und (seed, „generator_struktur_versuch“, i); ein neuer Zeitpunkt des
    Nullpunktpfads oder ein neuer Abschnitt aus (seed, „generator_pfad_versuch“, i)."""

    def __init__(self, modell, laeufe, seed, rausch=None):
        self.modell, self.seed = modell, int(seed)
        self.vorrat = p0m.Vorrat(modell, laeufe, zufall.strom(seed, 'generator'), rausch,
                                 rng_zusatz=zufall.strom(seed, 'generator_struktur'))
        self.versuch_ereignisse = [e for e in modell.effekte_art('ereignis') if 'versuch' in e]

    def messen(self, spec, versuch):
        effs = self._effekte(spec, versuch)
        i = versuch['index']
        kw = dict(rng_pfad=zufall.strom(self.seed, 'generator_pfad_versuch', i), ereignisse=effs,
                  messtag=versuch.get('messtag_ist'))
        if versuch['geplant']:
            k, d, _ = self.vorrat.lauf(spec, bezug=versuch['bezug'], **kw)
        else:
            k, d, _ = self.vorrat.lauf(spec, rng=zufall.strom(self.seed, 'generator_versuch', i),
                                       rng_zusatz=zufall.strom(self.seed, 'generator_struktur_versuch', i), **kw)
        return k, d


def _kampagne_quelle_ablauf(quelle, profil, plan, seed, werkzeug8, n_min, k_max, v, rausch, effekte):
    """Kampagne aus der Modellquelle mit Ablauf der Phase 1 (wie kette.kampagne_ablauf und kette._kette_ablauf)."""
    m = quelle.modell(plan, k_max, _rausch(quelle, rausch), effekte)
    t = time.perf_counter()
    rng_r = zufall.strom(seed, 'reihenfolge')
    laeufe = kp.laufplan(m.plan, rng_r)
    kennung = formate.synth_kennung('PHASE0', quelle.name, seed)
    messung = MessungQuelle(m, laeufe, seed, _rausch(quelle, rausch))
    tab0 = messung.phase0(laeufe)
    tab0.meta.setdefault('kennung', kennung)
    w8 = kette.testvorgabe_werkzeug8() if werkzeug8 is None else werkzeug8
    tb, pe = kette.teil_b_erzeugen(tab0, quelle.kalibrierung, m, profil, w8, seed, n_min, kennung=kennung, verfahren=v)
    sw = auswertung._schwellen(tb, profil)
    gueltig0 = {x for e in tb['nr3']['einzel0'] for x in e['lauf_ids']}
    s3 = ablauf.s3_basis(tab0, gueltig0, sw.kmax)
    ak = dict(verfahren=v.kennung(), szenario=None, modellquelle=quelle.kennung()['sha256'], stufe=None,
              seed=int(seed), ebene='H', plan=kp.plan_dict(m.plan), schwellen_sha256=ablauf.schwellen_kennung(sw, s3),
              profil_sha256=profil.sha256())
    a = ablauf.Ablauf([l for l in laeufe if l['phase'] == 1], messung, sw, s3, rng_r, v.optionen, m.plan.T_lauf,
                      m.plan.tag_pause, kennung=ak, fassung=v.fassung)
    a.ausfuehren()
    regel = kette.wiederaufnahme_regel(profil, v, tb)
    wa = kette.wiederaufnehmen(a, regel) if regel is not None else None
    tab = kette.ablauf_tabelle(dict(tab0=tab0, ablauf=a))
    erg = auswertung.auswerten(tab, quelle.kalibrierung, tb, profil)
    return dict(ergebnis=erg, teil_b=tb, tabelle=tab, modell=m, laeufe=laeufe, pilot=pe, verfahren=v.kennung(),
                laufzeit_s=round(time.perf_counter() - t, 3),
                ablauf=dict(a.bericht(), harness_wiederaufnahme=wa))


def kampagne_quelle(quelle, profil, plan, seed, werkzeug8=None, n_min=None, k_max=None, verfahren=None, rausch=None,
                    effekte=None):
    """Eine Kampagne aus der Modellquelle: Generator, Pilotskript, Teil B, Stufe 2; mit einem Verfahren „zustand“
    Phase 1 als Ablauf (MessungQuelle)."""
    v = vf.oder_standard(verfahren)
    if v.ablauf == 'zustand':
        return _kampagne_quelle_ablauf(quelle, profil, plan, seed, werkzeug8, n_min, k_max, v, rausch, effekte)
    m = quelle.modell(plan, k_max, _rausch(quelle, rausch), effekte)
    t = time.perf_counter()
    laeufe = kp.laufplan(m.plan, zufall.strom(seed, 'reihenfolge'))
    tab = p0m.erzeuge(m, laeufe, zufall.strom(seed, 'generator'), rng_zusatz=zufall.strom(seed, 'generator_struktur'))
    kennung = formate.synth_kennung('PHASE0', quelle.name, seed)
    tab.meta.setdefault('kennung', kennung)
    w8 = kette.testvorgabe_werkzeug8() if werkzeug8 is None else werkzeug8
    tb, pe = kette.teil_b_erzeugen(tab, quelle.kalibrierung, m, profil, w8, seed, n_min, kennung=kennung, verfahren=v)
    erg = auswertung.auswerten(tab, quelle.kalibrierung, tb, profil)
    return dict(ergebnis=erg, teil_b=tb, tabelle=tab, modell=m, laeufe=laeufe, pilot=pe, verfahren=v.kennung(),
                laufzeit_s=round(time.perf_counter() - t, 3))


def _eine(auftrag):
    quelle, profil, plan, seed, w8, n_min, rausch, k_max, verfahren, effekte = auftrag
    r = kampagne_quelle(quelle, profil, plan, seed, w8, n_min, k_max, verfahren, rausch, effekte)
    return kampagnen.kurzbefund(r['ergebnis'], r['teil_b'], seed, r.get('ablauf'))


def kampagnen_seed(basis, rolle, quelle, i):
    return zufall.unterseed(basis, rolle, 'phase0', quelle.name, int(i))


def wahrheit_quelle(quelle, plan, k_max=None, rausch=None, effekte=None):
    """Wahrheit der Quelle (Struktur bei exakter Superposition, rauschfrei) in der Form von kampagnen.wahrheit_kurz."""
    m = quelle.modell(plan, k_max, _rausch(quelle, rausch), effekte)
    w, felder = wahrheit.berechne(m, kp.schnitt_konfigurationen(m.plan))
    out = {k: w.get(k) for k in ('klasse', 'r_max_rel_beide', 'r_max_rel_yhat0', 'r_max_rel_yhat1',
                                 'klasse_sens_faktor_0_1', 'klasse_sens_fassung_A', 'r_max_rel_je_groesse',
                                 'zellminimum_min_N', 'schnitt', 'Delta_B')}
    out['F'] = {k: np.asarray(felder[k], float) for k in ('F_mess', 'F_yhat0', 'F_yhat1') if k in felder}
    out['staerke'] = None
    out['quelle'] = 'Struktur der Modellquelle (keine Szenario-Wahrheit)'
    return out


def ausfuehren_quelle(quelle, profil, n, seed_basis, rolle='pruefung', plan=None, n_min=None, werkzeug8=None,
                      rausch=None, staerke=None, prozesse=1, fortschritt=None, k_max=None, verfahren=None,
                      effekte=None, start=0):
    """n Kampagnen der Modellquelle (Seeds start … start + n − 1); Rückgabe wie kampagnen.ausfuehren (meta, befunde,
    wahrheit). staerke wird nicht verwendet (Schnittstelle von kampagnen.ausfuehren)."""
    if staerke is not None:
        raise ValueError('Modellquelle: keine Effektstärke (exakte Superposition der Struktur)')
    plan = kp.Plan() if plan is None else plan
    verfahren = vf.oder_standard(verfahren)
    seeds = [kampagnen_seed(seed_basis, rolle, quelle, i) for i in range(start, start + n)]
    auftraege = [(quelle, profil, plan, s, werkzeug8, n_min, rausch, k_max, verfahren, effekte) for s in seeds]
    t = time.perf_counter()
    if prozesse > 1:
        befunde = kampagnen._parallel(auftraege, prozesse, _eine)
    else:
        befunde = []
        for i, a in enumerate(auftraege):
            befunde.append(_eine(a))
            if fortschritt:
                fortschritt(i + 1, n)
    r = p0m.parameter(_rausch(quelle, rausch))
    meta = dict(szenario=f'phase0:{quelle.name}', stufe=None, profil=profil.id, profil_sha256=profil.sha256(), n=n,
                seed_basis=int(seed_basis), rolle=rolle, seeds=seeds, plan=kampagnen._plan_dict(plan), n_min=n_min,
                werkzeug8_herkunft=None if werkzeug8 is None else werkzeug8.get('c_H1_herkunft'),
                werkzeug8=('TESTVORGABE' if werkzeug8 is None else 'übergeben'),
                normative_kampagnenzahl=regeln.NORMATIVE_ZAHLEN['kampagnen_pruefung'],
                reduziert=bool(n < regeln.NORMATIVE_ZAHLEN['kampagnen_pruefung']) or profil.reduziert,
                laufzeit_s=round(time.perf_counter() - t, 2), prozesse=prozesse, code_version=formate.code_version(),
                k_max=k_max, rauschmodell=r.name, staerke=None, verfahren=verfahren.kennung(),
                modellquelle=quelle.kennung()['sha256'], effekte=list(effekte or quelle.effekte))
    return dict(meta=meta, befunde=befunde, wahrheit=wahrheit_quelle(quelle, plan, k_max, rausch, effekte))


# ── R1-d: Rundreise der Schätzer ────────────────────────────────────────────────────────────────────────
R1D_PUNKTE = tuple((s, st) for s in ('N01-A4', 'N04-laufart', 'N03-ungleich') for st in ('L0', 'L2', 'L4'))
R1D_PLAN = dict(n0=20, n_pilot=20, n_bloecke=4)
R1D_SEED = 20261020


def r1d_auftraege(n_saetze=1000, punkte=R1D_PUNKTE, seed_basis=R1D_SEED, plan=R1D_PLAN, profil='ENTW-2026-11',
                  eps_ctrl=2000):
    """Auftragsliste R1-d (je Szenariopunkt n_saetze Phase-0-Sätze); jeder Auftrag ist ein dict mit Seed."""
    return [dict(rechnung='R1-d', version=VERSION, szenario=s, stufe=st, i=i, plan=dict(plan), profil=profil,
                 eps_ctrl_datensaetze=eps_ctrl, seed=zufall.unterseed(seed_basis, 'r1d', s, st, i),
                 seed_kalibrierung=zufall.unterseed(seed_basis, 'r1d_kalibrierung', s))
            for s, st in punkte for i in range(n_saetze)]


def _wahre_parameter(m):
    r = p0m.parameter(m.rausch)
    Ta = m.plan.n_zyklen / m.system.f
    return dict(sigma_a=p0m._arr(r.a('L')).tolist(), sigma_a_K=p0m._arr(r.a('K')).tolist(),
                sigma_delta_grad=p0m._arr(r.p('L')).tolist(), sigma_off_grad=[0.0] + p0m._arr(
                    r.index_versatz_grad, 2).tolist(), sigma_jitter_grad=[0.0] + p0m._arr(r.jitter_grad, 2).tolist(),
                sigma_h_zellen=p0m._arr(r.sigma_h(Ta)).tolist(),
                sigma_mittel_zellen=p0m._arr(r.sigma_mittel(Ta)).tolist())


_KAL_CACHE = {}


def _kalibrierung(sid, m, seed):
    """Kalibrierung P0.1–P0.5 je Szenario (einmal je Szenario und Seed; R1-d prüft die Laufgrößen, nicht P0.4/P0.5)."""
    key = (sid, int(seed))
    if key not in _KAL_CACHE:
        _KAL_CACHE[key] = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)[2]
    return _KAL_CACHE[key]


def _kurz(lg, satz):
    k = lgm.komponenten(lg)
    out = {x: [None if not np.isfinite(v) else float(v) for v in k[x]] for x in (
        'sigma_a', 'sigma_a_oben80', 'sigma_delta_grad', 'sigma_delta_grad_oben80', 'sigma_off_grad',
        'sigma_off_grad_oben80', 'sigma_jitter_grad', 'sigma_h_zellen', 'sigma_mittel_zellen')}
    out['kohaerenz_p'] = [lg['module'][j]['kohaerenz'][x]['p'] for j in range(3) for x in ('amplitude', 'phase')
                          if lg['module'][j]['kohaerenz']]
    u = lg['uebertragung']
    hh = u.get('harmonische', []) if u.get('pruefbar') else None
    out['uebertragung'] = None if hh is None else [h.get('verhaeltnis') for h in hh]
    out['erfasster_anteil'] = None if hh is None else [h.get('erfasster_anteil') for h in hh]
    out['sigma_ref'] = satz['sigma_ref']['sigma_ref']
    out['p_hat'] = satz['p_hat']
    out['diffusion_nachgewiesen'] = bool(lg['nullpunkt']['diffusion'].get('nachgewiesen'))
    return out


def r1d_satz(a):
    """Ein Auftrag von R1-d: Schätzung auf Szenariodaten und Rundreise über das Strukturmodell (Punktschätzer)."""
    plan = kp.plan_aus_dict(dict(a['plan'], p0_anordnung='p07'))
    prof = regeln.profil(a['profil']).mit_reduktion(eps_ctrl_datensaetze=a['eps_ctrl_datensaetze'])
    t = time.perf_counter()
    m = szenarien.modell(a['szenario'], a['stufe'], plan=plan)
    kal = _kalibrierung(a['szenario'], m, a['seed_kalibrierung'])
    laeufe = [l for l in kp.laufplan(m.plan, zufall.strom(a['seed'], 'reihenfolge')) if l['phase'] == 0]
    tab = ebene_h.erzeuge(m, laeufe, zufall.strom(a['seed'], 'generator')).sortiert()
    k = m.system.k_max
    s1 = pilot.satz_fuer_plan(tab, kal, prof, m.system.f, k, a['seed'])
    ung = set(s1['gueltigkeit']['gruende'])
    g = np.array([x['lauf_id'] not in ung for x in tab.koepfe])
    q = p0m.quelle_aus_phase0(tab, g, kal, s1['laufgroessen'], 'punkt')
    m2 = q.modell(plan)
    tab2 = p0m.erzeuge(m2, laeufe, zufall.strom(a['seed'], 'r1d_rundreise'),
                       rng_zusatz=zufall.strom(a['seed'], 'r1d_rundreise_zusatz')).sortiert()
    s2 = pilot.satz_fuer_plan(tab2, kal, prof, m.system.f, k, a['seed'])
    return dict(auftrag=a, wahr=_wahre_parameter(m), schaetzung=_kurz(s1['laufgroessen'], s1),
                rundreise=_kurz(s2['laufgroessen'], s2), laufzeit_s=round(time.perf_counter() - t, 3))


def r1d_auswerten(ergebnisse):
    """Je Szenariopunkt: Mittel und Streuung des Verhältnisses Schätzung/Wahrheit (σ_a, σ_δ, σ_off, Jitter, Boden),
    Überdeckung der oberen 80-%-Grenze (Anteil wahr ≤ oben80; nominal 0,8 je Komponente, marginal), Rundreise
    (Verhältnis erneute Schätzung/Schätzung), Ablehnungsrate der Kohärenzprüfung (p < 0,05), σ̂_ref und p̂."""
    out = {}
    for e in ergebnisse:
        a = e['auftrag']
        out.setdefault(f"{a['szenario']}/{a['stufe']}", []).append(e)
    zus = {}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)                  # Module ohne Größe (Modul 1: σ_off = 0)
        for key, liste in out.items():
            zus[key] = _r1d_punkt(liste)
    return zus


def _r1d_punkt(liste):
    """Zusammenfassung eines Szenariopunkts von R1-d (r1d_auswerten)."""
    z = {}
    for name in ('sigma_a', 'sigma_delta_grad', 'sigma_off_grad', 'sigma_jitter_grad', 'sigma_h_zellen'):
        w = np.array([x['wahr'][name] for x in liste], float)
        s = np.array([[np.nan if v is None else v for v in x['schaetzung'][name]] for x in liste], float)
        rr = np.array([[np.nan if v is None else v for v in x['rundreise'][name]] for x in liste], float)
        with np.errstate(invalid='ignore', divide='ignore'):
            v = s / w
            vr = rr / s
        z[name] = dict(verhaeltnis_mittel=np.nanmean(v, 0).tolist(), verhaeltnis_sd=np.nanstd(v, 0).tolist(),
                       rundreise_mittel=np.nanmean(vr, 0).tolist())
        if name + '_oben80' in liste[0]['schaetzung']:
            o = np.array([[np.nan if v is None else v for v in x['schaetzung'][name + '_oben80']] for x in liste],
                         float)
            z[name]['ueberdeckung_oben80'] = np.nanmean(w <= o, 0).tolist()
    kp_ = np.array([x['schaetzung']['kohaerenz_p'] for x in liste], float)
    z['kohaerenz_ablehnung_0_05'] = float(np.mean(kp_ < 0.05)) if kp_.size else None
    z['sigma_ref_mittel'] = float(np.mean([x['schaetzung']['sigma_ref'] for x in liste]))
    z['p_hat_mittel'] = float(np.mean([x['schaetzung']['p_hat'] for x in liste]))
    z['n'] = len(liste)
    return z


# ── R2-d: Gleichheit auf Ebene der Entscheidungen ───────────────────────────────────────────────────────
R2D_PUNKTE = (('N01-A4', 'L2'), ('N04-laufart', 'L2'))
R2D_SEED = 20261021


def r2d_auftraege(n_kampagnen=400, punkte=R2D_PUNKTE, seed_basis=R2D_SEED, plan=None, n_min=18, bootstrap_B=1000,
                  profil='ENTW-2026-11'):
    """Auftragsliste R2-d: je Punkt Szenariogenerator und Phase-0-Modell (Kalibrier- und Prüfsimulation mit je
    n_kampagnen, Stufe 2, B = bootstrap_B); der Phase-0-Satz, aus dem das Modell geschätzt wird, hat einen eigenen
    Seed."""
    plan = dict(n0=20, n_pilot=20, n_bloecke=24) if plan is None else plan
    out = []
    for s, st in punkte:
        for gen in ('szenario', 'phase0_struktur'):
            out.append(dict(rechnung='R2-d', version=VERSION, szenario=s, stufe=st, generator=gen,
                            n_kal=n_kampagnen, n_pruef=n_kampagnen, plan=dict(plan), n_min=n_min,
                            bootstrap_B=bootstrap_B, profil=profil, seed=zufall.unterseed(seed_basis, 'r2d', s, st),
                            seed_phase0=zufall.unterseed(seed_basis, 'r2d_phase0', s, st)))
    return out


def quelle_aus_szenario_phase0(sid, stufe, plan, seed, profil, grenze='punkt', modell='struktur'):
    """Modellquelle aus einem Phase-0-Satz eines Szenarios (Generator, Kalibrierung, Pilotskript beim k_max des
    Systems): nur die Phase-0-Daten gehen ein, nicht die Szenarioparameter. Rückgabe (Quelle, Satz)."""
    m = szenarien.modell(sid, stufe, plan=plan)
    laeufe = [l for l in kp.laufplan(m.plan, zufall.strom(seed, 'reihenfolge')) if l['phase'] == 0]
    tab = ebene_h.erzeuge(m, laeufe, zufall.strom(seed, 'generator')).sortiert()
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
    s = pilot.satz_fuer_plan(tab, kal, profil, m.system.f, m.system.k_max, seed)
    ung = set(s['gueltigkeit']['gruende'])
    g = np.array([x['lauf_id'] not in ung for x in tab.koepfe])
    return p0m.quelle_aus_phase0(tab, g, kal, s['laufgroessen'], grenze, modell=modell), s


def r2d_punkt(a, prozesse=1):
    """Ein Auftrag von R2-d: Kalibrier- und Prüfsimulation mit dem gewählten Generator; Rückgabe der Raten."""
    from . import kalibrierung
    plan = kp.plan_aus_dict(dict(a['plan'], p0_anordnung='p07'))
    prof = regeln.profil(a['profil']).mit_reduktion(bootstrap_B=a['bootstrap_B'], h3_mc=a['bootstrap_B'],
                                                     eps_ctrl_datensaetze=2000)
    if a['generator'] == 'szenario':
        k = kalibrierung.kalibrieren(a['szenario'], a['stufe'], prof, a['n_kal'], a['n_pruef'], a['seed'], plan,
                                     a['n_min'], prozesse)
    elif a['generator'] == 'phase0_struktur':
        q, _ = quelle_aus_szenario_phase0(a['szenario'], a['stufe'], plan, a['seed_phase0'], prof)
        k = kalibrierung.kalibrieren(a['szenario'], a['stufe'], prof, a['n_kal'], a['n_pruef'], a['seed'], plan,
                                     a['n_min'], prozesse, quelle=q)
    else:
        raise ValueError(f'Generator {a["generator"]!r} unbekannt')
    return dict(auftrag=a, c_H1=k['c_H1'], rauschbias=dict(b0=np.asarray(k['rauschbias']['b0']).tolist()),
                gemeinsam=k['gemeinsame_bestaetigung'], pruefung=k['pruefung'], h2=k['h2'].get('schluessel'),
                raten={x: v for x, v in k['raten_pruefung']['raten'].items() if x.startswith(('H1:', 'H2:'))})


def r2d_vergleich(a, b):
    """Unterschied der Entscheidungsraten zweier R2-d-Ergebnisse mit Standardfehler (Differenz/SE je Rate)."""
    out = {}
    for name in sorted(set(a['raten']) & set(b['raten'])):
        x, y = a['raten'][name], b['raten'][name]
        if x['rate'] is None or y['rate'] is None:
            continue
        se = float(np.hypot(x['mc_se'], y['mc_se']))
        out[name] = dict(differenz=float(y['rate'] - x['rate']), se=se,
                         z=None if se == 0 else float((y['rate'] - x['rate']) / se))
    return out


def r2d_bekannt_gleich(sid, stufe, plan, seed, profil, n_min=18):
    """Variante „bekannt“: Szenarioparameter im Strukturgenerator, Struktur aus Werkzeug 2 mit dem Szenariosystem
    (Szenario ohne Effekte): Laufzusammenfassungen und Entscheidungen bitgleich zum Szenariogenerator."""
    m = szenarien.modell(sid, stufe, plan=plan)
    if m.effekte:
        raise ValueError('Variante „bekannt“ nur für Szenarien ohne Effekte')
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[sid], m, seed)
    q = p0m.Modellquelle(p0m.struktur_system(m.system, k_voll=m.k_voll), p0m.aus_rauschmodell(m.rausch),
                         m.system.delta_profil_grad, kal, m.system.k_max, name=f'bekannt:{sid}')
    a = kette.kette(sid, stufe, profil, plan=plan, seed=seed, n_min=n_min, kalibrierung=kal, mit_wahrheit=False)
    b = kampagne_quelle(q, profil, plan, seed, n_min=n_min)
    teile = ('H1', 'H1Z', 'H2', 'H3', 'H4', 'H0', 'E3')
    ha = formate.sha256_json({h: a['ergebnis'][h] for h in teile})
    hb = formate.sha256_json({h: b['ergebnis'][h] for h in teile})
    return dict(gleich=ha == hb, tabelle_gleich=formate.sha256_bytes(formate.npz_bytes(a['tabelle'].daten)) ==
                formate.sha256_bytes(formate.npz_bytes(b['tabelle'].daten)), ergebnis_sha256=(ha, hb))


# ── R3-d: Planung mit dem Pilotmodell gegen das Szenario-Orakel ─────────────────────────────────────────
R3D_SEED = 20261022


def r3d_auftraege(szenario='N01-V1G0', stufe='L1', n_kandidaten=(16, 20, 24, 28, 32), n_kal=200, n_pruef=200,
                  bootstrap_B=1000, seed_basis=R3D_SEED, profil='ENTW-2026-11', max_aufrufe=None, zeit=None,
                  plan=None):
    """Auftragsliste R3-d (K12-ähnliche Suche in Entwicklungsgröße): je Haken (phase0_modell, szenario_orakel) ein
    Auftrag mit denselben Phase-0-Daten, Kandidaten und Seeds."""
    zeit = zeit or dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21,
                        N_I=0)
    plan = dict(n0=20, n_pilot=20, n_bloecke=24) if plan is None else plan
    return [dict(rechnung='R3-d', version=VERSION, szenario=szenario, stufe=stufe, haken=h,
                 n_kandidaten=list(n_kandidaten), n_kal=n_kal, n_pruef=n_pruef, bootstrap_B=bootstrap_B,
                 profil=profil, max_aufrufe=max_aufrufe, zeit=dict(zeit), plan=dict(plan),
                 seed=zufall.unterseed(seed_basis, 'r3d', szenario, stufe),
                 seed_phase0=zufall.unterseed(seed_basis, 'r3d_phase0', szenario, stufe))
            for h in ('phase0_modell', 'szenario_orakel')]


def r3d_punkt(a, prozesse=1):
    """Ein Auftrag von R3-d: Pilotskript mit Planungshaken auf den Phase-0-Daten des Szenarios (Seed seed_phase0)."""
    from . import planung
    plan = kp.plan_aus_dict(dict(a['plan'], p0_anordnung='p07'))
    prof = regeln.profil(a['profil']).mit_reduktion(bootstrap_B=a['bootstrap_B'], h3_mc=a['bootstrap_B'],
                                                     eps_ctrl_datensaetze=2000)
    m = szenarien.modell(a['szenario'], a['stufe'], plan=plan)
    laeufe = [l for l in kp.laufplan(m.plan, zufall.strom(a['seed_phase0'], 'reihenfolge')) if l['phase'] == 0]
    tab = ebene_h.erzeuge(m, laeufe, zufall.strom(a['seed_phase0'], 'generator'))
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG[a['szenario']], m, a['seed_phase0'])
    prot = []
    sid = a['szenario'] if a['haken'] == 'szenario_orakel' else None
    hk = planung.haken(sid, a['stufe'] if sid else None, prof, a['n_kal'], a['n_pruef'], a['seed'],
                       tuple(a['n_kandidaten']), (20,), plan, prozesse, prot, max_aufrufe=a['max_aufrufe'],
                       rauschquelle=a['haken'])
    pe = pilot.pilot_auswerten(tab, kal, prof, m.system.f, zeit=a['zeit'], seed=a['seed_phase0'], planung=hk)
    s = pe['suche']
    return dict(auftrag=a, suche={x: s.get(x) for x in ('ergebnis', 'k_max', 'N_z', 'n_min', 'n0', 'n', 'reserve_r',
                                                        'planung_quelle', 'grund')},
                aufrufe=[dict(k=p['k'], N_z=p['N_z'], n_min=p.get('n_min'),
                              kandidaten=[{x: c.get(x) for x in ('n_min', 'n0', 'P_gemeinsam', 'mc_se', 'erfuellt',
                                                                 'c_H1')} for c in p.get('kandidaten', [])])
                         for p in prot])
