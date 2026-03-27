@echo off
echo Installing libraries to your user folder...
echo.

pip install --user --target="%USERPROFILE%\MyApp\libs" pystray Pillow google-genai

echo.
echo Done! Libraries installed to: %USERPROFILE%\MyApp\libs
pause
