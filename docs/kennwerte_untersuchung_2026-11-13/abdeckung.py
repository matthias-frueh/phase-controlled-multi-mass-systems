"""Untersuchung der Kennwerte (13.11.2026), Schritt 3: Abdeckung. Was erkennt der Vergleich der Kennwerte, was nicht?

Aufruf aus dem Wurzelverzeichnis des Repositorys:

    python3 docs/kennwerte_untersuchung_2026-11-13/abdeckung.py <Ablage aus messen.py, eine Umgebung>

Die Felder der Laufzusammenfassungen zweier Prüfkampagnen werden gezielt verändert; je Veränderung und Feld wird
gezählt, wie oft der Vergleich der Kennwerte (kennwerte.vergleich, Toleranz des Moduls) anschlägt und wie oft ein
Vergleich Eintrag für Eintrag mit derselben Toleranz je Eintrag (kennwerte.vergleich_objekt; er braucht die vollen
Bezugsfelder). Zufällige Stellen sind mit festem Seed gezogen. Schreibt abdeckung.json neben dieses Skript.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, 'code')
import numpy as np                                                       # noqa: E402

from pcmms_auswertung import kennwerte as kw                             # noqa: E402
from pcmms_auswertung.harness.pruefsatz import _einzeilig                # noqa: E402  (kompakter JSON-Text)

HIER = os.path.dirname(os.path.abspath(__file__))
KAMPAGNEN = ('A04-R4/L1/7', 'I01-amplitude/L1/7')
N_ZUFALL = 100


def tau(x):
    r = kw._reell(x)
    e = np.isfinite(r)
    return kw.RTOL * float(np.abs(r[e]).max()) + kw.ATOL


def flach(x):
    """Ansicht auf die reellen Einträge (komplex: Re, Im nacheinander) einer Kopie von x."""
    y = np.array(x, dtype=complex if np.iscomplexobj(x) else float)
    return y, y.reshape(-1).view(float)


def ein_eintrag(x, rng, rel=None, m_anteil=None):
    """Ein zufälliger endlicher Eintrag ungleich 0: relativ um rel verändert oder um m_anteil·M verschoben."""
    y, r = flach(x)
    kand = np.flatnonzero(np.isfinite(r) & (r != 0))
    i = int(rng.choice(kand))
    r[i] = r[i] * (1 + rel) if rel is not None else r[i] + m_anteil * float(np.abs(r[np.isfinite(r)]).max())
    return y


def zwei_eintraege(x, rng):
    y, r = flach(x)
    i, j = rng.choice(np.flatnonzero(np.isfinite(r)), 2, replace=False)
    r[[i, j]] = r[[j, i]]
    return y


def zwei_laeufe(x, rng):
    y = np.array(x)
    i, j = rng.choice(len(y), 2, replace=False)
    y[[i, j]] = y[[j, i]]
    return y


def lauf_doppelt(x, rng):
    y = np.array(x)
    i, j = rng.choice(len(y), 2, replace=False)
    y[i] = y[j]
    return y


def rauschen(x, rng, anteil):
    y, r = flach(x)
    r += anteil * tau(x) * rng.uniform(-1, 1, r.size)
    return y


def nan(x, rng):
    y, r = flach(x)
    r[int(rng.choice(np.flatnonzero(np.isfinite(r))))] = np.nan
    return y


# Name → (Funktion(x, rng), zufällig?, nur für komplexe Felder?)
VERAENDERUNGEN = {
    'Rauschen bis 0,5·τ je Eintrag (darf nicht anschlagen)': (lambda x, g: rauschen(x, g, 0.5), True, False),
    'Rauschen bis 0,99·τ je Eintrag (darf nicht anschlagen)': (lambda x, g: rauschen(x, g, 0.99), True, False),
    'alle Einträge relativ um 1e-9 größer': (lambda x, g: np.array(x) * (1 + 1e-9), False, False),
    'alle Einträge relativ um 1e-10 größer': (lambda x, g: np.array(x) * (1 + 1e-10), False, False),
    'alle Einträge um 2·τ verschoben': (lambda x, g: np.array(x) + 2 * tau(x), False, False),
    'ein Eintrag relativ um 1e-2 geändert': (lambda x, g: ein_eintrag(x, g, rel=1e-2), True, False),
    'ein Eintrag relativ um 1e-4 geändert': (lambda x, g: ein_eintrag(x, g, rel=1e-4), True, False),
    'ein Eintrag relativ um 1e-6 geändert': (lambda x, g: ein_eintrag(x, g, rel=1e-6), True, False),
    'ein Eintrag um 1e-3·M verschoben': (lambda x, g: ein_eintrag(x, g, m_anteil=1e-3), True, False),
    'ein Eintrag um 1e-5·M verschoben': (lambda x, g: ein_eintrag(x, g, m_anteil=1e-5), True, False),
    'ein Eintrag um 1e-7·M verschoben': (lambda x, g: ein_eintrag(x, g, m_anteil=1e-7), True, False),
    'zwei Einträge vertauscht': (zwei_eintraege, True, False),
    'Werte zweier Läufe vertauscht': (zwei_laeufe, True, False),
    'Werte eines Laufs durch die eines anderen ersetzt': (lauf_doppelt, True, False),
    'alle Läufe um einen Platz verschoben': (lambda x, g: np.roll(np.array(x), 1, axis=0), False, False),
    'ein Eintrag fehlt (NaN)': (nan, True, False),
    'Imaginärteil mit anderem Vorzeichen': (lambda x, g: np.conj(x), False, True),
}


if __name__ == '__main__':
    d = pickle.load(open(sys.argv[1], 'rb'))
    out = dict(beschreibung='Abdeckung des Vergleichs der Kennwerte gegenüber einem Vergleich Eintrag für Eintrag '
                            '(abdeckung.py); Toleranz ' + json.dumps(kw.toleranz(), ensure_ascii=False),
               umgebung=d['umgebung'], kampagnen=list(KAMPAGNEN), versuche_je_zufall=N_ZUFALL, felder={}, ergebnis={})
    zeilen = {}
    for key in KAMPAGNEN:
        for name, x in d['pruefsaetze']['testdaten'][key]['daten'].items():
            x = np.asarray(x)
            if x.dtype.kind not in 'fc':
                continue
            bezug = kw.feld(x)
            n = bezug['n'] - bezug['nicht_endlich']['n']
            M = max(abs(bezug['minimum']), abs(bezug['maximum']))
            out['felder'][f'{key}: {name}'] = dict(n=n, M=M, tau=tau(x), schwelle_ein_eintrag_durch_M=n * tau(x) / M)
            for vname, (fn, zufall, nur_komplex) in VERAENDERUNGEN.items():
                if nur_komplex and x.dtype.kind != 'c':
                    continue
                rng = np.random.default_rng(20261113)
                z = zeilen.setdefault(vname, dict(versuche=0, kennwerte=0, eintragsweise=0, je_feld={}))
                f = z['je_feld'].setdefault(name, dict(versuche=0, kennwerte=0, eintragsweise=0))
                for _ in range(N_ZUFALL if zufall else 1):
                    y = fn(x, rng)
                    a = not kw.vergleich(bezug, kw.feld(y))['gleich']
                    b = not kw.vergleich_objekt(dict(x=x), dict(x=y))['gleich']
                    for w in (z, f):
                        w['versuche'] += 1
                        w['kennwerte'] += int(a)
                        w['eintragsweise'] += int(b)
    out['ergebnis'] = zeilen
    with open(os.path.join(HIER, 'abdeckung.json'), 'w', encoding='utf-8') as fh:
        fh.write(_einzeilig(out) + '\n')
    print(f'{"Veränderung":58s} {"Versuche":>8s} {"Kennwerte":>10s} {"Eintrag f. E.":>13s}')
    for vname, z in zeilen.items():
        print(f'{vname:58s} {z["versuche"]:8d} {z["kennwerte"]:10d} {z["eintragsweise"]:13d}')
