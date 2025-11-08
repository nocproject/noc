# ----------------------------------------------------------------------
# noc.core.prettyjson unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.prettyjson import to_json


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ({"key1": "value1", "key2": "value2", "key3": "value3"}, True),
        (["key1value1key2value2key3value3"], False),
    ],
)
def test_prettyjson(config, expected):
    assert to_json(config).startswith("{\n") == expected


@pytest.mark.parametrize(
    ("config", "expected"), [(("key1", "value1", "key2", "value2", "key3", "value3"), True)]
)
def test_prettyjson_error(config, expected):
    with pytest.raises(TypeError):
        assert to_json(config).startswith("{\n") == expected
