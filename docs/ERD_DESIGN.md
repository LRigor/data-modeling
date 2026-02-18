# Entity Relationship Diagram

## Overview

This document specifies the redesigned data model entities, relationships, and constraints.

## Core Entities

### Person
**Purpose**: Single source of truth for person information.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| person_id | UUID | PK | Unique identifier |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NOT NULL | Last name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email (used for matching) |
| phone | VARCHAR(50) | NULL | Phone number |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |
| is_active | BOOLEAN | NOT NULL | Soft delete flag |

**Indexes**: person_id (PK), email (unique), (last_name, first_name)

---

### Medical Condition
**Purpose**: Single normalized lookup table.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| medical_condition_id | UUID | PK | Unique identifier |
| name | VARCHAR(200) | UNIQUE, NOT NULL | Condition name |
| abbreviation | VARCHAR(50) | NULL | Abbreviation (DMD, GBM, IPF) |
| description | TEXT | NULL | Description |
| is_active | BOOLEAN | NOT NULL | Active flag |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

**Pre-populated**: Duchenne Muscular Dystrophy (DMD), Glioblastoma (GBM), Idiopathic Pulmonary Fibrosis (IPF)

---

### Patient Lead
**Purpose**: Unconverted leads from forms/landing pages.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| lead_id | UUID | PK | Unique identifier |
| person_id | UUID | FK → Person | Reference to person |
| medical_condition_id | UUID | FK → Medical Condition | Reference to condition |
| source | VARCHAR(100) | NOT NULL | Source (landing_page, contact_form) |
| status | VARCHAR(50) | NOT NULL | Status (new, converted, lost) |
| converted_to_patient_id | UUID | FK → Patient | Patient if converted |
| converted_at | TIMESTAMP | NULL | Conversion timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

---

### Patient
**Purpose**: Converted leads.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| patient_id | UUID | PK | Unique identifier |
| person_id | UUID | FK → Person, UNIQUE | Reference to person (one-to-one) |
| medical_condition_id | UUID | FK → Medical Condition | Reference to condition |
| first_contact_date | DATE | NULL | First contact date |
| initial_consult_date | DATE | NULL | Initial consultation date |
| status | VARCHAR(50) | NOT NULL | Status (active, inactive) |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

**Business Rule**: One patient per person (person_id is unique)

---

### Call History
**Purpose**: Tracks all calls/interactions (prevents data loss).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| call_id | UUID | PK | Unique identifier |
| patient_id | UUID | FK → Patient | Reference to patient |
| pn_id | UUID | FK → Person | Patient Navigator |
| booking_date | TIMESTAMP | NULL | Booking date/time |
| call_date | TIMESTAMP | NULL | Call date/time |
| reminder_date | TIMESTAMP | NULL | Reminder date/time |
| no_show | BOOLEAN | NOT NULL | No show flag |
| call_duration_minutes | INTEGER | NULL | Duration in minutes |
| outcome | VARCHAR(100) | NULL | Call outcome |
| notes | TEXT | NULL | Call notes |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Business Rule**: Multiple calls per patient allowed

---

### Clinical Trial Journey
**Purpose**: Multiple CT journeys per patient.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| ct_journey_id | UUID | PK | Unique identifier |
| patient_id | UUID | FK → Patient | Reference to patient |
| physician_id | UUID | FK → Physician | Referring physician |
| trial_id | VARCHAR(100) | NOT NULL | Trial identifier |
| trial_name | VARCHAR(500) | NULL | Trial name |
| referral_date | DATE | NULL | Referral date |
| eligible | BOOLEAN | NULL | Eligibility status |
| ineligible_reason | TEXT | NULL | Reason if not eligible |
| outcome | VARCHAR(100) | NULL | Journey outcome |
| status | VARCHAR(50) | NOT NULL | Status (referred, enrolled, etc.) |
| enrollment_date | DATE | NULL | Enrollment date |
| completion_date | DATE | NULL | Completion date |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

---

### EAP Journey
**Purpose**: Multiple EAP enrollments per patient.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| eap_journey_id | UUID | PK | Unique identifier |
| patient_id | UUID | FK → Patient | Reference to patient |
| physician_id | UUID | FK → Physician | Referring physician |
| eap_number | VARCHAR(100) | NOT NULL | EAP dossier number |
| product | VARCHAR(200) | NULL | Product name |
| enrollment_date | DATE | NULL | Enrollment date |
| status | VARCHAR(50) | NOT NULL | Status (pending, active, etc.) |
| approval_date | DATE | NULL | Approval date |
| completion_date | DATE | NULL | Completion date |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

---

### Physician
**Purpose**: Healthcare providers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| physician_id | UUID | PK | Unique identifier |
| person_id | UUID | FK → Person, UNIQUE | Reference to person (one-to-one) |
| hospital_id | UUID | FK → Hospital | Hospital affiliation |
| job_title | VARCHAR(200) | NULL | Job title |
| specialization_id | UUID | FK → Specialization | Specialization |
| medical_license_number | VARCHAR(100) | NULL | License number |
| is_active | BOOLEAN | NOT NULL | Active flag |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

---

### Hospital
**Purpose**: Hospital lookup table.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| hospital_id | UUID | PK | Unique identifier |
| name | VARCHAR(200) | NOT NULL | Hospital name |
| city | VARCHAR(100) | NULL | City |
| country | VARCHAR(100) | NULL | Country |
| address | TEXT | NULL | Full address |
| is_active | BOOLEAN | NOT NULL | Active flag |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Update timestamp |

---

### Specialization
**Purpose**: Physician specialization lookup.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| specialization_id | UUID | PK | Unique identifier |
| name | VARCHAR(200) | UNIQUE, NOT NULL | Specialization name |
| description | TEXT | NULL | Description |
| is_active | BOOLEAN | NOT NULL | Active flag |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

---

### Person Contact Type
**Purpose**: Links Person to Contact Type with temporal tracking.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| person_contact_type_id | UUID | PK | Unique identifier |
| person_id | UUID | FK → Person | Reference to person |
| contact_type_id | UUID | FK → Contact Type | Reference to contact type |
| valid_from | TIMESTAMP | NOT NULL | Role start date |
| valid_to | TIMESTAMP | NULL | Role end date (NULL = active) |
| is_active | BOOLEAN | NOT NULL | Current status |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Business Rule**: Only one active role of each type per person

---

### Patient Physician Relationship
**Purpose**: Links patients to physicians (many-to-many).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| patient_physician_id | UUID | PK | Unique identifier |
| patient_id | UUID | FK → Patient | Reference to patient |
| physician_id | UUID | FK → Physician | Reference to physician |
| relationship_type | VARCHAR(100) | NOT NULL | Type (primary_care, referring, etc.) |
| is_primary | BOOLEAN | NOT NULL | Primary physician flag |
| start_date | DATE | NULL | Relationship start |
| end_date | DATE | NULL | Relationship end (NULL = current) |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Business Rule**: Only one primary physician per patient

---

## Relationships

### One-to-One
- Person ↔ Patient (one person = one patient)
- Person ↔ Physician (one person = one physician)

### One-to-Many
- Person → Patient Lead
- Person → Person Contact Type
- Medical Condition → Patient Lead
- Medical Condition → Patient
- Patient → Call History
- Patient → Clinical Trial Journey
- Patient → EAP Journey
- Patient → Patient Physician Relationship
- Hospital → Physician
- Specialization → Physician

### Many-to-Many
- Patient ↔ Physician (via Patient Physician Relationship)

## Key Design Features

1. **Normalization**: Person as single source eliminates duplication
2. **Temporal Tracking**: Role changes tracked over time
3. **Multiple Journeys**: Separate tables for CT and EAP
4. **Call History**: Every interaction preserved
5. **Returning Patients**: Email-based matching prevents duplicates
