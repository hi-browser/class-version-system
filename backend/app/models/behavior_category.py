from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.core.database import Base

class BehaviorCategory(Base):
    __tablename__ = "behavior_category"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, nullable=False, unique=True)
    code = Column(String(50), nullable=False)
    name_cn = Column(String(50), nullable=False)
    is_positive = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
