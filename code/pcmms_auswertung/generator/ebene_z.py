"""Ebene Z: kurze Rohzeitreihen der drei Zellen mit Indeximpulsen (Plan AP-13, Abschnitt 2.3).

Dieselben Laufziehungen wie Ebene H (ebene_h.gruppe_signal): Im Zyklus c trägt Modul j
Re Σ_k Aⱼ·e^{−ikδⱼ}·e^{−ikφⱼ,c}·N_c,k⁽ʲ⁾·e^{ikθ} bei, θ = 2π(t − t_c)/T ab dem Indeximpuls von Modul 1 (bzw. von
Modul j im Lauf Lⱼ). Die Zeitreihe umfasst Rampe (Amplitudenhülle (1 − cos(πt/T_r))/2, Entwicklungsmodell statt einer
Frequenzrampe), Einschwingzeit, das Auswertefenster mit n_zyklen Zyklen und einen kurzen Auslauf. Die lineare Kette
wirkt auf die Harmonischen, eine Kettenkennlinie danach im Zeitbereich, weißes Rauschen je Abtastwert, ADC mit
Vollausschlag (G5) und ganzzahligen Rohwerten. Indexzeitstempel auf dem Raster des Zeitgebers (f_takt). Eine Zelle,
deren lineare Kraft unter null fiele, wird bei null abgeschnitten (Abheben ohne Stoßdynamik; nur Regelprüfung).

Die Abtastrate folgt aus A6 für f und k_max des Prüffalls: f_s ≥ π·k_max·f/√(2·10⁻³), aufgerundet auf 10 Hz.
"""
import numpy as np

from .. import konventionen as kv, rohdaten
from . import ebene_h

VERSION = 'ebene_z-0.1'


def abtastrate(f, kmax, reserve=1.0):
    return float(np.ceil(reserve * kv.abtastrate_a6(f, kmax) / 10.0) * 10.0)


def _rampe(t, T_r):
    return np.where(t < T_r, 0.5 * (1 - np.cos(np.pi * np.clip(t, 0, None) / T_r)), 1.0)


def zeitreihe(modell, g, i, spec, rng, kalib, f_s, T_r=0.5, T_e=0.5, f_takt=1e6, adc_bits=24, rausch=None,
              liftoff_abschneiden=True, ereignisse=()):
    """Rohdaten (inhalt, daten) eines Laufs i der Gruppe g. kalib: dict mit nullpunkt_adc (3) und
    empfindlichkeit_N_je_adc (3) der wahren Kette (Generatorwahrheit, nicht die Schätzung von AP-11).
    ereignisse: Effekte „ereignis“ dieses Laufs (saettigung: kurze Spitze am ADC-Endwert in der Zelle; indexfehler:
    ein fehlender Indeximpuls des Moduls im Fenster; liftoff_zelle: Zellkraft 20 ms lang null; lauf_drift: lineare
    Drift der Summe um wert über den Lauf; stoerung, aufzeichnung, park: Protokolleinträge)."""
    rausch = modell.rausch if rausch is None else rausch
    ant, K, Nz = g['ant'], g['K'], g['Nz']
    f = ant.f
    T = 1.0 / f
    k = np.arange(1, K + 1)
    n_vor = int(np.ceil((T_r + T_e) * f)) + 1
    n_nach = 1
    T_w0 = n_vor * T
    T_ges = T_w0 + (Nz + n_nach) * T
    t0 = rng.uniform(0, 1.0 / f_s)
    t = t0 + np.arange(int(np.floor((T_ges - t0) * f_s))) / f_s
    zyk = np.floor((t - T_w0) / T).astype(int)                     # Zyklusnummer (negativ: vor dem Fenster)
    # Zyklusphasen: Fenster aus den Ziehungen, außerhalb frisch gezogen mit gleichem Modell
    phi_f = g['phi_c'][i]                                           # (3, Nz)
    c_alle = np.arange(-n_vor, Nz + n_nach)
    phi = np.empty((3, c_alle.size))
    phi[:, n_vor:n_vor + Nz] = phi_f
    rest = np.r_[np.arange(n_vor), np.arange(n_vor + Nz, c_alle.size)]
    basis = phi_f.mean(1)
    if g['art'] == 'K':
        jit = rausch.jitter_grad * rng.standard_normal((3, rest.size))
        jit[0] = 0.0
        phi[:, rest] = basis[:, None] + jit                          # Laufversatz wie im Fenster, frischer Jitter
    else:
        phi[:, rest] = basis[:, None]
    fak = g['fak'][i]                                               # (3, K)
    Nz_k = ant.Nz_kraft * ant.G_F[None]                             # (Modul, Zelle, k) mit Kette
    koef = np.einsum('jk,jck,jnk->cnk', fak, Nz_k, np.exp(-1j * np.radians(phi)[:, :, None] * k[None, None, :]))
    # Zeitbereich: e^{ikθ} = e^{ikω(t − T_w0)} über Zyklusgrenzen stetig; Koeffizienten je Zyklus
    ci = zyk + n_vor
    basis_e = np.exp(1j * 2 * np.pi * f * (t - T_w0))
    p = np.ones_like(basis_e)
    sig = np.zeros((3, t.size))
    for kk in range(K):
        p = p * basis_e
        sig += np.real(koef[:, ci, kk] * p[None, :])
    sig *= _rampe(t, T_r)[None, :]
    F = ant.F0[:, None] + sig
    eff = modell.effekte_art('kennlinie')
    if eff:
        beta = sum(np.broadcast_to(np.asarray(e['beta'], float), (3,)) for e in eff)
        F = F + beta[:, None] * F ** 2
    if liftoff_abschneiden:
        F = np.maximum(F, 0.0)
    ereig = {e['ereignis']: e for e in ereignisse}
    if 'liftoff_zelle' in ereig:
        c = ereig['liftoff_zelle'].get('zelle', 1) - 1
        F[c, (t >= T_w0 + 0.3 * Nz * T) & (t < T_w0 + 0.3 * Nz * T + 0.02)] = ereig['liftoff_zelle'].get('wert', 0.0)
    F = F + rausch.nullpunkt_drift_N_je_s * (spec['t_start'] + t)[None, :] / 3
    F = F + rausch.lauf_drift_N * ((t - T_w0) / (Nz * T) - 0.5)[None, :] / 3
    if 'lauf_drift' in ereig:
        F = F + ereig['lauf_drift']['wert'] * ((t - T_w0) / (Nz * T) - 0.5)[None, :] / 3
    F = F + rausch.sigma_zelle * rng.standard_normal(F.shape)
    voll = 2 ** (adc_bits - 1) - 1
    roh = np.asarray(kalib['nullpunkt_adc'])[:, None] + F / np.asarray(kalib['empfindlichkeit_N_je_adc'])[:, None]
    if 'saettigung' in ereig:
        c = ereig['saettigung'].get('zelle', 1) - 1
        roh[c, (t >= T_w0 + 0.5 * Nz * T) & (t < T_w0 + 0.5 * Nz * T + 0.002)] = voll + 1.0
    ueber = (roh >= voll) | (roh <= -voll)
    adc = np.clip(np.rint(roh), -voll, voll).astype(np.int64)
    # Indeximpulse
    t_c = T_w0 + c_alle * T
    idx = {}
    for j in range(3):
        if not g['bew'][j]:
            idx[f'index_modul{j + 1}'] = np.zeros(0)
            continue
        tj = t_c + np.mod(phi[j], 360.0) / 360.0 * T if g['art'] == 'K' else t_c
        if 'indexfehler' in ereig and ereig['indexfehler'].get('modul', 2) == j + 1:
            tj = np.delete(tj, n_vor + Nz // 2)                     # ein fehlender Impuls mitten im Fenster
        tj = tj[(tj >= 0) & (tj < t[-1])]
        idx[f'index_modul{j + 1}'] = rohdaten.index_quantisiert(tj, f_takt)
    T0, sT = rausch.temperatur_C
    inhalt = dict(
        lauf={x: spec[x] for x in ('lauf_id', 'laufart', 'modul', 'einstellung', 'konfiguration', 'phase', 'block',
                                   'messtag', 'position', 'kontrollsatz', 't_start', 't_ende')},
        erfassung=dict(f_soll=f, f_s=f_s, t0=t0, adc=dict(bits=adc_bits, vollausschlag=voll), f_takt=f_takt,
                       kanaele=[dict(name='kraft_adc', art='kraft', einheit='ADC', zellen=[1, 2, 3])]
                       + [dict(name=f'index_modul{j}', art='index', einheit='s', modul=j) for j in (1, 2, 3)]
                       + [dict(name='temperatur_zellen', art='temperatur', einheit='°C')]),
        protokoll=dict(t_rampe_ende=T_r, t_e=T_w0 - T_r, n_zyklen_fenster=Nz, stoerung='stoerung' in ereig,
                       aufzeichnung_ok='aufzeichnung' not in ereig,
                       park_ok=None if g['art'] == 'K' else 'park' not in ereig, bediener='synthetisch', notizen=''),
        umgebung=dict(luftdruck_hPa=1013.0, lufttemperatur_C=21.0, feuchte_pct=45.0, versorgung_V=24.0),
        einstellungen=dict(verstaerkung='fest', filter='analog, gleich in allen Kraftkanälen', firmware='synthetisch',
                           kalibrier_ids=['SYNTH-P0.1']),
        generator=dict(programm=VERSION, szenario=None, seed=None))
    daten = dict(kraft_adc=adc, temperatur_zellen=T0 + sT * rng.standard_normal((3, 2)),
                 t_temperatur=np.array([0.0, float(t[-1])]), uebersteuerung=ueber.any(1), **idx)
    return inhalt, daten


def erzeuge(modell, laeufe, rng, verzeichnis, kennung, kalib, f_s=None, rausch=None, nur=None, **kw):
    """Rohdateien und Manifest für die Läufe (nur: Positionen, die geschrieben werden). Rückgabe Manifestzeilen und
    die Signale der Gruppen (für den Abgleich Ebene Z ↔ H mit denselben Ziehungen)."""
    rausch = modell.rausch if rausch is None else rausch
    f_s = abtastrate(modell.system.f, modell.system.k_max) if f_s is None else f_s
    gruppen = {}
    for i, l in enumerate(laeufe):
        gruppen.setdefault((l['laufart'], l['modul'], l['einstellung'], l['konfiguration']['id']), []).append(i)
    ereig = {}
    for eff in modell.effekte_art('ereignis'):
        for p in modell.ereignis_positionen(eff, laeufe):
            ereig.setdefault(p, []).append(eff)
    zeilen, signale = [], {}
    for key in sorted(gruppen, key=lambda q: gruppen[q][0]):
        specs = [laeufe[i] for i in gruppen[key]]
        g = ebene_h.gruppe_signal(modell, specs, rng, rausch)
        signale[key] = (gruppen[key], g)
        for jj, spec in enumerate(specs):
            if nur is not None and spec['position'] not in nur:
                continue
            inhalt, daten = zeitreihe(modell, g, jj, spec, rng, kalib, f_s, rausch=rausch,
                                      ereignisse=ereig.get(spec['position'], ()), **kw)
            zeilen.append(rohdaten.schreibe_rohlauf(verzeichnis, inhalt, daten, kennung))
    rohdaten.schreibe_manifest(verzeichnis, zeilen, kennung)
    return zeilen, signale
