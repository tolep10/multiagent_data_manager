import os
import platform
import shutil
import subprocess
from collections import deque
from pathlib import Path

from ...utils import settings
from ...models import FilesManagerToolsResponse


class FMAgentTools:
    def __init__(self):
        self._sandbox_folder = settings.REPORTS_PATH
        self._sandbox_path = Path(self._sandbox_folder).resolve()


    async def find_element(self, f_or_d_name: str) -> FilesManagerToolsResponse:
        """
        Recursively search for an item within the sandbox directory.
        """
        try:
            # Si el modelo envía "C:/Users/tolep/Pictures", force a que solo sea el nombre
            target_name = Path(f_or_d_name).name

            key_words = [p for p in target_name.lower().split() if len(p) > 2]

            if not key_words:
                return FilesManagerToolsResponse(error=True, content="ERROR: file name is not valid.")

            founds = []
            queue_dirs = deque([self._sandbox_path])

            while queue_dirs:
                current = queue_dirs.popleft()

                try:
                    if not current.resolve().is_relative_to(self._sandbox_path):
                        continue

                    for entry in current.iterdir():
                        if entry.name.lower() == target_name.lower():
                            founds.append(str(entry.relative_to(self._sandbox_path)))
                        else:
                            if entry.is_file():
                                if all(word in entry.name.lower() for word in key_words):
                                    founds.append(str(entry.relative_to(self._sandbox_path)))

                        if entry.is_dir() and not entry.is_symlink():
                            queue_dirs.append(entry)

                except (PermissionError, OSError):
                    continue

            if not founds:
                return FilesManagerToolsResponse(error=False, content=f"SUCCESS: file {target_name} not found")

            if len(founds) == 1:
                return FilesManagerToolsResponse(error=False, content=f"SUCCESS: file {target_name} founded in {founds[0]}")

            return FilesManagerToolsResponse(error=False, content="SUCCESS: multiple matches were found.:\n" + "\n".join(founds))

        except Exception as e:
            msg_error = f"ERROR: {str(e)}"
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)



    async def delete_element(self, relative_path: str) -> FilesManagerToolsResponse:
        """
        Removes the element passed as an argument.
        """
        try:
            target_path = (self._sandbox_path / relative_path).resolve()

            if not target_path.is_relative_to(self._sandbox_path):
                return FilesManagerToolsResponse(error=True, content="ERROR: Access denied, outside the sandbox.")

            if not target_path.exists():
                return FilesManagerToolsResponse(error=True, content=f"ERROR: '{relative_path}' doesn't exist.")

            if target_path.is_dir():
                shutil.rmtree(target_path)
            elif target_path.is_file():
                target_path.unlink()

            return FilesManagerToolsResponse(error=False, content='SUCCESS: item successfully deleted')

        except Exception as e:
            msg_error = f'ERROR: something was wrong during deletion: {str(e)}'
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)



    async def move_element(self, relative_path_origin: str, relative_path_dest: str) -> FilesManagerToolsResponse:
        """
        Moves a given element to a specified path.
        """
        try:
            origin_path = (self._sandbox_path / relative_path_origin).resolve()
            dest_folder = (self._sandbox_path / relative_path_dest).resolve()

            if not origin_path.is_relative_to(self._sandbox_path) or not dest_folder.is_relative_to(self._sandbox_path):
                return FilesManagerToolsResponse(error=True, content="ERROR: Access denied, outside the sandbox.")

            if not origin_path.exists():
                return FilesManagerToolsResponse(error=True, content="ERROR: the origin doesn't exists.")

            if dest_folder.exists() and not dest_folder.is_dir():
                return FilesManagerToolsResponse(error=True, content=f"ERROR: already exists a file in the destiny '{relative_path_dest}'.")

            dest_folder.mkdir(parents=True, exist_ok=True)

            final_path = dest_folder / origin_path.name

            if final_path.exists():
                return FilesManagerToolsResponse(error=True, content=f"ERROR: already an element named '{origin_path.name}' in the destiny path.")

            shutil.move(str(origin_path), str(final_path))
            return FilesManagerToolsResponse(error=False, content=f"SUCCESS: the element moved to {relative_path_dest}/")

        except Exception as e:
            msg_error = f"ERROR: {str(e)}"
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)



    async def copy_element(self, relative_path_origin: str, relative_path_dest: str) -> FilesManagerToolsResponse:
        """
        Copies a given item to a specified path.
        """
        try:
            origin_path = (self._sandbox_path / relative_path_origin).resolve()
            dest_folder = (self._sandbox_path / relative_path_dest).resolve()

            if not origin_path.is_relative_to(self._sandbox_path) or not dest_folder.is_relative_to(self._sandbox_path):
                return FilesManagerToolsResponse(error=True, content="ERROR: Access denied, outside the sandbox.")

            if not origin_path.exists():
                return FilesManagerToolsResponse(error=True, content="ERROR: origin doesn't exists.")

            if dest_folder.exists() and not dest_folder.is_dir():
                return FilesManagerToolsResponse(error=True, content=f"ERROR: ERROR: already exists a file in the destiny '{relative_path_dest}'.")

            dest_folder.mkdir(parents=True, exist_ok=True)

            final_path = dest_folder / origin_path.name

            if final_path.exists():
                counter = 0
                base_name = origin_path.stem
                extension = origin_path.suffix

                while final_path.exists():
                    counter += 1
                    final_path = dest_folder / f'{base_name}_{counter}{extension}'

            if origin_path == final_path or origin_path in final_path.parents:
                return FilesManagerToolsResponse(error=True, content="ERROR: Operation not permitted. A folder cannot be copied into itself.")

            if origin_path.is_dir():
                shutil.copytree(origin_path, final_path)
            else:
                shutil.copy2(origin_path, final_path)

            return FilesManagerToolsResponse(error=False, content=f"SUCCESS: the element was copied in {relative_path_dest}/")

        except Exception as e:
            msg_error = f"ERROR: {str(e)}"
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)



    async def create_dirs(self, relative_path: str) -> FilesManagerToolsResponse:
        """
        Create one or more directories.
        """
        try:
            final_path = (self._sandbox_path / relative_path).absolute()

            if not final_path.is_relative_to(self._sandbox_path):
                return FilesManagerToolsResponse(error=True, content="ERROR: access denied, you cannot create folders outside the sandbox..")

            if final_path.exists():
                if final_path.is_dir():
                    return FilesManagerToolsResponse(error=False, content=f"SUCCESS: folder '{relative_path}' already exists.")
                else:
                    return FilesManagerToolsResponse(error=True, content=f"ERROR: exists a file named '{relative_path}'.")

            final_path.mkdir(parents=True, exist_ok=True)

            return FilesManagerToolsResponse(error=False, content='SUCCESS: Path created successfully.')
        except Exception as e:
            msg_error = f"ERROR: {str(e)}"
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)


    async def open_file(self, relative_path) -> FilesManagerToolsResponse:
        """Open a file with the default application"""
        try:
            full_path = (self._sandbox_path / relative_path).resolve()

            if not full_path.is_relative_to(self._sandbox_path):
                return FilesManagerToolsResponse(error=True, content="ERROR: access denied outside the sandbox.")

            if not full_path.exists() or not full_path.is_file():
                return FilesManagerToolsResponse(error=True, content=f"ERROR: the element '{relative_path}' not exists or not is a valid file.")

            if platform.system() == "Windows":
                os.startfile(str(full_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", str(full_path)])
            else:  # Linux
                subprocess.call(["xdg-open", str(full_path)])

            return FilesManagerToolsResponse(error=False, content="SUCCESS: file opened successfully.")
        except Exception as e:
            msg_error = f"ERROR: to open file: {e}"
            print(msg_error)
            return FilesManagerToolsResponse(error=True, content=msg_error)
