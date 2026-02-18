# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- OR Python 3.11+ and PostgreSQL 15+ (for local development)

## Option 1: Docker Compose (Recommended)

### Step 1: Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- FastAPI application (port 8000)

### Step 2: Verify

```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### Step 3: Initialize Database (Optional)

```bash
# Seed medical conditions
docker-compose exec api python init_db.py
```

### Step 4: Test API

```bash
# Get medical conditions
curl http://localhost:8000/api/v1/medical-conditions

# Create a patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "person": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "medical_condition_id": "<uuid-from-medical-conditions>",
    "status": "active"
  }'
```

## Option 2: Local Development

### Step 1: Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Set Up Database

```bash
# Create database
createdb mytomorrows_db

# Run schema
psql -d mytomorrows_db -f schema.sql
```

### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env and set POSTGRES_* variables if needed
```

### Step 4: Initialize Database

```bash
python init_db.py
```

### Step 5: Run Application

```bash
uvicorn app.main:app --reload
```

### Step 6: Access API

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Endpoints

### Patients
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients` - List patients (paginated)
- `GET /api/v1/patients/{id}` - Get patient
- `PUT /api/v1/patients/{id}` - Update patient
- `DELETE /api/v1/patients/{id}` - Delete patient
- `GET /api/v1/patients/{id}/calls` - Get patient calls

### Call History
- `POST /api/v1/call-history` - Create call record
- `GET /api/v1/call-history/{id}` - Get call
- `PUT /api/v1/call-history/{id}` - Update call
- `DELETE /api/v1/call-history/{id}` - Delete call

### Medical Conditions
- `POST /api/v1/medical-conditions` - Create condition
- `GET /api/v1/medical-conditions` - List conditions
- `GET /api/v1/medical-conditions/{id}` - Get condition

## Example Usage

See `example_usage.py` for complete examples:

```bash
python example_usage.py
```

## Troubleshooting

### Database Connection Issues
- Check `POSTGRES_*` variables in `.env`
- Verify PostgreSQL is running
- Check database credentials

### Port Already in Use
- Change port in `docker-compose.yml`
- Or use `--port` flag for uvicorn

### Docker Issues
- Check logs: `docker-compose logs`
- Restart services: `docker-compose restart`

## Next Steps

1. Review API documentation at `/docs`
2. Read `README.md` for project overview
3. Check `DEPLOYMENT.md` for production deployment
4. Explore `ERD_DESIGN.md` for data model details
