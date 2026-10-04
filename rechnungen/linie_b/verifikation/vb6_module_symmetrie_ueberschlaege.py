#!/usr/bin/env python3
"""
Gegenprüfung LB-09, LB-14 (Luftkräfte an den Modulen, Gleichanteil, Zeitumkehrsymmetrie) und LB-12/LB-13 (Überschläge).

UNABHÄNGIGER RECHENWEG:
  - Modul-Harmonische ANALYTISCH (geschlossene Fourierintegrale der Halbsinus-Lagebögen), nicht per FFT.
  - Zeitumkehrsymmetrie des Linie-A-Egg z(t* - t) = z(t) numerisch geprüft; daraus <f(v)> = 0 für jede ungerade
    Momentanfunktion f; Prüfung der Aussage "F_bar_A ungerade unter phi -> -phi" an Kombinationen.
  - Impulsbilanz im geschlossenen Gehäuse: Kraft der Innenluft auf das Gesamtsystem = -rho_L V_mod a_mod
    (Innenluft-Schwerpunkt verschiebt sich gegenläufig), Gleichanteil exakt 0 (periodisch).
  - Kraftamplituden für Kugel/Scheibe (wie Gruppe, Formeln Stokes 1851 bzw. Potentialtheorie) zum Zahlenabgleich.
  - Überschläge: Auftrieb rho g V, Elektrostatik sigma^2 A/(2 eps0), Feldstärke sigma/eps0 gegen Durchschlag 3 MV/m.
ANNAHMEN wie Gruppe: Kugel R = 1,45 cm (100 g Stahl), Scheibe breitseitig R = 4 cm, Luft 20 °C.
"""
import numpy as np

F = 10.0; T = 1 / F; W1 = 2 * np.pi * F
THOLD = 0.65; TFAST = 1 - THOLD
RTOP = 0.005; RBOT = RTOP * TFAST / THOLD
RHO, MU, CS = 1.2, 1.8e-5, 343.0
NU = MU / RHO
U_C = 0.0327


def z_egg(ph):
    ph = np.mod(ph, 1.0)
    return np.where(ph < THOLD, RTOP * np.sin(np.pi * ph / THOLD), -RBOT * np.sin(np.pi * (ph - THOLD) / TFAST))


def v_egg(ph):
    ph = np.mod(ph, 1.0)
    return np.where(ph < THOLD, RTOP * np.pi / (THOLD * T) * np.cos(np.pi * ph / THOLD),
                    -RBOT * np.pi / (TFAST * T) * np.cos(np.pi * (ph - THOLD) / TFAST))


def zk_analytisch(k):
    """(1/T) int z e^{-ik W1 t} dt für Halbsinus-Lagebögen; v_k = i k W1 z_k, a_k = -(k W1)^2 z_k."""
    Om = k * W1
    L1, L2 = THOLD * T, TFAST * T
    a1, a2 = np.pi / L1, np.pi / L2
    I1 = a1 * (1 + np.exp(-1j * Om * L1)) / (a1**2 - Om**2)
    I2 = np.exp(-1j * Om * L1) * a2 * (1 + np.exp(-1j * Om * L2)) / (a2**2 - Om**2)
    return (RTOP * I1 - RBOT * I2) / T


def main():
    print("=" * 110)
    print("vb6 – Module, Symmetrie, Überschläge")
    print("=" * 110)
    k = np.arange(1, 6)
    zk = zk_analytisch(k)
    vk = 2 * np.abs(1j * k * W1 * zk)
    ak = 2 * np.abs((k * W1) ** 2 * zk)
    print("Analytische Amplituden (einseitig): |v_k| m/s =", " ".join(f"{x:.4e}" for x in vk))
    print("                                    |a_k| m/s^2 =", " ".join(f"{x:.4e}" for x in ak))
    N = 200000
    ph = (np.arange(N) + 0.5) / N
    z = z_egg(ph); v = v_egg(ph)
    print(f"Hub {np.ptp(z)*1e3:.4f} mm, v_max {np.abs(v).max():.4f} m/s")
    # Zeitumkehr: z(t*-t) = z(t) mit t* = THOLD*T (Mitte der Halte- und der Schnellphase sind Spiegelpunkte)
    zr = z_egg(THOLD - ph)
    print(f"Zeitumkehrsymmetrie max|z(t*-t) - z(t)| = {np.abs(zr - z).max():.2e} m (t* = THOLD*T)")
    print(f"<v|v|> = {np.mean(v*np.abs(v)):+.2e}, <v^3> = {np.mean(v**3):+.2e}, <v^5> = {np.mean(v**5):+.2e} (ungerade -> 0)")
    # Gegenprobe: Raum-Zeit-Antisymmetrie z(t+D) = -z(t)? -> nicht vorhanden (sonst wäre auch jede gerade Mittelung 0)
    best = min(np.abs(z_egg(ph + d) + z).max() for d in np.linspace(0, 1, 2001))
    print(f"Antisymmetrie z(t+D) = -z(t): bestes max|.| über D = {best*1e3:.3f} mm (nicht erfüllt -> 3. Ordnung mit Gedächtnis"
          " nicht durch Symmetrie ausgeschlossen)")
    # F_bar_A ~ <V|V|> für Kombinationen
    print("Zweiterm-Gleichrichtung <V|V|>, V = Summe der drei Modulgeschwindigkeiten / 3:")
    for p2, p3 in [(0, 0), (120, 240), (100, 240), (260, 120), (140, 240), (220, 120)]:
        V = (v_egg(ph) + v_egg(ph - p2 / 360) + v_egg(ph - p3 / 360)) / 3
        print(f"   ({p2:3d},{p3:3d}): <V|V|> = {np.mean(V*np.abs(V)):+.3e} m^2/s^2")
    print("   (100,240) und (260,120) = (-100,-240) mod 360 sowie (140,240)/(220,120) sollen entgegengesetzt gleich sein.")

    # Kraftamplituden Modul in offener Luft (Abgleich Gruppe)
    print("\nModul in offener Luft, Amplituden bei f / 2f / 3f (N):")
    for name, typ, R in [("Kugel R=1,45 cm", "k", 0.0145), ("Scheibe R=4 cm", "s", 0.04)]:
        am, vis = [], []
        for kk in (1, 2, 3):
            w = kk * W1
            d = np.sqrt(2 * NU / w)
            cv = 6 * np.pi * MU * R * (1 + R / d)
            me = (2 / 3) * np.pi * R**3 * RHO + 3 * np.pi * R**2 * RHO * d if typ == "k" else \
                (8 / 3) * RHO * R**3 + 3 * np.pi * R**2 * RHO * d
            am.append(me * ak[kk - 1]); vis.append(cv * vk[kk - 1])
        print(f"   {name}: Trägheit " + " / ".join(f"{x:.3e}" for x in am) + " ; viskos " + " / ".join(f"{x:.3e}" for x in vis)
              + f" ; max/u_c = {max(am)/U_C:.4f}")
    # Geschlossenes Gehäuse: Innenluft
    Vk = 0.1 / 7850
    print(f"\nGeschlossenes Gehäuse: Innenluftkraft auf das Gesamtsystem = rho_L V_mod a_mod; Stahlmodul 100 g "
          f"(V = {Vk*1e6:.2f} cm^3): Amplitude bei f = {RHO*Vk*ak[0]:.2e} N = {RHO*Vk*ak[0]/U_C:.1e} u_c "
          f"(relativ zur Modulträgheit rho_L/rho_St = {RHO/7850:.1e}); Gleichanteil exakt 0 (d/dt eines periodischen Impulses).")

    # Überschläge
    print("\nÜberschläge:")
    for V in (1.8e-3, 4e-3):
        print(f"   Auftrieb rho g V, V = {V*1e3:.1f} l: {RHO*9.81*V:.4f} N = {RHO*9.81*V/U_C:.2f} u_c; "
              f"+-10 hPa (1 %): {0.01*RHO*9.81*V:.2e} N")
    eps0 = 8.854e-12
    for s in (1e-7, 1e-6, 1e-5):
        print(f"   sigma = {s:.0e} C/m^2, A = 0,04 m^2: F = {s*s*0.04/(2*eps0):.3e} N; E = sigma/eps0 = {s/eps0:.2e} V/m "
              f"({s/eps0/3e6*100:.0f} % der Durchschlagfeldstärke 3 MV/m)")


if __name__ == "__main__":
    main()
