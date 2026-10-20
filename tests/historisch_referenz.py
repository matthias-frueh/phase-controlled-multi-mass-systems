"""Historische Referenz für die Gleichheitsprüfungen unter AF/ENTW-2026-10 (gegen main, Stand PR #23).

Dieselben Rechnungen laufen mit dem Code von main (Erzeugung der Referenzdatei) und mit dem aktuellen Code (Tests
test_e3_auswertung, test_d_laufgroessen): E3-Ausgabe einer kleinen Kampagne unter beiden historischen Profilen und
Pilotskript, Planungshaken (Kalibrierung als Attrappe), Teil B und Satz beim k des Plans unter ENTW-2026-10. Der Plan
hat die historische Anordnung der Referenzläufe (wie main). Verglichen wird strukturell mit Toleranz (vergleich):
gleiche Schlüssel, Zeichenketten und Wahrheitswerte exakt, ganze Zahlen exakt (wenn beide ganz sind), Zahlen sonst
relativ bis rtol = 1e-6; in Zahlenfeldern gilt zusätzlich eine absolute Grenze von 1e-12 des größten Betrags im Feld
(Auslöschungsreste), Kennwerte sind auf den größten Betrag normiert. Prüfsummen über Gleitkommadaten (Schlüssel mit
„sha256“ oder „hash“) und die Codeversion sind ausgenommen; Rauschmodelle und Ablaufoptionen gehen als Struktur ein,
nicht als Darstellungstext. Damit hängt die Prüfung nicht an den letzten Bits der Rechenumgebung (BLAS, libm,
Summationsreihenfolge, Darstellung von NumPy-Zahlen). Grenze: Zahlenfelder mit mehr als LANG Werten gehen nur über
Kennwerte ein (Form, Summen, Extrema, erste Werte und zwei positionsgewichtete Summen); diese erkennen Wertänderungen
und Vertauschungen, aber nicht jede denkbare Änderung, die alle Kennwerte zugleich erhält.

Referenz erzeugen (Code von main in VERZEICHNIS/code):
    python3 tests/historisch_referenz.py VERZEICHNIS tests/fixtures/historisch_main_referenz.json
"""
import json
import sys

RTOL = 1e-6                 # relativ, für alle Zahlen
FELD_ATOL = 1e-12           # absolut, bezogen auf den größten Betrag eines Zahlenfelds bzw. normierte Kennwerte
AUSGENOMMEN = ('sha256', 'hash', 'code_version')
ZEIT = dict(T_park=2.0, T_ramp=2.0, T_ab=1.0, T_eP=4.0, T_aP=10.0, T_verfuegbar=4 * 86400.0, d=2, N_K=21, N_I=0)
SCHRITT = 0.7548776662466927    # irrationale Schrittweite der Positionsgewichte


def _plan(kp, **kw):
    """Plan mit der historischen Anordnung der Referenzläufe (main kennt das Feld noch nicht)."""
    p = kp.Plan(**kw)
    return p.mit(p0_anordnung='historisch') if hasattr(p, 'p0_anordnung') else p


LANG = 64          # längere Zahlenfelder (etwa Bootstrap-Replikate) gehen als Kennwerte ein


def _kennwerte(a):
    """Kennwerte eines langen Zahlenfelds (je Real- und Imaginärteil): Form, Zahl und Lage der nicht endlichen Werte,
    größter Betrag (_skala) und, auf ihn normiert, Summe, Quadratsumme, Extrema, die ersten vier Werte und zwei
    positionsgewichtete Summen (Gewichte cos und sin der Position mal SCHRITT; erkennen Vertauschungen)."""
    import numpy as np
    a = np.asarray(a)
    teile = (('re', a.real), ('im', a.imag)) if np.iscomplexobj(a) else (('', a.astype(float)),)
    out = dict(_form=list(a.shape))
    for name, x in teile:
        x = x.ravel()
        f = np.isfinite(x)
        v = np.where(f, x, 0.0)
        s = float(np.abs(v).max()) if v.size else 0.0
        q = s if s > 0 else 1.0
        w = np.arange(x.size) * SCHRITT
        out[name + '_nicht_endlich'] = int((~f).sum())
        out[name + '_nicht_endlich_lage'] = float((np.flatnonzero(~f) * SCHRITT % 1.0).sum())
        out[name + '_skala'] = s
        out[name + '_summe'] = float(v.sum() / q)
        out[name + '_quadrate'] = float((v * v).sum() / q / q)
        out[name + '_min'] = float(x[f].min() / q) if f.any() else None
        out[name + '_max'] = float(x[f].max() / q) if f.any() else None
        out[name + '_erste'] = [float(y / q) if np.isfinite(y) else None for y in x[:4]]
        out[name + '_cos'] = float(v @ np.cos(w) / q)
        out[name + '_sin'] = float(v @ np.sin(w) / q)
    return out


def jsonbar(o):
    """Strukturen mit numpy-Werten als JSON-Werte (komplex als [re, im], nicht endlich als None; Zahlenfelder mit mehr
    als LANG Werten als Kennwerte)."""
    import numpy as np
    if isinstance(o, dict):
        return {str(k): jsonbar(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        try:
            a = np.asarray(o)
        except ValueError:
            a = None
        if a is not None and a.dtype.kind in 'fciub' and a.size > LANG:
            return _kennwerte(a)
        return [jsonbar(v) for v in o]
    if isinstance(o, np.ndarray):
        if o.dtype.kind in 'fciub' and o.size > LANG:
            return _kennwerte(o)
        return jsonbar(o.tolist())
    if isinstance(o, (complex, np.complexfloating)):
        return [jsonbar(float(np.real(o))), jsonbar(float(np.imag(o)))]
    if isinstance(o, (float, np.floating)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _struktur(o):
    """Datenklasse als Struktur (ihre Zahlen werden mit Toleranz verglichen), sonst ihr Text."""
    import dataclasses
    return jsonbar(dataclasses.asdict(o)) if dataclasses.is_dataclass(o) and not isinstance(o, type) else str(o)


def e3_ausgaben():
    from pcmms_auswertung import regeln
    from pcmms_auswertung.generator import kampagne as kp
    from pcmms_auswertung.harness import kette
    plan = _plan(kp, n0=20, n_pilot=20, n_bloecke=24)
    out = {}
    for name in ('AF-2026-10', 'ENTW-2026-10'):
        prof = regeln.profil(name).mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=1000)
        r = kette.kette('N01-A4', 'L1', prof, plan=plan, seed=7, n_min=18, mit_wahrheit=False)
        out[name] = jsonbar(r['ergebnis']['E3'])
    return out


def _verfahren(v):
    """Bindung, Ablauf und Optionen eines Verfahrens (ohne die Darstellung, die neue Felder ändern)."""
    return None if v is None else dict(bindung=v.bindung, ablauf=v.ablauf, optionen=_struktur(v.optionen))


def pilot_teil_b():
    """Pilotskript ohne und mit Planungshaken (Kalibrierung als Attrappe), Teil B und Satz unter ENTW-2026-10."""
    from pcmms_auswertung import pilot, regeln, teil_b
    from pcmms_auswertung.generator import kampagne as kp, szenarien
    from pcmms_auswertung.harness import kette, planung
    hist = regeln.profil('ENTW-2026-10').mit_reduktion(bootstrap_B=200, eps_ctrl_datensaetze=300, h3_mc=200)
    plan = _plan(kp, n0=20, n_pilot=20, n_bloecke=24)
    m, laeufe, tab = kette.kampagne_erzeugen('N01-A4', 'L1', plan, 5)
    _, _, kal = kette.kalibrierung_erzeugen(szenarien.KATALOG['N01-A4'], m, 5)
    t0 = tab.auswahl(tab.spalte('phase', int) == 0)
    out = dict(pilot_offen=pilot.pilot_auswerten(t0, kal, hist, m.system.f, zeit=ZEIT, seed=5))
    gesehen = []
    import dataclasses
    plan_dict = getattr(kp, 'plan_dict', dataclasses.asdict)          # main: asdict (ohne Feld p0_anordnung)

    def attrappe(sid_, stufe_, profil_, n_kal, n_pruef, seed, plan=None, n_min=None, **kw):
        gesehen.append(dict(sid=sid_, stufe=stufe_, profil=profil_.id, n_kal=n_kal, n_pruef=n_pruef, seed=seed,
                            plan=plan_dict(plan), n_min=n_min, rausch=[_struktur(r) for r in kw.get('rauschvarianten')],
                            k_max=kw.get('k_max'), verfahren=_verfahren(kw.get('verfahren'))))
        return dict(gemeinsame_bestaetigung=dict(rate=0.9 if n_min >= 18 else 0.5, mc_se=0.0, zaehler=1, nenner=1),
                    c_H1=dict(wert=3.7), h2=dict(schluessel='perzentil_0.95'), pruefung=None)
    alt = planung.kalibrierung.kalibrieren
    planung.kalibrierung.kalibrieren = attrappe
    try:
        prot = []
        hk = planung.haken('N01-A4', 'L1', hist, 2, 2, 77, n_kandidaten=(16, 18), n0_kandidaten=(20,), plan_basis=plan,
                           protokoll=prot, max_aufrufe=2)
        pe = pilot.pilot_auswerten(t0, kal, hist, m.system.f, zeit=ZEIT, seed=5, planung=hk)
    finally:
        planung.kalibrierung.kalibrieren = alt
    s = pe['suche']
    pl = dict(kette.plan_info(m, s['n_min']), n=s['n'], r=s['reserve_r'], n0=s['n0'], k_max=s['k_max'], N_z=s['N_z'],
              zeit=ZEIT, T_lauf=s['T_lauf'], p_hat=s['p_hat'])
    tb = teil_b.erstellen(t0, kal, pe, hist, pl, kette.testvorgabe_werkzeug8(), seed_b0=1, B=50)
    out.update(pilot_planung=pe, haken_aufrufe=gesehen, haken_protokoll=prot, teil_b=tb,
               satz=pilot.satz_fuer_plan(t0, kal, hist, m.system.f, 9, 5), ergebnis_suche=s['ergebnis'])
    return jsonbar(out)


def lies_referenz():
    """Referenzdatei tests/fixtures/historisch_main_referenz.json (mit dem Code von main erzeugt)."""
    import os
    with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'historisch_main_referenz.json'),
              encoding='utf-8') as f:
        return json.load(f)


def _groesster_betrag(o):
    """Größter Betrag der Zahlen eines (geschachtelten) Zahlenfelds, ohne in Strukturen abzusteigen."""
    if isinstance(o, list):
        return max((_groesster_betrag(x) for x in o), default=0.0)
    return abs(o) if isinstance(o, (int, float)) and not isinstance(o, bool) else 0.0


def vergleich(a, b, pfad='', atol=0.0, im_feld=False):
    """Abweichungen zwischen zwei JSON-Strukturen (Liste von Texten, leer bei Gleichheit im Sinne des Moduls)."""
    import math
    if isinstance(a, dict) and isinstance(b, dict):
        kennwerte = '_form' in a or '_form' in b
        out = []
        for k in sorted(set(a) | set(b)):
            if any(x in k for x in AUSGENOMMEN):
                continue
            if k not in a or k not in b:
                out.append(f'{pfad}/{k}: nur in {"neu" if k not in a else "Referenz"}')
                continue
            tol = FELD_ATOL if kennwerte and not k.endswith('_skala') else 0.0       # Kennwerte sind normiert
            out += vergleich(a[k], b[k], f'{pfad}/{k}', tol)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f'{pfad}: Länge {len(a)} ≠ {len(b)}']
        if not im_feld:
            atol = max(atol, FELD_ATOL * max(_groesster_betrag(a), _groesster_betrag(b)))
        return [x for i, (u, v) in enumerate(zip(a, b)) for x in vergleich(u, v, f'{pfad}/{i}', atol, True)]
    if isinstance(a, bool) or isinstance(b, bool):
        return [] if type(a) is type(b) and a == b else [f'{pfad}: {a!r} ≠ {b!r}']
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return [] if a == b else [f'{pfad}: {a!r} ≠ {b!r}']
    if isinstance(a, int) and isinstance(b, int):
        return [] if a == b else [f'{pfad}: {a} ≠ {b}']
    return [] if math.isclose(a, b, rel_tol=RTOL, abs_tol=atol) else [f'{pfad}: {a!r} ≠ {b!r}']


if __name__ == '__main__':
    code, ziel = sys.argv[1], sys.argv[2]
    sys.path.insert(0, code.rstrip('/') + '/code')
    import subprocess
    stand = subprocess.run(['git', '-C', code, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    ref = dict(beschreibung='Referenz der historischen Profile, mit dem Code von main berechnet (tests/'
                            'historisch_referenz.py); Vergleich mit Toleranz, nicht bitgleich über Umgebungen',
               main=stand, e3=e3_ausgaben(), pilot_teil_b=pilot_teil_b())
    with open(ziel, 'w', encoding='utf-8') as f:
        json.dump(ref, f, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    print(ziel, stand)
