# myTomorrows CRM - Data Model Redesign

## Overview

Redesigned data model for the myTomorrows CRM system addressing normalization, data integrity, and scalability issues.

## Problem Statement

The current model has these issues:
- Data duplication between Contact and Patient tables
- Medical condition stored as both option_set and lookup (inconsistent)
- Single Contact entity handles multiple user types (confusing)
- Only one CT journey per patient (limited)
- Call history can be overwritten (data loss)
- Returning patients may lose data

## Solution

**Core Principle**: Person table as single source of truth for all person data.

### Key Changes

1. **Person Table**: Centralizes name, email, phone - eliminates duplication
2. **Medical Condition**: Single lookup table replaces dual storage
3. **Separate Entities**: Patient Lead, Patient, Physician are distinct
4. **Multiple Journeys**: Separate tables for CT and EAP journeys
5. **Call History**: Separate table preserves all calls
6. **Returning Patients**: Email-based matching prevents duplicates

### Design Assumptions

1. **One Patient Per Person**: Database constraint ensures one patient record per person (person_id is unique in Patient table)
2. **Email-Based Matching**: Returning patients are identified by email address (unique constraint on Person.email)
3. **Multiple Calls Preserved**: Each call creates a new Call History record (no overwriting)
4. **Journey Independence**: Each CT/EAP journey is tracked independently with its own status and timeline
5. **Soft Deletes**: Person records use is_active flag for soft deletes (preserves historical data)
6. **Temporal Role Tracking**: Person Contact Type table tracks role changes over time with valid_from/valid_to timestamps

## Data Model

### Core Entities

- **Person**: Name, email, phone (single source of truth)
- **Patient Lead**: Unconverted leads linked to Person
- **Patient**: Converted leads linked to Person (one-to-one)
- **Call History**: All calls preserved (one-to-many with Patient)
- **Clinical Trial Journey**: Multiple CT journeys per patient
- **EAP Journey**: Multiple EAP enrollments per patient
- **Physician**: Healthcare providers linked to Person
- **Medical Condition**: Single lookup table

See `docs/ERD_DESIGN.md` for complete specifications.

## FastAPI Implementation

Production-ready API with CRUD operations for Patient, Call History, and Medical Conditions.

### Quick Start

```bash
# Using Docker Compose
docker-compose up -d

# Access API
http://localhost:8000/docs
```

### API Endpoints

**Patients** (`/api/v1/patients`)
- `POST /` - Create patient
- `GET /` - List patients (paginated, filtered)
- `GET /{id}` - Get patient
- `PUT /{id}` - Update patient
- `DELETE /{id}` - Delete patient
- `GET /{id}/calls` - Get call history

**Call History** (`/api/v1/call-history`)
- `POST /` - Create call record
- `GET /{id}` - Get call
- `PUT /{id}` - Update call
- `DELETE /{id}` - Delete call

**Medical Conditions** (`/api/v1/medical-conditions`)
- `POST /` - Create condition
- `GET /` - List conditions (with optional `is_active` filter)
- `GET /{id}` - Get condition by ID
- `PUT /{id}` - Update condition
- `DELETE /{id}` - Soft delete condition (sets `is_active=False`)

### Features

- **Returning Patient Handling**: Automatic email-based matching prevents duplicates
- **Multiple Calls**: Each call stored as separate record (no data loss)
- **Person ↔ CallHistory Relationships**: Proper SQLAlchemy relationships between Person and CallHistory via `pn_id` (patient navigator)
- **Soft Deletes**: Medical conditions support soft deletion via `is_active` flag
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Logging**: Structured logging throughout application
- **Type Safety**: Complete type hints and Pydantic validation
- **Container-Ready**: Docker and docker-compose configuration
- **Production-Ready**: Database connection pooling, transaction management, health checks
- **Testing**: Comprehensive test suite with pytest

### Technology Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Modern ORM with type safety
- **PostgreSQL 15** - Production-grade relational database
- **Pydantic v2** - Data validation and settings management
- **pytest** - Testing framework

## Documentation

All documentation is in the `docs/` directory:

- `docs/ERD_DESIGN.md` - Entity specifications
- `docs/MIGRATION_GUIDE.md` - Migration steps
- `docs/QUICKSTART.md` - Setup instructions

## Project Structure

```
data-modeling/
├── app/              # FastAPI application
│   ├── routes/       # API route handlers
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Pydantic schemas
│   ├── crud.py       # Database operations
│   └── main.py       # FastAPI app
├── docs/             # Documentation
├── tests/            # Test files
├── schema.sql        # Database schema
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Running Tests

```bash
# Run all tests (requires Docker Compose)
docker compose exec api pytest

# Run with verbose output
docker compose exec api pytest -v

# Run specific test file
docker compose exec api pytest tests/test_patients.py
```

See `docs/QUICKSTART.md` for detailed setup and testing instructions.

## Getting Started

1. **Setup**: See `docs/QUICKSTART.md`
2. **Data Model**: See `docs/ERD_DESIGN.md`
3. **Migration**: See `docs/MIGRATION_GUIDE.md`
