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
Profile: „AF-2026-11“ (Regelstand nach dem Auftrag des Autors vom 20.10.2026: Arbeitsfestlegungen und Regeltext,
alles Offene offen) und „ENTW-2026-11“ (dazu die Entwicklungsprüffälle) sind der aktuelle Stand und die Vorgabe.
„AF-2026-10“ und „ENTW-2026-10“ bleiben unverändert erhalten: Gespeicherte Profile und Ergebnisse von PR #20 bis #23
bleiben ihrem damaligen Stand zugeordnet, und unter diesen Profilen rechnet der Code wie damals (historischer Modus).
Verringerte Replikat- oder Kampagnenzahlen erzeugen ein abgeleitetes Profil mit Kennung „…+red(…)“; die Reduktion
steht in jedem Ergebnis.

Die Regeln von 2026-11 sind methodische Arbeitsfestlegungen. Sie sind statistisch nicht kalibriert und experimentell
nicht geprüft; eine bestandene Softwareprüfung hebt diesen Status nicht auf.
"""
import copy
import json
from dataclasses import dataclass

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
    _r('bootstrap.varianz', 'Varianz der Bootstrap-Replikate', '§8.3, A9.5', TD, 'Stichprobenvarianz mit ddof = 1',
       '', 'verarbeitung'),
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
    _r('h2.gleichstand_toleranz', 'Toleranz der Gleichstandsregel im Zeltfit', 'A9.6 (nennt keine Toleranz)', TD,
       'RSS ≤ RSS_min·(1 + 10⁻⁹) + 10⁻¹²·SST + 10⁻²⁸·n·max F²', 'Rundungsgleichheit, keine statistische Toleranz',
       'verarbeitung'),
    _r('h2.quantil', 'Quantildefinition der Bootstrap-Intervalle', '§8.6, A9.6', TD, 'numpy „linear“', '',
       'verarbeitung'),
    _r('h2.replikate_gemeinsam', 'Replikate von H2 und E3', 'A9.6, A9.13, Plan 2.6 c', TD,
       'Zeilen der Bootstrap-Indexmatrizen (B_H2 = B_E3 = B)', 'h2_replikate und e3_mc folgen bootstrap_B',
       'verarbeitung'),
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
    _r('zuordnung.s_formel', 'Kraftskala s der Zuordnung', '§8.10, A9.13', TD,
       's = Σⱼ|N̄′₁⁽ʲ⁾|/Σⱼ|N̄₁⁽ʲ⁾| aus den Einzelmodulläufen', '', 'bericht'),
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
    _r('p0.4.band', 'Anpassungsband der 1-FG-Anpassung', '§5.2 P0.4, A9.2 „festgelegtes Frequenzband“', TD,
       'Eingabe', 'Teil B bzw. ausdrücklicher Aufrufparameter; kein Vorgabewert', 'verarbeitung'),
    _r('p0.4.kohaerenz_min', 'Mindestkohärenz einer Frequenzlinie', '§5.2 P0.4, Werkzeug 4', TD, 0.5,
       'Linien darunter tragen kein Signal (Kanal unbelastet)', 'verarbeitung'),
    _r('p0.4.linearitaet', 'Linearität zweier Amplituden', '§5.2 P0.4, A9.2 „gleich innerhalb der Unsicherheit“', TD,
       'χ²-Test der Übertragungsdifferenz p ≥ 0,01 und |z| < 3 für f_n, ζ', '', 'bericht'),
    _r('p0.4.modellordnung', 'Zahl der Moden aus den Zellkanälen', '§5.2 P0.4, A1 (f₁, f_m, ζ_m)', TD,
       'gemeinsame Pole, zusätzliche Mode bei F-Test p ≤ 0,01; Moden außerhalb des Bands nicht bestimmt', '',
       'verarbeitung'),
    _r('p0.gf_modell', 'Modell der Kraftkette G_F aus dem Brückensimulator', '§5.2 P0.1, A9.7, Werkzeug 4', TD,
       'g·e^{−i2πfτ}/(1 + if/f_tp); ohne nachweisbaren Tiefpass g·e^{−i2πfτ}', 'Entwicklungsmodell', 'verarbeitung'),
    _r('verarbeitung.kennlinie', 'Umrechnung der Rohwerte in Stufe 1', 'A9.4 (1) „statische Kalibrierung je Zelle“',
       TD, 'linear', 'Nullpunkt und Empfindlichkeit aus P0.1; quadratischer Anteil nur berichtet (Befund: Text legt '
                     'die Kennlinienform der Umrechnung nicht fest)', 'verarbeitung'),
    _r('M.konvention', 'Bestimmung von M', '§3, §4, P0.2, §12 (I)', AF, 'b',
       'M = Σ_c F_c,stat/g; Gewicht M·g, träge Masse M + m_L getrennt'),
    _r('rauschmodelle', 'Rauschmodelle (Liste in Teil A oder Teil B)', '§12 Rauschmodelle …, A9.5', OF, None, '',
       'planung'),
    # Harness (Werkzeug 8): Umsetzungsdetails der Kalibrier- und Prüfsimulation
    _r('harness.c_vollstaendig', 'Kampagnen für das Quantil von c', '§8.4 „über die 147 korrelierten Tests“', TD,
       'nur Kampagnen mit allen Tests; ausgeschlossene werden gezählt', '', 'planung'),
    _r('harness.c_pool', 'gepooltes Quantil bei Prüfrate > 0,069', '§8.4', TD,
       '95-%-Quantil der vereinigten max|z⁰| beider Simulationen; Prüfsimulation danach neu ausgewertet', '',
       'planung'),
    _r('harness.ueberdeckung_beide', 'Überdeckung gegen ŷ⁰ und ŷ¹', '§8.6, A9.6', TD,
       'ein Intervalltyp gilt, wenn beide Überdeckungen die Schwelle erreichen', '', 'planung'),
    _r('harness.planung_rauschen', 'Rauschmodell der Planungssimulation', '§5.4, A9.2', TD,
       'Rauschmodell des Szenarios mit κ = √(ν_p/χ²₀,₂(ν_p)) skaliert (obere 80-%-Grenze)',
       'Generator aus gemessenen Pilotkovarianzen fehlt', 'planung'),
    _r('harness.seeds', 'Seeds der Kampagnen', 'Plan 4.3', TD, 'unterseed(Basis, Rolle, Szenario, Stufe, i)',
       'unabhängig von Prozesszahl und Reihenfolge', 'planung'),
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


# ── Regelstand 2026-11 (Auftrag des Autors vom 20.10.2026, Entscheidungsvorlage vom 19.10.2026) ──────────────
AUFTRAG = 'Arbeitsfestlegung nach dem Auftrag des Autors vom 20.10.2026 (Entscheidungsvorlage 2026-10-19, Abschnitt 9)'
_AENDERUNG_11 = [
    _r('g4.faktor', 'Fünftelkriterium (Faktor der Schwelle im historischen Modus je Laufart und für Lⱼ)',
       '§9.1 G4, Tab. F', FL, 3.0, '3·σ_Δ,X, σ_Δ = 1,4826·MAD je Laufart; Konfigurationen siehe g4.verfahren'),
    _r('e3.schwellen', 'Schwellen von E3 (0,1°, q_tol)', '§8.10, §12 Schwellen von E3', AF,
       dict(phase_grad=0.1, q_tol=5.8e-4), AUFTRAG + '; Schwellen unverändert', 'bericht'),
    _r('e3.pruefzahl', 'Zahl der E3-Prüfungen (Bonferroni)', 'A9.13, §12', AF, 43,
       AUFTRAG + '; 21 Schnittpunkte × 2 E3a-Prüfungen + E3b; fehlende Punkte und Rückfall verringern m nicht',
       'bericht'),
    _r('e3.rueckfall', 'Rückfall von E3', '§8.10, A9.11, §12', AF, 'je_pruefgroesse',
       AUFTRAG + '; E3b beschreibend bzw. einseitig, E3a bleibt dreiwertig', 'bericht'),
    _r('e3.pruefmenge', 'Prüfmenge von E3', '§12 Schwellen von E3', AF, 'schnitt21_triphasik',
       AUFTRAG + '; ohne Identifizierbarkeits- und Zusatzkonfigurationen', 'bericht'),
    _r('e3.e3b_form', 'E3b als Differenz oder absolut', '§8.10, §12', AF, 'differenz', AUFTRAG, 'bericht'),
    _r('h1.c_rauschmodelle', 'Rauschmodelle und Wahl des Quantils für c', '§8.4, §12 Rauschmodelle', AF, 'a',
       AUFTRAG + '; Fassung (a): Quantil aus dem Standardmodell, die Modellliste als Sensitivität'),
    _r('h1.bias', 'Rauschbias b̂⁰, b̂¹ getrennt mit u(b̂); dieselbe Korrektur in c', '§5.4, §8.3, A9.5', RT,
       'getrennt', 'mit den tatsächlich realisierten gültigen Laufzahlen der Auswertungsmenge A (Auftrag 20.10.2026)'),
    _r('rauschmodelle', 'Rauschmodelle (Liste in Teil A oder Teil B)', '§12 Rauschmodelle …, A9.5', AF,
       dict(standard='strukturmodell_phase0', eingebettet='familienanpassung', sensitivitaet='benannte_szenarien',
            bootstrap='optional'), AUFTRAG, 'planung'),
    _r('harness.c_vollstaendig', 'Kampagnen für das Quantil von c', '§8.4 „über die 147 korrelierten Tests“', AF,
       'menge_A', AUFTRAG + '; Auswertungsmenge A (harness.mengen), Ausschlüsse nach Grund gezählt', 'planung'),
    _r('harness.planung_rauschen', 'Rauschmodell der Planungssimulation', '§5.4, A9.2', AF,
       'phase0_modell', AUFTRAG + '; Modell aus Phase 0, obere 80-%-Grenze je identifizierbarer Komponente '
       '(planung.obere_grenze); das Szenariomodell bleibt unabhängige Referenz', 'planung'),
]
_NEU_11 = [
    # Ablauf der Phase 1 (A9.12, §9.2)
    _r('ablauf.fassung', 'Fassung des zustandsbehafteten Ablaufs', '§6, §8.8, §9.2, A9.12', AF, 'ablauf-4', AUFTRAG,
       'ablauf'),
    _r('ablauf.reihenfolge', 'Reihenfolge sofortiger Folgeläufe (A1 + Z1)', '§9.2, A9.12', AF,
       'R₁ zuerst; feststehender Verstoß → R₂, X′, R₃ geschlossen, auch bei ungültigem X′; danach übrige sofortige '
       'Wiederholungen, die zuletzt ausgelöste zuerst; ein sofortiger Halt hat Vorrang', AUFTRAG, 'ablauf'),
    _r('ablauf.halt', 'Ausstehende Folgeläufe und unvollständige Klammer bei Halt (H1 + K1)', '§9.2, A9.12', AF,
       'ausstehende sofortige Folgeläufe verworfen und protokolliert; G1-Fall ohne gemessenes X′ nach dem W-Satz als '
       'neue Folge R₂, X′, R₃; unvollständige Klammer: S1 nicht prüfbar, keine Sonderwiederholung, Platz fehlt',
       AUFTRAG, 'ablauf'),
    _r('ablauf.wiederaufnahme_alarm', 'Alarm im Kontrollsatz der Wiederaufnahme (N7)', '§9.2, §8.8', AF,
       'S1–S4; einzelne S3-Überschreitung und einzelner Nullpunktalarm werden wie sonst wiederholt, der reproduzierte '
       'Alarm hält an', AUFTRAG, 'ablauf'),
    _r('ablauf.bezugseroeffnung', 'Neuer Bezug nach einem Nullpunkthalt', '§8.8, §9.2, A9.12', AF,
       dict(ausloeser=['S1 reproduzierter Nullpunktalarm', 'Nullpunktalarm (technische Grenze)'],
            lauf='gesonderter Referenzlauf vor dem W-Satz, ohne Alarmvergleich gegen das verworfene R₀',
            grenze_wiederholungen=2, danach='Halt „Bezugseröffnung“ (verbraucht eine Wiederaufnahme)',
            ersatz='letzter gültiger Aufwärmlauf bei Tageswechsel'), AUFTRAG, 'ablauf'),
    _r('ablauf.aufwaermen', 'Aufwärmen nach einer Wiederaufnahme', '§6, §9.2', AF, 'nur_tageswechsel',
       AUFTRAG + '; durch Halt unterbrochener Block darf über Nacht fortgesetzt werden', 'ablauf'),
    _r('ablauf.tageswechsel', 'Tageswechsel bei der Wiederaufnahme in der Simulation', '§6', TD,
       'Ereignisfeld tageswechsel; fehlt es, gilt Zeitpunkt − Halt ≥ tag_pause des Plans',
       'Simulationsdetail, keine Fachregel', 'ablauf'),
    # Phase 0
    _r('p0.anordnung', 'Anordnung der Referenzläufe in Phase 0 (P0.7)', 'P0.7, A9.2', AF,
       dict(min_referenz=42, max_abstand=12, verteilung='gleichmaessig_mit_anfang_und_ende'),
       AUFTRAG + '; „nach zwölf“ als größter Abstand; tatsächliche gültige Zahl und Anordnung werden ausgewiesen',
       'generator'),
    _r('p0.laufgroessen', 'Laufgrößenmodell aus Phase 0 (Schätzer d0)', '§5.4, A9.2, A9.3', AF,
       dict(amplitude_phase='kohärente Projektion der Lⱼ-Abweichungen (σ_a,j, σ_δ,j, ν = n₀ⱼ − 1)',
            versatz='Laufmittel der Indexphasen der gültigen Piloten (σ_off,j)', boden='Referenzläufe'),
       AUFTRAG, 'planung'),
    # G4
    _r('g4.verfahren', 'Standardisierung der Fünftelschwelle für Konfigurationen', '§9.1 G4, A9.2', AF, 'b_plus',
       AUFTRAG + '; D (phasenkorrigierte Fünftel-Differenz) wählbarer Diagnosemodus, je_laufart historisch'),
    _r('g4.b_plus', 'Bestandteile von B+', '§9.1 G4', AF,
       dict(mischung='Laufversatz, Phasenrest, Modulamplitude', piloten='dieselbe Mischung für s̄_P',
            knick='Maximum über ±u(Δδⱼ)', ziehungen='normiert', schwelle='quantil', untergrenze_faktor=3.0),
       AUFTRAG),
    _r('g4.zielrate', 'Arbeitsziel der Fehlausschlüsse je Konfiguration und Lauf', 'A9.11', AF, 0.015,
       AUFTRAG + '; Zielvorgabe unter dem benannten Nullmodell, keine bestätigte Rate', 'bericht'),
    _r('g4.lj', 'G4 an Einzelmodul-Kontrollläufen', '§9.1 G4', AF,
       dict(schwelle='n_abhaengig', vergleich='pooling'), AUFTRAG),
    # E3
    _r('e3.grenzen', 'Konstruktion der E3-Grenzen (Option B)', '§8.10, A9.13', AF,
       dict(e3a='t_quantil_gefaltet', e3b='rice_kappa_lambda_max', nu='min_n_minus_1', nu_min=5,
            unauffaellig='t_0.95'), AUFTRAG, 'bericht'),
    _r('e3.zusatzszenarien', 'Zusätzliche E3b-Prüffälle', 'A9.11', AF, [0.005, 0.01],
       AUFTRAG + '; Amplitudenänderung 0,5 % und 1 % als kleine Zusatzprüffälle', 'bericht'),
    # Harness, Planung
    _r('harness.wiederaufnahme', 'Simulierte Wiederaufnahme fortsetzbarer Halte', '§9.2, A9.11', AF,
       dict(W=3, T_UA='Teil B', T_UA_entwicklung_s=1800.0,
            ereignis='Ursachenanalyse ohne Befund, kein Eingriff, kein Apparaturfehler'),
       AUFTRAG + '; nur im synthetischen Harness, nie für reale Daten', 'planung'),
    _r('harness.mengen', 'Bezugsmengen der Simulationen', '§5.4, §8.4, §8.6, A9.11', AF,
       dict(G='alle begonnenen Kampagnen der Rolle, einschließlich endgültig beendeter',
            A='abgeschlossen (auch nach Wiederaufnahme), ŷ¹ gültig, alle benötigten Prüfgrößen endlich'),
       AUFTRAG + '; P(H1 und H2) mit Nenner G', 'planung'),
    _r('harness.nachziehen', 'Sollzahl der Auswertungsmenge und Nachziehen', '§8.4, §8.6', AF,
       dict(soll_A=1000, versuchslimit_faktor=1.5),
       AUFTRAG + '; nur im Kalibrierbeispiel, bei Nichterreichen „nicht abgeschlossen“', 'planung'),
    _r('planung.reserve_ziel', 'Bedingung für die Reserve r', 'A9.2 (v)', AF,
       dict(anteil=0.95, nenner='nicht_endgueltig_beendet', zusatz_max=10),
       AUFTRAG + '; alle Schnittpunkte gemeinsam ≥ n_min', 'planung'),
    _r('planung.zeitformel', 'Terme der Zeitformel', '§5.3 (c), §12 Messzeit', AF,
       ['Läufe', 'Wiederholungen', 'Kontrollsatz der Wiederaufnahme', 'Bezugseröffnung', 'Ursachenanalyse T_UA',
        'Aufwärmen bei Tageswechsel'], AUFTRAG, 'planung'),
    _r('planung.obere_grenze', 'Obere 80-%-Grenze eines mehrteiligen Rauschmodells', '§5.4, A9.2', AF,
       'je_komponente_gemeinsamer_boden',
       AUFTRAG + '; marginale Grenzen, keine gemeinsame 80-%-Garantie', 'planung'),
    _r('planung.teil_b_werte', 'Teil-B-Werte aus Punktschätzern nach der Planung', '§8.4, A9.2, A9.11', AF,
       'punktschaetzer', AUFTRAG + '; Planung mit c_B an der oberen Grenze, danach Parameterschätzung', 'planung'),
    # Teil d2: Umsetzung des Strukturmodells (technisch; Begründung: der Auftrag verlangt, Regularisierung und nicht
    # identifizierbare Komponenten ausdrücklich zu behandeln und nicht Identifizierbares als benannte Sensitivitäten
    # mit festen Stärken zu führen; die Stärken sind ein Vorschlag der Umsetzung, ihre Festlegung gehört in Teil A)
    _r('p0.strukturmodell', 'Regularisierung und Annahmen des Strukturmodells aus Phase 0', '§5.4, A9.2, A9.11', TD,
       dict(punkt='√max(0, s² − Boden), abgeschnitten bei null',
            obere_grenze='√max(0, s²·ν/χ²₀,₂(ν) − Boden) je Komponente; Boden von ⟨N⟩: ein Faktor für alle Laufarten',
            nicht_identifizierbar='0, ausdrücklich benannt, als benannte Sensitivität geführt',
            rest='orthogonaler Rest je Modul und Harmonischer als Vielfaches des Zellbodens, laufweise',
            kombination='Streuung der Kombinationsläufe wie in den Lⱼ-Läufen (Übertragungstest an den Piloten)',
            boden='weiß über die Zyklen (σ ∝ 1/√T_a)',
            nullpunkt='Drift und Zufallspfad über die Betriebszeit (ohne Pausen); Sprünge zwischen Messtagen und '
                      'Phasen: Sensitivität drift_messtage'),
       'Umsetzung Teil d2 (generator.phase0_modell); Klärung am Normtext (A9.2, A9.11)', 'planung'),
    _r('rauschmodelle.sensitivitaeten', 'Benannte Sensitivitätsszenarien des Rauschmodells mit festen Stärken',
       '§12 Rauschmodelle, A9.11', TD,
       dict(version='sensitivitaeten-0.1', szenarien={
           'jitter_farbig': 'farbiger Jitter: AR(1) über die Zyklen mit Koeffizient 0,9',
           'jitter_korreliert': 'Jitter der Module 2 und 3 je Zyklus korreliert (ρ = 0,5)',
           'jitter_lastabhaengig': 'Jitter der Kombinationsläufe × (1 + 0,5·q₁(φ))',
           'phasendrift_lauf': 'lineare Indexphasendrift 0,1° über den Kombinationslauf (Module 2, 3)',
           'kombination_doppelt': 'Amplituden- und Phasenstreuung der Kombinationsläufe doppelt so groß wie in Lⱼ',
           'laufzeit_gemeinsam': 'gemeinsame Laufzeitschwankung der Kette statt modulweisem δ in den '
                                 'Kombinationsläufen',
           'amplitude_doppelt': 'Amplitudenstreuung je Modul doppelt so groß (alle Laufarten)',
           'nullpunkt_diffusion': 'Zufallspfad des Nullpunkts mit D·13·T_Lauf = σ²_m,Σ (Leave-one-out-Varianz am '
                                  'Abstand von P0.7 etwa verdoppelt)',
           'drift_phase1': 'Drift der Einzelmodulbasis zwischen Phase 0 und Phase 1: +0,1 % Amplitude aller Module '
                           'in Phase 1',
           'drift_messtage': 'Nullpunktsprung zwischen Messtagen und zwischen den Phasen, zufällig je Abschnitt mit '
                             'Streuung 2·σ_m,Σ'}),
       'Vorschlag der Umsetzung Teil d2, nur berichtet (keine Wirkung auf Ausgänge); Festlegung in Teil A ausstehend',
       'bericht'),
]
_ENTW_ENTSCHIEDEN_11 = ('e3.schwellen', 'e3.pruefzahl', 'e3.rueckfall', 'e3.pruefmenge', 'e3.e3b_form',
                        'h1.c_rauschmodelle', 'rauschmodelle')


def _grund_2026_11():
    ersatz = {r.id: r for r in _AENDERUNG_11}
    out = [ersatz.get(r.id, r) for r in _GRUND]
    ids = {r.id for r in out}
    for r in _NEU_11:
        if r.id in ids:
            raise ValueError(f'Regel {r.id} doppelt')
        out.append(r)
    return out


DIAGNOSEWERTE = {'g4.verfahren': ('d', 'je_laufart')}    # wählbare Diagnose-/Vergleichsmodi (nicht Standard)


class Regelprofil:
    def __init__(self, profil_id, beschreibung, regeln, reduktion=None, diagnose=None):
        self.id, self.beschreibung = profil_id, beschreibung
        self.regeln = {r.id: r for r in regeln}
        self.reduktion = dict(reduktion or {})
        self.diagnose = dict(diagnose or {})

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
        """Abgeleitetes Profil mit verringerten Replikat- oder Kampagnenzahlen (Entwicklungsdiagnostik).
        H2 und E3 verwenden die Zeilen der Bootstrap-Indexmatrizen (A9.6, A9.13); h2_replikate und e3_mc folgen
        deshalb bootstrap_B."""
        for k in zahlen:
            if k not in NORMATIVE_ZAHLEN:
                raise KeyError(k)
        if 'bootstrap_B' in zahlen:
            for k in ('h2_replikate', 'e3_mc'):
                if k in zahlen and int(zahlen[k]) != int(zahlen['bootstrap_B']):
                    raise ValueError(f'{k} folgt bootstrap_B (gemeinsame Zeilen der Indexmatrizen)')
                zahlen[k] = zahlen['bootstrap_B']
        red = {**self.reduktion, **{k: int(v) for k, v in zahlen.items() if int(v) != NORMATIVE_ZAHLEN[k]}}
        return Regelprofil(self._kennung(red, self.diagnose), self.beschreibung, self.regeln.values(), red,
                           self.diagnose)

    def _kennung(self, red, diag):
        return (self.id.split('+')[0]
                + ('+diag(' + ','.join(f'{k}={v}' for k, v in sorted(diag.items())) + ')' if diag else '')
                + ('+red(' + ','.join(f'{k}={v}' for k, v in sorted(red.items())) + ')' if red else ''))

    def mit_diagnose(self, **werte):
        """Abgeleitetes Profil mit einem ausdrücklich gewählten Diagnose-/Vergleichsmodus (DIAGNOSEWERTE, z. B.
        g4.verfahren='d'); Kennung „+diag(…)“, der Status der Regel wird EP (Entwicklungsprüffall). Nur für Regeln
        des Profilstands, die den Modus vorsehen."""
        werte = {k.replace('__', '.'): v for k, v in werte.items()}
        neu = dict(self.regeln)
        for rid, v in werte.items():
            if rid not in DIAGNOSEWERTE or v not in DIAGNOSEWERTE[rid]:
                raise ValueError(f'Diagnosemodus {rid}={v!r} nicht vorgesehen ({DIAGNOSEWERTE})')
            if rid not in self.regeln:
                raise KeyError(f'Regel {rid!r} nicht im Profil {self.id}')
            r = self.regeln[rid]
            neu[rid] = Regel(r.id, r.gegenstand, r.fundstelle, EP, v,
                             f'Diagnosemodus (nicht Standard; Standard {r.wert!r}): {r.herkunft}', r.wirkung)
        diag = {**self.diagnose, **werte}
        return Regelprofil(self._kennung(self.reduktion, diag), self.beschreibung, neu.values(), self.reduktion, diag)

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


def _profil_af_11():
    return Regelprofil('AF-2026-11', 'Regelstand nach dem Auftrag vom 20.10.2026: Arbeitsfestlegungen, Regeltext und '
                       'Tabelle F der Präregistrierung v2 (Entwicklungsversion); alle offenen Regeln offen',
                       _grund_2026_11())


def _profil_entw_11():
    regeln = []
    for r in _grund_2026_11():
        if r.id in _ENTW and r.id not in _ENTW_ENTSCHIEDEN_11:
            wert, herkunft = _ENTW[r.id]
            r = Regel(r.id, r.gegenstand, r.fundstelle, EP, wert, herkunft, r.wirkung)
        regeln.append(r)
    return Regelprofil('ENTW-2026-11', 'Entwicklungsprofil: wie AF-2026-11, dazu ausdrücklich gewählte '
                       'Entwicklungsprüffälle (Testvarianten und Vorschläge des Entwurfs); keine Festlegung', regeln)


PROFILE = {'AF-2026-10': _profil_af, 'ENTW-2026-10': _profil_entw, 'AF-2026-11': _profil_af_11,
           'ENTW-2026-11': _profil_entw_11}
AKTUELL = ('AF-2026-11', 'ENTW-2026-11')
HISTORISCH = ('AF-2026-10', 'ENTW-2026-10')
STANDARD = 'ENTW-2026-11'


def stand(p):
    """Regelstand eines Profils: '2026-11' (aktuell) oder '2026-10' (historisch)."""
    return p.id.split('+')[0].split('-', 1)[1]


def ist_historisch(p):
    return p.id.split('+')[0] in HISTORISCH


def profil(name=STANDARD):
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
    ('a6.', 'generator.ebene_z'), ('planung.', 'pilot, harness.planung'), ('p0.anordnung', 'generator.kampagne'),
    ('p0.laufgroessen', 'laufgroessen, pilot, teil_b'),
    ('p0.strukturmodell', 'generator.phase0_modell, harness.planung'), ('p0.', 'anpassung'),
    ('ablauf.', 'ablauf, auswertung'), ('M.', 'anpassung'),
    ('rauschmodelle.sensitivitaeten', 'generator.phase0_modell, harness.planung'),
    ('rauschmodelle', 'generator.rauschen, pilot'), ('harness.', 'harness'), ('ni.', '–'))


UMSETZUNG_11 = (                        # Stand 2026-11: zusätzliche bzw. genauere Module (vor UMSETZUNG geprüft)
    ('g4.', 'gueltigkeit, g4, teil_b'), ('e3.', 'kontrollen, e3_grenzen'), ('h1.c_rauschmodelle', 'harness.kalibrierung'),
    ('harness.mengen', 'harness.mengen, harness.kalibrierung'), ('harness.nachziehen', 'harness.mengen'),
    ('harness.wiederaufnahme', 'harness.kette, ablauf'), ('planung.reserve', 'harness.reserve, harness.planung'),
    ('planung.zeitformel', 'harness.reserve'), ('p0.laufgroessen', 'laufgroessen, pilot, teil_b'))


def umsetzung(rid, stand_=None):
    for pre, mod in (UMSETZUNG_11 if stand_ == '2026-11' else ()) + UMSETZUNG:
        if rid.startswith(pre):
            return mod
    return '–'


def matrix_markdown(stand_='2026-11'):
    """Regelmatrix als Markdown-Tabelle: Stand 2026-11 in docs/ap11_ap12_ap13_regelmatrix.md, der historische Stand
    2026-10 unverändert in docs/ap11_ap12_ap13_regelmatrix_2026-10.md."""
    af, entw = profil(f'AF-{stand_}'), profil(f'ENTW-{stand_}')
    zeilen = [f'| Regel | Gegenstand | Fundstelle | Status | Wert im Entwicklungsprofil {entw.id} | Umsetzung |',
              '|---|---|---|---|---|---|']
    for rid, r in af.regeln.items():
        e = entw.regeln[rid]
        wert = '–' if not e.verfuegbar() else json.dumps(formate._json_wert(e.wert), ensure_ascii=False)
        st = r.status + (' → entwicklungsprüffall' if e.status == EP else '')
        zeilen.append(f'| `{rid}` | {r.gegenstand} | {r.fundstelle} | {st} | {wert.replace("|", "∣")} | '
                      f'{umsetzung(rid, stand_)} |')
    return '\n'.join(zeilen) + '\n'
