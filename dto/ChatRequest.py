from pydantic import BaseModel

class ChatRequest(BaseModel):
    input_question: str
    user_id:str
    conversation_id:str