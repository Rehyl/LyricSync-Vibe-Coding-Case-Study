const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');


// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow();

  // Handle transcription requests from renderer process
  ipcMain.on('transcription-request', async (event, fileName, buffer, quality, modelSize) => {
    try {
      // Use standard FormData and Blob
      const formData = new FormData();
      const blob = new Blob([buffer]);

      // Append the file as a blob
      formData.append('file', blob, fileName);
      
      // Append other form fields
      formData.append('quality', quality);
      formData.append('model_size', modelSize || '');

      // Make API call to backend, letting fetch set the headers
      const response = await fetch('http://localhost:8001/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.detail || 'Unknown error'}`);
      }

      const data = await response.json();
      
      // Send response back to renderer process
      event.reply('transcription-response', data);
    } catch (error) {
      console.error('Transcription request failed:', error);
      // Send error back to renderer process
      event.reply('transcription-error', { message: error.message });
    }
  });

  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
