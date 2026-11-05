from abc import ABC, abstractmethod

from ..models import APIAgentsResponse, MyDir

class ExplorerHandler(ABC):

    @abstractmethod
    async def toggle_dir(self, relative_path: str) -> APIAgentsResponse:
        ...

    @abstractmethod
    async def load_path_content(self, relative_path: str) -> None:
        ...

    @abstractmethod
    async def get_root_struct(self) -> MyDir:
        ...