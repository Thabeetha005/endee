@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Starting Streamlit app..
cd ..
streamlit run simple_app.py --server.port 8512
pause
