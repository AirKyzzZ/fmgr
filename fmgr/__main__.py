from fmgr.console_ui import main_menu
from fmgr.file_explorer import FileExplorer
from fmgr.file_manager import FileManager
from fmgr.file_selector import FileSelector


def main() -> None:
    file_selector = FileSelector()
    file_explorer = FileExplorer(file_selector)
    file_manager = FileManager(file_selector)
    main_menu(file_selector, file_explorer, file_manager)


if __name__ == "__main__":
    main()
