"""
Call History API routes with CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud, schemas
from app.database import get_db
from app.exceptions import PatientNotFoundError, DatabaseError
from app.logger import logger

router = APIRouter(
    prefix="/call-history",
    tags=["call-history"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.CallHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new call history record",
    description="Create a new call history record for a patient. Multiple calls per patient are supported."
)
def create_call_history(
    call_history: schemas.CallHistoryCreate,
    db: Session = Depends(get_db)
) -> schemas.CallHistoryResponse:
    """
    Create a new call history record.
    
    Multiple call records per patient are supported. Each call is stored
    as a separate record to prevent data loss.
    
    Args:
        call_history: Call history creation schema
        db: Database session dependency
        
    Returns:
        Created call history response
        
    Raises:
        HTTPException: 404 if patient not found
                      500 if database operation fails
    """
    try:
        db_call = crud.create_call_history(db, call_history)
        logger.info(f"Successfully created call history {db_call.call_id}")
        return db_call
    except PatientNotFoundError as e:
        logger.warning(f"Patient not found for call history: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error creating call history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create call history due to database error"
        )


@router.get(
    "/{call_id}",
    response_model=schemas.CallHistoryResponse,
    summary="Get a call history record by ID",
    description="Get detailed information about a specific call history record."
)
def read_call_history(
    call_id: UUID,
    db: Session = Depends(get_db)
) -> schemas.CallHistoryResponse:
    """
    Get a call history record by ID.
    
    Args:
        call_id: UUID of the call history record
        db: Database session dependency
        
    Returns:
        Call history response schema
        
    Raises:
        HTTPException: 404 if call history not found
    """
    db_call = crud.get_call_history(db, call_id=call_id)
    if db_call is None:
        logger.warning(f"Call history {call_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call history {call_id} not found"
        )
    return db_call


@router.put(
    "/{call_id}",
    response_model=schemas.CallHistoryResponse,
    summary="Update a call history record",
    description="Update call history information. Only provided fields will be updated."
)
def update_call_history(
    call_id: UUID,
    call_update: schemas.CallHistoryUpdate,
    db: Session = Depends(get_db)
) -> schemas.CallHistoryResponse:
    """
    Update a call history record.
    
    Only provided fields will be updated. Fields not included in the
    update schema remain unchanged.
    
    Args:
        call_id: UUID of the call history record
        call_update: Call history update schema
        db: Database session dependency
        
    Returns:
        Updated call history response
        
    Raises:
        HTTPException: 404 if call history not found
    """
    db_call = crud.update_call_history(db, call_id=call_id, call_update=call_update)
    if db_call is None:
        logger.warning(f"Call history {call_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call history {call_id} not found"
        )
    logger.info(f"Successfully updated call history {call_id}")
    return db_call


@router.delete(
    "/{call_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a call history record",
    description="Delete a call history record."
)
def delete_call_history(
    call_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a call history record.
    
    Args:
        call_id: UUID of the call history record
        db: Database session dependency
        
    Raises:
        HTTPException: 404 if call history not found
    """
    success = crud.delete_call_history(db, call_id=call_id)
    if not success:
        logger.warning(f"Call history {call_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call history {call_id} not found"
        )
    logger.info(f"Successfully deleted call history {call_id}")
    return None
