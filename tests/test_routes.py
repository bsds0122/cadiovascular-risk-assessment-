import pytest
import datetime
from fastapi.testclient import TestClient

def test_complete_api_workflow(client: TestClient):
    # -------------------------------------------------------------
    # 1. Admin Registration (Public)
    # -------------------------------------------------------------
    admin_payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "sex": "Female",
        "email": "alice.admin@example.com",
        "phone": "1234567890",
        "specialization": "Clinical Management",
        "experience_years": 8,
        "hospital": "Central Health Hospital"
    }
    
    reg_response = client.post("/api/admin/register", json=admin_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["status_code"] == 201
    assert "email" in reg_data["data"]
    assert "password" in reg_data["data"]
    
    admin_email = reg_data["data"]["email"]
    admin_password = reg_data["data"]["password"]

    # -------------------------------------------------------------
    # 2. Authentication: Admin Login
    # -------------------------------------------------------------
    login_payload = {
        "email": admin_email,
        "password": admin_password
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["status_code"] == 200
    assert "access_token" in login_data["data"]
    
    admin_token = login_data["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # 3. Admin Profile (Get & Update)
    # -------------------------------------------------------------
    profile_response = client.get("/api/admin/profile", headers=admin_headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["status_code"] == 200
    assert profile_data["data"]["first_name"] == "Alice"

    update_profile_payload = {
        "first_name": "Alice Updated",
        "last_name": "Smith Updated",
        "hospital": "Central Health Hospital Clinic"
    }
    update_response = client.put("/api/admin/profile", json=update_profile_payload, headers=admin_headers)
    assert update_response.status_code == 200
    assert update_response.json()["status_code"] == 200

    profile_check = client.get("/api/admin/profile", headers=admin_headers)
    assert profile_check.json()["data"]["first_name"] == "Alice Updated"

    # -------------------------------------------------------------
    # 4. Admin Dashboard
    # -------------------------------------------------------------
    dashboard_response = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dashboard_response.status_code == 200
    assert dashboard_response.json()["status_code"] == 200

    # -------------------------------------------------------------
    # 5. Doctor Registration by Admin
    # -------------------------------------------------------------
    doctor_payload = {
        "email": "doctor.joe@example.com",
        "password": "doctorpassword123",
        "first_name": "Joe",
        "last_name": "MD",
        "sex": "Male",
        "phone": "0987654321",
        "specialization": "Endocrinology",
        "experience_years": 12,
        "hospital": "Central Health Hospital Clinic",
        "license_number": "LIC-998877"
    }
    doc_reg_response = client.post("/api/admin/doctors", json=doctor_payload, headers=admin_headers)
    assert doc_reg_response.status_code == 201
    doc_reg_data = doc_reg_response.json()
    assert doc_reg_data["status_code"] == 201
    doctor_password = doc_reg_data["data"]["password"]

    # -------------------------------------------------------------
    # 6. View Doctors (Admin perspective)
    # -------------------------------------------------------------
    view_docs_response = client.get("/api/admin/doctors", headers=admin_headers)
    assert view_docs_response.status_code == 200
    docs_list = view_docs_response.json()["data"]
    assert len(docs_list) >= 1
    
    # Extract the created doctor's ID
    doctor_id = None
    for doc in docs_list:
        if doc["email"] == "doctor.joe@example.com":
            doctor_id = doc["doctor_id"]
            break
    assert doctor_id is not None

    # Search for doctor
    search_docs_response = client.get(f"/api/admin/doctors/search?name=Joe", headers=admin_headers)
    assert search_docs_response.status_code == 200
    assert len(search_docs_response.json()["data"]) >= 1

    # Edit doctor profile (Admin perspective)
    edit_doc_payload = {
        "first_name": "Joe Registered",
        "last_name": "MD",
        "phone": "0987654321",
        "specialization": "Endocrinology & Diabetology",
        "experience_years": 13,
        "license_number": "LIC-998877"
    }
    edit_doc_response = client.put(f"/api/admin/doctors/{doctor_id}", json=edit_doc_payload, headers=admin_headers)
    assert edit_doc_response.status_code == 200

    # -------------------------------------------------------------
    # 7. Authentication: Doctor Login
    # -------------------------------------------------------------
    doc_login_payload = {
        "email": "doctor.joe@example.com",
        "password": doctor_password
    }
    doc_login_response = client.post("/api/auth/login", json=doc_login_payload)
    assert doc_login_response.status_code == 200
    doc_login_data = doc_login_response.json()
    doc_token = doc_login_data["data"]["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # -------------------------------------------------------------
    # 8. Doctor Profile (Get & Update)
    # -------------------------------------------------------------
    doc_profile_response = client.get("/api/doctor/profile", headers=doc_headers)
    assert doc_profile_response.status_code == 200
    assert doc_profile_response.json()["data"]["first_name"] == "Joe Registered"

    doc_update_payload = {
        "first_name": "Joe Doctor",
        "last_name": "MD",
        "phone": "0987654321",
        "specialization": "Endocrinology",
        "experience_years": 14,
        "license_number": "LIC-998877"
    }
    doc_update_response = client.put("/api/doctor/profile", json=doc_update_payload, headers=doc_headers)
    assert doc_update_response.status_code == 200

    # -------------------------------------------------------------
    # 9. Doctor Dashboard
    # -------------------------------------------------------------
    doc_dashboard_response = client.get("/api/doctor/dashboard", headers=doc_headers)
    assert doc_dashboard_response.status_code == 200
    assert doc_dashboard_response.json()["status_code"] == 200

    # -------------------------------------------------------------
    # 10. Patient Registration by Doctor
    # -------------------------------------------------------------
    patient_payload = {
        "first_name": "Bob",
        "last_name": "Brown",
        "sex": "Male",
        "date_of_birth": "1985-05-15",
        "phone_number": "1122334455",
        "next_of_kin_number": "5544332211",
        "date_of_diagnosis": "2020-10-10",
        "diabetes_type": "Type 2",
        "region": "Central",
        "district": "Lilongwe",
        "traditional_authority": "Chulu",
        "village": "Zidyana"
    }
    pat_reg_response = client.post("/api/doctor/patients", json=patient_payload, headers=doc_headers)
    assert pat_reg_response.status_code == 201
    
    # -------------------------------------------------------------
    # 11. View & Search Patients
    # -------------------------------------------------------------
    view_pats_response = client.get("/api/doctor/patients", headers=doc_headers)
    assert view_pats_response.status_code == 200
    pats_list = view_pats_response.json()["data"]
    assert len(pats_list) >= 1
    
    patient_id = pats_list[0]["patient_id"]

    search_pats_response = client.get("/api/doctor/patients/search?name=Bob", headers=doc_headers)
    assert search_pats_response.status_code == 200
    assert len(search_pats_response.json()["data"]) >= 1

    # Get patient profile
    pat_profile_response = client.get(f"/api/doctor/patients/{patient_id}", headers=doc_headers)
    assert pat_profile_response.status_code == 200
    assert pat_profile_response.json()["data"]["first_name"] == "Bob"

    # Edit patient profile
    edit_pat_payload = {
        "first_name": "Bobby",
        "last_name": "Brown",
        "phone_number": "1122334455",
        "next_of_kin_number": "5544332211",
        "diabetes_type": "Type 2 Diabetes",
        "traditional_authority": "Chulu",
        "village": "Zidyana"
    }
    edit_pat_response = client.put(f"/api/doctor/patients/{patient_id}", json=edit_pat_payload, headers=doc_headers)
    assert edit_pat_response.status_code == 200

    # -------------------------------------------------------------
    # 12. Cardiovascular Assessment
    # -------------------------------------------------------------
    assessment_payload = {
        "patient_id": patient_id,
        "age": 40,
        "sex": "Male",
        "weight": 78.5,
        "height": 175.0,
        "systolic_bp": 130,
        "diastolic_bp": 85,
        "fasting_blood_glucose": 6.8,
        "ldl_cholesterol": 110.0,
        "hdl_cholesterol": 55.0,
        "triglycerides": 150.0,
        "heart_rate": 72,
        "smoking_history": "former",
        "physical_activity": "moderate",
        "assessment_year": datetime.date.today().year,
        "assessment_month": datetime.date.today().month,
        "assessment_day": datetime.date.today().day
    }

    assess_response = client.post("/api/doctor/assessments", json=assessment_payload, headers=doc_headers)
    assert assess_response.status_code == 201
    assert assess_response.json()["status_code"] == 201
    # No risk_score in data as per new API behavior for assessments

    # -------------------------------------------------------------
    # 13. Patient Assessment & Monitoring Trends
    # -------------------------------------------------------------
    current_date = datetime.date.today()
    
    get_assess_response = client.get(
        f"/api/doctor/assessments/patients/{patient_id}?month={current_date.month}&year={current_date.year}",
        headers=doc_headers
    )
    assert get_assess_response.status_code == 200
    assert get_assess_response.json()["status_code"] == 200

    get_monitor_response = client.get(
        f"/api/doctor/monitoring/patients/{patient_id}/yearly?year={current_date.year}",
        headers=doc_headers
    )

    assert get_monitor_response.status_code == 200
    assert get_monitor_response.json()["status_code"] == 200

    # -------------------------------------------------------------
    # 14. Doctor Deactivation & Activation (Admin perspective)
    # -------------------------------------------------------------
    deactivate_response = client.put(f"/api/admin/doctors/{doctor_id}/deactivate", headers=admin_headers)
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["status_code"] == 200

    # Try to log in with deactivated doctor credentials -> should fail
    failed_login = client.post("/api/auth/login", json=doc_login_payload)
    assert failed_login.status_code == 403

    # Reactivate the doctor
    activate_response = client.put(f"/api/admin/doctors/{doctor_id}/activate", headers=admin_headers)
    assert activate_response.status_code == 200
    assert activate_response.json()["status_code"] == 200

    # -------------------------------------------------------------
    # 15. Delete Doctor Profile
    # -------------------------------------------------------------
    delete_response = client.delete(f"/api/admin/doctors/{doctor_id}", headers=admin_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["status_code"] == 200

    # Try to login again -> should fail with 401 Unauthorized since account is deleted
    failed_login2 = client.post("/api/auth/login", json=doc_login_payload)
    assert failed_login2.status_code == 401
