from typing import Optional
from pydantic import BaseModel

class ChatStart(BaseModel):
    user_uuid : str
    title : Optional[str] = None

class ChatAsk(BaseModel):
    user_uuid : str
    message : str
    chat_id : Optional[str] = None

class ChatTitleRequest(BaseModel):
    user_uuid : str
    chat_id : str
    message : str

class ChatResponse(BaseModel):
    chat_id : str
    answer : str