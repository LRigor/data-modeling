# myTomorrows CRM - Data Model Redesign

## Assignment Submission

This repository contains the complete solution for the myTomorrows take-home assignment, addressing both Part 1 (Data Modeling) and Part 2 (FastAPI Implementation).

**Repository Access**: Please grant access to the following GitHub users:
- Mulugruntz
- MyT-Marshall
- Jonas-Svensson-MyTomorrows
- martin-myt
- euan-holl-myt

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
- `GET /` - List conditions
- `GET /{id}` - Get condition

### Features

- **Returning Patient Handling**: Automatic email-based matching prevents duplicates
- **Multiple Calls**: Each call stored as separate record (no data loss)
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Logging**: Structured logging throughout application
- **Type Safety**: Complete type hints and Pydantic validation
- **Container-Ready**: Docker and docker-compose configuration
- **Production-Ready**: Database connection pooling, transaction management, health checks

### Implementation Choices

1. **Database**: PostgreSQL chosen for ACID compliance and JSON support
2. **ORM**: SQLAlchemy for type-safe database operations
3. **Validation**: Pydantic for request/response validation
4. **Error Handling**: Custom exception classes for better error messages
5. **Logging**: Structured logging for production monitoring
6. **API Design**: RESTful endpoints with proper HTTP methods and status codes
7. **Pagination**: Implemented for all list endpoints to handle large datasets
8. **Filtering**: Support for status and medical condition filters

### Technology Stack

- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Pydantic (validation)

## Documentation

All documentation is in the `docs/` directory:

- `docs/ERD_DESIGN.md` - Entity specifications
- `docs/DESIGN_SUMMARY.md` - Quick reference
- `docs/MIGRATION_GUIDE.md` - Migration steps
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/QUICKSTART.md` - Setup instructions

## Project Structure

```
data-modeling/
├── app/              # FastAPI application
├── docs/             # Documentation
├── tests/            # Test files
├── schema.sql        # Database schema
├── docker-compose.yml
└── requirements.txt
```

## Assignment Answers

### Part 1: Data Modeling

**Question 1.1: Redesign Data Model**
- Answer: See `docs/ERD_DESIGN.md` for complete entity specifications
- Summary: Person table as single source of truth eliminates duplication. Separate journey tables support multiple EAP/CT journeys. Call History table preserves all interactions.

**Question 1.2: Migration Strategy**
- Answer: See `docs/MIGRATION_GUIDE.md` for step-by-step migration plan
- Summary: 10-phase migration approach with data validation, rollback procedures, and timeline estimates.

### Part 2: FastAPI Implementation

**Implementation**: Complete CRUD API for Patient, Call History, and Medical Conditions
- **Assumptions Documented**: See "Solution" and "Features" sections below
- **Production Quality**: Type hints, error handling, logging, validation
- **Container-Ready**: Docker and docker-compose included
- **Cloud Deployment**: See `docs/DEPLOYMENT.md` for AWS, GCP, Azure
- **Infrastructure-as-Code**: Terraform and Kubernetes examples provided

## Getting Started

1. **Setup**: See `docs/QUICKSTART.md`
2. **Data Model**: See `docs/DESIGN_SUMMARY.md`
3. **Migration**: See `docs/MIGRATION_GUIDE.md`
4. **Deployment**: See `docs/DEPLOYMENT.md`
5. **Requirements Review**: See `ASSIGNMENT_REVIEW.md` for compliance checklist
