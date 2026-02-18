"""
Database initialization script.
Creates tables and optionally seeds initial data.
"""
from sqlalchemy import create_engine, text
from app.database import Base, engine
from app.config import settings
from app import models
import sys


def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_medical_conditions():
    """Seed initial medical conditions."""
    from app.database import SessionLocal
    from app import models
    
    db = SessionLocal()
    try:
        existing = db.query(models.MedicalCondition).count()
        if existing > 0:
            print(f"✓ Medical conditions already exist ({existing} records)")
            return
        
        conditions = [
            models.MedicalCondition(
                name="Duchenne Muscular Dystrophy",
                abbreviation="DMD",
                description="A genetic disorder characterized by progressive muscle degeneration"
            ),
            models.MedicalCondition(
                name="Glioblastoma",
                abbreviation="GBM",
                description="An aggressive type of brain cancer"
            ),
            models.MedicalCondition(
                name="Idiopathic Pulmonary Fibrosis",
                abbreviation="IPF",
                description="A chronic lung disease characterized by progressive scarring"
            ),
        ]
        
        for condition in conditions:
            db.add(condition)
        
        db.commit()
        print(f"✓ Seeded {len(conditions)} medical conditions")
    except Exception as e:
        print(f"✗ Error seeding medical conditions: {e}")
        db.rollback()
    finally:
        db.close()


def verify_connection():
    """Verify database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Database connection successful")
            print(f"  PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()
    
    if not verify_connection():
        print("\nPlease check your POSTGRES_* variables in .env file")
        sys.exit(1)
    
    print()
    init_database()
    print()
    seed_medical_conditions()
    print()
    
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
