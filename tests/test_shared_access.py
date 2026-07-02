
import pytest
import datetime
from fastapi.testclient import TestClient

def test_shared_doctor_access(client: TestClient):
    # 1. Setup: Register Admin to create Doctors
    admin_payload = {
        "first_name": "Admin", "last_name": "User", "sex": "Male",
        "email": "admin.shared@example.com", "phone": "1231231234",
        "specialization": "Admin", "experience_years": 10, "hospital": "Admin Hosp"
    }
    
    # Registration returns the password.
    reg_response = client.post("/api/admin/register", json=admin_payload).json()
    admin_password = reg_response["data"]["password"]
    admin_token = client.post("/api/auth/login", json={
        "email": "admin.shared@example.com", "password": admin_password
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create two doctors
    doc1_payload = {
        "email": "doc1@example.com", "password": "password123",
        "first_name": "Doctor", "last_name": "One", "sex": "Male",
        "phone": "1111111111", "specialization": "General",
        "experience_years": 5, "hospital": "Hosp 1", "license_number": "LIC-1"
    }
    doc2_payload = {
        "email": "doc2@example.com", "password": "password123",
        "first_name": "Doctor", "last_name": "Two", "sex": "Female",
        "phone": "2222222222", "specialization": "General",
        "experience_years": 5, "hospital": "Hosp 2", "license_number": "LIC-2"
    }
    
    doc1_reg = client.post("/api/admin/doctors", json=doc1_payload, headers=admin_headers).json()
    doc2_reg = client.post("/api/admin/doctors", json=doc2_payload, headers=admin_headers).json()
    
    doc1_pass = doc1_reg["data"]["password"]
    doc2_pass = doc2_reg["data"]["password"]
    
    doc1_token = client.post("/api/auth/login", json={"email": "doc1@example.com", "password": doc1_pass}).json()["data"]["access_token"]
    doc2_token = client.post("/api/auth/login", json={"email": "doc2@example.com", "password": doc2_pass}).json()["data"]["access_token"]
    
    headers1 = {"Authorization": f"Bearer {doc1_token}"}
    headers2 = {"Authorization": f"Bearer {doc2_token}"}

    # 3. Doctor 1 registers a patient
    patient_payload = {
        "first_name": "Shared",
        "last_name": "Patient",
        "sex": "Male",
        "date_of_birth": "1990-01-01",
        "phone_number": "1234567890",
        "next_of_kin_number": "0987654321",
        "date_of_diagnosis": "2020-01-01",
        "diabetes_type": "Type 1",
        "traditional_authority": "TA",
        "village": "Village",
        "region": "Central",
        "district": "Lilongwe"
    }
    client.post("/api/doctor/patients", json=patient_payload, headers=headers1)
    
    # Get patient ID
    patients = client.get("/api/doctor/patients", headers=headers1).json()["data"]
    patient_id = patients[0]["patient_id"]

    # 4. Doctor 2 attempts to access Doctor 1's patient
    # View
    view_response = client.get(f"/api/doctor/patients/{patient_id}", headers=headers2)
    assert view_response.status_code == 200
    assert view_response.json()["data"]["first_name"] == "Shared"

    # Search
    search_response = client.get("/api/doctor/patients/search?name=Shared", headers=headers2)
    assert search_response.status_code == 200
    assert len(search_response.json()["data"]) > 0

    # Update
    update_payload = {"first_name": "Shared Updated"}
    update_response = client.put(f"/api/doctor/patients/{patient_id}", json=update_payload, headers=headers2)
    assert update_response.status_code == 200

    # Assess
    assessment_payload = {
        "patient_id": patient_id,
        "age": 30,
        "sex": "Male",
        "weight": 70.0,
        "height": 170.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "fasting_blood_glucose": 5.5,
        "ldl_cholesterol": 100.0,
        "hdl_cholesterol": 50.0,
        "triglycerides": 150.0,
        "heart_rate": 72,
        "smoking_history": "never",
        "physical_activity": "active",
        "assessment_year": today.year,
        "assessment_month": today.month,
        "assessment_day": today.day
    }
    assess_response = client.post("/api/doctor/assessments", json=assessment_payload, headers=headers2)
    assert assess_response.status_code == 201

    # View Assessment
    today = datetime.date.today()
    assess_view_response = client.get(
        f"/api/doctor/assessments/patients/{patient_id}?month={today.month}&year={today.year}",
        headers=headers2
    )
    assert assess_view_response.status_code == 200
    assert assess_view_response.json()["data"]["weight"] == 70.0

    # 5. Verify Dashboard shows global stats
    dashboard_response = client.get("/api/doctor/dashboard", headers=headers2)
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["data"]["diabetesStatistics"]["total_diabetic_patients"] >= 1
