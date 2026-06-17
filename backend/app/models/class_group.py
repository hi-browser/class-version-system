from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base

class ClassGroup(Base):
    __tablename__ = "class_group"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(100), nullable=False)
    expected_count = Column(Integer, nullable=False, default=0)
    major = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())