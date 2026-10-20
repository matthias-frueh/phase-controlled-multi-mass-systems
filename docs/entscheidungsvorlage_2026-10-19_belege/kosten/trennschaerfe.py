# Beleg zur Entscheidungsvorlage vom 19.10.2026 (docs/entscheidungsvorlage_2026-10-19.md), Abschnitt 6 (eine G4-Variante für die zweite Anordnung, etwa 4,4 Standardfehler).
# Zweck: Trennschärfe der zweiten Phase-0-Anordnung in R1 (Normalnäherung mit Überdispersion), Eingaben aus der
#   Tabelle „Halte je Kampagne“ in Abschnitt 3.1.
# Seed: keiner. Laufzeit: gemessen unter 1 s (ein Prozess, ein Thread, 20.10.2026). Aufruf: python3 -I -B trennschaerfe.py > trennschaerfe.out
# Herkunft: Nachprüfung 7. Gegenüber der Quelle nur dieser Kopf.
# ---- Ende des Belegkopfs; ab hier das Skript in der Fassung der Quelle (nur Pfade wie oben angegeben geändert) ----
"""NL7: Trennschärfe der zweiten Phase-0-Anordnung in R1 (analytisch, Normalnäherung, Überdispersion D).
Eingaben gelesen aus der Vorlage 3.1 (Tabelle Halte je Kampagne): Generator 0,13 (D 2,0–2,1), 42 R 0,20 (D 2,5)."""
import math
for n in (1000, 3000):
    se_g = math.sqrt(2.05 * 0.13 / n); se_p = math.sqrt(2.5 * 0.20 / n)
    se_d = math.hypot(se_g, se_p)
    print(f'n={n}: SE Generator {se_g:.4f}, SE 42R {se_p:.4f}, SE Differenz {se_d:.4f}, Differenz/SE {(0.20-0.13)/se_d:.1f}')
p = 5/30
print('SE Anteil mit Halt bei p=5/30, n=1000:', round(math.sqrt(p*(1-p)/1000), 4))
