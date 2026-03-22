from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(title="MediCare Clinic API", description="Medical Appointment System")

# DATA------------------------------------------------------------------------------------------------------------------------------------------

doctors = [
    {"id": 1, "name": "Dr. Zaara Shaikh",   "specialization": "Neurologist",    "fee": 1500, "experience_years": 12, "is_available": True},
    {"id": 2, "name": "Dr. Mayank Sharma",    "specialization": "Dermatologist",   "fee": 500,  "experience_years": 7,  "is_available": True},
    {"id": 3, "name": "Dr. Rajesh Reddy",     "specialization": "Pediatrician",    "fee": 600,  "experience_years": 9,  "is_available": False},
    {"id": 4, "name": "Dr. Manoj Singh",   "specialization": "General",         "fee": 400,  "experience_years": 15, "is_available": True},
    {"id": 5, "name": "Dr. Ankita Patel",    "specialization": "Urologist",   "fee": 900,  "experience_years": 5,  "is_available": True},
    {"id": 6, "name": "Dr. Vikram Singh",   "specialization": "Cardiologist",    "fee": 1800, "experience_years": 20, "is_available": False},
    {"id": 7, "name": "Dr. Ramesh Kulkarni",  "specialization": "Pediatrician",    "fee": 700,  "experience_years": 6,  "is_available": True},
]

appointments = []
appt_counter  = 1

# PYDANTIC MODELS-------------------------------------------------------------------------------------------------------------------------

class AppointmentRequest(BaseModel):
    patient_name:       str  = Field(..., min_length=2,  description="Patient full name")
    doctor_id:          int  = Field(..., gt=0,          description="Doctor ID")
    date:               str  = Field(..., min_length=8,  description="Appointment date e.g. 2025-06-15")
    reason:             str  = Field(..., min_length=5,  description="Reason for visit")
    appointment_type:   str  = Field("in-person",        description="in-person / video / emergency")
    senior_citizen:     bool = Field(False,              description="Is the patient a senior citizen?")

class NewDoctor(BaseModel):
    name:             str  = Field(..., min_length=2)
    specialization:   str  = Field(..., min_length=2)
    fee:              int  = Field(..., gt=0)
    experience_years: int  = Field(..., gt=0)
    is_available:     bool = Field(True)

# HELPER FUNCTIONS------------------------------------------------------------------------------------------------------------------------

def find_doctor(doctor_id: int):
    """Return doctor dict if found, else None."""
    return next((d for d in doctors if d["id"] == doctor_id), None)


def find_appointment(appointment_id: int):
    """Return appointment dict if found, else None."""
    return next((a for a in appointments if a["appointment_id"] == appointment_id), None)


def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool) -> dict:
    """
    Q7 + Q9: Calculate consultation fee.
    - video      -> 80% of base fee
    - in-person  -> 100% of base fee
    - emergency  -> 150% of base fee
    Then if senior_citizen -> extra 15% discount on result.
    """
    type_map   = {"video": 0.80, "in-person": 1.00, "emergency": 1.50}
    multiplier = type_map.get(appointment_type.lower(), 1.00)
    after_type = int(base_fee * multiplier)

    if senior_citizen:
        discount  = int(after_type * 0.15)
        final_fee = after_type - discount
        return {
            "original_fee":base_fee,
            "after_type_adjustment":after_type,
            "senior_discount_15pct":discount,
            "final_fee":final_fee,
        }
    return {
        "original_fee":base_fee,
        "after_type_adjustment":after_type,
        "senior_discount_15pct":0,
        "final_fee":after_type,
    }


def filter_doctors_logic(result: list, specialization: Optional[str], max_fee: Optional[int],min_experience: Optional[int],
 is_available: Optional[bool],) -> list:

    """Q10: Apply optional filters with is not None checks."""
    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result

# Q1 — HOME ROUTE------------------------------------------------------------------------------------------------------------------------

@app.get("/", tags=["General"])
def home():
    return {"message": "Welcome to MediCare Clinic"}

# DOCTORS
# Route order: all fixed routes BEFORE /{doctor_id}

# Q2 — List all doctors------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors", tags=["Doctors"])
def get_all_doctors():
    available_count = len([d for d in doctors if d["is_available"]])
    return {
        "doctors":doctors,
        "total":len(doctors),
        "available_count":available_count,
    }


# Q5 — Summary------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/summary", tags=["Doctors"])
def doctors_summary():
    available = [d for d in doctors if d["is_available"]]
    most_experienced = max(doctors, key=lambda d: d["experience_years"])
    cheapest = min(doctors, key=lambda d: d["fee"])
    spec_count: dict = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1
    return {
        "total_doctors": len(doctors),
        "available_count": len(available),
        "most_experienced": {"name": most_experienced["name"], "years": most_experienced["experience_years"]},
        "cheapest_fee": {"name": cheapest["name"], "fee": cheapest["fee"]},
        "by_specialization": spec_count,
    }


# Q10 — Filter------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/filter", tags=["Doctors"])
def filter_doctors(
    specialization: Optional[str] = Query(None, description="e.g. Cardiologist / Dermatologist / Pediatrician / General"),
    max_fee: Optional[int] = Query(None, description="Maximum consultation fee"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    is_available: Optional[bool] = Query(None, description="True = available only"),
):
    result = filter_doctors_logic(list(doctors), specialization, max_fee, min_experience, is_available)
    return {
        "filters_applied": {
            "specialization": specialization,
            "max_fee":        max_fee,
            "min_experience": min_experience,
            "is_available":   is_available,
        },
        "count":   len(result),
        "doctors": result,
    }


# Q16 — Search------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/search", tags=["Doctors"])
def search_doctors(keyword: str = Query(..., description="Search by name or specialization")):
    results = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]
    if not results:
        return {"message": f"No doctors found matching '{keyword}'. Please try a different keyword."}
    return {"keyword": keyword, "total_found": len(results), "doctors": results}


# Q17 — Sort------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/sort", tags=["Doctors"])
def sort_doctors(
    sort_by: str = Query("fee", description="fee | name | experience_years"),
    order: str = Query("asc", description="asc | desc"),
):
    allowed_sort = ["fee", "name", "experience_years"]
    if sort_by not in allowed_sort:
        return {"error": f"sort_by must be one of {allowed_sort}"}
    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}
    result = sorted(doctors, key=lambda d: d[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "total": len(result), "doctors": result}


# Q18 — Pagination------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/page", tags=["Doctors"])
def paginate_doctors(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(3, ge=1, le=10, description="Doctors per page"),
):
    start = (page - 1) * limit
    sliced = doctors[start: start + limit]
    total_pages = math.ceil(len(doctors) / limit)
    return {
        "page": page,
        "limit": limit,
        "total": len(doctors),
        "total_pages": total_pages,
        "doctors": sliced,
    }


# Q20 — Browse: search + filter + sort + paginate-----------------------------------------------------------------------------------------------
@app.get("/doctors/browse", tags=["Doctors"])
def browse_doctors(
    keyword: Optional[str] = Query(None, description="Search name or specialization"),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    max_fee:        Optional[int]   = Query(None, description="Filter by max fee"),
    min_experience: Optional[int]   = Query(None, description="Filter by min experience years"),
    is_available:   Optional[bool]  = Query(None, description="Filter by availability"),
    sort_by: str = Query("fee", description="fee | name | experience_years"),
    order: str = Query("asc", description="asc | desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=10),
):
    # Step 1: keyword search
    result = [
        d for d in doctors
        if not keyword
        or keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]
    # Step 2: additional filters
    result = filter_doctors_logic(result, specialization, max_fee, min_experience, is_available)
    # Step 3: sort
    allowed_sort = ["fee", "name", "experience_years"]
    if sort_by in allowed_sort:
        result = sorted(result, key=lambda d: d[sort_by], reverse=(order == "desc"))
    # Step 4: paginate
    total = len(result)
    start = (page - 1) * limit
    total_pages = math.ceil(total / limit) if total > 0 else 1
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "doctors": result[start: start + limit],
    }


# Q3 — GET doctor by ID------------------------------------------------------------------------------------------------------------------------
@app.get("/doctors/{doctor_id}", tags=["Doctors"])
def get_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}
    return {"doctor": doctor}


# Q11 — POST add new doctor--------------------------------------------------------------------------------------------------------------
@app.post("/doctors", status_code=201, tags=["Doctors"])
def add_doctor(data: NewDoctor, response: Response):
    for d in doctors:
        if d["name"].lower() == data.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": f"Doctor '{data.name}' already exists"}
    new_id     = max(d["id"] for d in doctors) + 1
    new_doctor = {
        "id": new_id,
        "name": data.name,
        "specialization": data.specialization,
        "fee": data.fee,
        "experience_years": data.experience_years,
        "is_available": data.is_available,
    }
    doctors.append(new_doctor)
    return {"message": "Doctor added successfully", "doctor": new_doctor}


# Q12 — PUT update doctor--------------------------------------------------------------------------------------------------------------
@app.put("/doctors/{doctor_id}", tags=["Doctors"])
def update_doctor(
    doctor_id: int,
    response: Response,
    fee: Optional[int] = Query(None, description="New consultation fee"),
    is_available: Optional[bool] = Query(None, description="Availability status"),
):
    doctor = find_doctor(doctor_id)
    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}
    if fee is not None: doctor["fee"] = fee
    if is_available is not None: doctor["is_available"] = is_available
    return {"message": "Doctor updated successfully", "doctor": doctor}


# Q13 — DELETE doctor--------------------------------------------------------------------------------------------------------------
@app.delete("/doctors/{doctor_id}", tags=["Doctors"])
def delete_doctor(doctor_id: int, response: Response):
    doctor = find_doctor(doctor_id)
    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}
    active = [a for a in appointments if a["doctor_id"] == doctor_id and a["status"] == "scheduled"]
    if active:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Cannot delete '{doctor['name']}' — they have {len(active)} active scheduled appointment(s)"}
    doctors.remove(doctor)
    return {"message": f"Doctor '{doctor['name']}' deleted successfully"}


# APPOINTMENTS--------------------------------------------------------------------------------------------------------------
# Route order: all fixed routes BEFORE /{appointment_id}

# Q4 — GET all appointments-----------------------------------------------------------------------------------------------------
@app.get("/appointments", tags=["Appointments"])
def get_all_appointments():
    return {"appointments": appointments, "total": len(appointments)}


# Q15 — Active appointments--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/active", tags=["Appointments"])
def get_active_appointments():
    active = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {"active_appointments": active, "total": len(active)}


# Q19 — Search appointments by patient name--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/search", tags=["Appointments"])
def search_appointments(patient_name: str = Query(..., description="Patient name to search")):
    results = [a for a in appointments if patient_name.lower() in a["patient_name"].lower()]
    if not results:
        return {"message": f"No appointments found for '{patient_name}'"}
    return {"patient_name": patient_name, "total_found": len(results), "appointments": results}


# Q19 — Sort appointments--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/sort", tags=["Appointments"])
def sort_appointments(
    sort_by: str = Query("fee",  description="fee | date"),
    order: str = Query("asc",  description="asc | desc"),
):
    allowed = ["fee", "date"]
    if sort_by not in allowed:
        return {"error": f"sort_by must be one of {allowed}"}
    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}
    result = sorted(appointments, key=lambda a: a[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "appointments": result}


# Q19 — Paginate appointments--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/page", tags=["Appointments"])
def paginate_appointments(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10),
):
    start       = (page - 1) * limit
    total_pages = math.ceil(len(appointments) / limit) if appointments else 1
    return {
        "page": page,
        "limit": limit,
        "total": len(appointments),
        "total_pages": total_pages,
        "appointments": appointments[start: start + limit],
    }


# Q15 — Appointments by doctor--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/by-doctor/{doctor_id}", tags=["Appointments"])
def appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}
    result = [a for a in appointments if a["doctor_id"] == doctor_id]
    return {"doctor": doctor["name"], "total": len(result), "appointments": result}


# Q8 — POST book appointment--------------------------------------------------------------------------------------------------------------
@app.post("/appointments", status_code=201, tags=["Appointments"])
def book_appointment(data: AppointmentRequest, response: Response):
    global appt_counter

    # Q6: Pydantic already validates patient_name, doctor_id, date, reason, appointment_type-------------------------------------------------
    doctor = find_doctor(data.doctor_id)
    if not doctor:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Doctor not found"}
    if not doctor["is_available"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Dr. {doctor['name']} is currently not available. Please choose another doctor."}
    allowed_types = ["in-person", "video", "emergency"]
    if data.appointment_type.lower() not in allowed_types:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"appointment_type must be one of {allowed_types}"}

    # Q7 + Q9: calculate fee with type adjustment and senior citizen discount---------------------------------------------------------------
    fee_info = calculate_fee(doctor["fee"], data.appointment_type, data.senior_citizen)
    new_appt = {
        "appointment_id": appt_counter,
        "patient_name": data.patient_name,
        "doctor_id": data.doctor_id,
        "doctor_name": doctor["name"],
        "specialization": doctor["specialization"],
        "date": data.date,
        "reason": data.reason,
        "appointment_type": data.appointment_type,
        "senior_citizen": data.senior_citizen,
        "fee": fee_info["final_fee"],
        "fee_breakdown": fee_info,
        "status": "scheduled",
    }
    appointments.append(new_appt)
    appt_counter += 1
    return {"message": "Appointment booked successfully", "appointment": new_appt}


# Q14 — Confirm appointment--------------------------------------------------------------------------------------------------------------
@app.post("/appointments/{appointment_id}/confirm", tags=["Appointments"])
def confirm_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)
    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}
    appt["status"] = "confirmed"
    return {"message": "Appointment confirmed successfully", "appointment": appt}


# Q14 — Cancel appointment--------------------------------------------------------------------------------------------------------------
@app.post("/appointments/{appointment_id}/cancel", tags=["Appointments"])
def cancel_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)
    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}
    appt["status"] = "cancelled"
    doctor = find_doctor(appt["doctor_id"])
    if doctor:
        doctor["is_available"] = True
    return {"message": "Appointment cancelled. Doctor is now available again.", "appointment": appt}


# Q15 — Complete appointment--------------------------------------------------------------------------------------------------------------
@app.post("/appointments/{appointment_id}/complete", tags=["Appointments"])
def complete_appointment(appointment_id: int, response: Response):
    appt = find_appointment(appointment_id)
    if not appt:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Appointment not found"}
    appt["status"] = "completed"
    return {"message": "Appointment marked as completed", "appointment": appt}


# GET by ID--------------------------------------------------------------------------------------------------------------
@app.get("/appointments/{appointment_id}", tags=["Appointments"])
def get_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        return {"error": "Appointment not found"}
    return {"appointment": appt}
