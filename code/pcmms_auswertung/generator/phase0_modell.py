"""Strukturmodell aus Phase 0 (Teil d1/d2): Rauschparameter je Modul und Komponente, Strukturquellen und ein Generator
auf Ebene H, der den Szenariogenerator (ebene_h) als Sonderfall enthält.

Parameter (Strukturparameter, eingefroren; Skalare gelten für alle Module bzw. Zellen, Tupel je Modul (3) bzw. je
Modul 2 und 3 (2) bzw. je Zelle (3)):
  sigma_zelle, sigma_h_zelle, sigma_m_zelle  Boden je Zelle als Abtastwert-Äquivalent bei f_s_bezug: Rohstreuung σ_c
                       (Rohextrema, sigma_roh), Harmonische σ_h = s_h·√(2/(f_s·T_a)), Boden von ⟨N_c⟩
                       σ_m = s_m/√(f_s·T_a) (weiß über die Zyklen; None: wie sigma_zelle, Szenariofamilie)
  amp, phase_grad      je Laufart (L, K): Streuung der Modulamplitude [1] und des nicht erfassten Phasenrests [°] je
                       bewegtem Modul (Skalar oder je Modul)
  jitter_grad          Jitter je Zyklus der Module 2, 3 gegen Modul 1 [°] (erfasst über die Zeiger)
  index_versatz_grad   Versatz der Laufmittel der Indexphasen [°] (erfasst)
  nullpunkt_drift_N_je_s, lauf_drift_N, t_phi_s, f_streuung_hz, temperatur_C  wie rauschen.Rauschmodell
  Erweiterungen des Strukturmodells (Vorgabe 0, d. h. Szenariofamilie):
  versatz_korrelation  Korrelation der Laufversätze der Module 2 und 3
  jitter_korrelation   Korrelation des Jitters der Module 2 und 3 je Zyklus (Sensitivität)
  jitter_ar1           AR(1)-Koeffizient des Jitters über die Zyklen (farbiger Jitter, Sensitivität)
  jitter_last          lastabhängiger Jitter: σ·(1 + λ·q₁(φ)), q₁ = |Σⱼ e^{−iφⱼ}N̄ⱼ,₁|/Σⱼ|N̄ⱼ,₁| (Sensitivität)
  phasendrift_grad     lineare Drift der Indexphasen im Kombinationslauf je Modul [° über den Lauf] (erfasst)
  phase_gemeinsam_K    gemeinsame Laufzeitschwankung der Kette statt modulweisem δ in Kombinationsläufen
  rest_N               orthogonaler Rest je Modul, Zelle, Harmonischer (3, 3, k) [N je Re/Im], laufweise, vor der
                       Kette; in Kombinationsläufen mit den Zeigern des Laufs übertragen
  nullpunkt_diffusion_N2_je_s  Zufallspfad des Nullpunkts der Summe [N²/s] (zu den Laufzeitpunkten)
  nullpunkt_zeit       Zeitachse von Nullpunktdrift und Zufallspfad: 'global' (Kampagnenuhr mit Pausen, wie der
                       Szenariogenerator) oder 'betriebszeit' ((Position + ½)·T_Lauf, ohne Pausen zwischen Messtagen
                       und Phasen: Phase 0 enthält keine Pause, die Drift über eine Pause ist nicht identifizierbar)
  nullpunkt_sprung_sd_N  zufälliger Nullpunktsprung je Abschnitt (Phase, Messtag) [N] (Sensitivität drift_messtage)
  lauf_drift_sd_N      Streuung der Drift von ⟨N⟩ im Lauf je Lauf [N] (Fünftel ∓0,4·d)
  laufintern_amp_sd/_mittel, laufintern_phase_sd_grad/_mittel_grad  Änderung von Amplitude [1] und Phasenrest [°]
                       zwischen erstem und letztem Fünftel je Modul (lineare Änderung im Lauf, Laufmittel unverändert)

Generator (erzeuge): dieselben Gruppen, dieselbe Reihenfolge und dieselben Ziehungen aus dem Hauptstrom wie
ebene_h.erzeuge; Erweiterungen ohne eigene Ziehung (Korrelationen, AR(1), Last, Phasendrift, gemeinsames δ) formen
die Ziehungen des Hauptstroms um, Erweiterungen mit eigener Ziehung (Rest, Zufallspfad, Laufdriftstreuung,
Fünftelanteile) ziehen aus einem getrennten Strom rng_zusatz (ausdrücklich zu übergeben). Mit einem
rauschen.Rauschmodell bzw. aus_rauschmodell(…) und dem Generatormodell eines Szenarios entsteht deshalb genau die
Tabelle von ebene_h.erzeuge (Modus „bekannt“, bitgleich geprüft); mit geschätzten Parametern gilt nur die
Wiedergewinnung im Rahmen der Schätzunsicherheit (Rundreise).

Strukturquellen: struktur_p08 (Einzelmodul-Mittelkurven N̄⁽ʲ⁾ je Zelle der gültigen Lⱼ-Läufe am Arbeitspunkt,
statische Lasten aus den R-Läufen), struktur_kalibrierung (Werkzeug-2-Struktur in der 1-FG-Fassung aus P0.1–P0.5
für Kandidatenfrequenzen: N_c,k⁽ʲ⁾ = w_cj·G_F,c(kf)·m_j·H(kf)·a_k⁽ʲ⁾, a_k = −(2πfk)²·x_k; Kippmoden vernachlässigt wie
H3), struktur_system (Werkzeug 2 mit bekannten Systemparametern, nur Vergleich). Phase0Modell verbindet Struktur,
Plan, Δδ̂ⱼ aus P0.5 und Parameter zu einem Generatormodell ohne Szenario (exakte Superposition der Struktur); seine
Wahrheit ist die der Struktur selbst, nicht die eines Szenarios.

Parameter aus Phase 0: aus_laufgroessen (Strukturmodell, Regel rauschmodelle: standard; Punktschätzer oder obere
80-%-Grenze je identifizierbarer Komponente mit einem gemeinsamen Faktor für den Boden von ⟨N⟩ aller Laufarten;
nicht identifizierbare Komponenten 0 und benannt), familienanpassung (eingebettete Alternative: Szenariofamilie mit
gepoolten Momentenschätzern), benannte Sensitivitäten mit festen Stärken (SENSITIVITAETEN). Ein Residuen-Bootstrap
(Regel rauschmodelle: bootstrap optional) ist nicht umgesetzt.
"""
from dataclasses import asdict, dataclass, field, replace

import numpy as np

from .. import anpassung, formate, konventionen as kv
from .. import zusammenfassung as zf
from . import ebene_h, rauschen
from .systeme import antworten

VERSION = 'phase0_modell-0.1'
F_S_BEZUG = rauschen.F_S_REF
NULLPUNKT_ZEITEN = ('global', 'betriebszeit')


def _arr(x, n=3):
    """Skalar oder Tupel → Feld der Länge n (Skalar wiederholt)."""
    a = np.asarray(x, float)
    return np.broadcast_to(a, (n,)).copy() if a.ndim == 0 else a.reshape(n)


def _tupel(x):
    a = np.asarray(x, float)
    return float(a) if a.ndim == 0 else tuple(float(v) for v in a.ravel())


@dataclass(frozen=True)
class Strukturparameter:
    name: str = 'struktur'
    sigma_zelle: object = rauschen.SIGMA_SUMME_REF / np.sqrt(3)
    f_s_bezug: float = F_S_BEZUG
    amp: tuple = (('L', 0.0), ('K', 0.0))
    phase_grad: tuple = (('L', 0.02), ('K', 0.02))
    jitter_grad: object = 0.2
    index_versatz_grad: object = 0.05
    nullpunkt_drift_N_je_s: float = 0.0
    lauf_drift_N: float = 0.0
    t_phi_s: tuple = (0.6, 0.05)
    f_streuung_hz: float = 1e-5
    temperatur_C: tuple = (22.0, 0.005)
    sigma_h_zelle: object = None
    sigma_m_zelle: object = None
    versatz_korrelation: float = 0.0
    jitter_korrelation: float = 0.0
    jitter_ar1: float = 0.0
    jitter_last: float = 0.0
    phasendrift_grad: object = 0.0
    phase_gemeinsam_K: bool = False
    rest_N: object = None
    nullpunkt_diffusion_N2_je_s: float = 0.0
    nullpunkt_zeit: str = 'global'
    nullpunkt_sprung_sd_N: float = 0.0
    lauf_drift_sd_N: float = 0.0
    laufintern_amp_sd: object = 0.0
    laufintern_amp_mittel: object = 0.0
    laufintern_phase_sd_grad: object = 0.0
    laufintern_phase_mittel_grad: object = 0.0
    herkunft: tuple = ()

    def __post_init__(self):
        if self.nullpunkt_zeit not in NULLPUNKT_ZEITEN:
            raise ValueError(f'nullpunkt_zeit {self.nullpunkt_zeit!r} unbekannt ({", ".join(NULLPUNKT_ZEITEN)})')

    # Schnittstelle von rauschen.Rauschmodell (ebene_h, ebene_z)
    def a(self, laufart):
        return dict(self.amp)['L' if laufart == 'L' else 'K']

    def p(self, laufart):
        return dict(self.phase_grad)['L' if laufart == 'L' else 'K']

    def a_modul(self, laufart):
        return _arr(self.a(laufart))

    def p_modul(self, laufart):
        return _arr(self.p(laufart))

    def sigma_h(self, T_a):
        s = self.sigma_zelle if self.sigma_h_zelle is None else self.sigma_h_zelle
        return (s if np.ndim(s) == 0 else np.asarray(s, float)) * np.sqrt(2.0 / (self.f_s_bezug * T_a))

    def sigma_mittel(self, T_a):
        s = self.sigma_zelle if self.sigma_m_zelle is None else self.sigma_m_zelle
        return (s if np.ndim(s) == 0 else np.asarray(s, float)) / np.sqrt(self.f_s_bezug * T_a)

    def mit(self, **kw):
        return replace(self, **kw)

    def zusatzstrom_noetig(self):
        """Ziehen die Erweiterungen aus einem eigenen Strom (rng_zusatz)?"""
        return bool(self.rest_N is not None and np.any(np.asarray(self.rest_N, float) > 0)
                    or self.nullpunkt_diffusion_N2_je_s > 0 or self.lauf_drift_sd_N > 0 or self.nullpunkt_sprung_sd_N > 0
                    or np.any(_arr(self.laufintern_amp_sd) > 0) or np.any(_arr(self.laufintern_phase_sd_grad) > 0))

    def erweiterungen(self):
        """Namen der aktiven Erweiterungen gegenüber der Szenariofamilie."""
        d = asdict(Strukturparameter())
        x = asdict(self)
        aus = []
        for f in ('sigma_h_zelle', 'sigma_m_zelle', 'versatz_korrelation', 'jitter_korrelation', 'jitter_ar1',
                  'jitter_last', 'phasendrift_grad', 'phase_gemeinsam_K', 'rest_N', 'nullpunkt_diffusion_N2_je_s',
                  'nullpunkt_sprung_sd_N', 'lauf_drift_sd_N', 'laufintern_amp_sd', 'laufintern_amp_mittel', 'laufintern_phase_sd_grad',
                  'laufintern_phase_mittel_grad'):
            v = x[f]
            if v is None or v is False:
                continue
            if f in ('sigma_h_zelle', 'sigma_m_zelle') or (np.any(np.asarray(v, float) != 0) and v != d[f]):
                aus.append(f)
        if any(np.ndim(np.asarray(v, float)) > 0 for _, v in self.amp + self.phase_grad):
            aus.append('je_modul')
        if self.nullpunkt_zeit != 'global':
            aus.append('nullpunkt_zeit')
        return aus

    def beschreibung(self):
        """JSON-fähige Beschreibung (Herkunft, Prüfsumme)."""
        d = asdict(self)
        d['herkunft'] = dict(self.herkunft)
        return formate._json_wert(d)


def aus_rauschmodell(r, **kw):
    """Strukturparameter mit genau den Werten eines rauschen.Rauschmodell (Modus „bekannt“)."""
    st = Strukturparameter(name=r.name, sigma_zelle=r.sigma_zelle, f_s_bezug=r.f_s_bezug, amp=tuple(r.amp),
                           phase_grad=tuple(r.phase_grad), jitter_grad=r.jitter_grad,
                           index_versatz_grad=r.index_versatz_grad, nullpunkt_drift_N_je_s=r.nullpunkt_drift_N_je_s,
                           lauf_drift_N=r.lauf_drift_N, t_phi_s=tuple(r.t_phi_s), f_streuung_hz=r.f_streuung_hz,
                           temperatur_C=tuple(r.temperatur_C),
                           herkunft=(('quelle', f'bekannt: Rauschmodell {r.name}'),))
    return st.mit(**kw) if kw else st


def parameter(x):
    if isinstance(x, Strukturparameter):
        return x
    if isinstance(x, rauschen.Rauschmodell):
        return aus_rauschmodell(x)
    raise TypeError(f'Rauschparameter vom Typ {type(x).__name__} nicht unterstützt')


# ── Strukturquellen ──────────────────────────────────────────────────────────────────────────────────
@dataclass(eq=False)
class Struktur:
    """Antwort-artige Struktur einer Einstellung: Zellharmonische je Modul N_c,k⁽ʲ⁾ (Bezug eigener Index, gemessen bzw.
    mit Kette), statische Zelllasten F0; G_F = 1 (die Kette steckt in Nz)."""
    f: float
    Nz: np.ndarray
    F0: np.ndarray
    quelle: str
    herkunft: dict = field(default_factory=dict)

    def __post_init__(self):
        self.Nz = np.asarray(self.Nz, complex)
        self.F0 = np.asarray(self.F0, float)
        if self.Nz.ndim != 3 or self.Nz.shape[:2] != (3, 3):
            raise ValueError(f'Struktur: Nz der Form {self.Nz.shape} statt (3, 3, K)')

    @property
    def k_voll(self):
        return self.Nz.shape[-1]

    @property
    def Nz_kraft(self):
        return self.Nz

    @property
    def G_F(self):
        return np.ones((3, self.k_voll), complex)

    @property
    def Ns(self):
        return self.Nz.sum(1)


def struktur_p08(tab, gueltig):
    """Struktur am Arbeitspunkt aus Phase 0: N̄⁽ʲ⁾ je Zelle der gültigen Lⱼ-Läufe (P0.8), F0 aus den gültigen
    R-Läufen."""
    gueltig = np.asarray(gueltig, bool)
    art, mod = tab.spalte('laufart', object), tab.spalte('modul', object)
    p0 = (tab.spalte('phase', int) == 0) & (tab.spalte('einstellung', int) == 1) & gueltig
    Nz, n0 = [], []
    for j in (1, 2, 3):
        m = p0 & (art == 'L') & (mod == j)
        if not m.any():
            raise ValueError(f'Struktur aus P0.8: kein gültiger Einzelmodullauf von Modul {j}')
        Nz.append(tab.daten['Nk_zellen'][m].mean(0))
        n0.append(int(m.sum()))
    R = p0 & (art == 'R')
    if not R.any():
        raise ValueError('Struktur aus P0.8: kein gültiger Referenzlauf für die statischen Zelllasten')
    f = {float(k['f_soll']) for k in tab.koepfe}
    if len(f) != 1:
        raise ValueError(f'Struktur aus P0.8: mehrere Frequenzen {sorted(f)}')
    t = tab.auswahl(np.flatnonzero(p0)).sortiert()
    return Struktur(f=f.pop(), Nz=np.stack(Nz), F0=tab.daten['N_mittel_zellen'][R].mean(0),
                    quelle='P0.8: Einzelmodul-Mittelkurven N̄⁽ʲ⁾ je Zelle (gültige Lⱼ-Läufe), F0 aus den R-Läufen',
                    herkunft=dict(n0=n0, n_R=int(R.sum()),
                                  laeufe_sha256=formate.sha256_json([k['lauf_id'] for k in t.koepfe]),
                                  daten_sha256=formate.sha256_bytes(formate.npz_bytes(t.daten))))


def struktur_kalibrierung(kal, f, k_voll, starr=False):
    """Werkzeug-2-Struktur in der 1-FG-Fassung aus der Kalibrierung (P0.1–P0.5) bei Frequenz f (Kandidatenfrequenzen):
    N_c,k⁽ʲ⁾ = w_cj·G_F,c(kf)·m_j·H(kf)·a_k⁽ʲ⁾ mit a_k = −(2πfk)²·x_k⁽ʲ⁾ (Profil aus P0.5, frequenzunabhängig
    angenommen), H aus f_n, ζ (P0.4), w aus P0.1, m_j aus P0.2; Harmonische über dem Profil von P0.5 null. Kippmoden vernachlässigt.
    starr=True: H = 1 (ausdrücklich, etwa bei starrer Auflage ohne Mode im Band); sonst sind f_n, ζ Pflicht."""
    e = anpassung.h3_eingaenge(kal)
    fehl = [x for x in e['fehlend'] if not (starr and x.startswith('P0.4'))]
    if fehl:
        raise ValueError('Struktur aus der Kalibrierung: ' + '; '.join(fehl))
    k = np.arange(1, k_voll + 1)
    fk = f * k
    H = np.ones(k_voll, complex) if starr else anpassung.h1fg(fk, e['fn_zeta'][0], e['fn_zeta'][1])
    G = anpassung.gf_wert(e['bruecke'], fk)                                 # (Zelle, k)
    Nz = np.zeros((3, 3, k_voll), complex)
    for j, mod in enumerate(e['p05']['module']):
        x = np.asarray(mod['x_m'], complex)
        kk = min(k_voll, x.size)
        a = -(2 * np.pi * fk[:kk]) ** 2 * x[:kk]
        Nz[j, :, :kk] = e['zellanteile'][:, j][:, None] * G[:, :kk] * e['m_j'][j] * H[None, :kk] * a[None]
    F0 = np.asarray(kal['p0_2']['F_c_stat_N'], float)
    return Struktur(f=float(f), Nz=Nz, F0=F0,
                    quelle='Werkzeug 2 (1-FG-Fassung) mit den Kalibrierparametern aus P0.1–P0.5',
                    herkunft=dict(kalibrierung_sha256=formate.sha256_json(kal), f_hz=float(f), starr=bool(starr),
                                  k_profil=int(len(e['p05']['module'][0]['x_m']))))


def struktur_system(system, f=None, k_voll=60, hub_faktor=1.0):
    """Werkzeug 2 (auslegung.Aufbau) mit bekannten Systemparametern: nur Vergleich und Prüfung, keine Phase-0-Größe."""
    a = antworten(system, f=f, hub_faktor=hub_faktor, k_voll=k_voll)
    return Struktur(f=a.f, Nz=a.Nz, F0=a.F0, quelle=f'Werkzeug 2 mit bekannten Parametern ({system.name})',
                    herkunft=dict(system=system.name, bekannt=True))


@dataclass(frozen=True)
class SystemInfo:
    name: str
    f: float
    k_max: int


class Phase0Modell:
    """Generatormodell ohne Szenario: Struktur (exakte Superposition), Plan, Δδ̂ⱼ aus P0.5, Rauschparameter und
    gegebenenfalls Effekte benannter Sensitivitäten (etwa drift_basis). Schnittstelle wie generator.modell.
    Generatormodell, soweit ebene_h, wahrheit und harness.kette sie benutzen."""

    def __init__(self, struktur, plan, delta_delta_grad, k_max, rausch, effekte=(), vollausschlag_N=50.0,
                 name='Phase0', herkunft=None):
        if plan.einstellung2:
            raise ValueError('Phase-0-Modell: Einstellung 2 nicht umgesetzt (Struktur aus P0.8′ fehlt)')
        for e in effekte:
            if e['art'] in ('hertz', 'kennlinie', 'kopplung', 'phasenversatz_k', 'modul_k'):
                raise ValueError(f'Phase-0-Modell: Effekt {e["art"]!r} widerspricht der exakten Superposition der '
                                 'Planung (nur Sensitivitäten wie drift_basis, verstaerkung_p1, offset_k, ereignis)')
        self.struktur, self.plan, self.rausch = struktur, plan, rausch
        self._dd = np.asarray(delta_delta_grad, float)
        self.system = SystemInfo(name, float(struktur.f), int(k_max))
        self.effekte = tuple(effekte)
        self.k_voll = struktur.k_voll
        self.vollausschlag_N = vollausschlag_N
        self.hertz = None
        self.szenario = None
        self.staerke = None
        self.herkunft = dict(herkunft or {})

    def antwort(self, einstellung=1):
        if einstellung != 1:
            raise ValueError('Phase-0-Modell: nur Einstellung 1')
        return self.struktur

    @property
    def delta_delta_grad(self):
        return self._dd - self._dd[0]

    def index_soll_grad(self, phi_profil):
        return np.asarray(phi_profil, float) - self.delta_delta_grad

    def effekte_art(self, art):
        return [e for e in self.effekte if e['art'] == art]

    def ereignis_positionen(self, eff, laeufe):
        if 'laeufe' in eff:
            return list(eff['laeufe'])
        if 'auswahl' not in eff and 'versuch' in eff:
            return []
        a = eff['auswahl']
        pos = [l['position'] for l in laeufe
               if l['konfiguration']['id'] == a.get('konfiguration', l['konfiguration']['id'])
               and l['phase'] == a.get('phase', l['phase']) and l['laufart'] == a.get('laufart', l['laufart'])]
        if 'nummer' in a:
            return [pos[a['nummer']]] if len(pos) > a['nummer'] else []
        return pos


# ── Generator (Spiegel von ebene_h mit Erweiterungen) ────────────────────────────────────────────────────
def _jitter_umformen(zj, st, modell, phi_idx, Nz):
    """Korrelation zwischen den Modulen 2 und 3, AR(1) über die Zyklen und Lastfaktor auf die Standardnormalziehungen
    zj (n, 2, Nz); ohne Erweiterung unverändert."""
    if st.jitter_korrelation:
        r = float(st.jitter_korrelation)
        zj = zj.copy()
        zj[:, 1] = r * zj[:, 0] + np.sqrt(1 - r * r) * zj[:, 1]
    if st.jitter_ar1:
        p = float(st.jitter_ar1)
        x = np.empty_like(zj)
        x[..., 0] = zj[..., 0]
        c = np.sqrt(1 - p * p)
        for t in range(1, Nz):
            x[..., t] = p * x[..., t - 1] + c * zj[..., t]
        zj = x
    if st.jitter_last:
        N1 = modell.antwort(1).Nz[:, :, 0].sum(1)
        q1 = abs((np.exp(-1j * np.radians(phi_idx)) * N1).sum()) / max(np.abs(N1).sum(), 1e-300)
        zj = zj * (1 + float(st.jitter_last) * q1)
    return zj


def _gruppe_signal(modell, specs, rng, st, zrng):
    """Wie ebene_h.gruppe_signal (gleiche Ziehungen aus rng in gleicher Reihenfolge), mit den Erweiterungen von st."""
    l0 = specs[0]
    n, art, e = len(specs), l0['laufart'], l0['einstellung']
    ant = modell.antwort(e)
    K, Nz = ant.k_voll, modell.plan.n_zyklen
    nf = Nz // 5
    k = np.arange(1, K + 1)
    w = np.zeros(3)
    if art == 'K':
        w[:] = 1.0
        phi_idx = modell.index_soll_grad(l0['konfiguration']['phi_soll_grad'])
    elif art == 'L':
        w[l0['modul'] - 1] = 1.0
        phi_idx = np.zeros(3)
    else:
        phi_idx = np.zeros(3)
    bew = w > 0
    A = np.ones((n, 3))
    dl = np.zeros((n, 3))
    if bew.any():
        A[:, bew] += st.a_modul(art)[bew] * rng.standard_normal((n, bew.sum()))
        zd = rng.standard_normal((n, bew.sum()))
        if st.phase_gemeinsam_K and art == 'K':
            zd = np.repeat(zd[:, :1], bew.sum(), 1)
        dl[:, bew] = st.p_modul(art)[bew] * zd
    off = np.zeros((n, 3))
    jit = np.zeros((n, 3, Nz))
    if art == 'K':
        zo = rng.standard_normal((n, 2))
        if st.versatz_korrelation:
            r = float(st.versatz_korrelation)
            zo = np.c_[zo[:, 0], r * zo[:, 0] + np.sqrt(1 - r * r) * zo[:, 1]]
        off[:, 1:] = _arr(st.index_versatz_grad, 2) * zo
        zj = _jitter_umformen(rng.standard_normal((n, 2, Nz)), st, modell, phi_idx, Nz)
        jit[:, 1:, :] = _arr(st.jitter_grad, 2)[:, None] * zj
        if np.any(_arr(st.phasendrift_grad) != 0):
            rampe = np.arange(Nz) / max(Nz - 1, 1) - 0.5
            jit = jit + _arr(st.phasendrift_grad)[None, :, None] * rampe[None, None, :]
    phi_c = phi_idx[None, :, None] + off[:, :, None] + jit
    z = np.exp(-1j * np.radians(phi_c))
    P = np.ones_like(z)
    Za, Zf, Zl = (np.zeros((n, 3, K), complex) for _ in range(3))
    for i in range(K):
        P = P * z
        Za[:, :, i], Zf[:, :, i], Zl[:, :, i] = P.sum(-1), P[..., :nf].sum(-1), P[..., -nf:].sum(-1)
    fak = (w[None, :] * A)[:, :, None] * np.exp(-1j * k[None, None, :] * np.radians(dl)[:, :, None])
    phase1 = np.array([l['phase'] == 1 for l in specs])
    if art == 'K':
        for eff in modell.effekte_art('kopplung'):
            g = np.ones(K)
            ix = (np.asarray(eff['harmonische']) - 1) if eff.get('harmonische') is not None else slice(None)
            g[ix] = 1 - eff['x']
            fak = fak * g[None, None, :]
        for eff in modell.effekte_art('phasenversatz_k'):
            fak[:, eff['modul'] - 1, :] *= np.exp(-1j * k * np.radians(eff['grad']))
        for eff in modell.effekte_art('modul_k'):
            fak[:, eff['modul'] - 1, :] *= 1 + eff['faktor']
    for eff in modell.effekte_art('drift_basis'):
        d = np.broadcast_to(np.asarray(eff['faktor'], float), (3,))
        fak[phase1] *= (1 + d)[None, :, None]
    fak_f, fak_l = fak, fak
    li_sd = (_arr(st.laufintern_amp_sd), _arr(st.laufintern_phase_sd_grad))
    li_mw = (_arr(st.laufintern_amp_mittel), _arr(st.laufintern_phase_mittel_grad))
    if bew.any() and (np.any(li_sd[0] > 0) or np.any(li_sd[1] > 0) or np.any(li_mw[0] != 0) or np.any(li_mw[1] != 0)):
        da = li_mw[0][None, :] + (li_sd[0][None, :] * zrng.standard_normal((n, 3)) if np.any(li_sd[0] > 0) else 0.0)
        dd = li_mw[1][None, :] + (li_sd[1][None, :] * zrng.standard_normal((n, 3)) if np.any(li_sd[1] > 0) else 0.0)
        da, dd = np.broadcast_to(da, (n, 3)) * w[None], np.radians(np.broadcast_to(dd, (n, 3))) * w[None]
        fak_f = fak * ((1 - da / 2)[:, :, None] * np.exp(1j * k[None, None, :] * (dd / 2)[:, :, None]))
        fak_l = fak * ((1 + da / 2)[:, :, None] * np.exp(-1j * k[None, None, :] * (dd / 2)[:, :, None]))
    Fa, Ff, Fl = fak * Za / Nz, fak_f * Zf / nf, fak_l * Zl / nf
    if modell.hertz is not None:
        Nkr = ebene_h._hertz_kraft(modell, l0, art, e, phi_idx, Fa, Ff, Fl)
    else:
        Nkr = [np.einsum('njk,jck->nck', F, ant.Nz_kraft) for F in (Fa, Ff, Fl)]
    if st.rest_N is not None and bew.any():
        rs = np.asarray(st.rest_N, float)
        if np.any(rs > 0):
            kr = min(rs.shape[-1], K)
            O = np.zeros((n, 3, 3, K), complex)
            O[..., :kr] = rs[None, :, :, :kr] * (zrng.standard_normal((n, 3, 3, kr)) +
                                                 1j * zrng.standard_normal((n, 3, 3, kr)))
            O = O * bew[None, :, None, None]
            Nkr = [x + np.einsum('njk,njck->nck', Zx / nn, O) for x, Zx, nn in zip(Nkr, (Za, Zf, Zl), (Nz, nf, nf))]
    zeiger = np.where(bew[None, :, None], Za, np.nan + 1j * np.nan)
    fz = np.where(bew[None, None, :], np.stack([Zf[:, :, 0], Zl[:, :, 0]], 1), np.nan + 1j * np.nan)
    return dict(n=n, art=art, einstellung=e, ant=ant, K=K, Nz=Nz, nf=nf, phi_c=phi_c, zeiger=zeiger, A=A, dl=dl,
                fuenftel_zeiger=fz,
                bew=bew, fak=fak, phi_idx=phi_idx, Nkraft=Nkr[0], Nkraft_f=Nkr[1], Nkraft_l=Nkr[2], phase1=phase1)


def _ziehen(modell, specs, rng, st, zrng):
    """Wie ebene_h.ziehen (gleiche Ziehungen aus rng), Boden je Zelle, Laufdriftstreuung aus zrng."""
    g = _gruppe_signal(modell, specs, rng, st, zrng)
    ant = g['ant']
    Ta = modell.plan.n_zyklen / ant.f
    F0 = ant.F0
    GF = ant.G_F[None]
    Nh, mean = ebene_h.kennlinie(modell, g['Nkraft'] * GF, F0)
    Nh_f, mean_f = ebene_h.kennlinie(modell, g['Nkraft_f'] * GF, F0)
    Nh_l, mean_l = ebene_h.kennlinie(modell, g['Nkraft_l'] * GF, F0)
    gain = np.ones((len(specs), 3))
    for eff in modell.effekte_art('verstaerkung_p1'):
        gain[g['phase1']] *= 1 + np.broadcast_to(np.asarray(eff['faktor'], float), (3,))
    Nh, Nh_f, Nh_l = Nh * gain[:, :, None], Nh_f * gain[:, :, None], Nh_l * gain[:, :, None]
    mean, mean_f, mean_l = mean * gain, mean_f * gain, mean_l * gain
    if specs[0]['laufart'] == 'K':
        for eff in modell.effekte_art('offset_k'):
            mean, mean_f, mean_l = mean + eff['N'] / 3, mean_f + eff['N'] / 3, mean_l + eff['N'] / 3
    sh, sm = st.sigma_h(Ta), st.sigma_mittel(Ta)
    if np.ndim(sh):
        sh = np.asarray(sh)[:, None]
    m = len(specs)
    K = modell.k_voll
    r5 = np.sqrt(5.0) * (sh * (rng.standard_normal((m, 5, 3, K)) + 1j * rng.standard_normal((m, 5, 3, K))))
    m5 = np.sqrt(5.0) * sm * rng.standard_normal((m, 5, 3))
    Nrun = Nh + r5.mean(1)
    zm = np.exp(1j * np.radians(g['phi_c'])).mean(-1)
    pm = np.degrees(np.angle(zm)) % 360.0
    sg = np.degrees(np.sqrt(-2 * np.log(np.clip(np.abs(zm), 1e-300, 1.0))))
    n_abt = max(int(st.f_s_bezug * modell.plan.T_lauf), 10)
    sz = st.sigma_zelle if np.ndim(st.sigma_zelle) == 0 else np.asarray(st.sigma_zelle, float)
    ev_min = ebene_h._extremwert(rng, n_abt, (m, 3))
    ev_max = ebene_h._extremwert(rng, n_abt, (m, 3))
    T0, sT = st.temperatur_C
    t_min = T0 - np.abs(sT * rng.standard_normal((m, 3)))
    t_max = T0 + np.abs(sT * rng.standard_normal((m, 3)))
    tp = st.t_phi_s[0] + st.t_phi_s[1] * rng.standard_normal((m, 3))
    geregelt = (np.arange(3) > 0) & g['bew'] & (specs[0]['laufart'] == 'K')
    f_m = ant.f + st.f_streuung_hz * rng.standard_normal(m)
    ld = st.lauf_drift_N * 0.4
    if st.lauf_drift_sd_N > 0:
        ld = 0.4 * (st.lauf_drift_N + st.lauf_drift_sd_N * zrng.standard_normal(m))
    s_summe = 3 * sz ** 2 if np.ndim(sz) == 0 else float((sz ** 2).sum())
    return dict(
        g=g, f=ant.f, mean=mean, mean_f=mean_f, mean_l=mean_l, m5=m5, m5m=m5.mean(1), kurve=kv.kurve(Nh), sz=sz,
        ev_min=ev_min, ev_max=ev_max, ld=ld, drift=st.nullpunkt_drift_N_je_s,
        fest=dict(Nk_zellen=Nrun, Nk_summe=Nrun.sum(1), fuenftel_Nk=np.stack([(Nh_f + r5[:, 0]).sum(1),
                                                                            (Nh_l + r5[:, 4]).sum(1)], 1),
                  zeiger=g['zeiger'], phi_mittel_grad=np.where(g['bew'][None], pm, np.nan),
                  sigma_grad=np.where(g['bew'][None], sg, np.nan),
                  sigma_roh_zellen=np.sqrt(0.5 * (np.abs(Nh) ** 2).sum(-1) + sz ** 2),
                  sigma_roh_summe=np.sqrt(0.5 * (np.abs(Nh.sum(1)) ** 2).sum(-1) + s_summe),
                  temperatur_min_zellen=t_min, temperatur_max_zellen=t_max,
                  t_phi=np.where(geregelt[None], tp, np.nan)),
        f_mittel=f_m, optional=dict(fuenftel_zeiger=g['fuenftel_zeiger']))


def _bilden(modell, z, zeilen, t_mitte, daten, idx, nullpunkt=None):
    """Wie ebene_h.bilden; dazu der Wert des Zufallspfads des Nullpunkts je Lauf (Summe, gleich auf die Zellen) und eine
    Laufdrift je Lauf."""
    zeilen = np.asarray(zeilen, int)
    drift = z['drift'] * np.asarray(t_mitte, float) / 3
    if nullpunkt is not None:
        drift = drift + np.asarray(nullpunkt, float) / 3
    mean, mean_f, mean_l = (z[x][zeilen] + drift[:, None] for x in ('mean', 'mean_f', 'mean_l'))
    m5 = z['m5'][zeilen]
    mrun = mean + z['m5m'][zeilen]
    for name, v in z['fest'].items():
        daten[name][idx] = v[zeilen]
    for name, v in z.get('optional', {}).items():                      # optionale Felder, wenn das Format sie führt
        if name in daten:
            daten[name][idx] = v[zeilen]
    daten['N_mittel_zellen'][idx] = mrun
    daten['N_mittel'][idx] = mrun.sum(1)
    ld = z['ld'] if np.ndim(z['ld']) == 0 else np.asarray(z['ld'])[zeilen]
    daten['fuenftel_N_mittel'][idx, 0] = (mean_f + m5[:, 0]).sum(1) - ld
    daten['fuenftel_N_mittel'][idx, 1] = (mean_l + m5[:, 4]).sum(1) + ld
    x = mean[:, :, None] + z['kurve'][zeilen]
    daten['min_roh_zellen'][idx] = np.maximum(x.min(-1), 0.0) - z['sz'] * z['ev_min'][zeilen]
    daten['max_roh_zellen'][idx] = x.max(-1) + z['sz'] * z['ev_max'][zeilen]
    daten['uebersteuert_zellen'][idx] = daten['max_roh_zellen'][idx] >= modell.vollausschlag_N


def nullpunktpfad(D, t, rng):
    """Zufallspfad W(t) mit Var(W(t) − W(s)) = D·|t − s| zu den Zeitpunkten t (beliebige Reihenfolge), W(t_min) = 0."""
    t = np.asarray(t, float)
    o = np.argsort(t, kind='stable')
    dt = np.diff(t[o], prepend=t[o][0])
    w = np.cumsum(np.sqrt(D * dt) * rng.standard_normal(t.size))
    out = np.empty_like(w)
    out[o] = w
    return out


def nullpunktspruenge(sd, laeufe, rng):
    """Zufälliger Nullpunkt je Abschnitt (Phase, Messtag) in Laufreihenfolge, erster Abschnitt 0 [N]."""
    abschnitte = sorted({(l['phase'], l['messtag']) for l in laeufe})
    werte = np.r_[0.0, sd * rng.standard_normal(len(abschnitte) - 1)].cumsum()
    ort = dict(zip(abschnitte, werte))
    return np.array([ort[(l['phase'], l['messtag'])] for l in laeufe])


def erzeuge(modell, laeufe, rng, rausch=None, rng_zusatz=None):
    """Laufzusammenfassungen (LaufTabelle) wie ebene_h.erzeuge mit Strukturparametern (rausch: Strukturparameter oder
    rauschen.Rauschmodell; Vorgabe modell.rausch). rng_zusatz: eigener Strom der Erweiterungen mit Ziehung; ohne ihn
    sind solche Erweiterungen ein Fehler (kein stiller Ersatzstrom)."""
    st = parameter(modell.rausch if rausch is None else rausch)
    if st.zusatzstrom_noetig() and rng_zusatz is None:
        raise ValueError('Strukturmodell: Erweiterungen mit eigener Ziehung (Rest, Zufallspfad, Laufdrift, Fünftel) '
                         'verlangen rng_zusatz')
    n = len(laeufe)
    daten = zf.leere_daten(modell.k_voll, n)
    koepfe = [None] * n
    tm = np.array([0.5 * (l['t_start'] + l['t_ende']) for l in laeufe])
    td = tm if st.nullpunkt_zeit == 'global' else (np.array([l['position'] for l in laeufe], float) + 0.5) * \
        modell.plan.T_lauf
    W = nullpunktpfad(st.nullpunkt_diffusion_N2_je_s, td, rng_zusatz) if st.nullpunkt_diffusion_N2_je_s > 0 else None
    if st.nullpunkt_sprung_sd_N > 0:
        W = (np.zeros(n) if W is None else W) + nullpunktspruenge(st.nullpunkt_sprung_sd_N, laeufe, rng_zusatz)
    for idx in ebene_h._gruppen(laeufe):
        specs = [laeufe[i] for i in idx]
        z = _ziehen(modell, specs, rng, st, rng_zusatz)
        _bilden(modell, z, np.arange(len(idx)), td[idx], daten, idx, None if W is None else W[idx])
        for jj, i in enumerate(idx):
            koepfe[i] = ebene_h.kopf(modell, laeufe[i], z, jj)
    ebene_h._ereignisse(modell, laeufe, koepfe, daten)
    tab = zf.LaufTabelle(koepfe, daten)
    tab.meta['generator'] = dict(version=VERSION, parameter=st.name, erweiterungen=st.erweiterungen())
    return tab


class Vorrat:
    """Spiegel von ebene_h.Vorrat für das Strukturmodell (Ablauf „zustand“ mit Kampagnen aus einer Modellquelle):
    Ziehungen aller geplanten Läufe wie erzeuge (gleiche Ströme in gleicher Reihenfolge: Zufallspfad und Sprünge des
    Nullpunkts, dann die Gruppen); der ursprüngliche Versuch eines geplanten Laufs erhält dessen Ziehung, gebildet zu
    seinem tatsächlichen Zeitpunkt (Betriebszeit (Position + ½)·T_Lauf bzw. Kampagnenuhr bei nullpunkt_zeit 'global').
    Ohne Verschiebung entsteht genau die Tabelle von erzeuge. Zusätzliche Versuche ziehen aus eigenen Strömen je
    Versuch (Hauptstrom und Zusatzstrom der Erweiterungen). Der Zufallspfad des Nullpunkts ist ein einziger Pfad: Ein
    Versuch zu einer neuen Zeit erhält seinen Wert bedingt auf alle schon bekannten Werte (Brownsche Brücke zwischen
    den Nachbarn, Fortsetzung am Rand) aus dem Pfadstrom des Versuchs; ein Sprung je Abschnitt (Phase, Messtag) gilt
    für alle Versuche des Abschnitts, ein neuer Abschnitt setzt die Folge fort."""

    def __init__(self, modell, laeufe, rng, rausch=None, rng_zusatz=None):
        self.modell = modell
        self.st = st = parameter(modell.rausch if rausch is None else rausch)
        if st.zusatzstrom_noetig() and rng_zusatz is None:
            raise ValueError('Strukturmodell: Erweiterungen mit eigener Ziehung (Rest, Zufallspfad, Laufdrift, '
                             'Fünftel) verlangen rng_zusatz')
        self.T_lauf = float(modell.plan.T_lauf)
        td = np.array([self._zeit(l) for l in laeufe])
        D = st.nullpunkt_diffusion_N2_je_s
        W = nullpunktpfad(D, td, rng_zusatz) if D > 0 else None
        self.pfad = None if W is None else (list(td[np.argsort(td, kind='stable')]),
                                            list(W[np.argsort(td, kind='stable')]))
        self.sprung = {}
        if st.nullpunkt_sprung_sd_N > 0:
            S = nullpunktspruenge(st.nullpunkt_sprung_sd_N, laeufe, rng_zusatz)
            self.sprung = {(l['phase'], l['messtag']): float(x) for l, x in zip(laeufe, S)}
        self.ort = {}
        for idx in ebene_h._gruppen(laeufe):
            z = _ziehen(modell, [laeufe[i] for i in idx], rng, st, rng_zusatz)
            for jj, i in enumerate(idx):
                self.ort[laeufe[i]['lauf_id']] = (z, jj, float(td[i]), None if W is None else float(W[i]))
        self.ereignisse = {}
        for eff in modell.effekte_art('ereignis'):
            for p in modell.ereignis_positionen(eff, laeufe):
                self.ereignisse.setdefault(p, []).append(eff)

    def _zeit(self, spec):
        if self.st.nullpunkt_zeit == 'global':
            return 0.5 * (spec['t_start'] + spec['t_ende'])
        return (float(spec['position']) + 0.5) * self.T_lauf

    def _pfadwert(self, t, rng):
        """Wert des Zufallspfads zur Zeit t, bedingt auf die bekannten Werte; neue Werte werden Teil des Pfads."""
        T, W = self.pfad
        i = int(np.searchsorted(T, t))
        if i < len(T) and T[i] == t:
            return W[i]
        D = self.st.nullpunkt_diffusion_N2_je_s
        if rng is None:
            raise ValueError('Strukturmodell: neuer Zeitpunkt des Nullpunktpfads verlangt einen Pfadstrom')
        if i == 0:
            w = W[0] + np.sqrt(D * (T[0] - t)) * rng.standard_normal()
        elif i == len(T):
            w = W[-1] + np.sqrt(D * (t - T[-1])) * rng.standard_normal()
        else:
            a, b = T[i - 1], T[i]
            m = W[i - 1] + (W[i] - W[i - 1]) * (t - a) / (b - a)
            w = m + np.sqrt(D * (t - a) * (b - t) / (b - a)) * rng.standard_normal()
        T.insert(i, t)
        W.insert(i, float(w))
        return float(w)

    def _sprungwert(self, abschnitt, rng):
        if not self.sprung:
            return 0.0
        if abschnitt not in self.sprung:                    # Abschnitt außerhalb des Plans (Verschiebung)
            vorher = [k for k in sorted(self.sprung) if k < abschnitt]
            basis = self.sprung[vorher[-1]] if vorher else 0.0
            self.sprung[abschnitt] = basis + self.st.nullpunkt_sprung_sd_N * rng.standard_normal()
        return self.sprung[abschnitt]

    def lauf(self, spec, bezug=None, rng=None, rng_zusatz=None, rng_pfad=None, ereignisse=(), messtag=None):
        """Laufzusammenfassung (Kopf, Datenzeilen) eines Versuchs mit spec (Kopfangaben einschließlich Position,
        t_start, t_ende). bezug: lauf_id des geplanten Laufs, dessen Ziehung der Versuch verwendet; sonst rng und
        rng_zusatz: eigene Ströme des zusätzlichen Versuchs. rng_pfad: Strom für einen neuen Zeitpunkt des
        Nullpunktpfads bzw. einen neuen Abschnitt; messtag: tatsächlicher Messtag (Vorgabe spec['messtag'])."""
        t = self._zeit(spec)
        if bezug is not None:
            z, zeile, t_plan, w_plan = self.ort[bezug]
        else:
            if self.st.zusatzstrom_noetig() and rng_zusatz is None:
                raise ValueError('Strukturmodell: zusätzlicher Versuch ohne Zusatzstrom')
            z, zeile, t_plan, w_plan = _ziehen(self.modell, [spec], rng, self.st, rng_zusatz), 0, None, None
        W = None
        if self.pfad is not None:
            W = w_plan if (t_plan is not None and t == t_plan) else self._pfadwert(t, rng_pfad)
        if self.sprung:
            W = (0.0 if W is None else W) + self._sprungwert((spec['phase'], spec['messtag'] if messtag is None
                                                               else messtag), rng_pfad)
        daten = zf.leere_daten(self.modell.k_voll, 1)
        _bilden(self.modell, z, [zeile], [t], daten, [0], None if W is None else [W])
        k = ebene_h.kopf(self.modell, spec, z, zeile)
        effs = list(self.ereignisse.get(spec.get('position_geplant'), ())) if bezug is not None else []
        for eff in effs + list(ereignisse):
            ebene_h.ereignis_anwenden(self.modell, eff, k, daten, 0)
        return k, daten, (z, zeile)

    def tabelle(self, laeufe):
        """Laufzusammenfassungen geplanter Läufe zu ihren geplanten Zeitpunkten (gleich den Zeilen von erzeuge)."""
        koepfe, zeilen = [], []
        for l in laeufe:
            k, d, _ = self.lauf(dict(l, position_geplant=l['position']), bezug=l['lauf_id'])
            koepfe.append(k)
            zeilen.append(d)
        tab = zf.LaufTabelle(koepfe, {f: np.concatenate([d[f] for d in zeilen]) for f in zeilen[0]})
        tab.meta['generator'] = dict(version=VERSION, parameter=self.st.name, erweiterungen=self.st.erweiterungen())
        return tab


# ── Parameter aus Phase 0 ───────────────────────────────────────────────────────────────────────────
GRENZEN = ('punkt', 'oben80')
# Wert der Regel p0.strukturmodell, den aus_laufgroessen umsetzt (regeln._NEU_11)
STRUKTURREGEL = dict(punkt='√max(0, s² − Boden), abgeschnitten bei null',
                     obere_grenze='√max(0, s²·ν/χ²₀,₂(ν) − Boden) je Komponente; Boden von ⟨N⟩: ein Faktor für alle '
                                  'Laufarten',
                     nicht_identifizierbar='0, ausdrücklich benannt, als benannte Sensitivität geführt',
                     rest='orthogonaler Rest je Modul und Harmonischer als Vielfaches des Zellbodens, laufweise',
                     kombination='Streuung der Kombinationsläufe wie in den Lⱼ-Läufen (Übertragungstest an den '
                                 'Piloten)',
                     boden='weiß über die Zyklen (σ ∝ 1/√T_a)',
                     nullpunkt='Drift und Zufallspfad über die Betriebszeit (ohne Pausen); Sprünge zwischen '
                               'Messtagen und Phasen: Sensitivität drift_messtage')


def regeln_pruefen(profil, sensitivitaeten=False):
    """Bindung an das Profil (Regelstand 2026-11): p0.strukturmodell und gegebenenfalls rauschmodelle.sensitivitaeten
    müssen die hier umgesetzten Werte haben; sonst ValueError (kein stiller Ersatzweg)."""
    w = profil.wert('p0.strukturmodell')
    if w != STRUKTURREGEL:
        raise ValueError(f'Regel p0.strukturmodell: Wert {w!r} nicht umgesetzt')
    if sensitivitaeten:
        v = profil.wert('rauschmodelle.sensitivitaeten')
        if v != sensitivitaeten_regelwert():
            raise ValueError(f'Regel rauschmodelle.sensitivitaeten: Wert {v!r} nicht umgesetzt '
                             f'({SENSITIVITAETEN_VERSION})')
    return True


def _w(c, grenze, leer=0.0):
    """Wert einer Komponente (Punktschätzer oder obere 80-%-Grenze); nicht identifizierbar: leer (0, benannt)."""
    if c is None or not c.get('identifiziert'):
        return leer
    v = c['wert'] if grenze == 'punkt' else c['oben80']
    return leer if v is None else float(v)


def aus_laufgroessen(lg, grenze='punkt', name=None):
    """Strukturparameter (Strukturmodell, Regel rauschmodelle: standard) aus den Laufgrößen eines Satzes.
    grenze 'punkt': Punktschätzer (Teil-B-Werte nach der Planung); 'oben80': marginale obere 80-%-Grenze je
    identifizierbarer Komponente mit eigenem ν (Planung), der Boden von ⟨N⟩ mit einem gemeinsamen Faktor κ(ν_m) für
    alle Zellen und Laufarten (ein Parameter je Zelle für R-, L- und K-Läufe). Nicht identifizierbare Komponenten sind
    0 und stehen in herkunft['nicht_identifizierbar']; die Amplituden- und Phasenstreuung der Kombinationsläufe gleich
    der der Lⱼ-Läufe (Annahme, Übertragungstest im Satz)."""
    if grenze not in GRENZEN:
        raise ValueError(f'Grenze {grenze!r} unbekannt ({", ".join(GRENZEN)})')
    b = lg['bindung']
    Ta0 = float(b['T_a_s'])
    bo = lg['boden']
    fehlt = []

    def w(c, was):
        if c is None or not c.get('identifiziert'):
            fehlt.append(dict(komponente=was, grund=(c or {}).get('grund', 'fehlt')))
        return _w(c, grenze)
    sh = np.array([w(c, f'Boden Re/Im Zelle {i + 1}') for i, c in enumerate(bo['sigma_h_zellen'])])
    sig_c = np.asarray(bo.get('sigma_c', sh * np.sqrt(F_S_BEZUG * Ta0 / 2)), float)
    sm = np.array([_w(c, 'punkt') for c in bo['sigma_mittel_zellen']])
    nu_m = bo.get('nu_m')
    fak_m = 1.0
    if grenze == 'oben80' and nu_m:
        from .. import laufgroessen as lgm
        fak_m = lgm.kappa(nu_m)
    if not all(c.get('identifiziert') for c in bo['sigma_mittel_zellen']):
        fehlt.append(dict(komponente='Boden von ⟨N⟩', grund='keine Fünftel'))
    sm = sm * fak_m
    a = [w(m['sigma_a'], f'sigma_a Modul {j + 1}') for j, m in enumerate(lg['module'])]
    d = [w(m['sigma_delta'], f'sigma_delta Modul {j + 1}') for j, m in enumerate(lg['module'])]
    off = [w(c, f'sigma_off Modul {j}') for j, c in enumerate(lg['versatz']['module'][1:], start=2)]
    jit = [w(c, f'Jitter Modul {j}') for j, c in enumerate(lg['jitter']['module'][1:], start=2)]
    kr = lg['versatz'].get('korrelation') or {}
    r = float(np.clip(kr.get('wert') or 0.0, -0.99, 0.99))
    # orthogonaler Rest: q_jk·σ²_h,c (Vielfaches des Zellbodens bei T_a0), laufweise
    k = int(b['k'])
    s2h = np.asarray([0.0 if x['wert'] is None else x['wert'] ** 2 for x in bo['sigma_h_zellen']])
    rest = np.zeros((3, 3, k))
    for j, m in enumerate(lg['module']):
        for i, q in enumerate(m.get('rest') or []):
            qq = q['q'] if grenze == 'punkt' else q['q_oben80']
            rest[j, :, i] = np.sqrt(max(0.0, qq or 0.0) * s2h)
    nul = lg['nullpunkt']
    D = _w(nul['diffusion'], grenze)
    if not nul['diffusion'].get('identifiziert'):
        fehlt.append(dict(komponente='Nullpunktdiffusion', grund=nul['diffusion'].get('grund')))
    drift = (nul.get('drift') or {}).get('wert') or 0.0
    lm = lg['laufintern']['mittel_N']
    ld_mw = ((lm.get('mittel') or {}).get('wert') or 0.0) / 0.8
    ld_sd = _w(lm.get('streuung'), grenze) / 0.8
    li = lg['laufintern']['module']
    li_a = [_w((x or {}).get('amplitude'), grenze) for x in li]
    li_p = [_w((x or {}).get('phase'), grenze) for x in li]
    li_am = [((x or {}).get('amplitude_mittel') or {}).get('wert') or 0.0 for x in li]
    li_pm = [((x or {}).get('phase_mittel') or {}).get('wert') or 0.0 for x in li]
    te = lg['technik']
    tphi = (te['t_phi_s']['mittel'] or 0.6, te['t_phi_s']['streuung'] or 0.0)
    temp = (te['temperatur_C']['mittel'] or 22.0, te['temperatur_C']['streuung_im_lauf'] or 0.0)
    herk = (('quelle', 'Strukturmodell aus Phase 0 (laufgroessen)'), ('grenze', grenze),
            ('bindung', dict(k=k, N_z=b['N_z'], T_a_s=Ta0)), ('laufgroessen_version', lg['version']),
            ('faktor_boden_mittel', fak_m), ('nicht_identifizierbar', tuple(map(str, fehlt))),
            ('annahmen', ('Streuung der Kombinationsläufe gleich Lⱼ (je Modul)', 'Boden weiß über T_a (σ ∝ 1/√T_a)',
                          'orthogonaler Rest ∝ Zellboden, laufweise', 'Fünftelanteile linear im Lauf',
                          'Nullpunktdrift und Zufallspfad über die Betriebszeit, ohne Pausen')),
            ('lesart', 'marginale Grenzen je Komponente; keine gemeinsame 80-%-Garantie' if grenze == 'oben80'
             else 'Punktschätzer'))
    return Strukturparameter(
        name=name or f'struktur_phase0({grenze})', sigma_zelle=_tupel(sig_c), f_s_bezug=F_S_BEZUG,
        amp=(('L', _tupel(a)), ('K', _tupel(a))), phase_grad=(('L', _tupel(d)), ('K', _tupel(d))),
        jitter_grad=_tupel(jit), index_versatz_grad=_tupel(off), nullpunkt_drift_N_je_s=float(drift),
        lauf_drift_N=float(ld_mw), t_phi_s=tphi, f_streuung_hz=float(te['f_streuung_hz'] or 0.0), temperatur_C=temp,
        nullpunkt_zeit='betriebszeit',
        sigma_h_zelle=_tupel(sh * np.sqrt(F_S_BEZUG * Ta0 / 2)), sigma_m_zelle=_tupel(sm * np.sqrt(F_S_BEZUG * Ta0)),
        versatz_korrelation=r, rest_N=tuple(tuple(tuple(float(v) for v in zeile) for zeile in m) for m in rest)
        if rest.any() else None,
        nullpunkt_diffusion_N2_je_s=float(D), lauf_drift_sd_N=float(ld_sd), laufintern_amp_sd=_tupel(li_a),
        laufintern_amp_mittel=_tupel(li_am), laufintern_phase_sd_grad=_tupel(li_p),
        laufintern_phase_mittel_grad=_tupel(li_pm), herkunft=herk)


def familienanpassung(lg, grenze='punkt'):
    """Eingebettete Alternative (Regel rauschmodelle: eingebettet): die Szenariofamilie rauschen.Rauschmodell mit aus
    Phase 0 gepoolten Momentenschätzern (Amplitude, Phase, Jitter, Versatz als RMS über die Module; Boden der
    Harmonischen gepoolt über die Zellen, ⟨N⟩-Boden über die Familienkonvention σ_m = σ_h/√2 gebunden; lineare
    Nullpunkt- und Laufdrift; Kombinationsläufe wie Lⱼ). Ohne orthogonalen Rest, Zufallspfad und Fünftelanteile."""
    if grenze not in GRENZEN:
        raise ValueError(f'Grenze {grenze!r} unbekannt ({", ".join(GRENZEN)})')
    b = lg['bindung']
    Ta0 = float(b['T_a_s'])

    def rms(werte):
        x = np.array([v for v in werte if v is not None], float)
        return float(np.sqrt(np.mean(x ** 2))) if x.size else 0.0
    sh = rms([_w(c, grenze, None) for c in lg['boden']['sigma_h_zellen']])
    a = rms([_w(m['sigma_a'], grenze, None) for m in lg['module']])
    d = rms([_w(m['sigma_delta'], grenze, None) for m in lg['module']])
    j = rms([_w(c, grenze, None) for c in lg['jitter']['module'][1:]])
    o = rms([_w(c, grenze, None) for c in lg['versatz']['module'][1:]])
    te = lg['technik']
    lm = lg['laufintern']['mittel_N']
    return rauschen.getrennt(f'familie_phase0({grenze})', a, a, d, d, sigma_zelle=sh * np.sqrt(F_S_BEZUG * Ta0 / 2),
                             f_s_bezug=F_S_BEZUG, jitter_grad=j, index_versatz_grad=o,
                             nullpunkt_drift_N_je_s=float((lg['nullpunkt'].get('drift') or {}).get('wert') or 0.0),
                             lauf_drift_N=float(((lm.get('mittel') or {}).get('wert') or 0.0) / 0.8),
                             t_phi_s=(te['t_phi_s']['mittel'] or 0.6, te['t_phi_s']['streuung'] or 0.0),
                             f_streuung_hz=float(te['f_streuung_hz'] or 0.0),
                             temperatur_C=(te['temperatur_C']['mittel'] or 22.0,
                                           te['temperatur_C']['streuung_im_lauf'] or 0.0))


# ── benannte Sensitivitäten (feste Stärken; Vorschlag, Festlegung in Teil A ausstehend) ────────────────────────
SENSITIVITAETEN_VERSION = 'sensitivitaeten-0.1'
SENSITIVITAETEN = {
    'jitter_farbig': dict(beschreibung='farbiger Jitter: AR(1) über die Zyklen mit Koeffizient 0,9', jitter_ar1=0.9),
    'jitter_korreliert': dict(beschreibung='Jitter der Module 2 und 3 je Zyklus korreliert (ρ = 0,5)',
                              jitter_korrelation=0.5),
    'jitter_lastabhaengig': dict(beschreibung='Jitter der Kombinationsläufe × (1 + 0,5·q₁(φ))', jitter_last=0.5),
    'phasendrift_lauf': dict(beschreibung='lineare Indexphasendrift 0,1° über den Kombinationslauf (Module 2, 3)',
                             phasendrift_grad=(0.0, 0.1, 0.1)),
    'kombination_doppelt': dict(beschreibung='Amplituden- und Phasenstreuung der Kombinationsläufe doppelt so groß '
                                             'wie in Lⱼ', faktor_K=2.0),
    'laufzeit_gemeinsam': dict(beschreibung='gemeinsame Laufzeitschwankung der Kette statt modulweisem δ in den '
                                            'Kombinationsläufen', phase_gemeinsam_K=True),
    'amplitude_doppelt': dict(beschreibung='Amplitudenstreuung je Modul doppelt so groß (alle Laufarten)',
                              faktor_amp=2.0),
    'nullpunkt_diffusion': dict(beschreibung='Zufallspfad des Nullpunkts mit D·13·T_Lauf = σ²_m,Σ (Leave-one-out-'
                                             'Varianz am Abstand von P0.7 etwa verdoppelt)', diffusion_relativ=1.0),
    'drift_phase1': dict(beschreibung='Drift der Einzelmodulbasis zwischen Phase 0 und Phase 1: +0,1 % Amplitude '
                                      'aller Module in Phase 1', effekt=dict(art='drift_basis', faktor=0.001)),
    'drift_messtage': dict(beschreibung='Nullpunktsprung zwischen Messtagen und zwischen den Phasen, zufällig je '
                                        'Abschnitt mit Streuung 2·σ_m,Σ', sprung_relativ=2.0),
}


def sensitivitaeten_regelwert():
    """Wert der Regel rauschmodelle.sensitivitaeten, den dieser Code umsetzt (Namen und feste Stärken)."""
    return dict(version=SENSITIVITAETEN_VERSION,
                szenarien={k: v['beschreibung'] for k, v in SENSITIVITAETEN.items()})


def sensitivitaet(st, name, plan=None, f=None):
    """Strukturparameter und Effekte einer benannten Sensitivität (feste Stärke) auf der Grundlage st; plan und f
    braucht nur nullpunkt_diffusion (D·13·T_Lauf = σ²_m,Σ bei T_a = N_z/f). Rückgabe (Strukturparameter, Effekte)."""
    if name not in SENSITIVITAETEN:
        raise ValueError(f'Sensitivität {name!r} unbekannt ({", ".join(SENSITIVITAETEN)})')
    st = parameter(st)
    s = dict(SENSITIVITAETEN[name])
    s.pop('beschreibung')
    eff, kw = (), {}
    if 'faktor_K' in s:
        fk = s.pop('faktor_K')
        kw['amp'] = (('L', st.a('L')), ('K', _tupel(_arr(st.a('K')) * fk)))
        kw['phase_grad'] = (('L', st.p('L')), ('K', _tupel(_arr(st.p('K')) * fk)))
    if 'faktor_amp' in s:
        fa = s.pop('faktor_amp')
        kw['amp'] = tuple((x, _tupel(_arr(v) * fa)) for x, v in st.amp)
    if 'diffusion_relativ' in s:
        rel = s.pop('diffusion_relativ')
        if plan is None or f is None:
            raise ValueError('Sensitivität nullpunkt_diffusion verlangt plan und f')
        sm = st.sigma_mittel(plan.n_zyklen / f)
        sm2 = float((np.asarray(sm, float) ** 2).sum()) if np.ndim(sm) else 3.0 * float(sm) ** 2
        kw['nullpunkt_diffusion_N2_je_s'] = rel * sm2 / (13 * plan.T_lauf)
    if 'sprung_relativ' in s:
        rel = s.pop('sprung_relativ')
        if plan is None or f is None:
            raise ValueError('Sensitivität drift_messtage verlangt plan und f')
        sm = st.sigma_mittel(plan.n_zyklen / f)
        kw['nullpunkt_sprung_sd_N'] = rel * float(np.sqrt((np.asarray(sm, float) ** 2).sum() if np.ndim(sm)
                                                           else 3.0 * float(sm) ** 2))
    if 'effekt' in s:
        eff = (dict(s.pop('effekt')),)
    kw.update(s)
    return st.mit(name=f'{st.name}+{name}', herkunft=tuple(st.herkunft) + (('sensitivitaet', name),), **kw), eff


# ── singuläre Kovarianzen (Diagnose, Gauß-Lesart von Option B) ───────────────────────────────────────────
def gauss_unterraum(C, n, rng, rtol=1e-10):
    """n Ziehungen N(0, C) auch für singuläres oder numerisch indefinites C: Eigenzerlegung, Ziehung im Unterraum der
    Eigenwerte > rtol·λ_max; negative Eigenwerte unter der Toleranz werden als null gemeldet, nicht still entfernt.
    Rückgabe (X (n, d), Bericht)."""
    C = np.asarray(C, float)
    C = 0.5 * (C + C.T)
    w, V = np.linalg.eigh(C)
    lmax = max(float(w.max()), 0.0)
    tol = rtol * lmax
    halt = w > tol
    neg = w < -tol
    L = V[:, halt] * np.sqrt(w[halt])
    X = rng.standard_normal((n, int(halt.sum()))) @ L.T
    return X, dict(dimension=int(C.shape[0]), rang=int(halt.sum()), negativ=int(neg.sum()),
                   min_eigenwert=float(w.min()), toleranz=tol,
                   hinweis='Ziehung im Unterraum des Rangs; als Vorhersagemodell nicht ausreichend (Rang, erfasster '
                           'Phasenanteil, Konfigurationsabhängigkeit; Entscheidungsvorlage 5.1)')


def regularisieren(C, boden):
    """C + diag(boden): Regularisierung einer empirischen Kovarianz mit dem (bekannten) Sensorboden je Koordinate;
    macht C positiv definit, wenn boden > 0. Rückgabe (C_reg, Bericht)."""
    C = 0.5 * (np.asarray(C, float) + np.asarray(C, float).T)
    b = np.broadcast_to(np.asarray(boden, float), (C.shape[0],))
    if np.any(b <= 0):
        raise ValueError('Regularisierung: Boden muss positiv sein')
    Cr = C + np.diag(b)
    return Cr, dict(rang_vorher=int(np.linalg.matrix_rank(C)), rang_nachher=int(np.linalg.matrix_rank(Cr)),
                    min_eigenwert=float(np.linalg.eigvalsh(Cr).min()))


# ── Modellquelle ─────────────────────────────────────────────────────────────────────────────────────
@dataclass
class Modellquelle:
    """Quelle der simulierten Kampagnen ohne Szenario: Struktur, Rauschparameter, Δδ̂ⱼ, Kalibrierung (P0.1–P0.5) und
    Herkunft (nur Phase-0-Größen: Prüfsummen, Bindung, Grenze; keine Szenario-ID, keine Wahrheit)."""
    struktur: Struktur
    rausch: object
    delta_delta_grad: object
    kalibrierung: dict
    k_max: int
    name: str = 'phase0'
    effekte: tuple = ()
    herkunft: dict = field(default_factory=dict)

    def modell(self, plan, k_max=None, rausch=None, effekte=None):
        return Phase0Modell(self.struktur, plan, self.delta_delta_grad, self.k_max if k_max is None else k_max,
                            self.rausch if rausch is None else rausch,
                            self.effekte if effekte is None else effekte, name=self.name, herkunft=self.herkunft)

    def mit(self, **kw):
        return replace(self, **kw)

    def kennung(self):
        """Prüfsumme und Beschreibung (für Seeds, Checkpoints und Herkunft)."""
        r = parameter(self.rausch)
        d = dict(name=self.name, struktur=self.struktur.quelle, struktur_herkunft=self.struktur.herkunft,
                 struktur_sha256=formate.sha256_bytes(np.ascontiguousarray(self.struktur.Nz).tobytes()),
                 rausch=r.beschreibung(), delta_delta_grad=self.delta_delta_grad, k_max=self.k_max,
                 effekte=list(self.effekte), kalibrierung_sha256=formate.sha256_json(self.kalibrierung),
                 herkunft=self.herkunft)
        return dict(sha256=formate.sha256_json(d), beschreibung=formate._json_wert(d))


def quelle_aus_phase0(tab, gueltig, kal, lg, grenze='punkt', k_max=None, modell='struktur', name=None):
    """Modellquelle aus den Phase-0-Größen eines Satzes: Struktur aus P0.8 (gültige Läufe), Δδ̂ⱼ aus P0.5, Parameter
    aus den Laufgrößen (modell 'struktur': Strukturmodell, 'familie': Familienanpassung) an der Grenze grenze."""
    s = struktur_p08(tab, gueltig)
    if modell == 'struktur':
        r = aus_laufgroessen(lg, grenze)
    elif modell == 'familie':
        r = familienanpassung(lg, grenze)
    else:
        raise ValueError(f'Modell {modell!r} unbekannt (struktur, familie)')
    k = int(lg['bindung']['k'] if k_max is None else k_max)
    herk = dict(quelle='Phase 0', modell=modell, grenze=grenze, bindung=dict(lg['bindung']),
                laufgroessen_version=lg['version'], struktur=s.quelle, phase0=s.herkunft)
    return Modellquelle(s, r, np.asarray(kal['p0_5']['delta_delta_grad'], float), kal, k,
                        name=name or f'phase0_{modell}_{grenze}', herkunft=herk)
