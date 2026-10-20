# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 2.2 (B+, Identifizierbarkeit der Lⱼ-Schätzer).
# Zweck: Identifizierbarkeit des nicht über ρ erfassten Phasenrests δⱼ und der Amplitudenstreuung aus n₀ = 20
#   Lⱼ-Läufen (ν = 19), Rauschbodenanteil, Indexversatz aus 60 Piloten (ν = 57), Satterthwaite-ν der Relativphase.
# Eingaben: Argument 1 = struktur.json (Standard: hier). Seed: default_rng(20261019); B = 20 000.
# Laufzeit: gemessen 14 s Wandzeit, 14 s CPU (ein Prozess, ein Thread, 20.10.2026). Aufruf: python3 -I -B ident.py > ident.out
# Herkunft: Nachprüfung 6. Geändert: Pfad von struktur.json.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
# NL6: Identifizierbarkeit des nicht über ρ erfassten Phasenrests δⱼ aus n₀ = 20 Lⱼ-Läufen (ν = 19) und des erfassten
# Indexversatzes aus den Piloten, Ebene H wie generator/ebene_h.py (L-Lauf: Aⱼ, δⱼ, weißes Rauschen je Zelle; kein
# Versatz, kein Jitter). Schätzer je Lauf: kleinste Quadrate der Abweichung vom Modulmittel auf die Quadratur-
# richtung −ik·N̄_c,k (Phase) bzw. N̄_c,k (Amplitude) über Zellen und k ≤ k_max; Rauschboden aus 60 R-Läufen.
import json
import os
import sys
import numpy as np
from scipy import stats
S = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'struktur.json')))
rng = np.random.default_rng(20261019)
Nz, f, fs = 100, 10.0, 6400.0
sz = 0.02 / np.sqrt(3)
sh = sz * np.sqrt(2.0 / (fs * Nz / f))
rad = np.pi / 180
print(f'σ_h je Re/Im und Zelle = {sh*1e3:.4f} mN; κ(19) = {np.sqrt(19/stats.chi2.ppf(0.2,19)):.3f}, κ(57) = {np.sqrt(57/stats.chi2.ppf(0.2,57)):.3f}')
print(f'90-%-Intervall σ̂/σ bei ν = 19: [{np.sqrt(stats.chi2.ppf(0.05,19)/19):.3f}, {np.sqrt(stats.chi2.ppf(0.95,19)/19):.3f}]')
for name in ('A4', 'V1-G0', 'V1-G60h'):
    km = S[name]['k_max']
    Nc = np.array(S[name]['zelle_abs'])[0][:, :km]     # (Zelle, k) Beträge Modul 1
    k = np.arange(1, km + 1)
    w_phase = (k[None, :]**2 * Nc**2).sum()
    w_amp = (Nc**2).sum()
    sd_phase = sh / np.sqrt(w_phase) / rad
    sd_amp = sh / np.sqrt(w_amp)
    w3 = (k[None, :3]**2 * Nc[:, :3]**2).sum()
    print(f'== {name}: Rauschen des Laufschätzers δ̂ = {sd_phase:.4f}° (k ≤ {km}), {sh/np.sqrt(w3)/rad:.4f}° (k ≤ 3); Â: {sd_amp*100:.4f} %')
    for st, (a, p) in {'L0': (0.0, 0.02), 'L1': (0.003, 0.03), 'L2': (0.01, 0.10)}.items():
        print(f'   {st}: Rauschanteil an Var(δ̂) = {sd_phase**2/(p**2+sd_phase**2):.4f}; an Var(Â) = '
              f'{(sd_amp**2/(a**2+sd_amp**2)) if a > 0 else 1.0:.3f}')
    # Monte Carlo des Schätzers (komplexe Zellharmonische mit Phase aus struktur.json nur für Betrag nötig: Drehung
    # ändert die Projektion nicht; wir verwenden reelle positive N̄ je Zelle, k)
    B, n0 = 20000, 20
    for st, (a, p) in {'L0': (0.0, 0.02), 'L1': (0.003, 0.03)}.items():
        A = 1 + a * rng.standard_normal((B, n0))
        d = p * rad * rng.standard_normal((B, n0))
        X = (A[:, :, None, None] * np.exp(-1j * k[None, None, None, :] * d[:, :, None, None]) * Nc[None, None]
             + sh * (rng.standard_normal((B, n0) + Nc.shape) + 1j * rng.standard_normal((B, n0) + Nc.shape)))
        Xm = X.mean(1, keepdims=True)
        D = X - Xm
        # Quadratur: Im(D·conj(N̄)) / (−k|N̄|²) ≈ δ ; kleinste Quadrate mit Gewicht k²|N̄|²
        num = (-(k[None, None, None, :]) * np.imag(D * np.conj(Xm))).sum((2, 3))
        den = (k[None, None, None, :]**2 * np.abs(Xm)**2).sum((2, 3))
        dh = num / den
        # Rauschboden: σ_h² aus 60 R-Läufen (ν = 60·2·3·km, gepoolt)
        sh2 = sh**2 * stats.chi2.rvs(60 * 2 * 3 * km, size=B, random_state=rng) / (60 * 2 * 3 * km)
        boden = sh2 / den.mean(1)
        v = dh.var(1, ddof=1) - boden
        r = np.sqrt(np.maximum(v, 0)) / (p * rad)
        # Kreuzkovarianz k = 1 mit k = 2 (rauschfreier Schätzer), nur Zelle mit Modul
        c0 = int(np.argmax(Nc[:, 0]))
        q1 = -np.imag(D[:, :, c0, 0] * np.conj(Xm[:, :, c0, 0])) / np.abs(Xm[:, :, c0, 0])
        q2 = -np.imag(D[:, :, c0, 1] * np.conj(Xm[:, :, c0, 1])) / np.abs(Xm[:, :, c0, 1])
        cov = (q1 * q2).sum(1) / (n0 - 1) / (1 * 2 * Nc[c0, 0] * Nc[c0, 1])
        r2 = np.sqrt(np.maximum(cov, 0)) / (p * rad)
        print(f'   MC {st}: σ̂_δ/σ_δ Median {np.median(r):.3f}, 5–95 % [{np.quantile(r,0.05):.3f}, {np.quantile(r,0.95):.3f}] '
              f'(χ²₁₉: [{np.sqrt(stats.chi2.ppf(0.05,19)/19):.3f}, {np.sqrt(stats.chi2.ppf(0.95,19)/19):.3f}]); '
              f'Kreuzkovarianz k=1·2: Median {np.median(r2):.3f}, 5–95 % [{np.quantile(r2,0.05):.3f}, {np.quantile(r2,0.95):.3f}]')
# erfasster Versatz aus 60 Piloten (3 Konfigurationen × 20): Var(φ̄) − σ²/N_z, ν = 57
B = 20000
v, j = 0.05, 0.2
x = v * rng.standard_normal((B, 3, 20)) + j / np.sqrt(Nz) * rng.standard_normal((B, 3, 20))
s2 = ((x - x.mean(2, keepdims=True))**2).sum((1, 2)) / 57 - j**2 / Nz
r = np.sqrt(np.maximum(s2, 0)) / v
print(f'Indexversatz 0,05° aus 60 Piloten: σ̂/σ Median {np.median(r):.3f}, 5–95 % [{np.quantile(r,0.05):.3f}, {np.quantile(r,0.95):.3f}]')
# Satterthwaite-ν der Relativphase τⱼ = off_j + δ_j − δ_1 (L1: 0,05², 0,03², 0,03²; ν 57, 19, 19)
for (vo, vd) in ((0.05, 0.03), (0.05, 0.02)):
    comp = np.array([vo**2, vd**2, vd**2]); nus = np.array([57, 19, 19])
    nu = comp.sum()**2 / (comp**2 / nus).sum()
    print(f'Relativphase Versatz {vo}°, δ {vd}°: σ_τ = {np.sqrt(comp.sum()):.4f}°, ν_eff = {nu:.1f}, κ = {np.sqrt(nu/stats.chi2.ppf(0.2,nu)):.3f}; ohne δ-Pooling über Module')
