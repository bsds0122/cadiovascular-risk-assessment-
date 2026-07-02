import pytest
from fastapi.testclient import TestClient

def test_doctor_cannot_access_admin_routes(client: TestClient):
    # 1. Setup: Register an Admin and a Doctor
    admin_payload = {
        "first_name": "Admin", "last_name": "User", "sex": "Male",
        "email": "admin.rbac@example.com", "phone": "1231231234",
        "specialization": "Admin", "experience_years": 10, "hospital": "Admin Hosp"
    }
    admin_reg = client.post("/api/admin/register", json=admin_payload).json()
    admin_token = client.post("/api/auth/login", json={
        "email": admin_reg["data"]["email"], "password": admin_reg["data"]["password"]
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    doctor_payload = {
        "email": "doc.rbac@example.com", "password": "docpassword123",
        "first_name": "Doc", "last_name": "User", "sex": "Male",
        "phone": "4321432143", "specialization": "General",
        "experience_years": 5, "hospital": "Doc Hosp", "license_number": "LIC-RBAC"
    }
    doc_reg_response = client.post("/api/admin/doctors", json=doctor_payload, headers=admin_headers)
    doc_reg_data = doc_reg_response.json()
    doc_password = doc_reg_data["data"]["password"]
    
    doc_token = client.post("/api/auth/login", json={
        "email": "doc.rbac@example.com", "password": doc_password
    }).json()["data"]["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # 2. Test: Doctor tries to access Admin profile
    response = client.get("/api/admin/profile", headers=doc_headers)
    assert response.status_code == 403
    assert "restricted" in response.json()["detail"].lower()

    # 3. Test: Doctor tries to register another doctor (Now public)
    response = client.post("/api/admin/doctors", json=doctor_payload, headers=doc_headers)
    # Since it's public, it should either succeed (201) or fail with 409 if already exists
    assert response.status_code in [201, 409]

def test_admin_cannot_access_doctor_routes(client: TestClient):
    # 1. Setup: Admin token
    admin_payload = {
        "first_name": "Admin2", "last_name": "User", "sex": "Male",
        "email": "admin2.rbac@example.com", "phone": "1231231235",
        "specialization": "Admin", "experience_years": 10, "hospital": "Admin Hosp"
    }
    admin_reg = client.post("/api/admin/register", json=admin_payload).json()
    admin_token = client.post("/api/auth/login", json={
        "email": admin_reg["data"]["email"], "password": admin_reg["data"]["password"]
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Test: Admin tries to access Doctor profile
    response = client.get("/api/doctor/profile", headers=admin_headers)
    assert response.status_code == 403

    # 3. Test: Admin tries to register a patient
    patient_payload = {
        "first_name": "Bob", "last_name": "Brown", "sex": "Male",
        "date_of_birth": "1985-05-15", "phone_number": "1122334455",
        "next_of_kin_number": "5544332211", "date_of_diagnosis": "2020-10-10",
        "diabetes_type": "Type 2", "traditional_authority": "Chulu", "village": "Zidyana"
    }
    response = client.post("/api/doctor/patients", json=patient_payload, headers=admin_headers)
    assert response.status_code == 403
