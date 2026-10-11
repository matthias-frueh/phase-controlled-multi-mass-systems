"""
nr_modell.py – Sechs-Nadel-Messrahmen mit eingebettetem Dreimassenkörper (Vollmodell).

Stand 11.10.2026 · Simulation und Analytik, keine Messdaten, keine gebaute Apparatur. Alle Geometrien,
Steifigkeiten und Trägheiten sind Rechenbeispiele (Annahmen), keine Bauvorgabe.

Eigene Implementierung; aus dem Repository werden nur die Profilfunktion `profil` und der V1-Kandidat
`KANDIDAT` aus code/auslegung.py importiert (über PYTHONPATH), damit Profil und Massen identisch sind.

Koordinaten und Bezeichnungen
-----------------------------
Rechtshändig: x nach Ost, y nach Nord, z nach oben; Bezugspunkt O = Rahmenmitte (nominale Körpermitte),
ortsfest. Schwerkraft g = −g·e_z. Nadeln j in der Reihenfolge der Festhaltung vom 11.10.2026:
Nord, Süd, Ost, West, oben, unten. Jede Nadel ist genau ein Lastpfad: Fixierstelle am Körper, eine
Kontaktfläche zu ihrer eigenen Messschnittstelle. Angriffspunkt r_j der Pfadkraft in der Bilanz: bei art 'a' ein
Punkt der Wirkungslinie (Fixierstelle), bei art 'k' die Kugelgelenkmitte an der Schnittstelle (die Fixierstelle
liegt dort um die Nadellänge weiter innen). Eigener Bezug je Nadel: lokales Dreibein (n_j, t_j1, t_j2)
mit n_j = Druckrichtung auf den Körper (von der Schnittstelle zum Körper), t_j1 = nächste Achse zyklisch,
t_j2 = n_j × t_j1.

Übertragene Komponenten einer Nadel (Index c):
  art 'a'  eine gemessene Komponente λ_ja entlang n_j (Zweigelenkstab oder reibungsfreie Druckspitze);
           optional zwei ungemessene Querkomponenten mit Steifigkeit k_q (Nebenschluss, Befund NR-07)
  art 'k'  drei gemessene Kraftkomponenten (Nadel an der Fixierstelle fest, an der Schnittstelle
           kugelgelenkig; Schnittstelle misst die Kraft in n_j, t_j1, t_j2)
Komponente c der Nadel j wirkt auf den Körper mit λ_jc·e_jc; λ_ja > 0 heißt Druck, λ_ja < 0 Zug.
Dyname w = (F; τ_O) um O, G_jc = (e_jc; r_j × e_jc):   w = Σ G_jc λ_jc = G·λ.

Körper (Dreimassenkörper)
-------------------------
Träger (Masse m0, Schwerpunkt r0, Hauptträgheitsradien rho0 um r0) und drei Module (m_i) bei
R_i = (R_m cos ψ_i, R_m sin ψ_i, z_m), relativ zum Träger senkrecht geführt:
    s̈_i(t) = Hub·f²·ã(f·t − φ_i/360°)        (Egg-Profil wie Engine und Auslegung, φ verzögert)
Vorgabe: V1-Kandidat 3 × 100 g, Hub 8 mm Spitze-Spitze, m0 = 0,35 kg, f = 10 Hz; Lage G0 (R_m = 100 mm,
ψ = 0°, 120°, 240°); Trägerträgheit isotrop mit ρ0 = 80 mm. Lage und Trägheit sind Annahmen.

Bewegungsgleichung (kleine Bewegung x = (u; θ) des Körpers, Rahmen starr und ortsfest)
-----------------------------------------------------------------------------------------
    M6·ẍ + C·ẋ + K·x = w_g − w_mod(t)
    M6 = [[M·I, −M·[r_cm]×], [M·[r_cm]×, J_O]],   K = Σ k_jc G_jc G_jcᵀ,   C = β·K
    w_g      = (−M g e_z; r_cm × (−M g e_z))                 Gewichtsdyname um O
    w_mod(t) = Σ_i m_i s̈_i(t)·(e_z; R_i × e_z)                 Dyname der Modul-Relativbeschleunigung
Nadelkräfte λ_jc(t) = λ_V,jc − k_jc G_jcᵀ (x + β ẋ), λ_V Vorspannung im Nullraum von G (G·λ_V = 0).
Übertragene Dyname G·λ = −w_g + w_mod + M6·ẍ; gemessen wird G_m·λ_m (nur gemessene Komponenten), gleich G·λ,
solange keine Nadel ungemessene Komponenten überträgt (Befund NR-07). Starrer Grenzfall (Halterungsmoden ≫ k·f):
G·λ = −w_g + w_mod, unabhängig vom Kontakt. Je Harmonischer k (ω_k = 2πf·k), Z_k = K − ω_k² M6 + iω_k β K:
    λ_jc,k = k_jc (1 + iω_k β) G_jcᵀ Z_k⁻¹ w_mod,k,     w_mess,k = (1 + iω_k β) K Z_k⁻¹ w_mod,k.
Halterungsmoden = Eigenmoden des Körpers auf den elastischen Nadeln; die Rahmenstruktur ist starr und ortsfest.
Dämpfung steifigkeitsproportional, β so, dass die tiefste Halterungsmode ζ hat (Annahme, Vorgabe ζ = 0,02).
Gültig, solange jede Nadel in ihrem Kontaktzustand bleibt (Druckspitze: λ_a > 0; Reibkontakt:
|λ_t| ≤ μ_s·λ_a). Geometrische Steifigkeit aus Vorspannung und Gewicht und die Masse der Nadeln sind
vernachlässigt; freie Kontaktmomente τ^c_j an den Schnittstellen sind nicht modelliert (ideale Gelenke, Spitzen und
Kugelgelenke, τ^c_j = 0) (Annahmen).

Einheiten SI; Phasen an den Schnittstellen in Grad.
"""
import numpy as np
from auslegung import profil, KANDIDAT, THOLD, G

NAMEN = ('Nord', 'Süd', 'Ost', 'West', 'oben', 'unten')     # Reihenfolge der Festhaltung (11.10.2026)
EX, EY, EZ = np.eye(3)
AUSSEN = {'Nord': EY, 'Süd': -EY, 'Ost': EX, 'West': -EX, 'oben': EZ, 'unten': -EZ}   # Lage der Schnittstelle
ACHSE = {'Nord': 1, 'Süd': 1, 'Ost': 0, 'West': 0, 'oben': 2, 'unten': 2}
KOMP = ('Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz')
D_REF, A_REF = 0.15, 0.04          # Abstand der Angriffspunkte von O, Versatz der Wirkungslinien [m] (Beispiele)
K_A_REF = 1e6                      # axiale Nadelsteifigkeit [N/m] (Beispiel)
ZETA_REF = 0.02                    # Dämpfungsgrad der tiefsten Halterungsmode (Annahme)
N_PER = 16000                      # Stützstellen je Periode (wie N_FEIN in code/auslegung.py)
T_KONFIG = (0.0, 120.0, 240.0)     # Triphasik-Punkt
Z_KONFIG = (0.0, 110.0, 240.0)     # Zeltschnittpunkt (wie Prüfgruppe kippmoment)
S_KONFIG = (0.0, 0.0, 0.0)         # synchron


def kreuzmatrix(r):
    """[r]× mit [r]×·v = r × v."""
    x, y, z = r
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def dreibein(name):
    """Eigener Bezug der Nadel: n = Druckrichtung auf den Körper, t1 = nächste Achse zyklisch, t2 = n × t1."""
    n = -AUSSEN[name]
    t1 = np.eye(3)[(ACHSE[name] + 1) % 3]
    return n, t1, np.cross(n, t1)


def nadel(name, versatz=(0.0, 0.0, 0.0), D=D_REF, art='a', k_a=K_A_REF, k_t=0.0, k_q=0.0, n=None, r=None):
    """Eine Nadel mit Angriffspunkt r = D·aussen + versatz (oder r direkt) und Druckrichtung n (Vorgabe −aussen);
    r ist bei art 'a' die Fixierstelle auf der Wirkungslinie, bei art 'k' die Kugelgelenkmitte.
    art 'a': eine gemessene axiale Komponente, k_q > 0 fügt zwei ungemessene Querkomponenten hinzu.
    art 'k': drei gemessene Kraftkomponenten (axial k_a, quer k_t)."""
    nn, t1, t2 = dreibein(name) if n is None else _dreibein_frei(n)
    rr = D * AUSSEN[name] + np.asarray(versatz, float) if r is None else np.asarray(r, float)
    komp = [dict(e=nn, k=k_a, gemessen=True, typ='a')]
    if art == 'k':
        komp += [dict(e=t1, k=k_t, gemessen=True, typ='t1'), dict(e=t2, k=k_t, gemessen=True, typ='t2')]
    elif art == 'a':
        if k_q > 0:
            komp += [dict(e=t1, k=k_q, gemessen=False, typ='q1'), dict(e=t2, k=k_q, gemessen=False, typ='q2')]
    else:
        raise ValueError(f'unbekannte Nadelart {art!r}')
    return dict(name=name, r=rr, n=nn, t1=t1, t2=t2, art=art, komp=komp)


def _dreibein_frei(n):
    n = np.asarray(n, float) / np.linalg.norm(n)
    h = EX if abs(n[0]) < 0.9 else EY
    t1 = np.cross(n, h)
    t1 /= np.linalg.norm(t1)
    return n, t1, np.cross(n, t1)


def versatz(variante, name, A=A_REF):
    """Versatz des Angriffspunkts aus der Flächenmitte für die vorgefertigten Belegungen."""
    a, s = ACHSE[name], AUSSEN[name][ACHSE[name]]
    if variante in ('A', 'C'):
        return np.zeros(3)
    if variante == 'B':               # zyklisch gegensinnig: Ost/West ±A in y, Nord/Süd in z, oben/unten in x
        return s * A * np.eye(3)[(a + 1) % 3]
    if variante == 'B2':              # andere Zuordnung: Ost/West in z, Nord/Süd in x, oben/unten in y
        return s * A * np.eye(3)[(a + 2) % 3]
    if variante == 'Bg':              # gleichseitig: beide Nadeln eines Paars auf derselben Wirkungslinie
        return A * np.eye(3)[(a + 1) % 3]
    raise ValueError(f'unbekannte Belegung {variante!r}')


def rahmen(variante, D=D_REF, A=A_REF, k_a=K_A_REF, k_t=0.0, k_q=0.0):
    """Vorgefertigte Belegungen (Rechenbeispiele):
    'A'  zentral, axial: alle Wirkungslinien durch O (Rang 3)
    'B'  versetzt, axial, zyklisch gegensinnig (Rang 6, statisch bestimmt)
    'B2' versetzt, axial, andere zyklische Zuordnung (Rang 6)
    'Bg' gleichseitig versetzt (alle drei Paare: Rang 3; je gleichseitiges Paar ein Rang weniger)
    'C'  zentral, drei Kraftkomponenten je Nadel (Rang 6, Nullraum 12, vorspannbar)"""
    art = 'k' if variante == 'C' else 'a'
    return Rahmen([nadel(nm, versatz(variante, nm, A), D, art, k_a, k_t, k_q) for nm in NAMEN],
                  bezeichnung=variante)


class Rahmen:
    """Nadelsatz mit Matrix G (6 × n_c), Steifigkeiten und Kennzeichnung gemessener Komponenten."""

    def __init__(self, nadeln, bezeichnung=''):
        self.nadeln = nadeln
        self.bezeichnung = bezeichnung
        zeilen = [(j, c) for j, nd in enumerate(nadeln) for c in nd['komp']]
        self.j = np.array([j for j, _ in zeilen])
        self.typ = [c['typ'] for _, c in zeilen]
        E = np.array([c['e'] for _, c in zeilen])
        R = np.array([nadeln[j]['r'] for j, _ in zeilen])
        self.k = np.array([c['k'] for _, c in zeilen], float)
        self.gem = np.array([c['gemessen'] for _, c in zeilen])
        self.G = np.vstack((E.T, np.cross(R, E).T))
        self.K = (self.G * self.k) @ self.G.T
        self.axial = np.array([t == 'a' for t in self.typ])

    @property
    def Gm(self):
        return self.G[:, self.gem]

    def rang(self, l_ref, nur_gemessen=True):
        """Rang, Nullraumdimension und Kondition von [F; M/l_ref] (Kondition ∞ bei Rang < 6)."""
        Gs = (self.Gm if nur_gemessen else self.G).copy()
        Gs[3:] /= l_ref
        s = np.linalg.svd(Gs, compute_uv=False)
        r = int((s > max(Gs.shape) * np.finfo(float).eps * s[0]).sum())
        return r, Gs.shape[1] - r, (s[0] / s[5] if r == 6 else np.inf), s

    def blind(self, l_ref, nur_gemessen=True, tol=1e-9):
        """Basis der Lastrichtungen (skaliert [F; M/l_ref]), die die Komponenten nicht sehen (Linksnullraum)."""
        Gs = (self.Gm if nur_gemessen else self.G).copy()
        Gs[3:] /= l_ref
        U, s, _ = np.linalg.svd(Gs)
        r = int((s > tol * s[0]).sum())
        return U[:, r:]

    def nullraum(self, nur_gemessen=False, tol=1e-9):
        """Basis der selbstgleichgewichtigen Komponentenzustände (G·λ = 0): Vorspannung, Lastumlagerung."""
        Gx = self.Gm if nur_gemessen else self.G
        _, s, Vt = np.linalg.svd(Gx)
        r = int((s > tol * s[0]).sum())
        return Vt[r:].T

    def namen_komp(self):
        return [f"{self.nadeln[j]['name']}/{t}" for j, t in zip(self.j, self.typ)]


def formschluss(W, l_ref=D_REF, tol=1e-9):
    """Positive Aufspannung des R⁶ durch die Spalten von W (einseitige, reibungsfreie Kontakte; jeder Kontakt kann
    nur drücken). Gilt genau dann, wenn Rang W = 6 und ein λ > 0 mit W·λ = 0 existiert. Lineares Programm:
    max t unter W·λ = 0, λ ≥ t, Σλ = 1. Rückgabe (Formschluss, t*, Rang, λ*)."""
    from scipy.optimize import linprog
    Ws = np.asarray(W, float).copy()
    Ws[3:] /= l_ref
    n = Ws.shape[1]
    res = linprog(np.r_[np.zeros(n), -1.0],
                  A_ub=np.c_[-np.eye(n), np.ones(n)], b_ub=np.zeros(n),
                  A_eq=np.vstack((np.c_[Ws, np.zeros(6)], np.r_[np.ones(n), 0.0])), b_eq=np.r_[np.zeros(6), 1.0],
                  bounds=[(0, None)] * n + [(None, None)], method='highs')
    t = -res.fun if res.status == 0 else -np.inf
    rang = int(np.linalg.matrix_rank(Ws))
    lam = res.x[:n] if res.status == 0 else None
    return bool(rang == 6 and t > tol), t, rang, lam


class Koerper:
    """Dreimassenkörper (Träger + drei senkrecht geführte Module), Vorgabe V1-Kandidat in Lage G0."""

    def __init__(self, m=KANDIDAT['m'], hub=KANDIDAT['hub'], m0=KANDIDAT['m0'], f=KANDIDAT['f'], R_m=0.10,
                 psi_deg=(0.0, 120.0, 240.0), z_m=0.0, r0=(0.0, 0.0, 0.0), rho0=(0.08, 0.08, 0.08),
                 profil_art='egg', n=N_PER):
        self.m = np.asarray(m, float)
        self.hub = np.broadcast_to(np.asarray(hub, float), self.m.shape).astype(float)
        self.m0, self.f, self.n = float(m0), float(f), int(n)
        psi = np.radians(np.asarray(psi_deg, float))
        self.R = np.c_[R_m * np.cos(psi), R_m * np.sin(psi), np.full(self.m.size, float(z_m))]
        self.r0 = np.asarray(r0, float)
        self.M = self.m0 + self.m.sum()
        self.MG = self.M * G
        self.mu = self.m.sum() / self.M
        self.r_cm = (self.m0 * self.r0 + self.m @ self.R) / self.M

        def punkt(mm, r):
            return mm * ((r @ r) * np.eye(3) - np.outer(r, r))

        J0 = self.m0 * np.diag(np.asarray(rho0, float) ** 2)
        self.J_O = J0 + punkt(self.m0, self.r0) + sum(punkt(mi, Ri) for mi, Ri in zip(self.m, self.R))
        S = kreuzmatrix(self.M * self.r_cm)
        self.M6 = np.block([[self.M * np.eye(3), -S], [S, self.J_O]])
        c = np.fft.rfft(profil(self.n, profil_art, THOLD)) / self.n
        c[0] = 0.0                       # Gleichanteil exakt null (∫a dt = 0), wie linear_solver.py
        self.c = c
        self.kk = np.arange(c.size)
        self.omega = 2 * np.pi * self.f * self.kk
        self.Rxez = np.cross(self.R, EZ)       # R_i × e_z

    def w_g(self):
        """Gewichtsdyname um O (auf den Körper)."""
        F = np.array([0.0, 0.0, -self.MG])
        return np.r_[F, np.cross(self.r_cm, F)]

    def basis(self):
        """Statische Basislinie der gemessenen Dyname: −w_g = (M g e_z; r_cm × M g e_z) (Befund P1)."""
        return -self.w_g()

    def w_mod(self, phi_deg=T_KONFIG, aktiv=(1.0, 1.0, 1.0)):
        """Koeffizienten (6 × n_k) der Moduldyname, w(t) = Σ_k≥1 2·Re(w_k e^{ikωt})."""
        phi = np.radians(np.asarray(phi_deg, float))
        amp = self.m * self.hub * self.f ** 2 * np.asarray(aktiv, float)
        a = amp[:, None] * self.c[None, :] * np.exp(-1j * np.outer(phi, self.kk))
        W = np.zeros((6, self.kk.size), complex)
        W[2] = a.sum(0)
        W[3:] = self.Rxez.T @ a
        return W


def moden(koerper, rahmen_):
    """Eigenfrequenzen [Hz] und massennormierte Moden des gehaltenen Körpers (ungedämpft)."""
    from scipy.linalg import eigh
    w2, Phi = eigh(rahmen_.K, koerper.M6)
    return np.sqrt(np.clip(w2, 0.0, None)) / (2 * np.pi), Phi


def beta_daempfung(koerper, rahmen_, zeta=ZETA_REF):
    """β der steifigkeitsproportionalen Dämpfung C = β·K mit ζ an der tiefsten Mode."""
    f1 = moden(koerper, rahmen_)[0][0]
    return 2 * zeta / (2 * np.pi * f1) if f1 > 0 else 0.0


def antwort(koerper, rahmen_, phi_deg=T_KONFIG, starr=False, zeta=ZETA_REF, aktiv=(1.0, 1.0, 1.0),
            vorspannung=None):
    """Komponentenkräfte λ (n_c × n_k, Spalte 0 = statischer Wert) für Gewicht und Modulbewegung.
    starr: quasistatische Verteilung über die Steifigkeiten (Halterungsmoden ≫ k·f).
    vorspannung: λ_V (n_c) im Nullraum von G (wird geprüft)."""
    Gx, k, K = rahmen_.G, rahmen_.k, rahmen_.K
    W = koerper.w_mod(phi_deg, aktiv)
    lam = np.zeros((Gx.shape[1], W.shape[1]), complex)
    lam[:, 0] = -k * (Gx.T @ np.linalg.solve(K, koerper.w_g()))
    if vorspannung is not None:
        lv = np.asarray(vorspannung, float)
        if np.abs(Gx @ lv).max() > 1e-9 * max(1.0, np.abs(lv).max()):
            raise ValueError('Vorspannung liegt nicht im Nullraum von G')
        lam[:, 0] += lv
    if starr:
        lam[:, 1:] = k[:, None] * (Gx.T @ np.linalg.solve(K, W[:, 1:]))
        return lam
    beta = beta_daempfung(koerper, rahmen_, zeta)
    w = koerper.omega[1:]
    Z = K[None] - w[:, None, None] ** 2 * koerper.M6[None] + 1j * (w * beta)[:, None, None] * K[None]
    X = np.linalg.solve(Z, W[:, 1:].T[:, :, None])[:, :, 0].T          # Z_k⁻¹ w_mod,k, (6 × n_k−1)
    lam[:, 1:] = (k[:, None] * (1 + 1j * w * beta)[None, :]) * (Gx.T @ X)
    return lam


def uebertragung(koerper, rahmen_, k_harm, zeta=ZETA_REF):
    """Übertragungsmatrix T(kω) = (1 + iωβ)·K·Z⁻¹ von der Moduldyname zur Nadeldyname (alle Komponenten)."""
    beta = beta_daempfung(koerper, rahmen_, zeta)
    w = 2 * np.pi * koerper.f * k_harm
    Z = rahmen_.K - w ** 2 * koerper.M6 + 1j * w * beta * rahmen_.K
    return (1 + 1j * w * beta) * rahmen_.K @ np.linalg.inv(Z)


def zeit(coef):
    """Zeitverlauf über eine Periode aus einseitigen Koeffizienten (letzte Achse k = 0 … n/2)."""
    n = 2 * (coef.shape[-1] - 1)
    return np.fft.irfft(coef * n, n, axis=-1)


def dyname(rahmen_, lam, nur_gemessen=True):
    """Dyname aus Komponentenkräften (Koeffizienten oder Zeitreihen); nur gemessene oder alle Komponenten."""
    sel = rahmen_.gem if nur_gemessen else np.ones(rahmen_.gem.size, bool)
    return rahmen_.G[:, sel] @ lam[sel]


def amplituden(coef, kmax=6):
    """Amplituden 2|c_k| der Harmonischen k = 1 … kmax (halbe Spitze-Spitze-Werte je Harmonischer)."""
    return 2 * np.abs(coef[..., 1:kmax + 1])
