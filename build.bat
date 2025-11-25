@echo off
REM ========================================
REM Script de compilation Tamio FS
REM Crée les fichiers .exe pour Windows
REM ========================================

echo.
echo ========================================
echo  Compilation Tamio FS
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Installez Python depuis https://www.python.org/
    pause
    exit /b 1
)

REM Vérifier que PyInstaller est installé
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller n'est pas installé. Installation en cours...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer PyInstaller
        pause
        exit /b 1
    )
)

echo [1/3] Nettoyage des anciens fichiers...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo [2/3] Compilation de l'application Tamio FS (src/app.py)...
pyinstaller --onefile ^
            --windowed ^
            --collect-all customtkinter ^
            --name "Tamio_Config" ^
            --icon "tamio.ico" ^
            --add-data "tamio.ico;." ^
            --add-data "flush.exe;." ^
            --add-data "xml_extractor.exe;." ^
            --add-data "versions.txt;."
            --add-data "download.txt;."
            --noconfirm ^
            src/app.py

if errorlevel 1 (
    echo ERREUR lors de la compilation
    pause
    exit /b 1
)

echo [3/3] Nettoyage des fichiers temporaires...
rmdir /s /q build
del /q *.spec

echo.
echo ========================================
echo  COMPILATION TERMINEE !
echo ========================================
echo.

