from abc import ABC
from pathlib import Path
from typing import List, Literal, Union
from pydantic import BaseModel, computed_field


# class Element(ABC):
#     def __init__(self, path: str):
#         self.path: str = path
#         self.name: str = Path(path).name
#
#
# class MyFile(Element):
#     def __init__(self, path: str):
#         super().__init__(path)
#         self.ext: str = Path(path).suffix
#
#
# class MyDir(Element):
#     def __init__(self, path: str):
#         super().__init__(path)
#         self.dirs: List[Element] = []




# 1. Clase Base (Hereda de BaseModel y ABC)
class Element(BaseModel, ABC):
    path: str

    # Reemplaza el cálculo del __init__ de forma dinámica y eficiente
    @computed_field
    @property
    def name(self) -> str:
        return Path(self.path).name


# 2. Clase Archivo
class MyFile(Element):
    # Usamos un literal como 'tipo' para que Pydantic diferencie archivos de carpetas
    type: Literal["file"] = "file"

    @computed_field
    @property
    def ext(self) -> str:
        return Path(self.path).suffix


# 3. Clase Directorio (Recursiva)
class MyDir(Element):
    type: Literal["dir"] = "dir"

    # La lista ahora acepta explícitamente instancias de MyDir o MyFile
    dirs: List[Union["MyDir", MyFile]] = []


# ¡Crucial! Reconstruir el modelo para resolver la autoreferencia de MyDir
MyDir.model_rebuild()
