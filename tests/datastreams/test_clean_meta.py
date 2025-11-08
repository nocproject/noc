# ----------------------------------------------------------------------
# noc.core.datastream.base.clean_meta tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.datastream.base import DataStream


@pytest.mark.parametrize(
    ("meta", "current_meta", "expected"),
    [
        (
            {
                "client_groups": [],
                "pool": "default",
                "service_groups": ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"],
            },
            {"pool": "default", "service_groups": [], "client_groups": []},
            {
                "client_groups": [],
                "pool": ["default"],
                "service_groups": [["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"]],
            },
        ),
        (
            {
                "client_groups": [],
                "pool": "default2",
                "service_groups": ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"],
            },
            {"pool": ["default"], "service_groups": [], "client_groups": []},
            {
                "client_groups": [],
                "pool": ["default2", "default"],
                "service_groups": [["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"]],
            },
        ),
        (
            {"client_groups": [], "pool": "default2", "service_groups": []},
            {
                "pool": ["default"],
                "service_groups": ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"],
                "client_groups": [],
            },
            {
                "client_groups": [],
                "pool": ["default2", "default"],
                "service_groups": [[], ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"]],
            },
        ),
        (
            {"client_groups": [], "pool": "default2", "service_groups": []},
            {
                "pool": ["default"],
                "service_groups": [[], ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"]],
                "client_groups": [],
            },
            {
                "client_groups": [],
                "pool": ["default2", "default"],
                "service_groups": [[], ["6128a1bbda3903fa14f1b4eb", "6128a1bbda3903fa14f1b538"]],
            },
        ),
        (
            {"pool": "default", "service_groups": [], "client_groups": []},
            {},
            {"pool": ["default"], "service_groups": [], "client_groups": []},
        ),
    ],
)
def test_ds_clean_meta(meta, current_meta, expected):
    assert DataStream.clean_meta(meta, current_meta) == expected


@pytest.mark.parametrize(
    ("meta", "meta_filter", "expected"),
    [
        (
            {"servers": [["ns1.example.com", "ns2.example.com"]]},
            {"meta.servers": {"$elemMatch": {"$elemMatch": {"$in": ["ns1.example.com"]}}}},
            False,
        ),
        (
            {
                "servers": [
                    ["ns3.example.com", "ns2.example.com"],
                    ["ns1.example.com", "ns2.example.com"],
                ]
            },
            {"meta.servers": {"$elemMatch": {"$elemMatch": {"$in": ["ns1.example.com"]}}}},
            True,
        ),
        (
            {"pool": ["POOL1", "POOL2"]},
            {"meta.pool": "POOL2"},
            True,
        ),
        (
            {"pool": ["POOL1", "POOL2"]},
            {"meta.pool": "POOL1"},
            False,
        ),
    ],
)
def test_ds_is_moved(meta, meta_filter, expected):
    assert DataStream.is_moved(meta, meta_filter) == expected
