#!/usr/bin/env python3
"""
PCMMS – Fluid-Schub mit Phasenkopplung (3 Module)
Direkte Konsolen-Version
"""

import sys, os, csv, time, math
import numpy as np
import pandas as pd

# ------------------------------------------------------------
# KONFIGURATION
# ------------------------------------------------------------
N_GRID = 13
PLOT_ONLY = False
SAVE_CSV = True                    # Auf False setzen, wenn du gar keine Datei willst

# Physikalische Parameter
M_SHELL = 0.6
M_ARM   = 0.05
N_ARMS  = 3
M_TOTAL = M_SHELL + N_ARMS * M_ARM
RATIO   = (N_ARMS * M_ARM) / M_TOTAL

RHO_WATER = 1000.0
CD = 0.8
AREA = 0.03

F_HZ = 10.0
T_CYC = 1.0 / F_HZ
HOLD = 0.65
V_FAST = 0.06
V_SLOW = V_FAST * (1.0 - HOLD) / HOLD

DT = 5e-5
T_SIM = 8.0
T_BURN = 4.0
N_STEPS = int(T_SIM / DT)
N_BURN = int(T_BURN / DT)

# ------------------------------------------------------------
# EGG & SIMULATION
# ------------------------------------------------------------
def egg_vel(t):
    phi = (t % T_CYC) / T_CYC
    tf = 1.0 - HOLD
    if phi < tf:
        s = phi / tf
        return V_FAST * math.sin(math.pi * s)
    s = (phi - tf) / HOLD
    return -V_SLOW * math.sin(math.pi * s)

def simulate_drift(phi2_deg, phi3_deg):
    phi2 = math.radians(phi2_deg)
    phi3 = math.radians(phi3_deg)
    tau2 = phi2 / (2 * math.pi * F_HZ)
    tau3 = phi3 / (2 * math.pi * F_HZ)

    def r_dot(t):
        return (egg_vel(t) + egg_vel(t - tau2) + egg_vel(t - tau3)) / N_ARMS

    c_drag = 0.5 * RHO_WATER * CD * AREA
    Vcm = 0.0
    tail = []
    for i in range(N_STEPS):
        t = i * DT
        v_rel = Vcm - RATIO * r_dot(t)
        a = - (c_drag / M_TOTAL) * abs(v_rel) * v_rel

        k1 = a
        V1 = Vcm + 0.5*DT*k1
        k2 = - (c_drag / M_TOTAL) * abs(V1 - RATIO * r_dot(t + 0.5*DT)) * (V1 - RATIO * r_dot(t + 0.5*DT))
        V2 = Vcm + 0.5*DT*k2
        k3 = - (c_drag / M_TOTAL) * abs(V2 - RATIO * r_dot(t + 0.5*DT)) * (V2 - RATIO * r_dot(t + 0.5*DT))
        V3 = Vcm + DT*k3
        k4 = - (c_drag / M_TOTAL) * abs(V3 - RATIO * r_dot(t + DT)) * (V3 - RATIO * r_dot(t + DT))

        Vcm += DT * (k1 + 2*k2 + 2*k3 + k4) / 6.0
        if i >= N_BURN:
            tail.append(Vcm)

    return float(np.mean(tail))

# ------------------------------------------------------------
# CSV (optional)
# ------------------------------------------------------------
def append_result(phi2, phi3, drift):
    if not SAVE_CSV:
        return
    path = f'sweep_{N_GRID}x{N_GRID}_drift.csv'
    exists = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(['phi2_deg', 'phi3_deg', 'drift_mps', 'drift_mmps'])
        writer.writerow([f'{phi2:.3f}', f'{phi3:.3f}', f'{drift:.6e}', f'{drift*1000:.6f}'])

# ------------------------------------------------------------
# TEXT-HEATMAP (direkt in Konsole)
# ------------------------------------------------------------
def print_text_heatmap(df):
    if df.empty:
        print("Keine Daten vorhanden.")
        return
    
    print("\n" + "="*80)
    print("          TEXT-HEATMAP  (Drift in mm/s)")
    print("="*80)
    
    grid = df.pivot(index='phi3_deg', columns='phi2_deg', values='drift_mps')
    grid = grid.sort_index(ascending=False)
    
    # Einfache Skalierung für Text-Darstellung
    values = (grid * 1000).round(2)
    max_abs = max(abs(values.min().min()), abs(values.max().max())) + 0.01
    
    for phi3 in values.index:
        row_str = f"φ3={phi3:3.0f}° | "
        for phi2 in values.columns:
            val = values.loc[phi3, phi2]
            if abs(val) < 0.05:
                row_str += "  ·   "
            elif val > 0:
                row_str += f" +{val:4.1f}"
            else:
                row_str += f" {val:5.1f}"
        print(row_str)
    print("="*80)
    print(f"Drift-Statistik:  min = {df['drift_mps'].min()*1000:6.2f} mm/s | "
          f"max = {df['drift_mps'].max()*1000:6.2f} mm/s | "
          f"mean = {df['drift_mps'].mean()*1000:6.3f} mm/s")
    print("="*80)

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print('═'*70)
    print(f'PCMMS Fluid-Schub – Direkte Konsolen-Version ({N_GRID}×{N_GRID})')
    print('═'*70)

    if PLOT_ONLY:
        try:
            df = pd.read_csv(f'sweep_{N_GRID}x{N_GRID}_drift.csv')
            print_text_heatmap(df)
        except:
            print("Keine CSV gefunden.")
        return

    # Referenz
    print("Referenz (φ₂=φ₃=0):")
    ref = simulate_drift(0.0, 0.0)
    print(f"  Drift = {ref*1000:.3f} mm/s\n")

    # Sweep
    phis = np.linspace(0, 360, N_GRID, endpoint=False)
    points = [(p2, p3) for p2 in phis for p3 in phis]
    
    t_start = time.time()
    results = []
    
    for j, (p2, p3) in enumerate(points):
        drift = simulate_drift(p2, p3)
        append_result(p2, p3, drift)
        results.append((p2, p3, drift))
        
        if (j+1) % 10 == 0 or (j+1) == len(points):
            eta = (time.time() - t_start) / (j+1) * (len(points) - j - 1)
            print(f"  Fortschritt: {j+1:3d}/{len(points)}  |  ETA \~{eta/60:.1f} min")

    # Finale Ausgabe
    df = pd.DataFrame(results, columns=['phi2_deg', 'phi3_deg', 'drift_mps'])
    print_text_heatmap(df)
    
    total_time = (time.time() - t_start) / 60
    print(f"\nFertig in {total_time:.1f} Minuten.")

if __name__ == '__main__':
    main()