"""
Medical Condition API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app import crud, schemas
from app.database import get_db
from app.exceptions import MedicalConditionNotFoundError, DatabaseError
from app.logger import logger

router = APIRouter(
    prefix="/medical-conditions",
    tags=["medical-conditions"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.MedicalConditionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical condition",
    description="Create a new medical condition in the lookup table."
)
def create_medical_condition(
    medical_condition: schemas.MedicalConditionCreate,
    db: Session = Depends(get_db)
) -> schemas.MedicalConditionResponse:
    """
    Create a new medical condition in the lookup table.
    
    Args:
        medical_condition: Medical condition creation schema
        db: Database session dependency
        
    Returns:
        Created medical condition response
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        db_condition = crud.create_medical_condition(db, medical_condition)
        logger.info(f"Successfully created medical condition {db_condition.medical_condition_id}")
        return db_condition
    except DatabaseError as e:
        logger.error(f"Database error creating medical condition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medical condition due to database error"
        )


@router.get(
    "/",
    response_model=list[schemas.MedicalConditionResponse],
    summary="Get all medical conditions",
    description="Get a list of medical conditions with optional filtering."
)
def read_medical_conditions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
) -> List[schemas.MedicalConditionResponse]:
    """
    Get a list of medical conditions with optional filtering.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max 1000)
        is_active: Filter by active status
        db: Database session dependency
        
    Returns:
        List of medical condition responses
    """
    conditions = crud.get_medical_conditions(db, skip=skip, limit=limit, is_active=is_active)
    return conditions


@router.get(
    "/{medical_condition_id}",
    response_model=schemas.MedicalConditionResponse,
    summary="Get a medical condition by ID",
    description="Get detailed information about a specific medical condition."
)
def read_medical_condition(
    medical_condition_id: UUID,
    db: Session = Depends(get_db)
) -> schemas.MedicalConditionResponse:
    """
    Get a medical condition by ID.
    
    Args:
        medical_condition_id: UUID of the medical condition
        db: Database session dependency
        
    Returns:
        Medical condition response schema
        
    Raises:
        HTTPException: 404 if medical condition not found
    """
    db_condition = crud.get_medical_condition(db, medical_condition_id=medical_condition_id)
    if db_condition is None:
        logger.warning(f"Medical condition {medical_condition_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical condition {medical_condition_id} not found"
        )
    return db_condition
