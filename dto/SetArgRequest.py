from pydantic import BaseModel
class SetArgRequest(BaseModel):
    key : str
    val : str


    