# ----------------------------------------------------------------------
# ini tokenizer test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.ini import INITokenizer

CFG1 = """[section #1]
key1 = 12
next key = x

[section #2]
key11 = 15
next key = y
"""

TOKENS1 = [
    ("section #1", "key1", "12"),
    ("section #1", "next key", "x"),
    ("section #2", "key11", "15"),
    ("section #2", "next key", "y"),
]


@pytest.mark.parametrize(("input", "config", "expected"), [(CFG1, {}, TOKENS1)])
def test_tokenizer(input, config, expected):
    tokenizer = INITokenizer(input, **config)
    assert list(tokenizer) == expected
