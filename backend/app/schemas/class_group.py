from pydantic import BaseModel
from typing import Optional

class ClassGroupBase(BaseModel):
    course_name: str
    teacher_id: int
    student_count: int = 0

class ClassGroupCreate(ClassGroupBase):
    pass

class ClassGroupUpdate(BaseModel):
    course_name: Optional[str] = None
    teacher_id: Optional[int] = None
    student_count: Optional[int] = None

class ClassGroupOut(BaseModel):
    id: int
    course_name: str
    teacher_id: int
    teacher_name: Optional[str] = None
    student_count: int

    class Config:
        from_attributes = True