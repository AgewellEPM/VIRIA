#!/bin/bash

# === VIRIA Auto-Start Script ===
# Location: ~/VIRIA/run_viria.sh

echo "[⚙️] Starting VIRIA..."

# Activate your virtual environment if used
VENV_PATH="$HOME/viria_venv"

if [ -d "$VENV_PATH" ]; then
    echo "[🧪] Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "[⚠️] No virtual environment found. Using system Python."
fi

# Navigate to project directory
cd "$HOME/VIRIA" || {
    echo "[❌] VIRIA folder not found at $HOME/VIRIA"
    exit 1
}

# Run VIRIA main in background with log
echo "[🚀] Launching main.py..."
nohup python3 main.py > viria.log 2>&1 &

echo "[✅] VIRIA launched and logging to viria.log"
