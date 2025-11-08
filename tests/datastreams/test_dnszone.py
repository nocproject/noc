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


@pytest.mark.parametrize(
    ("zone_id", "masters", "slaves", "records"),
    [
        # zone_id, masters, slaves, records
        # example.com
        (
            10,
            ["ns1.example.com", "ns2.example.com"],
            [],
            [
                ("", "NS", "ns1.example.com."),
                ("", "NS", "ns2.example.com."),
                ("h1", "A", "10.0.0.3"),
                ("h2", "A", "10.0.0.4"),
                ("h3", "A", "10.0.1.3"),
                ("h4", "AAAA", "2001:db8::1"),
                ("h5", "AAAA", "2001:db8::2"),
                ("ns1", "A", "10.0.0.1"),
                ("ns2", "A", "10.0.0.2"),
                ("z12", "NS", "ns1.example.com."),
                ("z12", "NS", "ns2.example.com."),
                ("z21", "NS", "ns1.example.com."),
                ("z21", "NS", "ns2.example.com."),
                ("z31", "NS", "ns1.example.com."),
            ],
        ),
        # 0.0.10.in-addr.arpa
        (
            14,
            ["ns1.example.com", "ns2.example.com"],
            [],
            [
                ("", "NS", "ns1.example.com."),
                ("", "NS", "ns2.example.com."),
                ("8/29", "NS", "ns3.example.com."),
                ("8", "CNAME", "8.8/29"),
                ("9", "CNAME", "9.8/29"),
                ("10", "CNAME", "10.8/29"),
                ("11", "CNAME", "11.8/29"),
                ("12", "CNAME", "12.8/29"),
                ("13", "CNAME", "13.8/29"),
                ("14", "CNAME", "14.8/29"),
                ("15", "CNAME", "15.8/29"),
                ("3", "PTR", "h1.example.com."),
                ("4", "PTR", "h2.example.com."),
            ],
        ),
        # 8.b.d.0.1.0.0.2.ip6.int
        (
            16,
            ["ns1.example.com", "ns2.example.com"],
            [],
            [
                ("", "NS", "ns1.example.com."),
                ("", "NS", "ns2.example.com."),
                ("1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0", "PTR", "h4.example.com."),
                ("2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0", "PTR", "h5.example.com."),
            ],
        ),
    ],
)
def test_data(zone_id, masters, slaves, records):
    data = DNSZoneDataStream().get_object(zone_id)
    assert data
    assert data.get("name")
    assert data.get("serial")
    # Test masters
    if masters:
        assert "masters" in data
        assert data["masters"] == masters
    # Test slaves
    if slaves:
        assert "slaves" in data
        assert data["slaves"] == masters
    # Test records
    assert data.get("records")
    assert data["records"][0]["type"] == "SOA"
    for name, type, content in records:
        assert find_record(data["records"], name, type, content), (
            "%s (%s) is expected but missed" % (name, type)
        )
    # Test meta
    meta = DNSZoneDataStream().get_meta(data)
    assert meta
    assert "servers" in meta
    assert meta["servers"] == masters + slaves


def test_filter_server():
    q = DNSZoneDataStream.filter_server("ns1.example.com")
    assert q
    assert "meta.servers" in q
    assert q["meta.servers"] == {"$elemMatch": {"$elemMatch": {"$in": ["ns1.example.com"]}}}
