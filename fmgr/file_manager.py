from fmgr.interfaces import FileSelection, FileSystem, UserInterface


class FileManager:
    def __init__(self, selection: FileSelection, ui: UserInterface, file_system: FileSystem) -> None:
        self._selection = selection
        self._ui = ui
        self._file_system = file_system

    def copy_files(self, destination: str) -> None:
        try:
            selected_files = self._selection.get_selected_files()
            for path in selected_files:
                if self._file_system.exists(path):
                    self._file_system.copy(path, destination)
            self._ui.show_message(f"{len(selected_files)} file(s) copied")
            self._selection.clear_selection()
        except Exception as e:
            self._ui.show_message(f"Copy error: {e}")

    def move_files(self, destination: str) -> None:
        try:
            selected_files = self._selection.get_selected_files()
            for path in selected_files:
                if self._file_system.exists(path):
                    self._file_system.move(path, destination)
            self._ui.show_message(f"{len(selected_files)} file(s) moved")
            self._selection.clear_selection()
        except Exception as e:
            self._ui.show_message(f"Move error: {e}")

    def delete_files(self) -> None:
        try:
            selected_files = self._selection.get_selected_files()
            for path in selected_files:
                if self._file_system.exists(path):
                    self._file_system.delete(path)
            self._ui.show_message(f"{len(selected_files)} file(s)/folder(s) deleted")
            self._selection.clear_selection()
        except Exception as e:
            self._ui.show_message(f"Delete error: {e}")
