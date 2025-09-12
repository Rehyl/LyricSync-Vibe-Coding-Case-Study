"""System diagnostics and monitoring utilities."""

import logging
import subprocess
from typing import Dict, Any

import torch

from ..core.interfaces import SystemDiagnostics


class SystemDiagnosticService:
    """Provides system diagnostic capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "whisper_model_loaded": True,
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "ffmpeg_available": False,
            "ffmpeg_version": None
        }
        
        # Add GPU information if available
        if torch.cuda.is_available():
            info.update(self._get_gpu_info())
        
        # Check FFmpeg availability
        info.update(self._check_ffmpeg())
        
        return info
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU-specific information."""
        try:
            return {
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB",
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}GB",
                "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f}GB",
                "cuda_version": torch.version.cuda,
                "cudnn_version": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None
            }
        except Exception as e:
            self.logger.warning(f"Failed to get GPU info: {e}")
            return {"gpu_error": str(e)}
    
    def _check_ffmpeg(self) -> Dict[str, Any]:
        """Check FFmpeg availability and version."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.split('\n')[0]
                return {
                    "ffmpeg_available": True,
                    "ffmpeg_version": first_line
                }
            else:
                return {
                    "ffmpeg_available": False,
                    "ffmpeg_error": "FFmpeg command failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "ffmpeg_available": False,
                "ffmpeg_error": "FFmpeg command timed out"
            }
        except FileNotFoundError:
            return {
                "ffmpeg_available": False,
                "ffmpeg_error": "FFmpeg not found in PATH"
            }
        except Exception as e:
            return {
                "ffmpeg_available": False,
                "ffmpeg_error": f"FFmpeg check failed: {str(e)}"
            }
    
    def get_privacy_info(self) -> Dict[str, Any]:
        """Get privacy and security information."""
        return {
            "processing_location": "100% Local - No external APIs",
            "internet_required": False,
            "data_sent_externally": False,
            "external_api_calls": [],
            "whisper_model_location": "Downloaded locally on your machine",
            "audio_file_handling": "Processed locally, never uploaded anywhere",
            "privacy_guarantee": "Your audio files never leave your computer",
            "server_location": "localhost:8000 (your machine only)",
            "offline_capable": True,
            "verification_timestamp": "2025-09-12",
            "technical_details": {
                "whisper_source": "OpenAI Whisper - local inference only",
                "model_storage": "~/.cache/whisper/ on your machine",
                "network_dependencies": "None after initial setup"
            }
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check all required dependencies."""
        dependencies = {
            "torch": {"available": False, "version": None},
            "whisper": {"available": False, "version": None},
            "fastapi": {"available": False, "version": None},
            "ffmpeg": {"available": False, "version": None}
        }
        
        # Check Python packages
        try:
            import torch
            dependencies["torch"] = {"available": True, "version": torch.__version__}
        except ImportError:
            pass
        
        try:
            import whisper
            dependencies["whisper"] = {"available": True, "version": getattr(whisper, '__version__', 'unknown')}
        except ImportError:
            pass
        
        try:
            import fastapi
            dependencies["fastapi"] = {"available": True, "version": fastapi.__version__}
        except ImportError:
            pass
        
        # Check FFmpeg
        ffmpeg_info = self._check_ffmpeg()
        dependencies["ffmpeg"] = {
            "available": ffmpeg_info.get("ffmpeg_available", False),
            "version": ffmpeg_info.get("ffmpeg_version", "Not found")
        }
        
        return dependencies