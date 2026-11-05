from typing import Annotated

from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from fastapi.params import Depends
from starlette.requests import HTTPConnection

from ..models import ExplorerRequest, UserRequest
from ..dependencies import get_da_ma_multiagent_service
from ..services import manager, DataManagerMultiAgentService
from ..repositories import ExplorerHandlerImpl

def _get_root_struct(connection: HTTPConnection) -> ExplorerHandlerImpl:
    return connection.app.state.explorer_handler

router = APIRouter()

@router.get("/test")
def test_route():
    return {
        "status": "success",
    }

@router.post("/explorer/tree")
async def toggle_dir_content(explorer_request: ExplorerRequest, response: Response,
                      dama_service: Annotated[DataManagerMultiAgentService, Depends(get_da_ma_multiagent_service)],
                      ex_hand: Annotated[ExplorerHandlerImpl, Depends(_get_root_struct)]
                    ):

    result = await dama_service.toggle_explorer(explorer_request, ex_hand)

    if not result.error:
        ws_response = await dama_service.build_to_ws_response(ex_hand)
        await manager.broadcast(ws_response)

    response.status_code = result.status_code
    return result


@router.post("/agent")
async def call_agent(user_request: UserRequest, response: Response,
                     dama_service: Annotated[DataManagerMultiAgentService, Depends(get_da_ma_multiagent_service)],
                     ex_hand: Annotated[ExplorerHandlerImpl, Depends(_get_root_struct)]
                     ):

    result = await dama_service.launch_agents(user_request, ex_hand)

    if not result.error and result.activate_ws:
        ws_response = await dama_service.build_to_ws_response(ex_hand)
        await manager.broadcast(ws_response)

    response.status_code = result.status_code
    return result



@router.post("/open-file")
async def open_resource(explorer_request: ExplorerRequest, response: Response,
                      dama_service: Annotated[DataManagerMultiAgentService, Depends(get_da_ma_multiagent_service)]
                    ):

    result = await dama_service.open_file(explorer_request)
    response.status_code = result.status_code

    return result




@router.websocket("/ws/live-data")
async def websocket_endpoint(websocket: WebSocket,
                             dama_service: Annotated[DataManagerMultiAgentService, Depends(get_da_ma_multiagent_service)],
                             ex_hand: Annotated[ExplorerHandlerImpl, Depends(_get_root_struct)]
                             ):
    await manager.connect(websocket)
    result = await dama_service.build_to_ws_response(ex_hand)

    await websocket.send_json(result.model_dump())

    try:
        while True:
            # Mantiene el WebSocket abierto escuchando desconexiones de manera eficiente.
            # Las interfaces aquí solo ESCUCHAN (no necesitan enviar texto por aquí).
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


