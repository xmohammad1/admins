from pydantic import BaseModel

class Admin(BaseModel):
    username: str
    is_sudo: bool
    telegram_id: int | None
    discord_webhook: int | None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"