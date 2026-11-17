"""The registry, the bridge files and the skills must agree with each other."""
import ast
import re
from importlib import resources
from pathlib import Path

import pytest

from workit import installers
from workit.registry import APPS, find

ROOT = Path(str(resources.files("workit")))

BRIDGE_FILES = {
    "blender": "bridges/blender/__init__.py",
    "rhino": "bridges/rhino/workit_rhino.py",
    "3dsmax": "bridges/max/workit_max.py",
    "sketchup": "bridges/sketchup/workit.rb",
    "freecad": "bridges/freecad/WorkitStudio/workit_freecad.py",
    "maya": "bridges/maya/workit_maya.py",
    "fusion": "bridges/fusion/WorkitStudio/WorkitStudio.py",
    "c4d": "bridges/c4d/workit/workit.pyp",
    "houdini": "bridges/houdini/scripts/python/workit_houdini.py",
    "qgis": "bridges/qgis/workit/__init__.py",
}


def test_ids_and_aliases_are_unique():
    names = [app.id for app in APPS] + [alias for app in APPS for alias in app.aliases
                                        if alias != app.id]
    assert len(names) == len(set(names))


def test_socket_ports_do_not_overlap():
    ports = sorted(app.port for app in APPS if app.kind == "socket")
    assert all(b - a >= 5 for a, b in zip(ports, ports[1:]))


@pytest.mark.parametrize("app", APPS, ids=lambda app: app.id)
def test_every_app_has_a_skill(app):
    text = (ROOT / "skills" / f"{app.skill_name}.md").read_text("utf-8")
    assert len(text) > 300


@pytest.mark.parametrize("app_id,relative", BRIDGE_FILES.items())
def test_bridge_port_and_name_match_the_registry(app_id, relative):
    text = (ROOT / relative).read_text("utf-8")
    port = int(re.search(r"\b(?:BASE_)?PORT = (\d+)", text).group(1))
    assert port == find(app_id).port
    assert re.search(r"""["']%s["']""" % re.escape(app_id), text), "bridge must announce its app id"


@pytest.mark.parametrize("relative", [p for p in BRIDGE_FILES.values() if not p.endswith(".rb")]
                         + ["bridges/revit/WorkitStudio.extension/startup.py",
                            "bridges/_core/workit_core.py"])
def test_bridge_python_parses(relative):
    ast.parse((ROOT / relative).read_text("utf-8"))


def test_every_socket_app_has_an_installer():
    socket_apps = {app.id for app in APPS if app.kind == "socket"}
    assert socket_apps <= set(installers.installable())
    assert set(BRIDGE_FILES) == socket_apps


def test_aliases_resolve():
    assert find("3D Max").id == "3dsmax"
    assert find("naviswork").id == "navisworks"
    assert find("Civil3D").id == "autocad"
    with pytest.raises(KeyError):
        find("paint")
