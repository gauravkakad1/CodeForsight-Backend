from pydantic import BaseModel
class CreateAccountRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str