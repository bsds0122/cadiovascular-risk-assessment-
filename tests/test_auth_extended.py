import pytest
from fastapi.testclient import TestClient

def test_logout(client: TestClient):
    # 1. Register and Login Admin
    admin_payload = {
        "first_name": "Logout",
        "last_name": "Test",
        "sex": "Male",
        "email": "logout.test@example.com",
        "phone": "9998887776",
        "specialization": "Testing",
        "experience_years": 5,
        "hospital": "Test Hospital"
    }
    reg_response = client.post("/api/admin/register", json=admin_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    
    login_payload = {
        "email": reg_data["data"]["email"],
        "password": reg_data["data"]["password"]
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Logout
    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["status"] == "success"

    # 3. Verify logout (though if it's stateless JWT, this might depend on implementation)
    # Looking at the code, it uses blacklist service.
    profile_response = client.get("/api/admin/profile", headers=headers)
    # If logout blacklists the token, this should fail.
    assert profile_response.status_code == 401

def test_password_reset(client: TestClient):
    # 1. Register Admin
    admin_payload = {
        "first_name": "Pass",
        "last_name": "Reset",
        "sex": "Female",
        "email": "pass.reset@example.com",
        "phone": "1112223334",
        "specialization": "Testing",
        "experience_years": 5,
        "hospital": "Test Hospital"
    }
    reg_response = client.post("/api/admin/register", json=admin_payload)
    admin_email = reg_response.json()["data"]["email"]
    old_password = reg_response.json()["data"]["password"]

    # 2. Reset Password
    reset_payload = {
        "email": admin_email,
        "new_password": "newpassword123"
    }
    reset_response = client.put("/api/auth/password", json=reset_payload)
    assert reset_response.status_code == 200

    # 3. Try login with old password (should fail)
    login_payload_old = {"email": admin_email, "password": old_password}
    login_response_old = client.post("/api/auth/login", json=login_payload_old)
    assert login_response_old.status_code == 401

    # 4. Try login with new password (should succeed)
    login_payload_new = {"email": admin_email, "password": "newpassword123"}
    login_response_new = client.post("/api/auth/login", json=login_payload_new)
    assert login_response_new.status_code == 200
