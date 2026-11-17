import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import json, pytest
from logic.save_service import SaveService, SaveError, EditorNotFoundError


def fake_runner(fail=False, write=True, on_update=None):
    def run(cmd, **kw):
        args = cmd[1:]
        patch = next(a for a in args if a.startswith("--patch=")).split("=", 1)[1]
        if fail:
            return types.SimpleNamespace(returncode=2, stdout=b"", stderr=b"boom")
        if args[0] == "sample":
            json.dump({"player": {"cash": 5}}, open(patch, "w"))
        elif write:
            if on_update:
                on_update(patch)
            out = next(a for a in args if a.startswith("--output=")).split("=", 1)[1]
            open(out, "wb").write(b"NEWSAVE")
        return types.SimpleNamespace(returncode=0, stdout=b"", stderr=b"")
    return run


def make(tmp_path, **kw):
    exe = tmp_path / "editor.exe"; exe.write_bytes(b"x")
    return SaveService(editor_path=str(exe), temp_dir=str(tmp_path / "t"), runner=fake_runner(**kw))


def test_load(tmp_path):
    svc = make(tmp_path)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    assert svc.load(str(sav)) == {"player": {"cash": 5}}
    # Temp JSON debe limpiarse tras la carga
    assert not os.path.exists(svc.temp_json)


def test_save_replaces_and_backs_up(tmp_path):
    svc = make(tmp_path)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    backup = svc.save(str(sav), {"a": 1})
    assert sav.read_bytes() == b"NEWSAVE"
    assert open(backup, "rb").read() == b"old"
    # Temp files deben limpiarse tras el guardado
    assert not os.path.exists(svc.temp_json)
    assert not os.path.exists(svc.temp_save)


def test_save_preserves_utf8(tmp_path):
    captured = []
    def check_patch(patch_path):
        captured.append(open(patch_path, "r", encoding="utf-8").read())

    svc = make(tmp_path, on_update=check_patch)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    svc.save(str(sav), {"name": "Espada de dragón con cañón"})
    assert len(captured) == 1
    assert "Espada de dragón con cañón" in captured[0]
    assert "\\u00f3" not in captured[0]


def test_failed_editor_keeps_original(tmp_path):
    svc = make(tmp_path, fail=True)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    with pytest.raises(SaveError, match="boom"):
        svc.save(str(sav), {"a": 1})
    assert sav.read_bytes() == b"old"


def test_no_output_keeps_original(tmp_path):
    svc = make(tmp_path, write=False)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    with pytest.raises(SaveError):
        svc.save(str(sav), {"a": 1})
    assert sav.read_bytes() == b"old"


def test_invalid_data_writes_nothing(tmp_path):
    svc = make(tmp_path)
    sav = tmp_path / "a.sav"; sav.write_bytes(b"old")
    with pytest.raises(SaveError):
        svc.save(str(sav), {})
    assert sav.read_bytes() == b"old" and not (tmp_path / "backups").exists()


def test_editor_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda *_: None)
    svc = SaveService(editor_path=None, temp_dir=str(tmp_path / "t"), candidates=[str(tmp_path / "no.exe")])
    with pytest.raises(EditorNotFoundError):
        svc.run_editor(["sample"])
