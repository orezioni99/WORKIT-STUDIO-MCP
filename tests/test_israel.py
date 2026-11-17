"""The Israeli layer: extra guidance appended to the upstream scripting guides."""
from importlib import resources
from pathlib import Path

import pytest

from workit.registry import APPS, find
from workit.server import guide_text

IL = Path(str(resources.files("workit"))) / "skills" / "il"
SKILL_NAMES = {app.skill_name for app in APPS}


def test_every_guide_carries_the_israeli_common_rules():
    for app in APPS:
        text = guide_text(app)
        assert "## Working in Israel" in text, app.id
        assert "EPSG:2039" in text, app.id


@pytest.mark.parametrize("app_id", ["revit", "autocad", "sketchup", "qgis"])
def test_apps_with_an_israeli_section_get_it(app_id):
    text = guide_text(find(app_id))
    assert "(Israel)" in text


def test_clones_inherit_the_israeli_section_of_their_skill():
    assert "(Israel)" in guide_text(find("bricscad"))


def test_apps_without_an_israeli_section_still_get_the_upstream_guide():
    text = guide_text(find("blender"))
    assert "bpy" in text
    assert "(Israel)" not in text


def test_upstream_guide_comes_before_the_israeli_layer():
    text = guide_text(find("revit"))
    assert text.index("## Transactions") < text.index("(Israel)") < text.index(
        "## Rules that apply to every app") < text.index("## Working in Israel")


def test_israeli_files_match_a_known_skill_and_are_utf8():
    files = sorted(IL.glob("*.md"))
    assert files
    for path in files:
        assert path.stem == "_common" or path.stem in SKILL_NAMES, path.name
        assert path.read_text("utf-8").strip(), path.name


def test_common_israeli_rules_contain_hebrew():
    text = (IL / "_common.md").read_text("utf-8")
    assert any("֐" <= ch <= "׿" for ch in text)
