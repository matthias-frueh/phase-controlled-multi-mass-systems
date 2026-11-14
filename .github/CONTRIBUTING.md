# Beitragsregeln

**PCMMS — Phasenkontrollierte Mehrmassensysteme**\
Matthias Früh · Unabhängiger Forscher · ORCID [0009-0005-9984-4207](https://orcid.org/0009-0005-9984-4207)\
Stand: 12. November 2026

Diese Datei regelt, wie Korrekturen, Hinweise und Änderungen in dieses Repository gelangen. Was das Projekt
untersucht und was es ausdrücklich nicht behauptet, steht im [README](../README.md#worum-es-geht); wo man mit dem
Lesen anfängt, in der [Leseführung](../LESEFUEHRUNG.md).

---

## Meldeweg

- **Korrekturen, Hinweise und Reproduktionsbefunde:** als
  [GitHub Issue](https://github.com/matthias-frueh/phase-controlled-multi-mass-systems/issues).
- **Änderungen an Dateien:** als Pull Request gegen `main`. Eine Regel des Repositorys lässt Änderungen an `main`
  nur über Pull Requests zu.

## Verantwortung

Prüfung und Merge erfolgen ausschließlich durch den Autor. Ob und in welcher Form ein Beitrag übernommen wird,
entscheidet er.

## Nachweise

- **Zahlen** stehen mit Fundstelle: bei Angaben aus dem Repository die Datei mit Abschnitt, Zeile oder Datensatz;
  bei neuen Rechenergebnissen das erzeugende Skript mit Aufruf; bei Angaben aus der Literatur die Quelle mit Seite
  oder Gleichung.
- **Reproduktionsbefunde** nennen den Commit, den vollständigen Aufruf und die maßgebliche Ausgabe im Wortlaut.
  Weicht das Ergebnis von einer Angabe im Repository ab, wird diese Angabe mit Fundstelle genannt.
- **Pull Requests, die Code oder Tests ändern,** nennen in derselben Form das Ergebnis der Testsuite
  (`python3 -m pytest tests -q`, etwa 7 bis 13 Minuten je nach Rechner; siehe
  [README, „Nachrechnen“](../README.md#nachrechnen)).

## Literatur

Quellen werden vollständig angegeben. Hat eine Quelle eine DOI, wird sie genannt und vorher geprüft: Sie muss auf
genau die angegebene Arbeit führen. Quellen ohne DOI sind nicht ausgeschlossen, wenn sie nachprüfbar sind, etwa
über ISBN und Seitenangabe, Normnummer und Ausgabe, arXiv-Kennung oder eine dauerhaft erreichbare Adresse mit
Abrufdatum.

## Lizenz

Beiträge folgen der bestehenden Zuordnung: Code, Skripte und Tests stehen unter MIT, Dokumente, Daten, Protokolle
und Ausgaben unter CC BY 4.0. Maßgeblich ist die Aufstellung im [README, „Lizenz“](../README.md#lizenz) mit den
Dateien [`LICENSE`](../LICENSE) und [`LICENSE-CC-BY-4.0`](../LICENSE-CC-BY-4.0). Wer etwas einreicht, stellt es
unter die Lizenz, die für den Ablageort gilt. Fremdes Material wird nur mit Quellenangabe und einer dazu
passenden Lizenz übernommen.

## Wissenschaftlicher Status

Alles in diesem Repository ist Simulation oder Analytik; Messdaten existieren nicht. Beiträge halten diese
Trennung ein:

- Jede Aussage sagt, worauf sie beruht: analytische Herleitung, numerische Simulation oder Messung.
- Simulations- und Rechenergebnisse werden nicht als experimenteller Nachweis formuliert.
- Der Status gehört zur Aussage. Die Kennzeichnungen des Repositorys stehen in der
  [Leseführung, „Kennzeichnungen“](../LESEFUEHRUNG.md#kennzeichnungen).

---

*Contributing (EN):* Report corrections and reproduction findings via GitHub Issues; propose changes via pull
requests against `main`. Review and merge are done by the author only. All documents are in German; everything
here is simulation output, measured data do not exist.

*Vermerk:* Erstellt am 12.11.2026, Chat-Sitzung (Claude), nach Auftrag des Autors. Pfade, Befehle und
Einstellungen (Issues aktiv, Pull-Request-Regel für `main`) sind am Repository-Stand `5321864` geprüft.
Lizenz: CC BY 4.0 wie `docs/`.
