# ----------------------------------------------------------------------
# Run tests over tests/confdb/profiles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Third-party modules
import pytest
from collections import namedtuple

# NOC modules
from noc.core.handler import get_handler


PREFIX = ("tests", "confdb", "profiles")

MOCK1_STACK_DATA = {"stack": {"stackable": True, "member": 1}}

INTERFACES1 = [
    ("GigabitEthernet0/0/1", "physical"),
    ("GigabitEthernet0/0/2", "physical"),
    ("GigabitEthernet0/0/3", "physical"),
    ("GigabitEthernet0/0/4", "physical"),
    ("GigabitEthernet0/0/10", "physical"),
    ("XGigabitEthernet0/1/1", "physical"),
    ("XGigabitEthernet0/1/2", "physical"),
    ("XGigabitEthernet1/0/1", "physical"),
    ("Ethernet0/0/1", "physical"),
    ("M-Ethernet0/0/1", "physical"),
]

PATHS1 = [
    [
        [
            {"object": ("MockObject1", {}), "connection": ("1", "")},
            {"object": ("Connection1", {}), "connection": ("xfp 1", ["TransEth10G"])},
        ],
        "XGigabitEthernet0/1/1",
    ],
    [
        [
            {"object": ("MockObject1", {}), "connection": ("1", "")},
            {
                "object": ("Connection1", {}),
                "connection": ("XGigabitEthernetX/0/1", ["TransEth10G"]),
            },
        ],
        "XGigabitEthernet1/0/1",
    ],
    [
        [
            {"object": ("MockObject1", {}), "connection": ("1", "")},
            {"object": ("Connection1", {}), "connection": ("xfp 2", ["TransEth10G"])},
        ],
        "XGigabitEthernet0/1/2",
    ],
    # [
    #     [{"object": ("MockObject1", {}), "connection": ("MEth0/0/1", ["10BASET", "100BASETX"])}],
    #     "M-Ethernet0/0/1",
    # ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("GigabitEthernet0/0/1", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet0/0/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("GigabitEthernet0/0/2", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet0/0/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("GigabitEthernet0/0/3", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet0/0/3",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("Ethernet0/0/1", ["10BASET", "100BASETX"]),
            }
        ],
        "Ethernet0/0/1",
    ],
]

# Raisecom paths
INTERFACES2 = [
    ("gigaethernet1/1/1", "physical"),
    ("gigaethernet1/1/2", "physical"),
    ("gigaethernet1/1/3", "physical"),
    ("gigaethernet1/1/28", "physical"),
    ("fastethernet1/0/1", "physical"),
]

PATHS2 = [
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1/1/1", ["10BASET", "100BASETX", "1000BASETX"]),
            }
        ],
        "gigaethernet1/1/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1/1/2", ["10BASET", "100BASETX", "1000BASETX"]),
            }
        ],
        "gigaethernet1/1/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1/1/3", ["10BASET", "100BASETX", "1000BASETX"]),
            }
        ],
        "gigaethernet1/1/3",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1/1/28", ["10BASET", "100BASETX", "1000BASETX"]),
            }
        ],
        "gigaethernet1/1/28",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1/0/1", ["10BASET", "100BASETX"]),
            }
        ],
        "fastethernet1/0/1",
    ],
]

# Qtech paths
INTERFACES3 = [
    ("Ethernet1/0/1", "physical"),
    ("Ethernet1/0/2", "physical"),
    ("Ethernet1/0/3", "physical"),
    ("Ethernet1/0/28", "physical"),
]

PATHS3 = [
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("1", ["10BASET", "100BASETX"]),
            }
        ],
        "Ethernet1/0/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("2", ["10BASET", "100BASETX"]),
            }
        ],
        "Ethernet1/0/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("3", ["10BASET", "100BASETX"]),
            }
        ],
        "Ethernet1/0/3",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("sfp28", ["TransEth1G"]),
            }
        ],
        "Ethernet1/0/28",
    ],
]

# Eltex PATH

INTERFACES4 = [
    ("Gi 1/0/1", "physical"),
    ("Gi 1/0/2", "physical"),
    ("Gi 1/0/3", "physical"),
    ("Te 1/0/1", "physical"),
    ("Gi 2/0/1", "physical"),
    ("Gi 2/0/2", "physical"),
    ("Gi 2/0/3", "physical"),
    ("Te 2/0/1", "physical"),
    ("Gi 3/0/1", "physical"),
    ("Gi 3/0/2", "physical"),
    ("Gi 3/0/3", "physical"),
    ("Te 3/0/1", "physical"),
]

PATHS4 = [
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("gigabitethernet 1/0/1", ["TransEth100M", "TransEth1G"]),
            }
        ],
        "Gi 1/0/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("gigabitethernet 1/0/2", ["TransEth100M", "TransEth1G"]),
            }
        ],
        "Gi 1/0/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("gigabitethernet 1/0/3", ["TransEth100M", "TransEth1G"]),
            }
        ],
        "Gi 1/0/3",
    ],
    [
        [
            {
                "object": ("MockObject1", {}),
                "connection": ("tengigabitethernet 1/0/1", ["TransEth10G"]),
            }
        ],
        "Te 1/0/1",
    ],
]

# Stack

INTERFACES5 = [
    ("GigabitEthernet0/0/1", "physical"),
    ("GigabitEthernet0/0/2", "physical"),
    ("GigabitEthernet1/0/1", "physical"),
    ("GigabitEthernet1/0/2", "physical"),
    ("GigabitEthernet2/0/1", "physical"),
    ("GigabitEthernet2/0/2", "physical"),
    ("XGigabitEthernet0/1/1", "physical"),
    ("XGigabitEthernet0/1/2", "physical"),
    ("M-Ethernet0/0/1", "physical"),
]

PATHS5 = [
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "0"}}),
                "connection": ("1", ""),
            },
            {"object": ("Connection1", {}), "connection": ("xfp 1", ["TransEth10G"])},
        ],
        "XGigabitEthernet0/1/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "0"}}),
                "connection": ("1", ""),
            },
            {"object": ("Connection1", {}), "connection": ("xfp 2", ["TransEth10G"])},
        ],
        "XGigabitEthernet0/1/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "0"}}),
                "connection": ("GigabitEthernet0/0/1", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet0/0/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "0"}}),
                "connection": ("GigabitEthernet0/0/2", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet0/0/2",
    ],
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "1"}}),
                "connection": ("GigabitEthernet0/0/1", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet1/0/1",
    ],
    [
        [
            {
                "object": ("MockObject1", {"stack": {"stackable": "true", "member": "1"}}),
                "connection": ("GigabitEthernet0/0/2", ["TransEth1G"]),
            }
        ],
        "GigabitEthernet1/0/2",
    ],
]


PathItem = namedtuple("PathItem", ["object", "connection"])


class MockObject(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def get_data(self, interface, key):
        v = self.data.get(interface, {})
        return v.get(key)


class MockObjectConnection(object):
    def __init__(self, name, protocols):
        self.name = name
        self.protocols = protocols


class MockInterface(object):
    def __init__(self, name, default_name, type):
        self.name = name
        self.default_name = default_name
        self.type = type


@pytest.mark.parametrize(
    ("interfaces", "paths"),
    [
        (INTERFACES1, PATHS1),
        (INTERFACES2, PATHS2),
        (INTERFACES3, PATHS3),
        (INTERFACES4, PATHS4),
        (INTERFACES5, PATHS5),
    ],
)
def test_profile(interfaces, paths):
    ifaces = {}
    for iface_name, iface_type in interfaces:
        ifaces[iface_name] = MockInterface(iface_name, "", iface_type)

    h = get_handler("noc.core.confdb.collator.ifpath.IfPathCollator")
    collator = h()

    for path, result in paths:
        physical_path = [
            PathItem(
                object=MockObject(*p["object"]), connection=MockObjectConnection(*p["connection"])
            )
            for p in path
        ]
        r = collator.collate(physical_path, ifaces)
        assert r == result
