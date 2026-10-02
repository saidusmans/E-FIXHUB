@echo off
TITLE E-Fix Hub 2.0 Enterprise - Boot Sequence
echo ===================================================
echo [SYSTEM] INITIALIZING E-FIX HUB BOOT SEQUENCE...
echo ===================================================

:: Check for virtual environment
IF EXIST ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo [WARN] Virtual environment '.venv' not found. Ensure dependencies are installed globally or in .venv.
)

:: Run database sync
echo [INFO] Synchronizing Industrial Database...
python manage.py migrate

:: Launch Edge Browser (try full path first, fallback to protocol)
echo [INFO] Launching Neural Interface at http://127.0.0.1:8000/
IF EXIST "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" http://127.0.0.1:8000/
) ELSE IF EXIST "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" http://127.0.0.1:8000/
) ELSE (
    start microsoft-edge:http://127.0.0.1:8000/
)

:: Start the server
echo [INFO] Starting Core Engine...
python manage.py runserver

pause
