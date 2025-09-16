const { contextBridge, ipcRenderer } = require('electron');

// Esponi le funzionalità al processo di rendering in modo sicuro
contextBridge.exposeInMainWorld('electronAPI', {
  // Funzione per inviare un file al backend per la trascrizione
   sendTranscriptionRequest: (fileName, arrayBuffer, quality, modelSize) => {
     const buffer = Buffer.from(arrayBuffer);
     ipcRenderer.send('transcription-request', fileName, buffer, quality, modelSize);
   },

  // Funzione per ricevere la risposta dal backend
  onTranscriptionResponse: (callback) => {
    ipcRenderer.on('transcription-response', (event, data) => {
      callback(data);
    });
  },

  // Funzione per ricevere eventuali errori dal backend
  onTranscriptionError: (callback) => {
    ipcRenderer.on('transcription-error', (event, error) => {
      callback(error);
    });
  }
});
