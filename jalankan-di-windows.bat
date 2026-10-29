@echo off
title QuizVibe - Kahoot & Mentimeter Clone
color 0B
echo ===================================================
echo        MENYALAKAN QUIZVIBE DI WINDOWS
echo ===================================================
echo.

:: Cek apakah Python terinstall
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python belum terinstall di Windows Anda!
    echo Silakan install Python dari https://www.python.org/downloads/
    echo Pastikan centang "Add python.exe to PATH" saat install.
    echo.
    pause
    exit /b
)

echo [1/3] Memeriksa dan menginstall dependensi...
pip install -r requirements.txt >nul 2>&1

echo [2/3] Menginisialisasi Database Kuis...
python database.py

echo [3/3] Menjalankan Server QuizVibe di Port 8000...
echo.
echo ===================================================
echo APLIKASI SUDAH AKTIF!
echo Buka di Browser Anda:
echo   - Layar Host (Proyektor): http://localhost:8000/host.html
echo   - Layar Pemain:          http://localhost:8000/player.html
echo   - Studio Pembuat Kuis:   http://localhost:8000/creator.html
echo ===================================================
echo.
echo Menjalankan browser otomatis...
start http://localhost:8000/host.html

python server.py
pause
