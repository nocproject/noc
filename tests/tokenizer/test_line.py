# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test line tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.tokenizer.line import LineTokenizer

CFG1 = """first line
second long line

third  strange   line
"""

TOKENS1 = [
    ("first", "line"),
    ("second", "long", "line"),
    ("third", "strange", "line")
]

CFG2 = """# Line comment
first line
second line # with comment

third maybe strange line
"""

TOKENS2 = [
    ("first", "line"),
    ("second", "line"),
    ("third", "maybe", "strange", "line")
]

CFG3 = """// C-style comments
first line
second // commented
"""

TOKENS3 = [
    ("first", "line"),
    ("second",)
]

CFG4 = """! Config
interface e0
    description test
\tno shutdown
"""

TOKENS4 = [
    ("interface", "e0"),
    ("    ", "description", "test"),
    ("    ", "no", "shutdown")
]

CFG5 = """! Config
interface e0
    description "test interface"
    ip address 10.10.10.10 255.255.255.0

interface e1
    description "unterminated description

interface e2
    description "multi line" interface e2 "description here"
"""

TOKENS5 = [
    ("interface", "e0"),
    ("    ", "description", "test interface"),
    ("    ", "ip", "address", "10.10.10.10", "255.255.255.0"),
    ("interface", "e1"),
    ("    ", "description", "unterminated description"),
    ("interface", "e2"),
    ("    ", "description", "multi line", "interface", "e2", "description here")
]


@pytest.mark.parametrize("input,config,expected", [
    (CFG1, {}, TOKENS1),
    (CFG2, {"inline_comment": "#"}, TOKENS2),
    (CFG3, {"inline_comment": "//"}, TOKENS3),
    (CFG4, {"line_comment": "!", "tab_width": 4, "keep_indent": True}, TOKENS4),
    (CFG5, {"line_comment": "!", "tab_width": 4, "keep_indent": True, "string_quote": "\""}, TOKENS5)
])
def test_tokenizer(input, config, expected):
    tokenizer = LineTokenizer(input, **config)
    assert list(tokenizer) == expected
