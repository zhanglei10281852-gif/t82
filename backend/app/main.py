from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.init_data import init_db
from app.routers import auth, homestays, rooms, bookings, calendar, stats, reviews, holidays, maintenance

Base.metadata.create_all(bind=engine)

app = FastAPI(title="乡村民宿预订管理平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(homestays.router, prefix="/api/homestays", tags=["民宿管理"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["房间管理"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["预订管理"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["房态日历"])
app.include_router(stats.router, prefix="/api/stats", tags=["统计分析"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["评价管理"])
app.include_router(holidays.router, prefix="/api/holidays", tags=["节假日管理"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["维护管理"])


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    init_db(db)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "乡村民宿预订管理平台运行正常"}
