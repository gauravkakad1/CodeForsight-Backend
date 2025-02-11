from pydantic import BaseModel

class ChatRequest(BaseModel):
    input_question: str