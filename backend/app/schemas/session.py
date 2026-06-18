from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class SessionOut(BaseModel):
    id: int
    course_id: Optional[int]
    class_id: Optional[int]
    session_time: Optional[datetime]
    location: Optional[str]
    source_type: str
    source_path: str
    result_path: Optional[str]
    expected_count: int
    detected_count: int
    attendance_rate: float
    participation_rate: float
    abnormal_rate: float
    phone_rate: float
    head_down_rate: float
    behavior_json: Optional[str]
    trend_json: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class SessionUpdate(BaseModel):
    course_id: Optional[int] = None
    class_id: Optional[int] = None
    expected_count: Optional[int] = None
    session_time: Optional[datetime] = None