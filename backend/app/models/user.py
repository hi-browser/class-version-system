from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint, func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint('email', 'role', name='uq_email_role'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), nullable=False, index=True)
    name = Column(String(64), nullable=False, default="")
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default="teacher")
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())