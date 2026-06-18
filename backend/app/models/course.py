from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.core.database import Base

class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    class_group_id = Column(Integer, ForeignKey("class_group.id"), nullable=True)
    date = Column(Date, nullable=False)
    time_slot = Column(Integer, nullable=False)
    location = Column(String(50), nullable=False)