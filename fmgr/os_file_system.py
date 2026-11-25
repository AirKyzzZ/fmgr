import errno
import os
import shutil
import uuid

from fmgr.interfaces import FileSystem

_RENAME_UNAVAILABLE = {errno.EXDEV, errno.EPERM, errno.ENOTSUP, errno.EOPNOTSUPP}


def _ensure_free(path: str) -> None:
    if os.path.lexists(path):
        raise FileExistsError(errno.EEXIST, "Destination already exists", path)


def _target(source: str, destination: str) -> str:
    target = os.path.join(destination, os.path.basename(source))
    _ensure_free(target)
    return target


def _rename_without_replacing(current: str, original: str) -> None:
    if os.path.isdir(current) and not os.path.islink(current):
        os.rename(current, original)
        return
    # os.rename silently replaces an existing file, os.link refuses to
    os.link(current, original, follow_symlinks=False)
    os.unlink(current)


class OsFileSystem(FileSystem):
    def copy(self, source: str, destination: str) -> str:
        return shutil.copy2(source, _target(source, destination))

    def move(self, source: str, destination: str) -> str:
        return shutil.move(source, _target(source, destination))

    def restore(self, current: str, original: str) -> None:
        _ensure_free(original)
        try:
            _rename_without_replacing(current, original)
        except OSError as error:
            if error.errno not in _RENAME_UNAVAILABLE:
                raise
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
