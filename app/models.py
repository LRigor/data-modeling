"""
SQLAlchemy models for the database.
"""
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Person(Base):
    """Person model representing the single source of truth for person information."""
    __tablename__ = "person"
    
    person_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    patient = relationship("Patient", back_populates="person", uselist=False)
    physician = relationship("Physician", back_populates="person", uselist=False)
    call_histories = relationship("CallHistory", back_populates="patient", foreign_keys="CallHistory.patient_id")
    
    def __repr__(self):
        return f"<Person(id={self.person_id}, email={self.email})>"


class MedicalCondition(Base):
    """Medical Condition lookup table providing a single normalized source."""
    __tablename__ = "medical_condition"
    
    medical_condition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), unique=True, nullable=False)
    abbreviation = Column(String(50))
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    patients = relationship("Patient", back_populates="medical_condition")
    
    def __repr__(self):
        return f"<MedicalCondition(id={self.medical_condition_id}, name={self.name})>"


class Patient(Base):
    """Patient model representing a converted lead."""
    __tablename__ = "patient"
    
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"), unique=True, nullable=False, index=True)
    medical_condition_id = Column(UUID(as_uuid=True), ForeignKey("medical_condition.medical_condition_id"), nullable=False, index=True)
    first_contact_date = Column(Date)
    initial_consult_date = Column(Date)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    person = relationship("Person", back_populates="patient")
    medical_condition = relationship("MedicalCondition", back_populates="patients")
    call_histories = relationship("CallHistory", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.patient_id}, person_id={self.person_id})>"


class CallHistory(Base):
    """Call History model tracking all calls and interactions with Patient Navigators."""
    __tablename__ = "call_history"
    
    call_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patient.patient_id"), nullable=False, index=True)
    pn_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"), index=True)
    booking_date = Column(DateTime(timezone=True), index=True)
    call_date = Column(DateTime(timezone=True))
    reminder_date = Column(DateTime(timezone=True))
    no_show = Column(Boolean, default=False, nullable=False)
    call_duration_minutes = Column(Integer)
    outcome = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    patient = relationship("Patient", back_populates="call_histories")
    
    def __repr__(self):
        return f"<CallHistory(id={self.call_id}, patient_id={self.patient_id})>"


class Physician(Base):
    """Physician model representing healthcare providers."""
    __tablename__ = "physician"
    
    physician_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"), unique=True, nullable=False, index=True)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospital.hospital_id"), index=True)
    job_title = Column(String(200))
    specialization_id = Column(UUID(as_uuid=True), ForeignKey("specialization.specialization_id"), index=True)
    medical_license_number = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    person = relationship("Person", back_populates="physician")
    
    def __repr__(self):
        return f"<Physician(id={self.physician_id}, person_id={self.person_id})>"


class Hospital(Base):
    """Hospital lookup table providing normalized hospital information."""
    __tablename__ = "hospital"
    
    hospital_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Hospital(id={self.hospital_id}, name={self.name})>"
