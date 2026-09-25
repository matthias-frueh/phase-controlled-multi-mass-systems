# PCMMS — Zehn Fragen, zehn Antworten

*Kurzfassung zur Gesprächsvorbereitung. Ausführlich in `einordnung.md`.*

**Zahlen, die man parat haben sollte**
M·g = 6,3765 N · 361 Konfigurationen im Grobraster, 441 im 2°-Feinraster · Streuung des Zeitmittels
0,07 % · Liftoff 0 – 76,2 % · Schiefe −0,29 … +1,98 · Spitzenkraft bis 50,6 N ·
F_min-Maximum 5,330 N exakt bei (120°, 240°), Steigung 0,21 N/° (Resonanzwert von K = 10⁴ N/m; bei festem ζ
und K = 3·10⁴ … 10⁷ N/m 0,09–0,12 N/°) · alles Simulation

---

**1 · Gibt es das nicht schon?**

Die Bausteine ja, die Kombination nein. Interne Massen, Mehrmodulsysteme, Phasendifferenz als
Stellgröße, Liftoff, 2D-Parameterkarten — alles besetzt. Aber: Wer die Kontaktkraft als Zielgröße
nimmt (Perret-Liaudet & Rigaud, Umbanhowar & van Hecke), hat keine Mehrmassen-Phasensteuerung. Wer
Mehrmassen-Phasensteuerung betreibt (z. B. die Gruppe um Fang und Xu, Fudan), optimiert Geschwindigkeit.
PCMMS sitzt im Schnitt.

**2 · Was ist konkret der Beitrag?**

> Die zeitaufgelöste Kontaktkraft als primäre Zielgröße eines stationären, phasengesteuerten
> Mehrmassensystems, kartiert über den Raum relativer Phasenkonfigurationen.

Abgrenzend ist nicht die Observable, sondern der Anregungsraum. Status: Suchbefund, kein
Neuheitsbeweis — widerlegbar durch einen einzigen Literaturhinweis.

**3 · Ist es ein verkapptes Perpetuum mobile?**

Nein — und das ist konstruktiv abgesichert. Linie A behauptet ausdrücklich, dass das Zeitmittel
*nicht* verschiebbar ist, und nutzt diese Unmöglichkeit als Kontrollgröße: Jede beobachtete
Mittelwertabweichung gilt per Protokoll als Apparaturfehler. Nach dem
[Entwurf](praeregistrierung_v2_entwurf.md) der Präregistrierung v2 macht eine Abweichung über der
Kontrollschwelle ε_ctrl den Lauf ungültig; angehalten wird die Messung erst bei einem reproduzierbaren
Verstoß (S1, dort §9.2). Linie B behauptet Nettobewegung, benennt aber den Reaktionspartner (Luft) und
sagt vorher, dass der Effekt im Vakuum exakt verschwindet. Eine frühere Fassung behauptete tatsächlich eine
Mittelwertverschiebung — sie wurde zurückgezogen, dokumentiert und archiviert.

**4 · Warum schwankt die Kraft bei festem Mittel?**

Weil der Mittelwert das Integral betrifft, nicht den Verlauf. Beim Liftoff ist die Kraft phasenweise
exakt null; die fehlende Fläche wird durch Spitzen kompensiert. In der Simulation: 50,6 N Spitze bei
6,38 N Mittel — Faktor acht, bei 0,07 % Streuung des Mittels. Perret-Liaudet & Rigaud zeigen
experimentell dasselbe bei bis zu 15 % Kontaktverlust.

**5 · Rechnet ihr nicht nur vorwärts, was ihr selbst vorgegeben habt?**

Der härteste Einwand. Antwort: Die Messung prüft nicht die Simulation, sondern das **Kontaktmodell**.
Gerechnet wird mit linear-elastischem Kontakt plus viskoser Dämpfung, unilateral abgeschnitten —
ohne Hertz'sche Nichtlinearität, Rauheit, Stoßverluste. Die Frage lautet nicht „bestätigt das
Experiment die Simulation", sondern **„überlebt die vorhergesagte Phasenabhängigkeit den Übergang
zum realen Kontakt?"** Dieses Projekt hat an genau der Stelle schon einmal ein Artefakt produziert.

**6 · Warum keine Messdaten?**

Weil das Projekt prä-experimentell ist und das so benannt wird. Präregistrierung, Artefaktkatalog,
Entscheidungsregeln und Abbruchkriterien stehen *vor* der ersten Messung. In der experimentellen
Mechanik ist das unüblich — und es ist der Teil, der auch bei einem Null-Ergebnis Bestand hat.

**7 · Was, wenn nichts herauskommt?**

Dann ist das ein Ergebnis. Die Falsifikationsbedingung steht vorab fest: Ist die Regime-Struktur nach
allen Kontrollen nicht über dem Rauschboden nachweisbar, gilt H1 der Präregistrierung vom Juni 2026 für
den getesteten Bereich als falsifiziert. Nach dem [Entwurf](praeregistrierung_v2_entwurf.md) der
Präregistrierung v2, der die Bezeichnung H1 neu belegt, ist dieser Ausgang „nicht entscheidbar" (die
Präzision reicht nicht, dort §9.4) und wird wie jeder Ausgang veröffentlicht. Eingeplant, nicht abgefedert.

**8 · Warum kein Roboter?**

Weil Fortbewegung die Frage unbeantwortbar macht. Sobald sich das System bewegt, mischen sich
Reibungsmodell, Untergrund und Kontaktgeometrie ins Signal; die Wellenform ist nicht mehr isolierbar.
Der stationäre Aufbau ist eine Vereinfachung mit Absicht. Robotik ist mögliche nachgelagerte
Validierung, keine Voraussetzung.

**9 · Was ist die praktische Relevanz?**

Liftoff-Anteil und Spitzenkraft sind bei Vibrationsförderern, Siebmaschinen und Bodenverdichtung
unmittelbar Durchsatz- und Verschleißgrößen. Lassen sie sich über die Phasenlage einstellen, ohne
den mittleren Lastfall zu ändern, ist das ein Stellhebel. Ob er trägt, ist offen — das Projekt
behauptet es nicht.

**10 · Warum ohne Institut ernst nehmen?**

Die Physik ist unstrittig; Code und Simulationsdaten liegen in diesem Repository. Was fehlt, ist die Messung,
und das steht in jedem Dokument. Angeboten wird keine Entdeckung, sondern eine vorbereitete,
falsifizierbare Messfrage samt Auswerteplan — und die Bereitschaft, ein Null-Ergebnis zu
veröffentlichen.

---

**Nicht behauptet:** kein reaktionsloser Antrieb · keine Gravitationsmodifikation · keine
Gewichtsreduktion · keine Verschiebung des Zeitmittels · keine neue Physik.

**Offen zugegeben:** keine Messdaten · Schiefe bei hohem Liftoff schlecht konditioniert · dynamische
Kalibrierung bei intermittierendem Kontakt ungelöst · Parameterdiskrepanz 10 Hz (Code) gegen 2,2 Hz
(Dokumentation) ungeklärt · Linie B liegt näher an der Nachbarliteratur als Linie A.
