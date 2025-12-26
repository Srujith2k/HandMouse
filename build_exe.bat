@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM HandMouse - Build EXE (Windows / PyInstaller)
REM Run this from the project root (where main.py exists)
REM ==========================================

REM --- 1) Activate venv ---
if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
) else (
  echo [ERROR] .venv not found.
  echo Create it with: python -m venv .venv
  exit /b 1
)

REM --- 2) Ensure pip + pyinstaller ---
python -m pip install --upgrade pip
pip install pyinstaller

REM --- 3) Ensure model exists (download if missing) ---
if not exist "models\hand_landmarker.task" (
  echo [INFO] Model not found at models\hand_landmarker.task
  echo [INFO] Downloading model using scripts\download_model.ps1 ...

  powershell -ExecutionPolicy Bypass -File "scripts\download_model.ps1"
  if errorlevel 1 (
    echo [ERROR] Model download failed.
    exit /b 1
  )
)

if not exist "models\hand_landmarker.task" (
  echo [ERROR] Model still missing after download.
  echo Expected: models\hand_landmarker.task
  exit /b 1
)

REM --- 4) Clean previous builds ---
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "HandMouse.spec" del /q "HandMouse.spec"

REM --- 5) Build ---
REM NOTE:
REM --contents-directory "." prevents PyInstaller from putting assets in _internal/
REM --add-data puts the model into dist\HandMouse\models\
REM --collect-all mediapipe and hidden-import fix mediapipe.tasks.c packaging issues

pyinstaller --noconfirm --clean --onedir --name HandMouse ^
  --contents-directory "." ^
  --add-data "models\hand_landmarker.task;models" ^
  --collect-all mediapipe ^
  --hidden-import mediapipe.tasks.c ^
  main.py

if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)

echo.
echo [OK] Build finished.
echo EXE: dist\HandMouse\HandMouse.exe
echo Model: dist\HandMouse\models\hand_landmarker.task
echo.
echo To share: zip the entire dist\HandMouse\ folder
endlocal
