# English Word Reminder - Specification

## Project Overview
- **Project Name**: English Word Reminder (英语单词提醒助手)
- **Type**: Windows Desktop Application
- **Core Functionality**: A system tray application that displays 10 English words/phrases with Chinese explanations and example sentences every hour
- **Target Users**: English learners who want to improve vocabulary during work

## UI/UX Specification

### Window Structure
- **Main Window**: Hidden by default, shown when displaying words
- **System Tray**: Always present when app is running
- **Popup Window**: Displays 10 words, appears every hour

### Visual Design
- **Color Palette**:
  - Primary: `#4A90D9` (Blue)
  - Secondary: `#F5F5F5` (Light Gray)
  - Accent: `#FF6B6B` (Coral)
  - Text: `#333333` (Dark Gray)
  - Background: `#FFFFFF` (White)
- **Typography**:
  - Title: 16px Bold
  - Word: 14px Bold
  - Definition: 12px Regular
  - Example: 11px Italic
- **Spacing**: 10px padding between items

### Components
1. **System Tray Icon**
   - Shows app status
   - Right-click menu: Show Words, Settings, Exit

2. **Word Display Window**
   - Title bar with close button (manual hide)
   - Scrollable list of 10 words
   - Each word card contains:
     - English word/phrase (bold)
     - Chinese definition
     - Example sentence (italic, with translation)
   - "Hide" button to manually dismiss

3. **Settings** (optional for v1)
   - Gemini API key configuration

## Functionality Specification

### Core Features
1. **System Tray Integration**
   - App runs in background
   - Tray icon with context menu
   - Double-click tray to show words immediately

2. **Hourly Word Display**
   - Timer triggers every 60 minutes
   - Shows popup window with 10 new words
   - Window auto-appears at center of screen

3. **Word Generation (Gemini API)**
   - Request 10 practical English words/phrases
   - Include: word, Chinese definition, example sentence
   - Mix of: daily life words, work-related terms, common phrases

4. **Manual Hide**
   - "Hide" button closes popup window
   - Close button (X) also closes window
   - App continues running in tray

### User Interactions
- Right-click tray icon → Menu options
- Click "Hide" → Dismiss window
- Close window → Dismiss window (app stays in tray)

### Data Flow
1. App starts → Minimizes to tray
2. Timer ticks (every hour) → Call Gemini API
3. API returns words → Display popup
4. User clicks Hide → Window closes
5. Repeat

### Edge Cases
- No internet: Show cached words or error message
- API error: Retry or show last words
- User closes window: App stays in tray

## Technical Stack
- Python 3.x
- tkinter (GUI)
- pystray (System tray)
- google-generativeai (Gemini API)
- threading (Timer)

## Acceptance Criteria
1. App starts and minimizes to system tray
2. Tray icon is visible and has context menu
3. Every hour, a window appears with 10 words
4. Each word has Chinese definition and example
5. User can manually hide the window
6. App continues running after hiding window
7. Exit from tray menu closes app completely
