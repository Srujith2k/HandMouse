# scripts/download_model.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$modelsDir = Join-Path $root "models"
$modelPath = Join-Path $modelsDir "hand_landmarker.task"

New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null

# Official MediaPipe hosted model (Hand Landmarker)
$url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

Write-Host "Downloading model..."
Write-Host "From: $url"
Write-Host "To:   $modelPath"

Invoke-WebRequest -Uri $url -OutFile $modelPath

Write-Host "Done."
