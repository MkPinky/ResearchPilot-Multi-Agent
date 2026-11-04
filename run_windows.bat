@echo off
echo ==========================================
echo ResearchPilot - Multi-Agent Research Assistant
echo ==========================================
if not exist .venv (
  py -3.11 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env (
  copy .env.example .env
  echo.
  echo Created .env. Add your GROQ_API_KEY, then run this file again.
  notepad .env
  pause
  exit /b
)
streamlit run app.py
pause
