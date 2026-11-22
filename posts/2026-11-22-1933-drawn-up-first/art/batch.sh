#!/bin/sh
cd "$(dirname "$0")"
for n in 1 2 3; do python3.13 build.py $n l final >> .batch.log 2>&1; done
touch .finals-done
for n in 1 2 3; do python3.13 build.py $n abcdefghijk mid >> .batch.log 2>&1; done
touch .batch-done
