# PCMMS — Review-Leitfaden: Skripte zu Linie B (Medienkopplung)

**Datum:** 06.09.2026 · **Zweck:** externe Prüfung der beiden Skripte, auf die sich die Notiz
`PCMMS_Notiz_Richtung_Medienkopplung_2026-09-06_v5.md` stützt · **Autor:** Matthias Früh

> **Vermerk (22.10.2026).** Originaldatei `PCMMS_Review_Leitfaden_Skripte_LinieB_2026-09-06.md`, Stand 06.09.2026;
> hier unverändert bis auf diesen Vermerk. Prüfanleitung der externen Skriptprüfung zu Linie B, Arbeitspaket AP-28
> (Stufe S5, Status „später“, [`../arbeitsplan_status.md`](../arbeitsplan_status.md)). Simulation, keine Messdaten.
> Zuordnung und Stand:
> - **Dateien (§1):** Die drei v1-Skripte liegen unverändert in
>   [`quelle_v1/`](../../rechnungen/linie_b/review_2026-09-06/quelle_v1/), Reproduktionsskript und Ausgabe in
>   [`review_2026-09-06/`](../../rechnungen/linie_b/review_2026-09-06/) (Aufruf in
>   [`rechnungen/README.md`](../../rechnungen/README.md), Abschnitt `linie_b/`); `sweep_13x13_drift.csv` ist
>   [`daten/sweep_13x13_drift_v1.csv`](../../rechnungen/linie_b/daten/sweep_13x13_drift_v1.csv). Die MD5-Angaben der
>   Tabelle stimmen für diese fünf Dateien (geprüft 22.10.2026); `-2.py` liegt nicht im Repository. Die v1-Skripte sind
>   Prüfgegenstand, kein Werkzeug. Die geprüfte Notiz „v5“ liegt in der Fassung v5.2 vor
>   ([Richtungsnotiz v5.2](richtungsnotiz_medienkopplung_2026-09-06_v5_2.md)).
> - **Fragen (§4):** laut [`skriptkorrekturen_2026-09-06.md`](skriptkorrekturen_2026-09-06.md) (Kopf) von der Prüfung
>   beantwortet; die Antworten selbst liegen nicht im Repository. Übernommene Befunde dort §1, darunter abweichend vom
>   Leitfaden: Die 0,2 % im Dichtevergleich (§3) waren Resteinschwingen, die Profilamplitude im Fall M2 (heute Fall R)
>   beträgt 400 mm/s; Umsetzung in den v2-Skripten in [`quelle_kopie/`](../../rechnungen/linie_b/quelle_kopie/).
> - **Ergebnisse (§3):** nachgerechnet in [`PROTOKOLL.md`](../../rechnungen/linie_b/PROTOKOLL.md) LB-04 bis LB-08;
>   die Dichteunabhängigkeit gilt nur für c₁ = 0 (LB-06), τ und F̄_A für Wasser sind wegen der zugesetzten Masse nicht
>   belastbar (LB-03).
> - **Nicht Gegenstand (§5):** Die KC-Zahl beträgt 0,004–0,006 statt ≈ 10⁻² (LB-01); dort ist ein quasistationäres
>   Widerstandsgesetz nicht begründet, für einen glatten Träger nicht gültig (LB-02). Das Kraftmodell ist Gegenstand
>   von AP-28.
>
> Lizenz wie der Ordner: CC BY 4.0 ([`../../LICENSE-CC-BY-4.0`](../../LICENSE-CC-BY-4.0)).

## 1 · Dateien im Paket

| Datei | Zeilen | MD5 | Status |
|---|---|---|---|
| `pcmms_fluid_drift.py` | 178 | f49f5cd4… | Original, unverändert. Erzeugt `sweep_13x13_drift.csv` |
| `pcmms_medienkopplung_modell.py` | 79 | 95a9d926… | Original, „kanonisch" |
| `pcmms_medienkopplung_modell-1.py` | 112 | 7c010a27… | Original, mit v3.4-Erweiterung (Mehrmassen, Reibung, Pendel). Im Projekt existiert `-2.py` mit identischem MD5 |
| `sweep_13x13_drift.csv` | 169 Punkte | 10ff7a9e… | Original; keine Duplikate, Raster 0…332,3° in Schritten von 27,69° |
| `pcmms_review_reproduktion_2026-09-06.py` | — | 94886b12… | **Neu**, von der Prüfung getrennt zu lesen; importiert die Originale, verändert sie nicht |
| `pcmms_review_reproduktion_2026-09-06_output.txt` | — | — | Ausgabe des Reproduktionslaufs (Laufzeit 28 s) |

## 2 · Zuordnung Notiz ↔ Code

| Aussage in der Notiz (v5) | Stelle im Code | Prüfbefund |
|---|---|---|
| Modell B mit c₁ = 0; Widerstand auf Trägergeschwindigkeit relativ zum Medium (§4.2) | `pcmms_fluid_drift.py` Z. 67–68: `v_rel = Vcm - RATIO*r_dot(t)`, `a = -(c_drag/M_TOTAL)*|v_rel|*v_rel` | Bestätigt. Trägergeschwindigkeit exakt aus Impulskinematik (kein Rückstoß-Näherungsschritt); r_dot ist der Modulmittelwert, bei gleichen Modulmassen identisch mit der massengewichteten Summenbewegung |
| ρ = 1000 (Wasser) im Driftskript | Z. 25, 62 | Bestätigt |
| Burn-in 4 s unter τ ≈ 6 s; CSV-Maximum transientenbehaftet (§7 Punkt 2) | Z. 36–37, 79–82 | **Bestätigt und quantifiziert**, siehe §3 |
| Dichteunabhängigkeit der stationären Drift im gemittelten Modell (§4.2) | `pcmms_medienkopplung_modell.py` Z. 29–34 (`_drift`: Bilanz ⟨kd(vd+v_osc)⟩ = 0) | Bestätigt für das integrierte Modell bei ρ = 1000 gegen 100, siehe §3 |
| ρ = 1,2 (Luft) im Medienkopplungsmodell | Z. 27 | Bestätigt |
| Egg-Profil: schnelle Phase 35 %, langsame 65 %, gleicher Weg | `pcmms_fluid_drift.py` Z. 31–33, 44–51 | Bestätigt (V_SLOW·HOLD = V_FAST·(1−HOLD)) |
| Richtungsregel: Drift in Richtung des schnellen Innenmassenhubs (§4) | Z. 49 (schnelle Phase +V_FAST) → CSV (0,0) = +0,6916 mm/s | Konsistent: Innenmassen schnell nach +, Träger schnell nach −, mittlere Medienkraft nach +, Drift + |
| Auslenkung x = F·L/(M·g) (§4.3) | `-1.py` Z. 98–100 | Bestätigt |
| „Bloß zeitliche Asymmetrie reicht nicht" (§5: ⟨V|V|⟩ ≠ 0 nicht garantiert) | `pcmms_medienkopplung_modell.py` Z. 36–43 (`two_level`) | Bestätigt: zweistufige Kraft → Sägezahn-v mit gleichverteilter Geschwindigkeit → Drift = 0 |

## 3 · Reproduktionsergebnisse (Skriptparameter, Referenzpunkt φ₂ = φ₃ = 0)

**Konvergenz (ρ = 1000):** Periodenmittel von V_cm bei 2 / 4 / 8 / 16 / 32 / 60 s:
0,320 / 0,541 / 0,805 / 0,996 / 1,052 / 1,055 mm/s.
Mittel 4–8 s (CSV-Fenster): **0,6916 mm/s** — reproduziert den CSV-Wert 0,691635 exakt.
Mittel 40–60 s: **1,0547 mm/s.** Der CSV-Referenzwert liegt damit 34 % unter dem stationären Wert;
der stationäre Wert liegt 53 % über dem CSV-Wert. Die gesamte 13×13-Karte ist mit demselben Fenster
gerechnet; ihre Absolutwerte sind entsprechend zu klein, die Vorzeichen und die relative Struktur
sind davon nicht notwendig betroffen (zu prüfen).

**Gemittelte Bilanz (Modell B, c₁ = 0, v_osc = −RATIO·ṙ):** v_d = **1,0549 mm/s** — stimmt mit
dem integrierten Modell auf vier Stellen überein. Die Näherung „Widerstand ≪ Trägheit" ist für diese
Parameter erfüllt.

**Dichtevergleich (ρ = 100, T_SIM = 400 s):** Periodenmittel bei 100 / 200 / 300 / 400 s:
0,879 / 1,026 / 1,050 / 1,054 mm/s; Mittel 300–400 s **1,0528 mm/s** (ρ = 1000: 1,0549).
Dichteunabhängigkeit der stationären Drift innerhalb 0,2 % über einen Faktor 10 in ρ; die
Einschwingzeit skaliert wie τ ≈ M/(2c₂ρ⟨|v_osc|⟩): 5,8 s / 58 s / 4870 s für ρ = 1000 / 100 / 1,2.

**Definition „effektiver Schub" (Medienkopplungsmodell, Fall M1):** Das Skript gibt
F_eff = kd·v_d·|v_d| zurück (Z. 43, 51, 60) — den Widerstand, den ein stationär mit v_d bewegter
Körper erführe. Die Notiz verwendet für Konfiguration D die Gleichrichtungskraft bei vorgegebener
mittelwertfreier Bewegung, F̄_A = −kd·⟨v_osc|v_osc|⟩. Für M1: v_d = 5,31 mm/s, ⟨|v_osc|⟩ = 51,9 mm/s;
F_eff(Skript) = 3,39×10⁻⁷ N, F̄_A = 6,67×10⁻⁶ N, **Verhältnis 19,7** ≈ 2⟨|v_osc|⟩/|v_d|.
Pendelauslenkung (L = 1 m, M = 1 kg): 34,5 nm nach Skriptdefinition, 680 nm nach F̄_A.
Die Zahlen „Schub ~10⁻⁷–10⁻⁴ N" und „34,7 nm" im Forschungsrahmen §9 folgen der Skriptdefinition.

## 4 · Fragen an die Prüfung

1. **Modellgleichung.** Ist `v_rel = Vcm - RATIO*r_dot` die richtige Trägergeschwindigkeit relativ
   zum Medium für eine starre Hülle mit drei gleichen Innenmassen (Impulskinematik, keine Näherung)?
2. **Welche Kraft misst Konfiguration D?** F_eff = kd·v_d² (Skript) oder F̄_A = −kd⟨v_osc|v_osc|⟩
   (Notiz, Modell A/C)? Nach der Herleitung in der Notiz ist k⟨x⟩ = F̄_C ≈ F̄_A. Wenn das trägt, sind
   Forschungsrahmen §9 (Schub, Pendelauslenkung) und Prüfarchitektur §2 (Auflösung) um den Faktor
   2⟨|v_osc|⟩/|v_d| zu korrigieren — für M1 ≈ 20, für die Driftskript-Parameter ≈ 10. Bitte
   unabhängig herleiten.
3. **Konvergenz der Karte.** Reicht die Aussage „Absolutwerte um ~35 % zu klein, Struktur erhalten",
   oder ist die Karte mit T_BURN ≥ 40 s und T_SIM ≥ 60 s neu zu rechnen, bevor sie zitiert wird?
4. **Raster.** Das 13er-Raster (Schritt 27,69°) enthält weder 120° noch 240°; die triphasische
   Konfiguration ist in der CSV nicht enthalten (nächster Punkt (110,8°; 249,2°): −0,024 mm/s).
   Aussagen über „Triphasik" dürfen sich nicht auf diese CSV stützen. Zustimmung?
5. **Vorzeichenwechsel.** 54 von 169 Rasterpunkten haben negative Drift. Ist das konsistent mit der
   Richtungsregel der Notiz („Richtung aus dem vollständigen massengewichteten Summenprofil"), oder
   deutet es auf einen Implementierungsfehler (z. B. in der Phasenverschiebung `egg_vel(t - tau)`)?
6. **Numerik.** RK4 mit zeitabhängigem r_dot an Halbschritten (Z. 70–78), DT = 5×10⁻⁵ bei 10 Hz:
   ausreichend? Periodenmittel über ganze Perioden (4 s = 40 Perioden) im Original zufällig erfüllt;
   für andere T_BURN nicht garantiert.
7. **CSV-Anhängemodus.** Z. 92 öffnet die CSV mit `'a'`; Mehrfachläufe erzeugen Duplikate. Die
   vorliegende Datei ist duplikatfrei; für künftige Läufe Modus `'w'` oder Duplikatprüfung.
8. **Null-Befund zweistufige Kraft.** Ist die Argumentation (Sägezahn-v → gleichverteilte
   Geschwindigkeit → ⟨v|v|⟩ = 0) allgemein richtig, und stützt sie die Aussage der Notiz, dass
   Zeitasymmetrie der Anregung allein ⟨V|V|⟩ ≠ 0 nicht garantiert?
9. **Zwei Versionen** des Medienkopplungsmodells im Projekt (79 und 112 Zeilen; `-1` = `-2`).
   Welche ist die zitierfähige? Vorschlag: die 112-Zeilen-Fassung als kanonisch führen, die
   79-Zeilen-Fassung archivieren.
10. **Kleinigkeiten.** `except:` ohne Ausnahmetyp (Z. 146); ungültige Escape-Sequenz `\~` (Z. 169,
    SyntaxWarning); `brentq`-Intervall in `_drift` auf ±max|v_osc| begrenzt (Z. 33–34) — für M2 mit
    72 mm/s Drift bei 100 mm/s Amplitude knapp.

## 5 · Nicht Gegenstand dieser Prüfung

Die Gültigkeit des quasistationären Widerstandsgesetzes für die tatsächliche Oszillation
(Notiz §6, KC ≈ 10⁻²) ist eine Modellfrage, keine Codefrage. Alle Zahlen oben gelten innerhalb des
Zweiterm-Ansatzes mit stationärem C_D; sie sind keine physikalischen Effektgrößen.
