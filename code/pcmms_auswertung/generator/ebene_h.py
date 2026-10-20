"""Ebene H: Laufzusammenfassungen direkt aus dem Rauschmodell auf Ebene der Harmonischen (Plan AP-13, 2.3).

Je Lauf und bewegtem Modul j: Amplitude Aⱼ = 1 + ε, nicht erfasster Phasenrest δⱼ, erfasster Versatz der Indexphase
und Jitter je Zyklus (Module 2, 3 gegen Modul 1 in Kombinationsläufen). Die Zeiger Σ_c e^{−ikφⱼ,c} entstehen aus den
gezogenen Zyklusphasen; die Harmonische des Laufmittels ist Σⱼ Aⱼ·e^{−ikδⱼ}·ρⱼₖ,Lauf·N_c,k⁽ʲ⁾ (lineare Systeme; für
nichtlineare Effekte im Zeitbereich je Lauf, für den Hertz-Fall linearisiert um die Löserantwort). Dazu weißes
Sensorrauschen je Zelle auf Re/Im N_k und ⟨N_c⟩, die Fünftel aus den Zyklen des ersten und letzten Fünftels mit
eigenem Rauschen (Laufrauschen = Mittel der fünf Fünftel), Rohextrema aus der ungebänderten Zellkurve (negativ
abgeschnitten: Abheben einer Zelle ohne Stoßdynamik, nur für die Regeln G6/S2) mit einem Extremwert des Rauschens.
Ebene H bildet Rampe und Einschwingen nicht ab; das leistet Ebene Z.
"""
import numpy as np

from .. import konventionen as kv
from .. import zusammenfassung as zf

VERSION = 'ebene_h-0.1'


def _extremwert(rng, n_abtast, form):
    """Maximum von n unabhängigen Standardnormalwerten (Gumbel-Näherung)."""
    a = np.sqrt(2 * np.log(n_abtast))
    b = a - (np.log(np.log(n_abtast)) + np.log(4 * np.pi)) / (2 * a)
    return b + rng.gumbel(size=form) / a


def gruppe_signal(modell, specs, rng, rausch):
    """Rauschfreie Signalanteile einer Gruppe gleicher Läufe (gleiche Konfiguration, Laufart, Einstellung) mit den
    gezogenen Laufgrößen. Rückgabe dict mit Zyklusphasen, Zeigern, Zellharmonischen (Kraft, ohne Kette) für Lauf und
    Fünftel und den Laufgrößen; Ebene Z verwendet dieselben Ziehungen."""
    l0 = specs[0]
    n, art, e = len(specs), l0['laufart'], l0['einstellung']
    ant = modell.antwort(e)
    K, Nz = ant.k_voll, modell.plan.n_zyklen
    nf = Nz // 5
    k = np.arange(1, K + 1)
    w = np.zeros(3)
    if art == 'K':
        w[:] = 1.0
        phi_idx = modell.index_soll_grad(l0['konfiguration']['phi_soll_grad'])
    elif art == 'L':
        w[l0['modul'] - 1] = 1.0
        phi_idx = np.zeros(3)
    else:
        phi_idx = np.zeros(3)
    bew = w > 0
    A = np.ones((n, 3))
    dl = np.zeros((n, 3))
    if bew.any():
        A[:, bew] += rausch.a(art) * rng.standard_normal((n, bew.sum()))
        dl[:, bew] = rausch.p(art) * rng.standard_normal((n, bew.sum()))
    off = np.zeros((n, 3))
    jit = np.zeros((n, 3, Nz))
    if art == 'K':
        off[:, 1:] = rausch.index_versatz_grad * rng.standard_normal((n, 2))
        jit[:, 1:, :] = rausch.jitter_grad * rng.standard_normal((n, 2, Nz))
    phi_c = phi_idx[None, :, None] + off[:, :, None] + jit                 # Indexphasen je Zyklus [°]
    z = np.exp(-1j * np.radians(phi_c))
    P = np.ones_like(z)
    Za, Zf, Zl = (np.zeros((n, 3, K), complex) for _ in range(3))
    for i in range(K):
        P = P * z
        Za[:, :, i], Zf[:, :, i], Zl[:, :, i] = P.sum(-1), P[..., :nf].sum(-1), P[..., -nf:].sum(-1)
    fak = (w[None, :] * A)[:, :, None] * np.exp(-1j * k[None, None, :] * np.radians(dl)[:, :, None])
    phase1 = np.array([l['phase'] == 1 for l in specs])
    if art == 'K':
        for eff in modell.effekte_art('kopplung'):
            g = np.ones(K)
            g[(np.asarray(eff['harmonische']) - 1) if eff.get('harmonische') is not None else slice(None)] = 1 - eff['x']
            fak = fak * g[None, None, :]
        for eff in modell.effekte_art('phasenversatz_k'):
            fak[:, eff['modul'] - 1, :] *= np.exp(-1j * k * np.radians(eff['grad']))
        for eff in modell.effekte_art('modul_k'):
            fak[:, eff['modul'] - 1, :] *= 1 + eff['faktor']
    for eff in modell.effekte_art('drift_basis'):
        d = np.broadcast_to(np.asarray(eff['faktor'], float), (3,))
        fak[phase1] *= (1 + d)[None, :, None]
    Fa, Ff, Fl = fak * Za / Nz, fak * Zf / nf, fak * Zl / nf
    if modell.hertz is not None:
        Nkr = _hertz_kraft(modell, l0, art, e, phi_idx, Fa, Ff, Fl)
    else:
        Nkr = [np.einsum('njk,jck->nck', F, ant.Nz_kraft) for F in (Fa, Ff, Fl)]
    zeiger = np.where(bew[None, :, None], Za, np.nan + 1j * np.nan)
    fz = np.where(bew[None, None, :], np.stack([Zf[:, :, 0], Zl[:, :, 0]], 1), np.nan + 1j * np.nan)
    return dict(n=n, art=art, einstellung=e, ant=ant, K=K, Nz=Nz, nf=nf, phi_c=phi_c, zeiger=zeiger, A=A, dl=dl,
                fuenftel_zeiger=fz,
                bew=bew, fak=fak, phi_idx=phi_idx, Nkraft=Nkr[0], Nkraft_f=Nkr[1], Nkraft_l=Nkr[2], phase1=phase1)


def _hertz_kraft(modell, l0, art, e, phi_idx, Fa, Ff, Fl):
    """Hertz-Fall (1 FG, Zellen = Summe/3): Löserantwort der Konfiguration plus lineare Abweichung der
    Laufgrößen über die Einzelmodul-Löserantworten (erste Ordnung)."""
    tab = modell.hertz
    K = Fa.shape[-1]
    k = np.arange(1, K + 1)
    einzel = np.asarray(tab['einzel'])[:, :K]                              # (Modul, k) Summenkraft
    if art == 'K':
        basis = np.asarray(tab['kombination'][l0['konfiguration']['id']])[:K]
        rho0 = np.exp(-1j * np.outer(np.radians(phi_idx), k))
    elif art == 'L':
        basis = np.zeros(K, complex)
        rho0 = np.zeros((3, K))
    else:
        return [np.zeros((Fa.shape[0], 3, K), complex)] * 3
    out = []
    for F in (Fa, Ff, Fl):
        s = basis[None, :] + np.einsum('njk,jk->nk', F - rho0[None], einzel)
        out.append(np.repeat(s[:, None, :] / 3.0, 3, 1))
    return out


def kennlinie(modell, Nkr, F0):
    """Quadratische Kettenkennlinie im Zeitbereich je Zelle, auf das Ausgangssignal der linearen Kette:
    N = F + β·F² (F einschließlich der statischen Zelllast F0); Rückgabe Harmonische und Gleichanteil."""
    effs = modell.effekte_art('kennlinie')
    K = Nkr.shape[-1]
    if not effs:
        return Nkr, np.broadcast_to(F0, Nkr.shape[:-1]).copy()
    beta = np.zeros(3)
    for eff in effs:
        beta = beta + np.broadcast_to(np.asarray(eff['beta'], float), (3,))
    x = F0[None, :, None] + kv.kurve(Nkr)                                  # (n, 3, N_θ)
    y = x + beta[None, :, None] * x ** 2
    return kv.harmonische(y, K), y.mean(-1)


def _gruppen(laeufe):
    """Gruppen gleicher Läufe (Laufart, Modul, Einstellung, Konfiguration) in der Reihenfolge ihres ersten Laufs."""
    gruppen = {}
    for i, l in enumerate(laeufe):
        gruppen.setdefault((l['laufart'], l['modul'], l['einstellung'], l['konfiguration']['id']), []).append(i)
    return [gruppen[key] for key in sorted(gruppen, key=lambda q: gruppen[q][0])]


def ziehen(modell, specs, rng, rausch):
    """Alle Zufallsziehungen einer Gruppe gleicher Läufe (in der Reihenfolge, in der erzeuge den Strom verbraucht) und
    alle zeitunabhängigen Größen. Zeitabhängig ist nur die Nullpunktdrift; sie fügt bilden() zum Laufzeitpunkt hinzu."""
    K = modell.k_voll
    g = gruppe_signal(modell, specs, rng, rausch)
    ant = g['ant']
    Ta = modell.plan.n_zyklen / ant.f
    F0 = ant.F0
    GF = ant.G_F[None]
    Nh, mean = kennlinie(modell, g['Nkraft'] * GF, F0)
    Nh_f, mean_f = kennlinie(modell, g['Nkraft_f'] * GF, F0)
    Nh_l, mean_l = kennlinie(modell, g['Nkraft_l'] * GF, F0)
    gain = np.ones((len(specs), 3))
    for eff in modell.effekte_art('verstaerkung_p1'):
        gain[g['phase1']] *= 1 + np.broadcast_to(np.asarray(eff['faktor'], float), (3,))
    Nh, Nh_f, Nh_l = Nh * gain[:, :, None], Nh_f * gain[:, :, None], Nh_l * gain[:, :, None]
    mean, mean_f, mean_l = mean * gain, mean_f * gain, mean_l * gain
    if specs[0]['laufart'] == 'K':
        for eff in modell.effekte_art('offset_k'):
            mean, mean_f, mean_l = mean + eff['N'] / 3, mean_f + eff['N'] / 3, mean_l + eff['N'] / 3
    # Sensorrauschen: fünf Fünftel mit eigenem Rauschen, das Laufrauschen ist ihr Mittel
    sh, sm = rausch.sigma_h(Ta), rausch.sigma_mittel(Ta)
    m = len(specs)
    r5 = np.sqrt(5.0) * (sh * (rng.standard_normal((m, 5, 3, K)) + 1j * rng.standard_normal((m, 5, 3, K))))
    m5 = np.sqrt(5.0) * sm * rng.standard_normal((m, 5, 3))
    Nrun = Nh + r5.mean(1)
    zm = np.exp(1j * np.radians(g['phi_c'])).mean(-1)
    pm = np.degrees(np.angle(zm)) % 360.0
    sg = np.degrees(np.sqrt(-2 * np.log(np.clip(np.abs(zm), 1e-300, 1.0))))
    # Rohextrema (ganzer Lauf ohne Rampe): ungebänderte Zellkurve, Abheben negativ abgeschnitten
    n_abt = max(int(rausch.f_s_bezug * modell.plan.T_lauf), 10)
    sz = rausch.sigma_zelle
    ev_min = _extremwert(rng, n_abt, (m, 3))
    ev_max = _extremwert(rng, n_abt, (m, 3))
    T0, sT = rausch.temperatur_C
    t_min = T0 - np.abs(sT * rng.standard_normal((m, 3)))
    t_max = T0 + np.abs(sT * rng.standard_normal((m, 3)))
    tp = rausch.t_phi_s[0] + rausch.t_phi_s[1] * rng.standard_normal((m, 3))
    geregelt = (np.arange(3) > 0) & g['bew'] & (specs[0]['laufart'] == 'K')       # Module 2, 3 im Kombinationslauf
    f_m = ant.f + rausch.f_streuung_hz * rng.standard_normal(m)
    return dict(
        g=g, f=ant.f, mean=mean, mean_f=mean_f, mean_l=mean_l, m5=m5, m5m=m5.mean(1), kurve=kv.kurve(Nh), sz=sz,
        ev_min=ev_min, ev_max=ev_max, ld=rausch.lauf_drift_N * 0.4,     # erstes/letztes Fünftel bei ∓0,4 des Laufs
        drift=rausch.nullpunkt_drift_N_je_s,
        fest=dict(Nk_zellen=Nrun, Nk_summe=Nrun.sum(1), fuenftel_Nk=np.stack([(Nh_f + r5[:, 0]).sum(1),
                                                                            (Nh_l + r5[:, 4]).sum(1)], 1),
                  zeiger=g['zeiger'], fuenftel_zeiger=g['fuenftel_zeiger'],
                  phi_mittel_grad=np.where(g['bew'][None], pm, np.nan),
                  sigma_grad=np.where(g['bew'][None], sg, np.nan),
                  sigma_roh_zellen=np.sqrt(0.5 * (np.abs(Nh) ** 2).sum(-1) + sz ** 2),
                  sigma_roh_summe=np.sqrt(0.5 * (np.abs(Nh.sum(1)) ** 2).sum(-1) + 3 * sz ** 2),
                  temperatur_min_zellen=t_min, temperatur_max_zellen=t_max,
                  t_phi=np.where(geregelt[None], tp, np.nan)),
        f_mittel=f_m)


def bilden(modell, z, zeilen, t_mitte, daten, idx):
    """Laufzusammenfassungen der Zeilen `zeilen` einer gezogenen Gruppe zu den Laufzeitpunkten t_mitte (Mitte des
    Laufs, s) in daten[idx]: Nullpunktdrift zum tatsächlichen Zeitpunkt, davon abhängig ⟨N⟩, Fünftelmittel und
    Rohextrema; alle übrigen Felder unverändert aus der Ziehung."""
    zeilen = np.asarray(zeilen, int)
    drift = z['drift'] * np.asarray(t_mitte, float) / 3
    mean, mean_f, mean_l = (z[x][zeilen] + drift[:, None] for x in ('mean', 'mean_f', 'mean_l'))
    m5 = z['m5'][zeilen]
    mrun = mean + z['m5m'][zeilen]
    for name, v in z['fest'].items():
        daten[name][idx] = v[zeilen]
    daten['N_mittel_zellen'][idx] = mrun
    daten['N_mittel'][idx] = mrun.sum(1)
    daten['fuenftel_N_mittel'][idx, 0] = (mean_f + m5[:, 0]).sum(1) - z['ld']
    daten['fuenftel_N_mittel'][idx, 1] = (mean_l + m5[:, 4]).sum(1) + z['ld']
    x = mean[:, :, None] + z['kurve'][zeilen]
    daten['min_roh_zellen'][idx] = np.maximum(x.min(-1), 0.0) - z['sz'] * z['ev_min'][zeilen]
    daten['max_roh_zellen'][idx] = x.max(-1) + z['sz'] * z['ev_max'][zeilen]
    daten['uebersteuert_zellen'][idx] = daten['max_roh_zellen'][idx] >= modell.vollausschlag_N


def kopf(modell, l, z, zeile):
    """Kopf der Laufzusammenfassung eines Laufs l (Zeile `zeile` der gezogenen Gruppe z)."""
    g = z['g']
    return dict(lauf_id=l['lauf_id'], laufart=l['laufart'], modul=l['modul'], einstellung=l['einstellung'],
                konfiguration=l['konfiguration'], phase=l['phase'], block=l['block'], messtag=l['messtag'],
                position=l['position'], kontrollsatz=l['kontrollsatz'], t_start=l['t_start'], t_ende=l['t_ende'],
                f_soll=z['f'], f_mittel=float(z['f_mittel'][zeile]), n_zyklen=g['Nz'], n_fuenftel=g['nf'],
                k_voll=modell.k_voll, n_theta=kv.N_THETA, stoerung=False, aufzeichnung_ok=True,
                park_ok=None if l['laufart'] == 'K' else True, fehlende_kanaele=[], hash_rohdatei=None,
                version_stufe1=VERSION, kalibrier_hash=None, ebene='H')


def erzeuge(modell, laeufe, rng, rausch=None):
    """Laufzusammenfassungen (LaufTabelle) für die Läufe des Plans (Liste aus kampagne.laufplan) zu ihren geplanten
    Zeitpunkten."""
    rausch = modell.rausch if rausch is None else rausch
    n = len(laeufe)
    daten = zf.leere_daten(modell.k_voll, n)
    koepfe = [None] * n
    for idx in _gruppen(laeufe):
        specs = [laeufe[i] for i in idx]
        z = ziehen(modell, specs, rng, rausch)
        bilden(modell, z, np.arange(len(idx)), np.array([0.5 * (l['t_start'] + l['t_ende']) for l in specs]), daten,
               idx)
        for jj, i in enumerate(idx):
            koepfe[i] = kopf(modell, laeufe[i], z, jj)
    _ereignisse(modell, laeufe, koepfe, daten)
    return zf.LaufTabelle(koepfe, daten)


def ereignis_anwenden(modell, eff, kopf_, daten, i):
    """Ein Effekt „ereignis“ auf den Lauf i (Kopf kopf_, Zeile i der Datenfelder)."""
    a = eff['ereignis']
    if a == 'saettigung':
        daten['uebersteuert_zellen'][i, eff.get('zelle', 1) - 1] = True
        daten['max_roh_zellen'][i, eff.get('zelle', 1) - 1] = modell.vollausschlag_N
    elif a == 'indexfehler':
        daten['index_fehler'][i, eff.get('modul', 2) - 1] += eff.get('wert', 1)
    elif a == 'stoerung':
        kopf_['stoerung'] = True
    elif a == 'aufzeichnung':
        kopf_['aufzeichnung_ok'] = False
    elif a == 'park':
        kopf_['park_ok'] = False
    elif a == 'lauf_drift':
        daten['fuenftel_N_mittel'][i, 1] += eff['wert']
    elif a == 'liftoff_zelle':
        daten['min_roh_zellen'][i, eff.get('zelle', 1) - 1] = eff.get('wert', 0.0)
    else:
        raise ValueError(f'Ereignis {a!r} unbekannt')


def _ereignisse(modell, laeufe, koepfe, daten):
    pos = {l['position']: i for i, l in enumerate(laeufe)}
    for eff in modell.effekte_art('ereignis'):
        for p in modell.ereignis_positionen(eff, laeufe):
            if p not in pos:
                continue
            i = pos[p]
            ereignis_anwenden(modell, eff, koepfe[i], daten, i)


class Vorrat:
    """Ziehungen aller geplanten Läufe wie erzeuge (gleicher Strom, gleiche Reihenfolge) für einen Ablauf, der die
    Läufe zu anderen Zeitpunkten ausführt: Der ursprüngliche Versuch eines geplanten Laufs erhält dessen Ziehung,
    gebildet zum tatsächlichen Zeitpunkt; ohne Verschiebung entsteht genau die Tabelle von erzeuge. Zusätzliche
    Versuche (Wiederholungen, eingefügte Referenzläufe) ziehen aus einem eigenen Strom je Versuch und verbrauchen den
    Strom der geplanten Läufe nicht."""

    def __init__(self, modell, laeufe, rng, rausch=None):
        self.modell = modell
        self.rausch = modell.rausch if rausch is None else rausch
        self.ort = {}
        for idx in _gruppen(laeufe):
            z = ziehen(modell, [laeufe[i] for i in idx], rng, self.rausch)
            for jj, i in enumerate(idx):
                self.ort[laeufe[i]['lauf_id']] = (z, jj)
        self.ereignisse = {}
        for eff in modell.effekte_art('ereignis'):
            for p in modell.ereignis_positionen(eff, laeufe):
                self.ereignisse.setdefault(p, []).append(eff)

    def lauf(self, spec, bezug=None, rng=None, ereignisse=()):
        """Laufzusammenfassung (Kopf, Datenzeilen) eines Versuchs mit spec (Kopfangaben einschließlich t_start,
        t_ende). bezug: lauf_id des geplanten Laufs, dessen Ziehung der Versuch verwendet (ursprünglicher Versuch);
        sonst rng: eigener Strom des zusätzlichen Versuchs. Geplante Ereignisse gelten nur für den ursprünglichen
        Versuch ihres Laufs; ereignisse: weitere Effekte „ereignis“ dieses Versuchs."""
        if bezug is not None:
            z, zeile = self.ort[bezug]
        else:
            z, zeile = ziehen(self.modell, [spec], rng, self.rausch), 0
        daten = zf.leere_daten(self.modell.k_voll, 1)
        bilden(self.modell, z, [zeile], [0.5 * (spec['t_start'] + spec['t_ende'])], daten, [0])
        k = kopf(self.modell, spec, z, zeile)
        effs = list(self.ereignisse.get(spec.get('position_geplant'), ())) if bezug is not None else []
        for eff in effs + list(ereignisse):
            ereignis_anwenden(self.modell, eff, k, daten, 0)
        return k, daten, (z, zeile)

    def tabelle(self, laeufe):
        """Laufzusammenfassungen geplanter Läufe zu ihren geplanten Zeitpunkten (gleich den Zeilen von erzeuge)."""
        koepfe, zeilen = [], []
        for l in laeufe:
            k, d, _ = self.lauf(dict(l, position_geplant=l['position']), bezug=l['lauf_id'])
            koepfe.append(k)
            zeilen.append(d)
        return zf.LaufTabelle(koepfe, {f: np.concatenate([d[f] for d in zeilen]) for f in zeilen[0]})
