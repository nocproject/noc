# ----------------------------------------------------------------------
# noc.core.path tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 Gufo Labs
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path
from typing import Tuple, Dict

# Third-party modules
import pytest

# NOC modules
from noc.core.path import safe_path, _clean_component, safe_json_path


@pytest.mark.parametrize(
    ("s", "expected"),
    [
        ("clean", "clean"),
        ("  many   spaces     ", "many_spaces"),
        ("!@#SFP+$%%", "SFP+"),
        ("to be (or not to)   ", "to_be_or_not_to"),
        ("Здравствуй, товарищ!", "Zdravstvuy_tovarishch"),
    ],
)
def test_clean_component(s: str, expected: str) -> None:
    r = _clean_component(s)
    assert r == expected


@pytest.mark.parametrize(
    ("args", "kwargs", "expected"),
    [
        (("item",), {}, ("item",)),
        (("split|item",), {"sep": "|"}, ("split", "item")),
        (("split", "item"), {"suffix": ".json"}, ("split", "item.json")),
        (
            ("switch | SFP+-48-ports",),
            {"sep": "|", "suffix": ".json"},
            ("switch", "SFP+-48-ports.json"),
        ),
        (
            ("little (?)", "bit", "of кириллица!"),
            {"suffix": ".json"},
            ("little", "bit", "of_kirillitsa.json"),
        ),
        (("x", "@#@$", "y | ()()"), {"sep": "|", "suffix": ".json"}, ("x", "y.json")),
    ],
)
def test_safe_path(args: Tuple[str], kwargs: Dict[str, str], expected: Tuple[str]) -> None:
    r = safe_path(*args, **kwargs)
    assert r == Path(*expected)


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("item",), ("item.json",)),
        (("split|item",), ("split", "item.json")),
        (("split", "item"), ("split", "item.json")),
        (
            ("switch | SFP+-48-ports",),
            ("switch", "SFP+-48-ports.json"),
        ),
        (
            ("little (?)", "bit", "of кириллица!"),
            ("little", "bit", "of_kirillitsa.json"),
        ),
    ],
)
def test_safe_json_path(args: Tuple[str], expected: Tuple[str]) -> None:
    r = safe_json_path(*args)
    assert r == Path(*expected)
