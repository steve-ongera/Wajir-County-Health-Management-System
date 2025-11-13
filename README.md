# Wajir County Health Management System

A comprehensive Django-based health management system designed for county-level public health operations in Kenya, with support for community health volunteers (CHVs), facility management, maternal & child health, surveillance, supply chain, and M&E reporting.

## 🎯 Overview

This system provides a complete solution for managing county health operations including:

- **Population Health Management**: Household registration, individual health records
- **Maternal & Child Health**: ANC/PNC visits, pregnancy tracking, immunizations
- **Community Health**: CHV management, household visits, outreach events
- **Referral System**: Inter-facility patient referrals with tracking
- **Disease Surveillance**: Disease reporting, outbreak management
- **Supply Chain**: Commodity tracking, stock management, procurement
- **Laboratory**: Test ordering and result management
- **M&E Reporting**: Program indicators, monthly reports, campaigns
- **HR & Training**: Staff profiles, training records, certifications

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Data Models](#data-models)
- [Security](#security)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Features

- **Multi-tenant Architecture**: Support for multiple counties, sub-counties, and wards
- **Role-Based Access Control**: 11 different user roles with granular permissions
- **Kenyan Healthcare Context**: National ID, NHIF integration, county health structure
- **Geographic Information**: Optional PostGIS support for mapping and catchment areas
- **Audit Trail**: Complete audit logging for all sensitive operations
- **Interoperability**: FHIR mapping support for integration with national systems

### Health Programs

- **Maternal Health**: Complete pregnancy cycle tracking (ANC, delivery, PNC)
- **Child Health**: Immunization tracking, growth monitoring
- **Disease Surveillance**: Real-time disease reporting and outbreak management
- **Community Outreach**: Campaign management, mass screening events
- **Chronic Disease Management**: Screening for TB, HIV, diabetes, hypertension

### Supply Chain

- **Inventory Management**: Track medicines, vaccines, and medical supplies
- **Stock Transactions**: IN/OUT/TRANSFER/ADJUSTMENT with full audit trail
- **Expiry Tracking**: Automated alerts for expiring commodities
- **Procurement Workflow**: Request → Approval → Purchase Order → Delivery
- **Supplier Management**: Supplier profiles and performance tracking

### Reporting & Analytics

- **Monthly Reports**: Facility and sub-county level aggregated metrics
- **Program Indicators**: Track KPIs with baseline and targets
- **Export Capabilities**: CSV, Excel, PDF, JSON, FHIR Bundle
- **Dashboard Statistics**: Real-time health metrics visualization

## 💻 System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **Django**: 4.2 LTS or higher
- **PostgreSQL**: 12 or higher (with PostGIS extension optional)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum for application and database
- **OS**: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+

### Recommended Stack

```
Python 3.11
Django 4.2 LTS
PostgreSQL 15 with PostGIS 3.3
Redis 7.0 (for caching and Celery)
Nginx 1.24 (web server)
Gunicorn 21.0 (WSGI server)
Celery 5.3 (async tasks)
```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/wajir-health-system.git
cd wajir-health-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies (Ubuntu/Debian)

```bash
# PostgreSQL and PostGIS
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis

# Python development headers
sudo apt-get install python3-dev libpq-dev

# GDAL for geographic support (optional)
sudo apt-get install gdal-bin libgdal-dev

# Redis (optional, for caching)
sudo apt-get install redis-server
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-django
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=wajir_health_db
DB_USER=wajir_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Gateway (Africa's Talking or similar)
SMS_API_KEY=your-sms-api-key
SMS_USERNAME=your-sms-username

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=wajir-health-files
AWS_S3_REGION_NAME=eu-west-1

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Django Settings

Update `settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # or django.db.backends.postgresql
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'health.User'

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Optional for PostGIS
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    
    # Your app
    'health',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

## 🗄️ Database Setup

### 1. Create PostgreSQL Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE wajir_health_db;
CREATE USER wajir_user WITH PASSWORD 'your-secure-password';
ALTER ROLE wajir_user SET client_encoding TO 'utf8';
ALTER ROLE wajir_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE wajir_user SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE wajir_health_db TO wajir_user;

# Enable PostGIS (optional)
\c wajir_health_db
CREATE EXTENSION postgis;

\q
```

### 2. Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Load Initial Data

```bash
# Load counties, sub-counties, and wards
python manage.py loaddata initial_data/counties.json

# Load roles and permissions
python manage.py loaddata initial_data/roles.json

# Load common commodities
python manage.py loaddata initial_data/commodities.json
```

## 🏃 Running the Application

### Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Access the application:
- Admin Interface: http://localhost:8000/admin
- API: http://localhost:8000/api/

### Production Server (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 wajir_health.wsgi:application
```

### Celery Worker (for async tasks)

```bash
# Start Celery worker
celery -A wajir_health worker -l info

# Start Celery beat (for scheduled tasks)
celery -A wajir_health beat -l info
```

## 📡 API Documentation

### Authentication

The API uses Token Authentication. Obtain a token:

```bash
POST /api/auth/token/
{
    "email": "user@example.com",
    "password": "password123"
}
```

Response:
```json
{
    "token": "your-auth-token-here"
}
```

Use the token in subsequent requests:
```
Authorization: Token your-auth-token-here
```

### Key Endpoints

#### Facilities
```
GET    /api/facilities/                 - List all facilities
POST   /api/facilities/                 - Create facility
GET    /api/facilities/{id}/            - Get facility details
PUT    /api/facilities/{id}/            - Update facility
DELETE /api/facilities/{id}/            - Delete facility
```

#### Persons/Patients
```
GET    /api/persons/                    - List persons
POST   /api/persons/                    - Register person
GET    /api/persons/{id}/               - Get person details
GET    /api/persons/{id}/pregnancies/  - Get pregnancy history
GET    /api/persons/{id}/immunizations/ - Get immunization history
```

#### Referrals
```
GET    /api/referrals/                  - List referrals
POST   /api/referrals/                  - Create referral
GET    /api/referrals/{id}/             - Get referral details
PUT    /api/referrals/{id}/status/      - Update referral status
POST   /api/referrals/{id}/follow-up/   - Add follow-up
```

#### Stock Management
```
GET    /api/stock/                      - List stock
GET    /api/stock/low-stock/            - Get low stock items
GET    /api/stock/expiring/             - Get expiring items
POST   /api/stock/transaction/          - Record transaction
```

#### Reports
```
GET    /api/reports/monthly/            - Get monthly reports
POST   /api/reports/monthly/            - Submit monthly report
GET    /api/reports/surveillance/       - Get surveillance reports
GET    /api/reports/dashboard/          - Get dashboard statistics
```

### Filtering and Search

Most list endpoints support filtering:

```
GET /api/persons/?gender=F&household__ward__subcounty__county={county_id}
GET /api/referrals/?status=PENDING&urgency=EMERGENCY
GET /api/stock/?facility={facility_id}&expiry_date__lt=2024-12-31
```

## 👥 User Roles

### 1. County Administrator
- Full system access
- Manage all facilities and users
- View county-wide reports

### 2. Public Health Officer
- Disease surveillance
- Outbreak management
- Health program oversight

### 3. M&E Officer
- Data quality monitoring
- Report generation
- Indicator tracking

### 4. Facility Manager
- Facility operations
- Staff management
- Resource allocation

### 5. Clinical Officer / Nurse
- Patient care
- Treatment records
- Referrals

### 6. Laboratory Technician
- Lab test processing
- Result entry
- Quality control

### 7. Pharmacist
- Stock management
- Dispensing
- Expiry monitoring

### 8. Data Clerk
- Data entry
- Record management
- Report compilation

### 9. Community Health Volunteer (CHV)
- Household visits
- Community screening
- Health education
- Referral linkage

### 10. Community Health Extension Worker (CHEW)
- CHV supervision
- Community programs
- Outreach coordination

## 📊 Data Models

### Core Entities

1. **Administrative**: County, SubCounty, Ward
2. **Users**: User, Role, Permission
3. **Health Facilities**: Facility, CommunityUnit
4. **Population**: Household, Person
5. **Health Services**: Pregnancy, ANCVisit, PNCVisit, Immunization
6. **Public Health**: HouseholdVisit, OutreachEvent, Screening
7. **Referrals**: Referral, ReferralFollowUp
8. **Surveillance**: SurveillanceReport, MortalityReport
9. **Supply Chain**: Commodity, Stock, StockTransaction, ProcurementRequest
10. **Laboratory**: LabTestOrder, LabResult
11. **HR**: StaffProfile, Training, TrainingAttendance
12. **System**: AuditLog, Notification, FHIRMapping

### Key Relationships

```
County → SubCounty → Ward → Facility
County → SubCounty → Ward → CommunityUnit → CHV
Ward → Household → Person
Person → Pregnancy → ANCVisit/PNCVisit
Person → Referral → Facility
Facility → Stock → Commodity
```

## 🔒 Security

### Data Protection

1. **Encryption**: Sensitive fields (National ID, NHIF) should be encrypted at rest
2. **Access Control**: Row-level security based on user's county/facility
3. **Audit Logging**: All CRUD operations on sensitive data are logged
4. **Authentication**: Token-based authentication with expiry
5. **HTTPS**: All production traffic must use HTTPS

### Security Best Practices

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### GDPR/Data Protection Compliance

- Personal data is minimized
- Consent tracking for data collection
- Right to access: Export personal data
- Right to erasure: Anonymize instead of delete (for audit trail)
- Data retention policies

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test health

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Data

```bash
# Load test data
python manage.py loaddata test_data/fixtures.json

# Create test users
python manage.py create_test_users
```

### Example Test

```python
from django.test import TestCase
from health.models import Person, Household

class PersonTestCase(TestCase):
    def setUp(self):
        self.household = Household.objects.create(
            household_number="TEST-001"
        )
    
    def test_person_age_calculation(self):
        person = Person.objects.create(
            first_name="Test",
            last_name="User",
            date_of_birth="2000-01-01",
            gender="M",
            household=self.household
        )
        self.assertGreater(person.get_age(), 20)
```

## 🚢 Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wajir_health.wsgi:application"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: wajir_health_db
      POSTGRES_USER: wajir_user
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 wajir_health.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery:
    build: .
    command: celery -A wajir_health worker -l info
    depends_on:
      - db
      - redis
    env_file:
      - .env

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

### Deploy Commands

```bash
# Build and start
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Configure proper database backups
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Configure proper logging
- [ ] Set up automated backups
- [ ] Configure email notifications
- [ ] Test disaster recovery plan

## 📚 Documentation

- [User Manual](docs/user-manual.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)
- [Developer Guide](docs/developer-guide.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Wajir County Health Department**
- **Development Team**

## 🙏 Acknowledgments

- Ministry of Health, Kenya
- Wajir County Government
- Community Health Volunteers
- All healthcare workers

## 📞 Support

For support, email support@wajirhealth.go.ke or join our Slack channel.

## 🗺️ Roadmap

### Version 2.0 (Q2 2024)
- [ ] Mobile app for CHVs
- [ ] WhatsApp integration for notifications
- [ ] Advanced analytics dashboard
- [ ] Integration with Kenya HMIS
- [ ] Offline mode support

### Version 3.0 (Q4 2024)
- [ ] AI-powered disease outbreak prediction
- [ ] Telemedicine integration
- [ ] Electronic Medical Records (EMR)
- [ ] Pharmacy dispensing module
- [ ] Revenue collection module

---

**Built with ❤️ for Wajir County**