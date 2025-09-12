"""Interface definitions and protocols for the transcription application."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Protocol


class ModelManager(ABC):
    """Abstract base class for model management."""
    
    @abstractmethod
    def load_model(self, model_name: str) -> Any:
        """Load a model with the given name."""
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the current device."""
        pass
    
    @property
    @abstractmethod
    def device(self) -> str:
        """Get the current device."""
        pass


class TextProcessor(Protocol):
    """Protocol for text processing operations."""
    
    def clean_text(self, text: str) -> str:
        """Clean and process text."""
        ...


class FileValidator(Protocol):
    """Protocol for file validation operations."""
    
    def validate_file(self, file: Any) -> None:
        """Validate uploaded file."""
        ...


class SystemDiagnostics(Protocol):
    """Protocol for system diagnostic operations."""
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        ...
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies."""
        ...