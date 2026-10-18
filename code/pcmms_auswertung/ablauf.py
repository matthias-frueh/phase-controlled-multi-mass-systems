"""Zustandsbehafteter Ablauf der Phase 1 in der Simulation (Präreg §6, §8.8, §9.1, §9.2, A9.12). Simulationssoftware,
keine Steuerung einer Messapparatur (AP-10).

Getrennt sind die geplante Laufreihenfolge (kampagne.laufplan mit dem Reihenfolgegenerator von §6) und die tatsächlich
ausgeführte Reihenfolge. Jeder Versuch erhält eine Kennung, den Bezug zum geplanten Lauf, einen Versuchszähler, Rolle,
Anlass, Zeitpunkt und seine Gültigkeits- und Alarmgründe; verworfene und ersetzte Versuche bleiben erhalten. Jeder
Versuch dauert T_Lauf; nachfolgende Läufe und ihre zeitabhängigen Effekte (Nullpunktdrift) verschieben sich, ein Messtag
beginnt tag_pause nach dem letzten Lauf des Vortags. Entschieden wird nur mit dem, was zu diesem Zeitpunkt feststeht:
G2–G10 nach dem Lauf, G1 mit dem nächsten gültigen Referenzlauf (Vorprüfung gegen R₀ sofort), Nullpunktalarm gegen den
vorangehenden gültigen Referenzlauf, S1–S4 – nie mit Wahrheit, Vorhersagen, Hypothesen- oder E3-Größen; die Messung
erhält nur die Kopfangaben des Versuchs.

Regeln (maßgeblich ist die Präregistrierung; Lesarten unten):
- Konfigurationslauf, vor Beginn des Schlusskontrollsatzes seines Blocks als ungültig erkannt: Wiederholung an einem
  Platz, den der Reihenfolgegenerator gleichverteilt unter den offenen Konfigurationsplätzen des Blocks und dem Platz vor
  dem Schlusskontrollsatz zieht (rng.integers(0, m + 1) bei m offenen Konfigurationsläufen; Platz j < m: unmittelbar
  vor dem j-ten offenen Konfigurationslauf, j = m: vor dem Schlusskontrollsatz); höchstens zwei Wiederholungen je
  Konfiguration und Block, danach fehlt der Lauf (Reserve r). Die übrigen geplanten Läufe behalten ihre Reihenfolge.
- G1/S1: Vorprüfung |⟨N⟩_X − ⟨N⟩_R₀| > ε_ctrl → sofort R₁. Mit dem nächsten gültigen Referenzlauf steht G1 aller
  offenen Läufe fest (Interpolation zwischen den einschließenden gültigen Referenzläufen, gueltigkeit.interpolation).
  Steht ein Verstoß vor Beginn des Schlusskontrollsatzes fest: sofort R₂, X′, R₃, auch über die Wiederholungsgrenze
  hinaus; X′ zählt als Wiederholung. X′ hat keine Vorprüfung mit R₁; sein G1 steht mit R₃ fest. S1, wenn X′ G1
  gegen die Klammer R₂/R₃ desselben Falls verletzt (eine nicht reproduzierte Alarmwiederholung ersetzt R₂ bzw. R₃,
  §8.8). Ist die Klammer unvollständig (R₂ oder R₃ ungültig), gilt G1 von X′ wie für jeden Lauf zwischen den
  einschließenden gültigen Referenzläufen, S1 ist dann „nicht prüfbar“ und wird nicht ausgelöst; ein dabei G1-ungültiges
  X′ wird nicht weiter wiederholt. Ein aus anderem Grund ungültiges X′ folgt der Regel für Konfigurationsläufe. Später
  festgestellte Verstöße werden weder wiederholt noch nach S1 geprüft.
- Nullpunktalarm: sofortige Wiederholung; Überschreitung im selben Kanal → S1, sonst ersetzt die Wiederholung den
  alarmierten Lauf. Aufwärm-Referenzläufe lösen keinen Alarm aus; bis zwei aufeinanderfolgende um weniger als σ̂_ref
  differieren, höchstens zehn, sonst Halt (§6).
- Kontrolllauf: aus anderem Grund als G1 ungültig (bei R auch ein nicht reproduzierter Alarm) → sofort wiederholt,
  höchstens zweimal, danach Halt; bei L₁′–L₃′ fehlt der Lauf danach, ohne Halt.
- S2 (Einzelzell-Liftoff, ohne G5/G8/G10-ungültige Läufe): Halt; die Konfiguration bleibt in den Blöcken, wird weiter
  gemessen und ist von Tests ausgeschlossen (Stufe 2), bei Lⱼ ist ŷ¹ ungültig (§8.2); ein zweites S2 ohne
  festgestellten Apparaturfehler beendet Phase 1 (abgebrochen). Maßgeblich ist die S2-Bilanz (gueltigkeit.s2_bilanz,
  offline gleich): Ein S2 zählt nicht, wenn die Wiederaufnahme seines Halts einen Apparaturfehler ausdrücklich
  feststellt; die Ausschlüsse bleiben. Ein S2 während eines anderen Halts (Kontrolllauf an der Grenze) wird gezählt.
  S3 in Lⱼ (Einstellung 1): Überschreitung → sofortige Wiederholung; dieselbe Größe erneut → Halt. S4: G2 in zwei
  aufeinanderfolgenden Läufen → Halt.
- Halt: Ablaufstand mit Grund, fortsetzbar nur mit einem ausdrücklich übergebenen externen Ereignis (fortsetzen);
  danach zuerst ein vollständiger Kontrollsatz (gemessen, ohne Alarm), dann der unterbrochene Block in der gezogenen
  Reihenfolge. Ein angehaltener oder abgebrochener Ablauf ist keine abgeschlossene Kampagne.
- Einstellung 2: G2–G4 nicht gefasst (nicht prüfbar); ob S1, S2 und S4 für L₁′–L₃′ gelten, ist offen (§12) – nicht
  angewandt und als Lücke vermerkt. Für Einstellung 2 gibt es keine Qualifikationsaussage.

Lesarten, wo die Präregistrierung nicht ausdrücklich ist (im Bericht als offen geführt):
- Schlusskontrollsatz eines Blocks ist der Kontrollsatz an seinem Ende (Plankennung block = b); ein mit dem Folgeblock
  geteilter Satz gehört als Schlusskontrollsatz zum vorangehenden Block.
- G1, S1 und die Vorprüfung betreffen nur Läufe ohne Verstoß gegen G2–G10; ein sonst ungültiger Lauf folgt der
  Wiederholungsregel seiner Art.
- Ein Referenzlauf außerhalb eines Kontrollsatzes, der gegen G2–G10 verstößt, wird nicht wiederholt (keine Regel); er
  ist kein Bezug. Ein Alarm der Wiederholung nur in anderen Kanälen führt zu einer weiteren Wiederholung (technische
  Grenze GRENZE_ALARMKETTE, danach Halt ohne Regelausgang).
- S3 wird an Lⱼ ohne Verstoß gegen G2–G10 geprüft; eine gültige S3-Wiederholung ist ein gültiger Kontrolllauf (§8.2).
- Der Kontrollsatz der Wiederaufnahme wird in einer vom Reihenfolgegenerator gezogenen Reihenfolge gemessen.
- Liegt nach einem Halt ein Messtag dazwischen, ändert das nichts an der Zuordnung zum unterbrochenen Block.

Zustand: zustand() liefert den vollständigen, serialisierbaren Ablaufstand (Warteschlange, Versuche mit Daten, Zähler,
Zustand des Reihenfolgegenerators); Ablauf.aus_zustand setzt fort. Die Kennung (Verfahren, Seeds, Teil B, Plan) gehört
zum Stand; eine Fortsetzung mit anderer Kennung wird zurückgewiesen.
"""
import copy
import math
from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats

from . import formate, gueltigkeit, konventionen as kv, zusammenfassung as zf

VERSION = 'ablauf-2'            # ablauf-2: X′ ohne Vorprüfung mit R₂/R₃ geprüft; S2-Bilanz aus den Ereignissen
GRENZE_KONFIGURATION = 2        # §6, A9.12: höchstens zwei Wiederholungen je Konfiguration und Block
GRENZE_KONTROLLE = 2            # A9.12: Kontrolllauf höchstens zweimal sofort wiederholt
GRENZE_AUFWAERMEN = 10          # §6: höchstens zehn Aufwärm-Referenzläufe
GRENZE_ALARMKETTE = 10          # technische Grenze (keine Fachregel): Alarmwiederholungen ohne Regelausgang
REGELN_LAUF = ('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10')
SOFORT = ('R1', 'R2', 'X_strich', 'R3', 'kontrollwiederholung', 'alarmwiederholung', 's3_wiederholung',
          'aufwaermen', 'wiederaufnahme_kontrolle')
LUECKEN_E2 = ('Einstellung 2: G2–G4 nicht gefasst (f′, δf_tol′, σ_tol′, σ_Δ′ offen, §12)',
              'S1, S2 und S4 für L₁′–L₃′ offen (§12): nicht angewandt')


@dataclass(frozen=True)
class Ablaufoptionen:
    """wiederholungen: Konfigurations-, Kontroll-, G1-/S1-, Alarm- und S3-Wiederholungen nach A9.12; aufwaermen:
    Aufwärm-Referenzläufe nach §6 (sonst der eine Aufwärmlauf des Laufplans); halt: S1–S4, ausgeschöpfte Kontrollläufe
    und nicht abgeschlossenes Aufwärmen halten an. Alle aus: der Laufplan wird unverändert ausgeführt."""
    wiederholungen: bool = True
    aufwaermen: bool = True
    halt: bool = True


AUS = Ablaufoptionen(False, False, False)


class AblaufFehler(ValueError):
    pass


def _konfig(spec):
    return spec['konfiguration']['id']


def _schluessel(*teile):
    return '|'.join(str(x) for x in teile)


def versuch_passt(auswahl, spec, versuch):
    """Auswahl eines Ereignisses unter den Versuchen (Effekt „ereignis“ mit Schlüssel „versuch“)."""
    for k, v in auswahl.items():
        if k == 'konfiguration' and _konfig(spec) != v:
            return False
        if k in ('block', 'messtag', 'laufart') and spec.get(k) != v:
            return False
        if k in ('nummer', 'rolle') and versuch.get(k) != v:
            return False
    return True


def s3_basis(tab0, gueltige_ids, kmax, n_tests=42):
    """S3-Bezug je Modul aus den gültigen Einzelmodulläufen Lⱼ der Phase 0 (Einstellung 1): Mittel, Streuung, n₀ⱼ und
    Schwelle c_S·s·√(1 + 1/n₀ⱼ), c_S = t(1 − 0,05/42; n₀ⱼ − 1), wie gueltigkeit.s3_pruefung."""
    out = {}
    for j in (1, 2, 3):
        sel = [i for i, k in enumerate(tab0.koepfe) if k['laufart'] == 'L' and k['phase'] == 0 and k['modul'] == j
               and k['einstellung'] == 1 and k['lauf_id'] in gueltige_ids]
        if len(sel) < 2:
            continue
        X0 = kv.h1_vektor(tab0.daten['Nk_summe'][sel, :kmax])
        mu, s = X0.mean(0), X0.std(0, ddof=1)
        n0 = len(sel)
        cS = stats.t.ppf(1 - 0.05 / n_tests, n0 - 1)
        out[str(j)] = dict(mu=mu, schwelle=cS * s * np.sqrt(1 + 1 / n0), n0=n0)
    return out


def schwellen_kennung(sw, s3, stellen=12):
    """Prüfsumme der Eingänge, mit denen der Ablauf entscheidet (Schwellen aus Teil B, S3-Bezug), auf `stellen`
    Nachkommastellen gerundet: unabhängig vom letzten Bit der linearen Algebra und vom übrigen Inhalt von Teil B."""
    def rund(x):
        if isinstance(x, dict):
            return {str(k): rund(v) for k, v in x.items()}
        if isinstance(x, (list, tuple, np.ndarray)):
            return [rund(v) for v in np.asarray(x, dtype=object).tolist()] if not isinstance(x, np.ndarray) or \
                x.dtype == object else np.round(np.asarray(x, float), stellen).tolist()
        if isinstance(x, (float, np.floating)):
            return None if not np.isfinite(x) else round(float(x), stellen)
        return x
    felder = {k: rund(v) for k, v in sw.__dict__.items() if k != 'herkunft'}
    return formate.sha256_json(dict(schwellen=felder, s3=rund(s3)))


class Ablauf:
    """Ablauf der Phase 1 einer Kampagne. geplant: Phase-1-Läufe des Laufplans in geplanter Reihenfolge; messung:
    Objekt mit messen(spec, versuch) → (Kopf, Datenfelder mit führender Länge 1); sw: Schwellen aus Teil B
    (auswertung._schwellen); s3: s3_basis; rng: Reihenfolgegenerator nach dem Ziehen des Laufplans; optionen:
    Ablaufoptionen; T_lauf, tag_pause aus dem Plan; kennung: Herkunft (Verfahren, Seeds, Teil B, Plan)."""

    def __init__(self, geplant, messung, sw, s3, rng, optionen, T_lauf, tag_pause, kennung=None, _zustand=None):
        self.messung, self.sw, self.s3, self.rng, self.opt = messung, sw, s3, rng, optionen
        self.T_lauf, self.tag_pause = float(T_lauf), float(tag_pause)
        self.kennung = kennung
        self.geplant = [dict(l) for l in geplant]
        if any(l['phase'] != 1 for l in self.geplant):
            raise AblaufFehler('Ablauf: nur Läufe der Phase 1')
        self.tage = []
        for l in self.geplant:
            if not self.tage or self.tage[-1][-1]['messtag'] != l['messtag']:
                self.tage.append([])
            self.tage[-1].append(l)
        self.ks = self._kontrollsaetze()
        if _zustand is not None:
            self.z = _zustand
            return
        self.z = dict(version=VERSION, status='bereit', tag=-1, queue=[], t=float(self.geplant[0]['t_start']),
                      position0=int(self.geplant[0]['position']), versuche=[], r0=None, offen_g1=[], wdh={}, kwdh={},
                      s3_offen={}, schluss_begonnen=[], s2=[], s2_zaehler=0, s4_vor=False, ziehungen=[], halt=None,
                      ende=None, luecken=[], ausgeschlossen=[], ereignisse=[], aufwaermen=[], alarmkette=0,
                      wiederaufnahmen=0, entscheidungen=[])

    # ── Plan ────────────────────────────────────────────────────────────────────────────────────────────
    def _kontrollsaetze(self):
        """Je Kontrollsatz: Block und ob er Schlusskontrollsatz dieses Blocks ist (folgt auf Konfigurationen des
        Blocks); je Block der Schlusskontrollsatz."""
        ks, gesehen = {}, set()
        for l in self.geplant:
            if l['laufart'] == 'K':
                gesehen.add(l['block'])
            if l['kontrollsatz'] is not None and l['kontrollsatz'] not in ks:
                ks[l['kontrollsatz']] = dict(block=l['block'], schluss=l['block'] in gesehen)
        schluss = {v['block']: k for k, v in ks.items() if v['schluss']}
        return dict(saetze={str(k): v for k, v in ks.items()}, schluss={str(b): k for b, k in schluss.items()})

    def _rolle_geplant(self, l):
        if l['laufart'] == 'R' and l['block'] is None:
            tag = next(t for t in self.tage if t[0]['messtag'] == l['messtag'])
            return 'aufwaermen' if l is tag[0] or l['lauf_id'] == tag[0]['lauf_id'] else 'schlussreferenz'
        if l['kontrollsatz'] is not None:
            return 'kontrolle'
        if l['laufart'] == 'R':
            return 'referenz_block'
        return 'konfiguration'

    def _element(self, l):
        return dict(spec={k: l[k] for k in ('lauf_id', 'laufart', 'modul', 'einstellung', 'konfiguration', 'phase',
                                            'block', 'messtag', 'kontrollsatz', 'position')},
                    rolle=self._rolle_geplant(l), geplant=True, bezug=l['lauf_id'], nummer=0, anlass='Laufplan')

    # ── Ausführung ──────────────────────────────────────────────────────────────────────────────────────
    @property
    def status(self):
        return self.z['status']

    def ausfuehren(self, bis=None):
        """Führt den Ablauf bis zum Ende, zu einem Halt oder (bis: Zahl der Phase-1-Versuche) zu einer technischen
        Unterbrechung aus. Rückgabe des Status."""
        if self.z['status'] in ('angehalten', 'abgebrochen', 'abgeschlossen'):
            raise AblaufFehler(f'Ablauf {self.z["status"]}: Fortsetzung nur mit fortsetzen(ereignis)'
                               if self.z['status'] == 'angehalten' else f'Ablauf bereits {self.z["status"]}')
        self.z['status'] = 'laufend'
        while self.z['status'] == 'laufend':
            if bis is not None and len(self.z['versuche']) >= bis:
                self.z['status'] = 'unterbrochen'
                break
            if not self.z['queue']:
                if self.z['tag'] + 1 >= len(self.tage):
                    self._offen_am_ende()
                    self.z['status'] = 'abgeschlossen'
                    self.z['ende'] = dict(status='abgeschlossen', grund='alle Blöcke gemessen')
                    break
                self._neuer_tag()
                continue
            self._schritt(self.z['queue'].pop(0))
        return self.z['status']

    def _neuer_tag(self):
        z = self.z
        if z['tag'] >= 0:
            z['t'] += self.tag_pause
        z['tag'] += 1
        z['queue'] = [self._element(l) for l in self.tage[z['tag']]]
        z['aufwaermen'] = []

    def _offen_am_ende(self):
        for i in self.z['offen_g1']:
            v = self.z['versuche'][i]['kopf']['versuch']
            v['g1'] = 'nicht feststellbar'
            v['entscheidung'].append('G1 nicht feststellbar: kein gültiger Referenzlauf danach')
            if v['rolle'] == 'X_strich':
                v['s1'] = 'nicht prüfbar'
                v['g1_klammer'] = dict(vor=self._v(v['r0'])['id'], nach=None, vorgesehen=False,
                                       grund='kein gültiger Referenzlauf nach X′')
        self.z['offen_g1'] = []

    def _messen(self, el):
        """Führt einen Versuch aus: Kopfangaben zum aktuellen Zeitpunkt, Messung, Protokolleintrag, Zeit fortschreiben."""
        z = self.z
        n = len(z['versuche'])
        spec = dict(el['spec'])
        spec.update(phase=1, position=z['position0'] + n, t_start=z['t'], t_ende=z['t'] + self.T_lauf)
        spec['position_geplant'] = el['spec'].get('position') if el['geplant'] else None
        if not el['geplant']:
            spec['lauf_id'] = f'1-V{n:05d}-{_konfig(spec)}'
        v = dict(id=f'V{n:05d}', index=n, bezug=el['bezug'], bezug_versuch=el.get('bezug_versuch'),
                 geplant=bool(el['geplant']), nummer=int(el['nummer']), rolle=el['rolle'], anlass=el['anlass'],
                 block=spec['block'], messtag=spec['messtag'], kontrollsatz=spec['kontrollsatz'],
                 konfiguration=_konfig(spec), position_geplant=spec['position_geplant'], t_start=spec['t_start'],
                 t_ende=spec['t_ende'], gueltig=None, gruende=[], nicht_pruefbar=[], g1=None, alarm=[],
                 entscheidung=[], halt=None)
        for x in ('alarm_vor', 's3_groessen'):
            if x in el:
                v[x] = el[x]
        kopf, daten = self.messung.messen(spec, v)
        kopf = dict(kopf, versuch=v)
        z['versuche'].append(dict(kopf=kopf, daten=daten))
        z['t'] = spec['t_ende']
        ks = spec['kontrollsatz']
        if ks is not None and str(ks) == str(self.ks['schluss'].get(str(spec['block']))):
            if spec['block'] not in z['schluss_begonnen']:
                z['schluss_begonnen'].append(spec['block'])
        return n

    def _pruefen(self, n):
        """G2–G10 eines Versuchs mit den Schwellen aus Teil B."""
        rec = self.z['versuche'][n]
        t1 = zf.LaufTabelle([rec['kopf']], rec['daten'])
        pr = gueltigkeit.pruefe(t1, self.sw, regeln=REGELN_LAUF)
        v = rec['kopf']['versuch']
        v['gueltig'] = bool(pr['gueltig'][0])
        v['gruende'] = list(pr['gruende'][0])
        v['nicht_pruefbar'] = sorted(g for g, x in pr['nicht_pruefbar'].items() if x)
        return {g: pr['regeln'][g][0] for g in REGELN_LAUF}

    def _wert(self, n, feld):
        return self.z['versuche'][n]['daten'][feld][0]

    def _tmitte(self, n):
        v = self.z['versuche'][n]['kopf']
        return 0.5 * (v['t_start'] + v['t_ende'])

    def _v(self, n):
        return self.z['versuche'][n]['kopf']['versuch']

    def _notiz(self, n, text):
        self._v(n)['entscheidung'].append(text)
        self.z['entscheidungen'].append(dict(versuch=self._v(n)['id'], text=text))

    def _vorn(self, *elemente):
        self.z['queue'][0:0] = list(elemente)

    def _einschub(self, n, rolle, anlass, art=None, **extra):
        """Element eines zusätzlichen Versuchs mit dem Lauf von Versuch n als Vorlage (art='R': Referenzlauf)."""
        k = self.z['versuche'][n]['kopf']
        v = k['versuch']
        spec = {x: k[x] for x in ('laufart', 'modul', 'einstellung', 'konfiguration', 'block', 'messtag',
                                  'kontrollsatz')}
        spec['phase'] = 1
        if art == 'R':
            spec.update(laufart='R', modul=None, einstellung=1, kontrollsatz=None,
                        konfiguration=dict(id='R', gruppe='referenz', phi_soll_grad=None))
        nummer = v['nummer'] + 1 if art is None else 0
        el = dict(spec=spec, rolle=rolle, geplant=False, bezug=v['bezug'] if art is None else None,
                  bezug_versuch=v['id'], nummer=nummer, anlass=anlass)
        el.update(extra)
        return el

    def _halt(self, n, regel, grund, endgueltig=False):
        z = self.z
        if not self.opt.halt:
            self._notiz(n, f'{regel}: {grund} – ohne Halt (Ablaufoption halt aus)')
            return
        self._v(n)['halt'] = regel
        z['halt'] = dict(regel=regel, grund=grund, versuch=self._v(n)['id'], t=z['t'], block=self._v(n)['block'],
                         fortsetzbar=not endgueltig)
        z['status'] = 'abgebrochen' if endgueltig else 'angehalten'
        z['ende'] = dict(status=z['status'], grund=f'{regel}: {grund}')
        self._notiz(n, f'Halt {regel}: {grund}' if not endgueltig else f'Phase 1 beendet ({regel}): {grund}')

    def _wiederaufnahme(self, n):
        """Gehört Versuch n zum Kontrollsatz einer Wiederaufnahme (der ohne Alarm bleiben muss, §9.2)?"""
        return str(self._v(n)['kontrollsatz'] or '').startswith('W')

    def _luecke(self, text):
        if text not in self.z['luecken']:
            self.z['luecken'].append(text)

    # ── Schritt je Versuch ─────────────────────────────────────────────────────────────────────────────
    def _schritt(self, el):
        n = self._messen(el)
        k = self.z['versuche'][n]['kopf']
        if k['einstellung'] == 2:            # beide Lücken, sobald ein L′ läuft (S4 für L′ wird ebenfalls nicht geprüft)
            for t in LUECKEN_E2:
                self._luecke(t)
        if el['rolle'] == 'aufwaermen':
            self._aufwaermen(n)
        elif k['laufart'] == 'R':
            self._referenz(n)
        else:
            self._lauf(n)

    def _aufwaermen(self, n):
        z = self.z
        self._pruefen(n)
        v = self._v(n)
        z['aufwaermen'].append(n)
        if v['gueltig']:
            self._gueltige_referenz(n)
        if not self.opt.aufwaermen:
            return
        a = z['aufwaermen']
        if len(a) >= 2 and all(self._v(i)['gueltig'] for i in a[-2:]):
            d = abs(self._wert(a[-1], 'N_mittel') - self._wert(a[-2], 'N_mittel'))
            if d < self.sw.sigma_ref or d <= gueltigkeit.RUNDUNG_REL * abs(self._wert(a[-1], 'N_mittel')):
                self._notiz(n, f'Aufwärmen abgeschlossen nach {len(a)} Läufen (|Δ⟨N⟩| < σ̂_ref)')
                return
        if len(a) >= GRENZE_AUFWAERMEN:
            self._halt(n, 'Aufwärmen', f'nach {len(a)} Läufen keine zwei aufeinanderfolgenden innerhalb σ̂_ref (§6)')
            return
        self._vorn(self._einschub(n, 'aufwaermen', 'Aufwärmen (§6)', art='R'))

    def _referenz(self, n):
        z = self.z
        v = self._v(n)
        self._pruefen(n)
        kontroll_r = v['rolle'] in ('kontrolle', 'kontrollwiederholung', 'wiederaufnahme_kontrolle') or (
            v['rolle'] == 'alarmwiederholung' and v['kontrollsatz'] is not None)
        if not v['gueltig']:
            if kontroll_r:
                self._kontrolle_ungueltig(n, f'ungültig ({", ".join(v["gruende"])})')
            else:
                self._notiz(n, f'Referenzlauf ungültig ({", ".join(v["gruende"])}): kein Bezug, keine Wiederholung')
            return
        if z['r0'] is not None:
            r0 = z['r0']
            kan = gueltigkeit.alarm_kanaele(self.sw, self._wert(n, 'N_mittel'), self._wert(n, 'N_mittel_zellen'),
                                            self._wert(r0, 'N_mittel'), self._wert(r0, 'N_mittel_zellen'))
        else:
            kan = []
        if kan:
            v['alarm'] = kan
            v['gueltig'] = False
            v['gruende'] = ['G1']
            vorher = v.get('alarm_vor') or []
            if set(kan) & set(vorher):
                self._halt(n, 'S1', f'reproduzierter Nullpunktalarm ({", ".join(sorted(set(kan) & set(vorher)))})')
                return
            if self._wiederaufnahme(n):
                self._halt(n, 'Wiederaufnahme', f'Nullpunktalarm ({", ".join(kan)}) im Kontrollsatz der Wiederaufnahme')
                return
            if not self.opt.wiederholungen:
                self._notiz(n, f'Nullpunktalarm ({", ".join(kan)}) – keine Wiederholung (Ablaufoption)')
                return
            if kontroll_r:
                self._kontrolle_ungueltig(n, f'Nullpunktalarm ({", ".join(kan)})', alarm=kan)
                return
            z['alarmkette'] += 1
            if z['alarmkette'] > GRENZE_ALARMKETTE:
                self._halt(n, 'Nullpunktalarm', f'mehr als {GRENZE_ALARMKETTE} Alarmwiederholungen ohne Regelausgang '
                                                '(technische Grenze)')
                return
            self._notiz(n, f'Nullpunktalarm ({", ".join(kan)}): sofortige Wiederholung (§8.8)')
            self._vorn(self._einschub(n, 'alarmwiederholung', f'Nullpunktalarm {", ".join(kan)}', art='R',
                                      alarm_vor=kan))
            return
        if v.get('alarm_vor'):
            self._notiz(n, 'Alarm nicht reproduziert: die Wiederholung ersetzt den alarmierten Referenzlauf')
        z['alarmkette'] = 0
        self._gueltige_referenz(n)

    def _gueltige_referenz(self, n):
        """n ist gültiger Referenzlauf: G1 aller offenen Läufe steht fest; n wird R₀."""
        z = self.z
        offen, z['offen_g1'] = z['offen_g1'], []
        einschuebe = []
        for i in offen:
            vi = self._v(i)
            dN, _ = gueltigkeit.interpolation(self._wert(i, 'N_mittel'), self._tmitte(i),
                                              self._wert(vi['r0'], 'N_mittel'), self._tmitte(vi['r0']),
                                              self._wert(n, 'N_mittel'), self._tmitte(n))
            verl = gueltigkeit.g1_verletzt(dN, self._wert(i, 'N_mittel'), self.sw.eps_ctrl)
            vi['g1'] = bool(verl)
            vi['g1_bezug'] = [self._v(vi['r0'])['id'], self._v(n)['id']]
            if vi['rolle'] == 'X_strich':
                vi['g1_klammer'] = self._klammer_x(i, vi['r0'], n)
                if not verl and not vi['g1_klammer']['vorgesehen']:
                    self._notiz(i, f'G1 von X′ gegen {vi["g1_bezug"][0]}/{vi["g1_bezug"][1]} eingehalten; Klammer R₂/R₃ '
                                   f'unvollständig ({vi["g1_klammer"]["grund"]}): S1 nicht prüfbar')
            if not verl:
                continue
            vi['gueltig'] = False
            vi['gruende'] = sorted(set(vi['gruende']) | {'G1'}, key=gueltigkeit.REGELN_G.index)
            einschuebe += self._g1_verstoss(i)
        z['r0'] = n
        if einschuebe:
            self._vorn(*einschuebe)

    def _vor_schluss(self, i):
        """Steht für Versuch i der Schlusskontrollsatz seines Blocks noch bevor?"""
        v = self._v(i)
        if v['kontrollsatz'] is not None and self.ks['saetze'].get(str(v['kontrollsatz']), {}).get('schluss'):
            return False
        return v['block'] is not None and v['block'] not in self.z['schluss_begonnen']

    def _g1_verstoss(self, i):
        """Feststehender G1-Verstoß von Versuch i: R₂, X′, R₃ (vor Beginn des Schlusskontrollsatzes) oder S1."""
        v = self._v(i)
        k = self.z['versuche'][i]['kopf']
        if k['laufart'] == 'L' and k['einstellung'] == 2:
            self._luecke(LUECKEN_E2[1])
            self._notiz(i, 'G1-Verstoß eines L′: S1 für L′ offen (§12), keine Wiederholung')
            return []
        if v['rolle'] == 'X_strich':
            kl = v.get('g1_klammer') or {}
            if kl.get('vorgesehen'):
                self._halt(i, 'S1', f'G1-Verstoß der Wiederholung X′ gegen R₂/R₃ ({kl["vor"]}/{kl["nach"]})')
            else:
                v['s1'] = 'nicht prüfbar'
                self._notiz(i, f'G1-Verstoß von X′ gegen {kl.get("vor")}/{kl.get("nach")}; Klammer R₂/R₃ unvollständig '
                               f'({kl.get("grund")}): S1 nicht prüfbar, keine weitere Wiederholung')
            return []
        if not self._vor_schluss(i):
            v['spaet_erkannt'] = True
            self._notiz(i, 'G1-Verstoß erst nach Beginn des Schlusskontrollsatzes festgestellt: keine Wiederholung, '
                           'keine S1-Prüfung')
            return []
        if not self.opt.wiederholungen:
            self._notiz(i, 'G1-Verstoß – keine Wiederholung (Ablaufoption)')
            return []
        key = self._wdh_schluessel(i)
        zaehler = self.z['kwdh'] if k['laufart'] != 'K' else self.z['wdh']
        zaehler[key] = zaehler.get(key, 0) + 1
        self._notiz(i, f'G1-Verstoß vor Beginn des Schlusskontrollsatzes: R₂, X′, R₃ (Wiederholung {zaehler[key]})')
        return [self._einschub(i, 'R2', f'G1 {v["id"]}', art='R'),
                self._einschub(i, 'X_strich', f'G1 {v["id"]}'),
                self._einschub(i, 'R3', f'G1 {v["id"]}', art='R')]

    def _wdh_schluessel(self, i):
        v = self._v(i)
        if v['kontrollsatz'] is not None:
            return _schluessel(v['kontrollsatz'], v['konfiguration'])
        return _schluessel(v['konfiguration'], v['block'])

    def _wurzel(self, n):
        """Ursprünglicher Referenzversuch einer Kette von Alarmwiederholungen: Eine nicht reproduzierte Wiederholung
        ersetzt den alarmierten Lauf (§8.8)."""
        v = self._v(n)
        while v['rolle'] == 'alarmwiederholung' and v.get('bezug_versuch'):
            v = self._v(int(v['bezug_versuch'][1:]))
        return v

    def _klammer_x(self, i, a, b):
        """Klammer von X′ (Versuch i) aus den Referenzläufen a (vorher) und b (nachher): vorgesehen nur, wenn a das R₂
        und b das R₃ desselben G1-Falls sind, gegebenenfalls ersetzt durch nicht reproduzierte Alarmwiederholungen."""
        x = self._v(i).get('bezug_versuch')
        ra, rb = self._wurzel(a), self._wurzel(b)
        ok_a = ra['rolle'] == 'R2' and ra.get('bezug_versuch') == x
        ok_b = rb['rolle'] == 'R3' and rb.get('bezug_versuch') == x
        grund = None if ok_a and ok_b else '; '.join(
            ([] if ok_a else [f'Bezug vor X′ ist {ra["id"]} ({ra["rolle"]}), nicht R₂ des Falls {x}']) +
            ([] if ok_b else [f'Bezug nach X′ ist {rb["id"]} ({rb["rolle"]}), nicht R₃ des Falls {x}']))
        return dict(vor=self._v(a)['id'], nach=self._v(b)['id'], vorgesehen=bool(ok_a and ok_b), grund=grund)

    def _lauf(self, n):
        """Lauf mit bewegten Modulen (Konfiguration oder Kontrolllauf Lⱼ, Lⱼ′)."""
        z = self.z
        v = self._v(n)
        k = z['versuche'][n]['kopf']
        strich = k['laufart'] == 'L' and k['einstellung'] == 2
        reg = self._pruefen(n)
        # S4 (G2 in zwei aufeinanderfolgenden Läufen mit bewegten Modulen) und S2
        s4 = reg['G2'] is True and z['s4_vor'] and not strich
        z['s4_vor'] = reg['G2'] is True
        s2 = reg['G6'] is True and not any(reg[g] is True for g in ('G5', 'G8', 'G10'))
        if s2 and strich:
            self._luecke(LUECKEN_E2[1])
            self._notiz(n, 'Einzelzell-Liftoff in L′: S2 für L′ offen (§12), nicht angewandt')
            s2 = False
        if not v['gueltig']:
            if k['laufart'] == 'K':
                self._konfiguration_ungueltig(n)
            else:
                self._kontrolle_ungueltig(n, f'ungültig ({", ".join(v["gruende"])})')
        elif strich:
            v['r0'] = z['r0']
            if z['r0'] is not None:
                z['offen_g1'].append(n)
        else:
            v['r0'] = z['r0']
            if z['r0'] is not None:
                z['offen_g1'].append(n)
                d = abs(self._wert(n, 'N_mittel') - self._wert(z['r0'], 'N_mittel'))
                # X′ hat seine Klammer R₂/R₃ (§9.2, A9.12); eine Vorprüfung mit R₁ würde sie ersetzen
                if v['rolle'] != 'X_strich' and self.opt.wiederholungen and \
                        gueltigkeit.g1_verletzt(d, self._wert(n, 'N_mittel'), self.sw.eps_ctrl):
                    self._notiz(n, 'Vorprüfung gegen R₀: |Δ⟨N⟩| > ε_ctrl → sofort R₁')
                    self._vorn(self._einschub(n, 'R1', f'Vorprüfung {v["id"]}', art='R'))
            if k['laufart'] == 'L' and k['einstellung'] == 1:
                self._s3(n)
        if s2:                                     # S2 wird immer gezählt, auch wenn schon ein anderer Halt vorliegt
            self._s2(n, halten=z['status'] == 'laufend')
        if s4 and z['status'] == 'laufend':
            self._halt(n, 'S4', 'G2 in zwei aufeinanderfolgenden Läufen')

    def _konfiguration_ungueltig(self, n):
        z = self.z
        v = self._v(n)
        if not self.opt.wiederholungen:
            self._notiz(n, 'ungültig – keine Wiederholung (Ablaufoption)')
            return
        if not self._vor_schluss(n):
            v['spaet_erkannt'] = True
            self._notiz(n, 'ungültig nach Beginn des Schlusskontrollsatzes erkannt: keine Wiederholung')
            return
        key = self._wdh_schluessel(n)
        if z['wdh'].get(key, 0) >= GRENZE_KONFIGURATION:
            v['grenze'] = True
            self._notiz(n, f'ungültig ({", ".join(v["gruende"])}); Grenze von {GRENZE_KONFIGURATION} Wiederholungen je '
                           'Konfiguration und Block ausgeschöpft')
            return
        z['wdh'][key] = z['wdh'].get(key, 0) + 1
        el = self._einschub(n, 'wiederholung', f'ungültig ({", ".join(v["gruende"])})')
        pos = self._platz(n)
        z['queue'].insert(pos, el)
        self._notiz(n, f'ungültig ({", ".join(v["gruende"])}): Wiederholung {z["wdh"][key]} am gezogenen Platz')

    def _platz(self, n):
        """Wiederholungsplatz im Block des Versuchs n: gleichverteilt unter den m offenen Konfigurationsläufen
        (geplante und bereits eingefügte Wiederholungen, nicht die sofortigen Einschübe) und dem Platz vor dem
        Schlusskontrollsatz; Ziehung mit dem Reihenfolgegenerator, protokolliert."""
        z = self.z
        b = self._v(n)['block']
        q = z['queue']
        offen = [i for i, el in enumerate(q) if el['spec']['laufart'] == 'K' and el['spec']['block'] == b
                 and el['rolle'] in ('konfiguration', 'wiederholung')]
        sks = self.ks['schluss'].get(str(b))
        ende = next((i for i, el in enumerate(q) if sks is not None and str(el['spec']['kontrollsatz']) == str(sks)),
                    len(q))
        m = len(offen)
        j = int(self.rng.integers(0, m + 1))
        pos = offen[j] if j < m else ende
        z['ziehungen'].append(dict(versuch=self._v(n)['id'], block=b, konfiguration=self._v(n)['konfiguration'],
                                   m=m, gezogen=j, plaetze=m + 1, einfuege_index=pos,
                                   vor=(q[pos]['spec']['lauf_id'] if q[pos]['geplant'] else
                                        f'Wiederholung von {q[pos]["bezug"]}') if j < m else 'Schlusskontrollsatz',
                                   regel='rng.integers(0, m + 1) des Reihenfolgegenerators'))
        return pos

    def _kontrolle_ungueltig(self, n, anlass, alarm=None):
        """Ungültiger Kontrolllauf (anderer Grund als G1): sofort wiederholt, höchstens zweimal; dann Halt, bei L′
        fehlt der Lauf. Rückgabe True bei Halt."""
        z = self.z
        v = self._v(n)
        k = z['versuche'][n]['kopf']
        strich = k['laufart'] == 'L' and k['einstellung'] == 2
        if not self.opt.wiederholungen:
            self._notiz(n, f'Kontrolllauf {anlass} – keine Wiederholung (Ablaufoption)')
            return False
        key = self._wdh_schluessel(n)
        if z['kwdh'].get(key, 0) >= GRENZE_KONTROLLE:
            v['grenze'] = True
            if strich:
                self._notiz(n, f'L′ {anlass} nach {GRENZE_KONTROLLE} Wiederholungen: fehlt, ohne Halt (A9.12)')
                return False
            self._halt(n, 'Kontrolllauf', f'{v["konfiguration"]} nach {GRENZE_KONTROLLE} Wiederholungen ungültig '
                                          f'({anlass})')
            return True
        z['kwdh'][key] = z['kwdh'].get(key, 0) + 1
        extra = dict(alarm_vor=alarm) if alarm else {}
        if v.get('s3_groessen'):
            extra['s3_groessen'] = v['s3_groessen']
        self._notiz(n, f'Kontrolllauf {anlass}: sofortige Wiederholung {z["kwdh"][key]}')
        self._vorn(self._einschub(n, 'kontrollwiederholung', anlass, **extra))
        return False

    def _s3(self, n):
        z = self.z
        v = self._v(n)
        b = self.s3.get(str(z['versuche'][n]['kopf']['modul']))
        if not b:
            return
        X = kv.h1_vektor(z['versuche'][n]['daten']['Nk_summe'][:, :self.sw.kmax])[0]
        mu = np.asarray(b['mu'], float)
        boden = gueltigkeit.RUNDUNG_REL * np.abs(mu)                     # Rundungsboden wie gueltigkeit (technisch)
        ueber = [kv.GROESSEN_H1[q] for q in np.flatnonzero(np.abs(X - mu) > np.asarray(b['schwelle']) + boden)]
        v['s3_ueber'] = ueber
        vorher = v.get('s3_groessen')
        if vorher:
            gleich = sorted(set(ueber) & set(vorher))
            if gleich:
                self._halt(n, 'S3', f'Drift der Einzelmodulreferenz reproduziert ({", ".join(gleich)})')
            else:
                self._notiz(n, 'S3 nicht reproduziert')
            return
        if ueber and self._wiederaufnahme(n):
            self._halt(n, 'Wiederaufnahme', f'S3-Überschreitung ({", ".join(ueber)}) im Kontrollsatz der Wiederaufnahme')
            return
        if ueber and self.opt.wiederholungen:
            self._notiz(n, f'S3-Überschreitung ({", ".join(ueber)}): sofortige Wiederholung')
            self._vorn(self._einschub(n, 's3_wiederholung', f'S3 {", ".join(ueber)}', s3_groessen=ueber))

    def _s2(self, n, halten=True):
        """S2 an Versuch n: Ausschluss der Konfiguration (bleibt auch nach einem festgestellten Apparaturfehler), Halt;
        maßgeblich für das Ende von Phase 1 ist die S2-Bilanz aus den S2-Versuchen und den Ursachenanalysen
        (gueltigkeit.s2_bilanz, offline gleich)."""
        z = self.z
        v = self._v(n)
        z['s2'].append(v['id'])
        k = z['versuche'][n]['kopf']
        if k['laufart'] == 'K' and v['konfiguration'] not in z['ausgeschlossen']:
            z['ausgeschlossen'].append(v['konfiguration'])
        bil = gueltigkeit.s2_bilanz(z['s2'], z['ereignisse'])
        z['s2_zaehler'] = len(bil['massgeblich'])
        if bil['beendet']:
            if not halten:
                self._notiz(n, f'zweites S2 ohne festgestellten Apparaturfehler während des Halts '
                               f'{(z["halt"] or {}).get("regel")}: Phase 1 endet')
            self._halt(n, 'S2', 'zweites S2 ohne festgestellten Apparaturfehler', endgueltig=True)
        elif not halten:
            self._notiz(n, 'S2 während eines anderen Halts: gezählt, kein eigener Halt; die Ursachenanalyse dieses Halts '
                           'gilt auch für das S2')
        elif k['laufart'] == 'K':
            self._halt(n, 'S2', f'Einzelzell-Liftoff in {v["konfiguration"]}; die Konfiguration bleibt in den Blöcken '
                                'und ist von Tests ausgeschlossen')
        else:
            self._halt(n, 'S2', f'Einzelzell-Liftoff im Kontrolllauf {v["konfiguration"]}; ŷ¹ ungültig (§8.2)')

    # ── Wiederaufnahme ─────────────────────────────────────────────────────────────────────────────────
    def fortsetzen(self, ereignis):
        """Wiederaufnahme nach einem Halt mit einem ausdrücklich protokollierten externen Ereignis
        dict(art='wiederaufnahme', quelle, zeitpunkt (s, nicht vor dem Halt), befund, mechanischer_eingriff (bool),
        apparaturfehler (bool)). Danach ein vollständiger Kontrollsatz in gezogener Reihenfolge, dann der unterbrochene
        Block."""
        z = self.z
        if z['status'] != 'angehalten':
            raise AblaufFehler(f'Wiederaufnahme nur nach einem Halt (Status {z["status"]})')
        pflicht = gueltigkeit.WIEDERAUFNAHME_PFLICHT
        if not isinstance(ereignis, dict) or any(x not in ereignis for x in pflicht) or \
                ereignis['art'] != 'wiederaufnahme':
            raise AblaufFehler(f'Wiederaufnahme verlangt ein externes Ereignis mit {", ".join(pflicht)}')
        if not all(isinstance(ereignis[x], bool) for x in ('mechanischer_eingriff', 'apparaturfehler')):
            raise AblaufFehler('Wiederaufnahme: mechanischer_eingriff und apparaturfehler ausdrücklich als wahr oder '
                               'falsch angeben')
        if float(ereignis['zeitpunkt']) < z['t']:
            raise AblaufFehler('Wiederaufnahme vor dem Halt')
        if ereignis['mechanischer_eingriff']:
            raise AblaufFehler('Wiederaufnahme nach mechanischem Eingriff: Vergleich von n₀ Einzelmodulläufen je Modul '
                               'mit Phase 0 (§9.2, Testlogik offen, §12) nicht umgesetzt')
        z['ereignisse'].append(dict(ereignis, halt=z['halt']))
        z['s2_zaehler'] = len(gueltigkeit.s2_bilanz(z['s2'], z['ereignisse'])['massgeblich'])
        z['t'] = float(ereignis['zeitpunkt'])
        z['wiederaufnahmen'] += 1
        b = z['halt']['block']
        ks = f'W{z["wiederaufnahmen"]}'
        vorlage = next(l for l in self.geplant if l['kontrollsatz'] is not None)
        mitglieder = []
        for l in self.geplant:
            if l['kontrollsatz'] == vorlage['kontrollsatz']:
                mitglieder.append(l)
        ordnung = self.rng.permutation(len(mitglieder))
        z['ziehungen'].append(dict(art='Wiederaufnahme', kontrollsatz=ks, reihenfolge=[int(i) for i in ordnung],
                                   regel='rng.permutation des Reihenfolgegenerators'))
        els = []
        for i in ordnung:
            l = mitglieder[int(i)]
            spec = {x: l[x] for x in ('laufart', 'modul', 'einstellung', 'konfiguration', 'messtag')}
            spec.update(phase=1, block=b, kontrollsatz=ks, lauf_id=None, position=None)
            els.append(dict(spec=spec, rolle='wiederaufnahme_kontrolle', geplant=False, bezug=None, nummer=0,
                            anlass=f'Wiederaufnahme {z["wiederaufnahmen"]}'))
        self.ks['saetze'][ks] = dict(block=b, schluss=False)
        z['queue'][0:0] = els
        z['halt'] = None
        z['ende'] = None
        z['status'] = 'bereit'
        return self.ausfuehren()

    # ── Ergebnis ───────────────────────────────────────────────────────────────────────────────────────
    def tabelle(self):
        """Laufzusammenfassungen aller ausgeführten Versuche der Phase 1 (LaufTabelle) in Ausführungsreihenfolge; meta
        nennt Version, Status und Kennung des Ablaufs."""
        vs = self.z['versuche']
        if not vs:
            raise AblaufFehler('keine Versuche')
        daten = {f: np.concatenate([np.asarray(v['daten'][f]) for v in vs]) for f in vs[0]['daten']}
        return zf.LaufTabelle([v['kopf'] for v in vs], daten, meta=dict(ablauf=self.kurz()))

    def kurz(self):
        """Ablaufstand für die Tabelle (meta „ablauf“): Status, Halt, Kennung, Optionen, Lücken und die Angaben, aus
        denen Stufe 2 die S2-Bilanz selbst nachrechnet (S2-Versuche, protokollierte Wiederaufnahmen mit ihrem Halt)."""
        z = self.z
        return dict(version=VERSION, status=z['status'], ende=z['ende'], halt=z['halt'], kennung=self.kennung,
                    optionen=asdict(self.opt), luecken=list(z['luecken']), s2=list(z['s2']),
                    ereignisse=copy.deepcopy(z['ereignisse']), s2_bilanz=gueltigkeit.s2_bilanz(z['s2'], z['ereignisse']))

    def zustand(self):
        """Vollständiger Ablaufstand (für Checkpoints): alle Versuche mit Daten, Warteschlange, Zähler, Generator."""
        z = copy.deepcopy(self.z)
        z['rng'] = self.rng.bit_generator.state
        z['ks'] = copy.deepcopy(self.ks)
        z['kennung'] = self.kennung
        z['optionen'] = asdict(self.opt)
        return z

    @classmethod
    def aus_zustand(cls, zustand, geplant, messung, sw, s3, rng, T_lauf, tag_pause, kennung):
        """Fortsetzung aus einem gespeicherten Ablaufstand; Kennung und Optionen müssen übereinstimmen."""
        if formate.sha256_json(zustand.get('kennung')) != formate.sha256_json(kennung):
            raise AblaufFehler('Ablaufstand mit anderer Kennung (Verfahren, Optionen, Seeds, Teil B oder Plan): keine '
                               'Fortsetzung')
        if zustand.get('version') != VERSION:
            raise AblaufFehler(f'Ablaufstand der Version {zustand.get("version")} ≠ {VERSION}')
        z = copy.deepcopy(zustand)
        rng.bit_generator.state = z.pop('rng')
        ks = z.pop('ks')
        opt = Ablaufoptionen(**z.pop('optionen'))
        z.pop('kennung')
        for v in z['versuche']:
            v['daten'] = {f: np.asarray(x) for f, x in v['daten'].items()}
        a = cls(geplant, messung, sw, s3, rng, opt, T_lauf, tag_pause, kennung, _zustand=z)
        a.ks = ks
        return a

    def bericht(self):
        """Ablaufbericht je Kampagne: Status, Laufzahl und Messdauer (geplant/realisiert), Versuche nach Rolle und
        Anlass, Auswahl/Ersatz/Fehlen je Konfiguration und Block, Kontrollläufe, ausgeschöpfte Grenzen, Ziehungen."""
        return bericht(self)


def bericht(a):
    z = a.z
    vs = [v['kopf']['versuch'] for v in z['versuche']]
    geplant = a.geplant
    T = a.T_lauf
    t_plan = (geplant[-1]['t_ende'] - geplant[0]['t_start']) if geplant else 0.0
    t_real = (vs[-1]['t_ende'] - vs[0]['t_start']) if vs else 0.0
    rollen, anlaesse = {}, {}
    for v in vs:
        rollen[v['rolle']] = rollen.get(v['rolle'], 0) + 1
        if not v['geplant']:
            a_ = v['anlass'].split(' ')[0] if v['rolle'] in ('R1', 'R2', 'R3', 'X_strich') else v['anlass']
            anlaesse[f'{v["rolle"]}: {a_}'] = anlaesse.get(f'{v["rolle"]}: {a_}', 0) + 1
    # Auswahl je Konfiguration und Block
    plaetze = {}
    for l in geplant:
        if l['laufart'] == 'K':
            plaetze[_schluessel(_konfig(l), l['block'])] = dict(konfiguration=_konfig(l), block=l['block'],
                                                                 geplant=l['lauf_id'], versuche=[], gueltig=[])
    for v in vs:
        if v['konfiguration'] in ('R',) or z['versuche'][v['index']]['kopf']['laufart'] != 'K':
            continue
        p = plaetze.get(_schluessel(v['konfiguration'], v['block']))
        if p is None:
            continue
        p['versuche'].append(v['id'])
        if v['gueltig'] and v['g1'] is not True:
            p['gueltig'].append(v['id'])
    auswahl = {}
    for key, p in plaetze.items():
        vv = [vs[int(x[1:])] for x in p['versuche']]
        if len(p['gueltig']) > 1:
            status = 'doppelt'
        elif p['gueltig']:
            status = 'gueltig' if p['gueltig'][0] == (vv[0]['id'] if vv else None) else 'ersetzt'
        elif not vv:
            status = 'nicht gemessen'
        elif any(x.get('halt') for x in vv):                          # ein Versuch dieses Platzes hielt an
            status = 'fehlt: Halt'
        elif any(x.get('grenze') for x in vv):
            status = 'fehlt: Grenze ausgeschöpft'
        elif any(x.get('spaet_erkannt') for x in vv):                  # Ungültigkeit nach Beginn des Schlusssatzes
            status = 'fehlt: spät erkannt'
        elif any(x.get('s1') == 'nicht prüfbar' for x in vv):         # X′ ohne vollständige Klammer R₂/R₃
            status = 'fehlt: S1 nicht prüfbar'
        elif z['status'] != 'abgeschlossen':
            status = 'fehlt: Halt'
        else:
            status = 'fehlt'
        if p['konfiguration'] in z['ausgeschlossen'] and status in ('gueltig', 'ersetzt'):
            status = status + ', S2-ausgeschlossen'
        auswahl[key] = dict(konfiguration=p['konfiguration'], block=p['block'], status=status,
                            ausgewaehlt=p['gueltig'][0] if len(p['gueltig']) == 1 else None, versuche=p['versuche'])
    zaehl = {}
    for x in auswahl.values():
        s = x['status'].split(',')[0]
        zaehl[s] = zaehl.get(s, 0) + 1
    # Kontrollläufe je Modul
    kontrolle = {}
    for v in vs:
        k = z['versuche'][v['index']]['kopf']
        if k['laufart'] == 'L':
            name = v['konfiguration']
            e = kontrolle.setdefault(name, dict(versuche=0, gueltig=0, fehlt=0))
            e['versuche'] += 1
            e['gueltig'] += int(bool(v['gueltig']) and v['g1'] is not True)
            e['fehlt'] += int(bool(v.get('grenze')))
    return dict(
        version=VERSION, status=z['status'], ende=z['ende'], halt=z['halt'], optionen=asdict(a.opt),
        laufzahl=dict(geplant=len(geplant), geplant_ausgefuehrt=sum(bool(v['geplant']) for v in vs),
                      ausgefuehrt=len(vs), zusaetzlich=sum(not v['geplant'] for v in vs)),
        messzeit_s=dict(geplant_laeufe=len(geplant) * T, realisiert_laeufe=len(vs) * T, geplant_spanne=t_plan,
                        realisiert_spanne=t_real,
                        hinweis='Laufzeit = Zahl der Läufe × T_Lauf; Spanne vom ersten bis zum letzten Lauf der Phase 1 '
                                'einschließlich Tagespausen. Die normative Zeitformel (§5.3 c) bleibt unverändert.'),
        rollen=rollen, anlaesse=anlaesse, auswahl_zaehler=zaehl, auswahl=auswahl, kontrolllaeufe=kontrolle,
        grenzen=[v['id'] for v in vs if v.get('grenze')], ziehungen=list(z['ziehungen']), s2=list(z['s2']),
        ausgeschlossen=list(z['ausgeschlossen']), luecken=list(z['luecken']), ereignisse=list(z['ereignisse']),
        halte=[dict(versuch=v['id'], regel=v['halt']) for v in vs if v.get('halt')],
        qualifikation_einstellung2='ausgeschlossen' if z['luecken'] else 'nicht betroffen')


def speichern(pfad, a, kennung='SYNTH-ABLAUFSTAND'):
    """Ablaufstand als Datei (JSON-Skelett und NPZ der Versuchsdaten)."""
    return formate.schreibe_objekt(pfad, formate.kopf('ablaufstand', kennung), a.zustand())


def laden(pfad):
    return formate.lies_objekt(pfad, 'ablaufstand')[1]


def kurz(b):
    """Kompakter Ablaufbericht je Kampagne für Harness und Planung (ohne Versuchslisten)."""
    return dict(status=b['status'], halt=(b['halt'] or {}).get('regel'), grund=(b['ende'] or {}).get('grund'),
                laufzahl=b['laufzahl'], messzeit_s={k: v for k, v in b['messzeit_s'].items() if k != 'hinweis'},
                anlaesse=b['anlaesse'], auswahl=b['auswahl_zaehler'], grenzen=len(b['grenzen']), s2=len(b['s2']),
                luecken=b['luecken'], ziehungen=sum(1 for x in b['ziehungen'] if 'gezogen' in x))
