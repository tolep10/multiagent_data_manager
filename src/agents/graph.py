from typing import Optional, Dict, Any

from langchain_core.messages import AIMessage
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph

from .data_extractor_agent import DataExtractorAgent
from .files_manager_agent import FilesManagerAgent
from .report_manager_agent import ReportManagerAgent
from .supervisor_agent import SupervisorAgent

from ..models import AgentState, SupervisorDesition, SupervisorAgentResponse, AgentResponse

class DataManagerMultiAgentsGraph:
    def __init__(self):
        self._graph: Optional[CompiledStateGraph] = None
        self._extractor_agent: DataExtractorAgent = DataExtractorAgent()
        self._files_manager_agent: FilesManagerAgent = FilesManagerAgent()
        self._report_manager_agent: ReportManagerAgent = ReportManagerAgent()
        self._supervisor_agent: SupervisorAgent = SupervisorAgent()


    async def supervisor_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            messages = state["messages"]
            progress = state.get("progress", {})
            response: SupervisorAgentResponse = await self._supervisor_agent.get_desition(messages, progress)

            new_messages = []

            if response.error or not response.content:
                raise RuntimeError(response.message)


            desition: SupervisorDesition = response.content
            #print(f"agent: {desition.next}")
            #print(f"instruction: {desition.instruction_to_agent}")

            if desition.next != "END":
                new_messages.append(AIMessage(
                    content=f"Assignation to {desition.next}:{desition.instruction_to_agent}",
                    name="Supervisor"))

            return {
                "messages": new_messages,
                "next_agent": desition.next
            }

        except Exception as e:
            message_error = f"Supervisor Node Error: {e}"
            print(message_error)
            return {
                "error": message_error
            }


    async def extractor_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            messages = state["messages"]
            progress = state.get("progress", {})
            response: AgentResponse = await self._extractor_agent.launch_agent(messages, progress)

            if response.error or not response.content:
                raise RuntimeError(response.message)

            extracted_data = response.content.get("extracted_data", [])
            curr_total_messages = len(messages)
            new_messages = response.content["messages"][curr_total_messages:]
            new_progress = response.content.get("progress", {})


            return {
                "messages": new_messages,
                "extracted_data": extracted_data,
                "progress": new_progress,
            }
        except Exception as e:
            message_error = f"Node Error: {e}"
            print(message_error)
            return {
                "error": message_error
            }


    async def reports_manager_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            messages = state["messages"]
            extracted_data = state.get("extracted_data", [])
            progress = state.get("progress", {})
            response: AgentResponse = await self._report_manager_agent.launch_agent(messages, extracted_data, progress)

            if response.error or not response.content:
                raise RuntimeError(response.message)

            curr_total_messages = len(messages)
            new_messages = response.content["messages"][curr_total_messages:]
            new_progress = response.content.get("progress", {})

            return {
                "messages": new_messages,
                "progress": new_progress,
            }
        except Exception as e:
            message_error = f"Node Error: {e}"
            print(message_error)
            return {
                "error": message_error
            }


    async def files_manager_node(self, state: AgentState) -> Dict[str, Any]:
        try:
            messages = state["messages"]
            progress = state.get("progress", {})
            response: AgentResponse = await self._files_manager_agent.launch_agent(messages, progress)

            if response.error or not response.content:
                raise RuntimeError(response.message)

            curr_total_messages = len(messages)
            new_messages = response.content["messages"][curr_total_messages:]
            new_progress = response.content.get("progress", {})

            return {
                "messages": new_messages,
                "progress": new_progress,
            }
        except Exception as e:
            message_error = f"Node Error: {e}"
            print(message_error)
            return {
                "error": message_error
            }


    def build_graph(self) -> None:
        # noinspection PyTypeChecker
        builder = StateGraph(AgentState)
        # noinspection PyTypeChecker
        builder.add_node("supervisor_agent", self.supervisor_node)
        # noinspection PyTypeChecker
        builder.add_node("data_extractor_agent", self.extractor_node)
        # noinspection PyTypeChecker
        builder.add_node("reports_manager_agent", self.reports_manager_node)
        # noinspection PyTypeChecker
        builder.add_node("files_manager_agent", self.files_manager_node)

        builder.add_edge(START,"supervisor_agent")
        builder.add_conditional_edges(
            "supervisor_agent",
            DataManagerMultiAgentsGraph._router_after_supervisor,
            {
                "data_extractor_agent":"data_extractor_agent",
                "reports_manager_agent":"reports_manager_agent",
                "files_manager_agent":"files_manager_agent",
                END:END
            }
        )
        builder.add_edge("data_extractor_agent", "supervisor_agent")
        builder.add_edge("reports_manager_agent", "supervisor_agent")
        builder.add_edge("files_manager_agent", "supervisor_agent")

        self._graph = builder.compile()



    def get_workflow(self) -> Optional[CompiledStateGraph]:
        try:
            if not self._graph:
                self.build_graph()

            return self._graph
        except Exception as e:
            print(f"Error to build graph: {str(e)}")
            return None



    @staticmethod
    def _router_after_supervisor(state: AgentState) -> str:
        if state.get("error") or state["next_agent"] == "END":
            return END

        return state["next_agent"]
