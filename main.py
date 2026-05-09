
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply Leave
@app.post("/apply-leave")
def apply_leave(leave: schemas.LeaveCreate, db: Session = Depends(get_db)):

    if leave.start_date < date.today():
        raise HTTPException(status_code=400, detail="Past date not allowed")

    if leave.end_date < leave.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    existing = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.employee_id == leave.employee_id,
        models.LeaveRequest.start_date <= leave.end_date,
        models.LeaveRequest.end_date >= leave.start_date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Overlapping leave not allowed")

    new_leave = models.LeaveRequest(**leave.dict(), status="Pending")

    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)

    return new_leave

# View Leaves
@app.get("/leaves")
def get_leaves(db: Session = Depends(get_db)):
    return db.query(models.LeaveRequest).all()


@app.put("/update/{leave_id}")
def update_leave(leave_id: int, leave: schemas.LeaveCreate, db: Session = Depends(get_db)):

    db_leave = db.query(models.LeaveRequest).get(leave_id)

    if not db_leave:
        raise HTTPException(status_code=404, detail="Not found")

    if db_leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Cannot update")

    if leave.start_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot update past leave")

    for key, value in leave.dict().items():
        setattr(db_leave, key, value)

    db.commit()
    return db_leave

@app.put("/approve/{leave_id}")
def approve(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(models.LeaveRequest).get(leave_id)

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    leave.status = "Approved"
    db.commit()
    return leave

@app.delete("/delete/{leave_id}")
def delete_leave(leave_id: int, db: Session = Depends(get_db)):

    db_leave = db.query(models.LeaveRequest).get(leave_id)

    if not db_leave:
        raise HTTPException(status_code=404, detail="Not found")

    if db_leave.status != "Pending":
        raise HTTPException(status_code=400, detail="Cannot delete non-pending leave")

    db.delete(db_leave)
    db.commit()

    return {"message": "Deleted"}


# Approve
@app.put("/approve/{leave_id}")
def approve(leave_id: int, db: Session = Depends(get_db)):

    leave = db.query(models.LeaveRequest).get(leave_id)

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    leave.status = "Approved"
    db.commit()

    return leave

# Reject
@app.put("/reject/{leave_id}")
def reject(leave_id: int, db: Session = Depends(get_db)):

    leave = db.query(models.LeaveRequest).get(leave_id)

    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    leave.status = "Rejected"
    db.commit()

    return leave



@app.post("/register")
def register(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):

    existing = db.query(models.Employee).filter(
        models.Employee.email == emp.email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_emp = models.Employee(
        name=emp.name,
        email=emp.email,
        password=emp.password
    )

    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)

    return {"message": "Registered successfully"}

@app.post("/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):

    user = db.query(models.Employee).filter(
        models.Employee.email == data.email
    ).first()

    if not user or user.password != data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": user.id}