from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    prompts = relationship("Prompt", back_populates="owner", cascade="all, delete-orphan")
    history = relationship("PromptHistory", back_populates="owner", cascade="all, delete-orphan")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lazy_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    prompt_type = Column(String, default="text")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="prompts")


class PromptHistory(Base):
    __tablename__ = "prompt_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lazy_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    prompt_type = Column(String, default="text")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="history")
