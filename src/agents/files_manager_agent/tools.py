from pathlib import Path
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command

from ...models import DirFileOperations, DirPathBuild, MoveCopyOperations, FilesManagerToolsResponse
from .fm_agent_tools import FMAgentTools
from ...utils import settings

fm_tools = FMAgentTools()

@tool(args_schema=DirFileOperations)
async def find_element(relative_path: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Recursively search for an item within the sandbox directory.
    """
    try:
        cleaned_path = clean_path(relative_path)
        result: FilesManagerToolsResponse = await fm_tools.find_element(cleaned_path)

        return Command(
            update={
                "progress": {"element_found": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f'ERROR: find:{str(e)}'
        print(err)
        return Command(
            update={
                "progress": {"element_found": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )



@tool(args_schema=DirFileOperations)
async def delete_element(relative_path: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Removes the element passed as an argument.
    """
    try:
        cleaned_path = clean_path(relative_path)

        result: FilesManagerToolsResponse = await fm_tools.delete_element(cleaned_path)

        if not result.error:
            reload_path = get_last_path_part(cleaned_path)
            await settings.update_paths_to_reload([reload_path])


        return Command(
            update={
                "progress": {"element_deleted": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f'ERROR: delete: {str(e)}'
        print(err)
        return Command(
            update={
                "progress": {"element_deleted": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )



@tool(args_schema=MoveCopyOperations)
async def move_element(relative_path_origin: str, relative_path_dest: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Moves a given element to a specified path.
    """
    try:
        cleaned_path_origin = clean_path(relative_path_origin)
        cleaned_path_dest = clean_path(relative_path_dest)
        result: FilesManagerToolsResponse = await fm_tools.move_element(cleaned_path_origin, cleaned_path_dest)

        if not result.error:
            reload_path_origin = get_last_path_part(cleaned_path_origin)
            await settings.update_paths_to_reload([reload_path_origin, cleaned_path_dest])


        return Command(
            update={
                "progress": {"element_moved": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f"ERROR: move: {str(e)}"
        print(err)
        return Command(
            update={
                "progress": {"element_moved": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )



@tool(args_schema=MoveCopyOperations)
async def copy_element(relative_path_origin: str, relative_path_dest: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Copies a given item to a specified path.
    """
    try:
        cleaned_path_origin = clean_path(relative_path_origin)
        cleaned_path_dest = clean_path(relative_path_dest)
        result: FilesManagerToolsResponse = await fm_tools.copy_element(cleaned_path_origin, cleaned_path_dest)

        if not result.error:
            reload_path_origin = get_last_path_part(cleaned_path_origin)
            await settings.update_paths_to_reload([reload_path_origin, cleaned_path_dest])


        return Command(
            update={
                "progress": {"element_copied": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f"ERROR: copy: {str(e)}"
        print(err)
        return Command(
            update={
                "progress": {"element_copied": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )



@tool(args_schema=DirPathBuild)
async def create_dirs(relative_path: str, path_new: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """
    Create one or more directories.
    """
    try:
        cleaned_relative_path = clean_path(relative_path)
        cleaned_path_new = clean_path(path_new)
        result: FilesManagerToolsResponse = await fm_tools.create_dirs(cleaned_path_new)

        if not result.error:
            await settings.update_paths_to_reload([cleaned_relative_path])


        return Command(
            update={
                "progress": {"path_created": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f"ERROR: create: {str(e)}"
        print(err)

        return Command(
            update={
                "progress": {"path_created": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )


@tool(args_schema=DirFileOperations)
async def open_file(relative_path: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Open a file with the default application"""
    try:
        cleaned_path = clean_path(relative_path)

        result: FilesManagerToolsResponse = await fm_tools.open_file(cleaned_path)

        return Command(
            update={
                "progress": {"element_opened": result.content},
                "messages": [
                    ToolMessage(
                        content=result.content,
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    except Exception as e:
        err = f'ERROR: open file: {str(e)}'
        print(err)

        return Command(
            update={
                "progress": {"element_opened": f"ERROR: {str(e)}"},
                "messages": [
                    ToolMessage(
                        content=f"ERROR: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )



def clean_path(path: str) -> str:
    path = path.strip().lstrip(r"/\ ")

    return path


def get_last_path_part(relative_path: str) -> str:
    relative_path = Path(relative_path).parent

    return "" if str(relative_path) == "." else str(relative_path)


tools = [find_element, delete_element,
         move_element, copy_element, create_dirs, open_file]