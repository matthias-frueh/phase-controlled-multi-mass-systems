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
    return dict(n=n, art=art, einstellung=e, ant=ant, K=K, Nz=Nz, nf=nf, phi_c=phi_c, zeiger=zeiger, A=A, dl=dl,
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


def erzeuge(modell, laeufe, rng, rausch=None):
    """Laufzusammenfassungen (LaufTabelle) für die Läufe des Plans (Liste aus kampagne.laufplan)."""
    rausch = modell.rausch if rausch is None else rausch
    K = modell.k_voll
    n = len(laeufe)
    daten = zf.leere_daten(K, n)
    koepfe = [None] * n
    gruppen = {}
    for i, l in enumerate(laeufe):
        gruppen.setdefault((l['laufart'], l['modul'], l['einstellung'], l['konfiguration']['id']), []).append(i)
    T_a = modell.plan.n_zyklen / modell.system.f
    for key in sorted(gruppen, key=lambda q: gruppen[q][0]):
        idx = gruppen[key]
        specs = [laeufe[i] for i in idx]
        g = gruppe_signal(modell, specs, rng, rausch)
        ant = g['ant']
        Ta = modell.plan.n_zyklen / ant.f
        F0 = ant.F0
        GF = ant.G_F[None]
        Nh, mean = kennlinie(modell, g['Nkraft'] * GF, F0)
        Nh_f, mean_f = kennlinie(modell, g['Nkraft_f'] * GF, F0)
        Nh_l, mean_l = kennlinie(modell, g['Nkraft_l'] * GF, F0)
        gain = np.ones((len(idx), 3))
        for eff in modell.effekte_art('verstaerkung_p1'):
            gain[g['phase1']] *= 1 + np.broadcast_to(np.asarray(eff['faktor'], float), (3,))
        Nh, Nh_f, Nh_l = Nh * gain[:, :, None], Nh_f * gain[:, :, None], Nh_l * gain[:, :, None]
        mean, mean_f, mean_l = mean * gain, mean_f * gain, mean_l * gain
        if key[0] == 'K':
            for eff in modell.effekte_art('offset_k'):
                mean, mean_f, mean_l = mean + eff['N'] / 3, mean_f + eff['N'] / 3, mean_l + eff['N'] / 3
        t_mitte = np.array([0.5 * (l['t_start'] + l['t_ende']) for l in specs])
        drift = rausch.nullpunkt_drift_N_je_s * t_mitte / 3
        mean, mean_f, mean_l = mean + drift[:, None], mean_f + drift[:, None], mean_l + drift[:, None]
        # Sensorrauschen: fünf Fünftel mit eigenem Rauschen, das Laufrauschen ist ihr Mittel
        sh, sm = rausch.sigma_h(Ta), rausch.sigma_mittel(Ta)
        m = len(idx)
        r5 = np.sqrt(5.0) * (sh * (rng.standard_normal((m, 5, 3, K)) + 1j * rng.standard_normal((m, 5, 3, K))))
        m5 = np.sqrt(5.0) * sm * rng.standard_normal((m, 5, 3))
        Nrun = Nh + r5.mean(1)
        mrun = mean + m5.mean(1)
        ld = rausch.lauf_drift_N * 0.4                                    # erstes/letztes Fünftel bei ∓0,4 des Laufs
        daten['Nk_zellen'][idx] = Nrun
        daten['Nk_summe'][idx] = Nrun.sum(1)
        daten['N_mittel_zellen'][idx] = mrun
        daten['N_mittel'][idx] = mrun.sum(1)
        daten['fuenftel_Nk'][idx, 0] = (Nh_f + r5[:, 0]).sum(1)
        daten['fuenftel_Nk'][idx, 1] = (Nh_l + r5[:, 4]).sum(1)
        daten['fuenftel_N_mittel'][idx, 0] = (mean_f + m5[:, 0]).sum(1) - ld
        daten['fuenftel_N_mittel'][idx, 1] = (mean_l + m5[:, 4]).sum(1) + ld
        daten['zeiger'][idx] = g['zeiger']
        zm = np.exp(1j * np.radians(g['phi_c'])).mean(-1)
        pm = np.degrees(np.angle(zm)) % 360.0
        sg = np.degrees(np.sqrt(-2 * np.log(np.clip(np.abs(zm), 1e-300, 1.0))))
        daten['phi_mittel_grad'][idx] = np.where(g['bew'][None], pm, np.nan)
        daten['sigma_grad'][idx] = np.where(g['bew'][None], sg, np.nan)
        # Rohextrema (ganzer Lauf ohne Rampe): ungebänderte Zellkurve, Abheben negativ abgeschnitten
        x = mean[:, :, None] + kv.kurve(Nh)
        n_abt = max(int(rausch.f_s_bezug * modell.plan.T_lauf), 10)
        sz = rausch.sigma_zelle
        daten['min_roh_zellen'][idx] = np.maximum(x.min(-1), 0.0) - sz * _extremwert(rng, n_abt, (m, 3))
        daten['max_roh_zellen'][idx] = x.max(-1) + sz * _extremwert(rng, n_abt, (m, 3))
        daten['uebersteuert_zellen'][idx] = daten['max_roh_zellen'][idx] >= modell.vollausschlag_N
        daten['sigma_roh_zellen'][idx] = np.sqrt(0.5 * (np.abs(Nh) ** 2).sum(-1) + sz ** 2)
        daten['sigma_roh_summe'][idx] = np.sqrt(0.5 * (np.abs(Nh.sum(1)) ** 2).sum(-1) + 3 * sz ** 2)
        T0, sT = rausch.temperatur_C
        daten['temperatur_min_zellen'][idx] = T0 - np.abs(sT * rng.standard_normal((m, 3)))
        daten['temperatur_max_zellen'][idx] = T0 + np.abs(sT * rng.standard_normal((m, 3)))
        tp = rausch.t_phi_s[0] + rausch.t_phi_s[1] * rng.standard_normal((m, 3))
        geregelt = (np.arange(3) > 0) & g['bew'] & (key[0] == 'K')         # Module 2, 3 im Kombinationslauf
        daten['t_phi'][idx] = np.where(geregelt[None], tp, np.nan)
        f_m = ant.f + rausch.f_streuung_hz * rng.standard_normal(m)
        for jj, i in enumerate(idx):
            l = laeufe[i]
            koepfe[i] = dict(lauf_id=l['lauf_id'], laufart=l['laufart'], modul=l['modul'],
                             einstellung=l['einstellung'], konfiguration=l['konfiguration'], phase=l['phase'],
                             block=l['block'], messtag=l['messtag'], position=l['position'],
                             kontrollsatz=l['kontrollsatz'], t_start=l['t_start'], t_ende=l['t_ende'], f_soll=ant.f,
                             f_mittel=float(f_m[jj]), n_zyklen=g['Nz'], n_fuenftel=g['nf'], k_voll=K,
                             n_theta=kv.N_THETA, stoerung=False, aufzeichnung_ok=True,
                             park_ok=None if l['laufart'] == 'K' else True, fehlende_kanaele=[], hash_rohdatei=None,
                             version_stufe1=VERSION, kalibrier_hash=None, ebene='H')
    _ereignisse(modell, laeufe, koepfe, daten)
    return zf.LaufTabelle(koepfe, daten)


def _ereignisse(modell, laeufe, koepfe, daten):
    pos = {l['position']: i for i, l in enumerate(laeufe)}
    for eff in modell.effekte_art('ereignis'):
        for p in modell.ereignis_positionen(eff, laeufe):
            if p not in pos:
                continue
            i = pos[p]
            a = eff['ereignis']
            if a == 'saettigung':
                daten['uebersteuert_zellen'][i, eff.get('zelle', 1) - 1] = True
                daten['max_roh_zellen'][i, eff.get('zelle', 1) - 1] = modell.vollausschlag_N
            elif a == 'indexfehler':
                daten['index_fehler'][i, eff.get('modul', 2) - 1] += eff.get('wert', 1)
            elif a == 'stoerung':
                koepfe[i]['stoerung'] = True
            elif a == 'aufzeichnung':
                koepfe[i]['aufzeichnung_ok'] = False
            elif a == 'park':
                koepfe[i]['park_ok'] = False
            elif a == 'lauf_drift':
                daten['fuenftel_N_mittel'][i, 1] += eff['wert']
            elif a == 'liftoff_zelle':
                daten['min_roh_zellen'][i, eff.get('zelle', 1) - 1] = eff.get('wert', 0.0)
            else:
                raise ValueError(f'Ereignis {a!r} unbekannt')
