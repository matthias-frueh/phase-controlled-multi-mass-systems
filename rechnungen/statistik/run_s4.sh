#!/bin/sh
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH=../../code
timeout 540 python3 s4_identifizierbarkeit.py b > s4_identifizierbarkeit_rest_ausgabe.txt 2>&1
timeout 540 python3 s4_identifizierbarkeit.py a:40,60 > s4_identifizierbarkeit_hertz_40_60_ausgabe.txt 2>&1
timeout 540 python3 s4_identifizierbarkeit.py a:120,300 > s4_identifizierbarkeit_hertz_120_300_ausgabe.txt 2>&1
echo fertig
