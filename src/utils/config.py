import asyncio
import os
from typing import Optional, List, ClassVar

from dotenv import load_dotenv
from dataclasses import dataclass

from langchain_ollama import ChatOllama
from pydantic import SecretStr

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


load_dotenv()

@dataclass(frozen=True)
class Settings:
    REPORTS_PATH: str = "C:\\Users\\tolep\\Documents\\proyectos\\IA_projects\\langchain_langgraph_projects\\data_manager_multiagent\\xlsx_reports"

    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT") or 5432)

    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_API_KEY_2: Optional[str] = os.getenv("GROQ_API_KEY_2")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEY_2: Optional[str] = os.getenv("GEMINI_API_KEY_2")
    OLLAMA_API_KEY: Optional[str] = os.getenv("OLLAMA_API_KEY")

    LLM_AGENT = None
    LLM_AGENT_QWEN = None
    LLM_SUPERVISOR = None
    LLM_AGENT_OLLAMA = None

    PATHS_TO_RELOAD: ClassVar[List[str]] = []
    list_lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    def validate_db_vars(cls) -> bool:
        required_keys = [
            ("DB_NAME",cls.DB_NAME),
            ("DB_USER", cls.DB_USER),
            ("DB_PASSWORD", cls.DB_PASSWORD),
            ("DB_HOST", cls.DB_HOST)
        ]

        missing_keys = [key for key, value in required_keys if not value]

        if missing_keys:
            print(f"Error, next configurations are missing: {", ".join(missing_keys)}")
            return False

        return True

    @classmethod
    def get_llm_supervisor(cls) -> Optional[ChatGoogleGenerativeAI]:
        try:
            if cls.GEMINI_API_KEY:
                if not cls.LLM_SUPERVISOR:
                    cls.LLM_SUPERVISOR = ChatGoogleGenerativeAI(api_key=cls.GEMINI_API_KEY, model="gemini-2.5-flash", temperature=0)

                return cls.LLM_SUPERVISOR
            else:
                raise RuntimeError("Model Supervisor is not set")
        except Exception as e:
            print(e)
            return None




    @classmethod
    def get_llm_agent(cls) -> Optional[ChatGroq]:
        try:
            if cls.GROQ_API_KEY:
                secret_groq = SecretStr(cls.GROQ_API_KEY)

                if not cls.LLM_AGENT:
                    cls.LLM_AGENT = ChatGroq(api_key=secret_groq, model="openai/gpt-oss-120b", temperature=0)

                return cls.LLM_AGENT
            else:
                raise RuntimeError("Model Agent is not set")

        except Exception as e:
            print(e)
            return None


    @classmethod
    def get_llm_agent_qwen(cls) -> Optional[ChatGroq]:
        try:
            if cls.GROQ_API_KEY_2:
                secret_groq = SecretStr(cls.GROQ_API_KEY_2)

                if not cls.LLM_AGENT_QWEN:
                    cls.LLM_AGENT_QWEN = ChatGroq(api_key=secret_groq, model="openai/gpt-oss-20b", temperature=0)

                return cls.LLM_AGENT_QWEN
            else:
                raise RuntimeError("Model Agent is not set")

        except Exception as e:
            print(e)
            return None


    @classmethod
    def get_llm_agent_ollama(cls) -> Optional[ChatOllama]:
        try:
            if cls.OLLAMA_API_KEY:
                if not cls.LLM_AGENT_OLLAMA:
                    cls.LLM_AGENT_OLLAMA = ChatOllama(model="gemma4:31b", base_url="https://ollama.com", reasoning=False, num_predict=1024,
                                                      client_kwargs={
                                                          "headers":{
                                                              "Authorization": f"Bearer {cls.OLLAMA_API_KEY}"
                                                          }
                                                      })

                return cls.LLM_AGENT_OLLAMA
            else:
                raise RuntimeError("Model Agent is not set")

        except Exception as e:
            print(e)
            return None


    @classmethod
    async def get_paths_to_reload(cls):
        async with cls.list_lock:
            return cls.PATHS_TO_RELOAD


    @classmethod
    async def update_paths_to_reload(cls, paths_to_reload: List[str]):
        async with cls.list_lock:
            cls.PATHS_TO_RELOAD += paths_to_reload


    @classmethod
    async def clean_paths_to_reload(cls):
        async with cls.list_lock:
            cls.PATHS_TO_RELOAD.clear()





# Instancia única para importar en todo el proyecto
settings = Settings()
