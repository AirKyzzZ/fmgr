from pathlib import Path

import pytest

from fmgr.os_file_system import OsFileSystem


@pytest.mark.parametrize("make_entry", [lambda path: path.write_text("data"), lambda path: path.mkdir()])
def test_restore_puts_a_trashed_entry_back(tmp_path, make_entry):
    original = tmp_path / "entry"
    make_entry(original)
    file_system = OsFileSystem()
    trashed = file_system.trash(str(original))

    file_system.restore(trashed, str(original))

    assert original.exists()
    assert [path.name for path in tmp_path.iterdir()] == ["entry"]


def test_restore_never_moves_into_a_directory_that_took_the_original_name(tmp_path):
    original = tmp_path / "report.txt"
    original.write_text("data")
    file_system = OsFileSystem()
    trashed = file_system.trash(str(original))
    original.mkdir()

    with pytest.raises(FileExistsError):
        file_system.restore(trashed, str(original))

    assert list(original.iterdir()) == []
    assert Path(trashed).read_text() == "data"
