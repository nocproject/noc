# ----------------------------------------------------------------------
# Config params test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.config.base import BaseConfig
from noc.core.config.params import (
    BooleanParameter,
    BytesSizeParameter,
    FloatParameter,
    HandlerParameter,
    IntParameter,
    ListParameter,
    MapParameter,
    SecondsParameter,
    SecretParameter,
    StringParameter,
    UUIDParameter,
)


@pytest.mark.parametrize(
    ("cfg", "value", "expected"),
    [
        ({}, "str. test", "str. test"),
        ({}, 42, "42"),
        ({"choices": ["a", "b", "c", "1"]}, "a", "a"),
        ({"choices": ["a", "b", "c", "1"]}, 1, "1"),
    ],
)
def test_string_parameter(cfg: dict[str, object], value: object, expected: str) -> None:
    class Config(BaseConfig):
        string = StringParameter(**cfg)

    config = Config()
    assert config.string is None
    config.string = value
    assert config.string == expected


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({"default": "default"}, "default"),
        ({"choices": ["a", "b", "c"], "default": "b"}, "b"),
    ],
)
def test_string_parameter_defaults(cfg: dict[str, object], expected: str) -> None:
    class Config(BaseConfig):
        string = StringParameter(**cfg)

    config = Config()
    assert config.string == expected


def test_string_parameter_errors() -> None:
    class Config(BaseConfig):
        string = StringParameter(choices=["a", "b", "c", "1"])

    config = Config()
    with pytest.raises(ValueError):
        config.string = "d"


def test_string_parameter_none() -> None:
    class Config(BaseConfig):
        string = StringParameter()

    config = Config()
    assert config.string is None


def test_secret_parameter() -> None:
    class Config(BaseConfig):
        secret = SecretParameter()

    config = Config()
    config.secret = "password"
    assert config.secret == "password"


def test_secret_parameter_none() -> None:
    class Config(BaseConfig):
        secret = SecretParameter()

    config = Config()
    assert config.secret is None


def test_secret_parameter_defaults() -> None:
    class Config(BaseConfig):
        secret = SecretParameter(default="password")

    config = Config()
    assert config.secret == "password"


def test_uuid_parameter() -> None:
    class Config(BaseConfig):
        installation_id = UUIDParameter()

    config = Config()
    config.installation_id = "287fb1c7-dff8-495d-9c97-462a0456c817"
    assert config.installation_id == "287fb1c7-dff8-495d-9c97-462a0456c817"
    with pytest.raises(ValueError):
        config.installation_id = "xxxxxx"


def test_uuid_parameter_none() -> None:
    class Config(BaseConfig):
        installation_id = UUIDParameter()

    config = Config()
    assert config.installation_id is None


def test_uuid_parameter_defaults() -> None:
    class Config(BaseConfig):
        installation_id = UUIDParameter(default="287fb1c7-dff8-495d-9c97-462a0456c817")

    config = Config()
    assert config.installation_id == "287fb1c7-dff8-495d-9c97-462a0456c817"


def test_uuid_parameter_error() -> None:
    class Config(BaseConfig):
        installation_id = UUIDParameter()

    config = Config()
    with pytest.raises(ValueError):
        config.installation_id = "xxxxxx"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (42, 42),
        ("13", 13),
    ],
)
def test_int_parameter(value: object, expected: int) -> None:
    class Config(BaseConfig):
        integer = IntParameter()

    config = Config()
    config.integer = value
    assert config.integer == expected


def test_int_parameter_none() -> None:
    class Config(BaseConfig):
        integer = IntParameter()

    config = Config()
    assert config.integer is None


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({"default": 42}, 42),
        ({"default": "42"}, 42),
    ],
)
def test_int_parameter_default(cfg: dict[str, object], expected: int) -> None:
    class Config(BaseConfig):
        integer = IntParameter(**cfg)

    config = Config()
    assert config.integer == expected


@pytest.mark.parametrize(
    ("cfg", "value", "expected"),
    [
        ({"min": 42}, 50, 50),
        ({"min": 42}, "50", 50),
        ({"min": 50}, 50, 50),
        ({"min": 50}, "50", 50),
        ({"max": 60}, 50, 50),
        ({"max": 60}, "50", 50),
        ({"max": 50}, 50, 50),
        ({"max": 50}, "50", 50),
        ({"min": 10, "max": 20}, 10, 10),
        ({"min": 10, "max": 20}, "10", 10),
    ],
)
def test_int_parameter_range(cfg: dict[str, object], value: object, expected: int) -> None:
    class Config(BaseConfig):
        ranged = IntParameter(**cfg)

    config = Config()
    config.ranged = value
    assert config.ranged == expected


@pytest.mark.parametrize(
    ("cfg", "value"),
    [
        ({"min": 20}, 10),
        ({"max": 20}, 30),
        ({"min": 10, "max": 20}, 5),
        ({"min": 10, "max": 20}, 25),
    ],
)
def test_int_parameter_range_error(cfg: dict[str, object], value: object) -> None:
    class Config(BaseConfig):
        ranged = IntParameter(**cfg)

    config = Config()
    with pytest.raises(ValueError):
        config.ranged = value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (False, False),
        (True, True),
        (0, False),
        (1, True),
        ("y", True),
        ("t", True),
        ("true", True),
        ("yes", True),
        ("no", False),
    ],
)
def test_bool_parameter(value: object, expected: bool) -> None:
    class Config(BaseConfig):
        boolean = BooleanParameter()

    config = Config()
    config.boolean = value
    assert config.boolean is expected


def test_bool_parameter_none() -> None:
    class Config(BaseConfig):
        boolean = BooleanParameter()

    config = Config()
    assert config.boolean is None


@pytest.mark.parametrize(("cfg", "expected"), [])
def test_bool_parameter_default(cfg: dict[str, object], expected: bool) -> None:
    class Config(BaseConfig):
        boolean = BooleanParameter(**cfg)

    config = Config()
    assert config.boolean is expected


@pytest.mark.parametrize(
    ("cfg", "value", "expected"),
    [
        ({"item": StringParameter()}, [1], ["1"]),
        ({"item": StringParameter()}, [1, "2"], ["1", "2"]),
        ({"item": BooleanParameter()}, ["mo"], [False]),
        ({"item": BooleanParameter()}, ["mo", "yes", "t", "y"], [False, True, True, True]),
    ],
)
def test_list_parameter(
    cfg: dict[str, object], value: list[object], expected: list[object]
) -> None:
    class Config(BaseConfig):
        items = ListParameter(**cfg)

    config = Config()
    config.items = value
    assert config.items == expected


def test_list_parameter_none() -> None:
    class Config(BaseConfig):
        items = ListParameter[str](item=StringParameter())

    config = Config()
    assert config.items is None


def test_list_parameter_default() -> None:
    class Config(BaseConfig):
        items = ListParameter[str](item=StringParameter(), default=[1, "2"])

    config = Config()
    assert config.items == ["1", "2"]


def test_float_parameter() -> None:
    class Config(BaseConfig):
        f = FloatParameter()
        default_f = FloatParameter(default=1.0)

    config = Config()
    # f
    assert config.f is None
    config.f = 1.0
    assert config.f == 1.0
    config.f = "5.0"
    assert config.f == 5.0
    with pytest.raises(ValueError):
        config.f = "xxx"
    # default_f
    assert config.default_f == 1.0


@pytest.mark.parametrize(("value", "expected"), [("one", 1), ("two", 2)])
def test_map_parameter(value: str, expected: int) -> None:
    class Config(BaseConfig):
        m = MapParameter[int](mappings={"one": 1, "two": 2})

    config = Config()
    config.m = value
    assert config.m == expected


def test_map_parameter_none() -> None:
    class Config(BaseConfig):
        m = MapParameter[int](mappings={"one": 1, "two": 2})

    config = Config()
    assert config.m is None


def test_map_parameter_default() -> None:
    class Config(BaseConfig):
        m = MapParameter[int](mappings={"one": 1, "two": 2}, default="one")

    config = Config()
    assert config.m == 1


def test_map_parameter_error() -> None:
    class Config(BaseConfig):
        m = MapParameter[int](mappings={"one": 1, "two": 2})

    config = Config()
    with pytest.raises(ValueError):
        config.m = "three"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (15, 15),
        ("15", 15),
        ("1M", 60),
        ("5M", 300),
        ("1h", 3600),
        ("5h", 18000),
        ("1d", 86400),
        ("5d", 432000),
        ("1w", 604800),
        ("5w", 3024000),
        ("1m", 2592000),
        ("5m", 12960000),
        ("1y", 31536000),
        ("5y", 157680000),
    ],
)
def test_seconds_parameter(value: object, expected: int) -> None:
    class Config(BaseConfig):
        s = SecondsParameter()

    config = Config()
    config.s = value
    assert config.s == expected


def test_seconds_parameter_none() -> None:
    class Config(BaseConfig):
        s = SecondsParameter()

    config = Config()
    assert config.s is None


@pytest.mark.parametrize(
    ("cfg", "expected"), [({"default": 15}, 15), ({"default": "15"}, 15), ({"default": "1h"}, 3600)]
)
def test_seconds_parameter_default(cfg: dict[str, object], expected: int) -> None:
    class Config(BaseConfig):
        s = SecondsParameter(**cfg)

    config = Config()
    assert config.s == expected


def test_bytes_parameter() -> None:
    class Config(BaseConfig):
        s = BytesSizeParameter()
        default_s = BytesSizeParameter(default="1M")

    config = Config()
    # s
    assert config.s is None
    config.s = 15
    assert config.s == 15
    config.s = "15"
    assert config.s == 15
    config.s = "1K"
    assert config.s == 1024
    config.s = "5K"
    assert config.s == 5120
    config.s = "1M"
    assert config.s == 1048576
    config.s = "5M"
    assert config.s == 5242880
    config.s = "1G"
    assert config.s == 1073741824
    config.s = "5G"
    assert config.s == 5368709120
    config.s = "1T"
    assert config.s == 1099511627776
    config.s = "5T"
    assert config.s == 5497558138880
    # default_s
    assert config.default_s == 1048576


def my_handler():
    pass


HANDLER_PATH = f"{__name__}.my_handler"


def test_handler() -> None:
    class Config:
        handler = HandlerParameter()

    config = Config()
    config.handler = HANDLER_PATH
    assert config.handler == HANDLER_PATH


def test_handler_none() -> None:
    class Config:
        handler = HandlerParameter()

    config = Config()
    assert config.handler is None


def test_handler_default() -> None:
    class Config:
        handler = HandlerParameter(default=HANDLER_PATH)

    config = Config()
    assert config.handler == HANDLER_PATH
