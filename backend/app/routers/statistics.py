import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.class_session import ClassSession

router = APIRouter()

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_sessions = db.query(func.count(ClassSession.id)).scalar() or 0
    avg_attendance = db.query(func.avg(ClassSession.attendance_rate)).scalar() or 0
    avg_participation = db.query(func.avg(ClassSession.participation_rate)).scalar() or 0
    avg_abnormal = db.query(func.avg(ClassSession.abnormal_rate)).scalar() or 0

    recent = db.query(ClassSession).order_by(ClassSession.id.desc()).limit(10).all()
    return {
        "total_sessions": total_sessions,
        "avg_attendance": round(float(avg_attendance), 2),
        "avg_participation": round(float(avg_participation), 2),
        "avg_abnormal": round(float(avg_abnormal), 2),
        "recent": [
            {
                "id": x.id,
                "created_at": x.created_at,
                "detected_count": x.detected_count,
                "attendance_rate": x.attendance_rate,
                "participation_rate": x.participation_rate,
                "abnormal_rate": x.abnormal_rate,
            } for x in recent
        ],
    }

@router.get("/behavior-summary")
def behavior_summary(db: Session = Depends(get_db)):
    sessions = db.query(ClassSession).all()
    merged = {}
    for s in sessions:
        if not s.behavior_json:
            continue
        try:
            data = json.loads(s.behavior_json)
        except Exception:
            continue
        for item in data:
            name = item.get("name", "未知")
            merged[name] = merged.get(name, 0) + int(item.get("count", 0))
    return [{"name": k, "value": v} for k, v in merged.items()]

@router.get("/attendance-trend")
def attendance_trend(db: Session = Depends(get_db)):
    sessions = db.query(ClassSession).order_by(ClassSession.session_time.asc()).limit(30).all()
    return [
        {
            "id": s.id,
            "time": s.session_time.strftime("%m-%d %H:%M") if s.session_time else (s.created_at.strftime("%m-%d %H:%M") if s.created_at else str(s.id)),
            "attendance_rate": s.attendance_rate,
            "participation_rate": s.participation_rate,
            "abnormal_rate": s.abnormal_rate,
        }
        for s in sessions
    ]


@router.get("/attendance-trend/filter")
def attendance_trend_filtered(
    course_id: int | None = None,
    class_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(ClassSession).order_by(ClassSession.session_time.asc())
    if course_id:
        q = q.filter(ClassSession.course_id == course_id)
    if class_id:
        q = q.filter(ClassSession.class_id == class_id)
    sessions = q.limit(50).all()
    return [
        {
            "id": s.id,
            "time": s.session_time.strftime("%m-%d %H:%M") if s.session_time else (s.created_at.strftime("%m-%d %H:%M") if s.created_at else str(s.id)),
            "attendance_rate": s.attendance_rate,
            "participation_rate": s.participation_rate,
            "abnormal_rate": s.abnormal_rate,
        }
        for s in sessions
    ]