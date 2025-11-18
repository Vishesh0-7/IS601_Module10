# FastAPI User Management API

A production-ready FastAPI application with user registration, password hashing, comprehensive testing, and CI/CD pipeline.

## 🚀 Features

- **User Registration API** with username and email uniqueness validation
- **Password Security** using bcrypt hashing
- **SQLAlchemy ORM** with PostgreSQL
- **Pydantic Schemas** for request/response validation
- **Comprehensive Testing** (unit + integration tests)
- **Docker Support** for containerization
- **CI/CD Pipeline** with GitHub Actions
- **Automatic Docker Hub Publishing**

## 📋 Technology Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **Passlib** - Password hashing (bcrypt)
- **Pytest** - Testing framework
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

## 📁 Project Structure

```
mod10/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection and session
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── security.py      # Password hashing utilities
│   ├── crud.py          # CRUD operations
│   └── routes.py        # API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_unit.py     # Unit tests
│   └── test_integration.py  # Integration tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # GitHub Actions workflow
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── README.md
└── reflection.md
```

## 🔧 Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mod10
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Start PostgreSQL** (if not using Docker)
   ```bash
   # Ensure PostgreSQL is running on localhost:5432
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000
   
   Interactive API docs: http://localhost:8000/docs

## 🐳 Docker

### Using Docker Compose (Recommended)

```bash
# Start both app and database
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Manually

```bash
# Build image
docker build -t fastapi-user-api .

# Run container (requires PostgreSQL running separately)
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host.docker.internal:5432/fastapi_db \
  fastapi-user-api
```

## 🧪 Testing

### Run All Tests

```bash
pytest -v
```

### Run Unit Tests Only

```bash
pytest tests/test_unit.py -v -m unit
```

### Run Integration Tests Only

```bash
# Ensure PostgreSQL is running
export DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_test

pytest tests/test_integration.py -v -m integration
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

## 📡 API Endpoints

### Root
- `GET /` - Welcome message
- `GET /health` - Health check

### Users
- `POST /users/` - Create a new user
  - Request body: `{"username": "string", "email": "user@example.com", "password": "string"}`
  - Response: `{"id": 1, "username": "string", "email": "user@example.com", "created_at": "2025-11-17T..."}`

## 🔐 Security

- Passwords are hashed using **bcrypt** (via Passlib)
- Password hashes are **never** exposed in API responses
- Minimum password length: 8 characters
- Username and email uniqueness enforced at database level

## 🚀 CI/CD Pipeline

The project includes a complete GitHub Actions workflow that:

1. **Runs on**: Push to `main`/`develop` branches, and pull requests
2. **Test Job**:
   - Spins up PostgreSQL service
   - Installs dependencies
   - Runs unit tests
   - Runs integration tests
3. **Build and Push Job** (only on `main` branch):
   - Builds Docker image
   - Pushes to Docker Hub with tags:
     - `latest`
     - `<commit-sha>`

### Required GitHub Secrets

Configure these in your repository settings:

- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token
- `DOCKERHUB_REPO` - Repository name (e.g., `fastapi-user-api`)

### Docker Hub

Published images: `https://hub.docker.com/r/<username>/<repo>`

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/fastapi_db` |

## 🛠️ Development

### Database Migrations

Currently using `Base.metadata.create_all()` for table creation. For production, consider using **Alembic** for migrations.

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

## 📄 License

This project is part of IS601 coursework.

## 👤 Author

Vishesh - IS601 Student

---

For more details on challenges and learning outcomes, see [reflection.md](reflection.md).
