# Smart Village Management System (LIFF Edition)

A comprehensive village management system built with FastAPI backend and LINE LIFF integration for modern community management.

## 🏗️ Architecture

This system follows a microservices architecture with the following components:

- **Backend API**: FastAPI with PostgreSQL database
- **Admin Dashboard**: React TypeScript application  
- **LIFF PWA**: LINE Front-end Framework Progressive Web App
- **Authentication**: JWT + LINE LIFF integration

## 🚀 Features

### Core Features
- **User Management**: Multi-role user system (Super Admin, Village Admin, Accounting Admin, Resident)
- **Village Management**: Complete village information and property management
- **Property Management**: Unit tracking, ownership, and resident assignment
- **Authentication**: Secure JWT-based auth with LINE LIFF integration
- **Access Control**: Role-based permissions and security

### LINE Integration
- LINE LIFF for mobile-first experience
- LINE Login authentication
- LINE Notify for notifications
- Seamless mobile user experience

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+ (optional, for caching)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SafetyDady/smart-village-management-system.git
cd smart-village-management-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 3. Environment Configuration

Edit the `.env` file with your configuration:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_village

# Security
SECRET_KEY=your_super_secret_key_here

# LINE Platform
LINE_CHANNEL_ID=your_line_channel_id
LINE_CHANNEL_SECRET=your_line_channel_secret
LIFF_ID=your_liff_app_id
```

### 4. Database Setup

```bash
# Create database
createdb smart_village

# Run migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_users.py -v

# Run specific test
python -m pytest tests/test_users.py::TestUserEndpoints::test_login_success -v
```

### Test Database

Tests use SQLite in-memory database by default. No additional setup required.

## 📊 Database Schema

### Core Models

- **Users**: User accounts with roles and LINE integration
- **Villages**: Village information and settings
- **Properties**: Property units within villages

### Relationships

- Users can belong to multiple villages (many-to-many)
- Properties belong to one village (one-to-many)
- Users can own/rent multiple properties (many-to-many)

## 🔐 Authentication

### JWT Authentication

```bash
# Login
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### LINE LIFF Authentication

```bash
# LINE LIFF Login
POST /api/v1/auth/line-login
{
  "id_token": "line_id_token",
  "access_token": "line_access_token"
}
```

## 📚 API Documentation

### Core Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/line-login` - LINE LIFF login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

#### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

#### Villages
- `GET /api/v1/villages/` - List villages
- `POST /api/v1/villages/` - Create village
- `GET /api/v1/villages/{id}` - Get village by ID
- `PUT /api/v1/villages/{id}` - Update village

#### Properties
- `GET /api/v1/properties/` - List properties
- `POST /api/v1/properties/` - Create property
- `GET /api/v1/properties/{id}` - Get property by ID
- `PUT /api/v1/properties/{id}` - Update property

### Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

## 🔧 Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🚀 Deployment

### Production Environment

1. Set production environment variables
2. Use production database (PostgreSQL)
3. Configure reverse proxy (nginx)
4. Use process manager (systemd, supervisor)

### Docker Deployment

```bash
# Build image
docker build -t smart-village-backend .

# Run container
docker run -p 8000:8000 smart-village-backend
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/     # API route handlers
│   │       └── api.py         # API router
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── security.py        # Security utilities
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── alembic.ini               # Alembic configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Contact the development team
- Check the documentation at `/docs`

## 🔄 Changelog

### Version 1.0.0 (Current)
- Initial release with core functionality
- FastAPI backend with authentication
- Database models and migrations
- Basic API endpoints
- Test suite setup
- Documentation

---

**Smart Village Management System** - Building better communities through technology.

