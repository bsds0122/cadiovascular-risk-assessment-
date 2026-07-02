import pytest
from datetime import date
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.doctors import Doctor
from app.models.patients import Patient
from app.services.patient.view import (
    get_all_patients,
    search_patients,
    autocomplete_patients,
    get_patient_by_id
)

@pytest.fixture
def setup_data(db_session: Session):
    # Create a user
    user = User(email="doctor@example.com", password="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create a doctor
    doctor = Doctor(
        user_id=user.user_id,
        first_name="John",
        last_name="Doe",
        phone="1234567890",
        specialization="General",
        experience_years=5,
        hospital="City Hospital",
        license_number="LIC123"
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    # Create patients
    p1 = Patient(
        doctor_id=doctor.doctor_id,
        first_name="Alice",
        last_name="Smith",
        phone_number="111",
        next_of_kin_number="222",
        date_of_diagnosis=date(2020, 1, 1),
        diabetes_type="Type 1",
        region="North",
        district="District 1",
        traditional_authority="TA 1",
        village="Village 1"
    )
    p2 = Patient(
        doctor_id=doctor.doctor_id,
        first_name="Bob",
        last_name="Jones",
        phone_number="333",
        next_of_kin_number="444",
        date_of_diagnosis=date(2021, 1, 1),
        diabetes_type="Type 2",
        region="South",
        district="District 2",
        traditional_authority="TA 2",
        village="Village 2"
    )
    p3 = Patient(
        doctor_id=doctor.doctor_id,
        first_name="Charlie",
        last_name="Brown",
        phone_number="555",
        next_of_kin_number="666",
        date_of_diagnosis=date(2022, 1, 1),
        diabetes_type="Type 1",
        region="East",
        district="District 3",
        traditional_authority="TA 3",
        village="Village 3"
    )
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    return doctor, [p1, p2, p3]

def test_get_all_patients(db_session: Session, setup_data):
    doctor, patients = setup_data
    
    # Test normal retrieval
    response = get_all_patients(db_session, doctor.doctor_id)
    assert response["status_code"] == 200
    assert len(response["data"]) == 3
    
    # Test skip and limit
    response = get_all_patients(db_session, doctor.doctor_id, skip=1, limit=1)
    assert response["status_code"] == 200
    assert len(response["data"]) == 1
    
    # Test negative skip (should default to 0)
    response = get_all_patients(db_session, doctor.doctor_id, skip=-5)
    assert response["status_code"] == 200
    assert len(response["data"]) == 3

def test_search_patients(db_session: Session, setup_data):
    doctor, patients = setup_data
    
    # Search by first name
    response = search_patients(db_session, doctor.doctor_id, name="Alice")
    assert response["status_code"] == 200
    assert len(response["data"]) == 1
    assert response["data"][0]["first_name"] == "Alice"
    
    # Search by part of last name
    response = search_patients(db_session, doctor.doctor_id, name="Jon")
    assert response["status_code"] == 200
    assert len(response["data"]) == 1
    assert response["data"][0]["last_name"] == "Jones"
    
    # Search with empty query
    response = search_patients(db_session, doctor.doctor_id, name="")
    assert response["status_code"] == 200
    assert response["data"] == []

def test_autocomplete_patients(db_session: Session, setup_data):
    doctor, patients = setup_data
    
    # Autocomplete query
    response = autocomplete_patients(db_session, doctor.doctor_id, query="Al")
    assert response["status_code"] == 200
    assert len(response["data"]) == 1
    assert response["data"][0]["label"] == "Alice Smith"
    
    # Autocomplete with multiple matches
    response = autocomplete_patients(db_session, doctor.doctor_id, query="o")
    # Bob Jones, Charlie Brown both have 'o'
    assert len(response["data"]) >= 2
    
def test_get_patient_by_id(db_session: Session, setup_data):
    doctor, patients = setup_data
    p1 = patients[0]
    
    # Test valid retrieval
    response = get_patient_by_id(db_session, p1.patient_id, doctor.doctor_id)
    assert response["status_code"] == 200
    assert response["data"]["first_name"] == "Alice"
    
    # Test non-existent patient
    response = get_patient_by_id(db_session, 9999, doctor.doctor_id)
    assert response["status_code"] == 404
    
    # Test patient belonging to different doctor (though we only have one doctor here)
    # We could create another doctor to test this properly
    user2 = User(email="doctor2@example.com", password="hashed_password")
    db_session.add(user2)
    db_session.commit()
    doctor2 = Doctor(
        user_id=user2.user_id,
        first_name="Jane", last_name="Smith", phone="0987654321",
        specialization="Cardio", experience_years=10, hospital="General Hospital",
        license_number="LIC456"
    )
    db_session.add(doctor2)
    db_session.commit()
    
    response = get_patient_by_id(db_session, p1.patient_id, doctor2.doctor_id)
    assert response["status_code"] == 404
