from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.class_group import ClassGroup
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.class_group import ClassGroupCreate, ClassGroupUpdate, ClassGroupOut

router = APIRouter()

def _enrich(cg: ClassGroup, db: Session) -> ClassGroupOut:
    out = ClassGroupOut(
        id=cg.id,
        course_name=cg.course_name,
        teacher_id=cg.teacher_id,
        student_count=cg.student_count,
    )
    teacher = db.get(User, cg.teacher_id)
    if teacher:
        out.teacher_name = teacher.name
    return out

@router.get("", response_model=list[ClassGroupOut])
def list_classes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(ClassGroup)
    if current_user.role == "teacher":
        q = q.filter(ClassGroup.teacher_id == current_user.id)
    rows = q.order_by(ClassGroup.id.desc()).all()
    return [_enrich(r, db) for r in rows]

@router.post("", response_model=ClassGroupOut)
def create_class(payload: ClassGroupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权创建班级")
    teacher = db.get(User, payload.teacher_id)
    if not teacher or teacher.role != "teacher":
        raise HTTPException(400, "指定的教师不存在或不是教师角色")
    obj = ClassGroup(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _enrich(obj, db)

@router.put("/{class_id}", response_model=ClassGroupOut)
def update_class(class_id: int, payload: ClassGroupUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(ClassGroup, class_id)
    if not obj:
        raise HTTPException(404, "班级不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权修改班级")
    if payload.teacher_id is not None:
        teacher = db.get(User, payload.teacher_id)
        if not teacher or teacher.role != "teacher":
            raise HTTPException(400, "指定的教师不存在或不是教师角色")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return _enrich(obj, db)

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(ClassGroup, class_id)
    if not obj:
        raise HTTPException(404, "班级不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权删除班级")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}