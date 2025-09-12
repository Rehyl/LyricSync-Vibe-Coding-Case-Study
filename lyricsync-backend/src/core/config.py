"""Configuration module for the LyricSync Audio Transcription application."""

from dataclasses import dataclass
from enum import Enum
from typing import Set
import logging
import os


class QualityLevel(Enum):
    """Enumeration for transcription quality levels."""
    FAST = "fast"
    BALANCED = "balanced"
    HIGH = "high"
    BEST = "best"


class ModelSize(Enum):
    """Enumeration for Whisper model sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large-v3"


@dataclass
class AppConfig:
    """Configuration class for application settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    whisper_model: str = "small"
    default_model_size: ModelSize = ModelSize.SMALL
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    supported_formats: Set[str] = None
    
    def __post_init__(self):
        """Initialize default values and configure logging."""
        if self.supported_formats is None:
            self.supported_formats = {
                '.mp3', '.wav', '.m4a', '.flac', '.ogg', 
                '.wma', '.aac', '.mp4', '.mov', '.avi'
            }
        
        # Override with environment variables if available
        self.whisper_model = os.getenv("WHISPER_MODEL", self.whisper_model)
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Global configuration instance
config = AppConfig()