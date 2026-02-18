"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class PersonBase(BaseModel):
    """Base schema for Person."""
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")


class PersonCreate(PersonBase):
    """Schema for creating a Person."""
    pass


class PersonUpdate(BaseModel):
    """Schema for updating a Person."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class PersonResponse(PersonBase):
    """Schema for Person response."""
    person_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class MedicalConditionBase(BaseModel):
    """Base schema for Medical Condition."""
    name: str = Field(..., min_length=1, max_length=200, description="Condition name")
    abbreviation: Optional[str] = Field(None, max_length=50, description="Abbreviation")
    description: Optional[str] = Field(None, description="Description")


class MedicalConditionCreate(MedicalConditionBase):
    """Schema for creating a Medical Condition."""
    pass


class MedicalConditionUpdate(BaseModel):
    """Schema for updating a Medical Condition."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Condition name")
    abbreviation: Optional[str] = Field(None, max_length=50, description="Abbreviation")
    description: Optional[str] = Field(None, description="Description")
    is_active: Optional[bool] = Field(None, description="Active status")


class MedicalConditionResponse(MedicalConditionBase):
    """Schema for Medical Condition response."""
    medical_condition_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PatientBase(BaseModel):
    """Base schema for Patient."""
    medical_condition_id: UUID = Field(..., description="Medical condition ID")
    first_contact_date: Optional[date] = Field(None, description="First contact date")
    initial_consult_date: Optional[date] = Field(None, description="Initial consultation date")
    status: str = Field("active", max_length=50, description="Patient status")


class PatientCreate(PatientBase):
    """Schema for creating a Patient."""
    person: PersonCreate = Field(..., description="Person information")


class PatientCreateWithPersonId(PatientBase):
    """Schema for creating a Patient with existing Person ID."""
    person_id: UUID = Field(..., description="Existing person ID")


class PatientUpdate(BaseModel):
    """Schema for updating a Patient."""
    medical_condition_id: Optional[UUID] = None
    first_contact_date: Optional[date] = None
    initial_consult_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)


class PatientResponse(PatientBase):
    """Schema for Patient response."""
    patient_id: UUID
    person_id: UUID
    created_at: datetime
    updated_at: datetime
    person: Optional[PersonResponse] = None
    medical_condition: Optional[MedicalConditionResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    """Schema for paginated Patient list response."""
    items: List[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CallHistoryBase(BaseModel):
    """Base schema for Call History."""
    patient_id: UUID = Field(..., description="Patient ID")
    pn_id: Optional[UUID] = Field(None, description="Patient Navigator ID")
    booking_date: Optional[datetime] = Field(None, description="Booking date")
    call_date: Optional[datetime] = Field(None, description="Call date")
    reminder_date: Optional[datetime] = Field(None, description="Reminder date")
    no_show: bool = Field(False, description="No show flag")
    call_duration_minutes: Optional[int] = Field(None, ge=0, description="Call duration in minutes")
    outcome: Optional[str] = Field(None, max_length=100, description="Call outcome")
    notes: Optional[str] = Field(None, description="Call notes")


class CallHistoryCreate(CallHistoryBase):
    """Schema for creating a Call History."""
    pass


class CallHistoryUpdate(BaseModel):
    """Schema for updating a Call History."""
    pn_id: Optional[UUID] = None
    booking_date: Optional[datetime] = None
    call_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    no_show: Optional[bool] = None
    call_duration_minutes: Optional[int] = Field(None, ge=0)
    outcome: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CallHistoryResponse(CallHistoryBase):
    """Schema for Call History response."""
    call_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    detail: List[dict]
    error_code: str = "VALIDATION_ERROR"
