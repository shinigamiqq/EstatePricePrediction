import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException, Depends
from typing import Optional

# секретный ключ для jwt
# в проде надо бы вынести в .env но сейчас и так сойдет
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# захардкоженные юзеры для демки
# по хорошему надо хэшировать пароли и хранить в бд
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    }
}

# отдельный токен для удаления истории 
DELETE_HISTORY_TOKEN = "delete-history-secret-token"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    #создает jwt токен с заданным временем жизни
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    #проверяет токен и возвращает payload
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def authenticate_user(username: str, password: str) -> Optional[dict]:
    # проверяет логин/пароль
    user = USERS_DB.get(username)
    
    if user and user["password"] == password:
        return user
    
    return None


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    # достает юзера из jwt токена в заголовке Authorization
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # парсим "Bearer <token>"
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    payload = verify_token(token)
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = USERS_DB.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    # проверяет что юзер админ
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user


def verify_delete_token(x_delete_token: Optional[str] = Header(default=None)) -> bool:
    # проверяет токен для удаления истории 
    if not x_delete_token:
        raise HTTPException(status_code=401, detail="X-Delete-Token header required")
    
    if x_delete_token != DELETE_HISTORY_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid delete token")
    
    return True
