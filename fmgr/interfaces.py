from abc import ABC, abstractmethod
from enum import IntEnum


class ErrorChoice(IntEnum):
    IGNORE = 0
    IGNORE_ALL = 1
    STOP = 2
    ROLLBACK = 3


class FileSelection(ABC):
    @abstractmethod
    def get_selected_files(self) -> list[str]: ...

    @abstractmethod
    def clear_selection(self) -> None: ...


class UserInterface(ABC):
    @abstractmethod
    def show_message(self, message: str) -> None: ...

    @abstractmethod
    def error_choice(self, path: str, error: OSError) -> int: ...


class FileSystem(ABC):
    @abstractmethod
    def copy(self, source: str, destination: str) -> str: ...

    @abstractmethod
    def move(self, source: str, destination: str) -> str: ...

    @abstractmethod
    def restore(self, current: str, original: str) -> None: ...

    @abstractmethod
    def trash(self, path: str) -> str: ...

    @abstractmethod
    def delete(self, path: str) -> None: ...
