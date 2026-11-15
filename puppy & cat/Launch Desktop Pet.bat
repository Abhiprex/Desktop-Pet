@echo off
cd /d "%~dp0"
if exist "Desktop Pet.exe" (
    start "" "Desktop Pet.exe"
) else (
    start "" "C:\Python314\pythonw.exe" "run_pet.pyw"
)
exit
