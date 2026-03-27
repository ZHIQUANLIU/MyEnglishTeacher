@echo off
echo Installing required libraries to your user directory...
echo.

pip install --user pystray
if errorlevel 1 (echo Failed: pystray)

pip install --user Pillow
if errorlevel 1 (echo Failed: Pillow)

pip install --user google-genai
if errorlevel 1 (echo Failed: google-genai)

echo.
echo All done! Now you can run start.bat
pause
