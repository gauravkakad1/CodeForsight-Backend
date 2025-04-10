from pydantic import BaseModel
class GetConversationsRequest(BaseModel):
    user_id: str