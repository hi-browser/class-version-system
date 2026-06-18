from datetime import datetime,timedelta,timezone
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def decode_access_token(token:str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        return None

def create_verify_token(email: str) -> str:
    """生成邮箱验证专用令牌，有效期 30 分钟"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": email, "type": "email_verify", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_verify_token(token: str) -> str | None:
    """解码验证令牌，返回邮箱地址，失败返回 None"""
    payload = decode_access_token(token)
    if payload is None or payload.get("type") != "email_verify":
        return None
    return payload.get("sub")

def send_verify_email(to_email: str, verify_token: str) -> bool:
    """发送验证邮件，成功返回 True"""
    verify_url = f"http://127.0.0.1:8000/api/auth/verify?token={verify_token}"
    html = f"""
    <div style="max-width:600px;margin:0 auto;padding:30px;font-family:Arial,sans-serif;
                background:#f5f7fa;border-radius:8px">
      <h2 style="color:#409eff">智慧课堂分析系统</h2>
      <p>感谢注册！请点击下方按钮验证您的邮箱：</p>
      <a href="{verify_url}" target="_blank" style="display:inline-block;padding:14px 40px;
         background:#409eff;color:#fff;text-decoration:none;border-radius:6px;font-size:16px;
         margin:20px 0">验证邮箱</a>
      <p style="color:#909399;font-size:13px">如果按钮无法点击，请复制以下链接到浏览器：</p>
      <p style="color:#409eff;font-size:12px;word-break:break-all">{verify_url}</p>
      <p style="color:#909399;font-size:13px;margin-top:30px">链接 30 分钟内有效，请尽快验证。</p>
    </div>
    """
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = "验证您的邮箱 - 智慧课堂分析系统"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    try:
        with SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        return True
    except Exception:
        return False