# MyBlog

A modern blog system based on a microservices architecture, featuring a frontend-backend separation design, support for multiple theme switching, and flexible permission management.

## ✨ Core Features

- **Microservices Architecture**: Service registration and discovery powered by LinkGateway
- **Multi-Engine Support**: Built-in FileEngine and PermDog permission engine
- **Theme System**: Supports three themes: China Red, Danqing Blue, and Fenxia Purple
- **Permission Management**: Fine-grained access control based on permission_level
- **Plugin Mechanism**: Extensible via plugins for performance monitoring, traffic monitoring, etc.
- **Modern Frontend**: Built with Vue 3 + Vite, supporting animations and responsive design

## 🏗️ System Architecture

```
myblog/
├── my_blog_backend/          # Backend services
│   ├── LinkGateway/          # Core gateway module
│   │   ├── gateway.py        # Gateway main entry
│   │   ├── registry.py       # Service registration and discovery
│   │   ├── api_mapper.py     # API routing mapping
│   │   ├── auth.py           # Authentication and authorization
│   │   ├── db_link.py        # Database connection management
│   │   └── plugin.py         # Plugin system
│   ├── engines/              # Business engines
│   │   ├── FileEngine/       # File processing engine
│   │   └── PermDog/          # Permission management engine
│   ├── services/             # Business services
│   │   ├── post-service/     # Post service
│   │   ├── interaction-service/ # Interaction service (likes/comments)
│   │   └── user-server/      # User service
│   └── plugins/              # Plugin implementations
├── my_blog_frontend/         # Frontend application
│   └── src/
│       ├── modules/          # Business modules
│       ├── components/       # Common components
│       └── styles/           # Style files
└── docker/                   # Docker configuration
```

## 🚀 Quick Start

### Environment Requirements

- Python 3.13+
- Node.js 20+
- SQLite (default) or other databases

### Start Backend

```bash
cd my_blog_backend
pip install -e .
python main.py
```

The service will be available at `http://localhost:8000`

### Start Frontend

```bash
cd my_blog_frontend
npm install
npm run dev
```

The service will be available at `http://localhost:5173`

### Deploy with Docker

```bash
docker-compose up -d
```

## 📖 Documentation Navigation

- [Project Overview](./Docs/README.md#project-overview)
- [Architecture Design](./Docs/README.md#architecture-design)
- [Backend Development Guide](./Docs/README.md#backend-development)
- [Frontend Development Guide](./Docs/README.md#frontend-development)
- [API Documentation](./Docs/README.md#api-documentation)
- [Contribution Guide](./Docs/CONTRIBUTING.md)

## 🔧 Development Guide

### Project Structure Guidelines

```
Backend Structure:
- engines/       # Engine modules; each must include a file_engine.json configuration
- services/      # Business services; each must include a service.json configuration
- plugins/       # Plugin implementations; must inherit the Plugin base class

Frontend Structure:
- modules/       # Feature modules containing views, services, and state management
- components/    # Common components
- utils/         # Utility functions
```

### Core Module Descriptions

**LinkGateway**: The system's core gateway, responsible for service registration/discovery, API routing mapping, and authentication/authorization.

**FileEngine**: Article file processing engine supporting CRUD operations and comment management.

**PermDog**: Permission management engine managing permission_level (P0–P3) and operational permissions.

### Adding a New Service

1. Create a service folder under `services/`
2. Add a `service.json` configuration file
3. Implement the service class inheriting from the base interface
4. Register the service in the gateway

### Adding a New Engine

1. Create an engine folder under `engines/`
2. Add an `engine.json` configuration file
3. Inherit from `BaseEngine` and implement core methods
4. Register the engine with the service registry

## 🎨 Theme System

The system includes three built-in themes, switchable via CSS class names:

| Theme | Class Name | Description |
|-------|------------|-------------|
| China Red | `theme-china-red` | Traditional red palette |
| Danqing Blue | `theme-danqing-blue` | Fresh blue palette |
| Fenxia Purple | `theme-fenxia-purple` | Soft purple palette |

## 🔐 Permission Levels

| Level | Description | Access Scope |
|-------|-------------|--------------|
| P0 | Public | All users |
| P1 | Internal | Registered users |
| P2 | Private | Specified users |
| P3 | Confidential | Author only |

## 🧪 Testing

```bash
# Backend tests
cd my_blog_backend
pytest tests/

# Frontend tests
cd my_blog_frontend
npm run test
```

## 📦 Technology Stack

**Backend**:
- FastAPI / Uvicorn
- Pydantic
- SQLAlchemy
- Alembic

**Frontend**:
- Vue 3
- Vite
- Pinia
- Vue Router

**Infrastructure**:
- SQLite / PostgreSQL
- Docker
- GitHub Actions

## 🤝 Contribution Guide

Contributions are welcome! Please read the [Contribution Guide](./Docs/CONTRIBUTING.md) for details on:

- Forking the project
- Code style requirements
- Pull Request guidelines
- Code review checklist

## 📄 License

This project is licensed under the MIT License.

## 📞 Get Help

- Review the [Documentation](./Docs/README.md)
- Check the [FAQ](./Docs/README.md#faq)
- Submit questions via Issues

---

MyBlog - Make sharing simpler ✨