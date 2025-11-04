@echo off
REM ========================================
REM Script de compilation DEBUG - Tamio FS
REM Version avec console pour débogage
REM ========================================

echo.
echo ========================================
echo  Compilation DEBUG Tamio FS
echo  (avec console pour voir les erreurs)
echo ========================================
echo.

REM Nettoyer
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo Compilation de l'application en mode DEBUG...
pyinstaller --onefile ^
            --console ^
            --collect-all customtkinter ^
            --name "Tamio_FS_DEBUG" ^
            --noconfirm ^
            src/app.py

echo.
echo ========================================
echo  COMPILATION DEBUG TERMINEE !
echo ========================================
echo.
echo Le fichier .exe DEBUG est dans: dist\
echo Cette version affiche la console pour voir les erreurs.
echo.
echo  - Tamio_FS_DEBUG.exe
echo.
echo Au demarrage, choisissez entre mode Serveur ou Station.
echo.
pause
