"""Tests for ingredients persistence using a temporary custom file."""

import os
from pathlib import Path

import ingredients


def test_add_and_load_custom(tmp_path, monkeypatch):
    custom_file = tmp_path / "custom.json"
    # point the module to use this path
    monkeypatch.setenv("CUSTOM_INGREDIENTS_PATH", str(custom_file))

    # ensure clean start
    if custom_file.exists():
        custom_file.unlink()

    # add a custom ingredient
    ingredients.add_custom_ingredient("test-nut", 96.5)

    # load_custom should pick it up
    loaded = ingredients.load_custom()
    assert "test-nut" in loaded
    assert abs(loaded["test-nut"] - 96.5) < 1e-9

    # get_all_ingredients should include it too
    all_ing = ingredients.get_all_ingredients()
    assert "test-nut" in all_ing
