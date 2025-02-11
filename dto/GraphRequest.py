from pydantic import BaseModel

class GraphRequest(BaseModel):
    dot_code: str