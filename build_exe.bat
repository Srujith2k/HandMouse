.venv\Scripts\activate
pip install pyinstaller

rmdir /s /q build dist
del /q HandMouse.spec 2>nul

pyinstaller --noconfirm --clean --onedir --name HandMouse ^
  --contents-directory "." ^
  --add-data "models\\hand_landmarker.task;models" ^
  --collect-all mediapipe ^
  --hidden-import mediapipe.tasks.c ^
  main.py
