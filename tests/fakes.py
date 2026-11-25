import errno
import posixpath

from fmgr.interfaces import FileSelection, FileSystem, UserInterface

DIRECTORY = "<directory>"


class FakeSelection(FileSelection):
    def __init__(self, files: list[str] | None = None) -> None:
        self.files = list(files or [])

    def get_selected_files(self) -> list[str]:
        return self.files

    def clear_selection(self) -> None:
        self.files.clear()


class FakeUserInterface(UserInterface):
    def __init__(self, choices: list[int] | None = None) -> None:
        self.choices = list(choices or [])
        self.messages: list[str] = []
        self.errors: list[tuple[str, OSError]] = []

    def show_message(self, message: str) -> None:
        self.messages.append(message)

    def error_choice(self, path: str, error: OSError) -> int:
        self.errors.append((path, error))
        return self.choices.pop(0)


class FakeFileSystem(FileSystem):
    def __init__(self, entries: dict[str, str]) -> None:
        self.entries = dict(entries)
        self.failures: dict[tuple[str, str], Exception] = {}

    def fail(self, operation: str, path: str, error: Exception) -> None:
        self.failures[(operation, path)] = error

    def is_dir(self, path: str) -> bool:
        return self.entries.get(path) == DIRECTORY

    def copy(self, source: str, destination: str) -> str:
        self._check("copy", source)
        if self.entries[source] == DIRECTORY:
            raise IsADirectoryError(errno.EISDIR, "Is a directory", source)
        target = self._target(source, destination)
        self.entries[target] = self.entries[source]
        return target

    def move(self, source: str, destination: str) -> str:
        self._check("move", source)
        target = self._target(source, destination)
        self.entries[target] = self.entries.pop(source)
        return target

    def restore(self, current: str, original: str) -> None:
        self._check("restore", current)
        self._ensure_free(original)
        self.entries[original] = self.entries.pop(current)

    def trash(self, path: str) -> str:
        self._check("trash", path)
        trashed = posixpath.join(posixpath.dirname(path), f".{posixpath.basename(path)}.trash")
        self._ensure_free(trashed)
        self.entries[trashed] = self.entries.pop(path)
        return trashed

    def delete(self, path: str) -> None:
        self._check("delete", path)
        del self.entries[path]

    def _check(self, operation: str, path: str) -> None:
        if (operation, path) in self.failures:
            raise self.failures[(operation, path)]
        if path not in self.entries:
            raise FileNotFoundError(errno.ENOENT, "No such file or directory", path)

    def _target(self, source: str, destination: str) -> str:
        if destination not in self.entries:
            raise FileNotFoundError(errno.ENOENT, "No such file or directory", destination)
        if self.entries[destination] != DIRECTORY:
            raise NotADirectoryError(errno.ENOTDIR, "Not a directory", destination)
        target = posixpath.join(destination, posixpath.basename(source))
        self._ensure_free(target)
        return target

    def _ensure_free(self, path: str) -> None:
        if path in self.entries:
            raise FileExistsError(errno.EEXIST, "File exists", path)
