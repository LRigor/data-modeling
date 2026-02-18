# Data Model Design Summary

## Problem Statement

Current CRM model issues:
1. Data duplication (Contact/Patient)
2. Medical condition inconsistency (option_set vs lookup)
3. Overloaded Contact entity (multiple user types)
4. Single CT journey limitation
5. Call history overwriting
6. Returning patient data loss

## Solution

**Person as Single Source of Truth**: All person data (name, email) stored once in Person table.

## Key Entities

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| **Person** | Single source of truth | person_id, first_name, last_name, email |
| **Patient Lead** | Unconverted leads | lead_id, person_id, medical_condition_id, source |
| **Patient** | Converted leads | patient_id, person_id (unique), medical_condition_id |
| **Call History** | All calls preserved | call_id, patient_id, booking_date, call_date, outcome |
| **Clinical Trial Journey** | Multiple CT journeys | ct_journey_id, patient_id, trial_id, status |
| **EAP Journey** | Multiple EAP enrollments | eap_journey_id, patient_id, eap_number, status |
| **Physician** | Healthcare providers | physician_id, person_id (unique), hospital_id |
| **Medical Condition** | Single lookup table | medical_condition_id, name, abbreviation |

## Requirements Mapping

| Requirement | Solution |
|------------|----------|
| Normalize Contact/Patient | Person table eliminates duplication |
| Multiple EAP/CT Journeys | Separate journey tables |
| Consolidate Medical Condition | Single lookup table |
| Separate Contact Types | Person Contact Type junction table |
| Preserve Call History | Separate Call History table |
| Handle Returning Patients | Email-based Person matching |

## Data Flow

**New Lead**:
1. Person fills form → Creates Person (or matches existing)
2. Creates Patient Lead → Links to Person + Medical Condition
3. Books call → Creates Call History record

**Conversion**:
1. Patient Lead → Patient (links to same Person)
2. Updates Person Contact Type (role change)

**Multiple Calls**:
- Each call creates new Call History record
- No overwriting, full history preserved

## Benefits

- **Consistency**: Single source of truth
- **Scalability**: Multiple journeys supported
- **History**: All interactions preserved
- **Maintainability**: Clear entity separation
- **Performance**: Proper indexing

## Next Steps

1. Review `ERD_DESIGN.md` for detailed specifications
2. Review `MIGRATION_GUIDE.md` for migration steps
3. Execute `schema.sql` to create database
