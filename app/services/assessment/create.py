import httpx
from datetime import date
from sqlalchemy.orm import Session

from app.models.assessments import Assessment
from app.models.patients import Patient

MODEL_URL ="https://model-2-t8ad.onrender.com/predict"


# ==========================================================
# CREATE ASSESSMENT SERVICE (FULL LOGIC)
# ==========================================================
async def assess_patient(db: Session, assessment_data):

   
    # ------------------------------------------------------
    # 3. CALCULATE BMI
    # ------------------------------------------------------
    height_m = assessment_data.height / 100
    bmi = round(assessment_data.weight / (height_m ** 2), 2)

    # ------------------------------------------------------
    # 4. CALCULATE TOTAL CHOLESTEROL
    #    (Friedewald approximation)
    # ------------------------------------------------------
    total_chol = (
        assessment_data.ldl_cholesterol
        + assessment_data.hdl_cholesterol
        + (assessment_data.triglycerides / 5)
    )
    total_chol = round(total_chol, 2)

    # ------------------------------------------------------
    # 5. CONVERT GLUCOSE (mmol/L → mg/dL)
    # ------------------------------------------------------
    glucose = round(assessment_data.fasting_blood_glucose * 18, 2)

    # ------------------------------------------------------
    # 6. PREPARE ML PAYLOAD
    # ------------------------------------------------------
    payload = {
        "sex": assessment_data.sex,
        "age": assessment_data.age,
        "cigsPerDay": assessment_data.cigs_per_day,
        "totChol": total_chol,
        "sysBP": assessment_data.systolic_bp,
        "diaBP": assessment_data.diastolic_bp,
        "BMI": bmi,
        "heartRate": assessment_data.heart_rate,
        "glucose": glucose,
    }

    # ------------------------------------------------------
    # 7. CALL ML MODEL
    # ------------------------------------------------------
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MODEL_URL, json=payload)
            response.raise_for_status()
            result = response.json()

    except httpx.RequestError as e:
        return {
            "status_code": 500,
            "details": f"Model request failed: {str(e)}",
            "data": None,
        }

    except httpx.HTTPStatusError as e:
        return {
            "status_code": 500,
            "details": f"Model returned error: {str(e)}",
            "data": None,
        }

    # ------------------------------------------------------
    # 8. SAVE TO DATABASE
    # ------------------------------------------------------
    assessment = Assessment(
        patient_id=assessment_data.patient_id,

        assessment_year=assessment_data.assessment_year,
        assessment_month=assessment_data.assessment_month,
        assessment_day=assessment_data.assessment_day,

    
        systolic_bp=assessment_data.systolic_bp,
        diastolic_bp=assessment_data.diastolic_bp,
        glucose = assessment_data.fasting_blood_glucose,
       
        # model outputs
        risk_level=result.get("diagnosis", "Unknown"),
        risk_percentage=result.get("probability", 0.0) * 100,
        feature_importance=result.get("feature_importance", []),
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # ------------------------------------------------------
    # 9. RESPONSE
    # ------------------------------------------------------
    return {
        "status_code": 201,
        "details": "Assessment created successfully",
        "data": {
            # MODEL OUTPUT
            "risk_level": assessment.risk_level,
            "risk_percentage": assessment.risk_percentage,
            "feature_importance": assessment.feature_importance,
        },
    }