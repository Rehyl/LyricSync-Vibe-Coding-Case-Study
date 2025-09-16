"""Main entry point for the LyricSync Audio Transcription Server."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.api.routes import app
from src.core.config import config

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("LyricSync Audio Transcription Server")
    print("="*50)
    print(f"Web Interface: http://{config.host}:{config.port}")
    print(f"API Documentation: http://{config.host}:{config.port}/docs")
    print(f"Privacy Check: http://{config.host}:{config.port}/privacy-check")
    print(f"System Check: http://{config.host}:{config.port}/system-check")
    print("="*50 + "\n")
    
    uvicorn.run(
        app, 
        host=config.host, 
        port=config.port,
        log_level=config.log_level.lower()
    )