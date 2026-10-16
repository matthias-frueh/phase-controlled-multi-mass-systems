"""Gemeinsame Konventionen (Präreg v2 §4, A1, A9.4) für Generator, Anpassung und Auswertung.

Harmonische: N_k = (2/N_θ)·Σₙ N̄(θₙ)·e^{−ikθₙ}, k ≥ 1, θₙ = 2πn/N_θ, N_θ = 2000; Rücktransformation
N̄(θ) = ⟨N⟩ + Σ_k Re(N_k·e^{ikθ}). |N_k| ist die Amplitude wie in `linear_solver.py --section`.
Phasen: in Dateien und Schnittstellen in Grad, intern in Radiant. Ein um φ verzögertes Signal (Modul j mit Phase
φⱼ) erhält den Faktor e^{−ikφ}; θ = 0 am Indeximpuls von Modul 1 (Kombinationsläufe), von Modul j (Lⱼ, Lⱼ′) bzw. am
virtuellen Takt (Referenzläufe). Profilphase φⱼ^P = φⱼ + Δδⱼ (A1). Indizes: Zellen c = 1, 2, 3 und Module j = 1, 2, 3
stehen in Feldern an den Stellen 0, 1, 2.

F_min, F_max, Schiefe und A gelten für die bandbegrenzte Kurve auf ihren N_θ Stützstellen (A1). Die zweiten und
dritten Momente folgen exakt aus den Harmonischen, solange 3·k_max < N_θ: m₂ = ½·Σ|N_k|²,
m₃ = ¾·Re Σ_{a,b ≥ 1, a+b ≤ K} N_a·N_b·conj(N_{a+b}) (Präreg A2.3 für die Sonderfälle).
"""
import itertools

import numpy as np

N_THETA = 2000
SCHNITT_PHI2 = np.arange(100.0, 140.0 + 1e-9, 2.0)      # 21 Schnittpunkte (Profilphasen φ₂, φ₃ = 240°)
SCHNITT_PHI3 = 240.0
PILOTEN = ((110.0, 250.0), (130.0, 230.0), (110.0, 252.0))
GROESSEN_H1 = ('F_min_rel', 'Re_N1', 'Im_N1', 'Re_N2', 'Im_N2', 'Re_N3', 'Im_N3')   # 7 Größen je Punkt


def theta_raster(n=N_THETA):
    return 2 * np.pi * np.arange(n) / n


def basis(kmax, n=N_THETA, k0=1):
    """Reelle Basis (2K × n): Zeilen cos(kθ) und −sin(kθ) für k = k0 … kmax; Kurve = [Re N, Im N] @ Basis."""
    th = theta_raster(n)
    k = np.arange(k0, kmax + 1)
    return np.concatenate([np.cos(np.outer(k, th)), -np.sin(np.outer(k, th))], 0)


def reell(Nk):
    """Komplexe Harmonische (…, K) → reelle Koeffizienten (…, 2K) passend zu basis()."""
    Nk = np.asarray(Nk)
    return np.concatenate([Nk.real, Nk.imag], -1)


def kurve(Nk, n=N_THETA):
    """Schwingungsanteil Σ_k Re(N_k e^{ikθ}) auf dem Raster (für k = 1 … K der letzten Achse)."""
    Nk = np.asarray(Nk, complex)
    K = Nk.shape[-1]
    if 2 * K >= n:
        raise ValueError(f'k_max = {K} zu groß für N_θ = {n}')
    Y = np.zeros(Nk.shape[:-1] + (n // 2 + 1,), complex)
    Y[..., 1:K + 1] = Nk / 2
    return np.fft.irfft(Y, n, axis=-1) * n


def harmonische(x, kmax, n=None):
    """Harmonische k = 1 … kmax einer Kurve auf n Stützstellen (letzte Achse) nach der Präreg-Konvention."""
    x = np.asarray(x, float)
    n = x.shape[-1] if n is None else n
    return 2 * np.fft.rfft(x, axis=-1)[..., 1:kmax + 1] / n


def fmin_rel(Nk, n=N_THETA):
    """F_min − ⟨N⟩ der bandbegrenzten Kurve auf N_θ Stützstellen."""
    return kurve(Nk, n).min(-1)


def fmax_rel(Nk, n=N_THETA):
    return kurve(Nk, n).max(-1)


def momente(Nk):
    """m₂ und m₃ des Schwingungsanteils über die N_θ Stützstellen, exakt aus den Harmonischen (3K < N_θ)."""
    Nk = np.asarray(Nk, complex)
    K = Nk.shape[-1]
    m2 = 0.5 * (np.abs(Nk) ** 2).sum(-1)
    m3 = np.zeros(Nk.shape[:-1])
    for s in range(2, K + 1):                     # s = a + b, a, b ≥ 1
        a = np.arange(1, s)
        m3 = m3 + (Nk[..., a - 1] * Nk[..., s - a - 1]).sum(-1) * np.conj(Nk[..., s - 1])
    return m2, 0.75 * np.real(m3)


def schiefe(Nk):
    """γ₁ = m₃/m₂^{3/2} (wie scipy.stats.skew über die Stützstellen); nan bei konstanter Kurve."""
    m2, m3 = momente(Nk)
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(m2 > 0, m3 / np.where(m2 > 0, m2, 1.0) ** 1.5, np.nan)


def kenngroessen(Nk, n=N_THETA):
    """F_min − ⟨N⟩, F_max − ⟨N⟩, γ₁ und A = (F_max − ⟨N⟩)/(⟨N⟩ − F_min) einer bandbegrenzten Kurve."""
    x = kurve(Nk, n)
    mn, mx = x.min(-1), x.max(-1)
    with np.errstate(invalid='ignore', divide='ignore'):
        A = np.where(mn < 0, mx / np.where(mn < 0, -mn, 1.0), np.nan)
    return dict(F_min_rel=mn, F_max_rel=mx, gamma1=schiefe(Nk), A=A)


def h1_vektor(Nk, n=N_THETA):
    """Die sieben H1-Größen (F_min − ⟨N⟩, Re/Im N₁, N₂, N₃) aus bandbegrenzten Harmonischen (…, k_max ≥ 3)."""
    Nk = np.asarray(Nk, complex)
    if Nk.shape[-1] < 3:
        raise ValueError('k_max ≥ 3 erwartet (Präreg §5.4, Tabelle F)')
    return np.stack([fmin_rel(Nk, n)] + [f(Nk[..., k]) for k in range(3) for f in (np.real, np.imag)], -1)


def zeigerfaktor(phi_grad, k):
    """e^{−ikφ} für Phasen φ (Grad, beliebige Form) und Ordnungen k (letzte Achse angehängt)."""
    return np.exp(-1j * np.multiply.outer(np.radians(np.asarray(phi_grad, float)), np.asarray(k, float)))


def wickel_grad(x):
    """Phase in Grad auf (−180°, 180°]."""
    return 180.0 - np.mod(180.0 - np.asarray(x, float), 360.0)


def zirkulaer_mittel_grad(phi_grad, achse=-1):
    """Zirkuläres Mittel arg⟨e^{iφ}⟩ und Jitter σ = √(−2 ln R) in Grad (A1)."""
    z = np.exp(1j * np.radians(np.asarray(phi_grad, float))).mean(achse)
    R = np.clip(np.abs(z), 1e-300, 1.0)
    return np.degrees(np.angle(z)) % 360.0, np.degrees(np.sqrt(-2 * np.log(R)))


def s3_bilder(phi2, phi3):
    """Die sechs Bilder einer Konfiguration (0, φ₂, φ₃) unter Modulvertauschung und Zeitverschiebung (S₃):
    Liste von (Permutation σ, (ψ₂, ψ₃), φ_ref) mit ψⱼ = φ_σ(j) − φ_σ(1). Bei identischen Modulen gilt
    N_k(Bild) = N_k(Basis)·e^{ikφ_ref} (Phasenregel arg N_k → arg N_k + k·φ_ref), F_min − ⟨N⟩, |N_k| und γ₁
    bleiben gleich. Bei ungleichen Modulen gilt das nicht; die Superposition der gemessenen Einzelantworten
    sagt jedes Bild trotzdem richtig vorher."""
    phi = np.array([0.0, phi2, phi3])
    out = []
    for perm in itertools.permutations(range(3)):
        ref = phi[perm[0]]
        psi = np.mod(phi[list(perm)] - ref, 360.0)
        out.append((perm, (psi[1], psi[2]), ref))
    return out


def kammfaktor(phi2, phi3, k):
    """(1 + e^{−ikφ₂} + e^{−ikφ₃})/3 (Präreg A2.1)."""
    k = np.asarray(k, float)
    return (1 + np.exp(-1j * k * np.radians(phi2)) + np.exp(-1j * k * np.radians(phi3))) / 3


def abtastrate_a6(f, kmax, schwelle=1e-3):
    """Kleinste Abtastrate mit (π·k_max·f/f_s)²/2 ≤ schwelle (Präreg §5.1, A6)."""
    return np.pi * kmax * f / np.sqrt(2 * schwelle)
