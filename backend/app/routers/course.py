from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.course import Course
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut

router = APIRouter()

@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Course)
    if current_user.role == "teacher":
        q = q.filter(Course.teacher_id == current_user.id)
    return q.order_by(Course.id.desc()).all()

@router.post("", response_model=CourseOut)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权创建课程")
    obj = Course(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "课程不存在")
    if current_user.role == "teacher":
        if obj.teacher_id != current_user.id:
            raise HTTPException(403, "无权修改此课程")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "课程不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权删除课程")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}