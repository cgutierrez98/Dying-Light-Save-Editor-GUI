import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest
from logic.config import atomic_replace, prune_backups, create_save_backup, list_save_backups
from logic.validation import validate_save_data, SaveValidationError, INT32_MIN, INT32_MAX, UINT32_MAX
from logic.cheats import (
    get_duplicate_id_map, max_kings, max_quantity, max_skill,
    set_rarity, set_platinum, KING
)
from logic.item_names import (
    get_ammo_data, set_ammo_value, max_all_ammo, get_display_name
)
from ui.common import find_steam_save_locations, find_default_save_path


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
    assert validate_save_data({"int_min": INT32_MIN, "uint_max": UINT32_MAX})
    for bad in ({}, None, {"a": float("nan")}, {"a": float("inf")}, {"a": UINT32_MAX + 1}, {"a": INT32_MIN - 1}):
        with pytest.raises(SaveValidationError):
            validate_save_data(bad)


def test_cheats_max_kings():
    item = {"name": "TestMachete"}
    max_kings(item)
    assert item["upgradeSockets"] == [KING] * 4


def test_cheats_max_quantity():
    item = {"name": "Medkit", "quantity": 1}
    max_quantity(item)
    assert item["quantity"] == 999999999


def test_cheats_max_skill():
    item_buff = {"name": "LegendSkill_UnarmedDamage_skill", "stacks": 5}
    max_skill(item_buff)
    assert item_buff["stacks"] == 9999

    item_unknown = {"unknown": {"unknown001": 2}}
    max_skill(item_unknown)
    assert item_unknown["unknown"]["unknown001"] == 9999


def test_cheats_rarity():
    item = {"name": "Katana"}
    set_rarity(item, "orange")
    assert item["attributes"]["color"] == "orange"

    set_platinum(item)
    assert item["attributes"]["color"] == "platinum"


def test_duplicate_id_map():
    items = [
        {"id": 100, "name": "Item A"},
        {"id": 200, "name": "Item B"},
        {"id": 100, "name": "Item A copy"},
        {"id": 0, "name": "Item Zero"},
        {"id": 0, "name": "Item Zero copy"},
        "invalid_non_dict_element",
        {"name": "No id item"}
    ]
    duplicates = get_duplicate_id_map(items)
    assert 100 in duplicates and len(duplicates[100]) == 2
    assert 0 in duplicates and len(duplicates[0]) == 2
    assert 200 not in duplicates


def test_ammo_operations():
    data = {
        "player": {
            "inventory": {
                "ammo": {
                    "items": [
                        {"id": 43, "value": 10},
                        {"id": 44, "value": 25}
                    ]
                }
            }
        }
    }
    ammo = get_ammo_data(data)
    pistol = next(a for a in ammo if a["id"] == 43)
    assert pistol["value"] == 10

    set_ammo_value(data, 43, 500)
    ammo_after = get_ammo_data(data)
    pistol_after = next(a for a in ammo_after if a["id"] == 43)
    assert pistol_after["value"] == 500

    max_all_ammo(data, 9999)
    ammo_maxed = get_ammo_data(data)
    for a in ammo_maxed:
        assert a["value"] == 9999


def test_steam_detection_no_crash():
    locs = find_steam_save_locations()
    assert isinstance(locs, list)
    path = find_default_save_path()
    assert path is None or isinstance(path, str)


def test_display_name_lookup():
    assert "Korek" in get_display_name("MacheteAKorek")
    assert get_display_name("UnknownWeirdWeapon123") == "UnknownWeirdWeapon123"
