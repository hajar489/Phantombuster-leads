#!/bin/bash

# 1. Draai je Python script
python3 phantombuster_likes_report-2.py

# 2. Voeg alle nieuwe output-bestanden toe
git add output/

# 3. Commit met datum
datum=$(date +%Y-%m-%d_%H-%M-%S)
git commit -m "Automatische output toegevoegd voor $datum"

# 4. Push naar GitHub
git push origin main
