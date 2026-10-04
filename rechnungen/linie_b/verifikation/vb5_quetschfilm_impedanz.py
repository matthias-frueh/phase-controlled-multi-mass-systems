#!/usr/bin/env python3
"""
Gegenprüfung LB-10/LB-11 (Luft unter dem Körperboden: Quetschfilm).

UNABHÄNGIGER RECHENWEG:
  (1) Exakte lineare Impedanz des oszillierenden Quetschfilms zwischen paralleler Kreisscheibe (Radius R) und Boden,
      Spalt h, mit Trägheit und Zähigkeit (instationäre Schmierfilmgleichung, Womersley-Profil; eigene Herleitung):
         rho du/dt = -dp/dr + mu d2u/dz2,  q(r) = -hdot r/2,  p(R) = p0
         F_Luft = -Z(omega) * hdot,   Z = i omega pi rho R^4 / (8 h Phi),   Phi = 1 - tanh(kh/2)/(kh/2),  k = sqrt(i omega/nu)
      Grenzfälle: Phi -> 1: Z = i omega m_sq, m_sq = pi rho R^4/(8h) (Trägheit);  kh -> 0: Z = 3 pi mu R^4/(2 h^3) (Gruppe).
  (2) Wirkung auf N(t) im linearen Dauerkontaktmodell, Frequenzbereich mit ANALYTISCHEN Fourierkoeffizienten des
      Egg-Lageprofils (geschlossene Integrale der Halbsinus-Beschleunigungsbögen, kein FFT des Zeitsignals):
         (K + i W C - M W^2 + i W Z(W)) z_k = -mu M a_k,   N_k = -(K + i W C) z_k  (Luftkraft umgeht die Wägezellen; Annahme)
      Abgleich m_a = 0 gegen linear_solver-Wert F_min(120,240) = 5,330390 N und Zeitbereich vb4 (m_a = 4,60 g).
  (3) Gleichanteil (reibungsfrei, nichtlinear in hdot, h): F(t) = -pi rho R^4 h''/(8h) + 3 pi rho R^4 h'^2/(16 h^2)
      [p(R) = p0], zeitlich gemittelt entlang h(t) = h0 + z(t) - <z> aus der linearen Lösung (ohne Kleinamplituden-
      näherung); Vergleich mit der Skala der Gruppe pi rho R^4 <zdot^2>/(16 h^2). Variante B: Eintrittsverlust
      (Einströmen: p(R) = p0 - rho u_R^2/2, Ausströmen: p(R) = p0) -> Vorzeichen/Betrag.
ANNAHMEN: R = 0,1128 m (Scheiben-Äquivalent 20x20 cm, wie Gruppe), h = 1/3/10 mm, Luft rho 1,2, mu 1,8e-5.
"""
import numpy as np

M, G = 0.65, 9.81
MG = M * G
F = 10.0
T = 1 / F
W1 = 2 * np.pi * F
THOLD = 0.65
TFAST = 1 - THOLD
RTOP = 0.005
RBOT = RTOP * TFAST / THOLD
A_H = -RTOP * (np.pi / (THOLD * T)) ** 2
A_F = RBOT * (np.pi / (TFAST * T)) ** 2
ZETA = 16.0 / (2 * np.sqrt(1e4 * M))
RHO, MU = 1.2, 1.8e-5
NU = MU / RHO
U_C = 0.0327
NK = 4096              # Harmonische
NT = 2 * NK * 8        # Zeitpunkte für irfft


def ak_egg(k):
    """c_k = (1/T) int_0^T a(t) exp(-i k W1 t) dt, analytisch."""
    Om = k * W1
    L1, L2 = THOLD * T, TFAST * T
    a1, a2 = np.pi / L1, np.pi / L2
    I1 = a1 * (1 + np.exp(-1j * Om * L1)) / (a1**2 - Om**2)
    I2 = np.exp(-1j * Om * L1) * a2 * (1 + np.exp(-1j * Om * L2)) / (a2**2 - Om**2)
    return (A_H * I1 + A_F * I2) / T


def Z_sq(Om, R, h):
    k = np.sqrt(1j * Om / NU)
    x = k * h / 2
    Phi = 1 - np.tanh(x) / x
    return 1j * Om * np.pi * RHO * R**4 / (8 * h * Phi)


def loesung(p2, p3, K, C, mu, Zfun):
    k = np.arange(1, NK + 1)
    Om = k * W1
    comb = (1 + np.exp(-1j * k * np.radians(p2)) + np.exp(-1j * k * np.radians(p3))) / 3
    a = ak_egg(k) * comb
    Zair = Zfun(Om)
    zk = -mu * M * a / (K + 1j * Om * C - M * Om**2 + 1j * Om * Zair)
    Nk = -(K + 1j * Om * C) * zk
    spec = np.zeros(NT // 2 + 1, complex)
    spec[1:NK + 1] = Nk * NT          # irfft-Normierung: x = (1/NT) sum X e^{..}, X_k = NT * c_k (zweiseitig)
    N_t = MG + np.fft.irfft(spec, NT)
    zs = np.zeros(NT // 2 + 1, complex); zs[1:NK + 1] = zk * NT
    zd = np.zeros(NT // 2 + 1, complex); zd[1:NK + 1] = 1j * Om * zk * NT
    zdd = np.zeros(NT // 2 + 1, complex); zdd[1:NK + 1] = -Om**2 * zk * NT
    return N_t, np.fft.irfft(zs, NT), np.fft.irfft(zd, NT), np.fft.irfft(zdd, NT), Nk


def main():
    print("=" * 110)
    print("vb5 – Quetschfilm: exakte lineare Impedanz, Wirkung auf F_min, Gleichanteil")
    print("=" * 110)
    R = 0.1128
    print(f"Freie Scheibe (Gruppe): m_a = (8/3) rho R^3 = {(8/3)*RHO*R**3*1e3:.3f} g")
    print("(1) Quetschfilm-Impedanz Z = c_eff + i omega m_eff, R = 0,1128 m:")
    for h in (1e-3, 3e-3, 10e-3):
        msq = np.pi * RHO * R**4 / (8 * h)
        csq = 3 * np.pi * MU * R**4 / (2 * h**3)
        out = []
        for f in (10, 20, 30, 60):
            Om = 2 * np.pi * f
            Z = Z_sq(Om, R, h)
            out.append(f"{f} Hz: c = {Z.real:.3e} N s/m, m = {Z.imag/Om*1e3:6.2f} g (omega h^2/nu = {Om*h*h/NU:.0f})")
        print(f"  h = {h*1e3:4.1f} mm: reibungsfrei m_sq = pi rho R^4/(8h) = {msq*1e3:.2f} g "
              f"({msq/M*100:.2f} % von M); zäh c_sq = {csq:.3e} N s/m")
        for o in out:
            print("       " + o)

    print("\n(2) Wirkung auf N(t), lineare Dauerkontaktlösung mit analytischen a_k:")
    N0, *_ = loesung(120, 240, 1e4, 16.0, 1.0, lambda Om: 0 * Om)
    print(f"  Abgleich m_a = 0: F_min(120,240) = {N0.min():.6f} N (linear_solver 5,330390 N)")
    scen = [("K=1e4, mu=1", 1e4, 1.0), ("K=1e5, mu=0,4", 1e5, 0.4), ("K=1e6, mu=0,4", 1e6, 0.4)]
    airs = [("freie Scheibe 4,60 g", lambda Om: 1j * Om * 4.60e-3),
            ("Quetschfilm h=10 mm", lambda Om: Z_sq(Om, R, 10e-3)),
            ("Quetschfilm h=3 mm", lambda Om: Z_sq(Om, R, 3e-3)),
            ("Quetschfilm h=1 mm", lambda Om: Z_sq(Om, R, 1e-3))]
    for sn, K, mu in scen:
        C = 2 * ZETA * np.sqrt(K * M)
        print(f"  {sn}:")
        base = {}
        for p2 in (100, 120, 140):
            Nb, zb, zdb, zddb, _ = loesung(p2, 240, K, C, mu, lambda Om: 0 * Om)
            base[p2] = (Nb, zb, zdb, zddb)
        for an, Zf in airs:
            row = []
            fm = {}
            for p2 in (100, 120, 140):
                Na, *_ = loesung(p2, 240, K, C, mu, Zf)
                fm[p2] = Na.min()
                row.append(Na.min() - base[p2][0].min())
            dz = [(fm[120] - fm[p]) - (base[120][0].min() - base[p][0].min()) for p in (100, 140)]
            print(f"     {an:22s}: dF_min(100/120/140) = " + " / ".join(f"{x:+.2e}" for x in row)
                  + f" N; max |dF_min|/u_c(0,0327) = {max(abs(x) for x in row)/U_C:.2f}; Zeltdifferenz 120-100/120-140 "
                  + " / ".join(f"{x:+.2e}" for x in dz) + " N")

    print("\n(3) Gleichanteil des Quetschfilms (reibungsfrei), K=1e4/mu=1 und K=1e5/mu=0,4, R = 0,1128 m:")
    for sn, K, mu in (scen[0], scen[1]):
        C = 2 * ZETA * np.sqrt(K * M)
        for p2 in (100, 120, 140):
            Nb, zb, zdb, zddb = loesung(p2, 240, K, C, mu, lambda Om: 0 * Om)[:4]
            zrel = zb - zb.mean()
            for h0 in (3e-3, 10e-3):
                hh = h0 + zrel
                Fa = -np.pi * RHO * R**4 * zddb / (8 * hh) + 3 * np.pi * RHO * R**4 * zdb**2 / (16 * hh**2)
                ur = R * zdb / (2 * hh)                         # radiale Randgeschwindigkeit (Betrag)
                extra = np.where(zdb > 0, -0.5 * RHO * ur**2 * np.pi * R**2, 0.0)   # Eintrittsverlust beim Einströmen
                skala = np.pi * RHO * R**4 * np.mean(zdb**2) / (16 * h0**2)
                print(f"   {sn} ({p2},240) h0 = {h0*1e3:4.1f} mm: z_pp = {np.ptp(zb)*1e3:.4f} mm, "
                      f"<F>_A(p(R)=p0) = {Fa.mean():+.3e} N, <F>_B(Eintrittsverlust) = {(Fa+extra).mean():+.3e} N, "
                      f"Skala Gruppe = {skala:.3e} N ({skala/U_C:.3f} u_c)")


if __name__ == "__main__":
    main()
