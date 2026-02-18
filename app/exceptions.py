"""
Custom exception classes for the application.
"""
from typing import Optional


class PatientNotFoundError(Exception):
    """Raised when a patient is not found."""
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        super().__init__(f"Patient {patient_id} not found")


class PersonNotFoundError(Exception):
    """Raised when a person is not found."""
    
    def __init__(self, person_id: Optional[str] = None, email: Optional[str] = None):
        self.person_id = person_id
        self.email = email
        identifier = person_id or email or "unknown"
        super().__init__(f"Person {identifier} not found")


class DuplicatePatientError(Exception):
    """Raised when attempting to create a duplicate patient."""
    
    def __init__(self, person_id: str):
        self.person_id = person_id
        super().__init__(f"Patient already exists for person {person_id}")


class MedicalConditionNotFoundError(Exception):
    """Raised when a medical condition is not found."""
    
    def __init__(self, condition_id: str):
        self.condition_id = condition_id
        super().__init__(f"Medical condition {condition_id} not found")


class DatabaseError(Exception):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)
