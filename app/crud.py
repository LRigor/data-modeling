"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional, List, Tuple
from uuid import UUID
from app import models, schemas
from app.exceptions import (
    PatientNotFoundError,
    PersonNotFoundError,
    DuplicatePatientError,
    MedicalConditionNotFoundError,
    DatabaseError
)
from app.logger import logger


def get_person(db: Session, person_id: UUID) -> Optional[models.Person]:
    """Get a person by ID."""
    return db.query(models.Person).filter(models.Person.person_id == person_id).first()


def get_person_by_email(db: Session, email: str) -> Optional[models.Person]:
    """Get a person by email."""
    return db.query(models.Person).filter(models.Person.email == email).first()


def get_persons(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[models.Person]:
    """Get multiple persons with pagination."""
    query = db.query(models.Person)
    
    if is_active is not None:
        query = query.filter(models.Person.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """
    Create a new person record.
    
    Args:
        db: Database session
        person: Person creation schema
        
    Returns:
        Created Person model instance
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        db_person = models.Person(
            first_name=person.first_name,
            last_name=person.last_name,
            email=person.email,
            phone=person.phone
        )
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        logger.info(f"Created person {db_person.person_id} with email {person.email}")
        return db_person
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating person: {e}")
        raise DatabaseError(f"Failed to create person: duplicate email or constraint violation", e)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating person: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def update_person(
    db: Session, 
    person_id: UUID, 
    person_update: schemas.PersonUpdate
) -> Optional[models.Person]:
    """Update a person."""
    db_person = get_person(db, person_id)
    if not db_person:
        return None
    
    update_data = person_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_person, field, value)
    
    db.commit()
    db.refresh(db_person)
    return db_person


def delete_person(db: Session, person_id: UUID) -> bool:
    """Soft delete a person (set is_active=False)."""
    db_person = get_person(db, person_id)
    if not db_person:
        return False
    
    db_person.is_active = False
    db.commit()
    return True


def get_medical_condition(
    db: Session, 
    medical_condition_id: UUID
) -> Optional[models.MedicalCondition]:
    """Get a medical condition by ID."""
    return db.query(models.MedicalCondition).filter(
        models.MedicalCondition.medical_condition_id == medical_condition_id
    ).first()


def get_medical_conditions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[models.MedicalCondition]:
    """Get multiple medical conditions."""
    query = db.query(models.MedicalCondition)
    
    if is_active is not None:
        query = query.filter(models.MedicalCondition.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def create_medical_condition(
    db: Session,
    medical_condition: schemas.MedicalConditionCreate
) -> models.MedicalCondition:
    """Create a new medical condition."""
    try:
        db_condition = models.MedicalCondition(
            name=medical_condition.name,
            abbreviation=medical_condition.abbreviation,
            description=medical_condition.description
        )
        db.add(db_condition)
        db.commit()
        db.refresh(db_condition)
        logger.info(f"Created medical condition {db_condition.medical_condition_id}")
        return db_condition
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating medical condition: {e}")
        raise DatabaseError(f"Failed to create medical condition: duplicate name or constraint violation", e)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating medical condition: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def update_medical_condition(
    db: Session,
    medical_condition_id: UUID,
    medical_condition_update: schemas.MedicalConditionUpdate
) -> Optional[models.MedicalCondition]:
    """
    Update a medical condition.
    
    Args:
        db: Database session
        medical_condition_id: UUID of the medical condition to update
        medical_condition_update: Update schema with fields to update
        
    Returns:
        Updated MedicalCondition model instance or None if not found
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        db_condition = get_medical_condition(db, medical_condition_id)
        if not db_condition:
            return None
        
        update_data = medical_condition_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_condition, field, value)
        
        db.commit()
        db.refresh(db_condition)
        logger.info(f"Updated medical condition {medical_condition_id}")
        return db_condition
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating medical condition: {e}")
        raise DatabaseError(f"Failed to update medical condition: duplicate name or constraint violation", e)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating medical condition: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def delete_medical_condition(db: Session, medical_condition_id: UUID) -> bool:
    """
    Soft delete a medical condition (set is_active=False).
    
    Args:
        db: Database session
        medical_condition_id: UUID of the medical condition to delete
        
    Returns:
        True if successful, False if medical condition not found
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        db_condition = get_medical_condition(db, medical_condition_id)
        if not db_condition:
            return False
        
        db_condition.is_active = False
        db.commit()
        logger.info(f"Soft deleted medical condition {medical_condition_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting medical condition: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def get_patient(db: Session, patient_id: UUID) -> Optional[models.Patient]:
    """Get a patient by ID with relationships."""
    return db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()


def get_patient_by_person_id(
    db: Session, 
    person_id: UUID
) -> Optional[models.Patient]:
    """Get a patient by person ID."""
    return db.query(models.Patient).filter(
        models.Patient.person_id == person_id
    ).first()


def get_patients(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    medical_condition_id: Optional[UUID] = None
) -> Tuple[List[models.Patient], int]:
    """Get multiple patients with pagination and filters."""
    query = db.query(models.Patient)
    
    if status:
        query = query.filter(models.Patient.status == status)
    
    if medical_condition_id:
        query = query.filter(models.Patient.medical_condition_id == medical_condition_id)
    
    total = query.count()
    patients = query.offset(skip).limit(limit).all()
    
    return patients, total


def create_patient_with_person(
    db: Session,
    patient: schemas.PatientCreate
) -> models.Patient:
    """
    Create a new patient with person information.
    
    If a person with the provided email exists, the existing person record
    is used (returning patient scenario). Otherwise, a new person record
    is created.
    
    Args:
        db: Database session
        patient: Patient creation schema with person information
        
    Returns:
        Created Patient model instance
        
    Raises:
        DuplicatePatientError: If patient already exists for the person
        MedicalConditionNotFoundError: If medical condition doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        medical_condition = get_medical_condition(db, patient.medical_condition_id)
        if not medical_condition:
            raise MedicalConditionNotFoundError(str(patient.medical_condition_id))
        
        db_person = get_person_by_email(db, patient.person.email)
        
        if not db_person:
            db_person = create_person(db, patient.person)
            logger.info(f"Created new person {db_person.person_id} for patient")
        else:
            if patient.person.first_name:
                db_person.first_name = patient.person.first_name
            if patient.person.last_name:
                db_person.last_name = patient.person.last_name
            if patient.person.phone:
                db_person.phone = patient.person.phone
            db.commit()
            db.refresh(db_person)
            logger.info(f"Using existing person {db_person.person_id} for returning patient")
        
        existing_patient = get_patient_by_person_id(db, db_person.person_id)
        if existing_patient:
            raise DuplicatePatientError(str(db_person.person_id))
        
        db_patient = models.Patient(
            person_id=db_person.person_id,
            medical_condition_id=patient.medical_condition_id,
            first_contact_date=patient.first_contact_date,
            initial_consult_date=patient.initial_consult_date,
            status=patient.status
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        logger.info(f"Created patient {db_patient.patient_id} for person {db_person.person_id}")
        return db_patient
    except (DuplicatePatientError, MedicalConditionNotFoundError):
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating patient: {e}")
        raise DatabaseError(f"Failed to create patient: constraint violation", e)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating patient: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def create_patient_with_existing_person(
    db: Session,
    patient: schemas.PatientCreateWithPersonId
) -> models.Patient:
    """
    Create a new patient with existing person ID.
    
    Args:
        db: Database session
        patient: Patient creation schema with existing person ID
        
    Returns:
        Created Patient model instance
        
    Raises:
        PersonNotFoundError: If person doesn't exist
        DuplicatePatientError: If patient already exists for the person
        MedicalConditionNotFoundError: If medical condition doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        db_person = get_person(db, patient.person_id)
        if not db_person:
            raise PersonNotFoundError(person_id=str(patient.person_id))
        
        medical_condition = get_medical_condition(db, patient.medical_condition_id)
        if not medical_condition:
            raise MedicalConditionNotFoundError(str(patient.medical_condition_id))
        
        existing_patient = get_patient_by_person_id(db, patient.person_id)
        if existing_patient:
            raise DuplicatePatientError(str(patient.person_id))
        
        db_patient = models.Patient(
            person_id=patient.person_id,
            medical_condition_id=patient.medical_condition_id,
            first_contact_date=patient.first_contact_date,
            initial_consult_date=patient.initial_consult_date,
            status=patient.status
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        logger.info(f"Created patient {db_patient.patient_id} for existing person {patient.person_id}")
        return db_patient
    except (PersonNotFoundError, DuplicatePatientError, MedicalConditionNotFoundError):
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating patient: {e}")
        raise DatabaseError(f"Failed to create patient: constraint violation", e)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating patient: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def update_patient(
    db: Session,
    patient_id: UUID,
    patient_update: schemas.PatientUpdate
) -> Optional[models.Patient]:
    """Update a patient."""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, patient_id: UUID) -> bool:
    """Delete a patient (hard delete)."""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    
    db.delete(db_patient)
    db.commit()
    return True


def get_call_history(db: Session, call_id: UUID) -> Optional[models.CallHistory]:
    """Get a call history record by ID."""
    return db.query(models.CallHistory).filter(
        models.CallHistory.call_id == call_id
    ).first()


def get_call_histories_by_patient(
    db: Session,
    patient_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[models.CallHistory], int]:
    """Get call histories for a patient."""
    query = db.query(models.CallHistory).filter(
        models.CallHistory.patient_id == patient_id
    ).order_by(models.CallHistory.call_date.desc().nulls_last())
    
    total = query.count()
    calls = query.offset(skip).limit(limit).all()
    
    return calls, total


def create_call_history(
    db: Session,
    call_history: schemas.CallHistoryCreate
) -> models.CallHistory:
    """
    Create a new call history record.
    
    Args:
        db: Database session
        call_history: Call history creation schema
        
    Returns:
        Created CallHistory model instance
        
    Raises:
        PatientNotFoundError: If patient doesn't exist
        DatabaseError: If database operation fails
    """
    try:
        db_patient = get_patient(db, call_history.patient_id)
        if not db_patient:
            raise PatientNotFoundError(str(call_history.patient_id))
        
        db_call = models.CallHistory(
            patient_id=call_history.patient_id,
            pn_id=call_history.pn_id,
            booking_date=call_history.booking_date,
            call_date=call_history.call_date,
            reminder_date=call_history.reminder_date,
            no_show=call_history.no_show,
            call_duration_minutes=call_history.call_duration_minutes,
            outcome=call_history.outcome,
            notes=call_history.notes
        )
        db.add(db_call)
        db.commit()
        db.refresh(db_call)
        logger.info(f"Created call history {db_call.call_id} for patient {call_history.patient_id}")
        return db_call
    except PatientNotFoundError:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating call history: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}", e)


def update_call_history(
    db: Session,
    call_id: UUID,
    call_update: schemas.CallHistoryUpdate
) -> Optional[models.CallHistory]:
    """Update a call history record."""
    db_call = get_call_history(db, call_id)
    if not db_call:
        return None
    
    update_data = call_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_call, field, value)
    
    db.commit()
    db.refresh(db_call)
    return db_call


def delete_call_history(db: Session, call_id: UUID) -> bool:
    """Delete a call history record."""
    db_call = get_call_history(db, call_id)
    if not db_call:
        return False
    
    db.delete(db_call)
    db.commit()
    return True
