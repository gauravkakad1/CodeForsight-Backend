from pydantic import BaseModel
class CreateConversationRequest(BaseModel):
    user_id : str
    conversation_name : str 
