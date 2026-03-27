@echo off
echo Trying to install libraries...
echo.

pip install --user pystray Pillow google-genai

if errorlevel 1 (
    echo.
    echo Failed. Let's try another way...
    pip install pystray Pillow google-genai --force-reinstall
)

pause
