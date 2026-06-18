from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.course import Course
from app.models.class_group import ClassGroup
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut

router = APIRouter()

def _enrich(course: Course, db: Session):
    out = CourseOut(
        id=course.id,
        class_group_id=course.class_group_id,
        date=course.date,
        time_slot=course.time_slot,
        location=course.location,
    )
    if course.class_group_id:
        cg = db.get(ClassGroup, course.class_group_id)
        if cg:
            out.class_group_name = cg.course_name
            out.student_count = cg.student_count
            teacher = db.get(User, cg.teacher_id)
            if teacher:
                out.teacher_name = teacher.name
    return out

@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Course)
    if current_user.role == "teacher":
        sub = db.query(ClassGroup.id).filter(ClassGroup.teacher_id == current_user.id).subquery()
        q = q.filter(Course.class_group_id.in_(sub))
    rows = q.order_by(Course.date.desc(), Course.time_slot.asc()).all()
    return [_enrich(r, db) for r in rows]

@router.post("", response_model=CourseOut)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权创建排课")
    conflict = db.query(Course).filter(
        Course.date == payload.date,
        Course.time_slot == payload.time_slot,
        Course.location == payload.location,
    ).first()
    if conflict:
        raise HTTPException(400, f"该日期({payload.date})第{payload.time_slot}节 {payload.location} 已有排课，请重新选择")
    obj = Course(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _enrich(obj, db)

@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "排课不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权修改排课")
    conflict = db.query(Course).filter(
        Course.id != course_id,
        Course.date == payload.date,
        Course.time_slot == payload.time_slot,
        Course.location == payload.location,
    ).first()
    if conflict:
        raise HTTPException(400, f"该日期({payload.date})第{payload.time_slot}节 {payload.location} 已有排课，请重新选择")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _enrich(obj, db)

@router.get("/locations")
def list_locations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "teacher":
        sub = db.query(ClassGroup.id).filter(ClassGroup.teacher_id == current_user.id).subquery()
        rows = db.query(Course.location).filter(Course.class_group_id.in_(sub)).distinct().order_by(Course.location.asc()).all()
    else:
        rows = db.query(Course.location).distinct().order_by(Course.location.asc()).all()
    return [r[0] for r in rows]

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(Course, course_id)
    if not obj:
        raise HTTPException(404, "排课不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权删除排课")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}