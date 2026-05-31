from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..models import get_db, InternalUser
from ..services.auth import verify_password, create_access_token, get_password_hash
from ..schemas.user import UserCreate, Token, User

router = APIRouter(prefix="/auth", tags=["auth"])

# Standard JWT Login
@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(InternalUser).filter(InternalUser.email == form_data.username).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Mock OAuth2 (Simulating Google OAuth callback for MVP Phase 1)
@router.post("/oauth/mock")
def mock_oauth_login(email: str, name: str, db: Session = Depends(get_db)):
    user = db.query(InternalUser).filter(InternalUser.email == email).first()
    if not user:
        # Auto-create user for Mock OAuth if doesn't exist
        user = InternalUser(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
