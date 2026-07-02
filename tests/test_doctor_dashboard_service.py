import pytest
from sqlalchemy.orm import Session
from app.services.doctor.dashboard import get_dashboard_data
from app.models.doctors import Doctor
from app.models.patients import Patient
from app.models.assessments import Assessment
from app.models.user import User
from datetime import date

def test_get_dashboard_data_empty(db_session: Session):
    # Create a test doctor
    user = User(email="doctor@test.com", password="hashed_password")
    db_session.add(user)
    db_session.commit()
    
    doctor = Doctor(
        user_id=user.user_id,
        first_name="John",
        last_name="Doe",
        phone="1234567890",
        specialization="Cardiology",
        experience_years=10,
        hospital="Test Hospital",
        license_number="LIC123"
    )
    db_session.add(doctor)
    db_session.commit()
    
    response = get_dashboard_data(db_session, doctor)
    
    assert response["status_code"] == 200
    assert response["data"]["greeting"] == "Welcome back, Dr. John Doe!"
    assert response["data"]["diabetesStatistics"]["total_diabetic_patients"] == 0
    assert response["data"]["patientRiskStatistics"]["total_assessed_patients"] == 0
    assert response["data"]["assessmentRiskStatistics"]["total_assessments"] == 0

def test_get_dashboard_data_with_data(db_session: Session):
    # Create a test doctor
    user = User(email="doctor2@test.com", password="hashed_password")
    db_session.add(user)
    db_session.commit()
    
    doctor = Doctor(
        user_id=user.user_id,
        first_name="Jane",
        last_name="Smith",
        phone="0987654321",
        specialization="Cardiology",
        experience_years=5,
        hospital="City Hospital",
        license_number="LIC456"
    )
    db_session.add(doctor)
    db_session.commit()
    
    # Create patients
    # Since Patient model is missing 'sex', this test will likely fail if I include 'sex'
    # But dashboard.py USES 'sex', so I must see it fail.
    
    p1 = Patient(
        doctor_id=doctor.doctor_id,
        first_name="Patient",
        last_name="One",
        sex="Male",
        phone_number="111",
        next_of_kin_number="222",
        date_of_diagnosis=date(2020, 1, 1),
        diabetes_type="Type 1",
        region="Region",
        district="District",
        traditional_authority="TA",
        village="Village"
    )
    # If I try to set p1.sex = "Male", it will fail here too because of the model.
    # But dashboard.py expects it.
    
    db_session.add(p1)
    db_session.commit()
    
    # dashboard.py will try to query Patient.sex and fail.
    response = get_dashboard_data(db_session, doctor)
    
    assert response["status_code"] == 200
    stats = response["data"]["diabetesStatistics"]
    assert stats["total_diabetic_patients"] == 1
    assert stats["male_patients"] == 1
    assert stats["female_patients"] == 0
    assert stats["type_1"]["total"] == 1
    assert stats["type_1"]["male"] == 1
    assert stats["type_1"]["percentage"] == 100.0

    # Add assessments
    a1 = Assessment(
        patient_id=p1.patient_id,
        assessment_year=2023,
        assessment_month=1,
        assessment_day=1,
        age=50,
        sex="Male",
        weight=80.0,
        height=1.75,
        systolic_bp=160,
        diastolic_bp=100,
        fasting_blood_glucose=140.0,
        ldl_cholesterol=180.0,
        hdl_cholesterol=40.0,
        triglycerides=200.0,
        total_cholesterol=250.0,
        heart_rate=80,
        smoking_history="Current Smoker",
        physical_activity="Sedentary",
        risk_percentage=25.0,
        risk_score=5.0,
        risk_category="High Risk",
        explanation=["High BP", "Smoking"],
        recommendation=["Quit smoking"]
    )
    db_session.add(a1)
    db_session.commit()
    
    response = get_dashboard_data(db_session, doctor)
    
    patient_risk = response["data"]["patientRiskStatistics"]
    assert patient_risk["total_assessed_patients"] == 1
    assert patient_risk["high_risk"]["count"] == 1
    assert patient_risk["high_risk"]["percentage"] == 100.0
    
    assessment_risk = response["data"]["assessmentRiskStatistics"]
    assert assessment_risk["total_assessments"] == 1
    assert assessment_risk["high_risk"]["count"] == 1
    assert assessment_risk["high_risk"]["percentage"] == 100.0
