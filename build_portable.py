#!/usr/bin/env python
import PyInstaller.__main__
import os
import shutil
import json

APP_NAME = "EnglishWordReminder"
SCRIPT = "english_word_reminder.py"

if not os.path.exists("config.json"):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump({"api_key": "", "difficulty": "CEFR B1 (中级)"}, f, ensure_ascii=False, indent=2)

if not os.path.exists("words_cache.json"):
    with open("words_cache.json", "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

print("Building portable version...")

if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

PyInstaller.__main__.run([
    SCRIPT,
    "--name=" + APP_NAME,
    "--onefile",
    "--windowed",
    "--icon=NONE",
    "--collect-all=pystray",
    "--collect-all=PIL",
    "--hidden-import=google.genai",
])

print(f"\nDone! Executable: dist/{APP_NAME}.exe")
print("Copy the .exe file to any folder, it will create config.json and words_cache.json there.")
