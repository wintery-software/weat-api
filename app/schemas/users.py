from pydantic import BaseModel


class UserForm(BaseModel):
    username: str
    password: str
