const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1800,
    height: 1200,
    webPreferences: { nodeIntegration: true, contextIsolation: false }
  });
  mainWindow.loadFile(path.join(__dirname, './frontend/build/index.html'));
}

function startPythonBackend() {
  const backendPath = app.isPackaged ? path.join(process.resourcesPath, 'backend') : path.join(__dirname, 'backend');
  const script = (process.platform === 'win32') ? 'flask.exe' : 'flask';
  const venvPath = (process.platform === 'win32') ? 'Scripts' : 'bin';
  const scriptPath = path.join(backendPath, 'venv', venvPath, script);

  pythonProcess = spawn(scriptPath, ['run', '--port=5555'], { cwd: backendPath });
  pythonProcess.stdout.on('data', (data) => console.log(`Python Backend: ${data}`));
  pythonProcess.stderr.on('data', (data) => console.error(`Python Backend Error: ${data}`));
}

app.whenReady().then(() => {
  if (app.isPackaged) startPythonBackend();
  createMainWindow();
});

app.on('window-all-closed', () => process.platform !== 'darwin' && app.quit());
app.on('will-quit', () => pythonProcess && pythonProcess.kill());
