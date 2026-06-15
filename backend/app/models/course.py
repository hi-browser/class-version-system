from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    teacher_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
