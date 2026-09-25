# Wellenform statt Mittelwert

### Ein Werkstattbericht zu phasenkontrollierten Mehrmassensystemen

*Matthias Früh · Gravidon Systemics Research · ORCID 0009-0005-9984-4207 · September 2026*

---

Der Aufbau ist schnell beschrieben. Ein geschlossener Körper von 0,650 kg steht auf einer Unterlage. In seinem Inneren bewegen sich drei Massen periodisch auf und ab, jede mit einer eigenen, einstellbaren Phasenlage. Sie berühren einander nicht. Gemessen werden soll die Kraft, mit der der Körper auf die Unterlage drückt.

Vorweg zwei Dinge, die man wissen sollte, bevor man weiterliest. Der Stand ist rein simulativ; es liegen keine Messdaten vor. Und es geht hier nicht um einen reaktionslosen Antrieb, nicht um Gravitationsmodifikation und nicht um neue Physik. Das Vorhaben bewegt sich vollständig innerhalb der klassischen Mechanik. Was daran trotzdem interessant ist, steht weiter unten.

---

## Warum der Mittelwert keine Antwort geben kann

Die naheliegende Frage lautet: Verändert die Innenbewegung die Kraft auf die Unterlage? Die Antwort ist bekannt, bevor man misst. Bei jeder beschränkten periodischen Innenbewegung ist der Zeitmittelwert der Auflagerkraft gleich der Gewichtskraft. Bei 0,650 kg und g = 9,81 m/s² sind das 6,3765 N — unabhängig davon, wie die Massen im Inneren laufen.

Das ist kein Ergebnis, das man erst herausfinden müsste. Es folgt aus dem Schwerpunktsatz. Innendynamik kann Kraftimpulse zeitlich umverteilen, sie kann die Summe nicht ändern.

Für die Versuchsplanung ist das eine gute Nachricht. Man hat damit eine Größe, deren Sollwert exakt bekannt ist. Weicht der gemessene Mittelwert davon ab, hat man ein Problem in der Messkette — Drift, Kalibrierfehler, ein zu kurzes Auswertefenster. Der Mittelwert wird damit vom Erkenntniskanal zum Kontrollkanal. Eine Abweichung ist ein Prüfanlass, kein Befund.

In der Simulation lässt sich das direkt beobachten. Im Feinsweep um die interessante Phasenkonfiguration bleibt der Mittelwert über 441 Konfigurationen hinweg zwischen 6,376330 und 6,376690 N, also innerhalb von ±0,2 mN um den Sollwert. Im Grobsweep über den gesamten Phasenraum dagegen streut er zwischen 6,333041 und 6,383209 N. Die Abweichung von bis zu 43,5 mN tritt ausschließlich dort auf, wo der Körper zyklisch abhebt und die Kraft zwischen null und mehreren Dutzend Newton springt — dort ist ein Einschwingvorgang nach 5 Sekunden nicht immer abgeklungen, und manche Antworten wiederholen sich erst nach zwei oder drei Anregungsperioden, sodass ein 10-Sekunden-Fenster nicht auf ganze Perioden fällt. Der Kontrollkanal funktioniert, aber seine Empfindlichkeit hängt vom Betriebsregime ab. Wer eine Schwelle für ihn festlegt, ohne die Fensterlänge mitzudenken, bekommt Fehlalarme genau an den interessanten Punkten.

---

## Was stattdessen zugänglich ist

Wenn die Fläche unter der Kurve festliegt, bleibt die Form. Und die ist alles andere als starr.

Der Kontakt ist einseitig: die Unterlage kann drücken, nicht ziehen. Sobald die Innendynamik den Körper stärker nach oben beschleunigt, als die Schwerkraft ihn hält, hebt er ab und die Kraft ist exakt null. Diese Nullphasen müssen anderswo im Zyklus durch Kraftspitzen kompensiert werden, sonst stimmt der Mittelwert nicht. Aus einer harmlosen Sinusanregung wird so eine stark verzerrte, unsymmetrische Kraftzeitreihe.

Wie stark, hängt an der Phasenlage. Über 361 Konfigurationen des Grobsweeps — bei 10 Hz, 7,7 mm Hub und einer angesetzten Kontaktsteifigkeit von 10 000 N/m, mit der gesamten Masse in den drei bewegten Modulen (ein ruhendes Gehäuse ist im Modell nicht enthalten) — bewegt sich die Schiefe der Kraftverteilung zwischen −0,2880 und +1,9790. Der Anteil der Zykluszeit ohne Kontakt reicht bis 76,22 %. Die Spitzenkraft erreicht 50,5521 N, also fast das Achtfache der statischen Last. Die Minimalkraft liegt zwischen null und 2,8821 N.

Grob lassen sich drei Regime unterscheiden. Bei synchronen Phasen arbeiten alle drei Massen gleichzeitig, der Körper hüpft, die Schiefe ist hoch. Bei der triphasischen Konfiguration — 120° und 240° Versatz — löschen sich die Beiträge weitgehend aus, der Kontakt reißt nie ab. Dazwischen liegt ein Übergangsbereich mit kontinuierlicher Modulation und negativer Schiefe.

---

## Wie eine eigene Hypothese an einem Modellfehler starb

Eine frühere Fassung des Vorhabens behauptete etwas anderes: dass eine hinreichend asymmetrische Innendynamik den Zeitmittelwert der Kontaktkraft verschieben könne. Vier Ergebnisstände dokumentierten das mit Zahlen — −0,00625 N, dann −0,01564 bis −0,01870 N, dann bis −0,03746 N, schließlich +0,03742 N bei umgekehrter Dämpfung. Die Werte waren klein, aber systematisch und schienen mit den Modellparametern monoton zu skalieren.

Sie waren ein Rechenartefakt. Das damalige Kontaktmodell schrieb die Eindrückung der Unterlage direkt vor, als δ = −m·a/K. Innerhalb dieser Annahme war die Arithmetik stimmig; die Annahme selbst war unzulässig. Die Auflagerkoordinate ist keine vorgeschriebene Größe, sie ist eine Zustandsgröße, die von der Kontaktkraft getrieben wird und integriert werden muss. Die vier Ergebnisstände bildeten die numerischen Folgen dieses Fehlers präzise ab — was sich in der Rückschau als Bestätigung angefühlt hatte, war die Konsistenz zwischen falscher Annahme und der daraus abgeleiteten Rechnung.

Ein zweiter Fehler steckte im Bewegungsprofil selbst. Die Trajektorie der Innenmassen bestand aus einer langsamen Halte- und einer schnellen Rückführphase; an der Naht dazwischen sprang die Geschwindigkeit. Ein Geschwindigkeitssprung bedeutet einen Dirac-Stoß in der Beschleunigung, und der schlug als Bias von −0,808 N durch. Bemerkenswert daran ist, wo der Fehler sitzt: nicht im Zeitschritt, sondern im Modell. Man kann die Integration beliebig verfeinern, der Bias bleibt. Er verschwindet erst, wenn das Profil stetig differenzierbar gemacht wird — hier über die Bedingung R_bot = R_top · T_fast / T_hold.

Beide Korrekturen zusammen haben die ursprüngliche Hypothese erledigt. Die betroffenen Stände sind archiviert und werden nicht mehr zitiert.

---

## Warum eine Zahl ohne ihre Parameter kein Ergebnis ist

Nach der Korrektur blieb ein Befund, der stabil aussah. Verfeinert man den Phasenraum um die triphasische Konfiguration auf ein 2°-Raster, zeigt die Minimalkraft eine klare Struktur: Bei festgehaltenem φ₃ = 240° steigt sie von 0,7677 N bei φ₂ = 100° monoton an, erreicht 5,3304 N exakt bei 120° und fällt danach wieder auf 1,6176 N bei 140°. Zwischen 118° und 120° beträgt die Steigung rund 0,21 N pro Grad (bei K = 10⁴ N/m, dazu unten mehr). In 90,7 % des untersuchten Fensters hebt der Körper überhaupt nicht ab — die Struktur ist ein Phänomen des Dauerkontakts und braucht keine Stoßvorgänge.

Eine Zeltkurve mit einem Meter Höhenunterschied in Newton, an einem Punkt, den man vorher benennen kann. Das ist eine brauchbare Vorhersage.

Nur gehört zu ihr eine Fußnote, die größer ist als die Aussage. Der Wert 5,3304 N gilt für 10 Hz, 7,7 mm Hub und eine Kontaktsteifigkeit von 10 000 N/m. Die letzte Zahl ist keine gemessene Größe, sondern eine Modellannahme. Und die Minimalkraft hängt erheblich an ihr (ζ fest heißt: Dämpfungsgrad der Referenz, ζ = 0,0992; nachrechenbar mit `python3 code/linear_solver.py --ktable`):

| Steifigkeit K [N/m] | 3f / f_n | F_min [N], ζ fest, C = 2ζ√(KM) | F_min [N], C = 16 N·s/m fest |
|---|---|---|---|
| 10 000 | 1,52 | 5,3304 | 5,3304 |
| 23 000 | 1,00 | hebt ab | hebt ab |
| 30 000 | 0,88 | 1,5018 | 0,9139 |
| 100 000 | 0,48 | 3,4073 | 2,0285 |
| 1 000 000 | 0,15 | 4,3404 | 4,3687 |
| 10 000 000 | 0,05 | 4,4823 | 4,4503 |

Der Zusammenhang ist nicht monoton, und das hat einen Grund. An der triphasischen Konfiguration löscht die Mittelung dreier um ein Drittel der Periode versetzter Profile die niedrigen Harmonischen aus; übrig bleiben das Dreifache, Sechsfache und Neunfache der Anregungsfrequenz. Ob die verbleibende Modulation verstärkt oder gedämpft wird, entscheidet sich daran, wo diese Harmonischen relativ zur Eigenfrequenz des Kontakts liegen. Bei den gewählten Parametern liegt diese bei 19,74 Hz — und die dritte Harmonische bei 30 Hz, also knapp darüber. Genau auf die Eigenfrequenz trifft die dritte Harmonische bei 23 095 N/m (3f = f_n). Für K ≈ 21 500 bis 26 250 N/m (ζ fest) hebt der Körper selbst an der triphasischen Konfiguration ab: Die lineare Lösung erreicht dort ein F_min bis −0,855 N, die RK4-Rechnung ergibt bei 23 000 N/m 19,35 % Liftoff. 30 000 N/m liegt knapp oberhalb dieses Bandes, deshalb die niedrige Minimalkraft in der Tabelle.

Für die Flanken der Zeltkurve zählt eine andere Harmonische. Neben dem triphasischen Punkt heben sich erste und zweite Harmonische nicht mehr vollständig auf, und die zweite liegt bei den gewählten Parametern praktisch auf der Kontaktresonanz: 2f/f_n = 1,013, Überhöhung |H₂| = 5,03. Für ein einzelnes Modul mit voller Masse, gleichbedeutend mit synchroner Phasung, hat die zweite Harmonische der Kontaktkraft deshalb eine größere Amplitude (16,125 N) als die erste (13,032 N). Setzt man in der Rechnung nur für die zweite Harmonische |H₂| := 1, fällt die Steigung zwischen 118° und 120° von 0,212 auf 0,046 N pro Grad, und der Anteil des Phasenraums mit Kontaktast (lineare Lösung ohne Abheben) steigt von 4,24 auf 35,3 %. Bei festem ζ und K = 30 000 bis 10 000 000 N/m liegt die Steigung bei 0,09 bis 0,12 N pro Grad. Die 0,21 N pro Grad sind also ein Resonanzwert von K = 10 000 N/m (nachrechenbar mit `python3 code/linear_solver.py --harmonics`).

Macht man die Auflage steif genug, verschwindet die Abhängigkeit. Oberhalb von etwa einer Million Newton pro Meter verändert ein Faktor zehn in K die Minimalkraft noch um 0,14 N, und der Wert läuft gegen den quasistatischen Grenzfall von 4,5483 N, in dem die Kraft nur noch der Spitzenbeschleunigung der Innenmassen folgt.

Daraus folgt eine Auslegungsregel — halte das Verhältnis der dritten Harmonischen zur Kontakteigenfrequenz klein; das gilt für den Wert am triphasischen Punkt, für die Steigung der Zeltkurve und für die Phasenkarte zählen f/f_n und 2f/f_n — und eine Regel für den Umgang mit der Zahl selbst. Die 5,3304 N sind keine Eigenschaft der Phasenlage. Sie sind eine Eigenschaft der Phasenlage bei einer bestimmten, angenommenen Auflagersteifigkeit. Ohne diese Angabe ist die Zahl nicht zitierfähig, und mit vier Nachkommastellen suggeriert sie eine Bestimmtheit, die sie nicht hat.

Es war einiges an Rechnerei nötig, um an diesen Punkt zu kommen. Der Ertrag ist eine Zahl mit einer Bedingung daran statt einer Zahl ohne.

---

## Was ein Vorhaben ohne Messdaten anbieten kann

Nichts von alledem ist gemessen. Es gibt keinen Aufbau, keine Messreihe, keine Kraftsensordaten. Was es gibt, ist eine Frage, die scheitern kann, und die Bedingungen, unter denen sie scheitert.

Das ist weniger, als eine Veröffentlichung üblicherweise beansprucht, aber es ist nicht nichts. Die Zeltkurve ist eine quantitative Vorhersage an einer vorher benannten Stelle des Parameterraums, mit einer Steigung, die man gegen ein Messrauschen halten kann. Der Mittelwert liefert eine unabhängige Kontrollgröße mit exakt bekanntem Sollwert. Das Auswerteverfahren ist beschrieben, Analyseplan und Abbruchkriterien sind präregistriert (die Zeltkurve kommt mit der vorgesehenen v2 der Präregistrierung hinzu), und ein Null-Ergebnis — die Strukturen zeigen sich nicht über dem Rauschen — ist als gültiger Ausgang eingeplant und zur Veröffentlichung vorgesehen.

Offen ist einiges, und das gehört dazu. Zwei Schwellenwerte des Auswerteverfahrens sind nicht festgelegt. Zwischen den Rechnungen und der älteren Textdokumentation besteht eine unentschiedene Diskrepanz bei Frequenz und Profilasymmetrie. Und die schwierigste Frage ist eine metrologische: Wie kalibriert man eine Kraftmesskette für einen Kontakt, der zyklisch abhebt? Statische Rückführbarkeit ist Standard, die Übertragung auf intermittierenden Kontakt ist es nicht.

Getrennt davon läuft eine zweite, ausdrücklich optionale Untersuchung mit eigenem Aufbau: ein frei beweglicher Körper, der über die Kopplung an das umgebende Medium eine gerichtete Nettodrift erfahren könnte. Die Simulationen liefern dort Werte zwischen −0,104 und +0,692 mm/s. Der Effekt skaliert mit der Dichte des Mediums und verschwindet im Vakuum, weil der Reaktionspartner fehlt. Diese Linie hat mit der stationären Wellenformmessung nichts zu tun und wird nicht mit ihr vermischt.

Bleibt der Teil, der sich am schlechtesten in eine Ergebnisliste schreiben lässt: Von den vier ursprünglichen Ergebnisständen ist keiner übrig geblieben. Die Arbeit, die sie erzeugt hat, war trotzdem nicht umsonst — sie hat den Modellfehler sichtbar gemacht, der sie erzeugt hat. Das ist der übliche Verlauf. Nur steht es selten in den Veröffentlichungen.
