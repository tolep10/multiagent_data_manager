import asyncio
from typing import Optional
from pathlib import Path

from .explorer_handler import ExplorerHandler
from ..models import MyDir, MyFile, Element, APIAgentsResponse
from ..utils import settings

class ExplorerHandlerImpl(ExplorerHandler):

    def __init__(self):
        self.path_base = Path(settings.REPORTS_PATH)
        self.root_struct: MyDir = MyDir(path="")
        self.tree_lock = asyncio.Lock()


    async def toggle_dir(self, relative_path: str) -> APIAgentsResponse:
        async with self.tree_lock:
            try:
                target_path = self.path_base / relative_path

                if not target_path.is_relative_to(self.path_base) or not target_path.is_dir():
                    return APIAgentsResponse(error=True, content="", status_code=400, activate_ws=False)


                if relative_path == "":
                    current_dir = self.root_struct
                else:
                    if not self.root_struct.dirs:
                        return APIAgentsResponse(error=True, content="", status_code=403, activate_ws=False)

                    current_dir: Optional[Element] = self._search_dir_in_struct(relative_path)


                if not current_dir or not isinstance(current_dir, MyDir):
                    return APIAgentsResponse(error=True, content="", status_code=404, activate_ws=False)


                if current_dir.dirs:
                    current_dir.dirs.clear()
                else:
                    self._loader_dir_content(target_path, current_dir)


                return APIAgentsResponse(error=False, content="", status_code=200, activate_ws=True)

            except Exception as e:
                print(e)
                return APIAgentsResponse(error=True, content="", status_code=500, activate_ws=False)



    async def load_path_content(self, relative_path: str) -> None:
        async with self.tree_lock:
            try:
                if not self.root_struct.dirs:
                    self._loader_dir_content(self.path_base, self.root_struct)

                if self.root_struct.dirs and relative_path == "":# el dir base es el unico que no se debe recargar
                    self._process_reload_root()
                    return


                fragments = Path(relative_path).parts
                partial = []
                previous_dir = None

                for i in range(len(fragments)):
                    partial.append(fragments[i])
                    curr_path = "/".join(partial)
                    element = self._search_element_in_dir(curr_path, previous_dir)

                    if element and isinstance(element, MyDir):
                        if element.dirs and i == len(fragments) - 1:
                            element.dirs.clear()

                        target_path = Path(self.path_base / curr_path)
                        self._loader_dir_content(target_path, element)
                        previous_dir = element
                    else:
                        break

            except Exception as e:
                print(f"Error al cargar el contenido de los directorios: {e}")




    def _loader_dir_content(self, target_path: Path, current_dir: MyDir) -> None:
        index_from_cut = len(str(self.path_base)) + 1 # + 1 por la \ final

        for item in target_path.iterdir():
            path_to_element = str(item)[index_from_cut:]

            if item.is_dir() :
                current_dir.dirs.append(MyDir(path=path_to_element))
            elif item.is_file() :
                current_dir.dirs.append(MyFile(path=path_to_element))



    def _search_element_in_dir(self, partial_path: str, start_dir: Optional[MyDir] = None) -> Optional[Element]:
        current_dir = start_dir if start_dir else self.root_struct
        partial_path = Path(partial_path) #convertir a Path para lidiar con los separadores

        for c_dir in current_dir.dirs:
            if c_dir.path == str(partial_path):
                return c_dir

        return None


    def _process_reload_root(self) -> None:
        root_copy: MyDir = MyDir(path=str(self.path_base))
        self._loader_dir_content(self.path_base, root_copy)

        dic_dir_orig = {element.path: element for element in self.root_struct.dirs}
        dic_dir_copy = {element.path: element for element in root_copy.dirs}

        keys_orig = set(dic_dir_orig.keys())
        keys_copy = set(dic_dir_copy.keys())

        keys_to_delete = keys_orig - keys_copy  # Están en origen pero no en copia
        keys_to_add = keys_copy - keys_orig  # Están en copia pero no en origen


        self.root_struct.dirs = [
            obj for obj in self.root_struct.dirs
            if obj.path not in keys_to_delete
        ]

        for k in keys_to_add:
            self.root_struct.dirs.append(dic_dir_copy[k])



    def _search_dir_in_struct(self, relative_path: str) -> Optional[Element]:
        path_to_find = Path(relative_path)
        fragments = path_to_find.parts
        index = 1
        current_dir = self.root_struct
        continue_search = True

        while continue_search:
            if current_dir.path == str(path_to_find):
                return current_dir

            continue_search = False
            partial = Path("/".join(fragments[0:index]))

            for c_dir in current_dir.dirs:
                if isinstance(c_dir, MyDir):
                    if c_dir.path == str(partial):
                        current_dir = c_dir
                        index += 1
                        continue_search = True
                        break


        return None


    async def get_root_struct(self) -> MyDir:
        async with self.tree_lock:
            return self.root_struct















