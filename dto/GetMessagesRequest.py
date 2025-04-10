from pydantic import BaseModel

class   GetMessagesRequest(BaseModel):
    conversation_id: str
    user_id: str