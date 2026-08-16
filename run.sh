#!/bin/bash
# Double-click (or run `./run.sh`) to install Flask if needed and start the
# app. Your browser will open automatically once it's ready.
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
python3 app.py
