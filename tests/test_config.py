# -*- coding: utf-8 -*-
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
    StringParameter, SecretParameter, IntParameter, BooleanParameter, FloatParameter, MapParameter,
    HandlerParameter, SecondsParameter, ListParameter
)


def test_string_parameter():
    class Config(BaseConfig):
        string = StringParameter()
        default_string = StringParameter(default="default")
        choices = StringParameter(choices=["a", "b", "c", "1"])
        default_choices = StringParameter(choices=["a", "b", "c"], default="b")

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