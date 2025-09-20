from fastapi import Depends, HTTPException, status, Header
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.models.models import User

def get_db_session():
    yield from get_db()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db_session)) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_role(role: str):
    def _require_role(user: User = Depends(get_current_user)):
        # role param is "Creator" actions. Viewer cannot perform Creator actions.
        if user.role != role and user.role != "Creator":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _require_role
