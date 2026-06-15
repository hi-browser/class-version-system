import json
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.class_session import ClassSession
from app.services.file_service import save_upload_file
from app.cv.analyzer import analyzer

router = APIRouter()

@router.post("/analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    course_id: int | None = Form(None),
    class_id: int | None = Form(None),
    expected_count: int = Form(0),
    session_time: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        file_path, source_type = await save_upload_file(file)
        result = analyzer.analyze_file(file_path, source_type, expected_count)

        parsed_time = None
        if session_time:
            try:
                parsed_time = datetime.fromisoformat(session_time)
            except Exception:
                parsed_time = None

        obj = ClassSession(
            course_id=course_id,
            class_id=class_id,
            session_time=parsed_time,
            source_type=source_type,
            source_path=file_path,
            result_path=result.get("result_path"),
            expected_count=expected_count,
            detected_count=result.get("detected_count", 0),
            attendance_rate=result.get("attendance_rate", 0),
            participation_rate=result.get("participation_rate", 0),
            abnormal_rate=result.get("abnormal_rate", 0),
            phone_rate=result.get("phone_rate", 0),
            head_down_rate=result.get("head_down_rate", 0),
            behavior_json=json.dumps(result.get("behavior_counts", []), ensure_ascii=False),
            trend_json=json.dumps(result.get("trend", []), ensure_ascii=False),
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)

        result["session_id"] = obj.id
        result["source_path"] = file_path
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
