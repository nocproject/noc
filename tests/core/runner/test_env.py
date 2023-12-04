# ----------------------------------------------------------------------
# Evironment tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, List

# Pytest modules
import pytest

# NOC modules
from noc.core.runner.env import Environment


def env(*e: Dict[str, str]) -> Environment:
    """
    Create nested environment.

    From top to down.
    Returns:
        down environment
    """
    parent = None
    for data in e:
        env = Environment(data)
        if parent:
            env.set_parent(parent)
        parent = env
    return env


@pytest.mark.parametrize(
    ("env", "key", "expected"),
    [
        (env({"a": "1", "b": "2"}), "a", "1"),
        (env({"a": "1", "b": "2"}), "c", None),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "c", "3"),
        (env({"c": "3"}, {"a": "1", "b": "2"}), "c", "3"),
        (env({"a": "1", "b": "2"}, {"a": "3"}), "a", "3"),
    ],
)
def test_get(env: Environment, key: str, expected: Optional[str]):
    r = env.get(key)
    assert r == expected


@pytest.mark.parametrize(
    ("env", "key", "expected"),
    [
        (env({"a": "1", "b": "2"}), "a", "1"),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "c", "3"),
        (env({"c": "3"}, {"a": "1", "b": "2"}), "c", "3"),
        (env({"a": "1", "b": "2"}, {"a": "3"}), "a", "3"),
    ],
)
def test_getitem(env: Environment, key: str, expected: Optional[str]) -> None:
    r = env[key]
    assert r == expected


@pytest.mark.parametrize(
    ("env", "key"),
    [
        (env({"a": "1", "b": "2"}), "c"),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "d"),
    ],
)
def test_getitem_error(env: Environment, key: str) -> None:
    with pytest.raises(KeyError):
        env[key]


@pytest.mark.parametrize(
    ("env", "key", "expected"),
    [
        (env({"a": "1", "b": "2"}), "a", True),
        (env({"a": "1", "b": "2"}), "c", False),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "c", True),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "a", True),
        (env({"a": "1", "b": "2"}, {"c": "3"}), "d", False),
    ],
)
def test_contains(env: Environment, key: str, expected: bool) -> None:
    r = key in env
    assert r is expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        (env({"a": "1", "b": "2"}), ["a", "b"]),
        (env({"a": "1", "b": "2"}, {"c": "3"}), ["a", "b", "c"]),
        (env({"a": "1", "b": "2"}, {"a": "4", "c": "3"}), ["a", "b", "c"]),
        (
            env({"a": "1", "b": "2", "e": "7"}, {"a": "4", "c": "3"}, {"b": "5", "d": "6"}),
            ["a", "b", "c", "d", "e"],
        ),
    ],
)
def test_keys(env: Environment, expected: List[str]) -> None:
    r = list(sorted(env.keys()))
    assert r == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        (env({"a": "1", "b": "2"}), ["a", "b"]),
        (env({"a": "1", "b": "2"}, {"c": "3"}), ["a", "b", "c"]),
        (env({"a": "1", "b": "2"}, {"a": "4", "c": "3"}), ["a", "b", "c"]),
        (
            env({"a": "1", "b": "2", "e": "7"}, {"a": "4", "c": "3"}, {"b": "5", "d": "6"}),
            ["a", "b", "c", "d", "e"],
        ),
    ],
)
def test_iter(env: Environment, expected: List[str]) -> None:
    r = list(sorted(env))
    assert r == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        (env({"a": "1", "b": "2"}), ["1", "2"]),
        (env({"a": "1", "b": "2"}, {"c": "3"}), ["1", "2", "3"]),
        (env({"a": "1", "b": "2"}, {"a": "4", "c": "3"}), ["2", "3", "4"]),
        (
            env({"a": "1", "b": "2", "e": "7"}, {"a": "4", "c": "3"}, {"b": "5", "d": "6"}),
            ["3", "4", "5", "6", "7"],
        ),
    ],
)
def test_values(env: Environment, expected: List[str]) -> None:
    r = list(sorted(env.values()))
    assert r == expected


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        (env({"a": "1", "b": "2"}), [("a", "1"), ("b", "2")]),
        (env({"a": "1", "b": "2"}, {"c": "3"}), [("a", "1"), ("b", "2"), ("c", "3")]),
        (env({"a": "1", "b": "2"}, {"a": "4", "c": "3"}), [("a", "4"), ("b", "2"), ("c", "3")]),
        (
            env({"a": "1", "b": "2", "e": "7"}, {"a": "4", "c": "3"}, {"b": "5", "d": "6"}),
            [("a", "4"), ("b", "5"), ("c", "3"), ("d", "6"), ("e", "7")],
        ),
    ],
)
def test_items(env: Environment, expected: List[str]) -> None:
    r = list(sorted(env.items()))
    assert r == expected
