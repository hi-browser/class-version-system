from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
<<<<<<< HEAD
from app.core.database import Base, engine, SessionLocal
from app.models.course import Course
from app.models.class_group import ClassGroup
from app.models.behavior_category import BehaviorCategory
from app.routers import course, class_group, session, upload, statistics, behavior_category
=======
from app.core.database import Base, engine
from app.routers import course, class_group, session, upload, statistics, behavior_category, auth
>>>>>>> gitee/ysy-frontend-checkversiontest


def init_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Course).count() == 0:
            db.add_all([
                Course(course_name="计算机视觉导论", teacher_name="张老师", description="智慧课堂测试课程"),
                Course(course_name="人工智能基础", teacher_name="李老师", description="课堂行为统计演示课程"),
            ])
            db.commit()

        if db.query(ClassGroup).count() == 0:
            db.add_all([
                ClassGroup(class_name="软件工程2301班", expected_count=45, major="软件工程", grade="2023级"),
                ClassGroup(class_name="人工智能2302班", expected_count=50, major="人工智能", grade="2023级"),
            ])
            db.commit()

        if db.query(BehaviorCategory).count() == 0:
            db.add_all([
                BehaviorCategory(class_id=0, code="hand_raising", name_cn="举手互动", is_positive=True),
                BehaviorCategory(class_id=1, code="reading", name_cn="阅读/看书", is_positive=True),
                BehaviorCategory(class_id=2, code="writing", name_cn="低头书写", is_positive=True),
                BehaviorCategory(class_id=3, code="using_phone", name_cn="使用手机", is_positive=False),
                BehaviorCategory(class_id=4, code="bowing_head", name_cn="低头状态", is_positive=False),
                BehaviorCategory(class_id=5, code="leaning_over_table", name_cn="趴桌/疑似睡觉", is_positive=False),
            ])
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

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
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])

@app.get("/")
def root():
    return {"message": "Classroom Vision System backend is running."}