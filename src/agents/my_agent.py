from abc import ABC, abstractmethod
from typing import Optional


from langgraph.graph.state import CompiledStateGraph


class MyAgent(ABC):
    def __init__(self):
        self.agent: Optional[CompiledStateGraph] = None


    @abstractmethod
    def build_agent(self) -> None:
        ...



