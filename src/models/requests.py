from pydantic import BaseModel


class UserRequest(BaseModel):
    user_request: str


class ExplorerRequest(BaseModel):
    relative_path: str = ""