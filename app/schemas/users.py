from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True
