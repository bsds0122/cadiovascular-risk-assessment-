from pydantic import BaseModel, Field, field_validator, model_validator


class AssessmentCreate(BaseModel):

    # ======================================================
    # ASSESSMENT INFORMATION
    # ======================================================
    patient_id: int = Field(..., ge=1)

    assessment_day: int = Field(..., ge=1, le=31)
    assessment_month: int = Field(..., ge=1, le=12)
    assessment_year: int = Field(..., ge=2000, le=2100)

    # ======================================================
    # DEMOGRAPHICS (ADDED)
    # ======================================================
    sex: int = Field(..., ge=0, le=1, description="0 = Female, 1 = Male")
    age: int = Field(..., ge=1, le=120)

    # ======================================================
    # CLINICAL VITALS
    # ======================================================
    weight: float = Field(..., ge=20, le=300, description="Weight in kg")
    height: float = Field(..., ge=50, le=250, description="Height in cm")

    heart_rate: int = Field(..., ge=30, le=220)

    systolic_bp: float = Field(..., ge=70, le=250)
    diastolic_bp: float = Field(..., ge=40, le=150)

    cigs_per_day: int = Field(..., ge=0, le=100)

    # ======================================================
    # LABORATORY RESULTS
    # ======================================================
    fasting_blood_glucose: float = Field(..., ge=2.0, le=40.0)

    ldl_cholesterol: float = Field(..., ge=20, le=400)
    hdl_cholesterol: float = Field(..., ge=10, le=150)
    triglycerides: float = Field(..., ge=20, le=1000)

    # ======================================================
    # VALIDATIONS
    # ======================================================

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v):
        if not (20 <= v <= 300):
            raise ValueError("Weight must be between 20 and 300 kg.")
        return v

    @field_validator("height")
    @classmethod
    def validate_height(cls, v):
        if not (50 <= v <= 250):
            raise ValueError("Height must be between 50 and 250 cm.")
        return v

    @field_validator("heart_rate")
    @classmethod
    def validate_heart_rate(cls, v):
        if not (30 <= v <= 220):
            raise ValueError("Heart rate must be between 30 and 220 bpm.")
        return v

    @field_validator("fasting_blood_glucose")
    @classmethod
    def validate_glucose(cls, v):
        if not (2.0 <= v <= 40.0):
            raise ValueError("Fasting blood glucose must be between 2.0 and 40.0 mmol/L.")
        return v

    @model_validator(mode="after")
    def validate_bp(self):
        if self.systolic_bp <= self.diastolic_bp:
            raise ValueError("Systolic BP must be greater than Diastolic BP.")
        return self