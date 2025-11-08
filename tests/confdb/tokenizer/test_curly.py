# ----------------------------------------------------------------------
# curly tokenizer tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.curly import CurlyTokenizer


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
    ("services", "isis", "interface", "ge-0/0/1.0"),
]

CFG2 = """snmp {
    community pub1ic {
        authorization read-only;
    }
    community nnnn {
        authorization read-only;
    }
    community "@default" {
        authorization read-only;
    }
    community TTT {
        authorization read-only;
        clients {
            10.10.10.0/26;
        }
    }
}
"""

TOKENS2 = [
    ("snmp",),
    ("snmp", "community", "pub1ic"),
    ("snmp", "community", "pub1ic", "authorization", "read-only"),
    ("snmp", "community", "nnnn"),
    ("snmp", "community", "nnnn", "authorization", "read-only"),
    ("snmp", "community", "@default"),
    ("snmp", "community", "@default", "authorization", "read-only"),
    ("snmp", "community", "TTT"),
    ("snmp", "community", "TTT", "authorization", "read-only"),
    ("snmp", "community", "TTT", "clients"),
    ("snmp", "community", "TTT", "clients", "10.10.10.0/26"),
]

CFG3 = """dns {
    search-domains [ "test.example.com" "example.com" ];
}
"""

TOKENS3 = [
    ("dns",),
    ("dns", "search-domains", "test.example.com"),
    ("dns", "search-domains", "example.com"),
]


@pytest.mark.parametrize(
    ("input", "config", "expected"),
    [
        (CFG1, {"line_comment": "#", "explicit_eol": ";"}, TOKENS1),
        (CFG2, {"line_comment": "#", "explicit_eol": ";", "string_quote": '"'}, TOKENS2),
        (
            CFG3,
            {
                "line_comment": "#",
                "explicit_eol": ";",
                "string_quote": '"',
                "start_of_group": "[",
                "end_of_group": "]",
            },
            TOKENS3,
        ),
    ],
)
def test_tokenizer(input, config, expected):
    tokenizer = CurlyTokenizer(input, **config)
    assert list(tokenizer) == expected
