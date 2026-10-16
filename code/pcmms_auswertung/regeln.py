"""Regelprofile der Auswertung (AP-12) und des Pipelinetests (AP-13): jede Regel mit Fundstelle, Status und Wert.

Status (Regelmatrix in docs/ap11_ap12_ap13_regelmatrix.md):
  arbeitsfestlegung       vorläufige Festlegung des Autors, in §12 so gekennzeichnet (Präreg §0)
  regeltext               Regel des Entwurfs ohne Kennzeichnung als offen
  festlegung              Zahlenwert aus Tabelle F, nicht als offen gekennzeichnet
  entwicklungsprueffall   offene Entscheidung, für die Entwicklung ausdrücklich gewählter Prüffall (Testvariante
                          oder Vorschlag des Entwurfs); nur in Entwicklungsprofilen; keine Festlegung
  offen                   offene Entscheidung ohne Wert; abhängige Ausgänge lauten „nicht entscheidbar“ mit Grund
                          oder werden nur numerisch berichtet
  nicht_implementiert     genannte Option, in dieser Stufe nicht umgesetzt
  technisch               Umsetzungsdetail der Software ohne eigene Regelwirkung; dokumentiert, Klärung am Text

Es gibt keine stillen Vorgaben: Wer einen Wert braucht, ruft Regelprofil.wert(); bei offenen Regeln folgt RegelOffen
mit der Fundstelle, und die Auswertung berichtet „nicht entscheidbar (Grund: Regel offen …)“ bzw. nur Prüfgrößen.
Profile: „AF-2026-10“ (Arbeitsfestlegungen und Regeltext, alles Offene offen) und „ENTW-2026-10“ (dazu die
Entwicklungsprüffälle). Verringerte Replikat- oder Kampagnenzahlen erzeugen ein abgeleitetes Profil mit Kennung
„…+red(…)“; die Reduktion steht in jedem Ergebnis.
"""
import copy
import json
from dataclasses import dataclass, field

from . import formate

AF, RT, FL, EP, OF, NI, TD = ('arbeitsfestlegung', 'regeltext', 'festlegung', 'entwicklungsprueffall', 'offen',
                              'nicht_implementiert', 'technisch')
STATUS = (AF, RT, FL, EP, OF, NI, TD)
NORMATIVE_ZAHLEN = dict(bootstrap_B=10000, h2_replikate=10000, h3_mc=10000, e3_mc=10000,
                        eps_ctrl_datensaetze=10000, kampagnen_kalibrierung=1000, kampagnen_pruefung=1000)


class RegelOffen(Exception):
    """Ein benötigter Regelwert ist offen oder nicht implementiert."""

    def __init__(self, regel):
        self.regel = regel
        super().__init__(f'Regel {regel.id} ({regel.gegenstand}) ist {regel.status}: {regel.fundstelle}')

    @property
    def grund(self):
        return f'Regel offen: {self.regel.gegenstand} ({self.regel.fundstelle})'


@dataclass(frozen=True)
class Regel:
    id: str
    gegenstand: str
    fundstelle: str
    status: str
    wert: object = None
    herkunft: str = ''
    wirkung: str = 'ausgang'          # ausgang | bericht | planung | verarbeitung | generator

    def verfuegbar(self):
        return self.status not in (OF, NI) and self.wert is not None


def _r(id_, gegenstand, fundstelle, status, wert=None, herkunft='', wirkung='ausgang'):
    if status not in STATUS:
        raise ValueError(status)
    return Regel(id_, gegenstand, fundstelle, status, wert, herkunft, wirkung)


# ── Grundliste: Arbeitsfestlegungen, Regeltext, Tabelle F, technische Details, offene Punkte ──────────
_GRUND = [
    # Verarbeitung (Stufe 1)
    _r('verarbeitung.n_theta', 'Stützstellen je Zyklus', '§4, A1, A9.4 (4), Tab. F', FL, 2000, 'Tab. F: wie die Engine',
       'verarbeitung'),
    _r('verarbeitung.interpolation', 'Resampling je Zyklus', 'A9.4 (4)', RT, 'linear', '', 'verarbeitung'),
    _r('verarbeitung.filter', 'Softwarefilter', '§5.1, §8.1, A9.1, A9.4 (2)', RT, 'keine', '', 'verarbeitung'),
    _r('verarbeitung.zyklen', 'nur vollständige Zyklen im Auswertefenster', 'A9.4 (3)', RT, 'vollstaendig', '',
       'verarbeitung'),
    _r('verarbeitung.k_voll', 'Zahl gespeicherter Harmonischer je Lauf (≥ k_max; ungebändert für (a))',
       '§5.3 (a), Plan 2.6 b', TD, 60, 'Entwicklung: höchstens Nyquist der Abtastung', 'verarbeitung'),
    _r('verarbeitung.t_phi', 'Einregelzeit der Phasen je Lauf', '§5.4, §6 (T_φ)', TD,
       'erster Zyklus nach Rampenende, ab dem alle Indexphasen bis Fensterende innerhalb max(4σⱼ, 0,1°) um das '
       'Fenstermittel liegen', 'Präreg definiert T_φ nicht im Einzelnen', 'planung'),
    # Gültigkeit und Abbruch (§9.1, §9.2, §8.8, A9.8)
    _r('g2.delta_phi_tol_grad', 'Phasentoleranz δφ_tol', '§9.1 G2, Tab. F', FL, 0.5),
    _r('g2.sigma_tol', 'Jittertoleranz σ_tol', '§9.1 G2, Tab. F', FL, 3.0, 'dreifacher Median von σⱼ der Pilotläufe'),
    _r('g4.faktor', 'Fünftelkriterium', '§9.1 G4, Tab. F', FL, 3.0, '3·σ_Δ,X, σ_Δ = 1,4826·MAD je Laufart'),
    _r('g6.faktor', 'Liftoff-Schwelle F_LO,c', '§4, A1, Tab. F', FL, 5.0, 'Nullpunkt + 5·σ_c'),
    _r('g7.form', 'Form des Temperaturfensters G7', '§9.1 G7, §12 Driftbehandlung', OF),
    _r('g.einstellung2', 'G2–G4 für Läufe bei Einstellung 2', '§9.1, §12 Läufe bei Einstellung 2', OF),
    _r('s.l_strich', 'S1, S2, S4 für L₁′–L₃′', '§9.2, §12 Läufe bei Einstellung 2', OF),
    _r('h0.eps_faktor', 'ε_ctrl = 3·σ̂_ref bzw. 3·σ̂_betr', '§8.8, A9.8, Tab. F', FL, 3.0),
    _r('h0.alarm_faktor', 'Nullpunktalarm 3·√(4/3)·σ̂_ref', '§8.8, Tab. F', FL, 3.0 * (4.0 / 3.0) ** 0.5),
    _r('h0.referenzlaeufe_min', 'Referenzläufe der Phase 0', 'P0.7, Tab. F', FL, 42),
    _r('h0.sammeltest', 'Nullkontroll-Sammeltest und Wortregel', '§8.8, A9.8, §12 Wortlaut', AF,
       dict(alpha=0.05, vermerk='Einzellauftoleranz, keine Äquivalenzgrenze für das Mittel',
            aussagen=['Unterschied nachgewiesen', 'kein Unterschied nachgewiesen, Gleichheit nicht nachgewiesen']),
       '', 'bericht'),
    _r('s3.c_S', 'S3-Schwelle c_S = t(1 − 0,05/42; n₀ⱼ − 1)', '§9.2 S3, A8', RT, 42),
    # H1
    _r('h1.alpha', 'α je Familie', '§3, §8.4, Tab. F', FL, 0.05),
    _r('h1.groessen', 'H1-Größen', '§3 H1, §4', RT, ['F_min − ⟨N⟩', 'Re/Im N₁', 'Re/Im N₂', 'Re/Im N₃'],
       '21 Punkte × 7 Größen = 147 Tests; Summen- und Zellgrößen getrennt (H1Z)'),
    _r('h1.faktor', 'Äquivalenzgrenze Δ_q = Faktor·D_q', '§8.5, §12 (I), Tab. F', AF, 0.25),
    _r('h1.d_fassung', 'D für Re/Im N_k', '§8.5, A8, §12 (I)', AF, 'B', 'Fassung B: Durchmesser der Zeigermenge'),
    _r('h1.delta_rel', 'Relevanzgrenze Δ_rel,q', '§8.5, A8, §12 (I)', AF, 'gleich_delta_q'),
    _r('h1.sensitivitaet', 'Sensitivitätsvarianten (ohne Ausgangswirkung)', '§8.5, §8.9, A9.9', AF,
       dict(faktor=0.1, fassung_A=True, c_B=True), 'getrennt berichtet', 'bericht'),
    _r('h1.grenzen_quelle', 'D_q, Δ_q, Δ_rel als Punktwert aus ŷ⁰', '§8.5, A9.11, §12 (I)', AF, 'yhat0_teil_b',
       'in AP-13 je Kampagne aus ihrem verrauschten ŷ⁰'),
    _r('h1.tost', 'PB1: TOST mit t(0,95; ν_eff), IUT gegen ŷ⁰ und ŷ¹, ohne „kein |z| > c“', '§8.5, A8, Tab. F', AF,
       0.95),
    _r('h1.vollstaendigkeit', 'Bestätigung nur bei 21 auswertbaren Punkten', '§9.3', RT, 21),
    _r('h1.mindesteffekt', '|r⁰| − c·u⁰ > Δ_rel und |r¹| − c·u¹ > Δ_rel, gleiches Vorzeichen', '§8.5, §9.3', RT,
       'beide_gleiches_vorzeichen'),
    _r('h1.c_quelle', 'kritischer Wert c von H1', '§8.4, A9.3 Nr. 10', RT, 'teil_b',
       '95-%-Quantil von max|z⁰| aus der Kalibriersimulation; c_B nur Planung und Sensitivität'),
    _r('h1.c_quantil', 'Quantil von max|z⁰|', '§8.4', RT, 0.95),
    _r('h1.c_pruefschwelle', 'Prüfrate über 0,069 → gepooltes Quantil', '§8.4, A8, Tab. F', FL, 0.069),
    _r('h1.c_rauschmodelle', 'Rauschmodelle und Wahl des Quantils für c', '§8.4, §12 Rauschmodelle', OF),
    _r('h1.bias', 'Rauschbias b̂⁰, b̂¹ getrennt mit u(b̂); dieselbe Korrektur in c', '§5.4, §8.3, A9.5', RT,
       'getrennt'),
    _r('h1.bias_u', 'u(b̂): MC-Fehler und halbe Spannweite über die Rauschmodelle (Rechteck)', 'A9.5, Tab. F', FL,
       'rechteck'),
    _r('h1.rueckfall', 'Rückfall für H1 bei verfehlten Raten', '§12 Rückfall für H1', OF),
    _r('h1.zusaetze', 'Wortlaut der Zusätze', '§9.3, §9.4, §12 Wortlaut', AF,
       dict(bestaetigt='Abweichung nachgewiesen, innerhalb der Äquivalenzgrenze',
            nicht_entscheidbar='Abweichung nachgewiesen, Relevanz offen', drift='Drift der Einzelmodulbasis'),
       '', 'bericht'),
    _r('h1.gruende', 'Gründe für „nicht entscheidbar“', '§9.3, §9.4, §12 Wortlaut', AF,
       ['Präzision', 'Graubereich', 'Drift', 'Datenlage', 'Verfahren'], '', 'bericht'),
    _r('h1.grund_zuordnung', 'Zuordnung des Grundes je Test und Rangfolge', '§9.4', TD,
       'Datenlage > Verfahren > Drift > Graubereich > Präzision; Präzision: t_eq·u ≥ Δ_q, Graubereich sonst',
       'Präreg nennt nur die Klassen', 'bericht'),
    _r('h1.groesste_abweichung', 'Auswahl der „größten Abweichung“ für die Vertrauensgrenzen', '§9.3', TD,
       'größtes min(|r⁰| − c·u⁰, |r¹| − c·u¹)/Δ_q unter den Tests mit nachgewiesener Abweichung', '', 'bericht'),
    _r('h1.grenzfall', 'u_c = 0 (rauschfrei)', '—', TD,
       'u_c ≤ 1e-14·Skala gilt als null: Intervall entartet, z = 0 bei |r| ≤ 1e-14·Skala, sonst ±∞', '',
       'verarbeitung'),
    _r('drift.zusatz', 'Definition des Drift-Zusatzes', '§9.3, §12 Driftbehandlung', OF, None, '', 'bericht'),
    _r('drift.logik', 'Wirkung nachgewiesener Drift auf den Ausgang', '§9.3, §12 Driftbehandlung', OF),
    _r('bootstrap.B', 'Bootstrap-Replikate je Anteil', '§8.3, A9.5, Tab. F', FL, 10000, '', 'verarbeitung'),
    _r('bootstrap.ziehung', 'Indexmatrizen und Ziehreihenfolge', 'Plan AP-13 2.6 c', TD,
       'SeedSequence(seed).spawn: A_i in Listenreihenfolge, B¹_1…B¹_3, H3, H4, danach E3, Einstellung 2', '',
       'verarbeitung'),
    # H1Z
    _r('h1z.grenzen', 'Grenzen Δ_c,q, Δ_c,rel,q von H1Z', '§8.5, §12 Grenzen von H1Z', OF),
    _r('h1z.c_quelle', 'kritischer Wert von H1Z (441 Tests)', '§8.4', RT, 'teil_b', 'bis Teil B c_B = t(1 − α/882)'),
    # H2
    _r('h2.logik', 'Entscheidungslogik von H2', '§3, §8.6, §9.3, §12 (I)', AF, 'aequivalenz'),
    _r('h2.niveau', 'Niveau der H2-Intervalle', '§8.6, §12 (I), Tab. F', AF, 0.95),
    _r('h2.ueberdeckung', 'Überdeckungsschwelle', '§8.6, A9.6, Tab. F', FL, 0.936),
    _r('h2.replikate', 'Bootstrap-Replikate H2', '§8.6, A9.6', FL, 10000, '', 'verarbeitung'),
    _r('h2.suchschritt_grad', 'Suchschritt des Zeltfits', 'A9.6, Tab. F', FL, 0.001),
    _r('h2.gleichstand', 'Gleichstand im Zeltfit', 'A9.6', RT, 'kleinstes_phi'),
    _r('h2.rasterursprung', 'Ursprung des 0,001°-Rasters', 'A9.6 „über [min W, max W]“', TD, 'kleinste_abszisse'),
    _r('h2.delta_grad', 'δ_H2 (Äquivalenz- und Relevanzgrenze)', '§3, §8.6, §12 Grenzen von H2 und H3', OF),
    _r('h2.w_grad', 'Halbbreite w des Fitfensters', '§8.6, A9.6, §12 H2-Fitfenster', OF),
    _r('h2.mittelpunkt', 'Mittelpunkt des Fitfensters', 'A9.6, §12 H2-Fitfenster', OF),
    _r('h2.schaetzer', 'Schätzer der Spitzenlage', '§8.6, §12 Schätzer', OF),
    _r('h2.intervallkette', 'Intervalltyp und Rückfallkette', '§8.6, A9.6, §12 Intervall von H2', OF),
    _r('h2.ueberdeckung_bezug', 'Bezugswert der simulierten Überdeckung', '§8.6, §12 Intervall von H2', OF, None, '',
       'bericht'),
    _r('h2.vollstaendigkeit', 'Vollständigkeit bei H2', '§9.3, §12 Vollständigkeit', OF),
    _r('h2.lesart_entscheidbar', 'Lesart „H2 auch bei hoher Präzision entscheidbar“', 'A9.11, §12', OF, None, '',
       'bericht'),
    _r('h2.drift_zusatz', 'Drift-Zusatz bei H2', '§9.3, §12 Driftbehandlung', OF, None, '', 'bericht'),
    _r('h2.biaskorrektur', 'Rauschbias im Zeltfit', '§5.4, §8.6', TD, 'keine', 'Präreg nennt keine Korrektur für H2'),
    # H3
    _r('h3.logik', 'Entscheidungslogik von H3', '§3, §8.5, §9.3, §12 (I)', AF, 'aequivalenz'),
    _r('h3.delta', 'δ_H3', '§3, §8.5, §12 Grenzen von H2 und H3', OF),
    _r('h3.relevanz', 'Relevanzgrenze von H3', '§3, §8.5, §12', OF),
    _r('h3.fassung', 'Fassung K oder I', '§8.7, §12 (II)', OF),
    _r('h3.eingaenge', 'Eingänge nur aus P0.1–P0.5', '§3 H3, §5.2, A9.7', RT, 'kalibrierung'),
    _r('h3.mc', 'Monte-Carlo-Ziehungen', 'A9.7, Tab. F', FL, 10000, '', 'verarbeitung'),
    _r('h3.m', 'Testzahl der Familie', '§8.4, A8', RT, 18),
    # H4
    _r('h4.m', 'Testzahl (einseitig)', '§8.4, A8', RT, 23),
    _r('h4.aufnahme', 'Aufnahme in V: |γ̂₁| ≥ (c₄ + 1,645)·u_c,erw(γ₁)', '§3 H4, §8.5', RT, 1.645),
    # E3 und Zuordnung
    _r('e3.schwellen', 'Schwellen von E3 (0,1°, q_tol)', '§8.10, §12 Schwellen von E3', OF, None, '', 'bericht'),
    _r('e3.pruefzahl', 'Zahl der E3-Prüfungen (Bonferroni)', 'A9.13, §12', OF, None, '', 'bericht'),
    _r('e3.rueckfall', 'Rückfall von E3', '§8.10, A9.11, §12', OF, None, '', 'bericht'),
    _r('e3.pruefmenge', 'Prüfmenge von E3', '§12 Schwellen von E3', OF, None, '', 'bericht'),
    _r('e3.e3b_form', 'E3b als Differenz oder absolut', '§8.10, §12', OF, None, '', 'bericht'),
    _r('zuordnung.regel', 'Regel der Zuordnung', '§8.10, A9.13, §12 Zuordnung', OF, None, '', 'bericht'),
    _r('zuordnung.ausloeser', 'Auslöser der Zuordnung', '§8.10, §12 Zuordnung', OF, None, '', 'bericht'),
    _r('zuordnung.kriterium', 'Kriterium der Zuordnung (A9.11)', 'A9.11, §12 Zuordnung', OF, None, '', 'bericht'),
    _r('zuordnung.m_fest', 'm = 6·N_I fest bei Ausfällen', 'A9.13, §12 Läufe bei Einstellung 2', OF, None, '',
       'bericht'),
    _r('punkte_I', 'Punkte I', '§5.5, §12 Punkte I', OF, None, '', 'bericht'),
    _r('einstellung2.art', 'Art von Einstellung 2', '§5.5, §12 (II)', OF, None, '', 'generator'),
    _r('einstellung2.s', 'Kraftskala s', '§5.5, §12 Einstellung 2', OF, None, '', 'generator'),
    # Kontaktast, Planung, Phase 0
    _r('kontaktast.reserve', 'Mindestabstand 25 % der statischen Zelllast', '§5.3 (a), Tab. F', FL, 0.25),
    _r('kontaktast.resonanz', 'Resonanzabstand k·f ≤ f₁/2', '§5.3 (b), A6, Tab. F', FL, 0.5),
    _r('a6.interpolation', 'Abtastrate (π·k_max·f/f_s)²/2 ≤ 10⁻³', '§5.1, A6, Tab. F', FL, 1e-3, '', 'generator'),
    _r('planung.bedingung', 'P(H1 und H2 bestätigt | exakt) ≥ 0,8, Streuungen an der oberen 80-%-Grenze',
       '§5.4, A9.2, §12 (I)', AF, 0.8, '', 'planung'),
    _r('planung.faustregel', 'n_min ≥ (3·1°/(SNR·δ_H2))², notwendig, nicht hinreichend', '§5.4, A9.2', RT, 3.0, '',
       'planung'),
    _r('planung.zielfunktion', 'Zielfunktion der Laufzahlplanung', '§5.4, §12 Messzeit', OF, None, '', 'planung'),
    _r('planung.power', 'zusätzliche Power-Bedingung (Laufzahl von H1)', '§5.4, §12 Rauschmodelle …', OF, None, '',
       'planung'),
    _r('planung.n0_min', 'mindestens 20 Einzelmodulläufe je Modul', 'P0.8, §5.4, Tab. F', FL, 20, '', 'planung'),
    _r('planung.reserve', 'Reserve r = ⌈n_min·p̂/(1 − p̂)⌉ + 2', '§5.4, Tab. F', FL, 2, '', 'planung'),
    _r('planung.auslegungsgrenze', 'Startwert Δ_q/5,01 (ν → ∞) bzw. Δ_q/5,21 (ν = 19)', '§8.5, A8', RT,
       (5.012, 5.208), '', 'planung'),
    _r('p0.nachweisform', 'Nachweisform der Phase-0-Schwellen', '§5.2, A9.2, §12 Nachweis und Folge', OF, None, '',
       'bericht'),
    _r('p0.klirr_faktor', 'Klirrkriterium und P0.12 (Faktor auf u_c,erw)', '§5.2, §12 Schwelle des Klirrkriteriums',
       OF, None, '', 'bericht'),
    _r('p0.u_delta_delta_grad', 'Anforderung u(Δδⱼ) ≤ 0,1°', 'P0.5, Tab. F', FL, 0.1, 'prüfbare Anforderung',
       'bericht'),
    _r('p0.4.gewichtung', 'Kohärenzgewichtung der 1-FG-Anpassung', '§5.2 P0.4, A9.2, §12 Werkzeug 4', TD,
       'Gewicht 2·n_Mittel·γ²/((1 − γ²)·|T|²) je Real- und Imaginärteil', 'Varianz des H1-Schätzers', 'verarbeitung'),
    _r('M.konvention', 'Bestimmung von M', '§3, §4, P0.2, §12 (I)', AF, 'b',
       'M = Σ_c F_c,stat/g; Gewicht M·g, träge Masse M + m_L getrennt'),
    _r('rauschmodelle', 'Rauschmodelle (Liste in Teil A oder Teil B)', '§12 Rauschmodelle …, A9.5', OF, None, '',
       'planung'),
    # nicht implementierte Optionen
    _r('ni.fassung_I', 'H3 Fassung I (Betriebsimpedanz)', '§8.7, §12 (II)', NI),
    _r('ni.gespiegelt', 'H1′/H2′ am gespiegelten Schnitt', '§3, §6', NI),
    _r('ni.paarlaeufe', 'Paarläufe', '§5.5, §12 Paarläufe', NI),
    _r('ni.wiederaufnahme', 'Wiederaufnahme nach mechanischem Eingriff', '§9.2, §12', NI),
    _r('ni.signifikanzlogik', 'frühere Signifikanzlogik von H2/H3 und Regel vom 25.09.', 'A0, §12 (I)', NI,
       None, 'nicht als Hauptverfahren'),
    _r('ni.sensitivitaet_rest', 'übrige Sensitivitätsanalysen von A9.9', 'A9.9', NI, None,
       'Phase 0 + 1 gemeinsam, blockweise, ohne Jitterzeiger, k_max ± 2, je Block, w ± 2°, mit G1-ungültigen Läufen, '
       'ohne Biaskorrektur, Triphasik-Zusatzwerte, Zuordnung einseitig, E3 nominal'),
    _r('ni.neuberechnung', 'Neuberechnung von b̂ und c nach dem Datenschluss', '§12 Rauschmodelle …', NI),
    _r('ni.d2k', 'Auswertung von D2_K und Kabelschlaufe (P0.3)', '§5.2 P0.3', NI),
    _r('ni.einzelzell_dynamik', 'Einzelzell-Liftoff mit Stoßdynamik (nichtlineares 3-FG-Modell)', 'Plan 2.2 (c)', NI,
       None, '', 'generator'),
]

# Entwicklungsprüffälle: ausdrücklich gewählte Werte offener Regeln (nur im Profil ENTW-2026-10)
_ENTW = {
    'g7.form': ('a', 'Fassung (a) wie bisher: T_P0 ± ΔT'),
    'h1.c_rauschmodelle': ('a', 'Fassung (a): Quantil mit dem Rauschmodell des Szenarios bzw. von Teil B'),
    'drift.zusatz': ('a', 'Fassung (a): |z⁰| > c ohne gleichsinniges |z¹| > c oder umgekehrt (heutiger Text)'),
    'drift.logik': ('a', 'Fassung (a): Ausgang trotz Drift möglich, Drift als Zusatz'),
    'h1z.grenzen': ('a', 'Vorschlag (a): Δ_c,q = Δ_q/3, Δ_c,rel,q = Δ_rel,q/3'),
    'h2.delta_grad': (1.0, 'Testvariante ±1°'),
    'h2.w_grad': (6.0, 'Vorschlag w = 6° fest'),
    'h2.mittelpunkt': ('i', 'Fassung (i): Schnittpunkt mit größtem vorhergesagtem F̂_min − N_s, bei Gleichstand der '
                            'kleinere'),
    'h2.schaetzer': ('zelt', 'Fassung (a): stetiges Zelt'),
    'h2.intervallkette': ('a', 'Fassung (a): Perzentil, BCa, Perzentil mit Niveau 0,96–0,99, sonst nicht '
                               'entscheidbar; Typ aus der Kalibriersimulation (Teil B)'),
    'h2.ueberdeckung_bezug': ('schaetzer_rauschfrei', 'Wert des Schätzers an den rauschfreien Kurven; die Lage des '
                                                      'Maximums wird zusätzlich berichtet'),
    'h2.vollstaendigkeit': ('a', 'Fassung (a): alle Punkte von W auswertbar'),
    'h3.delta': (0.10, 'Testvariante ±10 %'),
    'h3.relevanz': ('gleich_delta', 'Relevanzgrenze gleich δ_H3·|N̂_k⁽ʲ⁾| (Mindestwert)'),
    'h3.fassung': ('K', 'Fassung K (Kennzeichnung) als Entwicklungsprüffall'),
    'e3.schwellen': (dict(phase_grad=0.1, q_tol=5.8e-4), 'Vorschlag (a): 0,1° und 5,8·10⁻⁴'),
    'e3.pruefzahl': ('zwei_je_konfiguration_plus_eins', 'heutige Fassung von A9.13'),
    'e3.rueckfall': ('ganz', 'Rückfall für E3 als Ganzes'),
    'e3.pruefmenge': ('auswertbare_schnittpunkte', 'ohne Identifizierbarkeits- und Zusatzkonfigurationen'),
    'e3.e3b_form': ('differenz', 'Differenz gegen die Vorhersage (heutiger Text)'),
    'zuordnung.regel': ('a', 'Fassung (a): Anpassungstest je Klasse gegen beide Vorhersagepaare'),
    'zuordnung.ausloeser': ('a', 'Fassung (a): |z⁰| > c mit gleichsinnigem |z¹| > c an einem Punkt von I'),
    'zuordnung.kriterium': ('a', 'Fassung (a): Trefferquote für Anker 0,1 % Kopplung und 1 mN Kettenresiduum'),
    'zuordnung.m_fest': ('fest', 'm = 6·N_I fest'),
    'punkte_I': ([116.0, 120.0, 124.0], 'Vorschlag (a)'),
    'einstellung2.art': ('beide', 'Generator rechnet zweite Amplitude und zweite Frequenz als Prüffälle'),
    'einstellung2.s': (0.5, 'Vorschlag s ≈ 0,5; zweite Frequenz: ganzzahlig nächst f·√0,5'),
    'planung.zielfunktion': ('a', 'Fassung (a): N_K·n_min + 3·n₀'),
    'p0.nachweisform': ('beide', 'Schätzwert und obere 95-%-Grenze werden beide berichtet, ohne Folge'),
    'p0.klirr_faktor': (0.3, 'Vorschlag (a): 0,3·u_c,erw'),
    'rauschmodelle': ('entwicklungsfamilie', 'weißes Rauschen je Zelle, Amplituden- und Phasenstreuung je Modul, '
                                             'Jitter, getrennt nach Laufart (Plan 2.2, Stufen L0–L5)'),
}


class Regelprofil:
    def __init__(self, profil_id, beschreibung, regeln, reduktion=None):
        self.id, self.beschreibung = profil_id, beschreibung
        self.regeln = {r.id: r for r in regeln}
        self.reduktion = dict(reduktion or {})

    def eintrag(self, rid):
        if rid not in self.regeln:
            raise KeyError(f'Regel {rid!r} nicht im Profil {self.id}')
        return self.regeln[rid]

    def hat(self, rid):
        return self.eintrag(rid).verfuegbar()

    def wert(self, rid):
        r = self.eintrag(rid)
        if not r.verfuegbar():
            raise RegelOffen(r)
        return copy.deepcopy(r.wert)

    def wert_oder_none(self, rid):
        return self.wert(rid) if self.hat(rid) else None

    def zahl(self, name):
        """Replikat- und Kampagnenzahlen: normativ oder reduziert (Reduktion steht im Profil)."""
        return int(self.reduktion.get(name, NORMATIVE_ZAHLEN[name]))

    def mit_reduktion(self, **zahlen):
        """Abgeleitetes Profil mit verringerten Replikat- oder Kampagnenzahlen (Entwicklungsdiagnostik)."""
        for k in zahlen:
            if k not in NORMATIVE_ZAHLEN:
                raise KeyError(k)
        red = {**self.reduktion, **{k: int(v) for k, v in zahlen.items() if int(v) != NORMATIVE_ZAHLEN[k]}}
        kenn = self.id.split('+')[0] + ('+red(' + ','.join(f'{k}={v}' for k, v in sorted(red.items())) + ')'
                                        if red else '')
        return Regelprofil(kenn, self.beschreibung, self.regeln.values(), red)

    @property
    def reduziert(self):
        return bool(self.reduktion)

    def als_dict(self):
        return dict(profil_id=self.id, beschreibung=self.beschreibung,
                    reduktion=dict(self.reduktion, normativ={k: NORMATIVE_ZAHLEN[k] for k in self.reduktion}),
                    regeln={r.id: dict(gegenstand=r.gegenstand, fundstelle=r.fundstelle, status=r.status, wert=r.wert,
                                       herkunft=r.herkunft, wirkung=r.wirkung) for r in self.regeln.values()})

    def sha256(self):
        return formate.sha256_json(self.als_dict())

    def kurz(self):
        """Profilangabe für Ergebnisse: Kennung, Prüfsumme, Reduktion und alle wirksamen Werte."""
        return dict(profil_id=self.id, sha256=self.sha256(), reduktion=self.als_dict()['reduktion'],
                    wirksam={r.id: dict(wert=r.wert, status=r.status, fundstelle=r.fundstelle)
                             for r in self.regeln.values() if r.verfuegbar()},
                    offen=sorted(r.id for r in self.regeln.values() if r.status == OF and not r.verfuegbar()),
                    nicht_implementiert=sorted(r.id for r in self.regeln.values() if r.status == NI))


def _profil_af():
    return Regelprofil('AF-2026-10', 'Arbeitsfestlegungen, Regeltext und Tabelle F der Präregistrierung v2 '
                       '(Entwicklungsversion); alle offenen Regeln offen', _GRUND)


def _profil_entw():
    regeln = []
    for r in _GRUND:
        if r.id in _ENTW:
            wert, herkunft = _ENTW[r.id]
            r = Regel(r.id, r.gegenstand, r.fundstelle, EP, wert, herkunft, r.wirkung)
        regeln.append(r)
    return Regelprofil('ENTW-2026-10', 'Entwicklungsprofil: wie AF-2026-10, dazu ausdrücklich gewählte '
                       'Entwicklungsprüffälle (Testvarianten und Vorschläge des Entwurfs); keine Festlegung', regeln)


PROFILE = {'AF-2026-10': _profil_af, 'ENTW-2026-10': _profil_entw}


def profil(name='ENTW-2026-10'):
    basis = name.split('+')[0]
    if basis not in PROFILE:
        raise KeyError(f'unbekanntes Regelprofil {name!r} (bekannt: {", ".join(PROFILE)})')
    return PROFILE[basis]()


def schreibe_profil(pfad, p):
    k = formate.kopf('regelprofil', formate.synth_kennung('REGELPROFIL', p.id))
    return formate.schreibe(pfad, k, inhalt=p.als_dict())


def lade_profil(pfad):
    """Lädt ein gespeichertes Profil; es muss bitgleich zu einem bekannten Profil (ggf. mit Reduktion) sein."""
    _, inhalt, _ = formate.lies(pfad, 'regelprofil')
    p = profil(inhalt['profil_id'])
    red = {k: v for k, v in inhalt.get('reduktion', {}).items() if k != 'normativ'}
    p = p.mit_reduktion(**red) if red else p
    if formate.sha256_json(p.als_dict()) != formate.sha256_json(inhalt):
        raise formate.FormatFehler(f'Regelprofil {inhalt["profil_id"]} weicht vom eingebauten Profil ab')
    return p


UMSETZUNG = (                           # Präfix der Regel → umsetzendes Modul (Spalte „Umsetzung“ der Regelmatrix)
    ('verarbeitung.', 'stufe1'), ('g2.', 'gueltigkeit'), ('g4.', 'gueltigkeit'), ('g6.', 'gueltigkeit'),
    ('g7.', 'gueltigkeit'), ('g.', 'gueltigkeit'), ('s.', 'gueltigkeit'), ('s3.', 'gueltigkeit'),
    ('h0.', 'gueltigkeit'), ('h1z.', 'h1'), ('h1.', 'h1, teil_b'), ('drift.', 'h1'), ('bootstrap.', 'bootstrap'),
    ('h2.', 'zeltfit, h2'), ('h3.', 'h3'), ('h4.', 'h4'), ('e3.', 'kontrollen'), ('zuordnung.', 'kontrollen'),
    ('punkte_I', 'kontrollen, generator'), ('einstellung2.', 'generator'), ('kontaktast.', 'teil_b, auswertung'),
    ('a6.', 'generator.ebene_z'), ('planung.', 'pilot, harness.planung'), ('p0.', 'anpassung'),
    ('M.', 'anpassung'), ('rauschmodelle', 'generator.rauschen, pilot'), ('ni.', '–'))


def umsetzung(rid):
    for pre, mod in UMSETZUNG:
        if rid.startswith(pre):
            return mod
    return '–'


def matrix_markdown(p=None):
    """Regelmatrix als Markdown-Tabelle (Grundlage von docs/ap11_ap12_ap13_regelmatrix.md)."""
    af, entw = profil('AF-2026-10'), profil('ENTW-2026-10')
    zeilen = ['| Regel | Gegenstand | Fundstelle | Status | Wert im Entwicklungsprofil ENTW-2026-10 | Umsetzung |',
              '|---|---|---|---|---|---|']
    for rid, r in af.regeln.items():
        e = entw.regeln[rid]
        wert = '–' if not e.verfuegbar() else json.dumps(formate._json_wert(e.wert), ensure_ascii=False)
        st = r.status + (' → entwicklungsprüffall' if e.status == EP else '')
        zeilen.append(f'| `{rid}` | {r.gegenstand} | {r.fundstelle} | {st} | {wert.replace("|", "∣")} | '
                      f'{umsetzung(rid)} |')
    return '\n'.join(zeilen) + '\n'
