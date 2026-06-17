from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token,
    decode_access_token, create_verify_token, decode_verify_token,
    send_verify_email,
)
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenOut, UserOut

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(401, "登录已过期，请重新登录")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(401, "无效的登录凭证")
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(401, "用户不存在")
    return user


@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email, User.role == payload.role).first():
        raise HTTPException(400, "该邮箱已注册该身份")
    if len(payload.password) < 6:
        raise HTTPException(400, "密码长度不能少于6位")
    if not payload.name or not payload.name.strip():
        raise HTTPException(400, "名称不能为空")
    if payload.role not in ("admin", "teacher"):
        raise HTTPException(400, "身份类型无效，请选择管理员或教师")

    password_hash = hash_password(payload.password)
    name = payload.name.strip()

    user = User(
        email=payload.email,
        name=name,
        password_hash=password_hash,
        role=payload.role,
        is_verified=False,
    )
    db.add(user)

    if payload.role == "admin":
        if db.query(User).filter(User.email == payload.email, User.role == "teacher").first():
            raise HTTPException(400, "该邮箱已注册教师身份")
        teacher = User(
            email=payload.email,
            name=name,
            password_hash=password_hash,
            role="teacher",
            is_verified=True,
        )
        db.add(teacher)

    db.commit()
    db.refresh(user)

    verify_token = create_verify_token(user.email)
    if not send_verify_email(user.email, verify_token):
        raise HTTPException(500, "验证邮件发送失败，请稍后重试")

    return {"message": "注册成功，请查收验证邮件完成验证"}


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    if payload.role not in ("admin", "teacher"):
        raise HTTPException(400, "身份类型无效")
    user = db.query(User).filter(User.email == payload.email, User.role == payload.role).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(400, "邮箱或密码错误")
    if not user.is_verified:
        raise HTTPException(400, "邮箱尚未验证，请先验证邮箱")
    token = create_access_token({"sub": str(user.id)})
    user_out = UserOut(id=user.id, email=user.email, name=user.name, is_verified=user.is_verified, role=user.role)
    return TokenOut(access_token=token, user=user_out)


@router.get("/verify", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    email = decode_verify_token(token)
    if email is None:
        return """<html><head><meta charset="utf-8"></head><body style="text-align:center;padding-top:80px;font-family:Arial">
        <h2 style="color:#f56c6c">验证链接已过期或无效</h2><p>请重新注册或请求新的验证邮件</p></body></html>"""
    user = db.query(User).filter(User.email == email, User.role == "admin").first()
    if user is None:
        return """<html><head><meta charset="utf-8"></head><body style="text-align:center;padding-top:80px;font-family:Arial">
        <h2 style="color:#f56c6c">用户不存在</h2></body></html>"""
    if user.is_verified:
        return """<html><head><meta charset="utf-8"></head><body style="text-align:center;padding-top:80px;font-family:Arial">
        <h2 style="color:#67c23a">邮箱已验证</h2><p>无需重复验证，请前往登录</p></body></html>"""
    user.is_verified = True
    teacher = db.query(User).filter(User.email == email, User.role == "teacher").first()
    if teacher and not teacher.is_verified:
        teacher.is_verified = True
    db.commit()
    return """<html><head><meta charset="utf-8"></head><body style="text-align:center;padding-top:80px;font-family:Arial">
    <h2 style="color:#67c23a">验证成功</h2><p>邮箱验证完成，请关闭此页面返回系统登录</p></body></html>"""


@router.post("/resend-verify")
def resend_verify(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(400, "该邮箱未注册")
    if user.is_verified:
        return {"message": "邮箱已验证，无需重复发送"}
    verify_token = create_verify_token(user.email)
    if not send_verify_email(user.email, verify_token):
        raise HTTPException(500, "验证邮件发送失败，请稍后重试")
    return {"message": "验证邮件已重新发送"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, email=current_user.email, name=current_user.name, is_verified=current_user.is_verified, role=current_user.role)


@router.get("/teachers")
def list_teachers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可查看教师列表")
    teachers = db.query(User).filter(User.role == "teacher").all()
    return [{"id": t.id, "name": t.name, "email": t.email} for t in teachers]