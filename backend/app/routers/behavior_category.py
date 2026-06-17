from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.behavior_category import BehaviorCategory
from app.models.user import User
from app.routers.auth import get_current_user
from app.cv.labels import CLASS_NAMES, CLASS_CN, POSITIVE_CLASSES

router = APIRouter()

class CategoryCreate(BaseModel):
    class_id: int
    code: str
    name_cn: str
    is_positive: bool = True

class CategoryUpdate(BaseModel):
    code: str | None = None
    name_cn: str | None = None
    is_positive: bool | None = None


def _require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可操作行为类别")


@router.get("")
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)

    rows = db.query(BehaviorCategory).order_by(BehaviorCategory.class_id.asc()).all()
    if rows:
        return rows

    for class_id, code in CLASS_NAMES.items():
        db.add(BehaviorCategory(
            class_id=class_id,
            code=code,
            name_cn=CLASS_CN[class_id],
            is_positive=class_id in POSITIVE_CLASSES,
        ))
    db.commit()
    return db.query(BehaviorCategory).order_by(BehaviorCategory.class_id.asc()).all()


@router.post("")
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    existing = db.query(BehaviorCategory).filter(BehaviorCategory.class_id == payload.class_id).first()
    if existing:
        raise HTTPException(400, "该类别编号已存在")
    obj = BehaviorCategory(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    obj = db.get(BehaviorCategory, category_id)
    if not obj:
        raise HTTPException(404, "行为类别不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_admin(current_user)
    obj = db.get(BehaviorCategory, category_id)
    if not obj:
        raise HTTPException(404, "行为类别不存在")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}