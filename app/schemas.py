from pydantic import BaseModel

class URLCreate(BaseModel):
    url : str

class URLResponse(BaseModel):
    short_code : str
    original_url : str
    clicks : int = 0
    created_at : str

