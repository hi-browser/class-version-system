from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut

router = APIRouter()

@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.id.desc()).all()

@router.post("", response_model=CourseOut)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    obj = Course(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "课程不存在")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "课程不存在")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}
