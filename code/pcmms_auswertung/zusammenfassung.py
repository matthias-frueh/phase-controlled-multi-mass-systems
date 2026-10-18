"""Laufzusammenfassung: Trennstelle zwischen Stufe 1 (Rohdaten → Lauf, A9.4 Schritte 1–6) und Stufe 2
(Läufe → Vorhersage, Unsicherheit, Entscheidung) nach Plan AP-13, Abschnitt 2.6 b.

Stufe 1 schreibt je Lauf eine Laufzusammenfassung; Ebene H des Generators erzeugt dieselbe Struktur direkt.
Stufe 2 braucht keine Zeitreihen: Die Konfigurationsmittelkurve ist bandbegrenzt und durch ⟨N⟩ und N_k
(k ≤ k_max) bestimmt (A9.4 Schritt 5).

Felder je Lauf (Kopf: JSON-Werte; Daten: Felder fester Form, k = 1 … k_voll, k_voll ≥ k_max):
  Kopf    lauf_id, laufart (R, L, K, D1, D2), modul (bei L), einstellung (1, 2), konfiguration (id, gruppe,
          phi_soll_grad = Profilphasen (0, φ₂, φ₃) bzw. null), phase (0, 1), block, messtag, position (Rang in der
          Laufreihenfolge), kontrollsatz, t_start, t_ende [s, Kampagnenuhr], f_soll, f_mittel [Hz], n_zyklen,
          n_fuenftel, k_voll, n_theta, stoerung (G8), aufzeichnung_ok (G10), park_ok (G9; null ohne geparktes
          Modul), fehlende_kanaele, hash_rohdatei, version_stufe1, kalibrier_hash, ebene (Z oder H)
  Daten   Nk_summe (k) und Nk_zellen (3, k): Harmonische der Mittelkurve, θ = 0 am Index von Modul 1 bzw. j;
          N_mittel, N_mittel_zellen (3): ⟨N⟩ über die ganzen Zyklen [N] (Bedeutung je Verarbeitungsstand:
          MITTEL_BEDEUTUNG; ab stufe1-0.2 Zeitmittel aus den Rohzeiten); zeiger (3, k) = Σ_c e^{−ikφⱼ,c} der
          Indexphasen (Modul 1: N_z; nicht laufende Module: nan); phi_mittel_grad, sigma_grad (3): zirkuläres
          Mittel und Jitter der Indexphasen; index_fehler (3): fehlende und überzählige Indeximpulse;
          fuenftel_N_mittel (2), fuenftel_Nk (2, k): erstes und letztes Fünftel (⌊N_z/5⌋ Zyklen) für G4;
          min_roh_zellen, max_roh_zellen (3): Extrema der kalibrierten Rohwerte des ganzen Laufs einschließlich
          Rampe und Einschwingzeit (G6, S2); sigma_roh_zellen (3), sigma_roh_summe: Standardabweichung der
          kalibrierten Rohwerte im Auswertefenster (in Referenzläufen σ_c, σ_Σ für F_LO, A1); uebersteuert_zellen (3)
          (G5); temperatur_min/max_zellen (3) (G7); t_phi (3): Einregelzeit der Phasen [s].
Fehlende Kanäle werden in fehlende_kanaele genannt; die abhängigen Felder sind nan, nie null-ergänzt.
"""
import numpy as np

from . import formate

MITTEL_BEDEUTUNG = {        # version_stufe1 → Bedeutung von N_mittel, N_mittel_zellen, fuenftel_N_mittel
    'stufe1-0.1': 'Phasenmittel: Gleichanteil der Mittelkurve, Zyklen gleich gewichtet (alte Bedeutung, vor '
                  'Korrektur B; bei ungleichen Periodendauern nicht das Zeitmittel nach A1)',
    'stufe1-0.2': 'Zeitmittel nach A1 über die akzeptierten Zyklusintervalle aus den Rohzeiten',
    'ebene_h-0.1': 'Generator Ebene H: Gleichanteil des Modells (gleiche Periodendauern, Zeit- gleich Phasenmittel)',
    'teil_b': 'Einzelmodulläufe aus Teil B (nur Harmonische)',
}
ALTE_BEDEUTUNG = ('stufe1-0.1',)
LAUFARTEN = ('R', 'L', 'K', 'D1', 'D2')
GRUPPEN = ('referenz', 'einzel', 'schnitt', 'zusatz', 'pilot', 'identifizierbarkeit', 'dummy', 'pruef')   # pruef: Prüffälle (S₃-Bilder), kein Teil des Präreg-Plans
DATENFELDER = {                         # Name: (dtype, Form je Lauf; 'k' = k_voll)
    'Nk_summe': ('complex128', ('k',)),
    'Nk_zellen': ('complex128', (3, 'k')),
    'N_mittel': ('float64', ()),
    'N_mittel_zellen': ('float64', (3,)),
    'zeiger': ('complex128', (3, 'k')),
    'phi_mittel_grad': ('float64', (3,)),
    'sigma_grad': ('float64', (3,)),
    'index_fehler': ('int64', (3,)),
    'fuenftel_N_mittel': ('float64', (2,)),
    'fuenftel_Nk': ('complex128', (2, 'k')),
    'min_roh_zellen': ('float64', (3,)),
    'max_roh_zellen': ('float64', (3,)),
    'sigma_roh_zellen': ('float64', (3,)),
    'sigma_roh_summe': ('float64', ()),
    'uebersteuert_zellen': ('bool', (3,)),
    'temperatur_min_zellen': ('float64', (3,)),
    'temperatur_max_zellen': ('float64', (3,)),
    't_phi': ('float64', (3,)),
}
KOPFFELDER = ('lauf_id', 'laufart', 'modul', 'einstellung', 'konfiguration', 'phase', 'block', 'messtag', 'position',
              'kontrollsatz', 't_start', 't_ende', 'f_soll', 'f_mittel', 'n_zyklen', 'n_fuenftel', 'k_voll', 'n_theta',
              'stoerung', 'aufzeichnung_ok', 'park_ok', 'fehlende_kanaele', 'hash_rohdatei', 'version_stufe1',
              'kalibrier_hash', 'ebene')


def konfig_id(laufart, phi_soll=None, modul=None, einstellung=1, gruppe=None):
    """Eindeutige Kennung einer Konfiguration: R, L1 … L3, S100 … S140 (Schnitt), Z0_0, P110_250, I116;
    Einstellung 2 mit Anhang „′“ (z. B. L1′, I116′)."""
    s = "′" if einstellung == 2 else ''
    if laufart == 'R':
        return 'R' + s
    if laufart == 'L':
        return f'L{int(modul)}{s}'
    if laufart in ('D1', 'D2'):
        return laufart + ('' if modul is None else str(int(modul))) + s
    p2, p3 = float(phi_soll[1]), float(phi_soll[2])
    fmt = lambda v: f'{v:g}'                                           # noqa: E731
    if gruppe == 'schnitt' or (gruppe is None and abs(p3 - 240.0) < 1e-9 and einstellung == 1):
        return f'S{fmt(p2)}{s}' if abs(p3 - 240.0) < 1e-9 else f'K{fmt(p2)}_{fmt(p3)}{s}'
    vor = {'pilot': 'P', 'zusatz': 'Z', 'identifizierbarkeit': 'I'}.get(gruppe, 'K')
    if vor == 'I' and abs(p3 - 240.0) < 1e-9:
        return f'I{fmt(p2)}{s}'
    return f'{vor}{fmt(p2)}_{fmt(p3)}{s}'


def pruefe_kopf_lauf(k):
    fehlend = [f for f in KOPFFELDER if f not in k]
    if fehlend:
        raise formate.FormatFehler(f'Laufzusammenfassung: Kopffelder fehlen: {fehlend}')
    if k['laufart'] not in LAUFARTEN:
        raise formate.FormatFehler(f'Laufart {k["laufart"]!r} unbekannt')
    if k['laufart'] == 'L' and k['modul'] not in (1, 2, 3):
        raise formate.FormatFehler('Einzelmodullauf ohne Modul 1–3')
    if k['einstellung'] not in (1, 2) or k['phase'] not in (0, 1):
        raise formate.FormatFehler('einstellung ∈ {1, 2} und phase ∈ {0, 1} erwartet')
    if k['konfiguration'].get('gruppe') not in GRUPPEN:
        raise formate.FormatFehler(f'Konfigurationsgruppe {k["konfiguration"].get("gruppe")!r} unbekannt')
    if k['ebene'] not in ('Z', 'H'):
        raise formate.FormatFehler('ebene ∈ {Z, H} erwartet')
    if not (isinstance(k['n_zyklen'], int) and k['n_zyklen'] >= 0):
        raise formate.FormatFehler('n_zyklen: ganze Zahl ≥ 0 erwartet')


def verarbeitungsstand(koepfe):
    """Verarbeitungsstände der Laufzusammenfassungen mit Anzahl und Bedeutung von ⟨N⟩; alte_bedeutung: mindestens
    eine Zusammenfassung trägt ⟨N⟩ in der Bedeutung vor Korrektur B (nicht stillschweigend als neu berechnet)."""
    st = {}
    for k in koepfe:
        st[k['version_stufe1']] = st.get(k['version_stufe1'], 0) + 1
    return dict(versionen=st, mittel_bedeutung={v: MITTEL_BEDEUTUNG.get(v, 'unbekannt') for v in st},
                alte_bedeutung=sorted(v for v in st if v in ALTE_BEDEUTUNG or v not in MITTEL_BEDEUTUNG))


def _form(spec, kv):
    return tuple(kv if s == 'k' else s for s in spec)


def pruefe_daten(d, kv, n=None):
    """Feldnamen, Datentypen und Formen (n: Zahl der Läufe bei Tabellen)."""
    if set(d) != set(DATENFELDER):
        raise formate.FormatFehler(f'Datenfelder {sorted(set(d) ^ set(DATENFELDER))} fehlen oder sind unbekannt')
    for name, (dt, spec) in DATENFELDER.items():
        form = ((n,) if n is not None else ()) + _form(spec, kv)
        a = np.asarray(d[name])
        if str(a.dtype) != dt or a.shape != form:
            raise formate.FormatFehler(f'Feld {name}: {a.dtype}{a.shape} statt {dt}{form}')


def leere_daten(kv, n=None):
    """Datenfelder mit nan (bzw. 0 bei Zählern, False bei Merkern) als Startwert für Erzeuger."""
    pre = (n,) if n is not None else ()
    out = {}
    for name, (dt, spec) in DATENFELDER.items():
        form = pre + _form(spec, kv)
        if dt.startswith('complex'):
            out[name] = np.full(form, np.nan + 1j * np.nan, complex)
        elif dt == 'float64':
            out[name] = np.full(form, np.nan)
        elif dt == 'int64':
            out[name] = np.zeros(form, np.int64)
        else:
            out[name] = np.zeros(form, bool)
    return out


class Laufzusammenfassung:
    """Ein Lauf: kopf (Metadaten, JSON) und daten (Felder nach DATENFELDER)."""

    def __init__(self, kopf, daten, meta=None):
        pruefe_kopf_lauf(kopf)
        pruefe_daten(daten, kopf['k_voll'])
        self.kopf, self.daten = dict(kopf), {k: np.asarray(v) for k, v in daten.items()}
        self.meta = dict(meta or {})               # Pflichtkopf der Datei (Schema, Datenart, Kennung)

    def schreiben(self, pfad, kennung, datenart='synthetisch'):
        k = formate.kopf('laufzusammenfassung', kennung, datenart, lauf=self.kopf)
        return formate.schreibe(pfad, k, self.daten)

    @classmethod
    def lesen(cls, pfad):
        k, _, felder = formate.lies(pfad, 'laufzusammenfassung')
        return cls(k['lauf'], felder, meta={x: k[x] for x in ('schema', 'schema_version', 'datenart', 'kennung')})


class LaufTabelle:
    """Viele Läufe in Spaltenform (gleiches k_voll); Ebene H und Stufe 2 arbeiten mit dieser Form."""

    def __init__(self, koepfe, daten, meta=None):
        self.koepfe = [dict(k) for k in koepfe]
        n = len(self.koepfe)
        kv = {k['k_voll'] for k in self.koepfe}
        if n and len(kv) != 1:
            raise formate.FormatFehler(f'Läufe mit verschiedenem k_voll {sorted(kv)} in einer Tabelle')
        self.k_voll = kv.pop() if n else 0
        for k in self.koepfe:
            pruefe_kopf_lauf(k)
        pruefe_daten(daten, self.k_voll, n)
        self.daten = {k: np.asarray(v) for k, v in daten.items()}
        ids = [k['lauf_id'] for k in self.koepfe]
        if len(set(ids)) != n:
            raise formate.FormatFehler('doppelte Lauf-IDs')
        self.meta = dict(meta or {})

    def __len__(self):
        return len(self.koepfe)

    @classmethod
    def aus_liste(cls, laeufe, meta=None):
        laeufe = list(laeufe)
        if not laeufe:
            raise formate.FormatFehler('keine Läufe')
        daten = {n: np.stack([l.daten[n] for l in laeufe]) for n in DATENFELDER}
        return cls([l.kopf for l in laeufe], daten, meta)

    def lauf(self, i):
        return Laufzusammenfassung(self.koepfe[i], {n: v[i] for n, v in self.daten.items()})

    def spalte(self, name, dtype=None):
        if name in self.daten:
            return self.daten[name]
        vals = [k[name] for k in self.koepfe]
        if dtype is not None:
            return np.array([np.nan if v is None and dtype is float else v for v in vals], dtype)
        return vals

    def konfig_ids(self):
        return [k['konfiguration']['id'] for k in self.koepfe]

    def auswahl(self, maske):
        idx = np.flatnonzero(np.asarray(maske, bool)) if np.asarray(maske).dtype == bool else np.asarray(maske, int)
        return LaufTabelle([self.koepfe[i] for i in idx], {n: v[idx] for n, v in self.daten.items()}, self.meta)

    def sortiert(self):
        """Läufe in aufsteigender Position der Laufreihenfolge (Ordnung der Bootstrap-Indizes, Plan 2.6 c)."""
        return self.auswahl(np.argsort(self.spalte('position', int), kind='stable'))

    def schreiben(self, pfad, kennung, datenart='synthetisch', **weitere):
        if 'ablauf' in self.meta and 'ablauf' not in weitere:            # Ablaufstand des zustandsbehafteten Ablaufs
            weitere['ablauf'] = self.meta['ablauf']
        k = formate.kopf('zusammenfassungen', kennung, datenart, laeufe=self.koepfe, **weitere)
        return formate.schreibe(pfad, k, self.daten)

    @classmethod
    def lesen(cls, pfad):
        k, _, felder = formate.lies(pfad, 'zusammenfassungen')
        meta = {x: k[x] for x in ('schema', 'schema_version', 'datenart', 'kennung')}
        if 'ablauf' in k:
            meta['ablauf'] = k['ablauf']
        return cls(k['laeufe'], felder, meta)
