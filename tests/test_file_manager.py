import pytest

from fmgr.file_manager import FileManager
from tests.fakes import DIRECTORY, FakeFileSystem, FakeSelection, FakeUserInterface


@pytest.fixture
def selection() -> FakeSelection:
    return FakeSelection()


@pytest.fixture
def ui() -> FakeUserInterface:
    return FakeUserInterface()


@pytest.fixture
def file_system() -> FakeFileSystem:
    return FakeFileSystem(
        {
            "/src": DIRECTORY,
            "/src/a.txt": "A",
            "/src/b.txt": "B",
            "/src/c.txt": "C",
            "/src/photos": DIRECTORY,
            "/dst": DIRECTORY,
        }
    )


@pytest.fixture
def manager(selection: FakeSelection, ui: FakeUserInterface, file_system: FakeFileSystem) -> FileManager:
    return FileManager(selection, ui, file_system)


def test_copies_a_selected_file(manager, selection, ui, file_system):
    selection.files = ["/src/a.txt"]

    manager.copy_files("/dst")

    assert file_system.entries["/dst/a.txt"] == "A"
    assert file_system.entries["/src/a.txt"] == "A"
    assert ui.messages == ["1 file(s) copied"]
