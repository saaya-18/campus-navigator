@echo off
REM Double-click this file to install Flask if needed and start the app.
REM Your browser will open automatically once it's ready.
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
python app.py
pause
