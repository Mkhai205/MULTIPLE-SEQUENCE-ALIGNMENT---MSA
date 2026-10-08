@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ======================================================================
echo   Multiple Sequence Alignment (MSA) Pipeline Studio - Group 5
echo   High-Performance C++17 Engine with OpenMP Concurrency
echo ======================================================================

:: Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH.
    echo Please install Python 3.10+ and add it to your PATH environment variable.
    pause
    exit /b 1
)

:: Check FastAPI and Uvicorn packages
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required Python packages (fastapi, uvicorn)...
    python -m pip install fastapi uvicorn
)

:: Check if msa_align.exe exists in build\Release
if not exist "build\Release\msa_align.exe" (
    echo [INFO] build\Release\msa_align.exe was not found.
    echo Building C++ project in Release mode...
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" (
        "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --build build --config Release
    ) else (
        cmake --build build --config Release
    )
    if %errorlevel% neq 0 (
        echo [ERROR] Build failed. Please verify MSVC/CMake environment.
        pause
        exit /b 1
    )
)

echo [INFO] Starting FastAPI server on http://localhost:8000 ...
echo [INFO] Opening default web browser...

:: Open user's default browser after server initializes (use ping delay to avoid redirection errors)
start "" /b cmd /c "ping 127.0.0.1 -n 3 >nul & start http://localhost:8000"

:: Launch server
python web/server.py
