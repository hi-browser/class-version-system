from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.class_group import ClassGroup
from app.schemas.class_group import ClassGroupCreate, ClassGroupUpdate, ClassGroupOut

router = APIRouter()

@router.get("", response_model=list[ClassGroupOut])
def list_classes(db: Session = Depends(get_db)):
    return db.query(ClassGroup).order_by(ClassGroup.id.desc()).all()

@router.post("", response_model=ClassGroupOut)
def create_class(payload: ClassGroupCreate, db: Session = Depends(get_db)):
    obj = ClassGroup(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{class_id}", response_model=ClassGroupOut)
def update_class(class_id: int, payload: ClassGroupUpdate, db: Session = Depends(get_db)):
    obj = db.get(ClassGroup, class_id)
    if not obj:
        raise HTTPException(404, "班级不存在")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    obj = db.get(ClassGroup, class_id)
    if not obj:
        raise HTTPException(404, "班级不存在")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}
