from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db, Base
from models import User, Booking, UserRole, BookingStatus
from schemas import (
    UserRegister, UserLogin, UserResponse, 
    BookingCreate, BookingResponse, BookingStatusUpdate, StatsResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_admin
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        role=UserRole.client
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@app.get("/api/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/bookings", response_model=BookingResponse)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = Booking(
        user_id=current_user.id,
        name=booking_data.name,
        phone=booking_data.phone,
        email=booking_data.email,
        service=booking_data.service,
        message=booking_data.message
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/api/bookings", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()

@app.get("/api/admin/bookings", response_model=List[BookingResponse])
def get_all_bookings(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

@app.patch("/api/admin/bookings/{booking_id}", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status_update.status
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/api/admin/stats", response_model=StatsResponse)
def get_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_bookings = db.query(Booking).count()
    new_bookings = db.query(Booking).filter(Booking.status == BookingStatus.new).count()
    confirmed_bookings = db.query(Booking).filter(Booking.status == BookingStatus.confirmed).count()
    completed_bookings = db.query(Booking).filter(Booking.status == BookingStatus.completed).count()
    total_users = db.query(User).filter(User.role == UserRole.client).count()
    
    return {
        "total_bookings": total_bookings,
        "new_bookings": new_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "total_users": total_users
    }
