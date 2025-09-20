from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import verify_password, create_access_token
from app.schemas.schemas import TokenResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_token(self, user: User) -> TokenResponse:
        payload = {"sub": user.username, "user_id": user.id, "role": user.role}
        token = create_access_token(payload)
        return TokenResponse(access_token=token)