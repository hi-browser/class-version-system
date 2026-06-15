from pydantic import BaseModel
from typing import Optional

class ClassGroupBase(BaseModel):
    class_name: str
    expected_count: int = 0
    major: Optional[str] = None
    grade: Optional[str] = None

class ClassGroupCreate(ClassGroupBase):
    pass

class ClassGroupUpdate(ClassGroupBase):
    pass

class ClassGroupOut(ClassGroupBase):
    id: int

    class Config:
        from_attributes = True
