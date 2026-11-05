from typing import Annotated, Any, Dict, List, TypedDict, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

def update_progress(current: dict, new_data: dict) -> dict:
    if current is None:
        current = {}
    return {**current, **new_data}


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    extracted_data: List[Dict[str, Any]]
    next_agent: str
    remaining_steps: int
    error: Optional[str]
    progress: Annotated[Dict[str, str], update_progress]


class SupervisorDesition(BaseModel):
    next: str = Field(description="next agent to invoke: 'data_extractor_agent', 'files_manager_agent', 'reports_manager_agent', or 'END'")
    instruction_to_agent: str = Field(description="The specific task or text fragment that the agent must process")


class SupervisorAgentResponse(BaseModel):
    error: bool
    content: Optional[SupervisorDesition]
    message: str