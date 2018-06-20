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
