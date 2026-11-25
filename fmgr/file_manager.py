import os
import shutil

from fmgr.file_selector import FileSelector


class FileManager:
    def __init__(self, file_selector: FileSelector) -> None:
        self.file_selector = file_selector

    def copy_files(self, destination: str) -> None:
        try:
            selected_files = self.file_selector.get_selected_files()
            for path in selected_files:
                if os.path.exists(path):
                    shutil.copy2(path, destination)
            print(f"{len(selected_files)} file(s) copied")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Copy error: {e}")

    def move_files(self, destination: str) -> None:
        try:
            selected_files = self.file_selector.get_selected_files()
            for path in selected_files:
                if os.path.exists(path):
                    shutil.move(path, destination)
            print(f"{len(selected_files)} file(s) moved")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Move error: {e}")

    def delete_files(self) -> None:
        try:
            selected_files = self.file_selector.get_selected_files()
            for path in selected_files:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            print(f"{len(selected_files)} file(s)/folder(s) deleted")
            self.file_selector.clear_selection()
        except Exception as e:
            print(f"Delete error: {e}")
