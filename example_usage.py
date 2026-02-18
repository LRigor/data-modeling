"""
Example usage of the API.
Demonstrates how to interact with the FastAPI endpoints.
"""
import requests
import json
from uuid import UUID


BASE_URL = "http://localhost:8000/api/v1"


def print_response(response, title="Response"):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, default=str))
    except:
        print(response.text)
    print()


def example_create_patient():
    """Example: Create a patient."""
    print("\n" + "="*60)
    print("Example 1: Create a Patient")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/medical-conditions")
    if response.status_code == 200:
        conditions = response.json()
        if conditions:
            medical_condition_id = conditions[0]["medical_condition_id"]
        else:
            print("No medical conditions found. Please seed the database first.")
            return
    else:
        print("Failed to fetch medical conditions")
        return
    
    patient_data = {
        "person": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890"
        },
        "medical_condition_id": str(medical_condition_id),
        "first_contact_date": "2024-01-15",
        "initial_consult_date": "2024-01-20",
        "status": "active"
    }
    
    response = requests.post(
        f"{BASE_URL}/patients",
        json=patient_data
    )
    
    print_response(response, "Create Patient")
    
    if response.status_code == 201:
        return response.json()["patient_id"]
    return None


def example_get_patients():
    """Example: Get all patients."""
    print("\n" + "="*60)
    print("Example 2: Get All Patients")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/patients",
        params={"skip": 0, "limit": 10}
    )
    
    print_response(response, "Get Patients")


def example_get_patient(patient_id: str):
    """Example: Get a specific patient."""
    print("\n" + "="*60)
    print(f"Example 3: Get Patient {patient_id}")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    print_response(response, "Get Patient")


def example_create_call_history(patient_id: str):
    """Example: Create call history."""
    print("\n" + "="*60)
    print("Example 4: Create Call History")
    print("="*60)
    
    call_data = {
        "patient_id": str(patient_id),
        "booking_date": "2024-01-25T10:00:00Z",
        "call_date": "2024-01-25T10:30:00Z",
        "reminder_date": "2024-01-25T09:00:00Z",
        "no_show": False,
        "call_duration_minutes": 30,
        "outcome": "converted",
        "notes": "Patient is interested in clinical trial options"
    }
    
    response = requests.post(
        f"{BASE_URL}/call-history",
        json=call_data
    )
    
    print_response(response, "Create Call History")


def example_get_patient_calls(patient_id: str):
    """Example: Get call history for a patient."""
    print("\n" + "="*60)
    print(f"Example 5: Get Call History for Patient {patient_id}")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/patients/{patient_id}/calls")
    print_response(response, "Get Patient Calls")


def example_update_patient(patient_id: str):
    """Example: Update a patient."""
    print("\n" + "="*60)
    print(f"Example 6: Update Patient {patient_id}")
    print("="*60)
    
    update_data = {
        "status": "inactive",
        "initial_consult_date": "2024-01-22"
    }
    
    response = requests.put(
        f"{BASE_URL}/patients/{patient_id}",
        json=update_data
    )
    
    print_response(response, "Update Patient")


def example_returning_patient():
    """Example: Handle returning patient (same email)."""
    print("\n" + "="*60)
    print("Example 7: Returning Patient (Same Email)")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/medical-conditions")
    if response.status_code == 200:
        conditions = response.json()
        if conditions:
            medical_condition_id = conditions[0]["medical_condition_id"]
        else:
            print("No medical conditions found.")
            return
    else:
        return
    
    patient_data = {
        "person": {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.doe@example.com",
            "phone": "+9876543210"
        },
        "medical_condition_id": str(medical_condition_id),
        "status": "active"
    }
    
    response = requests.post(
        f"{BASE_URL}/patients",
        json=patient_data
    )
    
    print_response(response, "Returning Patient")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("FastAPI Example Usage")
    print("="*60)
    print("\nMake sure the API is running: http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    patient_id = example_create_patient()
    
    if patient_id:
        example_get_patients()
        example_get_patient(str(patient_id))
        example_create_call_history(str(patient_id))
        example_get_patient_calls(str(patient_id))
        example_update_patient(str(patient_id))
    
    example_returning_patient()
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)
