import os

from fmgr.interfaces import FileSelection


class FileSelector(FileSelection):
    def __init__(self) -> None:
        self.selected_files: list[str] = []
        self.current_directory_contents: list[str] = []

    def load_directory_contents(self, directory_path: str) -> list[str]:
        try:
            self.current_directory_contents = os.listdir(directory_path)
            return self.current_directory_contents
        except Exception as e:
            print(f"Error loading directory contents: {e}")
            return []

    def select_files_by_indices(self, indices: str, directory_path: str) -> list[str]:
        try:
            selected_indices = [int(i.strip()) for i in indices.split(",")]
            self.selected_files.clear()
            for index in selected_indices:
                if 0 <= index < len(self.current_directory_contents):
                    full_path = os.path.join(directory_path, self.current_directory_contents[index])
                    self.selected_files.append(full_path)

            print("Selected files:")
            for file in self.selected_files:
                print(f" - {os.path.basename(file)}")
            return self.selected_files
        except ValueError:
            print("Invalid input. Please enter valid indices.")
            return []
        except Exception as e:
            print(f"Error selecting files: {e}")
            return []

    def get_selected_files(self) -> list[str]:
        return self.selected_files

    def clear_selection(self) -> None:
        self.selected_files.clear()
