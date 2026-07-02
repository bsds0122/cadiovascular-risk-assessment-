import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io

def test_bulk_patient_registration(client: TestClient):
    # 1. Setup: Register Admin and Doctor
    admin_payload = {
        "first_name": "Bulk", "last_name": "Admin", "sex": "Male",
        "email": "bulk.admin@example.com", "phone": "1231231236",
        "specialization": "Admin", "experience_years": 10, "hospital": "Bulk Hosp"
    }
    admin_reg = client.post("/api/admin/register", json=admin_payload).json()
    admin_token = client.post("/api/auth/login", json={
        "email": admin_reg["data"]["email"], "password": admin_reg["data"]["password"]
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    doctor_payload = {
        "email": "bulk.doc@example.com", "password": "docpassword123",
        "first_name": "Bulk", "last_name": "Doc", "sex": "Male",
        "phone": "4321432144", "specialization": "General",
        "experience_years": 5, "hospital": "Bulk Hosp", "license_number": "LIC-BULK"
    }
    doc_reg = client.post("/api/admin/doctors", json=doctor_payload, headers=admin_headers).json()
    doc_password = doc_reg["data"]["password"]
    
    doc_token = client.post("/api/auth/login", json={
        "email": "bulk.doc@example.com", "password": doc_password
    }).json()["data"]["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # 2. Create Dummy Excel Data
    data = {
        "first_name": ["John", "Jane"],
        "last_name": ["Doe", "Smith"],
        "date_of_birth": ["1990-01-01", "1992-02-02"],
        "sex": ["Male", "Female"],
        "phone_number": ["0123456789", "9876543210"],
        "next_of_kin_number": ["0123456780", "9876543211"],
        "date_of_diagnosis": ["2020-01-01", "2021-01-01"],
        "diabetes_type": ["Type 1", "Type 2"],
        "region": ["Central", "Southern"],
        "district": ["Lilongwe", "Blantyre"],
        "traditional_authority": ["TA1", "TA2"],
        "village": ["Village1", "Village2"]
    }
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_file.seek(0)

    # 3. Bulk Upload
    files = {"file": ("patients.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/api/doctor/patients/bulk", files=files, headers=doc_headers)
    
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    # No data assertion here as per new API behavior for patient bulk registration

    # 4. Verify Patients exist
    patients_response = client.get("/api/doctor/patients", headers=doc_headers)
    pats = patients_response.json()["data"]
    assert len(pats) == 2
    names = [p["first_name"] for p in pats]
    assert "John" in names
    assert "Jane" in names

def test_bulk_doctor_registration(client: TestClient):
    # 1. Setup: Register Admin
    admin_payload = {
        "first_name": "BulkDoc", "last_name": "Admin", "sex": "Male",
        "email": "bulkdoc.admin@example.com", "phone": "1231231237",
        "specialization": "Admin", "experience_years": 10, "hospital": "Bulk Hosp"
    }
    admin_reg = client.post("/api/admin/register", json=admin_payload).json()
    admin_token = client.post("/api/auth/login", json={
        "email": admin_reg["data"]["email"], "password": admin_reg["data"]["password"]
    }).json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Dummy Excel Data for Doctors
    # Columns from app/routes/admin/doctors.py services
    # first_name, last_name, email, phone, specialization, experience_years, hospital, license_number, sex
    data = {
        "first_name": ["DocA", "DocB"],
        "last_name": ["One", "Two"],
        "email": ["doca@example.com", "docb@example.com"],
        "phone": ["1111111111", "2222222222"],
        "specialization": ["Cardiology", "Neurology"],
        "experience_years": [10, 15],
        "hospital": ["Hosp A", "Hosp B"],
        "license_number": ["LIC-A", "LIC-B"],
        "sex": ["Male", "Female"]
    }
    df = pd.DataFrame(data)
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_file.seek(0)

    # 3. Bulk Upload
    files = {"file": ("doctors.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/api/admin/doctors/bulk", files=files, headers=admin_headers)
    
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["data"]["successful_registrations"] == 2

    # 4. Verify Doctors exist
    docs_response = client.get("/api/admin/doctors", headers=admin_headers)
    docs = docs_response.json()["data"]
    emails = [d["email"] for d in docs]
    assert "doca@example.com" in emails
    assert "docb@example.com" in emails
