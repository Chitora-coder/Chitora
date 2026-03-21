# AI Assistant: Project Overview & Progress

This document provides a comprehensive overview of the AI Assistant application, detailing its evolution, architecture, and current state across multiple versions.

## 🎯 Core Concept
The **AI Assistant** is a stealth, low-latency tool designed to solve Multiple Choice Questions (MCQs) and coding problems in real-time. 
1.  **Capture**: Instantly captures a portion or the entire screen.
2.  **Analyze**: Sends the image to a powerful Multimodal AI (Gemini 3 Pro).
3.  **Deliver**: Returns the answer immediately.

---

## 📦 Application Versions

The project consists of two distinct versions, evolving from a silent clipboard tool to a sophisticated visual overlay.

### 🏛️ Version 1: "Silent Mode" (Clipboard)
*File: `main.py`*

The original version designed for maximum stealth and zero visual footprint.

-   **Workflow**:
    1.  User presses **Alt + S**.
    2.  Cursor briefly changes to a "Wait" icon (hourglass) to indicate processing.
    3.  Screen is captured and sent to AI.
    4.  The answer (e.g., "B" or "42") is **copied to the clipboard**.
    5.  User pastes the answer (`Ctrl + V`) where needed.
-   **Key Features**:
    -   **Zero UI**: No windows, no popups. Completely invisible.
    -   **Feedback**: Minimal cursor feedback.
-   **Tech Stack**: Python, `pynput` (hotkeys), `pyperclip`, `ctypes` (cursor control).

### 🛡️ Version 2: "Stealth Overlay" (Native Visual)
*File: `main_v2.py`*

The advanced version introducing a visual interface that remains invisible to screen sharing tools.

-   **Workflow**:
    1.  User presses **Alt + S**.
    2.  Screen is captured and sent to AI.
    3.  The answer appears in a **custom floating overlay** at the bottom of the screen.
    4.  The overlay auto-hides after 2 seconds.
-   **Key Features**:
    -   **Protected Overlay**: Uses Win32 `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)`. **This makes the overlay invisible to OBS, Discord Screen Share, and other capture tools. Only YOU see it.**
    -   **High-Quality Rendering**: Uses **GDI+** for smooth, transparent, anti-aliased text rendering directly on the Windows desktop.
    -   **Click-Through**: The overlay ignores mouse events, ensuring it never interferes with work.
-   **Tech Stack**: Python, `ctypes` (Win32 API, GDI+), `pynput`.

### ⚡ Experimental: Electron Version
*Folder: `electron_v2/`*

An experimental branch attempting to recreate V2's functionality using web technologies.
-   **Architecture**: Hybrid App.
    -   **Frontend**: Electron (Node.js) HTML/CSS overlay.
    -   **Backend**: Python Flask Server (`backend_server.py`) handling AI and Screen Capture.
-   **Status**: Functional, but the Native V2 (`main_v2.py`) is currently preferred for its lightweight nature and robust Win32 integration without the overhead of Chromium.

---

## 🧠 AI Engine
*Files: `ai_engine.py` (V1), `ai_engine_v2.py` (V2)*

The brain of the operation uses Google's latest Gemini models.

-   **Primary Model**: `gemini-3-pro-preview` (November 2025 release). Selected for highest reasoning capability.
-   **Fallback Model**: `gemini-2.5-pro` (in V2) if the primary times out.
-   **Prompts**:
    -   **V1**: General "Elite Multi-Domain Expert".
    -   **V2**: Highly specialized "World-Class C Programming Expert" prompt, instructing the AI to "mentally compile and execute" code.

## 📈 Progress Report

| Feature | Version 1 | Version 2 | Electron Exp |
| :--- | :---: | :---: | :---: |
| **Hotkeys** | ✅ Alt+S | ✅ Alt+S | ✅ Alt+S |
| **Screen Capture** | ✅ Full Monitor | ✅ Full Monitor | ✅ Full Monitor |
| **AI Integration** | ✅ Gemini 3 Pro | ✅ Gemini 3 + Fallback | ✅ Gemini 3 |
| **Output Method** | 📋 Clipboard | 👁️ Visual Overlay | 👁️ Visual Overlay |
| **Screen Share Proof** | ❌ Visible | ✅ **INVISIBLE** | ✅ SetContentProtection |
| **Performance** | 🚀 High | 🚀 High | 🐢 Medium (Electron overhead) |

## 🚀 How to Run

### Setup
1.  Ensure you have Python installed.
2.  Install dependencies: `pip install -r requirements.txt` (typically `google-generativeai`, `python-dotenv`, `pynput`, `pillow`, `pyperclip`, `flask`, `flask-cors`).
3.  **Critical**: You must have a `.env` file with `GEMINI_API_KEY=your_key_here`.

### Running Version 1
```powershell
python main.py
```
*Press Alt+S. Wait for cursor change. Paste answer.*

### Running Version 2 (Recommended)
```powershell
python main_v2.py
```
*Press Alt+S. Look for the answer at the bottom left.*
