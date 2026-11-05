from typing import List, Dict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from google.api_core.exceptions import ResourceExhausted

from ...utils import settings
from ...models import SupervisorDesition, SupervisorAgentResponse
from .prompts import supervisor_system_prompt

class SupervisorAgent:
    def __init__(self):
        self._llm = settings.get_llm_supervisor()

    # noinspection PyTypeChecker
    # noinspection PyCallingNonCallable
    @retry(
        retry=retry_if_exception_type(ResourceExhausted),
        wait=wait_exponential(multiplier=2, min=10, max=60),
        stop=stop_after_attempt(5)
    )
    async def get_desition(self, messages: List[BaseMessage], progress: Dict[str, str]) -> SupervisorAgentResponse:
        try:
            if not self._llm:
                raise RuntimeError("LLM supervisor not initialized")

            original_user_request = messages[0].content
            current_progress = progress
            supervisor_payload = [
                SystemMessage(content=supervisor_system_prompt),
                HumanMessage(content=f"User Goal: {original_user_request}\n\nCurrent Workflow Progress: {current_progress}"),
            ]

            desition: SupervisorDesition = await self._llm.with_structured_output(SupervisorDesition).ainvoke(supervisor_payload)


            return SupervisorAgentResponse(error=False, content=desition, message="success")

        except Exception as e:
            message_error = f"ERROR: {e}"
            print(message_error)
            return SupervisorAgentResponse(error=True, message=message_error, content=None)
