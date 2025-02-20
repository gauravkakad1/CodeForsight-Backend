from pydantic import BaseModel

class ChatRequest(BaseModel):
    input_question: str
    user_id:int
    conversation_id:int