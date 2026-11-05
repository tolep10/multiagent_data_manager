from typing import Annotated

from fastapi.params import Depends

from ..services import DataManagerMultiAgentService, DataManagerMultiagentServiceImpl
from ..agents import DataManagerMultiAgentsGraph



def get_graph() -> DataManagerMultiAgentsGraph:
    return DataManagerMultiAgentsGraph()

def get_da_ma_multiagent_service(graph: Annotated[DataManagerMultiAgentsGraph, Depends(get_graph)]) -> DataManagerMultiAgentService:
    return DataManagerMultiagentServiceImpl(graph)