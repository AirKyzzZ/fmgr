from collections.abc import Callable

from fmgr.interfaces import ErrorChoice, FileSelection, FileSystem, UserInterface


class FileManager:
    def __init__(self, selection: FileSelection, ui: UserInterface, file_system: FileSystem) -> None:
        self._selection = selection
        self._ui = ui
        self._file_system = file_system

    def copy_files(self, destination: str) -> None:
        self._run(
            "Copy",
            "file(s) copied",
            apply=lambda source: self._file_system.copy(source, destination),
            undo=lambda source, copy: self._file_system.delete(copy),
        )

    def move_files(self, destination: str) -> None:
        self._run(
            "Move",
            "file(s) moved",
            apply=lambda source: self._file_system.move(source, destination),
            undo=lambda source, moved: self._file_system.restore(moved, source),
        )

    def delete_files(self) -> None:
        trashed = self._run(
            "Delete",
            "file(s)/folder(s) deleted",
            apply=self._file_system.trash,
            undo=lambda source, trashed: self._file_system.restore(trashed, source),
        )
        self._purge(trashed)

    def _run(
        self,
        operation: str,
        done_message: str,
        apply: Callable[[str], str],
        undo: Callable[[str, str], None],
    ) -> list[str]:
        selected_files = list(self._selection.get_selected_files())
        done, interruption = self._apply_all(selected_files, apply)
        if interruption == ErrorChoice.ROLLBACK:
            self._rollback(done, undo)
            self._ui.show_message(f"{operation} cancelled, changes rolled back")
            return []
        if interruption is None:
            self._ui.show_message(f"{len(done)} {done_message}")
        else:
            self._ui.show_message(f"{operation} stopped")
        self._selection.clear_selection()
        return [result for _, result in done]

    def _apply_all(
        self, sources: list[str], apply: Callable[[str], str]
    ) -> tuple[list[tuple[str, str]], int | None]:
        done: list[tuple[str, str]] = []
        ignore_all = False
        for source in sources:
            try:
                done.append((source, apply(source)))
            except OSError as error:
                if ignore_all:
                    continue
                choice = self._ui.error_choice(source, error)
                if choice == ErrorChoice.IGNORE_ALL:
                    ignore_all = True
                elif choice != ErrorChoice.IGNORE:
                    return done, choice
        return done, None

    def _rollback(self, done: list[tuple[str, str]], undo: Callable[[str, str], None]) -> None:
        for source, result in reversed(done):
            try:
                undo(source, result)
            except OSError as error:
                self._ui.show_message(f"Could not roll back {source}: {error}")

    def _purge(self, trashed_paths: list[str]) -> None:
        for path in trashed_paths:
            try:
                self._file_system.delete(path)
            except OSError as error:
                self._ui.show_message(f"Could not purge {path}: {error}")
