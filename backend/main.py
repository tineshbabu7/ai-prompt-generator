from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import os

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database import get_db
from models import User, Prompt, PromptHistory
from auth import verify_password, create_access_token, get_password_hash, verify_token
from schemas import LoginRequest, RegisterRequest, PromptRequest, QuestionRequest, SavePromptRequest, PromptResponse, ResetPasswordRequest, PromptHistoryResponse
from prompt_engine import enhance_prompt, detect_type, generate_questions

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Promptomania API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
     allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://ai-prompt-generator-66twu62lg-tineshbabu7-4659s-projects.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Promptomania API is running"}


@app.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(data.password)
    new_user = User(email=data.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully"}


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.username).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password reset successfully"}


@app.post("/auth/google")
def google_auth(payload: dict, db: Session = Depends(get_db)):
    """Verify Google ID token and return our own JWT."""
    credential = payload.get("credential")
    if not credential:
        raise HTTPException(status_code=400, detail="Missing Google credential")

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured on server")

    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")

    email = id_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Could not get email from Google")

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Auto-create account for Google users (no password needed)
        user = User(email=email, hashed_password="__google_oauth__")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/enhance-prompt")
def enhance_prompt_api(
    data: PromptRequest,
    user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    prompt_type = detect_type(data.prompt)
    enhanced = enhance_prompt(data.prompt, data.refinement)

    # Auto-save to prompt history
    db_user = db.query(User).filter(User.email == user).first()
    if db_user:
        entry = PromptHistory(
            user_id=db_user.id,
            lazy_prompt=data.prompt,
            enhanced_prompt=enhanced,
            prompt_type=prompt_type
        )
        db.add(entry)
        db.commit()

    return {"enhanced_prompt": enhanced, "prompt_type": prompt_type}


@app.post("/suggest-questions")
def suggest_questions(
    data: QuestionRequest,
    user: str = Depends(verify_token)
):
    questions = generate_questions(data.prompt, data.prompt_type)
    return {"questions": questions}


#Library endpoints
@app.post("/library/save", status_code=201)
def save_prompt(
    data: SavePromptRequest,
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Save a generated prompt to the user's library."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_prompt = Prompt(
        user_id=user.id,
        lazy_prompt=data.lazy_prompt,
        enhanced_prompt=data.enhanced_prompt,
        prompt_type=data.prompt_type
    )
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return {"message": "Prompt saved", "id": new_prompt.id}


@app.get("/library", response_model=List[PromptResponse])
def get_library(
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Retrieve all saved prompts for the logged-in user, newest first."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prompts = (
        db.query(Prompt)
        .filter(Prompt.user_id == user.id)
        .order_by(Prompt.created_at.desc())
        .all()
    )
    return prompts


@app.delete("/library/{prompt_id}", status_code=204)
def delete_prompt(
    prompt_id: int,
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a specific prompt from the user's library."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.user_id == user.id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    db.delete(prompt)
    db.commit()
    return


# ─── History endpoints ────────────────────────────────────────────────────────

@app.get("/history", response_model=List[PromptHistoryResponse])
def get_history(
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Retrieve all prompt history for the logged-in user, newest first."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entries = (
        db.query(PromptHistory)
        .filter(PromptHistory.user_id == user.id)
        .order_by(PromptHistory.created_at.desc())
        .all()
    )
    return entries


@app.delete("/history/{entry_id}", status_code=204)
def delete_history_entry(
    entry_id: int,
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a single history entry."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    entry = db.query(PromptHistory).filter(
        PromptHistory.id == entry_id, PromptHistory.user_id == user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")

    db.delete(entry)
    db.commit()
    return


@app.delete("/history", status_code=204)
def clear_history(
    user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Clear all prompt history for the logged-in user."""
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(PromptHistory).filter(PromptHistory.user_id == user.id).delete()
    db.commit()
    return
