"""AP-12: synthetisches Teil B nach Präreg A9.3 aus Phase-0-Daten, Kalibrierung (AP-11), Pilotanalyse (AP-11) und den
Ergebnissen von Werkzeug 8 (AP-13). Teil B wird nicht mit Messwerten gefüllt; synthetische Kennungen beginnen mit
„SYNTH-“ und behaupten keine Registrierung.

Gliederung (A9.3): nr1 Herkunft; nr2 Platzhalterwerte; nr3 Einzelmodul-Harmonische der Phase 0 je Lauf (Zellen,
ungebändert) mit den festen Indexmatrizen B⁰ⱼ; nr4 Vorhersage an den Sollphasen mit dem Jitter der Pilotläufe
(ρⱼₖ = e^{−ikφⱼ,soll}·e^{−k²σⱼ²/2}, A2.4), D_q (Fassung B, dazu Fassung A), Δ_q = Faktor·D_q, Δ_rel,q, Sensitivität
0,1·D_q, Rauschbias b̂⁰, b̂¹ mit u(b̂) (Werkzeug 8), u_c,erw, H1Z-Grenzen, ŷ⁰′ an den Punkten I; nr5 T(kω) für E3;
nr6 H2-Fenster, φ̂₂*, SNR und erwartete Halbbreite; nr7 H3-Vorhersage (nur zum Vergleich); nr8 Prüfmenge V;
nr9 Laufreihenfolge; nr10 Ergebnisse von Werkzeug 8 (c von H1 und H1Z mit Prüfrate und Herkunft, kritischer Wert für
ε_ctrl, Intervalltyp von H2 mit Überdeckung). Fehlende Werte stehen als None mit Vermerk; Stufe 2 meldet die
betroffenen Ausgänge dann als nicht entscheidbar mit Grund.
"""
import numpy as np
from scipy import stats

from . import bootstrap as bs, formate, h2, kontrollen, konventionen as kv, vorhersage as vh, zeltfit as zfit
from . import zusammenfassung as zf
from .regeln import RegelOffen

VERSION = 'teil_b-0.1'


def konfigurationen(zusatz=False, punkte_I=None):
    """Konfigurationsliste in der Reihenfolge von §6 (Schnitt aufsteigend, Zusatz, Punkte I bei Einstellung 2)."""
    out = [dict(id=zf.konfig_id('K', (0.0, p, kv.SCHNITT_PHI3), gruppe='schnitt'), gruppe='schnitt',
                phi=[0.0, float(p), kv.SCHNITT_PHI3], einstellung=1) for p in kv.SCHNITT_PHI2]
    if zusatz:
        out += [dict(id=zf.konfig_id('K', (0.0, 0.0, b), gruppe='zusatz'), gruppe='zusatz', phi=[0.0, 0.0, b],
                     einstellung=1) for b in (0.0, 180.0)]
    for p in (punkte_I or []):
        out.append(dict(id=zf.konfig_id('K', (0.0, p, kv.SCHNITT_PHI3), einstellung=2, gruppe='identifizierbarkeit'),
                        gruppe='identifizierbarkeit', phi=[0.0, float(p), kv.SCHNITT_PHI3], einstellung=2))
    return out


def _einzel(tab, modul, einstellung, ausschluss):
    sel = [i for i, k in enumerate(tab.koepfe) if k['laufart'] == 'L' and k['modul'] == modul
           and k['einstellung'] == einstellung and k['phase'] == 0 and k['lauf_id'] not in ausschluss]
    sel = sorted(sel, key=lambda i: tab.koepfe[i]['position'])
    return dict(Nk_zellen=tab.daten['Nk_zellen'][sel], lauf_ids=[tab.koepfe[i]['lauf_id'] for i in sel],
                positionen=[tab.koepfe[i]['position'] for i in sel])


def rho_soll(phi_profil, dd, sigma, kmax):
    """ρⱼₖ an den Sollphasen: Indexphase φ^P − Δδⱼ, Jitterfaktor e^{−k²σⱼ²/2} (σ in Grad)."""
    k = np.arange(1, kmax + 1)
    idx = np.asarray(phi_profil, float) - np.asarray(dd, float)
    return kv.zeigerfaktor(idx, k) * np.exp(-0.5 * np.outer(np.radians(np.asarray(sigma, float)), k) ** 2)


def d_grenzen(Y, kmax):
    """D_q über den Schnitt aus Vorhersagen Y (21, ≥ kmax) nach §8.5: F_min-Spannweite, Fassung B (Durchmesser),
    Fassung A (größter Betrag) für Re und Im N_k."""
    F = vh.fmin_rel_viele(Y[:, :kmax])
    DB, DA = [F.max() - F.min()], [F.max() - F.min()]
    for k in range(3):
        z = Y[:, k]
        dB = float(np.abs(z[:, None] - z[None, :]).max())
        dA = float(np.abs(z).max())
        DB += [dB, dB]
        DA += [dA, dA]
    return np.array(DB), np.array(DA)


def erstellen(tab0, kal, pilot_erg, profil, plan, werkzeug8=None, kennung=None, seed_b0=None, B=None):
    """Teil B (Inhalt als verschachteltes dict). tab0: Phase-0-Läufe (LaufTabelle); kal: Kalibrierung; pilot_erg:
    Ergebnis von pilot.pilot_auswerten; plan: dict(f, k_max, n_min, n0, r, n, d, n_max, zusatz, einstellung2 (art, s,
    punkte_I) oder None, seed_reihenfolge, laufreihenfolge, seed_bootstrap); werkzeug8: dict (c_H1, c_H1Z,
    bias0, bias1, u_bias0, u_bias1 (je (21,) Summe; *_zellen (21, 3)), h2_intervall, eps_kritisch, …) oder None."""
    w8 = dict(werkzeug8 or {})
    kmax = int(plan['k_max'])
    K = int(tab0.k_voll)
    B = profil.zahl('bootstrap_B') if B is None else int(B)
    p05 = kal['p0_5']
    dd = np.asarray(p05['delta_delta_grad'], float)
    ungueltig = set(pilot_erg['gueltigkeit']['gruende'])
    e2 = plan.get('einstellung2')
    # nr3: Einzelmodulläufe der Phase 0 und feste Indexmatrizen B⁰ⱼ
    nr3 = dict(einzel0=[_einzel(tab0, j, 1, ungueltig) for j in (1, 2, 3)],
               einzel0_strich=[_einzel(tab0, j, 2, ungueltig) for j in (1, 2, 3)] if e2 else None,
               B=B, seed_b0=seed_b0)
    ss = np.random.SeedSequence(seed_b0).spawn(6)
    idx = {}
    for j in range(3):
        n0j = len(nr3['einzel0'][j]['lauf_ids'])
        idx[f'B0/modul{j + 1}'] = np.random.Generator(np.random.PCG64(ss[j])).integers(0, n0j, size=(B, n0j))
        if e2:
            n0s = len(nr3['einzel0_strich'][j]['lauf_ids'])
            idx[f"B0′/modul{j + 1}"] = np.random.Generator(np.random.PCG64(ss[3 + j])).integers(0, n0s,
                                                                                                size=(B, n0s))
    nr3['indizes'] = idx
    for j, e in enumerate(nr3['einzel0']):
        if len(e['lauf_ids']) < 2:
            raise ValueError(f'Teil B nicht bildbar: Modul {j + 1} hat {len(e["lauf_ids"])} gültige Einzelmodulläufe '
                             'der Phase 0 (Pilotanalyse: Gültigkeit)')
    Nbar0 = np.stack([e['Nk_zellen'].mean(0) for e in nr3['einzel0']])          # (Modul, Zelle, K)
    # Referenzläufe der Phase 0: N_s je Zelle
    ref = [i for i, k in enumerate(tab0.koepfe) if k['laufart'] == 'R' and k['lauf_id'] not in ungueltig]
    N_s_z = tab0.daten['N_mittel_zellen'][ref].mean(0)
    # nr4: Vorhersage an den Sollphasen mit dem Jitter der Pilotläufe
    pil = [i for i, k in enumerate(tab0.koepfe) if k['konfiguration']['gruppe'] == 'pilot']
    sig = np.r_[0.0, np.nanmedian(tab0.daten['sigma_grad'][pil][:, 1:], 0)]
    konf = konfigurationen(plan.get('zusatz', False), e2['punkte_I'] if e2 else None)
    vor = {}
    for c in konf:
        if c['einstellung'] == 2:
            continue
        rho = rho_soll(c['phi'], dd, sig, K)
        Yz = vh.vorhersage(Nbar0, rho, zellen=True)
        vor[c['id']] = dict(Nk_zellen=Yz, Nk_summe=Yz.sum(0))
    schnitt = [c['id'] for c in konf if c['gruppe'] == 'schnitt']
    Y = np.array([vor[q]['Nk_summe'] for q in schnitt])
    DB, DA = d_grenzen(Y, kmax)
    fak = profil.wert('h1.faktor')
    Delta = fak * DB
    nr4 = dict(konfigurationen={q: dict(F_min_rel=float(vh.fmin_rel_viele(v['Nk_summe'][:kmax])),
                                        N_k=v['Nk_summe'][:3], gamma1=float(kv.schiefe(v['Nk_summe'][:kmax])),
                                        Nk_summe=v['Nk_summe'], Nk_zellen=v['Nk_zellen']) for q, v in vor.items()},
               D_B=DB, D_A=DA, Delta=Delta, Delta_rel=Delta.copy(), Delta_sens_0_1=0.1 * DB, Delta_sens_A=fak * DA,
               faktor=fak, d_fassung=profil.wert('h1.d_fassung'), jitter_grad=sig, N_s_zellen=N_s_z)
    # H1Z-Grenzen (Regel h1z.grenzen offen; Entwicklungsprüffall (a): Δ_q/3)
    try:
        regel = profil.wert('h1z.grenzen')
        nr4['h1z'] = dict(regel=regel, Delta_c=Delta / 3 if regel == 'a' else None,
                          Delta_c_rel=Delta / 3 if regel == 'a' else None)
    except RegelOffen as e:
        nr4['h1z'] = dict(regel=None, grund=e.grund, Delta_c=None, Delta_c_rel=None)
    for name in ('bias0', 'bias1', 'u_bias0', 'u_bias1', 'bias0_zellen', 'bias1_zellen', 'u_bias0_zellen',
                 'u_bias1_zellen'):
        nr4[name] = None if w8.get(name) is None else np.asarray(w8[name], float)
    nr4['bias_herkunft'] = w8.get('bias_herkunft', 'fehlt (Werkzeug 8)')
    # u_c,erw aus s_q (Pilot) und u(ŷ) (Bootstrap der Vorhersage an den Sollphasen)
    st = pilot_erg['streuungen_volles_fenster']
    s_q = np.array([st['s_q'][g] for g in kv.GROESSEN_H1]) if st.get('s_q') else None
    u_yhat = np.zeros((len(schnitt), 7))
    u_gam = np.zeros(len(schnitt))
    Bv = min(B, 2000)                                                   # u(ŷ) für u_c,erw und V (Schätzung)
    Nb = np.stack([(bs.zaehlmatrix(idx[f'B0/modul{j + 1}'][:Bv], e['Nk_zellen'].shape[0]) @
                    e['Nk_zellen'].sum(1)) / e['Nk_zellen'].shape[0] for j, e in enumerate(nr3['einzel0'])], 1)
    for i, q in enumerate(schnitt):
        c = next(x for x in konf if x['id'] == q)
        rho = rho_soll(c['phi'], dd, sig, K)
        reps = np.einsum('bjk,jk->bk', Nb, rho)[:, :kmax]
        u_yhat[i] = vh.groessen(reps, kmax).std(0, ddof=1)
        u_gam[i] = kv.schiefe(reps).std(ddof=1)
    n_min = int(plan['n_min'])
    nr4['u_yhat'] = u_yhat
    nr4['u_yhat_replikate'] = int(Bv)
    nr4['u_c_erw'] = None if s_q is None else np.sqrt(s_q[None, :] ** 2 / n_min + u_yhat ** 2)
    # nr8: Prüfmenge V
    c4 = float(stats.t.ppf(1 - 0.05 / profil.wert('h4.m'), n_min - 1))
    s_g = st.get('s_gamma1')
    V = []
    if s_g is not None:
        for i, q in enumerate(schnitt):
            g = nr4['konfigurationen'][q]['gamma1']
            ue = np.sqrt(s_g ** 2 / n_min + u_gam[i] ** 2)
            if abs(g) >= (c4 + profil.wert('h4.aufnahme')) * ue:
                V.append(dict(id=q, gamma_vorhersage=g, u_c_erw=float(ue)))
    nr8 = dict(V=V, c4=c4, zusatz=bool(plan.get('zusatz', False)))
    # nr6: H2-Fenster und Spitzenlage an der Vorhersage
    F_vor = np.array([nr4['konfigurationen'][q]['F_min_rel'] for q in schnitt])
    try:
        W = h2.fenster(F_vor, kv.SCHNITT_PHI2, profil)
        phiW = np.array([kv.SCHNITT_PHI2[i] for i in W['W']])
        fit = zfit.zeltfit(phiW[None], F_vor[W['W']][None])
        phis = float(fit['phi_stern'][0])
        lin = phiW <= phis
        sL = np.polyfit(phiW[lin], F_vor[W['W']][lin], 1)[0] if lin.sum() >= 2 else np.nan
        sR = -np.polyfit(phiW[~lin], F_vor[W['W']][~lin], 1)[0] if (~lin).sum() >= 2 else np.nan
        sF = st['s_q']['F_min_rel'] if st.get('s_q') else None
        snr = None if not sF else float(np.nanmean([abs(sL), abs(sR)]) * 1.0 / sF)
        nr6 = dict(W=W, W_ids=[schnitt[i] for i in W['W']], phi_hat_stern=phis, flanken=[float(sL), float(sR)],
                   SNR=snr, halbbreite_erwartet=None if snr is None else float(3 / (snr * np.sqrt(plan['n']))))
    except RegelOffen as e:
        nr6 = dict(W=None, grund=e.grund)
    # nr5: T(kω) für E3
    T = kontrollen.uebertragung(kal, plan['f'])
    nr5 = dict(T=T, hinweis='T aus P0.1 (Statik, Lagen, Verstärkungen), Kette und 1 FG; Kippmoden vernachlässigt')
    nr2 = dict(f=float(plan['f']), k_max=kmax, k_voll=K, delta_delta_grad=dd,
               u_delta_delta_grad=np.asarray(p05['u_delta_delta_grad'], float),
               sigma_tol_grad=pilot_erg['sigma_tol_grad'], delta_f_tol=plan.get('delta_f_tol'),
               sigma_ref=pilot_erg['sigma_ref']['sigma_ref'], sigma_ref_zellen=pilot_erg['sigma_ref']['sigma_ref_zellen'],
               eps_ctrl=pilot_erg['eps_ctrl'].get('eps_ctrl'), eps_ctrl_test=pilot_erg['eps_ctrl'],
               sigma_c=pilot_erg['sigma_c'], F_LO_zellen=pilot_erg['F_LO_zellen'],
               sigma_delta=pilot_erg['sigma_delta'], T_P0=plan.get('T_P0'), Delta_T=plan.get('Delta_T'),
               n_min=n_min, n0=int(plan['n0']), r=plan.get('r'), n=int(plan['n']), n_max=plan.get('n_max'),
               d=int(plan['d']), p_hat=pilot_erg['p_hat'], einstellung2=e2,
               F_c_stat=np.asarray(kal['p0_2']['F_c_stat_N'], float), N_s_zellen=N_s_z,
               konfigurationen=konf, f_takt=plan.get('f_takt', 1e6),
               pilot_suche={x: pilot_erg.get('suche', {}).get(x) for x in ('ergebnis', 'grund')})
    nr10 = dict(c_H1=w8.get('c_H1'), c_H1_herkunft=w8.get('c_H1_herkunft', 'fehlt (Werkzeug 8)'),
                c_H1Z=w8.get('c_H1Z'), c_H1Z_herkunft=w8.get('c_H1Z_herkunft', 'fehlt (Werkzeug 8)'),
                pruefrate=w8.get('pruefrate'), h2_intervall=w8.get('h2_intervall'),
                eps_kritisch=pilot_erg['eps_ctrl'].get('kritisch'), raten=w8.get('raten'))
    return dict(version=VERSION, kennung=kennung,
                nr1=dict(kalibrierung_sha256=formate.sha256_json(kal),
                         phase0_sha256=formate.sha256_bytes(formate.npz_bytes(tab0.daten)),
                         phase0_verarbeitung=zf.verarbeitungsstand(tab0.koepfe),
                         pilot_sha256=formate.sha256_json(pilot_erg), code_version=formate.code_version()),
                nr2=nr2, nr3=nr3, nr4=nr4, nr5=nr5, nr6=nr6, nr7=dict(hinweis='H3-Vorhersage rechnet Stufe 2 aus der '
                                                                               'Kalibrierung (nur zum Vergleich)'),
                nr8=nr8, nr9=dict(seed=plan.get('seed_reihenfolge'), laufreihenfolge=plan.get('laufreihenfolge')),
                nr10=nr10, seed_bootstrap=plan.get('seed_bootstrap'), profil=profil.kurz())


def schreiben(pfad, inhalt, kennung):
    return formate.schreibe_objekt(pfad, formate.kopf('teil_b', kennung, version=VERSION), inhalt)


def lesen(pfad):
    return formate.lies_objekt(pfad, 'teil_b')
