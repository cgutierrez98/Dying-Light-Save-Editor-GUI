import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest
from logic.config import atomic_replace, prune_backups, create_save_backup, list_save_backups
from logic.validation import validate_save_data, SaveValidationError


def test_atomic_replace(tmp_path):
    src = tmp_path / "a.bin"; dst = tmp_path / "b.sav"
    src.write_bytes(b"new"); dst.write_bytes(b"old")
    atomic_replace(str(src), str(dst))
    assert dst.read_bytes() == b"new" and not src.exists()
    assert [p.name for p in tmp_path.iterdir()] == ["b.sav"]


def test_atomic_replace_keep_source(tmp_path):
    src = tmp_path / "a.bin"; dst = tmp_path / "b.sav"
    src.write_bytes(b"x"); dst.write_bytes(b"y")
    atomic_replace(str(src), str(dst), keep_source=True)
    assert src.exists() and dst.read_bytes() == b"x"


def test_prune_backups(tmp_path):
    save = tmp_path / "s.sav"; save.write_bytes(b"1")
    bd = tmp_path / "backups"; bd.mkdir()
    for i in range(5):
        (bd / f"s.sav.bak_2026010{i}_000000").write_bytes(b"1")
    prune_backups(str(save), keep=2)
    assert sorted(p.name for p in bd.iterdir()) == ["s.sav.bak_20260103_000000", "s.sav.bak_20260104_000000"]


def test_backup_created(tmp_path):
    save = tmp_path / "s.sav"; save.write_bytes(b"1")
    assert create_save_backup(str(save)) and len(list_save_backups(str(save))) == 1


def test_validation():
    assert validate_save_data({"a": [1, 2.5]})
    for bad in ({}, None, {"a": float("nan")}):
        with pytest.raises(SaveValidationError):
            validate_save_data(bad)
