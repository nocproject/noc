# ---------------------------------------------------------------------
# SVG tests utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Tuple, Dict, List
import xml.etree.ElementTree as ET
import tempfile

# Third-party modules
import pytest

# NOC modules
from noc.core.svg import SVG

BROKEN = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <g id="1">
    <rect id="2"/>
    <g id="3"/>
        <rect id="4"/>
    </g>
  </g>
</svg>
"""

G1 = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="1">
    <rect id="2" />
    <g id="3">
      <rect id="4" />
    </g>
  </g>
</svg>"""

G2 = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="1">
    <rect id="2" />
    <g id="3">
      <rect id="4" />
    </g>
    <rect id="5" />
  </g>
</svg>"""

G3 = """<svg xmlns="http://www.w3.org/2000/svg">
  <g id="1">
    <rect id="2" />
    <g id="3">
      <rect id="5" />
    </g>
  </g>
</svg>"""

SRC_DEFS1 = """<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <circle id="myCircle" cx="0" cy="0" r="5" />
  </defs>
</svg>"""

OUT_DEFS1 = """<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <circle id="myCircle" cx="0" cy="0" r="5" />
  </defs>
  <g id="1">
    <rect id="2" />
    <g id="3">
      <rect id="4" />
    </g>
  </g>
</svg>"""

BROKEN_DEFS1 = """<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <circle cx="0" cy="0" r="5" />
  </defs>
</svg>
"""

OUTER = """<svg xmlns="http://www.w3.org/2000/svg">
  <rect width="736.6" height="178" style="stroke: rgb(0, 0, 0); fill: rgb(220, 117, 42);"/>
  <text style="fill: rgb(222, 51, 189); font-family: Arial, sans-serif; font-size: 21.5px; white-space: pre;" x="5" y="173.387">NOC 4U</text>
  <rect x="17.252" y="13.474" width="650" height="50" style="stroke: rgb(0, 0, 0); fill: rgb(145, 158, 195);" id="slot-1"/>
  <rect x="17.252" y="74.288" width="650" height="50" style="stroke: rgb(0, 0, 0); fill: rgb(145, 158, 195);" id="slot-2"/>
  <rect x="-759.37" y="-149.288" width="100" height="25" style="stroke: rgb(0, 0, 0); opacity: 0.9; fill: rgb(163, 89, 89); transform-box: fill-box; transform-origin: 50% 50%;" transform="matrix(0, 1, -1, 0, 1399.635284, 200.261993)" id="slot-3"/>
  <rect x="-759.37" y="-149.288" width="100" height="25" style="stroke: rgb(0, 0, 0); opacity: 0.9; fill: rgb(163, 89, 89); transform-origin: -709.37px -136.788px;" transform="matrix(0, 1, -1, 0, 1428.440308, 200.288025)" id="slot-4"/>
</svg>"""

INNER = """<svg viewBox="0 0 650 50" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:bx="https://boxy-svg.com">
  <defs>
    <symbol id="noc-rj-45" viewBox="0 0 15.71 12.568" bx:pinned="true">
      <title>RJ-45</title>
      <g id="g-1" transform="matrix(0.07855001091957092, 0, 0, 0.07855001091957092, 2.842170943040401e-14, 7.105427357601002e-15)">
        <rect style="fill:#cccccc;fill-opacity:1;stroke-width:0;stroke-miterlimit:4;stroke-dasharray:none" id="rect-1" width="200" height="160" x="0" y="0"/>
      </g>
    </symbol>
  </defs>
  <rect width="650" height="50" style="fill: rgb(216, 216, 216); stroke: rgb(0, 0, 0);"/>
  <text style="white-space: pre; fill: rgb(51, 51, 51); font-family: Arial, sans-serif; font-size: 15.7px;" x="11.453" y="27.649">LC-4</text>
  <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 151.79872131347656, 20.145544052124023)" id="slot-3" xlink:href="#noc-rj-45"/>
  <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 136.08871459960938, 20.145544052124023)" id="slot-2" xlink:href="#noc-rj-45"/>
</svg>"""

OUTER_OUT = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:ns1="https://boxy-svg.com" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <symbol id="noc-rj-45" viewBox="0 0 15.71 12.568" ns1:pinned="true">
      <title>RJ-45</title>
      <g id="g-1" transform="matrix(0.07855001091957092, 0, 0, 0.07855001091957092, 2.842170943040401e-14, 7.105427357601002e-15)">
        <rect style="fill:#cccccc;fill-opacity:1;stroke-width:0;stroke-miterlimit:4;stroke-dasharray:none" id="rect-1" width="200" height="160" x="0" y="0" />
      </g>
    </symbol>
  </defs>
  <rect width="736.6" height="178" style="stroke: rgb(0, 0, 0); fill: rgb(220, 117, 42);" />
  <text style="fill: rgb(222, 51, 189); font-family: Arial, sans-serif; font-size: 21.5px; white-space: pre;" x="5" y="173.387">NOC 4U</text>
  <g transform="translate(17.252, 13.474)" id="slot-1">
    <rect width="650" height="50" style="fill: rgb(216, 216, 216); stroke: rgb(0, 0, 0);" />
    <text style="white-space: pre; fill: rgb(51, 51, 51); font-family: Arial, sans-serif; font-size: 15.7px;" x="11.453" y="27.649">LC-4</text>
    <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 151.79872131347656, 20.145544052124023)" id="slot-1-slot-3" xlink:href="#noc-rj-45" />
    <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 136.08871459960938, 20.145544052124023)" id="slot-1-slot-2" xlink:href="#noc-rj-45" />
  </g>
  <g transform="translate(17.252, 74.288)" id="slot-2">
    <rect width="650" height="50" style="fill: rgb(216, 216, 216); stroke: rgb(0, 0, 0);" />
    <text style="white-space: pre; fill: rgb(51, 51, 51); font-family: Arial, sans-serif; font-size: 15.7px;" x="11.453" y="27.649">LC-4</text>
    <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 151.79872131347656, 20.145544052124023)" id="slot-2-slot-3" xlink:href="#noc-rj-45" />
    <use width="15.710000038146973" height="12.567999839782715" transform="matrix(1, 0, 0, 1, 136.08871459960938, 20.145544052124023)" id="slot-2-slot-2" xlink:href="#noc-rj-45" />
  </g>
  <rect x="-759.37" y="-149.288" width="100" height="25" style="stroke: rgb(0, 0, 0); opacity: 0.9; fill: rgb(163, 89, 89); transform-box: fill-box; transform-origin: 50% 50%;" transform="matrix(0, 1, -1, 0, 1399.635284, 200.261993)" id="slot-3" />
  <rect x="-759.37" y="-149.288" width="100" height="25" style="stroke: rgb(0, 0, 0); opacity: 0.9; fill: rgb(163, 89, 89); transform-origin: -709.37px -136.788px;" transform="matrix(0, 1, -1, 0, 1428.440308, 200.288025)" id="slot-4" />
</svg>"""


def test_parse_error() -> None:
    with pytest.raises(ValueError):
        SVG.from_string(BROKEN)


def test_from_string() -> None:
    SVG.from_string(G1)


def test_from_file() -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, "w") as fp:
            fp.write(G1)
        SVG.from_file(tmp.name)


def test_to_string() -> None:
    svg = SVG.from_string(G1)
    out = svg.to_string()
    assert out == G1


def test_clone() -> None:
    Q = ".//*[@id='4']"
    svg = SVG.from_string(G1)
    cloned = svg.clone()
    # Alter cloned
    ce4 = cloned.get_tree().find(Q)
    assert ce4 is not None
    ce4.set("width", "100")
    # The original must be unaltered
    e4 = svg.get_tree().find(Q)
    assert e4 is not None
    assert e4.get("width") is None
    assert ce4.get("width") == "100"
    assert id(e4) != id(ce4)


def test_add_prefix() -> None:
    svg = SVG.from_string(G1)
    e4 = svg.get_tree().find(".//*[@id='4']")
    assert e4 is not None
    svg.add_prefix("p1-")
    e4 = svg.get_tree().find(".//*[@id='4']")
    assert e4 is None
    e4 = svg.get_tree().find(".//*[@id='p1-4']")
    assert e4 is not None


def test_is_equal_same() -> None:
    svg = SVG.from_string(G1)
    e1 = svg.get_tree().find(".//*[@id='4']")
    assert e1 is not None
    assert SVG.is_equal(e1, e1) is True


def test_is_equal_tag_mismatch() -> None:
    svg = SVG.from_string(G1)
    e1 = svg.get_tree().find(".//*[@id='3']")
    assert e1 is not None
    e2 = svg.get_tree().find(".//*[@id='4']")
    assert e2 is not None
    assert SVG.is_equal(e1, e2) is False


def test_is_equal_attrib_mismatch() -> None:
    svg = SVG.from_string(G1)
    e1 = svg.get_tree().find(".//*[@id='2']")
    assert e1 is not None
    e2 = svg.get_tree().find(".//*[@id='4']")
    assert e2 is not None
    assert SVG.is_equal(e1, e2) is False


def test_is_equal_cloned_swallow() -> None:
    svg = SVG.from_string(G1)
    e1 = svg.get_tree().find(".//*[@id='4']")
    assert e1 is not None
    cloned = svg.clone()
    e2 = cloned.get_tree().find(".//*[@id='4']")
    assert e2 is not None
    assert id(e1) != id(e2)
    assert SVG.is_equal(e1, e2) is True


def test_is_equal_cloned_deep() -> None:
    svg = SVG.from_string(G1)
    e1 = svg.get_tree().find(".//*[@id='1']")
    assert e1 is not None
    cloned = svg.clone()
    e2 = cloned.get_tree().find(".//*[@id='1']")
    assert e2 is not None
    assert id(e1) != id(e2)
    assert SVG.is_equal(e1, e2) is True


def test_is_equal_deep_mismatch1() -> None:
    svg1 = SVG.from_string(G1)
    e1 = svg1.get_tree().find(".//*[@id='1']")
    assert e1 is not None
    svg2 = SVG.from_string(G2)
    e2 = svg2.get_tree().find(".//*[@id='1']")
    assert e2 is not None
    assert id(e1) != id(e2)
    assert SVG.is_equal(e1, e2) is False


def test_is_equal_deep_mismatch2() -> None:
    svg1 = SVG.from_string(G1)
    e1 = svg1.get_tree().find(".//*[@id='1']")
    assert e1 is not None
    svg2 = SVG.from_string(G3)
    e2 = svg2.get_tree().find(".//*[@id='1']")
    assert e2 is not None
    assert id(e1) != id(e2)
    assert SVG.is_equal(e1, e2) is False


def test_empty_defs() -> None:
    svg = SVG.from_string(G1)
    assert svg.get_defs() is None


def test_defs1() -> None:
    svg = SVG.from_string(G1)
    assert svg.get_defs() is None
    svg2 = SVG.from_string(SRC_DEFS1)
    defs = svg2.get_defs()
    assert defs is not None
    # Append defs
    for c in defs:
        svg.append_def(c)
    out = svg.to_string()
    assert out == OUT_DEFS1
    # Check _defs structure is populated
    assert "myCircle" in svg._defs
    # Try to append the same
    svg3 = SVG.from_string(SRC_DEFS1)
    defs = svg3.get_defs()
    assert defs is not None
    # Append defs
    for c in defs:
        svg.append_def(c)
    out = svg.to_string()
    assert out == OUT_DEFS1


def test_broken_defs() -> None:
    svg = SVG.from_string(G1)
    assert svg.get_defs() is None
    svg2 = SVG.from_string(BROKEN_DEFS1)
    defs = svg2.get_defs()
    assert defs is not None
    # Append defs
    for c in defs:
        svg.append_def(c)


def test_defs_same() -> None:
    svg = SVG.from_string(SRC_DEFS1)
    assert svg.get_defs() is not None
    svg2 = SVG.from_string(SRC_DEFS1)
    defs = svg2.get_defs()
    assert defs is not None
    # Append defs
    for c in defs:
        svg.append_def(c)
    out = svg.to_string()
    assert out == SRC_DEFS1


@pytest.mark.parametrize(
    ("attrs", "expected"),
    [
        ({}, None),
        ({"width": "100"}, None),
        ({"style": "fill:red"}, None),
        ({"style": "transform-origin: 50% 50%"}, (0.0, 0.0)),
        ({"style": "transform-origin: 50% 50%", "width": "100", "height": "50"}, (50.0, 25.0)),
        ({"style": "transform-origin: 5px 10px"}, (5.0, 10.0)),
        ({"style": "transform-origin: 5 10"}, (5.0, 10.0)),
    ],
)
def test_transform_origin(attrs: Dict[str, str], expected: Optional[Tuple[float, float]]) -> None:
    el = ET.Element("rect", attrs)
    transform_origin = SVG.get_transform_origin(el)
    assert transform_origin == expected


@pytest.mark.parametrize(
    ("attrs", "expected"),
    [
        ({"x": "100", "y": "50"}, "translate(100, 50)"),
        ({"x": "100.5", "y": "50"}, "translate(100.5, 50)"),
        ({"x": "100", "y": "50.25"}, "translate(100, 50.25)"),
        (
            {
                "x": "-759.37",
                "y": "-149.288",
                "width": "100",
                "height": "25",
                "style": "stroke: rgb(0, 0, 0); opacity: 0.9; fill: rgb(163, 89, 89); transform-origin: -709.37px -136.788px;",
                "transform": "matrix(0, 1, -1, 0, 1428.440308, 200.288025)",
                "id": "slot-4",
            },
            "translate(-709.37, -136.788) matrix(0, 1, -1, 0, 1428.440308, 200.288025) translate(-50, -12.5)",
        ),
    ],
)
def test_translate(attrs: Dict[str, str], expected: Optional[Tuple[float, float]]) -> None:
    el = ET.Element("rect", attrs)
    translate = SVG.get_transform(el)
    assert translate == expected


def test_embed_invalid_slot() -> None:
    outer = SVG.from_string(OUTER)
    inner = SVG.from_string(INNER)
    with pytest.raises(ValueError):
        outer.embed("slot-11", inner.clone())


def test_embed() -> None:
    outer = SVG.from_string(OUTER)
    inner = SVG.from_string(INNER)
    outer.embed("slot-1", inner)
    outer.embed("slot-2", inner)
    out = outer.to_string()
    assert out == OUTER_OUT


D1 = """<svg width="15"></svg>"""
D2 = """<svg width="15mm"></svg>"""
D3 = """<svg height="10"></svg>"""
D4 = """<svg height="10mm"></svg>"""
D5 = """<svg viewBox="0 0 15 10"></svg>"""


@pytest.mark.parametrize(
    ("s", "expected"), [(D1, 15.0), (D2, 15.0), (D3, 0.0), (D4, 0.0), (D5, 15.0)]
)
def test_width(s, expected) -> None:
    svg = SVG.from_string(s)
    assert svg.width == expected


@pytest.mark.parametrize(
    ("s", "expected"), [(D1, 0.0), (D2, 0.0), (D3, 10.0), (D4, 10.0), (D5, 10.0)]
)
def test_height(s, expected) -> None:
    svg = SVG.from_string(s)
    assert svg.height == expected


@pytest.mark.parametrize(
    ("s", "expected"), [(G1, ["1", "2", "3", "4"]), (G2, ["1", "2", "3", "4", "5"])]
)
def test_iter_id(s: str, expected: List[str]) -> None:
    svg = SVG.from_string(s)
    ids = list(svg.iter_id())
    assert ids == expected
