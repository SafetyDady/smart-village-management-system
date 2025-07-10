# Smart Village Management System

## 🏘️ ภาพรวมโปรเจกต์

Smart Village Management System เป็นระบบจัดการหมู่บ้านอัจฉริยะที่ออกแบบมาเพื่อลดภาระงานของผู้ดูแล เพิ่มความสะดวกสบายให้ผู้อยู่อาศัย และสร้างความโปร่งใสทางการเงิน โดยใช้ FastAPI เป็น Backend และรองรับการเชื่อมต่อกับ LINE Platform

## 🏗️ สถาปัตยกรรมระบบ

### Backend-First Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    SMART VILLAGE SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│  📊 Swagger UI       🔧 FastAPI Backend    📱 Future LIFF   │
│  (API Testing)       (Core System)         (Planned)        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              💾 PostgreSQL Database                 │   │
│  │         (Data Storage & Management)                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Current Implementation
| Component | Technology | Status | Purpose |
|-----------|------------|--------|---------|
| **🔧 Backend API** | FastAPI + Python 3.11 | ✅ Active | Core Business Logic & API |
| **💾 Database** | PostgreSQL + SQLAlchemy | ✅ Active | Data Storage |
| **📊 API Documentation** | Swagger UI | ✅ Active | API Testing & Documentation |
| **🔐 Authentication** | JWT + Bcrypt | ✅ Active | User Authentication |
| **📱 Frontend** | React/Next.js | 🔄 Planned | User Interface |

## 🚀 ฟีเจอร์ที่พร้อมใช้งาน

### 👥 ระบบจัดการผู้ใช้
- ✅ การสมัครสมาชิกและเข้าสู่ระบบ
- ✅ ระบบ Role-based Access Control (Super Admin, Village Admin, Accounting Admin, Resident)
- ✅ การจัดการข้อมูลส่วนตัว
- ✅ ระบบรีเซ็ตรหัสผ่าน
- ✅ การล็อคบัญชีเมื่อเข้าสู่ระบบผิดหลายครั้ง

### 🏘️ ระบบจัดการหมู่บ้าน
- ✅ การสร้างและจัดการข้อมูลหมู่บ้าน
- ✅ การตั้งค่าหมู่บ้าน (ค่าบำรุง, การแจ้งเตือน, ระบบประตู)
- ✅ การจัดการข้อมูลที่อยู่และการติดต่อ
- ✅ ระบบสีและการตั้งค่าการแสดงผล

### 🏠 ระบบจัดการทรัพย์สิน
- ✅ การสร้างและจัดการข้อมูลทรัพย์สิน/บ้าน
- ✅ การจัดการประเภททรัพย์สิน (บ้าน, คอนโด, ทาวน์เฮาส์)
- ✅ การติดตามสถานะการเข้าพัก
- ✅ การจัดการข้อมูลเจ้าของและผู้เช่า
- ✅ ระบบมิเตอร์และสาธารณูปโภค

### 🔐 ระบบความปลอดภัย
- ✅ JWT Token Authentication
- ✅ Password Hashing ด้วย Bcrypt
- ✅ Rate Limiting สำหรับการเข้าสู่ระบบ
- ✅ Session Management
- ✅ API Security Headers

## 📁 โครงสร้างโปรเจกต์

```
smart-village-management-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   └── v1/
│   │   │       ├── endpoints/ # API endpoints
│   │   │       │   ├── auth.py
│   │   │       │   ├── users.py
│   │   │       │   ├── villages.py
│   │   │       │   └── properties.py
│   │   │       └── api.py
│   │   ├── core/              # Core configurations
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── village.py
│   │   │   └── property.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── village.py
│   │   │   └── property.py
│   │   ├── services/          # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── village_service.py
│   │   │   ├── property_service.py
│   │   │   └── line_service.py
│   │   └── main.py           # FastAPI application
│   ├── alembic/               # Database migrations
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
├── README.md
└── .gitignore
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Authentication**: JWT + Bcrypt
- **Validation**: Pydantic v2
- **Documentation**: Swagger UI + ReDoc

### Development Tools
- **Environment**: Python Virtual Environment
- **Package Manager**: pip
- **Code Quality**: Type hints + Pydantic validation
- **API Testing**: Swagger UI (built-in)

## 🚀 การเริ่มต้นพัฒนา

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Backend Setup
```bash
# Clone repository
git clone https://github.com/SafetyDady/smart-village-management-system.git
cd smart-village-management-system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# แก้ไขค่าใน .env ให้เหมาะสม

# Setup database
# สร้าง database ใน PostgreSQL ก่อน
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

### การเข้าถึงระบบ
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Default Super Admin
```
Email: admin@example.com
Password: admin123
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - เข้าสู่ระบบ
- `POST /api/v1/auth/refresh` - รีเฟรช Token
- `POST /api/v1/auth/logout` - ออกจากระบบ

### Users Management
- `GET /api/v1/users/` - ดูรายการผู้ใช้
- `POST /api/v1/users/` - สร้างผู้ใช้ใหม่
- `GET /api/v1/users/{user_id}` - ดูข้อมูลผู้ใช้
- `PUT /api/v1/users/{user_id}` - แก้ไขข้อมูลผู้ใช้
- `DELETE /api/v1/users/{user_id}` - ลบผู้ใช้

### Villages Management
- `GET /api/v1/villages/` - ดูรายการหมู่บ้าน
- `POST /api/v1/villages/` - สร้างหมู่บ้านใหม่
- `GET /api/v1/villages/{village_id}` - ดูข้อมูลหมู่บ้าน
- `PUT /api/v1/villages/{village_id}` - แก้ไขข้อมูลหมู่บ้าน
- `DELETE /api/v1/villages/{village_id}` - ลบหมู่บ้าน

### Properties Management
- `GET /api/v1/properties/` - ดูรายการทรัพย์สิน
- `POST /api/v1/properties/` - สร้างทรัพย์สินใหม่
- `GET /api/v1/properties/{property_id}` - ดูข้อมูลทรัพย์สิน
- `PUT /api/v1/properties/{property_id}` - แก้ไขข้อมูลทรัพย์สิน
- `DELETE /api/v1/properties/{property_id}` - ลบทรัพย์สิน

## 📊 แผนการพัฒนา

### Phase 1: Foundation ✅ เสร็จแล้ว
- ✅ Backend API Foundation
- ✅ Database Schema & Models
- ✅ Authentication System
- ✅ User Management
- ✅ Village Management
- ✅ Property Management
- ✅ API Documentation

### Phase 2: Village Accounting 🔄 กำลังพัฒนา
- ⏳ Transaction Management
- ⏳ Payment Methods
- ⏳ Invoice Generation
- ⏳ Receipt Management
- ⏳ Financial Reporting

### Phase 3: Enhanced Access Control 📋 วางแผน
- 📋 Access Logs
- 📋 Visitor Management
- 📋 QR Code System
- 📋 License Plate Recognition

### Phase 4: LINE Integration 📋 วางแผน
- 📋 LINE LIFF Integration
- 📋 LINE Messaging API
- 📋 Notification System
- 📋 LINE Pay Integration

### Phase 5: Frontend Development 📋 วางแผน
- 📋 Admin Dashboard (React)
- 📋 Resident Portal (LIFF PWA)
- 📋 Landing Page (Next.js)

## 🔧 การกำหนดค่า Environment Variables

```bash
# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/smart_village

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME="Smart Village Admin"

# Environment
ENVIRONMENT=development
DEBUG=true

# LINE Integration (Future)
LINE_CHANNEL_ID=
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
LINE_LIFF_ID=
```

## 🧪 การทดสอบ

### Manual Testing
1. เปิด Swagger UI: http://localhost:8000/api/v1/docs
2. ทดสอบ Login ด้วย Super Admin account
3. Authorize ใน Swagger UI
4. ทดสอบ CRUD operations สำหรับ Users, Villages, Properties

### API Testing Examples
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"

# Create Village (ต้องใส่ Authorization header)
curl -X POST "http://localhost:8000/api/v1/villages/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart Village 1",
    "code": "SV001",
    "description": "A smart village for modern living",
    "address": "123 Main St",
    "city": "Bangkok",
    "state": "Bangkok",
    "postal_code": "10000"
  }'
```

## 🐛 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **Database Connection Error**
   - ตรวจสอบ PostgreSQL service ทำงานหรือไม่
   - ตรวจสอบ DATABASE_URL ใน .env

2. **Import Error**
   - ตรวจสอบ virtual environment ถูก activate หรือไม่
   - รัน `pip install -r requirements.txt` ใหม่

3. **Authentication Error**
   - ตรวจสอบ SECRET_KEY ใน .env
   - ตรวจสอบ Token expiration

## 📞 การติดต่อ

- **Project**: Smart Village Management System
- **Version**: 1.0.0 (Phase 1 Complete)
- **Repository**: https://github.com/SafetyDady/smart-village-management-system
- **License**: Private
- **Status**: Active Development

---

*Smart Village Management System - Making village management smarter, easier, and more transparent.*

