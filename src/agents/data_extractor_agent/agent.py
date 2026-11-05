from typing import List, Dict

from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, AIMessage

from .tools import data_extractor_agent_tools
from .prompts import extractor_system_prompt
from ..my_agent import MyAgent
from ...utils import settings
from ...models import AgentState, AgentResponse


class DataExtractorAgent(MyAgent):
    def __init__(self):
        super().__init__()
        self.llm = settings.get_llm_agent()


    def build_agent(self):
        self.agent = create_agent(
            model=self.llm,
            tools=data_extractor_agent_tools,
            system_prompt=extractor_system_prompt,
            state_schema=AgentState,
            name="data_extractor_agent"
        )

    async def launch_agent(self, messages: List[BaseMessage], progress: Dict[str, str]) -> AgentResponse:
        try:
            if not self.agent:
                self.build_agent()

            if self.agent:
                result = await self.agent.ainvoke({
                    "messages": messages,
                    "progress": progress
                })

                return AgentResponse(error=False, content=result, message="success")
            else:
                raise RuntimeError(f"Something went wrong with the agent data_extractor_agent")

        except Exception as e:
            msg_error = f"ERROR: {str(e)}"
            print(msg_error)
            return AgentResponse(error=True, content=[AIMessage(content=msg_error)], message=msg_error)



