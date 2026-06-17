from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.class_group import ClassGroup
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.class_group import ClassGroupCreate, ClassGroupUpdate, ClassGroupOut

router = APIRouter()

@router.get("", response_model=list[ClassGroupOut])
def list_classes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(ClassGroup)
    if current_user.role == "teacher":
        q = q.filter(ClassGroup.teacher_id == current_user.id)
    return q.order_by(ClassGroup.id.desc()).all()

@router.post("", response_model=ClassGroupOut)
def create_class(payload: ClassGroupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权创建班级")
    obj = ClassGroup(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{class_id}", response_model=ClassGroupOut)
def update_class(class_id: int, payload: ClassGroupUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = db.get(ClassGroup, class_id)
    if not obj:
        raise HTTPException(404, "班级不存在")
    if current_user.role == "teacher":
        raise HTTPException(403, "教师无权修改班级")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

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