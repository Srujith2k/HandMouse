# HandMouse (Windows) — Hand Gesture Mouse Controller

Control your Windows mouse using hand gestures through a webcam.

## What this project does
- **Move cursor** when you are **pointing with the index finger**
- **Left click + drag** using **thumb + middle finger pinch**
- **Right click** using **thumb + ring finger pinch**
- **Scroll mode** using **thumb + pinky pinch** (hold), then move hand up/down

> Note: Gesture mapping depends on your current `gestures/recognizer.py` logic.

---

## Project Setup (Dev)

### 1) Create venv
```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

### 2) Install dependencies
If you already have `requirements.txt`:
```bat
pip install -r requirements.txt
```

Otherwise install your deps manually (example):
```bat
pip install opencv-python mediapipe pynput
```

### 3) Download the model
This project expects:
- `models/hand_landmarker.task`

Download it using:
```bat
powershell -ExecutionPolicy Bypass -File scripts\download_model.ps1
```

### 4) Run
```bat
python main.py
```

---

## Config
This repo uses:
- `config.py` (defaults)
- optionally generates/reads a `config.json` next to the exe or next to your code (depending on your `config.py` implementation)

`config.json` is **not committed** to Git because it is user-specific.

---

## Build EXE (Recommended: onedir)
We build an app folder that contains `HandMouse.exe` and its dependencies.

### One command
```bat
build_exe.bat
```

### Output
- `dist\HandMouse\HandMouse.exe`
- `dist\HandMouse\models\hand_landmarker.task`

---

## Git Notes (Model File)
We do **not** commit `models/hand_landmarker.task` into Git.
- It’s downloaded via `scripts/download_model.ps1`
- It’s ignored via `.gitignore`

We keep the folder tracked using:
- `models/.gitkeep`

---

## Troubleshooting

### “Model file not found”
Confirm the file exists:
- `models/hand_landmarker.task` (dev)
- `dist/HandMouse/models/hand_landmarker.task` (packaged)

Re-run:
```bat
powershell -ExecutionPolicy Bypass -File scripts\download_model.ps1
```

### MediaPipe error inside EXE (missing mediapipe.tasks.c)
Rebuild using the provided `build_exe.bat` (it already includes:
- `--collect-all mediapipe`
- `--hidden-import mediapipe.tasks.c`)
