# PCMMS — Literaturabgleich für Forschungsrahmen v3.6 und Arbeitspapier

**Stand:** 12. September 2026 – Version v3 (Korrekturläufe; Änderungslog in §8) · Repository-Fassung 20.09.2026: organisatorische Punkte (Einreichungswege) entfernt, Zieltext (B) als „Arbeitspapier“ bezeichnet, sonst unverändert  
**Autor des PCMMS-Korpus:** Matthias Früh  
**Funktion:** Einmal geschriebener Arbeitsabgleich für zwei Zieltexte: (A) `PCMMS_Forschungsrahmen_v3.6` und (B) Forschungsstand des Arbeitspapiers.  
**Status:** Literatur- und Änderungsgrundlage; keine experimentelle Evidenz und kein Ersatz für Primärmessungen.

## 0. Verifikationsregel und Reichweite

1. Externe Aussagen werden gegen Primärquellen bzw. Originalarbeiten geprüft.
2. PCMMS-Zahlen werden gegen `PCMMS_Forschungsrahmen_v3_5_Frueh_2026.md` und `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md` geprüft.
3. Befund, analytische Folge, numerische Erwartung und offene Hypothese werden getrennt bezeichnet.
4. Der bereits vorliegende Architekturvergleich Popov ↔ PCMMS (Vorarbeit vom 12.09.2026, Gegenüberstellung Architektur/Mechanismus; nicht als Projektdatei abgelegt) wird nicht dupliziert. Ergänzt werden die dort fehlende **Regime-Abgrenzung**, der **Ratchet-Symmetrierahmen** und die **Kontaktmodell-Prüfspezifikation**.
5. Dieser Abgleich darf in v3.6 knapp und im Forschungsstand des Arbeitspapiers ausführlich verwendet werden; Zahlen, Zitate und Literaturangaben bleiben dabei identisch.

## 1. Verifizierte Referenzen

### 1.1 BibTeX-Arbeitsblock

```bibtex
@article{PopovLi2018,
  author  = {Popov, Mikhail and Li, Qiang},
  title   = {Multimode Active Control of Friction, Dynamic Ratchets and Actuators},
  journal = {Physical Mesomechanics},
  year    = {2018},
  volume  = {21},
  number  = {1},
  pages   = {24--31},
  doi     = {10.1134/S1029959918010046},
  eprint  = {1705.03379},
  archivePrefix = {arXiv},
  note    = {arXiv-Fassung betitelt: Multi-mode active control of friction, dynamic ratchets and actuators; Originalfassung Fiz. Mezomekh. 20(5), 26--32 (2017)}
}

@article{MadatovLiPopov2026,
  author  = {Madatov, Ibrohim and Li, Qiang and Popov, Valentin L.},
  title   = {From Friction Control to Dynamic Ratcheting and Actuation by Combined Normal and Tangential Oscillations},
  journal = {Lubricants},
  year    = {2026},
  volume  = {14},
  number  = {8},
  pages   = {286},
  doi     = {10.3390/lubricants14080286}
}

@article{Feng2026PhaseSpace,
  author  = {Feng, Y. T.},
  title   = {Exact Phase-Space Analytical Solution for the Power-Law Damped Contact Oscillator},
  year    = {2026},
  eprint  = {2603.27764},
  archivePrefix = {arXiv},
  primaryClass = {physics.comp-ph}
}

@article{Feng2026Harmonic,
  author  = {Feng, Y. T.},
  title   = {Hidden Harmonic Structure, Universal Damping, and Stability Bounds in Nonlinear Contact Dynamics},
  year    = {2026},
  eprint  = {2604.02533},
  archivePrefix = {arXiv}
}

@article{Feng2026EnergyPhase,
  author  = {Feng, Y. T.},
  title   = {Controlling Normal Energy Dissipation in Energy-Conserving Contact Models for Non-Spherical Particles: Energy--Phase Harmonisation and Adaptive Damping},
  journal = {Computational Mechanics},
  year    = {2026},
  doi     = {10.1007/s00466-026-02853-z}
}

@article{FlachYevtushenkoZolotaryuk2000,
  author  = {Flach, Sergej and Yevtushenko, O. and Zolotaryuk, Y.},
  title   = {Directed Current due to Broken Time-Space Symmetry},
  journal = {Physical Review Letters},
  year    = {2000},
  volume  = {84},
  pages   = {2358--2361},
  doi     = {10.1103/PhysRevLett.84.2358},
  eprint  = {chao-dyn/9908016},
  archivePrefix = {arXiv}
}

@article{DenisovFlachHanggi2014,
  author  = {Denisov, Sergey and Flach, Sergej and H{\"a}nggi, Peter},
  title   = {Tunable Transport with Broken Space--Time Symmetries},
  journal = {Physics Reports},
  year    = {2014},
  volume  = {538},
  number  = {3},
  pages   = {77--120},
  doi     = {10.1016/j.physrep.2014.01.003},
  eprint  = {1311.1086},
  archivePrefix = {arXiv}
}

@article{ZigelmanEtAl2026,
  author  = {Zigelman, Anna and Israel, Gilad and Or, Yizhar and Starosvetsky, Yuli},
  title   = {Passive Vibration-Driven Locomotion},
  journal = {Nonlinear Dynamics},
  year    = {2026},
  volume  = {114},
  number  = {10},
  pages   = {756},
  note    = {Artikelnummer 756; Open Access, online 26.05.2026},
  doi     = {10.1007/s11071-026-12592-8}
}

@article{WangEtAl2026Capsule,
  author  = {Wang, Zepeng and Tian, Jiyuan and Liu, Yang and Neves, Ana and Prasad, Shyam},
  title   = {Fluid-Structure Dynamics of a Vibro-Impact Capsule Robot in Multiphase Intestinal Environments},
  journal = {Nonlinear Dynamics},
  year    = {2026},
  volume  = {114},
  number  = {4},
  pages   = {294},
  note    = {Artikelnummer 294; online 26.02.2026},
  doi     = {10.1007/s11071-025-12175-z}
}

@article{MaoEtAl2017,
  author  = {Mao, Xinyu and Popov, Valentin L. and Starcevic, Jasminka and Popov, Mikhail},
  title   = {Reduction of Friction by Normal Oscillations. II. In-Plane System Dynamics},
  journal = {Friction},
  year    = {2017},
  volume  = {5},
  number  = {2},
  pages   = {194--206},
  doi     = {10.1007/s40544-017-0146-x},
  eprint  = {1611.07018},
  archivePrefix = {arXiv}
}

@article{TeideltEtAl2012,
  author  = {Teidelt, Elena and Willert, Emanuel and Filippov, Alexander E. and Popov, Valentin L.},
  title   = {Modeling of the Dynamic Contact in Stick-Slip Microdrives Using the Method of Reduction of Dimensionality},
  journal = {Physical Mesomechanics},
  year    = {2012},
  volume  = {15},
  number  = {5--6},
  pages   = {287--292},
  doi     = {10.1134/S1029959912030071}
}

@article{PapangeloCiavarella2015,
  author  = {Papangelo, Antonio and Ciavarella, Michele},
  title   = {On the Limits of Quasi-Static Analysis for a Simple Coulomb Frictional Oscillator in Response to Harmonic Loads},
  journal = {Journal of Sound and Vibration},
  year    = {2015},
  volume  = {339},
  pages   = {280--289},
  doi     = {10.1016/j.jsv.2014.11.028}
}
```

**Namensprüfung:** Erstautor der Arbeit von 2018 ist **Mikhail Popov (M. Popov)**, nicht V. L. Popov. V. L. Popov ist Mitautor der Arbeit von 2026; deren Erstautor ist **Ibrohim Madatov** (v1 dieser Datei: „Islam“ – falsch). Der Journaltitel der Arbeit von 2018 lautet „Multimode …“, die arXiv-Fassung „Multi-mode …“.

**Prüfstand 12.09.2026:** Alle Einträge in 1.1 gegen Verlags- bzw. arXiv-Seiten geprüft (Autoren, Jahr, Band, Seiten/Artikelnummer, DOI). Die DOI von Papangelo/Ciavarella ist am 12.09.2026 geklärt: 10.1016/j.jsv.2014.11.028 (ScienceDirect-Verlagstreffer, übereinstimmend mit der Crossref-Referenz in Chaos 35, 053126 (2025)); die Angabe …2014.10.034 aus v1 war falsch. Damit ist in 1.1 nichts mehr offen.

### 1.2 Nachzutragen (aus der Referenzliste des Lubricants-Papers; DOI offen)

```bibtex
@inproceedings{MadatovLiPopov2025AIP,
  author    = {Madatov, Ibrohim and Li, Qiang and Popov, Valentin L.},
  title     = {Actuators Based on Superposition of Normal and Tangential Oscillations},
  booktitle = {AIP Conference Proceedings},
  year      = {2025},
  volume    = {3177},
  pages     = {040004},
  note      = {Kurzvorl{\"a}ufer von MadatovLiPopov2026 (dort Ref. 15; Referenzliste gibt 40004); DOI nachtragen}
}
```

## 2. Abgleichpunkte gegen v3.5

### 2.1 §2 und Titel/Zusammenfassung — Linien A und B getrennt positionieren

**v3.5-Passage:** Titel und Zusammenfassung verbinden Wellenformsteuerung unmittelbar mit „medium-gekoppelter Fortbewegung“; §2 grenzt vor allem gegen Gewichtsreduktion und Leerraumantrieb ab.

**Externe Aussage:** Phasenabhängige Gleichrichtung periodischer Anregungen ist als Ratchet- bzw. Symmetriebrechungsproblem etabliert. Popov/Li behandeln einen tribologischen Spezialfall; Flach et al. und Denisov et al. liefern den breiteren Symmetrierahmen.

**Überschneidung:** Phase, zeitliche Symmetriebrechung, nichtlineare/dissipative Kopplung und gerichtete Antwort sind nicht als allgemeines Prinzip PCMMS-neu.

**Abgrenzung:**

- **Linie A:** Charakterisierung der Wellenform einer unilateralen Kontaktkraft in einem intern angeregten Mehrmassensystem; kein Effektanspruch; `mean(F_N) = M g` als Erhaltungs-Nullgröße.
- **Linie B:** Ratchet-/Gleichrichtungsmechanismus mit Medium als äußerem Reaktionspartner; Vakuum ist die Nullgrenze.

**Änderungsvorschlag:** Den bisherigen gemischten Positionierungssatz durch genau diese zwei Sätze ersetzen.

### 2.2 §6 — Kontaktkraft-Wellenform bleibt eigenständige Observable

**v3.5-Passage:** Schiefe, Liftoff-Anteil und Asymmetrieverhältnis `A = (F_max − Mg)/(Mg − F_min)` der Kontaktkraft werden als Charakterisierungsgrößen geführt (Hinweis: die Codevariable `peak_ratio` berechnet A, nicht `max(F)/mean(F)`; die Bezeichnung „Peak-to-Mean“ wird in dieser Datei nicht verwendet); die quantitative Vorhersage einer freien Drift daraus wird ausdrücklich verneint.

**Externe Aussage:** Die Ratchet-Literatur behandelt gerichteten Strom bzw. Transport und dessen Symmetrien. Madatov/Li/Popov behandeln die gemittelte Reibungs-Kraft-Geschwindigkeits-Kennlinie. Beides ersetzt keine Wellenformstatistik der unilateralen Normalkraft eines freien, intern angeregten Körpers.

**Abgrenzung:** Die PCMMS-Eigenständigkeit liegt nicht in „Phase erzeugt Richtung“, sondern in der Kombination aus interner Mehrmassentopologie, Profil- und Phasensteuerung, Liftoff-Regime, Wellenformstatistik und Erhaltungs-Nullkontrolle.

**Änderungsvorschlag:** Als Forschungsgegenstand von Linie A festschreiben; nicht als Vorstufe eines behaupteten Schubs formulieren.

### 2.3 §9 — Ratchet-Symmetrien und Reichweite des 80/20-Nullbefunds

**v3.5-Passage:** „Quadratischer Widerstand + zweistufige (rein zeitlich asymmetrische) Kraft → Drift ebenfalls null […] Bloße Timing-Asymmetrie genügt nicht.“

**Externe Aussage:** Für periodische Antriebe existieren stromumkehrende Zeit-/Raumsymmetrien. Ist insbesondere die Halbperioden-Antisymmetrie `F(t+T/2) = -F(t)` erhalten, ist bei einem ungeraden Widerstandsgesetz der gerichtete Mittelwert symmetriegeschützt null. Eine Wellenform aus ausschließlich ungeraden Harmonischen erfüllt diese Verschiebungsantisymmetrie. Biharmonische Anregung kann sie brechen; Dissipation bricht zusätzlich die relevante Zeitumkehrsymmetrie.

**PCMMS-Einordnung:**

- M1 (`omega + 2 omega`, Phase `phi`, symmetrische Hülle) ist in dieser Sprache ein deterministischer Ratchet mit **zeitlicher Symmetriebrechung**.
- M2 verwendet zusätzlich/alternativ **räumliche Asymmetrie** der Hülle.
- Die 50/50-Kontrolle ist als exakter, widerstandsgesetz-unabhängiger Nullfall zu begründen, sofern Antrieb und Modell tatsächlich `F(t+T/2) = -F(t)` und eine ungerade Mediumreaktion besitzen und der Attraktor eindeutig ist. Bei spontaner Symmetriebrechung (zwei koexistierende Attraktoren mit entgegengesetztem Drift) ist nur das Ensemblemittel null, nicht die Einzelrealisierung; Flach et al. formulieren die Aussage ausdrücklich für ein Ensemble von Trajektorien.
- Der numerische 80/20-Nullbefund des reduzierten v2-Skripts ist **kein allgemeiner Symmetriesatz**. Das Skript bildet die Geschwindigkeit aus der inneren Kraft, ohne die Drag-Rückwirkung voll in dieselbe Dynamik zurückzukoppeln.

**Offene Hypothese, kein Befund:** Im voll integrierten dissipativen Modell ist 80/20 nicht erkennbar symmetriegeschützt. Eine Drift höherer Ordnung in der Kopplungs-/Widerstandsstärke ist möglich; in Luft wird sie voraussichtlich praktisch null sein, bei den dokumentierten Wasserfällen ist sie numerisch zu prüfen.

**Änderungsvorschlag:** „Bloße Timing-Asymmetrie genügt nicht“ ersetzen durch: „Im reduzierten, nicht rückgekoppelten Skript ergibt das geprüfte 80/20-Profil numerisch null; diese Aussage ist nicht auf das voll integrierte dissipative Modell verallgemeinert.“

### 2.4 §9/§9.2 — korrigierte Kraftgröße und Effektzahl

**v3.5-Passage:** `F_drag,drift` wird als effektiver Schub verwendet; daraus folgen rund 34,5 nm Pendelauslenkung und die Bandangabe `10^-7 bis 10^-4 N`.

**Interner verifizierter Stand:**

- `F_drag,drift = 3,39·10^-7 N`
- relevante mittlere Kraft in Konfiguration D: `Fbar_A = 6,67·10^-6 N`
- Verhältnis: `19,7`
- Pendelauslenkung im Beispiel: rund `680 nm` statt `34,5 nm`

Diese Änderung ist in `PCMMS_Skriptkorrekturen_LinieB_2026-09-06.md` bereits als „aufgelistet, nicht eingearbeitet“ dokumentiert.

**Änderungsvorschlag:** In v3.6 einarbeiten; `F_drag,drift` nur als stationäre Drift-Widerstandskraft kennzeichnen und nicht mit der mittleren Pendelkraft gleichsetzen. Die Gültigkeit des quasistationären Widerstandsmodells bleibt offen.

### 2.5 §12 — Feng als Testfall statt bloßes Literaturzitat

**Externe Aussage:** Feng bildet den potenzgedämpften Kontaktoszillator mit `delta = A x^(2/(p+1))` im Phasenraum exakt auf ein lineares Feder-Dämpfer-System ab. Restitution, maximale Eindringtiefe und Energieaufteilung folgen analytisch; außerdem wird eine geschlossene Abschätzung für den kritischen Zeitschritt expliziter Integration angegeben.

**Nutzen für PCMMS:** Die Lösung ist ein analytischer Benchmark für eine einzelne Kontaktereignis-Routine, nicht Evidenz für PCMMS-Wellenformen oder Drift.

**Codebefund zu `pcmms_v3a_phasen_sweep.py`:**

```python
F = -K * z - C_DAMP * zd
if z >= 0.0 or F <= 0.0:
    return 0.0
```

Der Code trennt daher bei **geometrischer Öffnung oder nichtpositiver ungekappter Normalkraft**. Er lässt keine negative Kontaktkraft als Rückgabewert zu. Kontaktmodell: lineare Feder (`K`) plus linearer Dämpfer (`C_DAMP = 16 N·s/m`, ζ ≈ 0,1), also Fengs Potenzgesetz-Familie mit `p = 1`; Testebene T0 in Abschnitt 4 kann damit unmittelbar gegen die geschlossene Lösung für p = 1 laufen. Der mögliche Zugkraft-Artefaktpfad ist somit gekappt; offen bleibt, ob das frühe Trennen bei `F <= 0` gegenüber einem rein geometrischen Ende bei `delta = 0` Impuls, Restitution, Liftoff-Anteil oder das endliche Fensterresiduum relevant verändert.

**Änderungsvorschlag:** Den Robustheitstest aus Abschnitt 4 als Pflichtbestandteil von §12 aufnehmen.

### 2.6 §17 — Popov ist Architektur- und Regime-Kontrast

**Externe Aussage:** Madatov/Li/Popov modellieren quasistatisch und masselos bei kontinuierlichem Kontakt (`Delta u_z <= u_z,0`). Die Autoren grenzen Trägheit, Systemdämpfung, Frequenzverhältnisse, Resonanzen, Stöße und Kontaktverlust aus und verweisen dafür auf ihre Refs. 16–18.

**Refs. 16–18 identifiziert** (Reihenfolge in der Referenzliste des Lubricants-Papers am 12.09.2026 bestätigt: [15] Madatov/Li/Popov, AIP Conf. Proc. 3177 (2025); [16] Mao et al. 2017; [17] Teidelt et al. 2012; [18] Papangelo & Ciavarella 2015; [19] Benad et al. 2018)**:**

16. Mao et al. (2017): Systemmasse, Systemsteifigkeit, Frequenzverhältnisse und Resonanzfall; qualitative experimentelle Stützung.
17. Teidelt et al. (2012): dynamischer Stick-Slip-Kontakt in Mikroantrieben.
18. Papangelo & Ciavarella (2015): Grenzen quasistatischer Analyse für einen Coulomb-Reibungsoszillator unter harmonischer Last.

**PCMMS-Regime:** Linie A liegt nach eigenem Befund im dynamischen Nachbarbereich (`3f/f_n ≈ 1,5`), einschließlich dynamischer Liftoff-Schwelle `R_c ≈ 1,45` und dem kontrollierten Befund `gamma_1 = 0` ohne Liftoff bei Sinusprofilen. Deshalb sind Refs. 16–18 für die unmittelbare Regime-Abgrenzung wichtiger als das quasistatische Lubricants-Paper allein.

**Änderungsvorschlag:** Forschungsstand und §17 müssen Architektur **und** Regime getrennt vergleichen.

### 2.7 Zigelman et al. 2026 — M2-Kontrastfall ohne Liftoff

**Externe Aussage:** Kapsel mit innerem Pendel auf vertikal vibrierender Unterlage. Die Kapsel ist nach oben und unten geführt und kann sich nicht von der Unterlage lösen. Die Energie kommt von außen (Basisanregung); das innere Pendel ist passiv und wird parametrisch (2:1, oszillatorisch) oder resonant rotatorisch (1:1) angeregt. Die Gleichrichtung erfolgt über stückweise lineare, richtungsabhängige viskose Dämpfung der Kapsel (Vorwärtskoeffizient kleiner als rückwärts); die Autoren nennen fehlende experimentelle Validierung als Hauptlimitation.

**PCMMS-Einordnung:** In der Sprache von §2.3 ein M2-Fall (richtungsabhängige Mediumreaktion, räumliche Asymmetrie), nicht M1; kein Liftoff und keine unilaterale Kontaktkraft als Observable; Energiequelle extern statt intern.

**Abgrenzung:** Brauchbar als Kontrast in zwei Richtungen – gegen M1 (symmetrische Hülle, Rektifikation allein durch zeitliche Symmetriebrechung des intern erzeugten Antriebs) und gegen Linie A (Liftoff als Observable). Nicht als Vorläufer des PCMMS-Mechanismus zitieren.

**Änderungsvorschlag:** In §6.4 einen Satz ergänzen (erledigt in v2); in v3.6 §9 als Literaturbeispiel für M2 nennen.

## 3. Streich- und Ersatzliste v3.5 → v3.6

| v3.5 | Maßnahme für v3.6 |
|---|---|
| Gemischter Positionierungssatz A/B mit „expliziter Mediumkopplung“ | Streichen; durch getrennte Zwei-Satz-Positionierung aus §2.1 ersetzen. |
| Neuheitsnähe „Phase/Wellenformasymmetrie erzeugt gerichtete Antwort“ | Auf Ratchet-/Symmetrieliteratur zurückstufen; PCMMS-spezifische Architektur und Observable nennen. |
| „Bloße Timing-Asymmetrie genügt nicht“ als allgemeine Aussage | Streichen; auf den konkreten reduzierten 80/20-Skriptbefund begrenzen. |
| 50/50 nur als numerische Kontrolle | Durch exakte Halbperioden-Antisymmetrie begründen; Gültigkeitsannahmen nennen. |
| `F_drag,drift` als effektiver Pendelschub | Korrigieren zu `Fbar_A = 6,67·10^-6 N`; Größen nicht gleichsetzen. |
| rund 34,5/34,7 nm | Ersetzen durch rund 680 nm für das dokumentierte Beispiel. |
| pauschale Effektspanne `10^-7 bis 10^-4 N` | Neu ableiten oder als modellabhängige Vorabschätzung kennzeichnen. |
| Popov nur als Architektur-Nachbar | Um Regimevergleich und Refs. 16–18 ergänzen. |
| Feng nur als Zitat | Als analytischen Unit-Test und Zeitschritt-Benchmark operationalisieren. |

## 4. Kontaktmodell-Robustheitstest — Spezifikation

### 4.1 Ziel

Prüfen, ob Schiefe, Liftoff, Asymmetrieverhältnis A und Mittelwertresiduum physikalisch/numerisch robust sind oder wesentlich von Kontaktgesetz, Ablösebedingung und Zeitschritt abhängen.

### 4.2 Testebenen

**T0 — analytischer Einzelkontakt (Feng-Benchmark)**

- Initialwertproblem ohne Egg-Anregung und ohne Mehrmassenkopplung.
- Mindestens `p = 1` und `p = 3/2`.
- Sollwerte: Restitutionskoeffizient `e`, `delta_max`, Kontaktimpuls und Kontaktzeit nach analytischer/parametrischer Lösung.
- Zeitschritt unter Fengs Schranke wählen und anschließend halbieren.

**T1 — Ablösebedingung**

- Variante A: Kontaktende geometrisch bei `delta = 0`.
- Variante B: gekappte Kraft mit Ablösung bei `F_N <= 0` (aktueller v3a-Ansatz).
- Variante C: dokumentierte alternative dissipative Kontaktform ohne Zugkraft.
- Vergleichen: Impuls, `e`, Kontaktzeit, Minimum der ungekappte Kraft, Liftoff-Zeit.

**T2 — PCMMS-Phasenpunkte**

- Referenzpunkte: kein Liftoff, nahe dynamischer Schwelle, hoher Liftoff-Anteil, Extrempunkte der Phasenkarte.
- Variationen: `Delta t`, `k_c`, `c_c`, Kontaktgesetzfamilie und Ablösebedingung.
- Bei Dämpfungsvergleichen nach Möglichkeit auf gleichen Restitutionskoeffizienten kalibrieren.

**T3 — Erhaltungs- und Fensterprüfung**

- Relatives Mittelwertresiduum `r_F = |mean(F_N)-Mg|/(Mg)` nach Burn-in und über ganzzahlige Periodenzahlen. (`epsilon_phys` und `epsilon_ctrl` bleiben die Schwellen des Projekts – 3·σ̂_ref je Funktional bzw. Schwelle der Kontrollgröße – und werden hier nicht umdefiniert.)
- Zusätzlich Randterm aus Impulsänderung des Gesamtschwerpunkts ausweisen.
- Konvergenz über verlängerte Fenster und halbierte Zeitschritte prüfen.

### 4.3 Pass/Fail

Vor Messdaten wird kein erfundener universeller Zahlenwert eingesetzt. Für jeden Lauf ist eine **vorab deklarierte** numerische Toleranz `epsilon_tol` aus Integratorordnung, Zeitschritt-Konvergenz und analytischem T0-Fehler festzulegen.

**Pass:**

1. T0: Fehler in `e`, `delta_max` und Kontaktimpuls jeweils `<= epsilon_tol`.
2. T1/T2: Vorzeichen und qualitative Klassifikation der Hauptobservable bleiben unter zulässigen Modellvarianten stabil; quantitative Modellstreuung wird ausgewiesen.
3. T3: `r_F <= epsilon_tol` (und `r_F` innerhalb `epsilon_ctrl`) oder vollständig durch den explizit berechneten endlichen Randterm erklärt.
4. Kein negativer ausgegebener Kontaktkraftwert.

**Fail:**

- fehlende Zeitschritt-Konvergenz;
- systematisches Mittelwertresiduum oberhalb `epsilon_tol`, das nicht durch Randterm erklärbar ist;
- qualitative Ergebnisumkehr allein durch eine plausible Ablösebedingung;
- analytischer Einzelkontakt-Benchmark verfehlt.

Bei Fail wird der betreffende PCMMS-Befund als kontaktmodell-/numerikabhängig markiert und nicht als physikalischer Effekt interpretiert.

## 5. Offene numerische Fragen

1. **80/20, voll integriert:** Erzeugt das Profil mit rückgekoppelter Dissipation eine Drift höherer Ordnung? Getrennt für Luft und die dokumentierten Wasserparameter rechnen.
2. **Symmetrietest:** Für jedes Antriebsprofil numerisch `max_t |F(t+T/2)+F(t)|` ausweisen; nur bei Null innerhalb Toleranz als verschiebungsantisymmetrisch klassifizieren. Zusätzlich je Profil zwei Läufe mit vorzeichengespiegelten Startbedingungen rechnen; nur bei gleichem Drift-Endwert ist der Attraktor eindeutig (§2.3).
3. **Popov-Refs. 16–18:** Volltexte systematisch gegen PCMMS-Regimeparameter, Resonanz, Kontaktverlust und Ablösemodell auswerten.
4. **Kontaktende:** Impuls- und Restitutionsvergleich `delta=0` versus `F_N=0` durchführen; aktueller v3a-Code verwendet beide Kriterien disjunktiv.

## 6. Direkt verwendbare Forschungsstand-Absätze für das Arbeitspapier

### 6.1 Phasengesteuerte Gleichrichtung und Symmetrie

Die Erzeugung gerichteter Antworten durch phasenverschobene periodische Anregungen ist als Ratchet- und Symmetriebrechungsproblem etabliert. Flach, Yevtushenko und Zolotaryuk zeigten für zeitperiodisch getriebene Systeme, dass gerichteter Strom möglich wird, wenn die stromumkehrenden Raum-Zeit-Symmetrien des Antriebs gebrochen sind; Denisov, Flach und Hänggi ordneten diese Resultate in einen allgemeinen Transport- und Symmetrierahmen ein. Für tribologische Kontakte demonstrierten M. Popov und Li sowie später Madatov, Li und V. L. Popov, dass phasenverschobene Normal- und Tangentialschwingungen eine asymmetrische gemittelte Reibungskennlinie, dynamisches Ratcheting und Aktuatorregime erzeugen können. PCMMS beansprucht daher nicht die allgemeine Neuheit phasenbasierter Gleichrichtung. Der eigenständige Untersuchungsgegenstand liegt in intern angeregten Mehrmassensystemen, der getrennten Steuerung von Profil und Phase, der Wellenformstatistik unilateraler Kontaktkräfte und — in Linie B — einer expliziten Mediumkopplung als äußerem Reaktionspartner.

### 6.2 Regime-Abgrenzung der Kontaktmechanik

Das quasistatische Modell von Madatov, Li und Popov vernachlässigt die Indenterträgheit und setzt kontinuierlichen Kontakt voraus. Damit dient es als mechanistischer Kontrast, deckt jedoch das für PCMMS Linie A relevante dynamische Regime nicht ab. Die von den Autoren selbst genannten dynamischen Nachbararbeiten berücksichtigen Systemmasse und -steifigkeit, Frequenzverhältnisse, Resonanzen oder dynamischen Stick-Slip-Kontakt und diskutieren die Grenzen quasistatischer Näherungen. Diese Nachbarschaft ist für PCMMS wesentlich, weil die eigenen Simulationen mit `3f/f_n ≈ 1,5`, einer dynamischen Liftoff-Schwelle von ungefähr `R_c ≈ 1,45` und explizitem Kontaktverlust gerade außerhalb der quasistatischen Dauer-Kontakt-Annahme liegen. Architekturähnlichkeit und Regimeähnlichkeit sind deshalb getrennt zu bewerten.

### 6.3 Kontaktmodell und numerische Absicherung

Für die Interpretation der Kontaktkraft-Wellenform ist nicht nur die Zeitschrittweite, sondern auch die konkrete dissipative Kontakt- und Ablöseformulierung relevant. Fengs exakte Phasenraumlösung des potenzgedämpften Kontaktoszillators liefert hierfür einen analytischen Benchmark: Restitution, maximale Eindringtiefe, Energieaufteilung und eine Zeitschrittabschätzung können unabhängig von der PCMMS-Hypothese geprüft werden. In PCMMS wird Feng daher nicht als inhaltlicher Vorgänger des Mehrmassensystems zitiert, sondern als Unit-Test für die Kontaktroutine. Die Hauptobservablen werden zusätzlich über Zeitschritt-, Steifigkeits-, Dämpfungs-, Kontaktgesetz- und Ablösevariationen geprüft; ein Mittelwertresiduum gilt nur dann als physikalisch interpretierbar, wenn es konvergiert und weder aus einem endlichen Impulsrandterm noch aus der Kontaktmodellierung folgt.

### 6.4 Trennung der Forschungslinien

Linie A charakterisiert die zeitliche Wellenform der unilateralen Kontaktkraft ohne Anspruch auf eine Änderung ihres stationären Mittelwerts; `mean(F_N)=Mg` dient als Erhaltungs- und Pipelinekontrolle. Linie B untersucht demgegenüber einen Ratchet-Mechanismus, bei dem gerichteter Impuls ausschließlich über die Kopplung an ein äußeres Medium übertragen wird. Das Medium ist der Reaktionspartner, und die Vakuumgrenze bildet den Nullfall. Der Kontrast zu extern angeregten, geführten Kapseln mit richtungsabhängiger Dämpfung (Zigelman et al. 2026) macht die Trennung sichtbar: Dort tragen räumliche Asymmetrie der Mediumreaktion und externe Energiezufuhr die Fortbewegung, während der eigentliche Linie-B-Fall (M1) ausschließlich die zeitliche Struktur der intern erzeugten Kraft bei symmetrischer Mediumreaktion prüft. Diese Trennung vermeidet, dass Wellenformgestaltung, Kontaktkraftdiagnostik und mediumgestützte Drift als ein einziger Wirkungsanspruch erscheinen.

## 7. Quellenlinks zur Arbeitsprüfung

- Popov & Li 2018: https://doi.org/10.1134/S1029959918010046 ; https://arxiv.org/abs/1705.03379
- Madatov/Li/Popov 2026: https://doi.org/10.3390/lubricants14080286
- Feng, Phase-Space: https://arxiv.org/abs/2603.27764
- Feng, Stability Bounds: https://arxiv.org/abs/2604.02533
- Feng, Energy--Phase: https://doi.org/10.1007/s00466-026-02853-z
- Flach/Yevtushenko/Zolotaryuk: https://doi.org/10.1103/PhysRevLett.84.2358
- Denisov/Flach/Hänggi: https://doi.org/10.1016/j.physrep.2014.01.003
- Mao et al.: https://doi.org/10.1007/s40544-017-0146-x
- Papangelo/Ciavarella: https://doi.org/10.1016/j.jsv.2014.11.028
- Teidelt et al.: https://doi.org/10.1134/S1029959912030071
- Passive vibration-driven locomotion: https://doi.org/10.1007/s11071-026-12592-8
- Vibro-impact capsule: https://doi.org/10.1007/s11071-025-12175-z

## 8. Änderungslog v1 → v2 (12.09.2026)

1. BibTeX `MadatovLiPopov2026`: Vorname des Erstautors korrigiert (Islam → Ibrohim; Quelle: Autorenangaben MDPI, Affiliation Samarkand/TU Berlin).
2. BibTeX `PopovLi2018`: Titel auf die Journalfassung „Multimode …“ gesetzt; arXiv-Titel und Originalfassung (Fiz. Mezomekh. 20(5), 26–32, 2017) als `note`.
3. BibTeX `PapangeloCiavarella2015`: DOI entfernt, Konflikt (…2014.10.034 vs. …2014.11.028) als `note` dokumentiert; §7 entsprechend. Einziger offener Punkt der Referenzliste (in v3 geklärt, siehe unten).
4. BibTeX ergänzt: `TeideltEtAl2012` Heft 5–6 und DOI 10.1134/S1029959912030071; `MaoEtAl2017` Heft 2; `DenisovFlachHanggi2014` Heft 3; `ZigelmanEtAl2026` Heft 10, Artikelnummer 756; `WangEtAl2026Capsule` 114(4), Artikelnummer 294.
5. Neu 1.2: `MadatovLiPopov2025AIP` (Kurzvorläufer, aus der Referenzliste des Lubricants-Papers übernommen; DOI offen). Prüfstand-Vermerk unter 1.1 ergänzt.
6. §0.4: Chat-Label „Dokument 131“ durch neutrale Bezeichnung der Vorarbeit ersetzt.
7. §2.2 und §4.1: „Peak-to-Mean“/„Peakverhältnis“ → Asymmetrieverhältnis `A = (F_max − Mg)/(Mg − F_min)`; Hinweis, dass `peak_ratio` im Code A berechnet.
8. §2.3 und §5.2: Bedingung „Attraktor eindeutig“ (Ensemble-Aussage bei Flach et al.) ergänzt; Symmetrietest um Läufe mit gespiegelten Startbedingungen erweitert.
9. §2.5: Kontaktmodell des v3a-Codes als Feng-Fall `p = 1` benannt (K, C_DAMP = 16 N·s/m, ζ ≈ 0,1).
10. §2.6: Reihenfolge der Refs. 15–19 in der Lubricants-Referenzliste bestätigt und vermerkt.
11. Neu §2.7: Einordnung von Zigelman et al. 2026 als M2-Kontrastfall ohne Liftoff mit externer Energiezufuhr; §6.4 um einen Satz ergänzt.
12. §4.2/§4.3: `epsilon_phys` als Residuum gestrichen → `r_F`; ε_phys und ε_ctrl bleiben Projektschwellen.
13. Kopf: Versionsvermerk v2.

Unverändert: alle Zahlen in §2.4, Codezitat in §2.5, Streich-/Ersatzliste §3, Testebenen T0–T2, §6.1–6.3.

### v2 → v3 (12.09.2026)

14. BibTeX `PapangeloCiavarella2015`: Konfliktnotiz durch `doi = {10.1016/j.jsv.2014.11.028}` ersetzt (ScienceDirect-Verlagstreffer; deckungsgleich mit der Crossref-Referenz in Chaos 35, 053126, 2025). Prüfstand-Vermerk und §7 angepasst. Sonst keine Änderung.

---

**Redaktionelle Leitlinie:** In v3.6 knapp auf diesen Abgleich verweisen; im Forschungsstand die Absätze aus §6 übernehmen und mit den unveränderten BibTeX-Schlüsseln zitieren. Hypothesen wie die mögliche 80/20-Drift im integrierten Modell ausdrücklich als zu prüfende Erwartung kennzeichnen.
