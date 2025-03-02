@echo off
REM Navigate to your project directory (adjust if needed)
cd /d "C:\Users\OscarEriksson\Documents\remarkable-inputstream"

REM Activate the virtual environment
call .venv\Scripts\activate

REM Run your Python script
python app.py

REM Optional: Deactivate the virtual environment when done
deactivate
