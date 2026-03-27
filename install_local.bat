@echo off
set LIB_PATH=%USERPROFILE%\MyApp\libs
set PYTHONPATH=%LIB_PATH%

echo Installing libraries to: %LIB_PATH%
echo.

pip install --user --target="%LIB_PATH%" pystray Pillow google-genai

if errorlevel 1 (
    echo.
    echo Install failed. Try running:
    echo pip install --user pystray Pillow google-genai
) else (
    echo.
    echo Done! 
    echo Copy all files to a folder and run start.bat
)

pause
