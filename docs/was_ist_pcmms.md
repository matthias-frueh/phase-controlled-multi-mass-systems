# Was ist PCMMS?

**Phase-Controlled Multi-Mass Systems · Phasenkontrollierte Mehrmassensysteme**
Matthias Früh · ORCID 0009-0005-9984-4207 · Stand September 2026

*Für Leser ohne Vorwissen. Ersetzt die frühere Erklärfassung desselben Monats.*

---

## 1 · Die Grundidee

In einem geschlossenen mechanischen Körper bewegen sich mehrere Massen auf fest vorgegebenen
Bahnen. Alle im selben Takt — aber sie starten nicht gleichzeitig. Der zeitliche Versatz zwischen
ihnen, die **Phasenlage**, ist frei einstellbar.

Damit lässt sich eine Frage experimentell stellen:

> Wie verändert sich die Kraft, mit der der Körper auf seine Unterlage drückt, wenn ausschließlich
> die zeitliche Abstimmung seiner inneren Bewegungen verändert wird?

PCMMS sucht keine unbekannte Kraft. Es untersucht, wie sich bekannte mechanische Bewegungen zu
einer gemeinsamen Dynamik überlagern.

Die Richtung ist dabei wesentlich. Es wird nicht aus einer gemessenen Kraft rückwärts auf eine
Ursache geschlossen. Es gilt:

```
Phasenlage vorgeben  →  Bewegung erzeugen  →  Kraft messen
```

Das macht die Fragestellung überprüfbar statt interpretierbar.

---

## 2 · Die Kniebeuge

Stell dich auf eine Personenwaage und geh langsam in die Knie. Die Anzeige fällt zuerst, steigt
dann über dein Gewicht und pendelt sich wieder ein. Du warst in keinem Moment leichter oder
schwerer. Gesteuert hast du den zeitlichen **Verlauf** der Anzeige.

Daraus folgen zwei Dinge:

- **Der Mittelwert ist nicht verhandelbar.** Über die ganze Bewegung kommt exakt dein Gewicht
  heraus. Das ist ein Erhaltungssatz, kein Erfahrungswert.
- **Der Verlauf ist sehr wohl verhandelbar.** Schneller, tiefer, ruckartiger.

PCMMS ersetzt die Kniebeuge durch drei Massen mit einstellbarem Phasenversatz und fragt, wie weit
die Kontrolle über den Verlauf reicht — und ob sie sich an echter Hardware von Messfehlern
trennen lässt.

---

## 3 · Was gemessen wird

Der Körper steht auf einer Kontaktfläche. Dort wird die auftretende Kraft zeitlich aufgezeichnet.

Das ist heikler, als es klingt. **Eine Kraftmessung ist keine Ablesung.** Ein Sensor reagiert
mechanisch auf die Belastung — im Regelfall verformt sich ein Federkörper um wenige Mikrometer —
und erst ein bekanntes, kalibriertes Übertragungsmodell macht daraus eine belastbare Kraftangabe.
Belastbar ist deshalb nie der Absolutwert für sich, sondern die Verschiebung gegen eine Referenz.

Genau deshalb ist eine Größe wertvoll, deren Wert die Physik bereits festlegt. Bei PCMMS ist das
der Zeitmittelwert der Kontaktkraft: Bei periodischer, in sich beschränkter Innenbewegung
entspricht er im eingeschwungenen Zustand der Gewichtskraft des Körpers.

Dieser Wert ist **keine Entdeckung, sondern die Nulllinie**, an der die gesamte Messkette geprüft
wird. Weicht das gemessene Zeitmittel dauerhaft ab, ist die Messkette defekt — nicht die Physik.
Das ist per Protokoll ein Abbruchgrund, keine Interpretation.

Die eigentliche Frage lautet also nicht „wie groß ist die Kraft", sondern: **verändert sich die
Form der Kraftkurve?**

---

## 4 · Warum die Form nicht trivial ist

Die Auflage kann drücken, aber nicht ziehen. Hebt der Körper kurz ab, ist die Kraft nicht *wenig*,
sondern **exakt null**. Die Fläche, die dadurch im Verlauf fehlt, muss an anderer Stelle als höhere
Spitze zurückkommen — sonst stimmte der Mittelwert nicht mehr.

Die gesamte steuerbare Information sitzt damit in der Form. Und je näher das System an den
Kontaktverlust kommt, desto stärker verformt sich der Verlauf.

Beschrieben wird die Form über vier Größen:

| Größe | Was sie beschreibt |
|---|---|
| Schiefe | wie unsymmetrisch der Verlauf ist — kurze hohe Spitzen gegen lange flache Täler |
| Liftoff-Anteil | wie viel Prozent der Zeit gar kein Kontakt besteht |
| Asymmetrieverhältnis | Überhöhung nach oben im Verhältnis zur Entlastung nach unten |
| F_min | die kleinste Kraft im Zyklus — der Abstand zum Abheben |

Zusammen: die **Wellenformstatistik**. Sie ist der Untersuchungsgegenstand.

---

## 5 · Die zentrale Prüfform

Am anschaulichsten ist F_min, der Tiefstpunkt der Kraftkurve.

Verstellt man die Phasenlage schrittweise, sagt das Modell für F_min einen charakteristischen
Verlauf voraus: eine **Zeltform** mit ausgeprägter Spitze an der symmetrischen Konfiguration.

```
Phasenlage verändern  →  Minimum steigt und fällt  →  charakteristische Zeltform
```

Diese Form ist vor der Messung aus dem Modell festgelegt, nicht nachträglich ausgewählt.
Entscheidend ist deshalb nicht, ob sich *irgendetwas* ändert, sondern ob **genau diese Struktur**
reproduzierbar auftritt.

- Erscheint sie: das stützt die Modellbeschreibung.
- Erscheint sie nicht: die Vorhersage ist falsifiziert — oder Modell, Aufbau und Messkette müssen
  geprüft werden.

F_min ist die scharfe Prüfform, weil sie ohne Statistik ablesbar ist. Der Gegenstand bleibt die
Wellenformstatistik insgesamt.

---

## 6 · Warum das wissenschaftlich interessant sein könnte

Die Einzelbausteine sind nicht neu. Mehrere bewegte Massen, Phasenverschiebung, Kontaktkräfte und
Kontaktverlust sind seit Langem Gegenstand der klassischen Mechanik. Ein neues physikalisches
Grundgesetz wird ausdrücklich nicht behauptet.

Der mögliche Beitrag liegt in drei Punkten:

**Die Kombination.** Vorgegebene individuelle Bahnprofile, kontrollierte Phasenlage zwischen
mehreren Modulen und die zeitaufgelöste Kontaktkraft als *primäre Zielgröße* — bei absichtlich
stillstehendem Körper. Ausführlich behandelt im Dokument zum Neuheitsgrad.

**Die Attribution.** Weil der Körper sich nicht bewegt, entfällt die Rückkopplung zwischen Kraft,
Reibung und Bewegung. Die Phasenkonfiguration ist die einzige unabhängige Variable. Beobachtete
Änderungen sind ihr direkt zuzuordnen.

**Die Anwendungsnähe.** Intermittierender Kontakt bestimmt Verschleiß, Geräusch und
Positioniergenauigkeit — in Lagerungen, Vibrationsförderern, Werkzeugmaschinen, Prüfständen. Wer
F_min gezielt einstellen kann, kann Kontaktverlust vermeiden, wo er schadet, und herbeiführen, wo
er nützt.

Ob daraus eine reproduzierbare, quantitativ beschreibbare Systematik wird, entscheidet das
Experiment.

---

## 7 · Zwei getrennte Linien

**Linie A — Wellenformstatistik (primär).** Alles bisher Beschriebene. Der Körper steht still.

**Linie B — medium-gekoppelte Fortbewegung (optional, eigener Aufbau).** Der Körper hängt frei.
Untersucht wird, ob die Innenbewegung über den Luftwiderstand eine gerichtete Nettobewegung
erzeugt. Der Reaktionspartner wird ausdrücklich benannt: die umgebende Luft. Vorhergesagt wird,
dass der Effekt mit der Luftdichte skaliert und im Vakuum exakt verschwindet — genau das, was ein
reaktionsloser Antrieb nicht vorhersagen könnte.

Beide Linien sind erhaltungskonform. Keine ist widerlegt. Sie dürfen nicht vermischt werden.

---

## 8 · Und die alten Gleichungen?

Eine frühere Fassung des Projekts prüfte eine andere Hypothese: ob sich der **Mittelwert** der
äußeren Kraft dauerhaft verschieben könne. Diese Interpretation wurde analytisch und numerisch
verworfen — sie war ein Artefakt des damals verwendeten Kontaktmodells.

Die älteren Gleichungen bleiben dokumentiert. Nicht als heutige Aussage, sondern als archivierte
Nulllinie, ausdrücklich als überholt gekennzeichnet. Sie halten fest, welche Grenze das Projekt
selbst erkannt und korrigiert hat.

Die Geschichte wird damit nicht versteckt: Eine Hypothese wurde geprüft, als nicht tragfähig
erkannt und aus der aktuellen Forschungsfrage entfernt.

---

## 9 · Was PCMMS ausdrücklich nicht behauptet

- keine Anti-Gravitation
- kein Perpetuum mobile
- keinen reaktionslosen Antrieb
- keine Gewichtsreduktion
- keine Verletzung von Energie-, Impuls- oder Schwerpunktsatz

Die Kontaktkraft wird als Reaktionskraft eines klassischen mechanischen Systems behandelt. Der
Gegenstand ist nüchterner:

> Kann die zeitliche Abstimmung mehrerer innerer Bewegungen die Form der äußeren Kontaktkraft
> reproduzierbar strukturieren — und lässt sich diese Struktur experimentell mit den Vorhersagen
> des Modells vergleichen?

---

## 10 · Stand

Prä-experimentell. Die Simulationsseite ist abgeschlossen: ein 19×19-Phasensweep und ein Feinsweep
mit 2°-Raster um die symmetrische Konfiguration. **Eigene Messdaten existieren nicht.**

Ein Null-Ergebnis — die Formsteuerung ist an realer Hardware nicht auflösbar — ist vorab als
vollwertiges Resultat definiert, nicht als Scheitern.

---

## Quellen

- ORCID · https://orcid.org/0009-0005-9984-4207
- Zenodo · Veröffentlichungen unter *Früh, Matthias*
- Code · https://github.com/matthias-frueh/phase-controlled-multi-mass-systems
