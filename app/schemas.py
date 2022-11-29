from pydantic import BaseModel

class UserChangePassword(BaseModel):
    token: str
    password: str
    new_password: str

class ChangePasswordOut(BaseModel):
    password_changed: bool

class UserOut(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    token_id: str
