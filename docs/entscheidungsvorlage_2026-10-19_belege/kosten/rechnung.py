# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 6 (Rechenbudget), 2.5, 3.5, 5.5 und 8.
# Zweck: Nachrechnung der Kostenangaben aus den gelesenen Sekunden je Kampagne (PR #23), Kampagnenzahlen und
#   Kernstunden von R1/R2/R2-d, Phase-0-Läufe, Nachziehen bis |A| = 1000, κ der oberen 80-%-Grenze, Größe von b̂
#   aus den gespeicherten Werkzeug-8-Dateien.
# Eingaben: docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, docs/ap13_neulaeufe_2026-10-17/werkzeug8_*,
#   docs/e3b_g4_diagnose_2026-10-17/werkzeug8_V1G60h.*; Argument 1 = Ausgabe (JSON, auch auf stdout).
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B rechnung.py rechnung.json > /dev/null
# Herkunft: Nachprüfung 7 (Reihenfolge, Abhängigkeiten, Rechenbudget). Geändert: Repository-Pfad relativ.
# Repository-Wurzel: drei Ebenen über diesem Ordner; abweichend über die Umgebungsvariable PCMMS_REPO (etwa ein
#   Auszug von main 0f63187: git archive 0f63187 code docs | tar -x -C <ziel>).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""NL7: Nachrechnung der Kostenangaben (PR #23 ergebnisse.json) und Größen von b̂ (werkzeug8_*.npz).
Nur Lesen gespeicherter Dateien; keine Kampagnen."""
import json, os, sys
import numpy as np
from scipy import stats

REPO = os.environ.get('PCMMS_REPO') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))   # Repository-Wurzel (Kopf)
R = os.path.join(REPO, 'docs') + os.sep
d = json.load(open(R + 'ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json'))
out = {}

# 1) Sekunden je Kampagne (gelesen) und Kernstunden (nachgerechnet)
for key in ('abschaetzung', 'abschaetzung_korrektur'):
    s = d[key]['sekunden_je_kampagne']
    lo = s['voll_B10000_linear']
    up = max(s['voll_normativ_gemessen'].values())
    z = s['zuschlag_ablauf']
    o = dict(
        lo_je_system=2000 * lo / 3600,
        up_je_system=2000 * up * z / 3600,
        lo_drei=6000 * lo / 3600,
        up_drei_max=3 * 2000 * up * z / 3600,
        up_drei_je_system={k: 2000 * v * z / 3600 for k, v in s['voll_normativ_gemessen'].items()},
        up_drei_summe=sum(2000 * v * z / 3600 for v in s['voll_normativ_gemessen'].values()),
        zaehl_je_1000=1000 * s['schlank'] / 3600,
        bootstrap_anteil_B1000=s['voll_B1000'] - s['schlank'],
        lin_B10000=s['schlank'] + 10 * (s['voll_B1000'] - s['schlank']),
        gelesen=dict(kal_je_system=d[key]['kalibrierung_je_system_kernstunden'],
                     drei=d[key]['drei_referenzsysteme_kernstunden'],
                     zaehl=d[key]['zaehldiagnose_je_1000_kampagnen_kernstunden']))
    out[key] = o

# 2) Zähldiagnosen R1 (schlank, Ablauf zustand): 2,59 s bzw. 3,54 s je Kampagne (gelesen)
sl = (d['abschaetzung']['sekunden_je_kampagne']['schlank'], d['abschaetzung_korrektur']['sekunden_je_kampagne']['schlank'])
stat = (d['laufzeiten']['je_art']['schlank/H/historisch']['mittel'], d['laufzeiten_korrektur']['je_art']['schlank/H/historisch']['mittel'])
vollB1000 = (d['abschaetzung']['sekunden_je_kampagne']['voll_B1000'], d['abschaetzung_korrektur']['sekunden_je_kampagne']['voll_B1000'])
vollstat = d['laufzeiten']['je_art']['voll/H/k_konsistent']['mittel']


def kh(n, sek):
    return [round(n * x / 3600, 2) for x in sek]


r1 = {
    'R1_G4_3sys_x1000_x3var (Vorlage)': (9000, kh(9000, sl)),
    'R1_Halte_nur_ii_3sys_x1000_x2anordnungen': (6000, kh(6000, sl)),
    'R1_Halte_i_und_ii_getrennt_x2anordnungen': (12000, kh(12000, sl)),
    'R1_gemeinsam_3var_eine_anordnung (Vorlage 7-10)': (9000, kh(9000, sl)),
    'R1_gemeinsam_3var_plus_zweite_anordnung_fuer_1var': (12000, kh(12000, sl)),
    'R1_gemeinsam_3var_x2anordnungen_voll_faktoriell': (18000, kh(18000, sl)),
    'R2_6szen_3sys_300_statisch': (5400, kh(5400, stat)),
    'R2_9szen_3sys_300_statisch (Arbeitskopie: +3 Annahmen)': (8100, kh(8100, stat)),
    'R2d_2pkt_2gen_400_B1000_Ablauf': (1600, kh(1600, vollB1000)),
    'R2d_2pkt_2gen_400_B1000_statisch': (1600, kh(1600, (vollstat, vollstat * 2.852 / 1.988))),
}
out['r1_r2'] = {k: dict(kampagnen=v[0], kernstunden_schnell_langsam=v[1]) for k, v in r1.items()}
out['r2_sek_je_statische_kampagne_aus_4.5h'] = 4.5 * 3600 / 5400

# Phase-0-Läufe je Kampagne: Generator 61 R (Abstand 2) gegen 42 R; Phase 1 630 Läufe (PR #23)
andere = 3 * 20 + 3 * 20
gen_R = 1 + andere // max(1, min(12, andere // 41))
out['phase0'] = dict(andere=andere, R_generator=gen_R, laeufe_generator=andere + gen_R,
                     laeufe_42R=andere + 42, phase1=630,
                     anteil_aenderung=(andere + 42 + 630) / (andere + gen_R + 630) - 1,
                     R_bei_abstand_12=1 + andere // 12, andere_noetig_fuer_42R_abstand12=41 * 12)

# Nachziehen bis |A| = 1000
nz = {}
for lab, pga in (('ii_W3_erschoepft_0.36-0.76%', (0.0036, 0.0076)), ('ii_mit_Zuschlag_1%', (0.01, 0.01)),
                 ('i_halt_verloren_0.09-0.17', (0.09, 0.17)), ('i_beobachtet_5/30', (5 / 30, 5 / 30))):
    f = [1 / (1 - x) for x in pga]
    nz[lab] = dict(faktor=[round(x, 4) for x in f],
                   mehr_kh_je_system=[round((f[0] - 1) * 18.4, 2), round((f[1] - 1) * 81.1, 2)],
                   mehr_kh_drei=[round((f[0] - 1) * 55.1, 2), round((f[1] - 1) * 243.3, 2)])
out['nachziehen'] = nz

# 3) κ der oberen 80-%-Grenze
kap = {nu: float(np.sqrt(nu / stats.chi2.ppf(0.2, nu))) for nu in (19, 21, 41, 57)}
out['kappa'] = kap

# 4) b̂ aus werkzeug8_*.npz (gelesen) und Folgerungen (gerechnet)
bh = {}
for name, f, n in (('A4', 'ap13_neulaeufe_2026-10-17/werkzeug8_A4.npz', 200),
                   ('V1G0', 'ap13_neulaeufe_2026-10-17/werkzeug8_V1G0.npz', 60),
                   ('V1G60h', 'e3b_g4_diagnose_2026-10-17/werkzeug8_V1G60h.npz', None)):
    z = np.load(R + f, allow_pickle=False)
    j = json.load(open(R + f.replace('.npz', '.json')))
    herk = j['inhalt']['bias_herkunft']
    e = {}
    for b, u in (('bias0', 'u_bias0'), ('bias1', 'u_bias1')):
        B = z[b] * 1e3
        U = z[u] * 1e3
        chi = float(np.sum((B / U) ** 2))
        e[b] = dict(max_abs_mN=float(np.abs(B).max()), u_min_max_mN=[float(U.min()), float(U.max())],
                    max_abs_z=float(np.abs(B / U).max()), chi2_21=chi, p_chi2=float(stats.chi2.sf(chi, 21)))
        if n:
            sd = U * np.sqrt(n)
            e[b]['sd_je_kampagne_mN_min_max'] = [float(sd.min()), float(sd.max())]
            e[b]['max_abs_b_durch_sd'] = float(np.max(np.abs(B) / sd))
            e[b]['u_bei_1000_mN_min_max'] = [float(U.min() * np.sqrt(n / 1000)), float(U.max() * np.sqrt(n / 1000))]
            for nu in (57, 19):
                dk = kap[nu] - 1
                e[b][f'delta_b_kappa{nu}_mN_max'] = float(dk * np.abs(B).max())
                e[b][f'delta_z_kappa{nu}_max'] = float(np.max(dk * np.abs(B) / sd))
                e[b][f'delta_b_kappa{nu}_durch_u1000_max'] = float(np.max(dk * np.abs(B) / (U * np.sqrt(n / 1000))))
    bh[name] = dict(herkunft=herk, n_annahme=n, **e)
out['bhat'] = bh

json.dump(out, open(sys.argv[1], 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
