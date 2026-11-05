from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from .elements import MyDir


class FilesManagerResponseWS(BaseModel):
    """Object to ws"""
    error: bool
    content: Optional[MyDir]
    status_code: int


class AgentResponse(BaseModel):
    """Object returned to wrapped agent classes to be used in graph """
    error: bool
    content: Dict[str, Any] | Any
    message: Optional[str]


class FilesManagerToolsResponse(BaseModel):
    """Object returned for files manager tools """
    error: bool
    content: str



class APIAgentsResponse(BaseModel):
    """Object returned for service to router"""
    error: bool
    content: str
    status_code: int
    activate_ws: bool









