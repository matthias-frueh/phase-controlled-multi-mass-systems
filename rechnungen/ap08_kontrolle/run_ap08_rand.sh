#!/bin/sh
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=../../code
for L in "$@"; do timeout 540 python3 ap08_kontrolle.py $L 400 400 kopplung:0.10638,kopplung:0.115 > ap08_kontrolle_L${L}_rand_ausgabe.txt 2>&1; done
