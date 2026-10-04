#!/bin/sh
# Läufe der H1-OC-Simulation, je Rauschstufe ein Prozess (Wandzeit je Lauf < 540 s)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export PYTHONPATH=../../code
for L in 0 1 2 3 4 5; do
  timeout 540 python3 s2_h1_oc_kampagne.py $L 600 20 20 9 > s2_h1_oc_L${L}_ausgabe.txt 2>&1
done
echo fertig
