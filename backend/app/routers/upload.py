import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.class_session import ClassSession
from app.models.course import Course
from app.models.class_group import ClassGroup
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.file_service import save_upload_file
from app.cv.analyzer import analyzer

router = APIRouter()

@router.post("/analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    class_group_id: int = Form(...),
    analysis_date: str = Form(...),
    time_slot: int = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if time_slot < 1 or time_slot > 9:
        raise HTTPException(400, "上课时间必须在1~9之间")

    try:
        parsed_date = datetime.strptime(analysis_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "日期格式无效，请使用YYYY-MM-DD")

    cg = db.get(ClassGroup, class_group_id)
    if not cg:
        raise HTTPException(400, "班级不存在")

    if current_user.role == "teacher" and cg.teacher_id != current_user.id:
        raise HTTPException(403, "只能上传自己所教班级的分析")

    schedule = db.query(Course).filter(
        Course.class_group_id == class_group_id,
        Course.date == parsed_date,
        Course.time_slot == time_slot,
        Course.location == location,
    ).first()

    if not schedule:
        raise HTTPException(400, "未找到匹配的排课记录，请确认上课日期、时间、地点与排课表一致")

    expected_count = cg.student_count

    try:
        file_path, source_type = await save_upload_file(file)
        result = analyzer.analyze_file(file_path, source_type, expected_count)

        obj = ClassSession(
            course_id=schedule.id,
            class_id=class_group_id,
            session_time=datetime.now(),
            location=location,
            source_type=source_type,
            source_path=file_path,
            result_path=result.get("result_path"),
            result_video_path=result.get("result_video_path"),
            expected_count=expected_count,
            detected_count=result.get("detected_count", 0),
            attendance_rate=result.get("attendance_rate", 0),
            participation_rate=result.get("participation_rate", 0),
            abnormal_rate=result.get("abnormal_rate", 0),
            phone_rate=result.get("phone_rate", 0),
            head_down_rate=result.get("head_down_rate", 0),
            behavior_json=json.dumps(result.get("behavior_counts", []), ensure_ascii=False),
            trend_json=json.dumps(result.get("trend", []), ensure_ascii=False),
            analysis_text=result.get("analysis_text", ""),
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)

        result["session_id"] = obj.id
        result["source_path"] = file_path
        result["source_type"] = source_type
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))