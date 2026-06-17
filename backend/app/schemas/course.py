from pydantic import BaseModel
from typing import Optional

class CourseBase(BaseModel):
    course_name: str
    teacher_name: Optional[str] = None
    teacher_id: Optional[int] = None
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int

    class Config:
        from_attributes = True