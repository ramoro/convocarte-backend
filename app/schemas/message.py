from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CreateMessage(BaseModel):
    content: str
    receiver_id: int
    postulation_id: int

class Message(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    postulation_id: int
    files: str
    state: str
    created_at: datetime
    sender_fullname: Optional[str] = None
    sender_profile_picture: Optional[str] = None
    previous_message_id: Optional[int] = None

class UpdatedMessage(BaseModel):
    content: Optional[str] = None
    state: Optional[str] = None
    files: Optional[str] = None
    previous_message_id: Optional[int] = None