@echo off
cd /d "%~dp0"
set PYTHONPATH=src
echo.
echo  ╔══════════════════════════════════════╗
echo  ║  MedCommand Hospital Operations v2.0 ║
echo  ╚══════════════════════════════════════╝
echo.
echo  Starting dashboard...
echo  Open: http://localhost:8501
echo.
streamlit run app.py
pause
