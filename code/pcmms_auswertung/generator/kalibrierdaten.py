"""Synthetische Phase-0-Messdaten für AP-11 (Werkzeug 4): P0.1, P0.2, P0.4 und P0.5 mit bekannten Parametern.

Jede Funktion gibt (messung, wahrheit) zurück: `messung` ist, was ein Messprotokoll liefern würde (Rohwerte,
Übertragungsfunktionen mit Kohärenz, Zeitreihen, Datenblattangaben mit Unsicherheit), `wahrheit` die Parameter des
Generators. AP-11 erhält nur `messung`.

P0.1  Zelle einzeln: Laststufen auf- und absteigend, Rohwert = Nullpunkt + (F + β·F² + h·Richtung)/s + Rauschen;
      eingebaut: Gewichtsstück an Laststellen bekannter Lage, Anzeige ΔN_c = g_c·F_c mit der Statik der
      Dreipunktlagerung F = W·B⁻ᵀ·(1, x, y) bei wahren Zelllagen; Querkraft mit Übersprechen κ; Brückensimulator:
      Kettenübertragung G_F(ω) je Kanal (Sinus) und Superposition zweier Signale.
P0.2  statische Zelllasten bei geparkten Modulen (Konvention b: M = Σ_c F_c,stat/g), Bauteilwägung m_j, örtliches g.
P0.4  Übertragungsfunktion äußere Kraft → Zellen und Summe aus dem 3-FG-Modell (systeme.frf) mit Kraftkette, an der
      Mitte und über den Modulpositionen, zwei Amplituden (optional amplitudenabhängige Steifigkeit), Schätzfehler
      nach der Kohärenz (Varianz des H1-Schätzers je Real- und Imaginärteil (1 − γ²)/(2·n_Mittel·γ²)·|T|², wie
      die normierte Zufallsabweichung von Betrag und Phase); Betriebslastprüfung mit Oberwellen einer
      quadratischen Kennlinie gegen den Referenzaufnehmer.
P0.5  Weg der bewegten Masse je Modul mit Wegkanal G_x (Tiefpass, Laufzeit, Verstärkung) und Indeximpulsen des
      eigenen Encoders (Jitter, Zeitgeber); Datenblattwerte von G_x mit Unsicherheit.
"""
import numpy as np

from .. import konventionen as kv
from .. import rohdaten
from .systeme import G, antworten, frf


def statik(zellen, ort, W=1.0):
    """Zellkräfte einer senkrechten Last W am Ort (x, y) auf drei Zellen (starr): Bᵀ·F = W·(1, x, y)."""
    B = np.c_[np.ones(3), np.asarray(zellen, float)]
    return W * np.linalg.solve(B.T, np.r_[1.0, np.asarray(ort, float)])


def laststellen_standard(zellen, module):
    """Mitte, über jeder Zelle, über jeder Modulachse (Präreg A9.2); doppelte Orte entfallen."""
    orte = [np.zeros(2)] + [np.asarray(z, float) for z in zellen] + [np.asarray(m, float) for m in module]
    out = []
    for o in orte:
        if not any(np.allclose(o, q, atol=1e-6) for q in out):
            out.append(o)
    return np.array(out)


def p01_daten(s, rng, nullpunkt_adc=(120000.0, -80000.0, 45000.0), empf=(1e-6, 1.02e-6, 0.98e-6),
              beta=(0.0, 0.0, 0.0), hysterese_N=(0.0, 0.0, 0.0), sigma_adc=3.0, laststufen=np.arange(0.0, 10.01, 2.0),
              wiederholungen=3, gain_rel=(1.0, 1.0, 1.0), zelllage_fehler=None, orte=None, last_N=2.0,
              sigma_lage_N=2e-5, kappa_quer=(0.0, 0.0, 0.0), kette=None, f_bruecke=None, sigma_bruecke=1e-4,
              elektronik_beta=0.0, bruecke_fehler=1.0):
    """P0.1. zelllage_fehler: (3, 2) Abweichung der wahren von der nominellen Lage [m]; orte: Laststellen (P, 2);
    bruecke_fehler: systematischer Faktor des Brückensimulators auf G_F (falsche Kalibrierannahme, Plan C03)."""
    a = s.aufbau()
    zellen_nom = a.zellen.copy()
    zellen_wahr = zellen_nom + (0.0 if zelllage_fehler is None else np.asarray(zelllage_fehler, float))
    einzeln = []
    for c in range(3):
        F = np.r_[laststufen, laststufen[::-1][1:]]
        rich = np.r_[np.ones(laststufen.size), -np.ones(laststufen.size - 1)]
        F = np.tile(F, wiederholungen)
        rich = np.tile(rich, wiederholungen)
        roh = (nullpunkt_adc[c] + (F + beta[c] * F ** 2 + hysterese_N[c] * rich * (F > 0)) / empf[c]
               + sigma_adc * rng.standard_normal(F.size))
        einzeln.append(dict(last_N=F, richtung=rich, adc=roh, u_last_rel=1e-5))
    orte = laststellen_standard(zellen_nom, a.module) if orte is None else np.asarray(orte, float)
    dN = np.array([np.asarray(gain_rel) * statik(zellen_wahr, o, last_N) for o in orte])
    dN = dN + sigma_lage_N * rng.standard_normal(dN.shape)
    quer = dict(kraft_N=[[1.0, 0.0], [0.0, 1.0]],
                delta_summe_N=[float(np.sum(kappa_quer) * 1.0 + 2e-6 * rng.standard_normal()) for _ in range(2)],
                u_N=2e-6)
    f_br = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000.0]) if f_bruecke is None else np.asarray(f_bruecke)
    Gb = (s.kette if kette is None else kette).G(f_br) * bruecke_fehler
    Gm = Gb * (1 + sigma_bruecke * (rng.standard_normal(Gb.shape) + 1j * rng.standard_normal(Gb.shape)))
    # Superposition der Elektronik: Signal 1 (k = 1, 2), Signal 2 (k = 3, 4), einzeln und als Summe
    th = kv.theta_raster(400)
    s1 = 0.5 * np.cos(th) + 0.2 * np.cos(2 * th + 0.3)
    s2 = 0.3 * np.cos(3 * th - 0.4) + 0.1 * np.cos(4 * th + 1.0)

    def kette_e(x):
        return x + elektronik_beta * x ** 2 + 1e-6 * rng.standard_normal(x.size)
    sup = dict(theta_n=400, signal1=s1, signal2=s2, antwort1=kette_e(s1), antwort2=kette_e(s2),
               antwort12=kette_e(s1 + s2), einheit='N (Brückensimulator, als Kraft skaliert)')
    messung = dict(einzeln=einzeln, laststellen=dict(orte_m=orte, last_N=last_N, delta_N=dN, u_N=sigma_lage_N,
                                                     umrechnung='mit der Einzelkalibrierung je Zelle'),
                   zellen_nominal_m=zellen_nom, module_nominal_m=np.asarray(a.module, float), querkraft=quer,
                   bruecke=dict(f_hz=f_br, G=Gm, u_rel=sigma_bruecke), superposition=sup)
    wahr = dict(nullpunkt_adc=np.asarray(nullpunkt_adc), empfindlichkeit_N_je_adc=np.asarray(empf),
                beta=np.asarray(beta), hysterese_N=np.asarray(hysterese_N), zellen_m=zellen_wahr,
                gain_rel=np.asarray(gain_rel), kappa_quer=np.asarray(kappa_quer),
                kette=dict(f_tp=list((s.kette if kette is None else kette).f_tp),
                           tau=list((s.kette if kette is None else kette).tau)),
                elektronik_beta=elektronik_beta, bruecke_fehler=bruecke_fehler)
    return messung, wahr


def p02_daten(s, rng, u_F=2e-5, wiederholungen=5, u_m=2e-5, g=G, u_g=1e-5, u_m_L=None, m_L_angeben=True):
    """P0.2: statische Zelllasten (wiederholt), Bauteilwägung m_j, örtliches g; m_L = ρ_L·V_außen + m_hyd als
    vorgegebene Rechengröße des synthetischen Körpers (keine Messung; ohne Angabe fehlt sie im Protokoll)."""
    a = s.aufbau()
    F = a.F0[None, :] + u_F * rng.standard_normal((wiederholungen, 3))
    m = np.asarray(s.m) + u_m * rng.standard_normal(3)
    messung = dict(F_c_stat_N=F, u_F_N=u_F, m_j_kg=m, u_m_j_kg=u_m, g=dict(wert=g, u=u_g, quelle='örtlich (synthetisch)'),
                   luft=dict(druck_hPa=1013.0, temperatur_C=21.0, feuchte_pct=45.0), gesamtwaegung=None,
                   gesamtwaegung_grund='keine geeignete Waage im synthetischen Datensatz')
    if m_L_angeben:
        messung['m_L'] = dict(wert_kg=float(a.m_luft), u_kg=float(0.1 * a.m_luft if u_m_L is None else u_m_L),
                              quelle='synthetisch vorgegeben: ρ_L·V_außen + m_hyd (keine Messung)')
    wahr = dict(F0=a.F0, M=a.M, m=np.asarray(s.m), M_traege=a.M_traege, m_luft=a.m_luft)
    return messung, wahr


def p0_messungen(s, rng, p01=None, p02=None, p04=None, p05=None, p05_strich=None):
    """Alle Phase-0-Protokolle eines Systems (Abweichungen je Schritt als dict); Rückgabe (messung, wahrheit)."""
    mes, wahr = {}, {}
    for name, fn, kw in (('p01', p01_daten, p01), ('p02', p02_daten, p02), ('p04', p04_daten, p04),
                         ('p05', p05_daten, p05)):
        mes[name], wahr[name] = fn(s, rng, **(kw or {}))
    if p05_strich is not None:
        mes['p05_strich'], wahr['p05_strich'] = p05_daten(s, rng, **p05_strich)
    return mes, wahr


def schreibe_p0(pfad, messung, kennung):
    """Eingang von AP-11 (Schema p0_messung); die Wahrheit wird getrennt davon geschrieben."""
    from .. import formate
    return formate.schreibe_objekt(pfad, formate.kopf('p0_messung', kennung), messung)


def p04_daten(s, rng, f_band=(20.0, 600.0), df=2.0, n_mittel=50, rauschpegel=2e-4, anregung_N=0.5, orte=None,
              amplituden=(1.0, 2.0), kappa_amplitude=0.0, kette=None, klirr_beta=0.0, betriebslast_N=None,
              f_betrieb=None, kmax_klirr=3):
    """P0.4. rauschpegel: Kraftrauschen je Frequenzlinie und Mittelung [N]; kappa_amplitude: relative
    Steifigkeitsänderung je Amplitudenstufe (Nichtlinearität des Kontakts, Linearitätsprüfung)."""
    a = s.aufbau()
    f = np.arange(f_band[0], f_band[1] + 1e-9, df)
    orte = {'mitte': np.zeros(2), **{f'modul{j + 1}': a.module[j] for j in range(3)}} if orte is None else orte
    daten = {}
    for amp in amplituden:
        K_eff = None if s.K is None else s.K * (1 + kappa_amplitude * (amp - 1.0))
        s_eff = s if s.K is None else s.mit(K=K_eff, C=a.C, zeta=None)
        for name, o in orte.items():
            T = frf(s_eff if kette is None else s_eff.mit(kette=kette), f, o)            # (Zelle, f)
            T = np.vstack([T, T.sum(0, keepdims=True)])                                 # + Summe
            X = anregung_N * amp
            snr = (np.abs(T) * X / rauschpegel) ** 2
            g2 = snr / (1 + snr)
            var = np.full(T.shape, (rauschpegel / X) ** 2 / (2 * n_mittel))   # = (1 − γ²)/(2nγ²)·|T|², auch bei T = 0
            Tm = T + np.sqrt(var) * (rng.standard_normal(T.shape) + 1j * rng.standard_normal(T.shape))
            daten[f'{name}@{amp:g}'] = dict(ort_m=o, amplitude=amp, T=Tm, kohaerenz=g2, n_mittel=n_mittel)
    betrieb = None
    if f_betrieb is not None:
        betrieb = {}
        for name, o in orte.items():
            if name == 'mitte':
                continue
            for k in range(1, kmax_klirr + 1):
                fk = k * f_betrieb
                T1 = frf(s, [fk], o)[:, 0]
                last = betriebslast_N if betriebslast_N is not None else 1.0
                X = last / max(np.abs(T1).max(), 1e-12)
                y = T1 * X                                              # Grundwelle je Zelle
                ob = {}
                for h in (2, 3):
                    ref = 1e-6 * X * np.exp(1j * rng.uniform(0, 2 * np.pi))                  # Klirr des Erregers
                    Th = frf(s, [h * fk], o)[:, 0]
                    zus = klirr_beta * np.abs(y) ** 2 / 2 if h == 2 else 0.0 * y              # quadratische Kennlinie
                    ob[h] = dict(zellen=Th * ref + zus + 2e-7 * rng.standard_normal(3), referenz=ref, T_h=Th)
                betrieb[f'{name}@{k}f'] = dict(f_hz=fk, anregung_N=X, grundwelle=y, oberwellen=ob)
    messung = dict(f_hz=f, daten=daten, betriebslast=betrieb, f_betrieb=f_betrieb,
                   kanaele=['Zelle 1', 'Zelle 2', 'Zelle 3', 'Summe'],
                   hinweis='Übertragung äußere Kraft → Zellkraft, Module geparkt, mit Kraftkette')
    kz = a.kennzahlen()
    wahr = dict(f_n=a.f_n, zeta=a.zeta, K=a.K, C=a.C, M_traege=a.M_traege,
                moden=np.zeros(0) if a.starr else a.moden()[0], f_kipp=np.inf if a.starr else kz['f_kipp'],
                kappa_amplitude=kappa_amplitude, klirr_beta=klirr_beta)
    return messung, wahr


def p05_daten(s, rng, f=None, hub_faktor=1.0, n_zyklen=50, f_s=10000.0, sigma_weg_m=2e-7, jitter_grad=0.02,
              f_takt=1e6, G_x=dict(f_tp=5000.0, tau=20e-6, gain=1.0), G_x_datenblatt=None, k_voll=12,
              getrennte_sensoren=False):
    """P0.5: je Modul Weg relativ zum Rahmen über n_zyklen Zyklen bei Frequenz f mit Indeximpulsen des eigenen Encoders.
    G_x_datenblatt: dem Auswerter genannte Werte mit Unsicherheit (Vorgabe: die wahren Werte mit kleiner Unsicherheit);
    weicht der wahre Wegkanal davon ab, ist das eine Modellabweichung (Prüffall)."""
    f = s.f if f is None else f
    ant = antworten(s, f=f, hub_faktor=hub_faktor, k_voll=k_voll)
    k = np.arange(1, k_voll + 1)
    w = 2 * np.pi * f
    T = 1.0 / f
    datenblatt = G_x_datenblatt or dict(f_tp=G_x['f_tp'], u_f_tp=0.01 * G_x['f_tp'], tau=G_x['tau'], u_tau=1e-7,
                                        gain=G_x['gain'], u_gain=1e-4)
    module = []
    for j in range(3):
        Gx = G_x[j] if isinstance(G_x, (list, tuple)) else G_x
        Gk = Gx['gain'] * np.exp(-1j * k * w * Gx['tau']) / (1 + 1j * k * f / Gx['f_tp'])
        t0 = rng.uniform(0, 1 / f_s)
        t = t0 + np.arange(int((n_zyklen + 1) * T * f_s)) / f_s
        jit = jitter_grad * rng.standard_normal(n_zyklen + 2)                          # Flankenrauschen des Index
        t_idx = np.arange(n_zyklen + 2) * T + jit / 360.0 * T
        x = np.real((ant.X[j] * Gk)[None, :] * np.exp(1j * np.outer(w * t, k))).sum(1)   # Bezug: Index bei t = c·T
        x = x + sigma_weg_m * rng.standard_normal(t.size)
        module.append(dict(t_s=t, weg_m=x, index_s=rohdaten.index_quantisiert(t_idx[t_idx < t[-1]], f_takt)))
    messung = dict(f_hz=f, hub_faktor=hub_faktor, f_s=f_s, f_takt=f_takt, n_zyklen=n_zyklen, module=module,
                   G_x_datenblatt=datenblatt, getrennte_sensoren=getrennte_sensoren, k_voll=k_voll)
    dd = np.degrees(np.angle(ant.X[0, 0])) - np.degrees(np.angle(ant.X[:, 0]))
    wahr = dict(X=ant.X, A=ant.A, delta_delta_grad=kv.wickel_grad(dd), G_x=G_x, f=f)
    return messung, wahr
