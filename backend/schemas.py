from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str


class PromptRequest(BaseModel):
    prompt: str
    refinement: Optional[str] = None   # extra context from the right panel


class QuestionRequest(BaseModel):
    prompt: str
    prompt_type: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


class SavePromptRequest(BaseModel):
    lazy_prompt: str
    enhanced_prompt: str
    prompt_type: str


class PromptResponse(BaseModel):
    id: int
    lazy_prompt: str
    enhanced_prompt: str
    prompt_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class PromptHistoryResponse(BaseModel):
    id: int
    lazy_prompt: str
    enhanced_prompt: str
    prompt_type: str
    created_at: datetime

    class Config:
        from_attributes = True
