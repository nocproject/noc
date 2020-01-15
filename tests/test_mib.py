# -*- coding: utf-8 -*-
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
