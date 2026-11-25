from collections.abc import Callable

from fmgr.interfaces import ErrorChoice, FileSelection, FileSystem, UserInterface


class FileManager:
    def __init__(self, selection: FileSelection, ui: UserInterface, file_system: FileSystem) -> None:
        self._selection = selection
        self._ui = ui
        self._file_system = file_system

    def copy_files(self, destination: str) -> None:
        self._run("Copy", "file(s) copied", lambda source: self._file_system.copy(source, destination))

    def move_files(self, destination: str) -> None:
        self._run("Move", "file(s) moved", lambda source: self._file_system.move(source, destination))

    def delete_files(self) -> None:
        self._run("Delete", "file(s)/folder(s) deleted", self._file_system.delete)

    def _run(self, operation: str, done_message: str, apply: Callable[[str], None]) -> None:
        selected_files = list(self._selection.get_selected_files())
        interruption = self._apply_all(selected_files, apply)
        if interruption is None:
            self._ui.show_message(f"{len(selected_files)} {done_message}")
        else:
            self._ui.show_message(f"{operation} stopped")
        self._selection.clear_selection()

    def _apply_all(self, sources: list[str], apply: Callable[[str], None]) -> int | None:
        ignore_all = False
        for source in sources:
            try:
                apply(source)
            except OSError as error:
                if ignore_all:
                    continue
                choice = self._ui.error_choice(source, error)
                if choice == ErrorChoice.IGNORE_ALL:
                    ignore_all = True
                elif choice != ErrorChoice.IGNORE:
                    return choice
        return None
