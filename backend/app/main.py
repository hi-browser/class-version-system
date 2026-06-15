from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import course, class_group, session, upload, statistics, behavior_category

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static/results", StaticFiles(directory=settings.RESULT_DIR), name="results")

app.include_router(course.router, prefix="/api/courses", tags=["课程管理"])
app.include_router(class_group.router, prefix="/api/classes", tags=["班级管理"])
app.include_router(session.router, prefix="/api/sessions", tags=["课堂记录"])
app.include_router(upload.router, prefix="/api/upload", tags=["上传分析"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["统计分析"])
app.include_router(behavior_category.router, prefix="/api/behavior-categories", tags=["行为类别"])

@app.get("/")
def root():
    return {"message": "Classroom Vision System backend is running."}
