# PCMMS-Logo

Logo in festen Größen, z. B. für die E-Mail-Signatur. Das Repository ist
öffentlich, die Links über `raw.githubusercontent.com` laufen daher nicht ab
und liefern die Datei direkt als `image/png` bzw. `image/jpeg` aus.

Weißer Hintergrund, schmaler weißer Rand, Seitenverhältnis ca. 3,36 : 1.

| Datei | Größe (px) | Direktlink |
|---|---|---|
| `pcmms-logo-240.png` | 240 × 71 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-240.png |
| `pcmms-logo-360.png` | 360 × 107 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-360.png |
| `pcmms-logo-480.png` | 480 × 143 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-480.png |
| `pcmms-logo-720.png` | 720 × 214 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-720.png |
| `pcmms-logo-240.jpg` | 240 × 71 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-240.jpg |
| `pcmms-logo-360.jpg` | 360 × 107 | https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-360.jpg |
| `pcmms-logo.png` | 897 × 267 | Vorlage in voller Auflösung |

## In der Signatur

Wird nur die Bild-URL eingefügt, erscheint das Bild meist in seiner
Pixelgröße: `pcmms-logo-240.png` oder `pcmms-logo-360.png` nehmen.

In einer HTML-Signatur wird das Logo auf hochauflösenden Displays schärfer,
wenn die doppelt so große Datei auf die halbe Breite gesetzt wird:

```html
<img src="https://raw.githubusercontent.com/matthias-frueh/phase-controlled-multi-mass-systems/main/assets/logo/pcmms-logo-480.png"
     width="240" height="71" alt="PCMMS – Phase-Controlled Multi-Mass Systems"
     style="display:block;border:0;width:240px;height:auto;">
```

Für 360 px Anzeigebreite entsprechend `pcmms-logo-720.png` mit
`width="360" height="107"`.

Die Links zeigen auf den Branch `main`. Wird eine Datei hier ersetzt, ändert
sich der Link nicht; E-Mail-Programme können die alte Version aber eine Weile
zwischenspeichern.
