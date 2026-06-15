import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.class_session import ClassSession
from app.schemas.session import SessionOut, SessionUpdate

router = APIRouter()

@router.get("", response_model=list[SessionOut])
def list_sessions(course_id: int | None = None, class_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(ClassSession)
    if course_id:
        q = q.filter(ClassSession.course_id == course_id)
    if class_id:
        q = q.filter(ClassSession.class_id == class_id)
    return q.order_by(ClassSession.id.desc()).all()

@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    obj = db.get(ClassSession, session_id)
    if not obj:
        raise HTTPException(404, "课堂记录不存在")
    return obj

@router.get("/{session_id}/analysis")
def get_session_analysis(session_id: int, db: Session = Depends(get_db)):
    obj = db.get(ClassSession, session_id)
    if not obj:
        raise HTTPException(404, "课堂记录不存在")

    try:
        behavior_counts = json.loads(obj.behavior_json) if obj.behavior_json else []
    except Exception:
        behavior_counts = []

    try:
        trend = json.loads(obj.trend_json) if obj.trend_json else []
    except Exception:
        trend = []

    return {
        "id": obj.id,
        "course_id": obj.course_id,
        "class_id": obj.class_id,
        "session_time": obj.session_time,
        "source_type": obj.source_type,
        "source_path": obj.source_path,
        "result_path": obj.result_path,
        "expected_count": obj.expected_count,
        "detected_count": obj.detected_count,
        "attendance_rate": obj.attendance_rate,
        "participation_rate": obj.participation_rate,
        "abnormal_rate": obj.abnormal_rate,
        "phone_rate": obj.phone_rate,
        "head_down_rate": obj.head_down_rate,
        "behavior_counts": behavior_counts,
        "trend": trend,
        "created_at": obj.created_at,
    }

@router.put("/{session_id}", response_model=SessionOut)
def update_session(session_id: int, payload: SessionUpdate, db: Session = Depends(get_db)):
    obj = db.get(ClassSession, session_id)
    if not obj:
        raise HTTPException(404, "课堂记录不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

BASE_DIR = Path(__file__).resolve().parents[2]


def _to_local_static_file(path: str | None):
    if not path:
        return None

    path = path.replace("\\", "/").lstrip("/")

    if path.startswith("app/static/"):
        path = path.replace("app/static/", "static/", 1)

    if not path.startswith("static/"):
        return None

    local_path = BASE_DIR / "app" / path

    try:
        local_path = local_path.resolve()
        static_root = (BASE_DIR / "app" / "static").resolve()

        # 防止误删 static 目录外的文件
        if not str(local_path).startswith(str(static_root)):
            return None

        return local_path
    except Exception:
        return None


def _safe_delete_file(path: str | None):
    file_path = _to_local_static_file(path)

    if file_path and file_path.exists() and file_path.is_file():
        file_path.unlink()

@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    obj = db.get(ClassSession, session_id)
    if not obj:
        raise HTTPException(404, "课堂记录不存在")

    source_path = obj.source_path
    result_path = obj.result_path

    db.delete(obj)
    db.commit()

    _safe_delete_file(source_path)
    _safe_delete_file(result_path)

    return {"message": "删除成功"}
