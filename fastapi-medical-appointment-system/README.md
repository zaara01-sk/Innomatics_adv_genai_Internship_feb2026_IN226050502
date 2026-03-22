# 🏥 MediCare Clinic — FastAPI Medical Appointment System

A fully functional **REST API backend** built with **FastAPI** as the Final Project for the Innomatics Research Labs FastAPI Internship.  
This project simulates a real-world medical clinic system where doctors can be managed and patients can book, confirm, cancel, and complete appointments.

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fastapi-medical-appointment-system
cd fastapi-medical-appointment-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Open Swagger UI to test all endpoints
```
http://127.0.0.1:8000/docs
```

---

## 📋 Project Overview

| Detail | Info |
|--------|------|
| **Project** | Medical Appointment System |
| **Framework** | FastAPI |
| **Language** | Python 3.10+ |
| **Total Endpoints** | 20 |
| **Concepts Covered** | Day 1 – Day 6 |

### Data Models
- **Doctors** — id, name, specialization, fee, experience_years, is_available
- **Appointments** — appointment_id, patient_name, doctor, date, reason, type, fee breakdown, status

---

## ✅ API Endpoints (All 20 Questions)

### 📗 Day 1 — GET APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome home route |
| GET | `/doctors` | List all doctors with total + available count |
| GET | `/doctors/{doctor_id}` | Get doctor by ID (error if not found) |
| GET | `/appointments` | List all appointments with total |
| GET | `/doctors/summary` | Most experienced, cheapest fee, count per specialization |

### 📘 Day 2 — POST + Pydantic Validation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments` | Book appointment with full Pydantic validation |

**AppointmentRequest fields:**
- `patient_name` — min_length 2
- `doctor_id` — gt 0
- `date` — min_length 8
- `reason` — min_length 5
- `appointment_type` — default `in-person`
- `senior_citizen` — default `False`

### 📙 Day 3 — Helper Functions + Filter
**Plain helper functions (no @app decorator):**
- `find_doctor(doctor_id)` — returns doctor dict or None
- `find_appointment(appointment_id)` — returns appointment dict or None
- `calculate_fee(base_fee, appointment_type, senior_citizen)` — video: 80%, in-person: 100%, emergency: 150%, senior citizen: extra 15% off
- `filter_doctors_logic(...)` — applies all filters using `is not None` checks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors/filter` | Filter by specialization, max_fee, min_experience, is_available |

### 📒 Day 4 — CRUD Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/doctors` | Add new doctor — rejects duplicates, returns 201 |
| PUT | `/doctors/{doctor_id}` | Update fee or availability — 404 if not found |
| DELETE | `/doctors/{doctor_id}` | Delete doctor — blocked if active scheduled appointments exist |

### 📕 Day 5 — Multi-Step Workflow
**Booking → Confirm → Cancel / Complete**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appointments/{id}/confirm` | Change status to `confirmed` |
| POST | `/appointments/{id}/cancel` | Change status to `cancelled`, re-enables doctor |
| POST | `/appointments/{id}/complete` | Change status to `completed` |
| GET | `/appointments/active` | Returns only scheduled/confirmed appointments |
| GET | `/appointments/by-doctor/{doctor_id}` | All appointments for a specific doctor |

### 📓 Day 6 — Search, Sort & Pagination
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors/search` | Search by name or specialization (case-insensitive) |
| GET | `/doctors/sort` | Sort by fee, name, or experience_years (asc/desc) |
| GET | `/doctors/page` | Paginate doctors — returns total_pages |
| GET | `/appointments/search` | Search appointments by patient name |
| GET | `/appointments/sort` | Sort appointments by fee or date |
| GET | `/appointments/page` | Paginate appointments |
| GET | `/doctors/browse` | Combined: keyword search + filter + sort + pagination |

---

## 📁 Project Structure

```
fastapi-medical-appointment-system/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
    ├── Q1_home_route.png
    ├── Q2_get_all_doctors.png
    ├── Q3_get_doctor_by_id_1.png
    ├── Q3_get_doctor_by_id_2.png
    ├── Q4_get_all_appointments.png
    ├── Q5_doctors_summary.png
    ├── Q6_pydantic_validation.png
    ├── Q7_helper_functions.png
    ├── Q8_post_appointment.png
    ├── Q9_senior_citizen_discount.png
    ├── Q10_filter_doctors_1.png
    ├── Q10_filter_doctors_2.png
    ├── Q11_post_add_doctor_1.png
    ├── Q11_post_add_doctor_2.png
    ├── Q12_put_update_doctor_1.png
    ├── Q12_put_update_doctor_2.png
    ├── Q13_book_for_delete_test.png
    ├── Q13_delete_doctor_blocked.png
    ├── Q13_delete_doctor_success.png
    ├── Q14_confirm_cancel_appointment.png
    ├── Q15_complete_appointment.png
    ├── Q15_active_appointments.png
    ├── Q15_appointments_by_doctor.png
    ├── Q16_search_doctors.png
    ├── Q17_sort_doctors.png
    ├── Q18_paginate_doctors.png
    ├── Q19_appointments_search.png
    ├── Q19_appointments_sort.png
    ├── Q19_appointments_page.png
    └── Q20_browse_combined.png
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Programming language |
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |

---

## 🎓 Internship

Built as part of the **FastAPI Internship Final Project** at [Innomatics Research Labs](https://www.innomatics.in/).
