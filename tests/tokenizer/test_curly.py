# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# curly tokenizer tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.tokenizer.curly import CurlyTokenizer


CFG1 = """# comment
interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 10.0.0.1/24;
            }
            family inet6 {
                address fe80::1/64;
            }
        }
        unit 1 {
            family inet {
                address 10.0.1.1/24;
            }
        }
    }
    ge-0/0/1 {
        unit 0 {
            family inet {
                address 10.0.2.1/24;
            }
        }
    }
}
services {
    isis {
        interface ge-0/0/0.0;
        interface ge-0/0/0.1;
        interface ge-0/0/1.0;
    }
}
"""

TOKENS1 = [
    ("interfaces",),
    ("interfaces", "ge-0/0/0"),
    ("interfaces", "ge-0/0/0", "unit", "0"),
    ("interfaces", "ge-0/0/0", "unit", "0", "family", "inet"),
    ("interfaces", "ge-0/0/0", "unit", "0", "family", "inet", "address", "10.0.0.1/24"),
    ("interfaces", "ge-0/0/0", "unit", "0", "family", "inet6"),
    ("interfaces", "ge-0/0/0", "unit", "0", "family", "inet6", "address", "fe80::1/64"),
    ("interfaces", "ge-0/0/0", "unit", "1"),
    ("interfaces", "ge-0/0/0", "unit", "1", "family", "inet"),
    ("interfaces", "ge-0/0/0", "unit", "1", "family", "inet", "address", "10.0.1.1/24"),
    ("interfaces", "ge-0/0/1"),
    ("interfaces", "ge-0/0/1", "unit", "0"),
    ("interfaces", "ge-0/0/1", "unit", "0", "family", "inet"),
    ("interfaces", "ge-0/0/1", "unit", "0", "family", "inet", "address", "10.0.2.1/24"),
    ("services",),
    ("services", "isis"),
    ("services", "isis", "interface", "ge-0/0/0.0"),
    ("services", "isis", "interface", "ge-0/0/0.1"),
    ("services", "isis", "interface", "ge-0/0/1.0")
]


@pytest.mark.parametrize("input,config,expected", [
    (CFG1, {"line_comment": "#", "explicit_eol": ";"}, TOKENS1),
])
def test_tokenizer(input, config, expected):
    tokenizer = CurlyTokenizer(input, **config)
    assert list(tokenizer) == expected
