# ----------------------------------------------------------------------
# main.Label test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
import pytest

# NOC modules
from noc.main.models.label import Label


@pytest.mark.parametrize(
    ("iter_labels", "expected"),
    [
        ((), []),
        (([],), []),
        (([], []), []),
        ((["x"],), ["x"]),
        ((["x", "x"],), ["x"]),
        ((["x"], ["x"]), ["x"]),
        ((["x", "y", "x"],), ["x", "y"]),
        ((["x", "y", "x"], ["x"]), ["x", "y"]),
        ((["scope::x"],), ["scope::x"]),
        ((["scope::x", "x"],), ["scope::x", "x"]),
        ((["scope::x", "scope::y"],), ["scope::x"]),
        ((["scope::x", "x", "scope::y"],), ["scope::x", "x"]),
        ((["x", "scope1::scope2::x", "scope1::scope2::x"],), ["x", "scope1::scope2::x"]),
    ],
)
def test_merge_labels(iter_labels: tuple[list[str]], expected: list[str]) -> None:
    assert Label.merge_labels(iter_labels) == expected


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("mylabel", False),
        ("*", False),
        ("myscope::mylabel", False),
        ("myscope::*", True),
        ("myscope::mysubscope::mylabel", False),
        ("myscope::mysubscope::*", True),
    ],
)
def test_is_wildcard(label: str, expected: bool) -> None:
    instance = Label(name=label)
    assert instance.is_wildcard is expected


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("mylabel", []),
        ("myscope::mylabel", ["myscope"]),
        ("myscope::mysubscope::mylabel", ["myscope", "myscope::mysubscope"]),
    ],
)
def test_iter_scopes(label: str, expected: list[str]) -> None:
    instance = Label(name=label)
    scopes = list(instance.iter_scopes())
    assert scopes == expected
