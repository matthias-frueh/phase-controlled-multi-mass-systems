"""Unabhängige, deterministische Zufallsströme (Plan AP-13, Abschnitte 2.6 c und 4.3).

Jeder Strom folgt aus numpy.random.SeedSequence(basis, spawn_key=(Schlüssel …)); Schlüssel sind ganze Zahlen oder
Zeichenketten (über SHA-256 auf 32-Bit-Wörter abgebildet). Generator, Kalibriersimulation von c, Prüfsimulation,
Bootstrap und Monte-Carlo-Fortpflanzung erhalten verschiedene Schlüssel; eine Kampagne erhält ihren Strom aus
(Katalog, Szenario, Stufe, Kampagnennummer). Das Ergebnis hängt deshalb nicht von der Zahl der Prozesse oder der
Reihenfolge der Abarbeitung ab, und es gibt keine Suche nach einem Seed.
"""
import hashlib

import numpy as np

STROEME = ('generator', 'kalibrierung_c', 'pruefung_c', 'bootstrap', 'h3_mc', 'e3_mc', 'teil_b', 'planung',
           'rauschbias', 'eps_ctrl', 'p0_messung', 'zeltfit_testsatz')


def _wort(s):
    if isinstance(s, (int, np.integer)):
        if s < 0:
            raise ValueError('Schlüssel ≥ 0 erwartet')
        return [int(s) & 0xFFFFFFFF, int(s) >> 32] if s >= 2 ** 32 else [int(s)]
    h = hashlib.sha256(str(s).encode('utf-8')).digest()
    return [int.from_bytes(h[i:i + 4], 'little') for i in range(0, 16, 4)]


def seedsequence(basis, *schluessel):
    key = []
    for s in schluessel:
        key.extend(_wort(s))
    return np.random.SeedSequence(int(basis), spawn_key=tuple(key))


def strom(basis, *schluessel):
    """numpy.random.Generator (PCG64) des Stroms (basis, schlüssel …)."""
    return np.random.Generator(np.random.PCG64(seedsequence(basis, *schluessel)))


def unterseed(basis, *schluessel):
    """Ganzzahliger Seed (63 Bit) eines Teilstroms, etwa für Teil B oder die Bootstrap-Indizes einer Kampagne."""
    st = seedsequence(basis, *schluessel).generate_state(2, np.uint32)
    return int(st[0]) | (int(st[1] & 0x7FFFFFFF) << 32)


def katalog_seed(katalog_sha256):
    """Basis-Seed aus der Prüfsumme des Szenarienkatalogs (erste 16 Hexziffern, 64 Bit wie §6)."""
    return int(katalog_sha256[:16], 16)
