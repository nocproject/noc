# ----------------------------------------------------------------------
# Juniper.JUNOS Profile test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.profile.loader import loader


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (
            """
show configuration services rpm | display json

{master:0}
""",
            {},
        ),
        (
            """

{master:0}
""",
            {},
        ),
        (
            """

""",
            {},
        ),
        (
            """
show chassis environment | display json
{
    "environment-information" : [
    {
        "attributes" : {"xmlns" : "http://xml.juniper.net/junos/21.4R0/junos-chassis"},
        "environment-item" : [
        {
            "name" : [
            {
                "data" : "FPC 0 Power Supply 0"
            }
            ],
            "class" : [
            {
                "data" : "Power"
            }
            ],
            "status" : [
            {
                "data" : "OK"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "FPC 0 Power Supply 1"
            }
            ],
            "class" : [
            {
                "data" : "Power"
            }
            ],
            "status" : [
            {
                "data" : "OK"
            }
            ]
        }
        ]
    }
    ]
}

{master:0}

""",
            {
                "environment-information": [
                    {
                        "attributes": {
                            "xmlns": "http://xml.juniper.net/junos/21.4R0/junos-chassis"
                        },
                        "environment-item": [
                            {
                                "name": [{"data": "FPC 0 Power Supply 0"}],
                                "class": [{"data": "Power"}],
                                "status": [{"data": "OK"}],
                            },
                            {
                                "name": [{"data": "FPC 0 Power Supply 1"}],
                                "class": [{"data": "Power"}],
                                "status": [{"data": "OK"}],
                            },
                        ],
                    }
                ]
            },
        ),
    ],
)
def test_clear_json(x: str, expected: str):
    profile = loader.get_profile("Juniper.JUNOS")

    r = profile.clear_json(profile, x)
    assert r == expected
