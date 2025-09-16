// renderer.js - Logica del processo di rendering per l'app LyricSync

document.addEventListener('DOMContentLoaded', () => {
  // Otteniamo i riferimenti agli elementi DOM
  const uploadArea = document.querySelector('.upload-area');
  const fileInput = document.getElementById('file-input');
  const transcriptionButton = document.querySelector('.btn-primary');
  const transcriptionResult = document.getElementById('transcription-result');
  const transcriptionText = document.getElementById('transcription-text');

  // Gestiamo il click sull'area di upload per aprire la finestra di dialogo
  uploadArea.addEventListener('click', () => {
    fileInput.click();
  });

  // Gestiamo la selezione del file
  fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
      // Aggiorniamo il nome del file nel campo di testo
      const fileNameInput = document.getElementById('file-name');
      if (fileNameInput) {
        fileNameInput.value = file.name;
      }
      
      // Mostriamo un feedback visivo che il file è stato selezionato
      uploadArea.classList.add('file-selected');
      const uploadText = uploadArea.querySelector('p');
      if (uploadText) {
        uploadText.textContent = `File selezionato: ${file.name}`;
      }
    }
  });

  // Gestiamo il click sul pulsante "AVVIA TRASCRIZIONE"
  transcriptionButton.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (!file) {
      alert('Seleziona un file audio prima di avviare la trascrizione.');
      return;
    }

    // Otteniamo i valori selezionati per qualità e modello
    const quality = document.getElementById('quality').value;
    const modelSize = document.getElementById('model-size').value;

    // Disabilitiamo il pulsante durante l'elaborazione
    transcriptionButton.disabled = true;
    transcriptionButton.textContent = 'TRASCRIZIONE IN CORSO...';

    // Leggiamo il file e inviamo i suoi dati
    const reader = new FileReader();
    reader.onload = (e) => {
      const arrayBuffer = e.target.result;
      window.electronAPI.sendTranscriptionRequest(file.name, arrayBuffer, quality, modelSize);
    };
    reader.onerror = (e) => {
      console.error('File reading error:', e);
      alert('Errore durante la lettura del file.');
      transcriptionButton.disabled = false;
      transcriptionButton.textContent = 'AVVIA TRASCRIZIONE';
    };
    reader.readAsArrayBuffer(file);
  });

  // Gestiamo la risposta dal backend
  window.electronAPI.onTranscriptionResponse((data) => {
    // Riabilitiamo il pulsante
    transcriptionButton.disabled = false;
    transcriptionButton.textContent = 'AVVIA TRASCRIZIONE';

    // Visualizziamo la trascrizione ricevuta
    if (data && data.transcription) {
      transcriptionText.textContent = data.transcription;
      transcriptionResult.style.display = 'block';
    } else {
      transcriptionText.textContent = 'Trascrizione ricevuta ma vuota.';
      transcriptionResult.style.display = 'block';
    }
  });

  // Gestiamo gli errori dal backend
  window.electronAPI.onTranscriptionError((error) => {
    // Riabilitiamo il pulsante
    transcriptionButton.disabled = false;
    transcriptionButton.textContent = 'AVVIA TRASCRIZIONE';

    // Visualizziamo l'errore
    console.error('Errore durante la trascrizione:', error);
    alert(`Errore durante la trascrizione: ${error.message || error}`);
  });
});