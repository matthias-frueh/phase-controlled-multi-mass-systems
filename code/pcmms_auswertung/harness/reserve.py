"""Reserve, Ziel und Zeit der Planung (Auftrag vom 20.10.2026, b2; Regeln planung.reserve, planung.reserve_ziel,
planung.zeitformel, planung.zielfunktion; Präreg §5.3 (c), §5.4, A9.2 (v)).

- Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2 bleibt (planung.reserve). Zusätzliche Bedingung (planung.reserve_ziel): Alle
  Schnittpunkte erreichen gemeinsam in mindestens 95 % der nicht endgültig beendeten Kampagnen n_min gültige Läufe.
  Endgültig beendete Kampagnen gehören nicht in diesen bedingten Nenner, bleiben aber im Nenner von P(H1 und H2
  bestätigt). Verfehlt ein Kandidat die Bedingung, wird r um eins erhöht, höchstens zusatz_max-mal; danach endet der
  Kandidat mit dem Grund „Reservegrenze“ (kein unbeschränktes Erhöhen).
- Zeitbilanz (planung.zeitformel): Läufe des Plans, Wiederholungen, Kontrollsatz der Wiederaufnahme, Bezugseröffnung,
  Ursachenanalyse T_UA und Aufwärmen bei Tageswechsel, je Term als Mittel über die simulierten Kampagnen mit Zähler
  und Nenner; daneben die Formel von §5.3 (c). Zum Aufwärmen gehören alle zusätzlichen Aufwärmläufe nach einer
  Wiederaufnahme mit Tageswechsel und die am Beginn eines Messtags eingeschobenen (§6), nicht die Wiederholungen.
- Zielfunktion (planung.zielfunktion): nur Fassung (a) N_K·n_min + 3·n₀ ist umgesetzt; andere Werte sind ein Fehler.

Kleine Proben belegen keine Rate von 0,95; berichtet werden Zähler, Nenner und Standardfehler, kein „Ziel erreicht“
als Kalibrierfreigabe.
"""
import math

from . import metriken


def kandidaten_ordnen(n_liste, n0_liste, N_K=21, fassung='a'):
    """Kandidaten (n_min, n₀) in der Reihenfolge der Zielfunktion."""
    if fassung != 'a':
        raise ValueError(f'planung.zielfunktion {fassung!r} nicht umgesetzt (nur Fassung (a): N_K·n_min + 3·n₀)')
    return sorted(((int(n), int(n0)) for n in n_liste for n0 in n0_liste), key=lambda x: (N_K * x[0] + 3 * x[1], x))


def reserve_r(n_min, p_hat, plus):
    return int(math.ceil(n_min * p_hat / (1 - p_hat))) + int(plus) if p_hat < 1 else None


def endgueltig_beendet(b):
    """Ist die simulierte Kampagne endgültig beendet (Abbruch, ausgeschöpfte Wiederaufnahmen, nicht fortsetzbar)?"""
    ab = b.get('ablauf') or {}
    w = ab.get('harness_wiederaufnahme') or {}
    return bool(w.get('endgueltig')) or ab.get('status') == 'abgebrochen'


def bedingung(befunde, n_min, regel):
    """Anteil der nicht endgültig beendeten Kampagnen, in denen alle Schnittpunkte n_min gültige Läufe erreichen."""
    anteil = float(regel['anteil'])
    if regel.get('nenner') != 'nicht_endgueltig_beendet':
        raise ValueError(f'planung.reserve_ziel: Nenner {regel.get("nenner")!r} nicht unterstützt')
    offen = [b for b in befunde if not endgueltig_beendet(b)]
    ohne = [b for b in offen if not (b.get('ablauf') or {}).get('gueltig_je_schnittpunkt')]
    if ohne:
        raise ValueError('planung.reserve_ziel: Kampagnen ohne gueltig_je_schnittpunkt (nur ablauf-4)')
    ok = sum(all(v >= n_min for v in b['ablauf']['gueltig_je_schnittpunkt'].values()) for b in offen)
    r = metriken.rate(ok, len(offen), f'Anteil mit allen Schnittpunkten ≥ n_min = {n_min} gültigen Läufen '
                                      '(nicht endgültig beendete Kampagnen)')
    return dict(rate=r['rate'], mc_se=r['mc_se'], zaehler=ok, nenner=len(offen), anteil_soll=anteil,
                endgueltig_beendet=len(befunde) - len(offen), G=len(befunde),
                erfuellt=bool(r['rate'] is not None and r['rate'] >= anteil),
                hinweis='kleine Proben: Zähler und Nenner, keine bestätigte Rate')


def zeitbilanz(befunde, T_lauf, regel, formel_s=None):
    """Zeit je simulierter Kampagne nach Termen (Mittel, Zähler/Nenner); Läufe × T_Lauf plus T_UA je Wiederaufnahme.
    Aufwärmen bei Tageswechsel: zusätzliche Aufwärmläufe nach einer Wiederaufnahme mit Tageswechsel und am Beginn eines
    Messtags (Ablaufbericht zusatzlaeufe); Wiederholungen: die übrigen zusätzlichen Läufe."""
    erwartet = ['Läufe', 'Wiederholungen', 'Kontrollsatz der Wiederaufnahme', 'Bezugseröffnung',
                'Ursachenanalyse T_UA', 'Aufwärmen bei Tageswechsel']
    if list(regel) != erwartet:
        raise ValueError(f'planung.zeitformel: Terme {regel} nicht unterstützt')
    terme = {t: [] for t in erwartet}
    for b in befunde:
        ab = b.get('ablauf') or {}
        lz = ab.get('laufzahl') or {}
        zl = ab.get('zusatzlaeufe') or {}
        w = ab.get('harness_wiederaufnahme') or {}
        bez, wk = (int(zl.get(x, 0)) for x in ('bezugslauf', 'wiederaufnahme_kontrolle'))
        auf = sum(int(zl.get(x, 0)) for x in ('aufwaermen_nach_halt', 'aufwaermen_tagesbeginn'))
        terme['Läufe'].append(lz.get('geplant_ausgefuehrt', 0) * T_lauf)
        terme['Wiederholungen'].append((lz.get('zusaetzlich', 0) - bez - wk - auf) * T_lauf)
        terme['Kontrollsatz der Wiederaufnahme'].append(wk * T_lauf)
        terme['Bezugseröffnung'].append(bez * T_lauf)
        terme['Ursachenanalyse T_UA'].append(float(w.get('ursachenanalyse_s') or 0.0))
        terme['Aufwärmen bei Tageswechsel'].append(auf * T_lauf)
    n = len(befunde)
    out = {t: dict(mittel_s=metriken.mittel(v)['wert'] if n else None, summe_s=float(sum(v)), nenner=n)
           for t, v in terme.items()}
    gesamt = [sum(terme[t][i] for t in erwartet) for i in range(n)]
    return dict(terme=out, gesamt=metriken.mittel(gesamt) if n else None, nenner=n, formel_s=formel_s,
                hinweis='Zeit je Kampagne aus der Simulation; T_UA nur für simulierte Wiederaufnahmen')
