"""FastAPI application setup and route definitions."""

import logging
from typing import Dict, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import JSONResponse

from ..core.config import config, QualityLevel, ModelSize
from ..models.whisper_manager import WhisperModelManager
from ..services.text_processing import TranscriptionCleaner
from ..validation.file_validator import FileValidator
from ..services.transcription import TranscriptionService
from ..monitoring.diagnostics import SystemDiagnosticService


class TranscriptionAPI:
    """Main API application class."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = self._create_app()
        self._initialize_services()
        self._register_routes()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="LyricSync Audio Transcription API",
            description="Local API server for audio transcription using OpenAI Whisper",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        return app
    
    def _initialize_services(self) -> None:
        """Initialize all service dependencies."""
        try:
            # Initialize core services
            self.model_manager = WhisperModelManager(config)
            self.text_cleaner = TranscriptionCleaner()
            self.file_validator = FileValidator(config)
            self.transcription_service = TranscriptionService(
                self.model_manager, self.text_cleaner, self.file_validator, config
            )
            self.diagnostic_service = SystemDiagnosticService()
            
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise RuntimeError(f"Service initialization failed: {e}")
    
    def _register_routes(self) -> None:
        """Register all API routes."""
        
        @self.app.get("/")
        async def root():
            """API root endpoint."""
            return {
                "message": "LyricSync Audio Transcription API",
                "version": "2.0.0",
                "documentation": "/docs",
                "health_check": "/health",
                "system_check": "/system-check"
            }
        
        @self.app.get("/api")
        async def api_info():
            """API information endpoint."""
            return {
                "message": "LyricSync Audio Transcription API",
                "version": "2.0.0",
                "endpoints": {
                    "transcribe": "POST /transcribe - Upload audio file for transcription",
                    "system_check": "GET /system-check - System diagnostics",
                    "privacy_check": "GET /privacy-check - Privacy verification",
                    "health": "GET /health - Health check",
                    "dependencies": "GET /dependencies - Dependency status"
                }
            }
        
        @self.app.post("/transcribe")
        async def transcribe_audio(
            file: UploadFile = File(...), 
            quality: Optional[str] = Form("balanced"),
            model_size: Optional[str] = Form(None)
        ) -> Dict[str, str]:
            """
            Transcribe audio file to text using OpenAI Whisper.
            
            Args:
                file: Audio file to transcribe (multipart/form-data)
                quality: Transcription quality level (fast/balanced/high/best)
                model_size: Whisper model size (small/medium/large-v3)
                
            Returns:
                JSON response with transcription text
            """
            try:
                # Parse quality level
                quality_level = QualityLevel(quality)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid quality level. Choose from: {[q.value for q in QualityLevel]}"
                )
            
            # Parse model size if provided
            model_size_enum = None
            if model_size:
                try:
                    model_size_enum = ModelSize(model_size)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid model size. Choose from: {[m.value for m in ModelSize]}"
                    )
            
            try:
                transcription = await self.transcription_service.transcribe_file(
                    file, quality_level, model_size_enum
                )
                return {"transcription": transcription}
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error during transcription: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            device_info = self.model_manager.get_device_info()
            return {
                "status": "healthy",
                "model": f"whisper-{device_info.get('model_size', 'unknown')}",
                "device": device_info.get('device', 'unknown'),
                "quality_options": [q.value for q in QualityLevel],
                "model_sizes": [m.value for m in ModelSize],
                "supported_formats": list(config.supported_formats)
            }
        
        @self.app.get("/system-check")
        async def system_check():
            """System diagnostic endpoint."""
            system_info = self.diagnostic_service.get_system_info()
            device_info = self.model_manager.get_device_info()
            
            return {
                **system_info,
                **device_info
            }
        
        @self.app.get("/privacy-check")
        async def privacy_check():
            """Privacy verification endpoint."""
            privacy_info = self.diagnostic_service.get_privacy_info()
            device_info = self.model_manager.get_device_info()
            
            privacy_info["technical_details"]["processing_device"] = device_info.get("device")
            
            return privacy_info
        
        @self.app.get("/dependencies")
        async def check_dependencies():
            """Check all system dependencies."""
            return self.diagnostic_service.check_dependencies()
        
        @self.app.exception_handler(404)
        async def not_found_handler(request: Request, exc: HTTPException):
            """Custom 404 handler."""
            return JSONResponse(
                status_code=404,
                content={"detail": "Endpoint not found. Visit /docs for API documentation."}
            )
        
        @self.app.exception_handler(500)
        async def internal_error_handler(request: Request, exc: HTTPException):
            """Custom 500 handler."""
            self.logger.error(f"Internal server error: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error. Check server logs for details."}
            )
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


# Create the API instance
transcription_api = TranscriptionAPI()
app = transcription_api.get_app()