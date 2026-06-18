from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    role: str = "teacher"

class UserLogin(BaseModel):
    email: str
    password: str
    role: str = "teacher"

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    is_verified: bool
    role: str

    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut