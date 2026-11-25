import os
import shutil

from fmgr.interfaces import FileSystem


class OsFileSystem(FileSystem):
    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def copy(self, source: str, destination: str) -> None:
        shutil.copy2(source, destination)

    def move(self, source: str, destination: str) -> None:
        shutil.move(source, destination)

    def delete(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return
        os.remove(path)
