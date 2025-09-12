# 🎵 LyricSync Audio Transcription Server

A Python-based audio transcription server using OpenAI Whisper for local, privacy-focused audio-to-text conversion.

## 🚀 Features

- **Local Processing**: 100% offline transcription - no external API calls
- **Privacy First**: Audio files never leave your computer
- **GPU Acceleration**: Automatic CUDA detection for faster processing
- **Multiple Models**: Support for various Whisper model sizes (small, medium, large-v3)
- **Quality Options**: Configurable transcription quality levels
- **REST API**: Clean FastAPI-based REST endpoints
- **File Support**: Wide range of audio/video formats (MP3, WAV, M4A, FLAC, OGG, AAC, MP4, MOV, AVI)

## 🏗️ Architecture

The application follows a clean, modular architecture with:

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Clean service dependencies
- **Interface-based Design**: Easy to extend and test
- **SOLID Principles**: Maintainable and scalable codebase

### Core Components

- **API Layer**: FastAPI routes and HTTP handling
- **Service Layer**: Business logic and orchestration
- **Model Management**: Whisper model loading and GPU optimization
- **Text Processing**: Post-processing and cleaning
- **File Validation**: Upload validation and sanitization
- **System Diagnostics**: Health monitoring and dependency checking

## 📋 Requirements

- Python 3.8+
- PyTorch (with CUDA support for GPU acceleration)
- OpenAI Whisper
- FastAPI and dependencies
- FFmpeg (for audio processing)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LyricSync-Vibe-Coding-Case-Study
```

2. Install dependencies:
```bash
pip install -r docs/requirements.txt
```

3. Ensure FFmpeg is installed and available in PATH

## 🚀 Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

- **POST /transcribe**: Upload audio file for transcription
- **GET /api**: API information and endpoints
- **GET /health**: Health check and system status
- **GET /system-check**: Detailed system diagnostics
- **GET /privacy-check**: Privacy verification
- **GET /dependencies**: Dependency status check
- **GET /docs**: Interactive API documentation

### Transcription Example

```bash
curl -X POST "http://localhost:8000/transcribe" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@audio.mp3" \
     -F "quality=balanced" \
     -F "model_size=small"
```

## ⚙️ Configuration

Environment variables:
- `WHISPER_MODEL`: Default model size (default: "small")
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)

## 🔒 Privacy & Security

- **100% Local**: All processing happens on your machine
- **No External Calls**: No data sent to external services
- **Offline Capable**: Works completely offline after initial setup
- **Data Security**: Audio files are processed in memory and not stored

## 🧪 Testing

The modular architecture enables comprehensive testing:

```bash
# Run tests (when implemented)
python -m pytest tests/
```

## 📈 Performance

- **GPU Acceleration**: Automatic CUDA detection and optimization
- **Memory Management**: Efficient GPU memory handling
- **Model Caching**: Models loaded once and reused
- **Scalable**: Easy to extend with new models or processors

## 🛡️ Error Handling

- Comprehensive exception handling
- Graceful degradation (GPU → CPU fallback)
- Detailed logging and diagnostics
- User-friendly error messages

## 🔧 Development

### Project Structure
```
src/
├── api/           # FastAPI routes and HTTP handling
├── core/          # Configuration and interfaces
├── models/        # Whisper model management
├── services/      # Business logic and orchestration
├── monitoring/    # System diagnostics
└── validation/    # Input validation
```

### Adding New Features

The interface-based design makes it easy to extend:

- **New Models**: Implement `ModelManager` interface
- **Text Processors**: Implement `TextProcessor` protocol
- **Validators**: Implement `FileValidator` protocol

## 📚 API Documentation

Once the server is running, visit:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## ⚡ Quick Start

1. Install dependencies: `pip install -r docs/requirements.txt`
2. Run server: `python main.py`
3. Open browser: `http://localhost:8000/docs`
4. Test with curl or use the interactive API docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes.

---

**Note**: This is a local-first application prioritizing privacy and security. All transcription happens on your machine using the OpenAI Whisper model.