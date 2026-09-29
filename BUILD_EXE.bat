@echo off
setlocal EnableDelayedExpansion
title SL v2.0 — Selfish  ·  EXE Builder
color 08
cls

echo.
echo   ███████╗██╗
echo   ██╔════╝██║
echo   ███████╗██║
echo   ╚════██║██║
echo   ███████║███████╗
echo   ╚══════╝╚══════╝
echo   SELFISH v2.0 — Personal Performance System
echo.

echo  [1/5]  Python tekshirilmoqda...
python --version > "%TEMP%\sl_py.txt" 2>&1
if errorlevel 1 (
    echo  [XATO] Python topilmadi!
    echo  https://python.org/downloads — "Add Python to PATH" ni belgilang
    start https://python.org/downloads
    pause & exit /b 1
)
set /p PV=<"%TEMP%\sl_py.txt"
echo  [OK] %PV%

echo.
echo  [2/5]  SL_v2.py tekshirilmoqda...
if not exist "%~dp0SL_v2.py" (
    echo  [XATO] SL_v2.py topilmadi!
    pause & exit /b 1
)
echo  [OK] SL_v2.py topildi

echo.
echo  [3/5]  Kerakli paketlar o'rnatilmoqda...
pip install pyinstaller yt-dlp --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  [XATO] Internet tekshiring.
    pause & exit /b 1
)
echo  [OK] Paketlar tayyor

echo.
echo  [4/5]  SL.exe yaratilmoqda... (2-5 daqiqa)
echo.

cd /d "%~dp0"
if exist build    rmdir /s /q build
if exist dist     rmdir /s /q dist
if exist SL.spec  del /f /q SL.spec

python -m PyInstaller --onefile --windowed --name "SL" --clean --noconfirm SL_v2.py

if errorlevel 1 (
    echo  [XATO] EXE yaratilmadi!
    pause & exit /b 1
)

if not exist "dist\SL.exe" (
    echo  [XATO] dist\SL.exe topilmadi!
    pause & exit /b 1
)

copy /Y "dist\SL.exe" "%~dp0SL.exe" > nul
echo  [OK] SL.exe yaratildi

rmdir /s /q build > nul 2>&1
rmdir /s /q dist  > nul 2>&1
del /f /q SL.spec > nul 2>&1

echo.
echo  [5/5]  Startup sozlanmoqda...
echo  [INFO] SL.exe ishga tushganda o'zi Startup Folder'ga qo'shiladi.
echo  [OK] Tayyor

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║    ✅  SL v2.0 muvaffaqiyatli yaratildi!                 ║
echo  ╠══════════════════════════════════════════════════════════╣
echo  ║                                                          ║
echo  ║  📁  SL.exe: %~dp0SL.exe
echo  ║                                                          ║
echo  ║  🔑  Asosiy parol:   SL2024                             ║
echo  ║  🔐  Vault paroli:   VAULT2024                          ║
echo  ║                                                          ║
echo  ║  🆕  v2.0 YANGILIKLAR:                                  ║
echo  ║     • Startup: Startup Folder (tezkor, kechikishsiz)    ║
echo  ║     • Data: %%APPDATA%%\SL_Selfish\ (uninstalldan keyin) ║
echo  ║     • 90 kunlik tarix + sana tanlash                    ║
echo  ║     • Icon: SL logotipi                                  ║
echo  ║     • Uninstall: Vault ichida                            ║
echo  ║     • Strategic Planning Visual Tool (Miro/Whimsical)   ║
echo  ║       - 6 node turi: State/Goal/Decision/Action/Risk    ║
echo  ║       - Timeline: PAST → PRESENT → FUTURE               ║
echo  ║       - Probability slider · Impact score               ║
echo  ║       - Scenario simulation · AI maslahat               ║
echo  ║                                                          ║
echo  ║  📂  Config: SL.exe yonida (sl_config.json)             ║
echo  ║  📂  Data:   %%APPDATA%%\SL_Selfish\                     ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

explorer "%~dp0"
timeout /t 4 /nobreak > nul
start "" "%~dp0SL.exe"
endlocal
