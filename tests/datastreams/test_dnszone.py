# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dnszone datastream test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.services.datastream.streams.dnszone import DNSZoneDataStream


def find_record(records, name, type, content):
    for r in records:
        if r.get("name") == name and r.get("type") == type and r.get("rdata") == content:
            return True
    return False


@pytest.mark.parametrize("zone_id,records", [
    (10, [
        ("ns1", "A", "10.0.0.1"),
        ("ns2", "A", "10.0.0.2"),
        ("z12", "NS", "ns1.example.com."),
        ("z12", "NS", "ns2.example.com."),
        ("z21", "NS", "ns1.example.com."),
        ("z21", "NS", "ns2.example.com."),
        ("z31", "NS", "ns1.example.com.")
    ]),
    (14, [
        ("8", "CNAME", "8.8/29"),
        ("9", "CNAME", "9.8/29"),
        ("10", "CNAME", "10.8/29"),
        ("11", "CNAME", "11.8/29"),
        ("12", "CNAME", "12.8/29"),
        ("13", "CNAME", "13.8/29"),
        ("14", "CNAME", "14.8/29"),
        ("15", "CNAME", "15.8/29"),
        ("8/29", "NS", "ns3.example.com")
    ])
])
def test_data(zone_id, records):
    data = DNSZoneDataStream().get_object(zone_id)
    assert data
    assert data.get("name")
    assert data.get("serial")
    assert data.get("records")
    assert data["records"][0]["type"] == "SOA"
    for name, type, content in records:
        assert find_record(data["records"], name, type, content)
