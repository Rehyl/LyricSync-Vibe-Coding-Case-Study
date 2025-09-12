"""Model management for Whisper transcription models."""

import logging
from typing import Dict, Any

import torch
import whisper

from ..core.interfaces import ModelManager
from ..core.config import AppConfig, QualityLevel, ModelSize


class WhisperModelManager(ModelManager):
    """Concrete implementation of ModelManager for Whisper models."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._model = None
        self._device = None
        self._model_size = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the model manager."""
        self._setup_device()
        self.load_model()
    
    def load_model(self, model_name: str = None) -> whisper.Whisper:
        """Load Whisper model with GPU optimization."""
        if model_name is None:
            model_name = self.config.whisper_model
            
        self._model_size = model_name
        
        self.logger.info(f"Loading Whisper model '{model_name}' on {self._device}")
        
        try:
            self._model = whisper.load_model(model_name, device=self._device)
            self.logger.info(f"Whisper model '{model_name}' loaded successfully on {self._device}")
            
            if self._device == "cuda":
                self._log_gpu_memory("after model loading")
                
            return self._model
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.logger.info("Please ensure CUDA is properly installed for GPU acceleration")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def _setup_device(self) -> None:
        """Setup computing device (CUDA or CPU)."""
        if torch.cuda.is_available():
            self._device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.logger.info(f"GPU detected: {gpu_name} ({gpu_memory:.1f}GB VRAM)")
            self.logger.info("Using GPU acceleration for transcription")
            torch.cuda.empty_cache()
        else:
            self._device = "cpu"
            self.logger.warning("CUDA not available, falling back to CPU")
    
    def _log_gpu_memory(self, context: str) -> None:
        """Log GPU memory usage."""
        if self._device == "cuda":
            memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
            self.logger.info(f"GPU memory usage {context}: {memory_allocated:.2f}GB allocated, {memory_reserved:.2f}GB reserved")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""
        info = {
            "device": self._device,
            "model_size": self._model_size,
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB",
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}GB",
                "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f}GB",
                "cuda_version": torch.version.cuda,
                "cudnn_version": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None
            })
        
        return info
    
    @property
    def model(self) -> whisper.Whisper:
        """Get the loaded model."""
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model
    
    @property
    def device(self) -> str:
        """Get the current device."""
        return self._device
    
    def load_quality_model(self, quality: QualityLevel, model_size: ModelSize = None) -> whisper.Whisper:
        """Load model based on quality preference and model size."""
        quality_models = {
            QualityLevel.FAST: "tiny",
            QualityLevel.BALANCED: "base",
            QualityLevel.HIGH: "small",
            QualityLevel.BEST: "medium"
        }
        
        # Use explicit model size if provided, otherwise use quality mapping
        if model_size:
            selected_model = model_size.value
        else:
            selected_model = quality_models.get(quality, "base")
        
        if selected_model != self._model_size:
            self.logger.info(f"Loading {selected_model} model for {quality.value} quality")
            try:
                return whisper.load_model(selected_model, device=self._device)
            except Exception as e:
                self.logger.warning(f"Failed to load {selected_model} model, using default: {e}")
                return self._model
        
        return self._model
    
    def load_model_by_size(self, model_size: ModelSize) -> whisper.Whisper:
        """Load model by specific size."""
        model_name = model_size.value
        
        if model_name != self._model_size:
            self.logger.info(f"Loading {model_name} model")
            try:
                self._model = whisper.load_model(model_name, device=self._device)
                self._model_size = model_name
                
                if self._device == "cuda":
                    self._log_gpu_memory(f"after loading {model_name} model")
                    
                self.logger.info(f"Whisper model '{model_name}' loaded successfully")
                return self._model
                
            except Exception as e:
                self.logger.error(f"Failed to load {model_name} model: {e}")
                self.logger.info("Falling back to current model")
                return self._model
        
        return self._model
    
    def cleanup_gpu_memory(self) -> None:
        """Clean up GPU memory."""
        if self._device == "cuda":
            torch.cuda.empty_cache()
            self._log_gpu_memory("after cleanup")