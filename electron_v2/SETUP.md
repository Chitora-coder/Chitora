# Electron MCQ Assistant Setup

## Prerequisites
- Node.js installed (download from nodejs.org)
- Python virtual environment already set up

## Installation Steps

1. **Install Python Dependencies** (if not already done):
   ```
   cd c:\Users\adijain\Downloads\c_program
   .\venv\Scripts\pip install flask flask-cors
   ```

2. **Install Node.js Dependencies**:
   ```
   cd electron_v2
   npm install
   ```

3. **Copy .env file**:
   - Copy the `.env` file from parent directory to `electron_v2` folder
   - Or create a symlink

## Running the App

```
npm start
```

The app will:
1. Start the Python backend server (port 5555)
2. Launch the Electron overlay window
3. Register the Alt+S hotkey

Press **Alt+S** to capture and solve MCQ questions.

## Building Executable

To create a standalone .exe:
```
npm run build
```

The executable will be in the `dist` folder.

## Screen Capture Protection

The overlay window uses Electron's `setContentProtection(true)` which prevents:
- Screenshots
- Screen recording
- Screen sharing

The answer will only be visible on your physical screen.
