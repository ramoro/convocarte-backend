from pydantic import BaseModel    

class UserLogin(BaseModel):
    id: int
    email: str
    fullname: str
    profile_picture: str
    token: str
    token_type: str
