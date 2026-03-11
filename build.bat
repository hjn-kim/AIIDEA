@echo off
echo ========================================
echo  AIIDEA Build Start
echo ========================================

REM Generate icon.ico from assets/
py make_icon.py
if errorlevel 1 (
    echo [ERROR] Icon generation failed. Check assets/ folder.
    pause
    exit /b 1
)

REM PyInstaller build
py -m PyInstaller AIIDEA.spec --clean -y

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

REM Copy deploy .env (SMTP pre-configured, Gemini key empty)
copy /y ".env.deploy" "dist\AIIDEA\.env"

echo.
echo ========================================
echo  Building Installer (Inno Setup)
echo ========================================

REM Inno Setup compiler path (default install location)
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist %ISCC% (
    echo [SKIP] Inno Setup not found. Skipping installer build.
    echo        Install from: https://jrsoftware.org/isinfo.php
) else (
    %ISCC% AIIDEA_installer.iss
    if errorlevel 1 (
        echo [ERROR] Installer build failed.
        pause
        exit /b 1
    )
    echo [DONE] installer\AIIDEA_Setup.exe created.
)

echo.
echo ========================================
echo  Build Complete
echo ========================================
echo  - App folder : dist\AIIDEA\
echo  - Installer  : installer\AIIDEA_Setup.exe
echo.
pause
