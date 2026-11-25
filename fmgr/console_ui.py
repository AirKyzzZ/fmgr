from fmgr.file_explorer import FileExplorer
from fmgr.file_manager import FileManager
from fmgr.file_selector import FileSelector
from fmgr.interfaces import ErrorChoice, UserInterface

ERROR_CHOICES = {str(choice.value) for choice in ErrorChoice}


class ConsoleUserInterface(UserInterface):
    def show_message(self, message: str) -> None:
        print(message)

    def error_choice(self, path: str, error: OSError) -> int:
        print(f"Error on {path}: {error}")
        print("0. Ignore  1. Always ignore  2. Stop  3. Cancel and roll back")
        while True:
            answer = input("Your choice: ").strip()
            if answer in ERROR_CHOICES:
                return int(answer)
            print("Invalid choice")


def main_menu(file_selector: FileSelector, file_explorer: FileExplorer, file_manager: FileManager) -> None:
    while True:
        print("\n--- File Explorer ---")
        print("1. Display Directory")
        print("2. Navigate")
        print("3. Go to Parent Directory")
        print("4. Select Files")
        print("5. Copy")
        print("6. Move")
        print("7. Delete")
        print("8. Quit")

        choice = input("Your choice: ")

        try:
            if choice == "1":
                file_explorer.display_directory_contents()
            elif choice == "2":
                index = int(input("Enter navigation index: "))
                file_explorer.navigate(index)
            elif choice == "3":
                file_explorer.go_to_parent_directory()
            elif choice == "4":
                file_explorer.display_directory_contents()
                indices = input("Enter file indices to select (comma-separated): ")
                file_selector.select_files_by_indices(indices, file_explorer.current_path)
            elif choice == "5":
                destination = input("Enter destination path for copying: ")
                file_manager.copy_files(destination)
            elif choice == "6":
                destination = input("Enter destination path for moving: ")
                file_manager.move_files(destination)
            elif choice == "7":
                file_manager.delete_files()
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("Invalid choice")
        except Exception as e:
            print(f"An error occurred: {e}")
