from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

# --- Authentication Models ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Chat Models ---
class ChatMessageInput(BaseModel):
    message: str

class ChatMessageOutput(BaseModel):
    sender: str # 'user' or 'ai'
    message: str

class ChatState(BaseModel):
    stage: str = "start"
    condition: Optional[str] = None
    history: List[Dict[str, Any]] = [] # Stores Gemini conversation history [{role:'user'/'model', parts: ['text']}]
    question_count: int = 0 # To track assessment questions