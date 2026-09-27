# PCMMS-Logo

Logo in festen Größen als direkt verlinkbare Bilddatei, z. B. für die E-Mail-Signatur.

## Empfohlener Link

360 Pixel breit, gut lesbar:

```
https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-360.png
```

Kleiner, 240 Pixel breit (der Untertitel ist dann sehr fein):

```
https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-240.png
```

## Einfügen in die Signatur

1. Im Signatur-Editor die Funktion „Bild einfügen“ wählen und dort die Möglichkeit
   „aus URL“ bzw. „per Link“ nehmen, dann den Link einsetzen. Wird der Link nur als
   Text in die Signatur kopiert, erscheint auch nur der Text.
2. Erlaubt das Mail-Programm auf dem Handy nur reine Text-Signaturen, die Signatur in
   der Web-Version des Mail-Anbieters am Computer anlegen.
3. Manche Empfänger sehen das Logo erst, nachdem sie „Bilder anzeigen“ angetippt haben.
   Das ist bei verlinkten Bildern normal und kein Fehler des Links.

## Damit der Link dauerhaft funktioniert

Die Links haben kein Ablaufdatum, solange das Repository öffentlich bleibt und die
Datei unter ihrem Namen hier liegen bleibt. Ein Bezahl-Abo ist dafür nicht nötig.
Das Logo wird bei jedem Öffnen einer E-Mail neu geladen: Wird die Datei umbenannt oder
gelöscht oder das Repository auf „privat“ gestellt, verschwindet es auch aus bereits
verschickten E-Mails.

Geeignet sind nur Links, die mit `https://raw.githubusercontent.com/` beginnen und auf
`.png` oder `.jpg` enden. Nicht geeignet sind:

- die Adresse aus der Browserzeile einer GitHub-Dateiseite (enthält `/blob/`): das ist
  eine Webseite, kein Bild;
- Bilder, die in Issues oder Kommentare hochgeladen wurden, und Links aus privaten
  Repositories (enthalten `?token=`): diese laufen ab.

## Alle Größen

Alle Dateien liegen unter
`https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/`
gefolgt vom Dateinamen. PNG ist für ein Logo die bessere Wahl; JPG nur verwenden, wenn
das Mail-Programm kein PNG annimmt.

| Datei | Pixel | Verwendung |
|---|---|---|
| `pcmms-logo-240.png` | 240 × 71 | Signatur, klein |
| `pcmms-logo-360.png` | 360 × 107 | Signatur, empfohlen |
| `pcmms-logo-480.png` | 480 × 143 | HTML-Signatur, angezeigt mit 240 px |
| `pcmms-logo-720.png` | 720 × 214 | HTML-Signatur, angezeigt mit 360 px |
| `pcmms-logo-240.jpg` | 240 × 71 | Ersatz, falls PNG nicht geht |
| `pcmms-logo-360.jpg` | 360 × 107 | Ersatz, falls PNG nicht geht |
| `pcmms-logo.png` | 897 × 267 | Vorlage in voller Auflösung |

Alle Varianten haben einen weißen Hintergrund mit schmalem weißem Rand.

## HTML-Signatur

Nur relevant, wenn das Mail-Programm eine Signatur als HTML-Code annimmt. Auf
hochauflösenden Bildschirmen wird das Logo schärfer, wenn die doppelt so große Datei in
halber Breite angezeigt wird.

Anzeige mit 240 px Breite:

```html
<img src="https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-480.png"
     width="240" height="71" alt="PCMMS - Phase-Controlled Multi-Mass Systems"
     style="display:block;border:0;width:240px;max-width:100%;height:auto;">
```

Anzeige mit 360 px Breite:

```html
<img src="https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-720.png"
     width="360" height="107" alt="PCMMS - Phase-Controlled Multi-Mass Systems"
     style="display:block;border:0;width:360px;max-width:100%;height:auto;">
```

`display:block` setzt das Logo in eine eigene Zeile.

## Herkunft

Beschnitten aus der Logo-Grafik von Matthias Früh (1080 × 342 px), Hintergrund auf
reines Weiß gesetzt, bikubisch ohne Nachschärfen verkleinert.
