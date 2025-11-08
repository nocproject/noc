# ----------------------------------------------------------------------
# noc.core.rpsl unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.rpsl import rpsl_format, rpsl_multiple


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ([], "\n"),
        (["key1: value1", "key2"], "key1:value1\n"),
        (["key1: value1", "key2: value2"], "key1:value1\nkey2:value2\n"),
        (["key1: value1", "key2: value2", "bad_key3 bad_value3"], "key1:value1\nkey2:value2\n"),
    ],
)
def test_rpsl_format(config, expected):
    assert rpsl_format(config, 1) == expected


@pytest.mark.parametrize(
    ("config1", "config2", "config3", "config4", "expected"),
    [("key1", "value1", "key2", "value2", "key1:value1\nkey2:value2\n")],
)
def test_rpsl_multiple(config1, config2, config3, config4, expected):
    kv = []
    kv += rpsl_multiple(config1, config2)
    kv += rpsl_multiple(config3, config4)
    assert rpsl_format(kv, 1) == expected
