from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, func
from app.core.database import Base

class ClassSession(Base):
    __tablename__ = "class_session"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("class_group.id"), nullable=True)
    session_time = Column(DateTime, nullable=True)

    source_type = Column(String(20), nullable=False)  # image/video
    source_path = Column(String(255), nullable=False)
    result_path = Column(String(255), nullable=True)

    expected_count = Column(Integer, nullable=False, default=0)
    detected_count = Column(Integer, nullable=False, default=0)
    attendance_rate = Column(Float, nullable=False, default=0)

    participation_rate = Column(Float, nullable=False, default=0)
    abnormal_rate = Column(Float, nullable=False, default=0)
    phone_rate = Column(Float, nullable=False, default=0)
    head_down_rate = Column(Float, nullable=False, default=0)

    behavior_json = Column(Text, nullable=True)
    trend_json = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
