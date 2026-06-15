from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.behavior_category import BehaviorCategory
from app.cv.labels import CLASS_NAMES, CLASS_CN, POSITIVE_CLASSES

router = APIRouter()

@router.get("")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(BehaviorCategory).order_by(BehaviorCategory.class_id.asc()).all()
    if rows:
        return rows

    # 初次运行时自动插入默认行为类别
    for class_id, code in CLASS_NAMES.items():
        db.add(BehaviorCategory(
            class_id=class_id,
            code=code,
            name_cn=CLASS_CN[class_id],
            is_positive=class_id in POSITIVE_CLASSES,
        ))
    db.commit()
    return db.query(BehaviorCategory).order_by(BehaviorCategory.class_id.asc()).all()
