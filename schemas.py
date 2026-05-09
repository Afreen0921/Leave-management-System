from pydantic import BaseModel, validator
from datetime import date

# ===============================
# 👤 EMPLOYEE SCHEMAS
# ===============================

# Register Employee
class EmployeeCreate(BaseModel):
    name: str
    email: str
    password: str


# Response (optional, for display)
class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


# ===============================
# 🔐 LOGIN SCHEMA
# ===============================

class LoginData(BaseModel):
    email: str
    password: str


# ===============================
# 📝 LEAVE SCHEMAS
# ===============================

# Create Leave
class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str

    # ✅ Validation: end date must be after start
    @validator("end_date")
    def check_dates(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


# Response Leave
class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str

    class Config:
        from_attributes = True