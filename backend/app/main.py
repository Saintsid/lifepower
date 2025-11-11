from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import engine, get_db, Base
from models import User, Booking, UserRole, BookingStatus
from schemas import (
    UserRegister, UserLogin, UserResponse,
    BookingCreate, BookingResponse, BookingStatusUpdate, BookingCommentUpdate, StatsResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_admin, get_current_user_optional
)
from telegram import notify_new_booking

Base.metadata.create_all(bind=engine)

app = FastAPI()

# API Router с префиксом /api
api_router = APIRouter(prefix="/api")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "active_page": "index"
    })

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "active_page": "about"
    })

@app.get("/services", response_class=HTMLResponse)
def services_page(request: Request):
    return templates.TemplateResponse("services.html", {
        "request": request,
        "active_page": "services"
    })

@app.get("/contacts", response_class=HTMLResponse)
def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {
        "request": request,
        "active_page": "contacts"
    })

@app.get("/booking", response_class=HTMLResponse)
def booking(request: Request):
    return templates.TemplateResponse("booking.html", {
        "request": request,
        "active_page": "booking"
    })

@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {
        "request": request
    })

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request
    })

@app.get("/client-dashboard", response_class=HTMLResponse)
def client_dashboard(request: Request):
    return templates.TemplateResponse("client-dashboard.html", {
        "request": request
    })

@app.get("/admin-dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin-dashboard.html", {
        "request": request
    })

@api_router.post("/register", response_model=UserResponse)
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

@api_router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@api_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Создание заявки на консультацию
    Работает как с авторизацией, так и без неё
    """
    booking = Booking(
        user_id=current_user.id if current_user else None,
        name=booking_data.name,
        phone=booking_data.phone,
        email=booking_data.email,
        service=booking_data.service,
        message=booking_data.message,
        referral_source=booking_data.referral_source,
        referral_other=booking_data.referral_other if booking_data.referral_source == "other" else None
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    # Отправляем уведомление в Telegram
    await notify_new_booking(
        booking_data={
            "name": booking.name,
            "phone": booking.phone,
            "email": booking.email or "Не указан",
            "service": booking.service or "Не указана",
            "message": booking.message or "Нет сообщения",
            "created_at": booking.created_at.strftime("%d.%m.%Y %H:%M")
        },
        user_name=current_user.name if current_user else None
    )
    
    return booking

@api_router.get("/bookings", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Booking).filter(Booking.user_id == current_user.id).all()

@api_router.get("/admin/bookings", response_model=List[BookingResponse])
def get_all_bookings(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

@api_router.patch("/admin/bookings/{booking_id}", response_model=BookingResponse)
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

@api_router.patch("/admin/bookings/{booking_id}/comment", response_model=BookingResponse)
def update_booking_comment(
    booking_id: int,
    comment_update: BookingCommentUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.comment = comment_update.comment
    db.commit()
    db.refresh(booking)
    return booking

@api_router.get("/admin/stats", response_model=StatsResponse)
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

# Подключаем API роутер
app.include_router(api_router)
