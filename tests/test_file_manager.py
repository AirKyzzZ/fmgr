import posixpath
from collections.abc import Callable
from dataclasses import dataclass

import pytest

from fmgr.file_manager import FileManager
from fmgr.interfaces import ErrorChoice
from tests.fakes import DIRECTORY, FakeFileSystem, FakeSelection, FakeUserInterface

A = "/src/a.txt"
B = "/src/b.txt"
C = "/src/c.txt"
PHOTOS = "/src/photos"
INITIAL_ENTRIES = {
    "/src": DIRECTORY,
    A: "A",
    B: "B",
    C: "C",
    PHOTOS: DIRECTORY,
    "/dst": DIRECTORY,
}


@pytest.fixture
def selection() -> FakeSelection:
    return FakeSelection()


@pytest.fixture
def ui() -> FakeUserInterface:
    return FakeUserInterface()


@pytest.fixture
def file_system() -> FakeFileSystem:
    return FakeFileSystem(INITIAL_ENTRIES)


@pytest.fixture
def manager(selection: FakeSelection, ui: FakeUserInterface, file_system: FakeFileSystem) -> FileManager:
    return FileManager(selection, ui, file_system)


def without(*paths: str) -> dict[str, str]:
    return {path: content for path, content in INITIAL_ENTRIES.items() if path not in paths}


class TestCopyFiles:
    def test_copies_a_selected_file(self, manager, selection, ui, file_system):
        selection.files = [A]

        manager.copy_files("/dst")

        assert file_system.entries == {**INITIAL_ENTRIES, "/dst/a.txt": "A"}
        assert ui.messages == ["1 file(s) copied"]
        assert ui.errors == []

    def test_copies_every_selected_file(self, manager, selection, ui, file_system):
        selection.files = [A, B, C]

        manager.copy_files("/dst")

        assert file_system.entries == {**INITIAL_ENTRIES, "/dst/a.txt": "A", "/dst/b.txt": "B", "/dst/c.txt": "C"}
        assert ui.messages == ["3 file(s) copied"]

    def test_empty_selection_copies_nothing(self, manager, ui, file_system):
        manager.copy_files("/dst")

        assert file_system.entries == INITIAL_ENTRIES
        assert ui.messages == ["0 file(s) copied"]
        assert ui.errors == []

    def test_copies_a_large_selection(self, selection, ui):
        paths = [f"/src/file{index}.txt" for index in range(500)]
        file_system = FakeFileSystem({"/src": DIRECTORY, "/dst": DIRECTORY} | {path: path for path in paths})
        selection.files = list(paths)

        FileManager(selection, ui, file_system).copy_files("/dst")

        assert all(file_system.entries[path.replace("/src/", "/dst/")] == path for path in paths)
        assert ui.messages == ["500 file(s) copied"]

    def test_copies_names_with_spaces_and_accents(self, manager, selection, ui, file_system):
        file_system.entries["/src/été 2024 (copie).txt"] = "souvenirs"
        selection.files = ["/src/été 2024 (copie).txt"]

        manager.copy_files("/dst")

        assert file_system.entries["/dst/été 2024 (copie).txt"] == "souvenirs"
        assert ui.messages == ["1 file(s) copied"]

    def test_clears_the_selection_once_done(self, manager, selection):
        selection.files = [A, B]

        manager.copy_files("/dst")

        assert selection.files == []

    def test_reports_a_missing_source_to_the_user(self, manager, selection, ui, file_system):
        selection.files = ["/src/ghost.txt", A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.copy_files("/dst")

        [(path, error)] = ui.errors
        assert path == "/src/ghost.txt"
        assert isinstance(error, FileNotFoundError)
        assert file_system.entries["/dst/a.txt"] == "A"

    def test_never_overwrites_a_file_already_at_destination(self, manager, selection, ui, file_system):
        file_system.entries["/dst/a.txt"] = "old"
        selection.files = [A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.copy_files("/dst")

        assert isinstance(ui.errors[0][1], FileExistsError)
        assert file_system.entries["/dst/a.txt"] == "old"

    def test_copying_into_the_source_directory_is_reported(self, manager, selection, ui, file_system):
        selection.files = [A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.copy_files("/src")

        assert isinstance(ui.errors[0][1], FileExistsError)
        assert file_system.entries == INITIAL_ENTRIES

    def test_copies_a_file_selected_twice_only_once(self, manager, selection, ui, file_system):
        selection.files = [A, A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.copy_files("/dst")

        assert file_system.entries == {**INITIAL_ENTRIES, "/dst/a.txt": "A"}
        assert len(ui.errors) == 1

    def test_reports_a_directory_the_file_system_cannot_copy(self, manager, selection, ui, file_system):
        selection.files = [PHOTOS, A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.copy_files("/dst")

        assert ui.errors[0][0] == PHOTOS
        assert isinstance(ui.errors[0][1], IsADirectoryError)
        assert file_system.entries == {**INITIAL_ENTRIES, "/dst/a.txt": "A"}

    @pytest.mark.parametrize("destination", ["/nowhere", B])
    def test_refuses_a_destination_that_is_not_a_directory(self, manager, selection, ui, file_system, destination):
        selection.files = [A, C]

        manager.copy_files(destination)

        assert ui.errors == []
        assert ui.messages == [f"Destination is not a directory: {destination}"]
        assert file_system.entries == INITIAL_ENTRIES
        assert selection.files == [A, C]


class TestMoveFiles:
    def test_moves_a_selected_file(self, manager, selection, ui, file_system):
        selection.files = [A]

        manager.move_files("/dst")

        assert file_system.entries == {**without(A), "/dst/a.txt": "A"}
        assert ui.messages == ["1 file(s) moved"]
        assert ui.errors == []

    def test_moves_files_and_directories(self, manager, selection, ui, file_system):
        selection.files = [A, PHOTOS]

        manager.move_files("/dst")

        assert file_system.entries == {**without(A, PHOTOS), "/dst/a.txt": "A", "/dst/photos": DIRECTORY}
        assert ui.messages == ["2 file(s) moved"]

    def test_empty_selection_moves_nothing(self, manager, ui, file_system):
        manager.move_files("/dst")

        assert file_system.entries == INITIAL_ENTRIES
        assert ui.messages == ["0 file(s) moved"]
        assert ui.errors == []

    def test_moves_names_with_spaces_and_accents(self, manager, selection, ui, file_system):
        file_system.entries["/src/rapport final é.pdf"] = "pdf"
        selection.files = ["/src/rapport final é.pdf"]

        manager.move_files("/dst")

        assert "/src/rapport final é.pdf" not in file_system.entries
        assert file_system.entries["/dst/rapport final é.pdf"] == "pdf"
        assert ui.messages == ["1 file(s) moved"]

    def test_clears_the_selection_once_done(self, manager, selection):
        selection.files = [A, B]

        manager.move_files("/dst")

        assert selection.files == []

    def test_reports_a_missing_source_to_the_user(self, manager, selection, ui, file_system):
        selection.files = ["/src/ghost.txt", A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.move_files("/dst")

        [(path, error)] = ui.errors
        assert path == "/src/ghost.txt"
        assert isinstance(error, FileNotFoundError)
        assert file_system.entries == {**without(A), "/dst/a.txt": "A"}

    def test_keeps_both_files_on_a_name_collision(self, manager, selection, ui, file_system):
        file_system.entries["/dst/a.txt"] = "old"
        selection.files = [A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.move_files("/dst")

        assert isinstance(ui.errors[0][1], FileExistsError)
        assert file_system.entries["/dst/a.txt"] == "old"
        assert file_system.entries[A] == "A"

    def test_moving_into_the_source_directory_is_reported(self, manager, selection, ui, file_system):
        selection.files = [A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.move_files("/src")

        assert isinstance(ui.errors[0][1], FileExistsError)
        assert file_system.entries == INITIAL_ENTRIES

    def test_rollback_moves_a_directory_back(self, manager, selection, ui, file_system):
        selection.files = [PHOTOS, A]
        file_system.fail("move", A, PermissionError("locked"))
        ui.choices = [ErrorChoice.ROLLBACK]

        manager.move_files("/dst")

        assert file_system.entries == INITIAL_ENTRIES

    @pytest.mark.parametrize("destination", ["/nowhere", B])
    def test_refuses_a_destination_that_is_not_a_directory(self, manager, selection, ui, file_system, destination):
        selection.files = [A, C]

        manager.move_files(destination)

        assert ui.errors == []
        assert ui.messages == [f"Destination is not a directory: {destination}"]
        assert file_system.entries == INITIAL_ENTRIES
        assert selection.files == [A, C]


class TestDeleteFiles:
    def test_deletes_a_selected_file_without_leaving_it_staged(self, manager, selection, ui, file_system):
        selection.files = [A]

        manager.delete_files()

        assert file_system.entries == without(A)
        assert ui.messages == ["1 file(s)/folder(s) deleted"]
        assert ui.errors == []

    def test_deletes_files_and_directories(self, manager, selection, ui, file_system):
        selection.files = [A, PHOTOS, C]

        manager.delete_files()

        assert file_system.entries == without(A, PHOTOS, C)
        assert ui.messages == ["3 file(s)/folder(s) deleted"]

    def test_empty_selection_deletes_nothing(self, manager, ui, file_system):
        manager.delete_files()

        assert file_system.entries == INITIAL_ENTRIES
        assert ui.messages == ["0 file(s)/folder(s) deleted"]
        assert ui.errors == []

    def test_deletes_names_with_spaces_and_accents(self, manager, selection, ui, file_system):
        file_system.entries["/src/vieux brouillon à jeter.txt"] = "x"
        selection.files = ["/src/vieux brouillon à jeter.txt"]

        manager.delete_files()

        assert file_system.entries == INITIAL_ENTRIES
        assert ui.messages == ["1 file(s)/folder(s) deleted"]

    def test_clears_the_selection_once_done(self, manager, selection):
        selection.files = [A, B]

        manager.delete_files()

        assert selection.files == []

    def test_reports_a_missing_file_to_the_user(self, manager, selection, ui, file_system):
        selection.files = ["/src/ghost.txt", A]
        ui.choices = [ErrorChoice.IGNORE]

        manager.delete_files()

        [(path, error)] = ui.errors
        assert path == "/src/ghost.txt"
        assert isinstance(error, FileNotFoundError)
        assert file_system.entries == without(A)

    def test_keeps_a_locked_file_and_deletes_the_others(self, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail("trash", B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE]

        manager.delete_files()

        assert file_system.entries == without(A, C)

    def test_stop_purges_what_was_already_staged(self, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail("trash", B, PermissionError("locked"))
        ui.choices = [ErrorChoice.STOP]

        manager.delete_files()

        assert file_system.entries == without(A)

    def test_rollback_restores_a_deleted_directory(self, manager, selection, ui, file_system):
        selection.files = [PHOTOS, A]
        file_system.fail("trash", A, PermissionError("locked"))
        ui.choices = [ErrorChoice.ROLLBACK]

        manager.delete_files()

        assert file_system.entries == INITIAL_ENTRIES


def copied(file_system: FakeFileSystem, path: str) -> bool:
    return posixpath.join("/dst", posixpath.basename(path)) in file_system.entries


def moved(file_system: FakeFileSystem, path: str) -> bool:
    return copied(file_system, path) and path not in file_system.entries


def deleted(file_system: FakeFileSystem, path: str) -> bool:
    return path not in file_system.entries


@dataclass(frozen=True)
class Operation:
    name: str
    run: Callable[[FileManager], None]
    failing_step: str
    done_message: str
    processed: Callable[[FakeFileSystem, str], bool]


OPERATIONS = [
    Operation("Copy", lambda manager: manager.copy_files("/dst"), "copy", "file(s) copied", copied),
    Operation("Move", lambda manager: manager.move_files("/dst"), "move", "file(s) moved", moved),
    Operation("Delete", lambda manager: manager.delete_files(), "trash", "file(s)/folder(s) deleted", deleted),
]


@pytest.mark.parametrize("operation", OPERATIONS, ids=lambda operation: operation.name.lower())
class TestErrorChoices:
    def test_passes_the_failing_path_and_error_to_the_user(self, operation, manager, selection, ui, file_system):
        error = PermissionError("locked")
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, B, error)
        ui.choices = [ErrorChoice.IGNORE]

        operation.run(manager)

        assert ui.errors == [(B, error)]

    def test_ignore_skips_the_file_and_continues(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE]

        operation.run(manager)

        assert operation.processed(file_system, A)
        assert not operation.processed(file_system, B)
        assert operation.processed(file_system, C)
        assert selection.files == []

    def test_ignore_asks_again_on_the_next_error(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, A, PermissionError("locked"))
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE, ErrorChoice.IGNORE]

        operation.run(manager)

        assert [path for path, _ in ui.errors] == [A, B]
        assert operation.processed(file_system, C)

    def test_always_ignore_asks_only_once(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, A, PermissionError("locked"))
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE_ALL]

        operation.run(manager)

        assert [path for path, _ in ui.errors] == [A]
        assert operation.processed(file_system, C)

    def test_always_ignore_only_lasts_for_the_current_operation(self, operation, manager, selection, ui, file_system):
        file_system.fail(operation.failing_step, A, PermissionError("locked"))
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE_ALL, ErrorChoice.IGNORE]

        selection.files = [A]
        operation.run(manager)
        selection.files = [B]
        operation.run(manager)

        assert [path for path, _ in ui.errors] == [A, B]

    def test_ignored_files_are_not_counted(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, A, PermissionError("locked"))
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.IGNORE, ErrorChoice.IGNORE_ALL]

        operation.run(manager)

        assert ui.messages == [f"1 {operation.done_message}"]

    def test_stop_keeps_what_was_done_and_skips_the_rest(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.STOP]

        operation.run(manager)

        assert operation.processed(file_system, A)
        assert not operation.processed(file_system, B)
        assert not operation.processed(file_system, C)
        assert selection.files == []

    def test_stop_reports_how_many_files_were_processed(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, C, PermissionError("locked"))
        ui.choices = [ErrorChoice.STOP]

        operation.run(manager)

        assert ui.messages == [f"{operation.name} stopped, 2 {operation.done_message}"]

    def test_unknown_choice_stops_the_operation(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [42]

        operation.run(manager)

        assert operation.processed(file_system, A)
        assert not operation.processed(file_system, C)

    def test_rollback_restores_the_initial_state(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B, C]
        file_system.fail(operation.failing_step, C, PermissionError("locked"))
        ui.choices = [ErrorChoice.ROLLBACK]

        operation.run(manager)

        assert file_system.entries == INITIAL_ENTRIES
        assert ui.messages == [f"{operation.name} cancelled, changes rolled back"]

    def test_rollback_on_the_first_file_changes_nothing(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B]
        file_system.fail(operation.failing_step, A, PermissionError("locked"))
        ui.choices = [ErrorChoice.ROLLBACK]

        operation.run(manager)

        assert file_system.entries == INITIAL_ENTRIES

    def test_rollback_keeps_the_selection(self, operation, manager, selection, ui, file_system):
        selection.files = [A, B]
        file_system.fail(operation.failing_step, B, PermissionError("locked"))
        ui.choices = [ErrorChoice.ROLLBACK]

        operation.run(manager)

        assert selection.files == [A, B]

    def test_does_not_swallow_unexpected_exceptions(self, operation, manager, selection, file_system):
        selection.files = [A]
        file_system.fail(operation.failing_step, A, RuntimeError("bug"))

        with pytest.raises(RuntimeError):
            operation.run(manager)
