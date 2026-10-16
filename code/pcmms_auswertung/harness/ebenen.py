"""Abgleich Ebene Z ↔ Ebene H (Plan AP-13, Abschnitt 2.3, Kriterium K19), physikalisch und statistisch getrennt.

1. Rauschfrei (physikalisch-numerisch): dieselben Läufe auf Ebene Z (Rohzeitreihen → Stufe 1) und Ebene H. Erwartet
   wird Gleichheit bis auf die Interpolationsschranke von A6 (Harmonische), die Quantisierung der Zeitstempel
   (Zeiger) und die Abtastung der Extrema. Schranken unten; sie sind Prüfschranken dieser Softwarestufe.
2. Mit Rauschen (statistisch): getrennte Kampagnen auf beiden Ebenen (verschiedene Zufallsströme); verglichen werden
   die Mediane von u_c je Größe (Vorschlag K19: innerhalb 5 %) und die Raten der Ausgänge (innerhalb zwei
   MC-Standardfehlern). Mit wenigen Kampagnen ist das Entwicklungsdiagnostik.
"""
import os

import numpy as np

from .. import stufe1, zufall
from ..generator import ebene_h, ebene_z, kampagne as kp, rauschen, szenarien
from . import dateien, kette, metriken

SCHRANKEN = dict(Nk_zellen=3e-5, N_mittel_zellen=2e-6, zeiger=1e-2, min_roh_zellen=2e-4)
GROESSEN = ['F_min', 'Re N1', 'Im N1', 'Re N2', 'Im N2', 'Re N3', 'Im N3']


def vergleich_rauschfrei(sid, stufe, verzeichnis, n_zyklen=10, seed=3, konfigurationen=None):
    """Rauschfreie Läufe einer Auswahl von Konfigurationen auf beiden Ebenen; Rückgabe größte Abweichungen."""
    m0 = szenarien.modell(sid, stufe, plan=kp.Plan(n0=1, n_pilot=1, n_bloecke=1, n_zyklen=n_zyklen),
                          rausch=rauschen.RAUSCHFREI)
    laeufe = kp.laufplan(m0.plan, zufall.strom(seed, 'reihenfolge'))
    wahl = konfigurationen or {('S112', 1), ('S120', 1), ('L1', 0), ('L2', 0), ('L3', 0), ('R', 0), ('P110_250', 0)}
    pos = [l['position'] for l in laeufe if (l['konfiguration']['id'], l['phase']) in wahl]
    kalw = dict(nullpunkt_adc=[1000.0, -2000.0, 500.0], empfindlichkeit_N_je_adc=[1e-6, 1.1e-6, 0.9e-6])
    kal = dict(zellen=[dict(zelle=c + 1, nullpunkt_adc=kalw['nullpunkt_adc'][c], umrechnung='linear',
                            empfindlichkeit_N_je_adc=kalw['empfindlichkeit_N_je_adc'][c]) for c in range(3)])
    from .. import formate
    zeilen, _ = ebene_z.erzeuge(m0, laeufe, zufall.strom(seed, 'z'), verzeichnis, formate.synth_kennung('ZH', sid),
                                kalw, nur=pos)
    tab = ebene_h.erzeuge(m0, laeufe, zufall.strom(seed, 'h'))
    kmax = m0.system.k_max
    abw = {k: 0.0 for k in SCHRANKEN}
    arten = set()
    for z in zeilen:
        lz = stufe1.laufzusammenfassung(os.path.join(verzeichnis, z['lauf_id']), kal, k_voll=tab.k_voll)
        i = z['position']
        arten.add(lz.kopf['laufart'])
        abw['Nk_zellen'] = max(abw['Nk_zellen'], float(np.abs(lz.daten['Nk_zellen'][:, :kmax] -
                                                              tab.daten['Nk_zellen'][i, :, :kmax]).max()))
        abw['N_mittel_zellen'] = max(abw['N_mittel_zellen'], float(np.abs(lz.daten['N_mittel_zellen'] -
                                                                          tab.daten['N_mittel_zellen'][i]).max()))
        zh, zz = tab.daten['zeiger'][i, :, :kmax], lz.daten['zeiger'][:, :kmax]
        ok = np.isfinite(zh) & np.isfinite(zz)
        if ok.any():
            abw['zeiger'] = max(abw['zeiger'], float(np.abs(zz[ok] - zh[ok]).max()))
        abw['min_roh_zellen'] = max(abw['min_roh_zellen'], float(np.abs(lz.daten['min_roh_zellen'] -
                                                                        tab.daten['min_roh_zellen'][i]).max()))
    return dict(szenario=sid, stufe=stufe, n_laeufe=len(zeilen), laufarten=sorted(arten), abweichung=abw,
                schranken=SCHRANKEN, k_max=kmax, n_zyklen=n_zyklen,
                gleich=bool(all(abw[k] <= SCHRANKEN[k] for k in SCHRANKEN)),
                art='physikalisch-numerisch (rauschfrei)')


def _u_median(erg):
    return np.nanmedian(np.asarray(erg['H1']['tests0']['u'], float), axis=0)


def _beide(auftrag):
    sid, stufe, profil, plan, s, n_min, werkzeug8, ziel, behalten = auftrag
    rz = dateien.kette_dateien(ziel, sid, stufe, profil, plan=plan, seed=s, ebene='Z', n_min=n_min,
                               werkzeug8=werkzeug8)
    rh = kette.kette(sid, stufe, profil, plan=plan, seed=s, n_min=n_min, werkzeug8=werkzeug8, mit_wahrheit=False)
    if not behalten:
        import shutil
        shutil.rmtree(ziel, ignore_errors=True)
    return {e: (_u_median(erg), {h: erg[h]['ausgang'] for h in ('H1', 'H2', 'H1Z', 'H4')})
            for e, erg in (('Z', rz['ergebnis']), ('H', rh['ergebnis']))}


def vergleich_verrauscht(sid, stufe, profil, n_kampagnen, seed_basis, verzeichnis, plan, n_min=None, werkzeug8=None,
                         prozesse=1, behalten=False):
    """Getrennte Kampagnen auf Ebene Z (Dateikette mit Stufe 1) und Ebene H; Mediane von u_c und Raten.
    Die Rohdaten der Ebene Z werden nach der Auswertung gelöscht, außer behalten=True."""
    auftraege = [(sid, stufe, profil, plan, zufall.unterseed(seed_basis, 'ebenen', sid, stufe, i), n_min, werkzeug8,
                  os.path.join(verzeichnis, f'z{i:03d}'), behalten) for i in range(n_kampagnen)]
    if prozesse > 1:
        from .kampagnen import THREAD_VARIABLEN
        import concurrent.futures as cf
        import multiprocessing as mp
        alt = {v: os.environ.get(v) for v in THREAD_VARIABLEN}
        os.environ.update({v: '1' for v in THREAD_VARIABLEN})
        try:
            with cf.ProcessPoolExecutor(prozesse, mp_context=mp.get_context('spawn')) as ex:
                teile = list(ex.map(_beide, auftraege))
        finally:
            for v, w in alt.items():
                os.environ.pop(v, None) if w is None else os.environ.__setitem__(v, w)
    else:
        teile = [_beide(a) for a in auftraege]
    u = {e: [t[e][0] for t in teile] for e in ('Z', 'H')}
    aus = {e: [t[e][1] for t in teile] for e in ('Z', 'H')}
    kw = dict(szenario=sid, stufe=stufe, profil=profil.id)
    med = {e: np.nanmedian(np.stack(u[e]), 0) for e in u}
    rel = (med['Z'] - med['H']) / med['H']
    raten = {}
    for h in ('H1', 'H2', 'H1Z', 'H4'):
        for a in ('bestätigt', 'falsifiziert', 'nicht entscheidbar'):
            rz_ = metriken.rate(sum(x[h] == a for x in aus['Z']), n_kampagnen, f'P({h} {a}) Ebene Z', **kw)
            rh_ = metriken.rate(sum(x[h] == a for x in aus['H']), n_kampagnen, f'P({h} {a}) Ebene H', **kw)
            raten[f'{h}: {a}'] = dict(Z=rz_, H=rh_, innerhalb_2se=metriken.innerhalb(rz_, rh_))
    return dict(szenario=sid, stufe=stufe, n=n_kampagnen, u_c_median=dict(Z=dict(zip(GROESSEN, med['Z'].tolist())),
                                                                         H=dict(zip(GROESSEN, med['H'].tolist()))),
                u_c_relativ=dict(zip(GROESSEN, rel.tolist())), u_c_innerhalb_5_prozent=bool(np.all(np.abs(rel) <= 0.05)),
                raten=raten, art='statistisch (verrauscht, getrennte Zufallsströme)',
                lesart='Entwicklungsdiagnostik' if n_kampagnen < 1000 else 'normative Kampagnenzahl')
