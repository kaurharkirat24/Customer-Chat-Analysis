from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import get_db, InternalUser
from services.auth import verify_password, create_access_token, get_password_hash
from pydantic import BaseModel
from schemas.user import UserCreate, Token
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

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

# Standard JWT Signup
@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(InternalUser).filter(InternalUser.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = InternalUser(email=user_in.email, hashed_password=hashed_password, name=user_in.name or "New Agent")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

class GoogleTokenRequest(BaseModel):
    credential: str

@router.post("/google", response_model=Token)
def google_auth(request: GoogleTokenRequest, db: Session = Depends(get_db)):
    try:
        # Verify the token with Google
        CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
        idinfo = id_token.verify_oauth2_token(request.credential, google_requests.Request(), CLIENT_ID)
        
        email = idinfo['email']
        name = idinfo.get('name', 'Google User')
        
        user = db.query(InternalUser).filter(InternalUser.email == email).first()
        if not user:
            # Auto-create Google SSO user
            user = InternalUser(email=email, name=name, hashed_password=None)
            db.add(user)
            db.commit()
            db.refresh(user)
            
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid Google token")
