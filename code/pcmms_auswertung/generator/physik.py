"""Physik des Generators und ihre Gegenproben.

- egg_fourier: Fourier-Koeffizienten des Egg-Profils geschlossen (Integrale analytisch), unabhängig von der FFT in
  `auslegung.py`; Gegenprobe der Profilharmonischen.
- gegenprobe_starr_g0: starre Auflage, Module über den Zellen (G0): jede Zelle trägt M·g/3 + m_j·a_j(t − τⱼ) (Präreg A2.5),
  analytisch bekannte Zellharmonische.
- abgleich_linear_solver: Summe der Generatorantworten (3 FG, Superposition) gegen `linear_solver.solve()` und
  `linear_solver.waveform()` der Referenz-Engine.
- hertz_fall: nichtlinearer Kontakt mit dem ereignisgenauen Löser (`ereignisloeser.py`, Hunt-Crossley mit n = 1,5,
  α = 0 oder mit linearisierter Dämpfung): Kombinations- und Einzelmodulantworten im Dauerkontakt, wahres Residuum
  gegen die Superposition. Modellbereich: 1 FG ohne Kippmoden, Zellen als feste Aufteilung der Summe (Geometrie
  „zentral“), nur Konfigurationen ohne Abheben (Löser meldet die Flugzeit); keine Aussage über eine abhebende Zelle.
"""
import os
import sys

import numpy as np

from .. import konventionen as kv
from .systeme import G, HUB_REF, M_REF, antworten, system

_CODE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)
import ereignisloeser  # noqa: E402
import linear_solver  # noqa: E402


def egg_fourier(k, thold):
    """c_k = ∫₀¹ ã(s)·e^{−2πiks} ds des normierten Egg-Profils (a(t) = Hub·f²·ã(f·t), Hub Spitze-Spitze):
    ã = −π²/T_h·sin(πs/T_h) für s < T_h, π²/T_f·sin(π(s − T_h)/T_f) sonst (T_f = 1 − T_h), geschlossen integriert."""
    k = np.atleast_1d(np.asarray(k, float))
    al = 2 * np.pi * k

    def I(L):
        b = np.pi / L
        with np.errstate(divide='ignore', invalid='ignore'):
            v = (1 + np.exp(-1j * al * L)) * b / (b ** 2 - al ** 2)
        # Grenzfall α = π/L: ∫₀^L sin(bs)·e^{−ibs} ds = −iL/2
        return np.where(np.isclose(al, b, rtol=1e-12, atol=0), -0.5j * L, v)

    Th, Tf = thold, 1 - thold
    return -np.pi ** 2 / Th * I(Th) + np.pi ** 2 / Tf * np.exp(-1j * al * Th) * I(Tf)


def profil_harmonische_analytisch(s, j=0, k_voll=60, f=None, hub_faktor=1.0):
    """a_k⁽ʲ⁾ (Präreg-Konvention, Bezug Profilphase 0, ohne Profilform und δⱼ) des Egg-Profils geschlossen."""
    f = s.f if f is None else f
    k = np.arange(1, k_voll + 1)
    if s.profil != 'egg':
        raise ValueError('analytische Gegenprobe nur für das Egg-Profil')
    from .systeme import auslegung
    return 2 * s.hub[j] * hub_faktor * f ** 2 * egg_fourier(k, auslegung.THOLD)


def gegenprobe_starr_g0(s=None, k_voll=60):
    """Starre Auflage, G0: Zellharmonische des Moduls j = m_j·a_k⁽ʲ⁾ in Zelle j, null in den anderen (A2.5).
    Rückgabe größte Abweichung [N] der Generatorantwort (FFT-Profil, 3-FG-Statik) von der geschlossenen Form."""
    s = system('A4') if s is None else s
    if s.K is not None or s.geometrie != 'G0' or s.profilform or any(s.delta_profil_grad):
        raise ValueError('Gegenprobe gilt für starre Auflage, G0, ohne Profilabweichungen')
    ant = antworten(s, k_voll=k_voll)
    soll = np.zeros_like(ant.Nz_kraft)
    for j in range(3):
        soll[j, j] = s.m[j] * profil_harmonische_analytisch(s, j, k_voll)
    return dict(abw_N=float(np.abs(ant.Nz_kraft - soll).max()),
                abw_profil=float(np.abs(ant.A - np.array([profil_harmonische_analytisch(s, j, k_voll)
                                                          for j in range(3)])).max()),
                F0_abw=float(np.abs(ant.F0 - np.array([s.m0 / 3 + s.m[c] for c in range(3)]) * G).max()))


def superposition(ant, phi_index_grad, gewichte=(1.0, 1.0, 1.0), zellen=False):
    """Σⱼ wⱼ·N_k⁽ʲ⁾·e^{−ikφⱼ} (Präreg §8.2 mit idealen Zeigern) für Summe (k) oder Zellen (3, k)."""
    k = np.arange(1, ant.k_voll + 1)
    e = kv.zeigerfaktor(np.asarray(phi_index_grad, float), k) * np.asarray(gewichte, float)[:, None]
    return np.einsum('jk,jck->ck', e, ant.Nz) if zellen else (e * ant.Ns).sum(0)


def abgleich_linear_solver(punkte=((120.0, 240.0), (100.0, 240.0), (140.0, 240.0), (110.0, 250.0), (130.0, 230.0)),
                           k_voll=60):
    """Referenzsatz (M = 0,65 kg, μ = 1, K = 10⁴ N/m, C = 16 N·s/m, Egg, 10 Hz): Summe der Generatorantworten
    (Superposition der 3-FG-Einzelmodulantworten) gegen linear_solver. Rückgabe größte Abweichungen."""
    s = system('Referenz')
    ant = antworten(s, k_voll=k_voll)
    abw_k, abw_F = 0.0, 0.0
    for p2, p3 in punkte:
        Nk = superposition(ant, (0.0, p2, p3))
        _, N = linear_solver.waveform(p2, p3)
        ref = 2 * np.fft.rfft(N)[1:k_voll + 1] / N.size
        abw_k = max(abw_k, float(np.abs(Nk - ref).max()))
        r = linear_solver.solve(p2, p3)
        F_gen = ant.MG + kv.kurve(Nk).min()
        abw_F = max(abw_F, abs(F_gen - r['F_min_lin'][0]))
    return dict(abw_harmonische_N=abw_k, abw_F_min_N=abw_F, k_voll=k_voll,
                hinweis='F_min: Generator mit k ≤ k_voll auf N_θ = 2000, linear_solver mit vollem Spektrum')


def hertz_fall(f_n0=50.0, zeta=0.05, mu=0.4, M=M_REF, f=10.0, hub=HUB_REF, n=1.5, konfigurationen=None,
               k_voll=60, daempfung='linearisiert'):
    """Hertzscher Kontakt (Hunt-Crossley, n = 1,5) mit weicher Auflage (Plan A07, Stressszenario außerhalb von
    Regel (b)): Tangentensteifigkeit in der Ruhelage K = M·(2π·f_n0)², linearisierte Dämpfung C = 2ζ√(K·M) über
    α = C/(1,5·M·g) (daempfung='linearisiert') oder α = 0. Konfigurationen: dict id → (φ₂, φ₃) (Profilphasen).
    Rückgabe Tabelle: Einzelmodul- und Kombinationsantworten der Summe (Kraft, ohne Kette, Bezug eigener Index bzw.
    Modul 1), Mindestkraft, Flugzeit (muss 0 sein), wahres Residuum gegen die Superposition und Modellangaben."""
    if konfigurationen is None:
        konfigurationen = {f'S{p2:g}': (float(p2), 240.0) for p2 in kv.SCHNITT_PHI2}
        konfigurationen.update({f'P{a:g}_{b:g}': (a, b) for a, b in kv.PILOTEN})
    m_j, m0 = mu * M / 3, (1 - mu) * M
    K = M * (2 * np.pi * f_n0) ** 2
    K_h = (K / n) ** n * (M * G) ** (1 - n)
    C = 2 * zeta * np.sqrt(K * M)
    alpha = C / (1.5 * M * G) if daempfung == 'linearisiert' else 0.0
    T = 1.0 / f
    t = np.arange(kv.N_THETA) / kv.N_THETA * T

    def loese(phis, m_mod, m_rest):
        sy = ereignisloeser.System(phis=phis, m_mod=m_mod, m0=m_rest, hub=hub, f=f, gesetz='hc', K=K_h, alpha=alpha,
                                   n=n, g=G)
        z = ereignisloeser.startzustand(sy, 'orbit')
        r = ereignisloeser.simulate(sy, z[0], z[1], 0.0, 1, keep=True)
        N = ereignisloeser.abtasten(sy, r, t)[2]
        return kv.harmonische(N, k_voll), float(N.mean()), float(r['Fmin'][0]), float(r['tflug'][0])

    einzel, info = [], {}
    for j in range(3):
        Nk, mean, fmin, tflug = loese((0.0,), (m_j,), M - m_j)
        einzel.append(Nk)
        info[f'L{j + 1}'] = dict(F_min=fmin, t_flug=tflug, mittel=mean)
    einzel = np.array(einzel)
    kombi, resid = {}, {}
    k = np.arange(1, k_voll + 1)
    for kid, (p2, p3) in konfigurationen.items():
        Nk, mean, fmin, tflug = loese((0.0, p2, p3), (m_j,) * 3, m0)
        kombi[kid] = Nk
        sup = (einzel * kv.zeigerfaktor(np.array([0.0, p2, p3]), k)).sum(0)
        resid[kid] = Nk - sup
        info[kid] = dict(F_min=fmin, t_flug=tflug, mittel=mean)
    return dict(einzel=einzel, kombination=kombi, residuum=resid, info=info,
                modell=dict(gesetz='Hunt-Crossley', n=n, K_h=K_h, alpha=alpha, f_n0=f_n0, zeta=zeta, mu=mu, M=M, f=f,
                            hub=hub, K_tangential=K, C_linear=C,
                            grenzen='1 FG ohne Kippmoden; Zellen = Summe/3; nur Dauerkontakt (t_flug = 0); '
                                    'Laufstreuung im Generator linearisiert'))


def hertz_system(f_n0=50.0, zeta=0.05, mu=0.4, M=M_REF, f=10.0, k_max=9):
    """Generatorsystem passend zu hertz_fall (Geometrie „zentral“: Zellkraft = Summe/3; linearer Kontakt nur für
    statische Zelllasten und als Linearisierung)."""
    K = M * (2 * np.pi * f_n0) ** 2
    s = system('A4')
    return s.mit(name=f'A4-weich-{f_n0:g}Hz', K=K, zeta=zeta, C=None, geometrie='zentral', k_max=k_max, f=f,
                 m=(mu * M / 3,) * 3, m0=(1 - mu) * M)
