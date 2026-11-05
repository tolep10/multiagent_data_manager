import asyncio
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from .data_manager_multiagent_service import DataManagerMultiAgentService
from ..models import ExplorerRequest, APIAgentsResponse, UserRequest, FilesManagerResponseWS
from ..repositories import ExplorerHandler
from ..agents import DataManagerMultiAgentsGraph

from ..utils import settings


class DataManagerMultiagentServiceImpl(DataManagerMultiAgentService):
    def __init__(self, graph: DataManagerMultiAgentsGraph):
        self._graph = graph
        self._explorer_lock = asyncio.Lock()



    async def launch_agents(self, user_request: UserRequest, ex_hand: ExplorerHandler) -> APIAgentsResponse:
        try:
            api_response = APIAgentsResponse(error=False, content="success", status_code=200, activate_ws=False)
            if not self._graph:
                raise RuntimeError("ERROR: graph not initialized")

            workflow: Optional[CompiledStateGraph] = self._graph.get_workflow()

            if not workflow:
                raise RuntimeError("ERROR: workflow not initialized")

            initial_state = {
                "messages": [HumanMessage(content=user_request.user_request)],
                "extracted_data": [],
                "next_agent": "",
                "remaining_steps": 15,
                "error": None,
                "progress": {},
            }

            response = await workflow.ainvoke(initial_state)

            if response.get("error"):
                raise RuntimeError(response["error"])

            api_response.content = response["messages"][-1].content
            api_response.status_code = 200

            act_ws = await self._update_explorer(ex_hand)
            api_response.activate_ws = act_ws

            return api_response
        except Exception as e:
            message_error = f"ERROR: {e}"
            print(message_error)
            return APIAgentsResponse(error=True, content="An error occurred; we apologize for the inconvenience.", status_code=500, activate_ws=False)



    async def toggle_explorer(self, explorer_request: ExplorerRequest, ex_hand: ExplorerHandler) -> APIAgentsResponse:
        result = await ex_hand.toggle_dir(explorer_request.relative_path)

        if result.error:
            if result.status_code == 400:
                result.content = "El path no es válido"
            elif result.status_code == 403:
                result.content = "No se puede acceder al directorio especificado"
            elif result.status_code == 404:
                result.content = "El path no existe"
            elif result.status_code == 500:
                result.content = "Ocurrió un error de nuestro lado, lamentamos el inconveniente"

        return result


    async def build_to_ws_response(self, ex_hand: ExplorerHandler) -> FilesManagerResponseWS:
        init_conn_resp = FilesManagerResponseWS(error=False, content=None, status_code=200)

        try:
            init_conn_resp.content = await ex_hand.get_root_struct()

            return init_conn_resp
        except Exception as e:
            print(e)
            init_conn_resp.error = True
            init_conn_resp.status_code = 500
            return init_conn_resp



    async def open_file(self, explorer_request: ExplorerRequest) -> APIAgentsResponse:
        try:
            path_file = explorer_request.relative_path

            full_path = (Path(settings.REPORTS_PATH) / path_file).resolve()

            if not full_path.is_relative_to(Path(settings.REPORTS_PATH)):
                return APIAgentsResponse(error=True, content="ERROR: access denied outside the sandbox.",
                                            status_code=400, activate_ws=False)

            if not full_path.exists() or not full_path.is_file():
                return APIAgentsResponse(error=True,
                                            content=f"ERROR: the element '{path_file}' not exists or not is a valid file.",
                                            status_code=404, activate_ws=False)

            if platform.system() == "Windows":
                os.startfile(str(full_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", str(full_path)])
            else:  # Linux
                subprocess.call(["xdg-open", str(full_path)])

            return APIAgentsResponse(error=False, content="success", status_code=200, activate_ws=False)
        except Exception as e:
            msg_error = f"ERROR: to open file: {e}"
            print(msg_error)
            return APIAgentsResponse(error=True, content=msg_error, status_code=500, activate_ws=False)



    async def _update_explorer(self, ex_hand: ExplorerHandler) -> bool:
        async with self._explorer_lock:
            try:
                paths_to_reload = await settings.get_paths_to_reload()

                if paths_to_reload:
                    for path in paths_to_reload:
                        await ex_hand.load_path_content(path)

                    await settings.clean_paths_to_reload()

                    return True

                return False
            except Exception as e:
                print(f"ERROR to update explorer: {e}")
                return False