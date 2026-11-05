from abc import ABC, abstractmethod

from ..models import APIAgentsResponse, UserRequest, ExplorerRequest, FilesManagerResponseWS
from ..repositories import ExplorerHandler


class DataManagerMultiAgentService(ABC):
    @abstractmethod
    async def launch_agents(self, user_request: UserRequest, ex_hand: ExplorerHandler) -> APIAgentsResponse:
        pass

    @abstractmethod
    async def toggle_explorer(self, explorer_request: ExplorerRequest, ex_hand: ExplorerHandler) -> APIAgentsResponse:
        pass


    @abstractmethod
    async def build_to_ws_response(self, ex_hand: ExplorerHandler) -> FilesManagerResponseWS:
        pass

    @abstractmethod
    async def open_file(self, explorer_request: ExplorerRequest) -> APIAgentsResponse:
        pass