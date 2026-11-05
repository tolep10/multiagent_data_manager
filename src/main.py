from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from .repositories import ExplorerHandlerImpl
from .routes import router as multiagent_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el servidor
    app.state.explorer_handler = ExplorerHandlerImpl()
    yield
    # Se ejecuta al apagar el servidor (puedes limpiar memoria aquí)
    del app.state.explorer_handler.root_struct



origins = [
    "http://localhost:3000",      # React local
    "http://localhost:5173",      # Vite / Vue local
    "http://localhost:8000",
    "http://localhost:8001",
]

# 2. Agrega el middleware a tu aplicación
middleware = [
    Middleware(
        CORSMiddleware, # noqa
        allow_origins=origins,  # noqa
        allow_credentials=True, # noqa
        allow_methods=["*"],    # noqa
        allow_headers=["*"], # noqa
    )
]
app = FastAPI(lifespan=lifespan, middleware=middleware)
app.include_router(multiagent_router, prefix="/api")

@app.get("/")
def read_root():
    return {"Hello": "World"}