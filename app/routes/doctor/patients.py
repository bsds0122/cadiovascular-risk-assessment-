from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.patient.register import PatientRegister
from app.schemas.patient.update import PatientUpdate
from app.schemas.response import APIResponse

from app.services.patient.register import register_patient
from app.services.patient.register_excel import register_patients_excel
from app.services.patient.view import (
    get_all_patients,
    get_patient_by_id,
    search_patients,
    autocomplete_patients,update_patient
)


from app.utils.get_current_doctor import get_current_doctor_user



# ==========================================================
# DOCTOR PATIENT MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/patients",
    tags=["Doctor - Patient Management"],
)





# ==========================================================
# PATIENT REGISTRATION ENDPOINT
# ==========================================================
import os
import uuid
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    status,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.patient.register import PatientRegister
from app.schemas.response import APIResponse
from app.services.patient.register import register_patient
from app.utils.get_current_doctor import get_current_doctor_user

router = APIRouter(
    prefix="/patients",
    tags=["Doctor - Patient Management"],
)

UPLOAD_DIR = "uploads/patients"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==========================================================
# REGISTER A NEW PATIENT
# ==========================================================
@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    # ======================================================
    # FORM DATA
    # ======================================================
    first_name: str = Form(...),
    last_name: str = Form(...),
    sex: str = Form(...),

    phone_number: str = Form(...),
    next_of_kin_number: str = Form(...),

    date_of_diagnosis: date = Form(...),
    diabetes_type: str = Form(...),

    region: str = Form(...),
    district: str = Form(...),
    traditional_authority: str = Form(...),
    village: str = Form(...),

    # ======================================================
    # FILE UPLOAD
    # ======================================================
    profile_image: UploadFile = File(None),

    # ======================================================
    # DEPENDENCIES
    # ======================================================
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Register a new patient under a doctor.

    Supports:
    - FormData submission
    - Optional image upload
    - Schema validation
    """

    # ======================================================
    # HANDLE IMAGE UPLOAD
    # ======================================================
    file_path = None

    if profile_image:
        file_ext = profile_image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(profile_image.file.read())

    # ======================================================
    # VALIDATE USING SCHEMA
    # ======================================================
    patient_schema = PatientRegister(
        first_name=first_name,
        last_name=last_name,
        sex=sex,
        phone_number=phone_number,
        next_of_kin_number=next_of_kin_number,
        date_of_diagnosis=date_of_diagnosis,
        diabetes_type=diabetes_type,
        region=region,
        district=district,
        traditional_authority=traditional_authority,
        village=village,
        profile_image=file_path,
    )

    # ======================================================
    # CALL SERVICE LAYER
    # ======================================================
    result = register_patient(
        db=db,
        patient_data=patient_schema,
        doctor_id=doctor_id,
    )

    # ======================================================
    # RETURN RESPONSE
    # ======================================================
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
 
    )





# ==========================================================
# REGISTER MULTIPLE PATIENTS USING AN EXCEL FILE
# ==========================================================
@router.post(
    "/bulk",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patients_bulk(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    doctor_id: int = Depends( get_current_doctor_user),
):
    """
    Upload an Excel file and register multiple patients at once.
    """

    # ------------------------------------------------------
    # Process Excel file and create patient records in bulk
    # ------------------------------------------------------
    results = register_patients_excel(
        db=db,
        file=file,
        doctor_id=doctor_id,
    )

    # ------------------------------------------------------
    # Return bulk registration processing results
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# RETRIEVE ALL REGISTERED PATIENTS WITH PAGINATION
# ==========================================================
@router.get(
    "",
    response_model=APIResponse,
)
def view_patients(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    doctor_id: int = Depends( get_current_doctor_user),
):
    """
    Retrieve a paginated list of patients assigned to the doctor.
    """

    # ------------------------------------------------------
    # Fetch patient records using pagination parameters
    # ------------------------------------------------------
    results = get_all_patients(
        db=db,
        skip=skip,
        limit=limit,
    )

    # ------------------------------------------------------
    # Return patient list and pagination information
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# SEARCH PATIENTS BY NAME
# ==========================================================
@router.get(
    "/search",
    response_model=APIResponse,
)
def search_for_patients(
    name: str,
    db: Session = Depends(get_db),
    doctor_id: int = Depends( get_current_doctor_user),
):
    """
    Search for patients using their name.
    """

    # ------------------------------------------------------
    # Find matching patients belonging to the doctor
    # ------------------------------------------------------
    results = search_patients(
        db=db,
        name=name,
       
    )

    # ------------------------------------------------------
    # Return matching patient records
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# AUTOCOMPLETE PATIENTS
# ==========================================================
@router.get(
    "/autocomplete",
    response_model=APIResponse,
)
def autocomplete_patient_names(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    doctor_id: int = Depends( get_current_doctor_user),
):
    """
    Autocomplete patient names for search suggestions.
    """

    # ------------------------------------------------------
    # Fetch suggestions for the given query
    # ------------------------------------------------------
    results = autocomplete_patients(
        db=db,
        query=query,
        limit=limit,
    )

    # ------------------------------------------------------
    # Return autocomplete suggestions
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# RETRIEVE A SINGLE PATIENT PROFILE
# ==========================================================
@router.get(
    "/{patient_id}",
    response_model=APIResponse,
)
def get_patient_profile(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor_id: int = Depends( get_current_doctor_user),
):
    """
    Retrieve detailed information for a specific patient.
    """

    # ------------------------------------------------------
    # Fetch patient profile using the patient identifier
    # ------------------------------------------------------
    results = get_patient_by_id(
        db=db,
        patient_id=patient_id,
      
    )

    # ------------------------------------------------------
    # Return patient profile information
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )

# ==========================================================
# UPDATE PATIENT INFORMATION
# ==========================================================
@router.put(
    "/{patient_id}",
    response_model=APIResponse,
)
def edit_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Update an existing patient's information.
    Only the doctor who registered the patient can edit.
    """

    results = update_patient(
        db=db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        update_data=patient_data.model_dump(exclude_unset=True),
    )

    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )