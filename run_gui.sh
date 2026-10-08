#!/usr/bin/env bash
# ==============================================================================
# Multiple Sequence Alignment (MSA) Pipeline Studio - Group 5
# Launcher for Git Bash, MinGW, WSL, Linux, and macOS
# ==============================================================================

# Move to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "  Multiple Sequence Alignment (MSA) Pipeline Studio - Group 5"
echo "  High-Performance C++17 Engine with OpenMP Concurrency"
echo "======================================================================"

# Determine Python command
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        echo "[ERROR] Python is not found in PATH."
        echo "Please install Python 3.10+ and add it to your PATH."
        exit 1
    fi
fi

echo "[INFO] Using $($PYTHON_CMD --version)"

# Check and install FastAPI and Uvicorn if needed
"$PYTHON_CMD" -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] Installing required Python packages (fastapi, uvicorn)..."
    "$PYTHON_CMD" -m pip install fastapi uvicorn
fi

# Check if C++ binary exists
if [ ! -f "build/Release/msa_align.exe" ] && [ ! -f "build/msa_align.exe" ] && [ ! -f "build/msa_align" ]; then
    echo "[INFO] C++ alignment executable not found. Building project in Release mode..."
    cmake --build build --config Release
fi

echo "[INFO] Starting FastAPI server on http://localhost:8000 ..."
echo "[INFO] Opening default web browser..."

# Open default browser asynchronously
(
    sleep 2
    if command -v explorer.exe &> /dev/null; then
        explorer.exe "http://localhost:8000"
    elif command -v start &> /dev/null; then
        start "http://localhost:8000"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8000"
    elif command -v open &> /dev/null; then
        open "http://localhost:8000"
    fi
) &

# Run server
exec "$PYTHON_CMD" web/server.py
