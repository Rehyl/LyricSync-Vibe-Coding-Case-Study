"""Core transcription service implementation."""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import torch
from fastapi import UploadFile, HTTPException

from ..core.config import QualityLevel, ModelSize, AppConfig
from ..core.interfaces import ModelManager
from .text_processing import TranscriptionCleaner
from ..validation.file_validator import FileValidator


class TranscriptionService:
    """Service for handling audio transcription operations."""
    
    def __init__(self, model_manager: ModelManager, text_cleaner: TranscriptionCleaner, 
                 file_validator: FileValidator, config: AppConfig):
        self.model_manager = model_manager
        self.text_cleaner = text_cleaner
        self.file_validator = file_validator
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def transcribe_file(self, file: UploadFile, quality: QualityLevel = QualityLevel.BALANCED, 
                              model_size: ModelSize = None) -> str:
        """Transcribe uploaded audio file to text."""
        # Validate file
        self.file_validator.validate_file(file)
        
        model_info = model_size.value if model_size else "quality-based"
        self.logger.info(f"Processing file: {file.filename} with {quality.value} quality, model: {model_info}")
        
        # Create temporary file
        temp_file_path = await self._create_temp_file(file)
        
        try:
            # Get appropriate model
            if model_size:
                current_model = self.model_manager.load_model_by_size(model_size)
            else:
                current_model = self.model_manager.load_quality_model(quality)
            
            # Perform transcription
            transcription = await self._perform_transcription(temp_file_path, current_model, quality)
            
            # Clean and return result
            cleaned_transcription = self.text_cleaner.clean_text(transcription)
            
            self.logger.info(f"Transcription completed for {file.filename}")
            return cleaned_transcription
            
        finally:
            # Cleanup temporary file
            self._cleanup_temp_file(temp_file_path)
    
    async def _create_temp_file(self, file: UploadFile) -> str:
        """Create temporary file for audio processing."""
        file_extension = Path(file.filename).suffix.lower()
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                content = await file.read()
                
                # Check file size
                if len(content) > self.config.max_file_size:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large. Maximum size: {self.config.max_file_size / 1024 / 1024:.1f}MB"
                    )
                
                temp_file.write(content)
                return temp_file.name
                
        except Exception as e:
            self.logger.error(f"Failed to create temporary file: {e}")
            raise HTTPException(status_code=500, detail="Failed to process uploaded file")
    
    async def _perform_transcription(self, file_path: str, model, quality: QualityLevel) -> str:
        """Perform the actual transcription."""
        self.logger.info(f"Starting transcription with {quality.value} quality...")
        
        # Configure transcription options
        transcribe_options = self._get_transcription_options()
        
        # Log GPU memory before transcription if using CUDA
        if self.model_manager.device == "cuda":
            self.model_manager.cleanup_gpu_memory()
            self._log_gpu_memory("before transcription")
        
        try:
            result = model.transcribe(file_path, **transcribe_options)
            transcription = result["text"]
            
            # Log GPU memory after transcription if using CUDA
            if self.model_manager.device == "cuda":
                self._log_gpu_memory("after transcription")
                self.model_manager.cleanup_gpu_memory()
            
            return transcription
            
        except FileNotFoundError as e:
            self.logger.error(f"FFmpeg not found: {e}")
            raise HTTPException(
                status_code=500,
                detail="FFmpeg is required but not found. Please install FFmpeg and ensure it's in your PATH. See documentation for setup instructions."
            )
        except Exception as e:
            self.logger.error(f"Transcription error: {str(e)}")
            if "ffmpeg" in str(e).lower():
                raise HTTPException(
                    status_code=500,
                    detail="FFmpeg error occurred. Please ensure FFmpeg is properly installed. See documentation for troubleshooting."
                )
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    def _get_transcription_options(self) -> Dict[str, Any]:
        """Get transcription configuration options."""
        return {
            "fp16": self.model_manager.device == "cuda",  # Enable FP16 for GPU
            "verbose": False,
            "temperature": 0,  # Deterministic decoding
            "no_speech_threshold": 0.6,  # Higher threshold to avoid hallucinations
            "logprob_threshold": -1.0,  # Filter out low-probability tokens
            "compression_ratio_threshold": 2.4,  # Detect repetitive content
            "condition_on_previous_text": False,  # Avoid context bleeding
            "word_timestamps": False,  # Disable for better performance
        }
    
    def _log_gpu_memory(self, context: str) -> None:
        """Log GPU memory usage."""
        if self.model_manager.device == "cuda":
            memory_used = torch.cuda.memory_allocated(0) / 1024**3
            self.logger.info(f"GPU memory {context}: {memory_used:.2f}GB")
    
    def _cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                self.logger.debug(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def get_quality_options(self) -> Dict[str, str]:
        """Get available quality options with descriptions."""
        return {
            QualityLevel.FAST.value: "⚡ Fast (less accurate, tiny model)",
            QualityLevel.BALANCED.value: "⚖️ Balanced (recommended, base model)",
            QualityLevel.HIGH.value: "🎯 High quality (small model)",
            QualityLevel.BEST.value: "🏆 Best quality (very slow, medium model)"
        }
    
    def get_model_options(self) -> Dict[str, str]:
        """Get available model size options with descriptions."""
        return {
            ModelSize.SMALL.value: "🏃 Small (fast, good accuracy)",
            ModelSize.MEDIUM.value: "⚖️ Medium (balanced speed/accuracy)",
            ModelSize.LARGE.value: "🏆 Large v3 (best accuracy, slower)"
        }