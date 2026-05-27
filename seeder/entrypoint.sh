#!/bin/sh
# seeder/entrypoint.sh
# Confirmation gate before running the demo seeder.

echo "[seeder] Force starting demo seed..."
cd /seeder
python seed.py demo
