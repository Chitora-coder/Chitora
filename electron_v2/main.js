const { app, BrowserWindow, globalShortcut, screen, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const { spawn } = require('child_process');

let pythonProcess = null;
let overlayWindow = null;

// Start Python backend server
function startPythonBackend() {
    const pythonPath = path.join(__dirname, '..', 'venv', 'Scripts', 'python.exe');
    const scriptPath = path.join(__dirname, 'backend_server.py');

    pythonProcess = spawn(pythonPath, [scriptPath]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python Error: ${data}`);
    });
}

// Create the overlay window
function createOverlay() {
    const display = screen.getPrimaryDisplay();
    const { width, height } = display.workAreaSize;

    overlayWindow = new BrowserWindow({
        width: 150,
        height: 80,
        x: 20,
        y: height - 180,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        movable: false,
        minimizable: false,
        maximizable: false,
        closable: false,
        focusable: false,
        hasShadow: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    overlayWindow.loadFile('overlay.html');
    overlayWindow.setAlwaysOnTop(true, 'screen-saver');
    overlayWindow.setVisibleOnAllWorkspaces(true);
    overlayWindow.setIgnoreMouseEvents(true);

    // CRITICAL: Enable content protection to prevent screen capture
    overlayWindow.setContentProtection(true);

    overlayWindow.hide();
}

// Handle screenshot and AI processing
async function processScreenshot() {
    try {
        // Send request to Python backend
        const response = await axios.post('http://localhost:5555/process', {}, {
            timeout: 20000
        });

        const answer = response.data.answer || 'ERR';

        // Show answer in overlay with 'shell' mode
        overlayWindow.webContents.send('show-answer', answer);
        overlayWindow.show();

        // Hide after 5 seconds - enough to read
        setTimeout(() => {
            overlayWindow.hide();
        }, 5000);

    } catch (error) {
        console.error('Error:', error.message);
        overlayWindow.webContents.send('show-answer', 'ERR');
        overlayWindow.show();
        setTimeout(() => overlayWindow.hide(), 2000);
    }
}

app.whenReady().then(() => {
    // Start Python backend
    startPythonBackend();

    // Wait for backend to start
    setTimeout(() => {
        createOverlay();

        // Register global shortcut Alt+S
        const registered = globalShortcut.register('Alt+S', () => {
            console.log('Hotkey triggered!');
            processScreenshot();
        });

        if (!registered) {
            console.log('Hotkey registration failed');
        }

        console.log('MCQ Assistant Ready - Press Alt+S');
    }, 2000);
});

app.on('window-all-closed', () => {
    app.quit();
});

app.on('will-quit', () => {
    globalShortcut.unregisterAll();
    if (pythonProcess) {
        pythonProcess.kill();
    }
});
