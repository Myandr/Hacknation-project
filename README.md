# Hacknation Project

A modern full-stack application built during a hackathon, combining a powerful FastAPI backend with a cross-platform Flutter frontend.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Flutter](https://img.shields.io/badge/Flutter-Latest-blue.svg)
![Dart](https://img.shields.io/badge/Dart-Latest-blue.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Hacknation is a full-stack application that demonstrates modern web and mobile development practices. The project features:

- **RESTful API** built with FastAPI for high performance and automatic documentation
- **Cross-platform mobile app** developed with Flutter for iOS, Android, and Web
- **Type-safe architecture** with Python type hints and Dart strong typing
- **Automatic API documentation** with Swagger UI and ReDoc
- **Hot reload** capabilities for rapid development

## 🛠 Tech Stack

### Backend
- **Python 3.8+** - Modern Python with async/await support
- **FastAPI** - High-performance web framework for building APIs
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **Flutter** - Cross-platform UI framework
- **Dart** - Client-optimized programming language
- **C++** - Native components for performance-critical features
- **CMake** - Build system for native modules

### Development Tools
- **Virtual Environment** - Isolated Python dependencies
- **Hot Reload** - Fast development iteration
- **Swagger UI** - Interactive API documentation

## 📁 Project Structure

```
Hacknation-project/
├── backend2/                 # FastAPI backend
│   ├── main.py              # API entry point
│   ├── requirements.txt     # Python dependencies
│   └── .venv/               # Virtual environment
├── frontend/                # Flutter frontend
│   ├── lib/                 # Dart source code
│   ├── android/             # Android-specific config
│   ├── ios/                 # iOS-specific config
│   └── pubspec.yaml         # Flutter dependencies
├── Images/                  # Project images and assets
├── API_FOR_FLUTTER.md       # API documentation for frontend
├── PROJECT_STEPS_AGENTIC_COMMERCE.md  # Project roadmap
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Flutter SDK** - [Install Flutter](https://flutter.dev/docs/get-started/install)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Code Editor** - VS Code, Android Studio, or your preferred IDE

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Myandr/Hacknation-project.git
   cd Hacknation-project
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend2
   ```

3. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

4. **Activate virtual environment**
   - Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the API**
   - API: http://127.0.0.1:8000
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Check Flutter installation**
   ```bash
   flutter doctor
   ```

4. **Run the app**
   ```bash
   flutter run
   ```
   
   For web development:
   ```bash
   flutter run -d chrome
   ```

## 📚 API Documentation

The API is automatically documented using FastAPI's built-in documentation generators:

- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative documentation at `/redoc`
- **OpenAPI Schema**: Machine-readable specification at `/openapi.json`

For Flutter-specific API integration details, see [API_FOR_FLUTTER.md](API_FOR_FLUTTER.md).

### Key API Features

- ✅ **Type validation** with Pydantic models
- ✅ **Async/await** support for concurrent requests
- ✅ **CORS enabled** for frontend integration
- ✅ **Automatic schema** generation
- ✅ **Error handling** with proper HTTP status codes

## 💻 Development

### Backend Development

**Run with auto-reload:**
```bash
uvicorn main:app --reload
```

**Run on custom port:**
```bash
uvicorn main:app --reload --port 8080
```

**Run on custom host:**
```bash
uvicorn main:app --reload --host 0.0.0.0
```

### Frontend Development

**Hot reload:**
- Press `r` in terminal to hot reload
- Press `R` to hot restart
- Press `q` to quit

**Build for production:**
```bash
flutter build apk        # Android
flutter build ios        # iOS
flutter build web        # Web
```

**Run tests:**
```bash
flutter test
```

### Code Style

**Backend:**
- Follow PEP 8 style guide
- Use type hints for all functions
- Document functions with docstrings

**Frontend:**
- Follow Dart style guide
- Use `dartfmt` for formatting
- Run `flutter analyze` before committing

## 🚢 Deployment

### Backend Deployment Options

- **Docker**: Containerize the FastAPI application
- **Cloud Platforms**: AWS, Google Cloud, Azure
- **PaaS**: Heroku, Railway, Render
- **Server**: Gunicorn/Uvicorn with Nginx reverse proxy

### Frontend Deployment Options

- **iOS**: App Store via Xcode and TestFlight
- **Android**: Google Play Store
- **Web**: Netlify, Vercel, Firebase Hosting

### Environment Variables

Create a `.env` file for sensitive configuration:

```env
# Backend
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
API_KEY=your_api_key

# Frontend
API_BASE_URL=http://127.0.0.1:8000
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Keep pull requests focused and small

## 📝 License

This project is open source and available for educational and development purposes.

## 📧 Contact

**Developer**: Myandr

**Repository**: [https://github.com/Myandr/Hacknation-project](https://github.com/Myandr/Hacknation-project)

---

## 🎓 Learning Resources

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Advanced User Guide](https://fastapi.tiangolo.com/advanced/)

### Flutter
- [Official Documentation](https://flutter.dev/docs)
- [Flutter Cookbook](https://flutter.dev/docs/cookbook)
- [Dart Language Tour](https://dart.dev/guides/language/language-tour)

## 🙏 Acknowledgments

- Built during Hacknation hackathon
- Inspired by modern full-stack development practices
- Thanks to the FastAPI and Flutter communities

---

**Built with ❤️ using FastAPI and Flutter**
