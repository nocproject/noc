# ----------------------------------------------------------------------
# noc.core.config tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.config.base import BaseConfig
from noc.core.config.params import (
    StringParameter,
    SecretParameter,
    IntParameter,
    BooleanParameter,
    FloatParameter,
    MapParameter,
    HandlerParameter,
    SecondsParameter,
    ListParameter,
    BytesParameter,
    UUIDParameter,
)


def test_string_parameter():
    class Config(BaseConfig):
        string = StringParameter()
        default_string = StringParameter(default="default")
        choices = StringParameter(choices=["a", "b", "c", "1"])
        default_choices = StringParameter(choices=["a", "b", "c"], default="b")
        default_choices_with_none = StringParameter(
            choices=["a", "b", "c", "none"], default="none", none_value="none"
        )

    config = Config()
    # Test string
    assert config.string is None
    config.string = "str. test"
    assert config.string == "str. test"
    config.string = 42
    assert config.string == "42"
    # Test defaults
    assert config.default_string == "default"
    # Test choices
    assert config.choices is None
    config.choices = "a"
    assert config.choices == "a"
    config.choices = 1
    assert config.choices == "1"
    with pytest.raises(ValueError):
        config.choices = "d"
    # Test choices with defaults
    assert config.default_choices == "b"
    assert config.default_choices_with_none is None


def test_secret_parameters():
    class Config(BaseConfig):
        secret = SecretParameter()

    config = Config()
    assert config.secret is None
    config.secret = "password"
    assert config.secret == "password"


def test_uuid_parameters():
    class Config(BaseConfig):
        installation_id = UUIDParameter()

    config = Config()
    assert config.installation_id is None
    config.installation_id = "287fb1c7-dff8-495d-9c97-462a0456c817"
    assert config.installation_id == "287fb1c7-dff8-495d-9c97-462a0456c817"
    with pytest.raises(ValueError):
        config.installation_id = "xxxxxx"


def test_int_parameter():
    class Config(BaseConfig):
        integer = IntParameter()
        default_integer = IntParameter(default=42)
        min_integer = IntParameter(min=42)
        max_integer = IntParameter(max=42)
        ranged_integer = IntParameter(min=10, max=20)

    config = Config()
    # Test int
    assert config.integer is None
    config.integer = 42
    assert config.integer == 42
    config.integer = "13"
    assert config.integer == 13
    # Test default integer
    assert config.default_integer == 42
    # Test min
    config.min_integer = 50
    assert config.min_integer == 50
    with pytest.raises(ValueError):
        config.min_integer = 40
    assert config.min_integer == 50
    config.min_integer = 42
    assert config.min_integer == 42
    # Ranged integer
    assert config.ranged_integer is None
    with pytest.raises(ValueError):
        config.ranged_integer = 9
    assert config.ranged_integer is None
    config.ranged_integer = 10
    assert config.ranged_integer == 10
    config.ranged_integer = 15
    assert config.ranged_integer == 15
    config.ranged_integer = 20
    assert config.ranged_integer == 20
    with pytest.raises(ValueError):
        config.ranged_integer = 21
    assert config.ranged_integer == 20


def test_bool_parameter():
    class Config(BaseConfig):
        boolean = BooleanParameter()
        default_boolean = BooleanParameter(default=True)

    config = Config()
    assert config.boolean is None
    config.boolean = False
    assert config.boolean is False
    config.boolean = True
    assert config.boolean is True
    config.boolean = 0
    assert config.boolean is False
    config.boolean = 1
    assert config.boolean is True
    config.boolean = "y"
    assert config.boolean is True
    config.boolean = "t"
    assert config.boolean is True
    config.boolean = "true"
    assert config.boolean is True
    config.boolean = "yes"
    assert config.boolean is True
    config.boolean = "no"
    assert config.boolean is False
    # check defaults
    assert config.default_boolean is True


def test_list_parameter():
    class Config(BaseConfig):
        str_list = ListParameter(item=StringParameter())
        default_str_list = ListParameter(item=StringParameter(), default=[1, "2"])
        bool_list = ListParameter(item=BooleanParameter())

    config = Config()
    # str_list
    assert config.str_list is None
    config.str_list = [1]
    assert config.str_list == ["1"]
    config.str_list += ["2"]
    assert config.str_list == ["1", "2"]
    # default_str_list
    assert config.default_str_list == ["1", "2"]
    # bool_list
    config.bool_list = ["no", True]
    assert config.bool_list == [False, True]


def test_float_parameter():
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


def test_map_parameter():
    class Config(BaseConfig):
        m = MapParameter(mappings={"one": 1, "two": 2})
        default_m = MapParameter(mappings={"one": 1, "two": 2}, default="one")

    config = Config()
    # m
    assert config.m is None
    config.m = "one"
    assert config.m == 1
    config.m = "two"
    assert config.m == 2
    with pytest.raises(ValueError):
        config.m = "three"
    # default_m
    assert config.default_m == 1


def test_seconds_parameter():
    class Config(BaseConfig):
        s = SecondsParameter()
        default_s = SecondsParameter(default="1M")

    config = Config()
    # s
    assert config.s is None
    config.s = 15
    assert config.s == 15
    config.s = "15"
    assert config.s == 15
    config.s = "1M"
    assert config.s == 60
    config.s = "5M"
    assert config.s == 300
    config.s = "1h"
    assert config.s == 3600
    config.s = "5h"
    assert config.s == 18000
    config.s = "1d"
    assert config.s == 86400
    config.s = "5d"
    assert config.s == 432000
    config.s = "1w"
    assert config.s == 604800
    config.s = "5w"
    assert config.s == 3024000
    config.s = "1m"
    assert config.s == 2592000
    config.s = "5m"
    assert config.s == 12960000
    config.s = "1y"
    assert config.s == 31536000
    config.s = "5y"
    assert config.s == 157680000
    # default_s
    assert config.default_s == 60


def test_bytes_parameter():
    class Config(BaseConfig):
        s = BytesParameter()
        default_s = BytesParameter(default="1M")

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


def test_handler():
    class Config:
        handler = HandlerParameter()
        default_handler = HandlerParameter(default="noc.tests.test_config.my_handler")

    config = Config()
    assert config.handler is None
    assert config.default_handler == "noc.tests.test_config.my_handler"
