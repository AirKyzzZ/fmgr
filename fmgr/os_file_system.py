import errno
import os
import shutil
import uuid

from fmgr.interfaces import FileSystem


def _ensure_free(path: str) -> None:
    if os.path.lexists(path):
        raise FileExistsError(errno.EEXIST, "Destination already exists", path)


def _target(source: str, destination: str) -> str:
    target = os.path.join(destination, os.path.basename(source))
    _ensure_free(target)
    return target


class OsFileSystem(FileSystem):
    def copy(self, source: str, destination: str) -> str:
        return shutil.copy2(source, _target(source, destination))

    def move(self, source: str, destination: str) -> str:
        return shutil.move(source, _target(source, destination))

    def restore(self, current: str, original: str) -> None:
        _ensure_free(original)
        shutil.move(current, original)

    def trash(self, path: str) -> str:
        parent, name = os.path.split(path)
        trashed = os.path.join(parent, f".{name}.{uuid.uuid4().hex}.fmgr-trash")
        os.rename(path, trashed)
        return trashed

    def delete(self, path: str) -> None:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
            return
        os.remove(path)
