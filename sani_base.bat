@echo off
REM Pfad zu deiner virtuellen Umgebung
SET VENV_PATH=C:\Users\cleme\Desktop\JugendForscht\Jugendforscht_ASW_2025\venv

REM venv aktivieren
call "%VENV_PATH%\Scripts\activate.bat"

REM Script ausführen
python "C:\Users\cleme\Desktop\JugendForscht\Jugendforscht_ASW_2025/sani_raspi.py"

REM Optional: Fenster offen lassen

