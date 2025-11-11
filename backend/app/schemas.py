from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import UserRole, BookingStatus

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str]
    service: Optional[str]
    message: Optional[str]

class BookingResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    phone: str
    email: Optional[str]
    service: Optional[str]
    message: Optional[str]
    comment: Optional[str]
    status: BookingStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingCommentUpdate(BaseModel):
    comment: Optional[str]

class StatsResponse(BaseModel):
    total_bookings: int
    new_bookings: int
    confirmed_bookings: int
    completed_bookings: int
    total_users: int

