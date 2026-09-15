@echo off
cd /d "%~dp0"
where python >nul 2>nul || (echo Install Python 3.11 and add it to PATH.& pause & exit /b 1)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
pause
