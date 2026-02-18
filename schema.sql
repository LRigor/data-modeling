-- myTomorrows CRM Redesigned Database Schema
-- This schema addresses normalization, data integrity, and scalability concerns

-- Enable UUID extension (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- LOOKUP TABLES
-- ============================================================================

-- Contact Type Lookup
CREATE TABLE contact_type (
    contact_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate contact types
INSERT INTO contact_type (type_name, description) VALUES
    ('patient-lead', 'A patient lead who has not yet been converted'),
    ('physician', 'A healthcare provider/physician'),
    ('pharmacist', 'A pharmacist');

-- Medical Condition Lookup
CREATE TABLE medical_condition (
    medical_condition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    abbreviation VARCHAR(50),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate medical conditions
INSERT INTO medical_condition (name, abbreviation) VALUES
    ('Duchenne Muscular Dystrophy', 'DMD'),
    ('Glioblastoma', 'GBM'),
    ('Idiopathic Pulmonary Fibrosis', 'IPF');

-- Specialization Lookup
CREATE TABLE specialization (
    specialization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Hospital Lookup
CREATE TABLE hospital (
    hospital_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CORE ENTITIES
-- ============================================================================

-- Person (Base Entity - Single Source of Truth)
CREATE TABLE person (
    person_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Person Contact Type (Junction Table with Temporal Tracking)
CREATE TABLE person_contact_type (
    person_contact_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
    contact_type_id UUID NOT NULL REFERENCES contact_type(contact_type_id),
    valid_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Patient Lead
CREATE TABLE patient_lead (
    lead_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
    medical_condition_id UUID NOT NULL REFERENCES medical_condition(medical_condition_id),
    source VARCHAR(100) NOT NULL,
    landing_page_url VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'new',
    converted_to_patient_id UUID,
    converted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Patient
CREATE TABLE patient (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID UNIQUE NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
    medical_condition_id UUID NOT NULL REFERENCES medical_condition(medical_condition_id),
    first_contact_date DATE,
    initial_consult_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint for patient_lead after patient table is created
ALTER TABLE patient_lead 
    ADD CONSTRAINT fk_converted_patient 
    FOREIGN KEY (converted_to_patient_id) REFERENCES patient(patient_id);

-- Call History
CREATE TABLE call_history (
    call_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    pn_id UUID REFERENCES person(person_id),
    booking_date TIMESTAMP,
    call_date TIMESTAMP,
    reminder_date TIMESTAMP,
    no_show BOOLEAN NOT NULL DEFAULT FALSE,
    call_duration_minutes INTEGER,
    outcome VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Physician
CREATE TABLE physician (
    physician_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID UNIQUE NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
    hospital_id UUID REFERENCES hospital(hospital_id),
    job_title VARCHAR(200),
    specialization_id UUID REFERENCES specialization(specialization_id),
    medical_license_number VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Patient Physician Relationship
CREATE TABLE patient_physician_relationship (
    patient_physician_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    physician_id UUID NOT NULL REFERENCES physician(physician_id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Trial Journey
CREATE TABLE clinical_trial_journey (
    ct_journey_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    physician_id UUID REFERENCES physician(physician_id),
    trial_id VARCHAR(100) NOT NULL,
    trial_name VARCHAR(500),
    referral_date DATE,
    eligible BOOLEAN,
    eligibility_assessment_date DATE,
    ineligible_reason TEXT,
    outcome VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'referred',
    enrollment_date DATE,
    completion_date DATE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- EAP Journey
CREATE TABLE eap_journey (
    eap_journey_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    physician_id UUID REFERENCES physician(physician_id),
    eap_number VARCHAR(100) NOT NULL,
    product VARCHAR(200),
    enrollment_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    approval_date DATE,
    completion_date DATE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Person indexes
CREATE INDEX idx_person_email ON person(email);
CREATE INDEX idx_person_name ON person(last_name, first_name);
CREATE INDEX idx_person_active ON person(is_active);

-- Person Contact Type indexes
CREATE INDEX idx_person_contact_type_person ON person_contact_type(person_id);
CREATE INDEX idx_person_contact_type_active ON person_contact_type(is_active, valid_from, valid_to);
-- Unique index for active contact types (partial index)
CREATE UNIQUE INDEX idx_unique_active_contact_type ON person_contact_type(person_id, contact_type_id) 
    WHERE is_active = TRUE;

-- Patient Lead indexes
CREATE INDEX idx_patient_lead_person ON patient_lead(person_id);
CREATE INDEX idx_patient_lead_condition ON patient_lead(medical_condition_id);
CREATE INDEX idx_patient_lead_status ON patient_lead(status, created_at);
CREATE INDEX idx_patient_lead_converted ON patient_lead(converted_to_patient_id);

-- Patient indexes
CREATE INDEX idx_patient_person ON patient(person_id);
CREATE INDEX idx_patient_condition ON patient(medical_condition_id);
CREATE INDEX idx_patient_status ON patient(status, created_at);

-- Call History indexes
CREATE INDEX idx_call_history_patient ON call_history(patient_id, call_date);
CREATE INDEX idx_call_history_booking ON call_history(booking_date);
CREATE INDEX idx_call_history_pn ON call_history(pn_id);

-- Physician indexes
CREATE INDEX idx_physician_person ON physician(person_id);
CREATE INDEX idx_physician_hospital ON physician(hospital_id);
CREATE INDEX idx_physician_specialization ON physician(specialization_id);
CREATE INDEX idx_physician_license ON physician(medical_license_number);

-- Patient Physician Relationship indexes
CREATE INDEX idx_patient_physician_patient ON patient_physician_relationship(patient_id);
CREATE INDEX idx_patient_physician_physician ON patient_physician_relationship(physician_id);
CREATE INDEX idx_patient_physician_primary ON patient_physician_relationship(is_primary);
CREATE UNIQUE INDEX idx_unique_primary_physician ON patient_physician_relationship(patient_id) 
    WHERE is_primary = TRUE;

-- Clinical Trial Journey indexes
CREATE INDEX idx_ct_journey_patient ON clinical_trial_journey(patient_id, status);
CREATE INDEX idx_ct_journey_trial ON clinical_trial_journey(trial_id);
CREATE INDEX idx_ct_journey_physician ON clinical_trial_journey(physician_id);
CREATE INDEX idx_ct_journey_referral ON clinical_trial_journey(referral_date);

-- EAP Journey indexes
CREATE INDEX idx_eap_journey_patient ON eap_journey(patient_id, status);
CREATE INDEX idx_eap_journey_number ON eap_journey(eap_number);
CREATE INDEX idx_eap_journey_physician ON eap_journey(physician_id);
CREATE INDEX idx_eap_journey_enrollment ON eap_journey(enrollment_date);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_person_updated_at BEFORE UPDATE ON person
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_condition_updated_at BEFORE UPDATE ON medical_condition
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hospital_updated_at BEFORE UPDATE ON hospital
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_physician_updated_at BEFORE UPDATE ON physician
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patient_updated_at BEFORE UPDATE ON patient
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ct_journey_updated_at BEFORE UPDATE ON clinical_trial_journey
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_eap_journey_updated_at BEFORE UPDATE ON eap_journey
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS (Optional - for common queries)
-- ============================================================================

-- View: Active Patients with Person Info
CREATE OR REPLACE VIEW v_active_patients AS
SELECT 
    p.patient_id,
    p.person_id,
    per.first_name,
    per.last_name,
    per.email,
    mc.name AS medical_condition,
    p.first_contact_date,
    p.initial_consult_date,
    p.status,
    p.created_at
FROM patient p
JOIN person per ON p.person_id = per.person_id
JOIN medical_condition mc ON p.medical_condition_id = mc.medical_condition_id
WHERE p.status = 'active' AND per.is_active = TRUE;

-- View: Patient with Latest Call
CREATE OR REPLACE VIEW v_patient_latest_call AS
SELECT DISTINCT ON (ch.patient_id)
    p.patient_id,
    per.first_name,
    per.last_name,
    ch.call_date,
    ch.outcome,
    ch.no_show
FROM call_history ch
JOIN patient p ON ch.patient_id = p.patient_id
JOIN person per ON p.person_id = per.person_id
ORDER BY ch.patient_id, ch.call_date DESC NULLS LAST;

-- View: Patient Journey Summary
CREATE OR REPLACE VIEW v_patient_journey_summary AS
SELECT 
    p.patient_id,
    per.first_name || ' ' || per.last_name AS patient_name,
    COUNT(DISTINCT ct.ct_journey_id) AS ct_journey_count,
    COUNT(DISTINCT eap.eap_journey_id) AS eap_journey_count,
    COUNT(DISTINCT ch.call_id) AS call_count
FROM patient p
JOIN person per ON p.person_id = per.person_id
LEFT JOIN clinical_trial_journey ct ON p.patient_id = ct.patient_id
LEFT JOIN eap_journey eap ON p.patient_id = eap.patient_id
LEFT JOIN call_history ch ON p.patient_id = ch.patient_id
GROUP BY p.patient_id, per.first_name, per.last_name;
