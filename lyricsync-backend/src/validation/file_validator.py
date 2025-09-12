"""File validation utilities."""

import logging
from pathlib import Path
from typing import Set

from fastapi import UploadFile, HTTPException

from ..core.config import AppConfig


class FileValidator:
    """Handles file validation for uploads."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file for transcription."""
        self._check_file_exists(file)
        self._check_file_format(file)
        self._check_file_size(file)
    
    def _check_file_exists(self, file: UploadFile) -> None:
        """Check if file was provided."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
    
    def _check_file_format(self, file: UploadFile) -> None:
        """Check if file format is supported."""
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.config.supported_formats:
            supported_list = ', '.join(sorted(self.config.supported_formats))
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file_extension}'. Supported formats: {supported_list}"
            )
    
    def _check_file_size(self, file: UploadFile) -> None:
        """Check if file size is within limits."""
        # Note: FastAPI's UploadFile doesn't provide size directly
        # Size checking would be implemented during file reading
        pass
    
    def is_valid_audio_extension(self, filename: str) -> bool:
        """Check if filename has a valid audio extension."""
        if not filename:
            return False
        
        extension = Path(filename).suffix.lower()
        return extension in self.config.supported_formats