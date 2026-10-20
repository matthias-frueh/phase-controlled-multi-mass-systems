# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitte 1.2, 3.1 und 3.2.
# Zweck: Auswertung der Detailsimulation (Halte je Kampagne, Dispersionsindex, P(≥ k), Kette über dasselbe R₀,
#   Halt an R₂/R₃, Anteile nach u, Option (iii), Erschöpfung bei W = 1, 2, 3) und Verträglichkeit der 30 Kampagnen.
# Eingaben: Argument 1 = Verzeichnis mit detail_gen_F_201.npz und detail_A8_F_202.npz (aus detail.py, nicht im
#   Paket), Argument 2 = Verzeichnis mit den Checkpoint-Ordnern korr-N01-{A4,V1G0,V1G60h}-wiederholungen/ der Korrekturrunde von PR #23
#   (flüchtig, am 18.10.2026 unter /tmp/pcmms-ablauf-vergleich-20261018/ erzeugt; SHA-256 der ablauf_*.json in
#   docs/ap13_kmax_wiederholungen_2026-10-17/ergebnisse.json, Schlüssel "checkpoints")
# Seed: keiner. Laufzeit: gemessen 1 s Wandzeit, 1 s CPU (ein Prozess, ein Thread, 20.10.2026).
# Aufruf: python3 -I -B auswertung_detail.py <npz-ordner> <checkpoint-basis> > auswertung_detail.out
# Herkunft: Nachprüfung 1. Geändert: Checkpoint-Pfad als Argument 2 (vorher fest).
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""Auswertung der Detailsimulation (strenge Lesart, Wiederaufnahme ohne Befund, unbegrenzt) und Verträglichkeit."""
import sys, json, csv
import numpy as np
from scipy.stats import poisson, binom, norm
D = sys.argv[1]
for n in ('gen_F_201', 'A8_F_202'):
    d = np.load(f'{D}/detail_{n}.npz'); z = d['z']; u = d['u']
    G1, G1f, R1, Xs, S1X, S1A, al, nl, nref, G1L, WA, XW, R3, R2, WAA = z.T
    H = S1X + S1A + WA
    N = len(H)
    print(f'== {n}: N = {N}')
    print('  Halte je Kampagne: Mittel %.4f Var %.4f D %.2f; P(≥1..5) %s' % (H.mean(), H.var(), H.var() / H.mean(),
          [round(float((H >= k).mean()), 4) for k in (1, 2, 3, 4, 5)]))
    print('  homogene Poisson gleichen Mittels: P(≥2) %.4f P(≥4) %.1e' % (poisson.sf(1, H.mean()), poisson.sf(3, H.mean())))
    print('  W-Satz-Alarme nach Alarm-Halt: %.4f je Kampagne = %.2f je S1-Alarmhalt; Kettenfaktor (S1+WA)/S1 = %.2f' %
          (WAA.mean(), WAA.mean() / S1A.mean(), H.mean() / (S1X + S1A).mean()))
    print('  Halt an R₂ %.4f, an R₃ %.4f je Kampagne; X′ aus W-Lⱼ %.4f → Halt an X′ (×0,0167) %.1e' % (R2.mean(), R3.mean(), XW.mean(), XW.mean() * 7 * 2 * 0.05 / 42))
    q10 = np.quantile(u, 0.1)
    for lab, m in (('unterstes Zehntel u', u <= q10), ('u < 0,85', u < 0.85)):
        print(f'  {lab}: Anteil Kampagnen {m.mean():.3f}, Anteil Halte {H[m].sum() / H.sum():.2f}, X′-Halte {S1X[m].sum() / S1X.sum():.2f}, '
              f'R₂/R₃-Halte {(R2 + R3)[m].sum() / (R2 + R3).sum():.2f}, P(≥4 | Gruppe) {(H[m] >= 4).mean():.4f}, Anteil an ≥4 {((H >= 4) & m).sum() / max((H >= 4).sum(), 1):.2f}')
    ok = H == 0
    print('  Option (iii) (nur ohne Halt): Anteil %.3f; Mittel u %.4f gegen %.4f; X′ %.3f gegen %.3f; G1 %.3f gegen %.3f; R₁ %.3f gegen %.3f' %
          (ok.mean(), u[ok].mean(), u.mean(), Xs[ok].mean(), Xs.mean(), G1[ok].mean(), G1.mean(), R1[ok].mean(), R1.mean()))
    print('  ohne Halt: P(u<0,85) %.3f gegen %.3f' % ((u[ok] < 0.85).mean(), (u < 0.85).mean()))
    for W in (1, 2, 3):
        print(f'   W = {W}: nicht fortgesetzt (Halte > W) {float((H > W).mean()):.4f} ± {float(np.sqrt((H > W).mean() / N)):.4f}')
# Verträglichkeit der 30 Kampagnen
SIG = 20e-3 / np.sqrt(6400 * 10.0)
BAS = sys.argv[2]                       # flüchtige Checkpoints (Kopf)
p_x = []
for a in ('A4', 'V1G0', 'V1G60h'):
    j = json.load(open(f'{BAS}/korr-N01-{a}-wiederholungen/ablauf_korr-N01-{a}-wiederholungen.json'))
    for b in j['inhalt']['befunde']:
        e = b['teil_b']['eps_ctrl']
        for x in b['ablauf']['x_strich']:
            if x.get('g1') is not None:
                p_x.append((b['szenario'], b['index'], 2 * norm.sf(e / (np.sqrt(1.5) * SIG)), bool(x['g1'])))
lam = sum(p for *_, p, _ in p_x); obs = sum(g for *_, g in p_x)
print('X′ mit G1-Prüfung: %d, erwartete S1 über X′ (β = 0,5, gegeben ε) %.3f, beobachtet %d, P(≥%d) = %.3f' % (len(p_x), lam, obs, obs, poisson.sf(obs - 1, lam)))
for s, i, p, g in p_x:
    if g:
        print('   haltendes X′:', s, i, 'p = %.4f' % p)
for lab, p in (('gen_F', None), ('fest', 0.0302)):
    pass
print('Kampagnen mit S1 (erster Halt, ohne Wiederaufnahme): beobachtet 4/30')
for lab, p in (('σ̂ bekannt (fest)', 0.0302), ('gen_F (61 R, F-Test)', 0.0864), ('A8_F (42 R, F-Test)', 0.1216), ('A8 (42 R, ohne F-Test)', 0.1313)):
    print('   %-24s p = %.4f: erwartet %.2f, P(≥4 | Bin(30, p)) = %.3f' % (lab, p, 30 * p, binom.sf(3, 30, p)))
print('davon über X′ 2/30: gen_F λ = 0,0118 → P(≥2) = %.3f; über Alarm 2/30: λ = 0,0906 → P(≥2) = %.3f' % (poisson.sf(1, 30 * 0.0118), poisson.sf(1, 30 * 0.0906)))
print('bedingte p1(u) je Lauf (G1 Rand × G1 mittig):', {u: float('%.2g' % (2 * norm.sf(3 * u) * 2 * norm.sf(3 * u * np.sqrt(0.75)))) for u in (0.7, 0.8, 0.9, 1.0, 1.1, 1.2)})
