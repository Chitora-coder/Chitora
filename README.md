<<<<<<< HEAD
# Zero-Interface AI Assistant

A background tool that captures your screen, identifies C programming questions, and copies the answer to your clipboard instantly.

## 🚀 Usage (Standalone App)
**No terminal required.**

### 1. Setup
1.  Navigate to the `dist` folder inside this directory.
2.  You will see `AI_Assistant.exe`.
3.  **Critical**: Copy the `.env` file from the main folder into this `dist` folder (so it sits next to the .exe).

### 2. Run
Double-click `AI_Assistant.exe`.
*Nothing will appear on screen—this is intentional.* It is now running in the background.

### 3. Use
1.  See a C question.
2.  Press **`Alt` + `S`**.
3.  Paste the answer (`Ctrl` + `V`).

### 4. Stop
To stop it, open Task Manager and end the `AI_Assistant` task.

### 5. Start Automatically (Optional)
To have it run on startup:
1.  **Open Startup Folder**: Press `Win + R`, type `shell:startup`, and press Enter. Keep this folder open.
2.  **Find the App**: Open a separate window to where your `AI_Assistant.exe` is (the `dist` folder).
3.  **Create Shortcut**: 
    -   *Method A (Windows 11)*: Right-click `AI_Assistant.exe` -> Select **"Show more options"** -> **"Create shortcut"**. Then drag that new shortcut into the Startup folder.
    -   *Method B (Drag & Drop)*: Hold down the **`Alt`** key on your keyboard. While holding `Alt`, drag `AI_Assistant.exe` into the Startup folder. It will say "Create link in Startup". Release the mouse.

---

## 💻 Developer Mode (Python)
If you want to run from source:
```powershell
.\venv\Scripts\python main.py
```
-   **Configuration**: Managed in `.env` file.
-   **Hotkeys**: default is `Ctrl+Alt+S`.
=======
use it at your own risk brooo!!!
>>>>>>> ca4d4c5d4a67f1bca1b76521dffefb05e3f7f077
