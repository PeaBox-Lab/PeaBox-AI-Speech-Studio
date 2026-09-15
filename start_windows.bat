@echo off
cd /d "%~dp0"
where py >nul 2>nul || (echo Install 64-bit Python 3.11 from python.org and add it to PATH.& pause & exit /b 1)
if not exist .venv py -3.11 -m venv .venv
if not exist .venv\Scripts\python.exe (echo Python 3.11 was not found. Install it and run again.& pause & exit /b 1)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
streamlit run app.py
pause
