from abc import ABC, abstractmethod


class FileSelection(ABC):
    @abstractmethod
    def get_selected_files(self) -> list[str]: ...

    @abstractmethod
    def clear_selection(self) -> None: ...


class UserInterface(ABC):
    @abstractmethod
    def show_message(self, message: str) -> None: ...


class FileSystem(ABC):
    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def copy(self, source: str, destination: str) -> None: ...

    @abstractmethod
    def move(self, source: str, destination: str) -> None: ...

    @abstractmethod
    def delete(self, path: str) -> None: ...
