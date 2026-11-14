"""Kennwerte berechneter Felder und ihr Vergleich mit Toleranz (Ergebnisprüfung; Entscheidung E-4 vom 12.11.2026;
Untersuchung und Messwerte: docs/kennwerte_untersuchung_2026-11-13/bericht.md).

Wozu. Eine Prüfsumme über berechnete Gleitkommafelder gilt nur für genau einen Rechner: Dieselbe Rechnung ergibt mit
einem anderen Rechenkern der BLAS-Bibliothek Werte, die sich im Rundungsrauschen unterscheiden (in den Feldern der
Prüfsätze gemessen bis 6,5·10⁻¹⁴ des größten Betrags eines Feldes), und damit eine andere Prüfsumme. Die Herkunft
berechneter Daten belegt deshalb der Herkunftsnachweis (herkunft.py), der keine Gleitkommazahl enthält. Dieses Modul
prüft daneben die Werte: wenige Kennwerte je Feld, verglichen mit einer Toleranz.

Kennwerte eines Gleitkommafeldes (feld). Das Feld wird in Speicherreihenfolge (C) zu einem reellen Vektor x₀ … x₍ₙ₋₁₎;
komplexe Zahlen tragen Real- und Imaginärteil nacheinander bei. Nicht endliche Einträge (NaN, ±∞) zählen als 0 und
werden getrennt geführt.

    n            Zahl der reellen Einträge
    summe        Σ xᵢ
    quadrat      Σ xᵢ²
    gewichtet    Σ gᵢ·xᵢ für zwei feste Gewichtsfolgen gᵢ = ((a·i + c) mod p)/p (GEWICHTE); sie hängen von der
                 Stelle i ab und erkennen deshalb vertauschte oder verschobene Einträge
    minimum, maximum
    nicht_endlich   Zahl und SHA-256 des Musters der nicht endlichen Einträge (exakt)

Die Summen sind exakt gerundet (math.fsum), die Gewichte entstehen aus ganzen Zahlen. Gleiche Felder ergeben damit
auf jedem Rechner dieselben Kennwerte; Unterschiede in den Kennwerten stammen aus den Feldern. Felder mit ganzen
Zahlen oder Wahrheitswerten erhalten statt dessen die SHA-256-Prüfsumme ihrer Werte: Sie sind exakt.

Vergleich (vergleich, vergleich_felder). Zulässig ist je Eintrag eine Abweichung τ = rtol·M + atol; M ist der größte
Betrag des Feldes. Der Bezug auf M statt auf den einzelnen Eintrag folgt der Messung: Die Abweichung eines Eintrags
zwischen zwei Rechenkernen richtet sich nach der Größe des Feldes, nicht nach der des Eintrags (Einträge nahe null
weichen relativ zu sich selbst bis 100 % ab, relativ zu M höchstens 6,5·10⁻¹⁴;
docs/kennwerte_untersuchung_2026-11-13/bericht.md). Daraus folgen die Toleranzen der
Kennwerte so, dass der Vergleich nie anschlägt, wenn jeder Eintrag innerhalb von τ liegt:

    summe, gewichtet             n·τ
    quadrat                      (2·M + τ)·n·τ
    minimum, maximum             τ

Form, Datentyp, Zahl der Einträge, das Muster der nicht endlichen Einträge und die Prüfsummen exakter Felder müssen
gleich sein.

Was der Vergleich leistet und was nicht. Er erkennt jede systematische Änderung eines Feldes oberhalb von rtol,
vertauschte oder verschobene Einträge, geänderte Extremwerte und jede Änderung an Form, Typ, NaN-Muster und exakten
Feldern. Die Änderung eines einzelnen Eintrags erkennt er sicher erst oberhalb von n·τ, also n-mal gröber als ein
Vergleich Eintrag für Eintrag (bei den größten Feldern der Prüfsätze, n = 3,6·10⁵, ab 3,6·10⁻⁵·M), es sei denn, sie
verschiebt Minimum oder Maximum. Ein Vergleich Eintrag für Eintrag braucht die vollen Bezugsfelder.

Liegen beide Objekte vollständig vor (zwei Rechnungen im selben Lauf), vergleicht vergleich_objekt sie Eintrag für
Eintrag mit derselben Toleranz je Feld: Texte, ganze Zahlen, Wahrheitswerte und None exakt, Gleitkommazahlen und
-felder innerhalb von τ.

Das Modul liest keine Wahrheit, keinen Generator und keinen Harness; Pilotskript und Teil B dürfen es verwenden.
"""
import math

import numpy as np

from . import formate

VERSION = 'kennwerte-1'
RTOL = 1e-10            # zulässige Abweichung je Eintrag relativ zum größten Betrag des Feldes
ATOL = 1e-12            # und absolut (N, °, s …); entspricht der bisherigen Rundung der Prüfsätze auf 12 Stellen
GEWICHTE = ((7919, 1, 104729), (15485863, 7, 1299709))      # (a, c, p) mit p prim: gᵢ = ((a·i + c) mod p)/p
SUMMEN = ('summe', 'gewichtet_1', 'gewichtet_2')            # Kennwerte mit der Toleranz n·τ
MUSTER = {'nan': 1, '+inf': 2, '-inf': 3}


class KennwertFehler(formate.FormatFehler):
    """Kennwerte nicht bildbar oder nicht vergleichbar."""


def toleranz(rtol=RTOL, atol=ATOL):
    return dict(rtol=float(rtol), atol=float(atol), bezug='je Eintrag τ = rtol·M + atol, M größter Betrag des Feldes')


def _reell(a):
    """Feld als reeller Vektor in Speicherreihenfolge (C); komplex: Re und Im nacheinander."""
    a = np.ascontiguousarray(a)
    if a.dtype.kind == 'c':
        a = a.astype(np.complex128, copy=False)
        return np.stack([a.real.ravel(), a.imag.ravel()], -1).ravel()
    return a.astype(np.float64, copy=False).ravel()


def _gewichte(n, a, c, p):
    return ((a * np.arange(n, dtype=np.int64) + c) % p) / float(p)


def feld(a):
    """Kennwerte eines Feldes als JSON-fähiges dict (siehe Modulkopf)."""
    a = np.asarray(a)
    out = dict(dtype=str(a.dtype), form=[int(x) for x in a.shape])
    art = a.dtype.kind
    if art in 'biu':                                                    # exakt: Prüfsumme der Werte
        ziel = {'b': np.uint8, 'i': '<i8', 'u': '<u8'}[art]
        out.update(n=int(a.size), sha256=formate.sha256_bytes(np.ascontiguousarray(a).astype(ziel).tobytes()))
        return out
    if art not in 'fc':
        raise KennwertFehler(f'Kennwerte: Datentyp {a.dtype} wird nicht unterstützt')
    x = _reell(a)
    endlich = np.isfinite(x)
    n_ne = int(x.size - endlich.sum())
    if n_ne:
        muster = np.zeros(x.size, np.uint8)
        muster[np.isnan(x)] = MUSTER['nan']
        muster[np.isposinf(x)] = MUSTER['+inf']
        muster[np.isneginf(x)] = MUSTER['-inf']
        x = np.where(endlich, x, 0.0)
    out.update(n=int(x.size), nicht_endlich=dict(n=n_ne, sha256=formate.sha256_bytes(muster.tobytes()) if n_ne
                                                 else None))
    out.update(summe=math.fsum(x.tolist()), quadrat=math.fsum((x * x).tolist()))
    for nr, (ga, gc, gp) in enumerate(GEWICHTE, 1):
        out[f'gewichtet_{nr}'] = math.fsum((_gewichte(x.size, ga, gc, gp) * x).tolist())
    e = x[endlich] if n_ne else x
    out.update(minimum=float(e.min()) if e.size else None, maximum=float(e.max()) if e.size else None)
    return out


def felder(d, namen=None):
    """Kennwerte je Feld eines dict Name → Feld (alle oder die genannten), nach Namen geordnet."""
    return {k: feld(d[k]) for k in sorted(d if namen is None else namen)}


def _groesster_betrag(*kw):
    w = [abs(k[x]) for k in kw for x in ('minimum', 'maximum') if k.get(x) is not None]
    return max(w) if w else 0.0


def vergleich(soll, ist, rtol=RTOL, atol=ATOL):
    """Vergleich der Kennwerte zweier Felder. Rückgabe dict(gleich, kennwerte_gleich, abweichungen, auslastung):
    gleich – innerhalb der Toleranz; kennwerte_gleich – alle Kennwerte stimmen genau überein; abweichungen – Liste
    in Worten; auslastung – größte Abweichung eines Kennwerts geteilt durch seine Toleranz (0 bei Übereinstimmung,
    ∞ bei einem exakten Merkmal oder bei Toleranz 0)."""
    abw, last = [], 0.0
    for x in ('dtype', 'form', 'n'):
        if soll.get(x) != ist.get(x):
            abw.append(f'{x}: {ist.get(x)} statt {soll.get(x)}')
    if not abw and ('sha256' in soll) != ('sha256' in ist):
        abw.append('Kennwerte eines exakten Feldes gegen die eines Gleitkommafeldes')
    if abw:
        return dict(gleich=False, kennwerte_gleich=False, abweichungen=abw, auslastung=math.inf)
    if 'sha256' in soll:
        g = soll['sha256'] == ist['sha256']
        return dict(gleich=g, kennwerte_gleich=g, abweichungen=[] if g else ['Werte (exaktes Feld) verschieden'],
                    auslastung=0.0 if g else math.inf)
    if soll['nicht_endlich'] != ist['nicht_endlich']:
        return dict(gleich=False, kennwerte_gleich=False, auslastung=math.inf,
                    abweichungen=[f'nicht endliche Einträge: {ist["nicht_endlich"]["n"]} statt '
                                  f'{soll["nicht_endlich"]["n"]} oder an anderer Stelle'])
    n = soll['n'] - soll['nicht_endlich']['n']
    M = _groesster_betrag(soll, ist)
    tau = rtol * M + atol
    grenzen = {x: n * tau for x in SUMMEN}
    grenzen.update(quadrat=(2.0 * M + tau) * n * tau, minimum=tau, maximum=tau)
    genau = True
    for x, grenze in grenzen.items():
        a, b = soll.get(x), ist.get(x)
        if a is None or b is None:
            if a is not b:
                abw.append(f'{x}: {b} statt {a}')
                last, genau = math.inf, False
            continue
        d = abs(b - a)
        if d == 0.0:
            continue
        genau = False
        last = max(last, d / grenze if grenze > 0 else math.inf)
        if d > grenze:
            abw.append(f'{x}: {b!r} statt {a!r} (Abweichung {d:.3g}, zulässig {grenze:.3g})')
    return dict(gleich=not abw, kennwerte_gleich=genau, abweichungen=abw, auslastung=last)


def vergleich_felder(soll, ist, rtol=RTOL, atol=ATOL):
    """Vergleich der Kennwerte zweier Feldsätze (dict Name → Kennwerte). Rückgabe wie vergleich; die Abweichungen
    nennen das Feld, auslastung ist der größte Wert über die Felder und feld_auslastung das zugehörige Feld."""
    abw, last, wo, genau = [], 0.0, None, True
    for k in sorted(set(soll) | set(ist)):
        if k not in soll or k not in ist:
            abw.append(f'Feld {k}: ' + ('fehlt' if k in soll else 'zusätzlich'))
            last, wo, genau = math.inf, k, False
            continue
        v = vergleich(soll[k], ist[k], rtol, atol)
        abw += [f'Feld {k}: {x}' for x in v['abweichungen']]
        genau = genau and v['kennwerte_gleich']
        if v['auslastung'] > last:
            last, wo = v['auslastung'], k
    return dict(gleich=not abw, kennwerte_gleich=genau, abweichungen=abw, auslastung=last, feld_auslastung=wo,
                toleranz=toleranz(rtol, atol))


def pruefe(soll, ist, was, rtol=RTOL, atol=ATOL):
    """Wie vergleich_felder, bricht aber bei einer Abweichung ab; was: Bezeichnung für die Fehlermeldung."""
    v = vergleich_felder(soll, ist, rtol, atol)
    if not v['gleich']:
        mehr = '' if len(v['abweichungen']) == 1 else f' (und {len(v["abweichungen"]) - 1} weitere)'
        raise KennwertFehler(f'{was}: {v["abweichungen"][0]}{mehr}')
    return v


# ── Vergleich zweier vollständiger Objekte Eintrag für Eintrag ───────────────────────────────────────
def _zahl(x):
    return isinstance(x, (int, float, complex, np.integer, np.floating, np.complexfloating)) and \
        not isinstance(x, (bool, np.bool_))


def _gleitkomma(x):
    return isinstance(x, (float, complex, np.floating, np.complexfloating))


def _als_feld(x):
    """Zahl, Zahlenliste oder Feld → ndarray; alles andere None."""
    if isinstance(x, np.ndarray):
        return x if x.dtype.kind in 'biufc' else None
    if _zahl(x):
        return np.asarray(x)
    if isinstance(x, (list, tuple)) and x and all(_zahl(v) for v in x):
        return np.asarray(x)
    return None


def _vergleich_feld(a, b, rtol, atol):
    """Zwei Zahlenfelder: (Abweichung in Worten oder None, Auslastung, genau gleich)."""
    if a.shape != b.shape:
        return f'Form {b.shape} statt {a.shape}', math.inf, False
    if a.dtype.kind in 'biu' and b.dtype.kind in 'biu':
        g = bool(np.array_equal(a, b))
        return (None if g else 'ganze Zahlen oder Wahrheitswerte verschieden'), (0.0 if g else math.inf), g
    x, y = _reell(a), _reell(b)
    if x.size != y.size:
        return 'reell gegen komplex', math.inf, False
    ex, ey = np.isfinite(x), np.isfinite(y)
    if not np.array_equal(ex, ey) or not np.array_equal(x[~ex], y[~ey], equal_nan=True):
        return 'nicht endliche Einträge verschieden', math.inf, False
    if not ex.any():
        return None, 0.0, True
    d = np.abs(x[ex] - y[ex])
    dmax = float(d.max())
    if dmax == 0.0:
        return None, 0.0, True
    tau = rtol * float(max(np.abs(x[ex]).max(), np.abs(y[ex]).max())) + atol
    if dmax > tau:
        return f'größte Abweichung {dmax:.3g}, zulässig {tau:.3g} ({int((d > tau).sum())} von {d.size} Einträgen)', \
            dmax / tau if tau > 0 else math.inf, False
    return None, dmax / tau, False


def vergleich_objekt(soll, ist, rtol=RTOL, atol=ATOL, ohne=()):
    """Vergleich zweier verschachtelter Objekte (dict, Liste, Feld, Zahl, Text) Eintrag für Eintrag. Exakt: Schlüssel,
    Längen, Texte, ganze Zahlen, Wahrheitswerte, None. Mit Toleranz: Gleitkommazahlen und -felder, je Feld
    τ = rtol·M + atol (M größter Betrag des Feldes; eine einzelne Zahl ist ihr eigenes Feld). ohne: Schlüssel, die
    auf jeder Ebene übergangen werden (etwa Laufzeiten). Rückgabe dict(gleich, genau_gleich, abweichungen,
    auslastung, stelle_auslastung): abweichungen nennt den Pfad, auslastung ist die größte Abweichung geteilt durch
    ihre Toleranz."""
    abw, stand = [], dict(last=0.0, wo=None, genau=True)

    def melde(pfad, text):
        abw.append(f'{pfad or "(Wurzel)"}: {text}')
        stand.update(last=math.inf, wo=stand['wo'] or pfad, genau=False)

    def geh(a, b, pfad):
        if isinstance(a, dict) or isinstance(b, dict):
            if not (isinstance(a, dict) and isinstance(b, dict)):
                return melde(pfad, 'dict gegen anderes')
            ka, kb = set(a) - set(ohne), set(b) - set(ohne)
            if ka != kb:
                melde(pfad, f'Schlüssel verschieden: {sorted(map(str, ka ^ kb))}')
            for k in sorted(ka & kb, key=str):
                geh(a[k], b[k], f'{pfad}.{k}' if pfad else str(k))
            return
        fa, fb = _als_feld(a), _als_feld(b)
        if fa is not None or fb is not None:
            if fa is None or fb is None:
                return melde(pfad, f'{type(b).__name__} statt {type(a).__name__}')
            text, last, genau = _vergleich_feld(fa, fb, rtol, atol)
            stand['genau'] = stand['genau'] and genau
            if last > stand['last']:
                stand.update(last=last, wo=pfad)
            if text:
                abw.append(f'{pfad or "(Wurzel)"}: {text}')
            return
        if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
            if not (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))):
                return melde(pfad, 'Liste gegen anderes')
            if len(a) != len(b):
                return melde(pfad, f'Länge {len(b)} statt {len(a)}')
            for i, (x, y) in enumerate(zip(a, b)):
                geh(x, y, f'{pfad}[{i}]')
            return
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):          # Felder ohne Zahlen (Texte)
            if not (isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and np.array_equal(a, b)):
                melde(pfad, 'Feld verschieden')
            return
        if a != b or type(a) is not type(b) and not (a is None and b is None):
            melde(pfad, f'{b!r} statt {a!r}')

    geh(soll, ist, '')
    return dict(gleich=not abw, genau_gleich=stand['genau'] and not abw, abweichungen=abw, auslastung=stand['last'],
                stelle_auslastung=stand['wo'], toleranz=toleranz(rtol, atol))
