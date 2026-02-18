"""
Patient API routes with CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from math import ceil

from app import crud, schemas
from app.database import get_db
from app.exceptions import (
    PatientNotFoundError,
    PersonNotFoundError,
    DuplicatePatientError,
    MedicalConditionNotFoundError,
    DatabaseError
)
from app.logger import logger

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient",
    description="Create a new patient with person information. If person with email exists, uses existing person (handles returning patients)."
)
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db)
) -> schemas.PatientResponse:
    """
    Create a new patient.
    
    If a person with the provided email exists, the existing person record
    is used (returning patient scenario). Otherwise, a new person record
    is created. The operation validates that a patient doesn't already
    exist for the person.
    
    Args:
        patient: Patient creation schema with person information
        db: Database session dependency
        
    Returns:
        Created patient response
        
    Raises:
        HTTPException: 400 if validation fails or patient already exists
                      404 if medical condition not found
                      500 if database operation fails
    """
    try:
        db_patient = crud.create_patient_with_person(db, patient)
        db.refresh(db_patient)
        logger.info(f"Successfully created patient {db_patient.patient_id}")
        return db_patient
    except DuplicatePatientError as e:
        logger.warning(f"Attempted to create duplicate patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except MedicalConditionNotFoundError as e:
        logger.warning(f"Medical condition not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient due to database error"
        )


@router.post(
    "/with-person-id",
    response_model=schemas.PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a patient with existing person ID",
    description="Create a new patient using an existing person ID."
)
def create_patient_with_person_id(
    patient: schemas.PatientCreateWithPersonId,
    db: Session = Depends(get_db)
) -> schemas.PatientResponse:
    """
    Create a patient with existing person ID.
    
    Args:
        patient: Patient creation schema with existing person ID
        db: Database session dependency
        
    Returns:
        Created patient response
        
    Raises:
        HTTPException: 404 if person or medical condition not found
                      409 if patient already exists
                      500 if database operation fails
    """
    try:
        db_patient = crud.create_patient_with_existing_person(db, patient)
        db.refresh(db_patient)
        logger.info(f"Successfully created patient {db_patient.patient_id} with existing person")
        return db_patient
    except PersonNotFoundError as e:
        logger.warning(f"Person not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicatePatientError as e:
        logger.warning(f"Attempted to create duplicate patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except MedicalConditionNotFoundError as e:
        logger.warning(f"Medical condition not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient due to database error"
        )


@router.get(
    "/",
    response_model=schemas.PatientListResponse,
    summary="Get all patients",
    description="Get a paginated list of patients with optional filtering."
)
def read_patients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by patient status"),
    medical_condition_id: Optional[UUID] = Query(None, description="Filter by medical condition ID"),
    db: Session = Depends(get_db)
):
    """
    Get patients with pagination and filtering.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **status**: Filter by patient status (e.g., 'active', 'inactive')
    - **medical_condition_id**: Filter by medical condition UUID
    """
    patients, total = crud.get_patients(
        db, skip=skip, limit=limit, status=status, medical_condition_id=medical_condition_id
    )
    
    total_pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return schemas.PatientListResponse(
        items=patients,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get(
    "/{patient_id}",
    response_model=schemas.PatientResponse,
    summary="Get a patient by ID",
    description="Get detailed information about a specific patient."
)
def read_patient(
    patient_id: UUID,
    db: Session = Depends(get_db)
) -> schemas.PatientResponse:
    """
    Get a patient by ID.
    
    Args:
        patient_id: UUID of the patient
        db: Database session dependency
        
    Returns:
        Patient response schema
        
    Raises:
        HTTPException: 404 if patient not found
    """
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        logger.warning(f"Patient {patient_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return db_patient


@router.put(
    "/{patient_id}",
    response_model=schemas.PatientResponse,
    summary="Update a patient",
    description="Update patient information. Only provided fields will be updated."
)
def update_patient(
    patient_id: UUID,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update a patient."""
    db_patient = crud.update_patient(db, patient_id=patient_id, patient_update=patient_update)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return db_patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a patient",
    description="Delete a patient record (hard delete)."
)
def delete_patient(
    patient_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a patient."""
    success = crud.delete_patient(db, patient_id=patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return None


@router.get(
    "/{patient_id}/calls",
    response_model=list[schemas.CallHistoryResponse],
    summary="Get call history for a patient",
    description="Get all call history records for a specific patient."
)
def get_patient_calls(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get call history for a patient."""
    db_patient = crud.get_patient(db, patient_id)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    calls, total = crud.get_call_histories_by_patient(db, patient_id, skip=skip, limit=limit)
    return calls
