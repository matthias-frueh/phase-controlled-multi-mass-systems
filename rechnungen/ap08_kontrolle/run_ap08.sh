#!/bin/sh
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=../../code
for L in "$@"; do timeout 540 python3 ap08_kontrolle.py $L 400 300 > ap08_kontrolle_L${L}_ausgabe.txt 2>&1; done
