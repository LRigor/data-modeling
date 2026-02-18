# Migration Guide

## Overview

Step-by-step guide for migrating from the current CRM model to the redesigned normalized model.

## Pre-Migration Checklist

- [ ] Backup all existing data
- [ ] Set up staging environment
- [ ] Review data relationships
- [ ] Identify data quality issues
- [ ] Create rollback plan
- [ ] Schedule maintenance window

## Migration Phases

### Phase 1: Preparation

**Create mapping tables**:
```sql
CREATE TABLE migration_contact_to_person (
    old_contact_id UUID,
    new_person_id UUID,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE migration_patient_to_person (
    old_patient_id UUID,
    new_person_id UUID,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE migration_medical_condition (
    old_option_set_value VARCHAR(200),
    old_lookup_id UUID,
    new_medical_condition_id UUID,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Phase 2: Create New Schema

Execute `schema.sql` to create all new tables, indexes, and constraints.

### Phase 3: Migrate Medical Conditions

**Consolidate conditions**:
```sql
-- Extract from Contact (option_set)
INSERT INTO medical_condition (name, abbreviation)
SELECT DISTINCT medical_condition, 
    CASE 
        WHEN medical_condition = 'Duchenne Muscular Dystrophy' THEN 'DMD'
        WHEN medical_condition = 'Glioblastoma' THEN 'GBM'
        WHEN medical_condition = 'Idiopathic Pulmonary Fibrosis' THEN 'IPF'
    END
FROM Contact
WHERE medical_condition IS NOT NULL
ON CONFLICT (name) DO NOTHING;

-- Extract from Patient (lookup)
INSERT INTO medical_condition (name, abbreviation)
SELECT DISTINCT mc.name, mc.abbreviation
FROM Patient p
JOIN "Medical Condition" mc ON p.medical_condition = mc."medical conditon id"
WHERE mc.name NOT IN (SELECT name FROM medical_condition)
ON CONFLICT (name) DO NOTHING;
```

### Phase 4: Migrate Persons

**Extract unique persons**:
```sql
-- From Contact
INSERT INTO person (person_id, first_name, last_name, email, created_at)
SELECT DISTINCT ON (email)
    uuid_generate_v4(),
    firstname,
    lastname,
    email,
    booking_date
FROM Contact
WHERE email IS NOT NULL
ORDER BY email, booking_date ASC NULLS LAST;

-- From Patient (if not exists)
INSERT INTO person (person_id, first_name, last_name, email, created_at)
SELECT DISTINCT ON (email)
    uuid_generate_v4(),
    firstname,
    lastname,
    email,
    first_contact_date
FROM Patient
WHERE email IS NOT NULL
    AND email NOT IN (SELECT email FROM person)
ON CONFLICT (email) DO NOTHING;
```

### Phase 5: Migrate Patient Leads

```sql
INSERT INTO patient_lead (person_id, medical_condition_id, source, status, created_at)
SELECT 
    mcp.new_person_id,
    mmc.new_medical_condition_id,
    'landing_page',
    CASE WHEN p.patientid IS NOT NULL THEN 'converted' ELSE 'new' END,
    c.booking_date
FROM Contact c
JOIN migration_contact_to_person mcp ON c.contactid = mcp.old_contact_id
JOIN migration_medical_condition mmc ON c.medical_condition = mmc.old_option_set_value
LEFT JOIN Patient p ON c.contactid = p.contact_record
WHERE c.contact_type = 'patient - lead';
```

### Phase 6: Migrate Patients

```sql
INSERT INTO patient (patient_id, person_id, medical_condition_id, 
                     first_contact_date, initial_consult_date, status, created_at)
SELECT 
    p.patientid,
    mpp.new_person_id,
    mmc.new_medical_condition_id,
    p.first_contact_date,
    p.initial_consult_date,
    'active',
    p.first_contact_date
FROM Patient p
JOIN migration_patient_to_person mpp ON p.patientid = mpp.old_patient_id
JOIN migration_medical_condition mmc ON p.medical_condition = mmc.old_lookup_id;
```

### Phase 7: Migrate Call History

```sql
INSERT INTO call_history (patient_id, booking_date, reminder_date, no_show, created_at)
SELECT 
    p.patient_id,
    c.booking_date,
    c.reminder_date,
    COALESCE(c.no_show, FALSE),
    c.booking_date
FROM Contact c
JOIN migration_contact_to_person mcp ON c.contactid = mcp.old_contact_id
JOIN Patient old_p ON c.contactid = old_p.contact_record
JOIN migration_patient_to_person mpp ON old_p.patientid = mpp.old_patient_id
JOIN patient p ON mpp.new_person_id = p.person_id
WHERE c.booking_date IS NOT NULL;
```

### Phase 8: Migrate Physicians

```sql
INSERT INTO physician (person_id, hospital_id, job_title, medical_license_number, created_at)
SELECT 
    mcp.new_person_id,
    c.hospital,
    c.job_title,
    c.medical_license_number,
    c.booking_date
FROM Contact c
JOIN migration_contact_to_person mcp ON c.contactid = mcp.old_contact_id
WHERE c.contact_type = 'physician';
```

### Phase 9: Migrate Journeys

**EAP Journeys**:
```sql
INSERT INTO eap_journey (patient_id, physician_id, eap_number, product, enrollment_date, status)
SELECT 
    p.patient_id,
    ph.physician_id,
    ed.eap_number,
    ed.product,
    ed.eap_enrollment_date,
    CASE WHEN ed.eap_enrollment_date IS NOT NULL THEN 'active' ELSE 'pending' END
FROM "EAP Dossier" ed
JOIN Patient old_p ON ed.patient = old_p.patientid
JOIN migration_patient_to_person mpp ON old_p.patientid = mpp.old_patient_id
JOIN patient p ON mpp.new_person_id = p.person_id
LEFT JOIN patient_physician_relationship ppr ON p.patient_id = ppr.patient_id AND ppr.is_primary = TRUE
LEFT JOIN physician ph ON ppr.physician_id = ph.physician_id;
```

**CT Journeys**:
```sql
INSERT INTO clinical_trial_journey (patient_id, physician_id, trial_id, referral_date, 
                                     eligible, ineligible_reason, outcome, status)
SELECT 
    p.patient_id,
    ph.physician_id,
    old_p.trial_id,
    old_p.ct_referral_date,
    old_p.eligible,
    old_p.ineligible_reason,
    old_p.ct_outcome,
    CASE WHEN old_p.ct_referral_date IS NOT NULL THEN 'referred' ELSE 'pending' END
FROM Patient old_p
JOIN migration_patient_to_person mpp ON old_p.patientid = mpp.old_patient_id
JOIN patient p ON mpp.new_person_id = p.person_id
LEFT JOIN patient_physician_relationship ppr ON p.patient_id = ppr.patient_id AND ppr.is_primary = TRUE
LEFT JOIN physician ph ON ppr.physician_id = ph.physician_id
WHERE old_p.trial_id IS NOT NULL OR old_p.ct_referral_date IS NOT NULL;
```

### Phase 10: Data Validation

**Record count verification**:
```sql
-- Compare counts
SELECT 'Contact' as old_table, COUNT(*) as count FROM Contact
UNION ALL
SELECT 'Person' as new_table, COUNT(*) as count FROM person;

SELECT 'Patient (old)' as old_table, COUNT(*) as count FROM Patient
UNION ALL
SELECT 'Patient (new)' as new_table, COUNT(*) as count FROM patient;
```

**Integrity checks**:
```sql
-- Check for orphaned records
SELECT COUNT(*) as orphaned_patients
FROM patient p
LEFT JOIN person per ON p.person_id = per.person_id
WHERE per.person_id IS NULL;

-- Verify foreign keys
SELECT COUNT(*) as orphaned_leads
FROM patient_lead pl
LEFT JOIN person per ON pl.person_id = per.person_id
WHERE per.person_id IS NULL;
```

## Application Updates

1. Update data access layer to use new schema
2. Modify queries and entity mappings
3. Update API endpoints
4. Test all functionality

## Cutover

1. Stop application services
2. Run final backup
3. Execute migration scripts
4. Validate data integrity
5. Update application configuration
6. Start application services
7. Monitor for errors

## Rollback Plan

If migration fails:

1. Stop application
2. Restore old database from backup
3. Revert application configuration
4. Start application
5. Investigate and fix issues
6. Reschedule migration

## Timeline Estimate

- **Phases 1-2**: 2-3 days (Analysis and Schema Setup)
- **Phases 3-9**: 5-7 days (Data Migration)
- **Phase 10**: 1-2 days (Validation)
- **Application Updates**: 3-5 days
- **Cutover**: 1 day

**Total**: Approximately 2-3 weeks
