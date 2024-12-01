# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.mib import mib
from noc.core.snmp.render import render_mac
from noc.fm.models.mib import MIB


@pytest.mark.parametrize(
    "input,expected",
    [
        ("IF-MIB", "if_mib"),
        ("RFC1213-MIB", "rfc1213_mib"),
        ("CISCO-VLAN-MEMBERSHIP-MIB", "cisco-vlan-membership-mib"),
    ],
)
def test_mib_to_modname(input, expected):
    assert mib.mib_to_modname(expected)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("IF-MIB::ifName", "1.3.6.1.2.1.31.1.1.1.1"),
        (("IF-MIB::ifName", 0), "1.3.6.1.2.1.31.1.1.1.1.0"),
        (("SNMPv2-MIB::sysDescr", 0), "1.3.6.1.2.1.1.1.0"),
    ],
)
def test_mib_lookup(input, expected):
    assert mib[input] == expected


@pytest.mark.parametrize(
    "name", [x for x in os.listdir("cmibs") if x.endswith(".py") and not x.startswith("_")]
)
def test_compiled_mib(name):
    mod_name = name[:-3]
    mn = "noc.cmibs.%s" % mod_name
    m = __import__(mn, {}, {}, "*")
    assert hasattr(m, "NAME")
    assert mib.mib_to_modname(m.NAME) == mod_name
    assert hasattr(m, "MIB")
    assert isinstance(m.MIB, dict)
    assert m.MIB


@pytest.fixture
def clean_mib():
    mib.reset()
    yield mib
    mib.reset()


@pytest.mark.parametrize("name", ["IF-MIB::ifDescr", "SNMPv2-MIB::sysObjectID"])
def test_mib_loading(clean_mib, name):
    mib = clean_mib
    mib_name = name.split("::", 1)[0]
    # Check MIB is missed
    assert not mib.is_loaded(mib_name)
    # Load mib
    mib.load_mib(mib_name)
    assert mib.is_loaded(mib_name)
    # Fetch control value
    assert mib[name]


@pytest.mark.parametrize(
    "name,oid",
    [
        ("IF-MIB::ifName", "1.3.6.1.2.1.31.1.1.1.1"),
        (("IF-MIB::ifName", 0), "1.3.6.1.2.1.31.1.1.1.1.0"),
        (("SNMPv2-MIB::sysDescr", 0), "1.3.6.1.2.1.1.1.0"),
    ],
)
def test_implicit_mib_loading(clean_mib, name, oid):
    # Check cache is clean
    if isinstance(name, tuple):
        mib_name = name[0].split("::", 1)[0]
    else:
        mib_name = name.split("::", 1)[0]
    assert not mib.is_loaded(mib_name)
    # Implicit load
    assert mib[name] == oid
    assert mib.is_loaded(mib_name)
    # Cached
    assert mib[name] == oid


@pytest.mark.parametrize(
    "name", ["IF-MIBX::WUT", ("IF-MIBX::WUT", 10), "IF-MIB::WUT", ("IF-MIB::WUT", 10)]
)
def test_invalid_name(clean_mib, name):
    mib = clean_mib
    with pytest.raises(KeyError):
        assert mib[name]


@pytest.mark.parametrize(
    "mib_name,oid,value,display_hints,expected",
    [
        ("IF-MIB", "1.3.6.1.2.1.2.2.1.2.1", b"description", None, "description"),
        (
            "IF-MIB",
            "1.3.6.1.2.1.2.2.1.6.3",
            b"\x00\x01\x02\x03\x04\x05\x06",
            None,
            "00:01:02:03:04:05:06",
        ),
        (
            "IF-MIB",
            "1.3.6.1.2.1.2.2.1.6.3",
            b"\x00\x01\x02\x03\x04\x0a\x0b",
            None,
            "00:01:02:03:04:0a:0b",
        ),
        (
            "IF-MIB",
            "1.3.6.1.2.1.2.2.1.6.3",
            b"\x00\x01\x02\x03\x04\x0a\x0b",
            {"1.3.6.1.2.1.2.2.1.5": render_mac},  # Must be skipped
            "00:01:02:03:04:0a:0b",
        ),
        (
            "IF-MIB",
            "1.3.6.1.2.1.2.2.1.6.3",
            b"\x00\x01\x02\x03\x04\x0a\x0b",  # Length mismatch
            {"1.3.6.1.2.1.2.2.1.6": render_mac},
            "",
        ),
        (
            "IF-MIB",
            "1.3.6.1.2.1.2.2.1.6.3",
            b"\x01\x02\x03\x04\x0a\x0b",  # Length mismatch
            {"1.3.6.1.2.1.2.2.1.6": render_mac},
            "01:02:03:04:0A:0B",
        ),
        (
            "LLDP-MIB",
            "1.0.8802.1.1.2.1.4.1.1.5.0.59.3",
            b"\x01\x02\x03\x04\x05\x06",
            {"1.0.8802.1.1.2.1.4.1.1.5": render_mac},
            "01:02:03:04:05:06",
        ),
        (
            "CISCO-MAC-NOTIFICATION-MIB",
            "1.3.6.1.4.1.9.9.215.1.1.8.1.2",
            b"\x02\x05$\xae 7F`\xdb\x00\x04",
            {},
            "\x02\x05$® 7F`Û\x00\x04",
        ),
    ],
)
def test_mib_render(clean_mib, mib_name, oid, value, display_hints, expected):
    mib = clean_mib
    mib.load_mib(mib_name)
    assert mib.render(oid, value, display_hints) == expected


@pytest.mark.parametrize(
    "oids,expected",
    [
        (
            {
                "1.3.6.1.2.1.1.3.0": "249778441",
                "1.3.6.1.4.1.9.9.215.1.1.8.1.2": "=02=05$=C2=AE 7F`=C3=9B=00=04",
                "1.3.6.1.6.3.1.1.4.3.0": "1.3.6.1.4.1.9.9.215.2",
            },
            {
                "DISMAN-EVENT-MIB::sysUpTimeInstance": "249778441",
                "CISCO-MAC-NOTIFICATION-MIB::cmnHistMacChangedMsg": "\x02\x05$® 7F`Û\x00\x04",
                "SNMPv2-MIB::snmpTrapEnterprise.0": "CISCO-MAC-NOTIFICATION-MIB::cmnMIBNotificationPrefix",
            },
        )
    ],
)
def test_fm_mib(oids, expected):
    assert MIB.resolve_vars(oids) == expected
