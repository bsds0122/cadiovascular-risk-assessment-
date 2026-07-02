import pytest
from fastapi.testclient import TestClient
from app.core.database import SessionLocal, Base, engine
from main import app

client = TestClient(app)

def test_autocomplete_patients(client: TestClient):
    # -------------------------------------------------------------
    # 1. Admin Registration (Public)
    # -------------------------------------------------------------
    admin_payload = {
        "first_name": "Autocomplete",
        "last_name": "Admin",
        "sex": "Female",
        "email": "auto.admin@example.com",
        "phone": "9876543210",
        "specialization": "Clinical Management",
        "experience_years": 5,
        "hospital": "Autocomplete Hospital"
    }
    
    reg_response = client.post("/api/admin/register", json=admin_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    
    admin_email = reg_data["data"]["email"]
    admin_password = reg_data["data"]["password"]

    # -------------------------------------------------------------
    # 2. Authentication: Admin Login
    # -------------------------------------------------------------
    login_payload = {"email": admin_email, "password": admin_password}
    login_response = client.post("/api/auth/login", json=login_payload)
    admin_token = login_response.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # 3. Doctor Registration by Admin
    # -------------------------------------------------------------
    doctor_payload = {
        "email": "auto.doc@example.com",
        "password": "password123",
        "first_name": "Auto",
        "last_name": "Doc",
        "sex": "Male",
        "phone": "0123456789",
        "specialization": "General",
        "experience_years": 10,
        "hospital": "Autocomplete Hospital",
        "license_number": "LIC-AUTO"
    }
    doc_reg_response = client.post("/api/admin/doctors", json=doctor_payload, headers=admin_headers)
    doctor_password = doc_reg_response.json()["data"]["password"]

    # -------------------------------------------------------------
    # 4. Authentication: Doctor Login
    # -------------------------------------------------------------
    doc_login_payload = {"email": "auto.doc@example.com", "password": doctor_password}
    doc_login_response = client.post("/api/auth/login", json=doc_login_payload)
    doc_token = doc_login_response.json()["data"]["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # -------------------------------------------------------------
    # 5. Patient Registration by Doctor
    # -------------------------------------------------------------
    patient_payload = {
        "first_name": "Johnathan",
        "last_name": "Doe",
        "sex": "Male",
        "date_of_birth": "1990-01-01",
        "phone_number": "1112223333",
        "next_of_kin_number": "4445556666",
        "date_of_diagnosis": "2021-01-01",
        "diabetes_type": "Type 1",
        "region": "Central",
        "district": "Lilongwe",
        "traditional_authority": "T1",
        "village": "V1"
    }
    client.post("/api/doctor/patients", json=patient_payload, headers=doc_headers)

    # -------------------------------------------------------------
    # 6. Test Autocomplete
    # -------------------------------------------------------------
    autocomplete_response = client.get("/api/doctor/patients/autocomplete?query=John", headers=doc_headers)
    assert autocomplete_response.status_code == 200
    autocomplete_data = autocomplete_response.json()
    assert autocomplete_data["status_code"] == 200
    assert len(autocomplete_data["data"]) >= 1
    assert "Johnathan Doe" in autocomplete_data["data"][0]["label"]
