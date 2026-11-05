from pydantic import BaseModel, Field


class DirFileOperations(BaseModel):
    relative_path: str = Field(description="Path of the element on which the selected action will be performed")


class DirPathBuild(BaseModel):
    relative_path: str = Field(description="Path of the directory on which the selected action will be performed")
    path_new: str = Field(description="Path of the directory or directories to be created relative to relative_path")


class MoveCopyOperations(BaseModel):
    relative_path_origin: str = Field(description="Path of the element to copy or move")
    relative_path_dest: str = Field(description="Destination directory path")