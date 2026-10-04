#!/bin/sh
# Zusatzszenarien 20 % / 30 % Kopplung (Indizes 9, 10), 300 Kampagnen
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export PYTHONPATH=../../code
for L in 0 2 3 4 5; do timeout 540 python3 s2_h1_oc_kampagne.py $L 300 20 20 9 9,10 > s2_h1_oc_L${L}_zusatz_ausgabe.txt 2>&1; done
echo fertig
