"""
n2_vollmodell.py – Befunde NR-04 bis NR-06: Der Dreimassenkörper im Nadelrahmen (Vollmodell), starrer Grenzfall
und zum Vergleich mit Rahmendynamik (Belegung B, k_a = 10⁶ N/m).

1. Körper und Profil: V1-Kandidat (3 × 100 g, Hub 8 mm, m0 = 0,35 kg, 10 Hz, Egg) in Lage G0.
2. Moduldyname je Komponente und Harmonischer für T, Z, S und Einzelmodul 1: Auswahlregeln, dynamische
   Nullkanäle F_x, F_y, M_z, Umlaufsinn des Kippmoments.
3. Basislinie der gemessenen Dyname: (M g e_z; r_cm × M g e_z), mit und ohne Schwerpunktversatz.
4. Nadelkräfte der statisch bestimmten Belegung B: Mittel, Extremwerte, Zugbedarf, Harmonische je Nadel.
5. Nadelkräfte der vorspannbaren Belegung C: Lastaufteilung und Vorspannbedarf (Druckkontakt, Reibkontakt).
6. Zeltkurve im Rahmen: F_z,min entlang φ₃ = 240°, starr und mit Rahmendynamik; Kippmoment entlang des Schnitts.
7. Rückrechnung der drei Modulzeiger aus (F_z, M_x, M_y) je Harmonischer.

Laufzeit wenige Sekunden; schreibt keine Dateien.
"""
import numpy as np
from nr_modell import (NAMEN, KOMP, A_REF, D_REF, T_KONFIG, Z_KONFIG, S_KONFIG, Koerper, rahmen, antwort, zeit,
                       dyname, amplituden)

np.set_printoptions(precision=4, suppress=True, linewidth=150)
KONFIG = (('T (0°, 120°, 240°)', T_KONFIG, (1, 1, 1)), ('Z (0°, 110°, 240°)', Z_KONFIG, (1, 1, 1)),
          ('S (0°, 0°, 0°)', S_KONFIG, (1, 1, 1)), ('E1 nur Modul 1', S_KONFIG, (1, 0, 0)))


def kopf(text):
    print('\n' + '=' * 100 + '\n' + text + '\n' + '=' * 100)


def f(x, p=4):
    return f'{round(float(x), p) + 0.0:.{p}f}'


kp = Koerper()
RB = rahmen('B')

# ───────────────────────────── 1. Körper ─────────────────────────────
kopf('1. Dreimassenkörper (V1-Kandidat, Lage G0) – Annahmen siehe nr_modell.py')
print(f'M = {kp.M:.3f} kg, M·g = {kp.MG:.4f} N, bewegter Anteil μ = {kp.mu:.4f}, Hub {kp.hub[0] * 1e3:.1f} mm, '
      f'f = {kp.f:.0f} Hz')
print('Module (Masse, Lage [m]): ' + '; '.join(f'{m:.3f} kg {np.round(R, 4).tolist()}' for m, R in zip(kp.m, kp.R)))
print(f'Schwerpunkt r_cm = {np.round(kp.r_cm, 6).tolist()} m; Trägheit um O J_O = diag '
      f'{np.round(np.diag(kp.J_O), 6).tolist()} kg·m²')
A = kp.hub[0] * kp.f ** 2 * 2 * np.abs(kp.c[1:7])
print('Profilbeschleunigung je Modul, Amplituden A_k [m/s²], k = 1 … 6: ' + '  '.join(f(a, 3) for a in A))

# ───────────────────────────── 2. Moduldyname ─────────────────────────────
kopf('2. Moduldyname w_mod (starrer Grenzfall = gemessene Dyname minus Basislinie): Amplituden 2|w_k|')
print('Kräfte in N, Momente in N·m; R+ / R− = Radius des links / rechts umlaufenden Kippmoments (von oben gesehen)')
for name, phi, aktiv in KONFIG:
    W = kp.w_mod(phi, aktiv)
    amp = amplituden(W)
    print(f'\n{name}')
    print('  Komp.  ' + '  '.join(f'k={k:<6d}' for k in range(1, 7)))
    for i, c in enumerate(KOMP):
        print(f'  {c:5s}  ' + '  '.join(f'{f(a):8s}' for a in amp[i]))
    X, Y = W[3, 1:7], W[4, 1:7]
    print('  R+     ' + '  '.join(f'{f(a):8s}' for a in np.abs(X + 1j * Y)))
    print('  R−     ' + '  '.join(f'{f(a):8s}' for a in np.abs(X - 1j * Y)))
    print(f'  max|F_x|, max|F_y|, max|M_z| über die Periode: '
          f'{np.abs(zeit(W[[0, 1, 5]])).max():.1e} (dynamische Nullkanäle bei senkrechter Modulführung)')
W_T = kp.w_mod(T_KONFIG)
nz = [k for k in range(1, 13) if abs(W_T[2, k]) > 1e-12]
nm = [k for k in range(1, 13) if abs(W_T[3, k]) + abs(W_T[4, k]) > 1e-12]
print(f'\nT, k = 1 … 12: F_z ≠ 0 nur für k = {nz}; M_x, M_y ≠ 0 nur für k = {nm}')
print('Auswahlregel wie Prüfgruppe kippmoment (KM-03), hier für alle sechs Komponenten des gehaltenen Körpers.')

# ───────────────────────────── 3. Basislinie ─────────────────────────────
kopf('3. Basislinie der gemessenen Dyname (Zeitmittel über ganze Perioden, eingeschwungen)')
for r_cm in ((0.0, 0.0, 0.0), (0.005, -0.003, 0.02)):
    kb = Koerper(r0=np.asarray(r_cm) * Koerper().M / Koerper().m0)
    lam = antwort(kb, RB, T_KONFIG, starr=True)
    w_mittel = dyname(RB, zeit(lam)).mean(axis=1)
    print(f'r_cm = {np.round(kb.r_cm * 1e3, 2).tolist()} mm:  ⟨w_mess⟩ = '
          + '  '.join(f'{c}={round(float(x), 5) + 0.0:+.5f}' for c, x in zip(KOMP, w_mittel)))
    print(f'{"":30s}Basislinie (M g e_z; r_cm × M g e_z) = '
          + '  '.join(f'{c}={round(float(x), 5) + 0.0:+.5f}' for c, x in zip(KOMP, kb.basis())))
print('Mittel der Momente = r_cm × M g e_z = M g (y_cm, −x_cm, 0); hängt nur von der waagerechten Schwerpunktlage ab.')
print('Bei senkrechter Modulbewegung ist sie von der Phasenlage unabhängig: Δ⟨w⟩ zwischen Zuständen = 0 in allen')
print('sechs Komponenten, in B auch für jede einzelne Nadel (Befund NR-05).')

# ───────────────────────────── 4. Nadelkräfte B ─────────────────────────────
kopf(f'4. Belegung B (versetzt, statisch bestimmt, A = {A_REF} m): Nadelkräfte im starren Grenzfall [N]')
for name, phi, aktiv in KONFIG[:3]:
    lam = antwort(kp, RB, phi, starr=True, aktiv=aktiv)
    q = zeit(lam).real
    amp = amplituden(lam)
    print(f'\n{name}')
    print('  Nadel   Mittel     min      max    Spitze-Sp.  Zug?   2|q_k|, k = 1 … 6')
    for j, nmn in enumerate(NAMEN):
        zug = 'immer' if q[j].max() < -1e-9 else ('zeitw.' if q[j].min() < -1e-9 else 'nein')
        print(f'  {nmn:6s} {f(q[j].mean(), 3):>7s}  {f(q[j].min(), 3):>7s}  {f(q[j].max(), 3):>7s}  '
              f'{f(q[j].max() - q[j].min(), 3):>8s}   {zug:6s} ' + '  '.join(f'{f(a, 3):>6s}' for a in amp[j]))
print('\nOst/West: ∓F_x/2 + M_z/(2A) → bei senkrechter Modulführung im starren Grenzfall lastfrei (Nullkanäle).')
print('Nord/Süd: ∓F_y/2 + M_x/(2A) → nur k ≢ 0 (mod 3) am Triphasik-Punkt, Vorzeichenwechsel → zugfest nötig.')
print('oben/unten: ∓F_z/2 + M_y/(2A) → beide Klassen von Harmonischen; oben trägt im Mittel Zug (Mg/2).')

# ───────────────────────────── 5. Nadelkräfte C ─────────────────────────────
kopf('5. Belegung C (zentral, drei Kraftkomponenten je Nadel): Lastaufteilung und Vorspannbedarf, starr')
MU_S = 0.2
for k_t in (2e4, 1e5):
    RC = rahmen('C', k_t=k_t)
    ax = np.flatnonzero(RC.axial)
    print(f'\nk_a = 1e6 N/m, k_t = {k_t:.0e} N/m (k_t/k_a = {k_t / 1e6:g})')
    lam0 = antwort(kp, RC, T_KONFIG, starr=True)[:, 0].real
    print('  statisch ohne Vorspannung, axial [N]: ' + '  '.join(f'{n}={round(float(x), 3) + 0.0:+.3f}' for n, x in
                                                               zip(NAMEN, lam0[ax])))
    anteil = (lam0[ax][5] - lam0[ax][4]) / kp.MG
    print(f'  Anteil des Gewichts über die axialen Komponenten oben/unten: {anteil:.4f}; '
          f'Rest über Querkomponenten der Seitennadeln: {1 - anteil:.4f}')
    print('  Konfig.   Nadel   axial min   axial max   quer max   P_Druck   P_Reib(μ_s=0,2)')
    for name, phi, aktiv in KONFIG[:3]:
        lt = zeit(antwort(kp, RC, phi, starr=True, aktiv=aktiv)).real
        for j, nmn in enumerate(NAMEN):
            a = lt[ax[j]]
            qn = np.hypot(lt[ax[j] + 1], lt[ax[j] + 2])
            p_druck = max(0.0, -a.min())
            p_reib = max(0.0, (qn / MU_S - a).max())
            print(f'  {name[:1]:8s}  {nmn:6s}  {round(a.min(), 3) + 0.0:+9.3f}  {round(a.max(), 3) + 0.0:+9.3f}  {qn.max():8.3f}  {p_druck:8.3f}  '
                  f'{p_reib:8.3f}')
print('\nP_Druck: Vorspannung je Nadelpaar, damit die axiale Komponente nie Zug wird (Druckkontakt an der Schnittstelle).')
print('P_Reib: Vorspannung, damit eine reibschlüssig übertragene Querkraft im Haftbereich bleibt (μ_s = 0,2 angenommen).')
print('Mit gefangenem Kugelgelenk (zugfest) entfällt beides; die Vorspannung ist dann frei wählbar (Nullraum).')

# ───────────────────────────── 6. Zeltkurve ─────────────────────────────
kopf('6. Zeltkurve im Rahmen: F_z,min entlang φ₃ = 240° (starr und mit Rahmendynamik B, k_a = 1e6 N/m)')
print('  φ₂     F_z,min starr   F_z,min B dyn.   R+₁ [N·m]   R−₁ [N·m]   max|M| starr')
werte = []
for p2 in np.arange(100.0, 140.0 + 1e-9, 2.0):
    phi = (0.0, p2, 240.0)
    W = kp.w_mod(phi)
    fz = kp.MG + zeit(W[2]).real
    lam = antwort(kp, RB, phi)
    fz_dyn = dyname(RB, zeit(lam))[2].real
    m = zeit(W[3:5]).real
    werte.append((p2, fz.min(), fz_dyn.min()))
    print(f'  {p2:5.1f}   {fz.min():12.4f}   {fz_dyn.min():13.4f}   {abs(W[3, 1] + 1j * W[4, 1]):9.4f}   '
          f'{abs(W[3, 1] - 1j * W[4, 1]):9.4f}   {np.hypot(*m).max():10.4f}')
werte = np.array(werte)
i120 = int(np.argmin(np.abs(werte[:, 0] - 120.0)))
print(f'Spitze bei 120°: starr {werte[i120, 1]:.4f} N, dynamisch {werte[i120, 2]:.4f} N; Spannweite über den Schnitt '
      f'starr {werte[i120, 1] - werte[:, 1].min():.4f} N, dynamisch {werte[i120, 2] - werte[:, 2].min():.4f} N')
fz_min_s = kp.MG + zeit(kp.w_mod(S_KONFIG)[2]).real.min()
print(f'F_z,min synchron (S) = {fz_min_s:.4f} N > 0: Der V1-Kandidat bleibt in allen Phasenlagen im Kontaktast '
      f'(ε = {1 - fz_min_s / kp.MG:.4f}).')
print('Im starren Grenzfall ist F_z(t) = M g + Σ m_i s̈_i(t) dieselbe Funktion wie N(t) der starren Auflage, solange')
print('diese nicht abhebt; beim V1-Kandidaten also überall. Der Rahmen misst dort dieselbe vertikale Wellenform und')
print('zusätzlich die übrigen fünf Komponenten. Abheben gibt es im Rahmen nicht: F_z < 0 trägt die Nadel oben.')

# ───────────────────────────── 7. Modulzeiger ─────────────────────────────
kopf('7. Rückrechnung der drei Modulzeiger g_i,k = m_i·a_i,k aus (F_z, M_x, M_y) je Harmonischer')
Bm = np.vstack((np.ones(3), kp.Rxez[:, 0], kp.Rxez[:, 1]))     # (F_z, M_x, M_y) = Bm · g
Bs = Bm.copy()
Bs[1:] /= 0.10
print(f'Matrix (F_z; M_x/R_m; M_y/R_m) = B·g, Kondition {np.linalg.cond(Bs):.4f} (Lage G0, R_m = 0,10 m)')
k_st = Koerper(m=(0.1, 0.101, 0.1))
phi_st = (0.0, 121.0, 240.0)
W_st, W_0 = k_st.w_mod(phi_st), kp.w_mod(T_KONFIG)
for k in (1, 2, 3):
    g = np.linalg.solve(Bm, W_st[2:5, k])
    g0 = np.linalg.solve(Bm, W_0[2:5, k])
    rel = g / g0
    print(f'  k = {k}: |g_i/g_i,nom| = ' + '  '.join(f'{abs(r):.5f}' for r in rel)
          + '   Phase [°] = ' + '  '.join(f'{round(float(np.degrees(np.angle(r))), 3) + 0.0:+.3f}' for r in rel))
print('Störung: Modul 2 mit +1 % Masse und +1° Phase (φ₂ = 121°). Erwartet: Betrag 1,01, Phase −k·1° nur bei Modul 2.')
