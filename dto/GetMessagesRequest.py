from pydantic import BaseModel

class   GetMessagesRequest(BaseModel):
    conversation_id: int
    user_id: int