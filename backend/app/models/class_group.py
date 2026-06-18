from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class ClassGroup(Base):
    __tablename__ = "class_group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_name = Column(String(20), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_count = Column(Integer, nullable=False, default=0)