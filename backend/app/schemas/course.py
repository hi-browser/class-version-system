from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date

class CourseBase(BaseModel):
    class_group_id: Optional[int] = None
    date: date
    time_slot: int
    location: str

    @field_validator("time_slot")
    @classmethod
    def check_time_slot(cls, v):
        if v < 1 or v > 9:
            raise ValueError("上课时间必须在1~9之间")
        return v

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    class_group_name: Optional[str] = None
    teacher_name: Optional[str] = None
    student_count: Optional[int] = None

    class Config:
        from_attributes = True