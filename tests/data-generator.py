import random
import pandas as pd
from datetime import datetime

from app.services.assessment.cardiovascular_risk_engine import cardiovascular_risk_score

# -----------------------------------------------------
# IMPORT YOUR SCORING FUNCTION HERE
# -----------------------------------------------------
# from your_module import cardiovascular_risk_score


# -----------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)


def generate_base_patient(patient_id, risk_group):
    """
    risk_group:
    1 = low risk
    2 = moderate risk
    3 = high risk
    """

    if risk_group == 1:
        age = random.randint(18, 45)
        weight = random.randint(55, 75)
        height = random.uniform(1.55, 1.80)
        smoking = "never"
        activity = "high"

        base = {
            "age": age,
            "sex": random.choice(["male", "female"]),
            "weight": weight,
            "height": round(height, 2),
            "systolic_bp": random.randint(100, 125),
            "diastolic_bp": random.randint(65, 80),
            "fasting_blood_glucose": round(random.uniform(4.2, 5.5), 1),
            "ldl_cholesterol": round(random.uniform(1.5, 2.5), 1),
            "hdl_cholesterol": round(random.uniform(1.4, 2.0), 1),
            "triglycerides": round(random.uniform(0.7, 1.6), 1),
            "heart_rate": random.randint(60, 85),
            "smoking_history": smoking,
            "physical_activity": activity
        }

    elif risk_group == 2:
        age = random.randint(40, 60)
        weight = random.randint(65, 90)
        height = random.uniform(1.55, 1.80)
        smoking = random.choice(["never", "former"])
        activity = "moderate"

        base = {
            "age": age,
            "sex": random.choice(["male", "female"]),
            "weight": weight,
            "height": round(height, 2),
            "systolic_bp": random.randint(125, 145),
            "diastolic_bp": random.randint(80, 95),
            "fasting_blood_glucose": round(random.uniform(5.5, 7.0), 1),
            "ldl_cholesterol": round(random.uniform(2.6, 4.0), 1),
            "hdl_cholesterol": round(random.uniform(1.0, 1.5), 1),
            "triglycerides": round(random.uniform(1.5, 2.2), 1),
            "heart_rate": random.randint(65, 95),
            "smoking_history": smoking,
            "physical_activity": activity
        }

    else:
        age = random.randint(55, 80)
        weight = random.randint(80, 120)
        height = random.uniform(1.50, 1.75)
        smoking = "current"
        activity = "low"

        base = {
            "age": age,
            "sex": "male",
            "weight": weight,
            "height": round(height, 2),
            "systolic_bp": random.randint(145, 180),
            "diastolic_bp": random.randint(90, 110),
            "fasting_blood_glucose": round(random.uniform(7.0, 12.0), 1),
            "ldl_cholesterol": round(random.uniform(3.5, 6.0), 1),
            "hdl_cholesterol": round(random.uniform(0.7, 1.2), 1),
            "triglycerides": round(random.uniform(2.2, 4.5), 1),
            "heart_rate": random.randint(85, 110),
            "smoking_history": smoking,
            "physical_activity": activity
        }

    base["patient_id"] = patient_id
    return base


# -----------------------------------------------------
# MONTHLY VARIATION FUNCTION
# -----------------------------------------------------
def apply_monthly_change(data, trend):
    """
    trend:
    -1 = improving
     0 = stable
     1 = worsening
    """

    def adjust(value, percent):
        return value + (value * percent)

    # small realistic changes
    if trend == -1:
        data["weight"] -= random.uniform(0.2, 1.0)
        data["systolic_bp"] -= random.randint(0, 3)
        data["diastolic_bp"] -= random.randint(0, 2)
        data["fasting_blood_glucose"] -= round(random.uniform(0.0, 0.2), 1)

    elif trend == 1:
        data["weight"] += random.uniform(0.2, 1.0)
        data["systolic_bp"] += random.randint(0, 4)
        data["diastolic_bp"] += random.randint(0, 3)
        data["fasting_blood_glucose"] += round(random.uniform(0.0, 0.3), 1)

    # recompute BMI
    data["bmi"] = calculate_bmi(data["weight"], data["height"])

    return data


# -----------------------------------------------------
# MAIN GENERATION
# -----------------------------------------------------
records = []

months = list(range(1, 13))

for patient_id in range(1, 101):

    risk_group = random.choices([1, 2, 3], weights=[0.4, 0.35, 0.25])[0]

    base_patient = generate_base_patient(patient_id, risk_group)

    trend = random.choice([-1, 0, 1])  # improving/stable/worsening

    for month in months:

        patient_month = base_patient.copy()
        patient_month = apply_monthly_change(patient_month, trend)

        # add month info
        patient_month["assessment_year"] = 2026
        patient_month["assessment_month"] = month
        patient_month["assessment_day"] = random.randint(1, 28)

        # ensure BMI exists
        patient_month["bmi"] = calculate_bmi(
            patient_month["weight"],
            patient_month["height"]
        )

        # REMOVE weight/height if you don't want them stored
        # (optional depending on your DB design)

        # SCORE SYSTEM CALL
        result = cardiovascular_risk_score(patient_month)

        patient_month["risk_score"] = result["risk_score"]
        patient_month["risk_percentage"] = result["risk_percentage"]
        patient_month["risk_category"] = result["risk_category"]

        records.append(patient_month)


# -----------------------------------------------------
# SAVE TO CSV
# -----------------------------------------------------
df = pd.DataFrame(records)
df.to_csv("cardiovascular_assessments.csv", index=False)

print("Generated:", len(records), "records")
print("Saved to cardiovascular_assessments.csv")