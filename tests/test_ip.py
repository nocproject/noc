# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# noc.core.ip tests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.ip import IP, IPv4, IPv6, PrefixDB


def test_ip_prefix():
    assert repr(IP.prefix("192.168.0.1")) == "<IPv4 192.168.0.1/32>"
    assert repr(IP.prefix("::/0")), "<IPv6 ::/0>"
    assert repr(IP.prefix("2001:db8::/32")) == "<IPv6 2001:db8::/32>"
    assert repr(IP.prefix("::ffff:192.168.0.1")) == "<IPv6 ::ffff:192.168.0.1/128>"


def test_ip_afi():
    assert IP.get_afi("192.168.0.0/24") == "4"
    assert IP.get_afi("::1/128") == "6"


def test_ipv4_in():
    assert "192.168.0.0/24" in IPv4("192.168.0.0/24")
    assert IPv4("192.168.0.0/24") in IPv4("192.168.0.0/24")
    assert "192.168.1.1" not in IPv4("192.168.0.0/24")
    assert IPv4("192.168.1.1") not in IPv4("192.168.0.0/24")
    with pytest.raises(ValueError):
        "::1" in IPv4("192.168.0.0/24")


def test_ipv4_str():
    # Fully qualified
    assert str(IPv4("192.168.0.0/24")) == "192.168.0.0/24"
    # Address only
    assert str(IPv4("192.168.0.0")) == "192.168.0.0/32"


def test_ipv4_unicode():
    # Fully qualified
    assert unicode(IPv4("192.168.0.0/24")), u"192.168.0.0/24"
    # Address only
    assert unicode(IPv4("192.168.0.0")), u"192.168.0.0/32"
    # Netmask
    assert unicode(IPv4("192.168.0.0", netmask="255.255.255.0")) == u"192.168.0.0/24"


def test_ipv4_repr():
    assert repr(IPv4("192.168.0.0/24")) == "<IPv4 192.168.0.0/24>"


def test_ipv4_len():
    assert len(IPv4("192.168.0.0/24")) == 24
    assert len(IPv4("192.168.0.0")) == 32
    assert len(IPv4("0.0.0.0/0")) == 0


@pytest.fixture(
    params=[
        #    Prefix1          Prefix2      cmp    =     !=      <     <=     >     >=
        ("192.168.0.0/24", "192.168.0.0/24", 0, True, False, False, True, False, True),
        ("192.168.0.0/24", "192.168.1.0/24", -1, False, True, True, True, False, False),
        ("192.168.1.0/24", "192.168.0.0/24", 1, False, True, False, False, True, True),
        ("192.168.0.0/24", "192.168.0.0/25", -1, False, True, True, True, False, False),
        ("0.0.0.0/0", "192.168.0.0/24", -1, False, True, True, True, False, False),
        ("0.0.0.0/0", "0.0.0.0/1", -1, False, True, True, True, False, False),
    ]
)
def ipv4_comparison(request):
    return request.param


def test_ipv4_comparison(ipv4_comparison):
    p1, p2, c, eq, ne, lt, le, gt, ge = ipv4_comparison
    p1 = IPv4(p1)
    p2 = IPv4(p2)
    assert cmp(p1, p2) is c
    assert (p1 == p2) is eq
    assert (p1 != p2) is ne
    assert (p1 < p2) is lt
    assert (p1 > p2) is gt
    assert (p1 <= p2) is le
    assert (p1 >= p2) is ge


def test_ipv4_hash():
    p0 = IPv4("192.168.0.1")
    p1 = IPv4("192.168.0.2")
    s = {p0}
    assert p0 in s
    assert p1 not in s
    ss = {p0: 1}
    assert ss[p0] == 1
    with pytest.raises(KeyError):
        ss[p1]


def test_ipv4_add():
    assert repr(IPv4("0.0.0.0/32") + 1) == "<IPv4 0.0.0.1/32>"
    assert repr(IPv4("192.168.0.0/32") + 257) == "<IPv4 192.168.1.1/32>"
    assert repr(IPv4("255.255.255.255/32") + 2) == "<IPv4 0.0.0.1/32>"


def test_ipv4_sub():
    # prefix - number returns prefix
    assert repr(IPv4("192.168.0.10/32") - 9) == "<IPv4 192.168.0.1/32>"
    assert repr(IPv4("192.168.1.10/32") - 265) == "<IPv4 192.168.0.1/32>"
    assert repr(IPv4("0.0.0.0/32") - 1) == "<IPv4 255.255.255.255/32>"
    # prefix - prefix returns distance
    assert IPv4("192.168.0.10/32") - IPv4("192.168.0.1/32") == 9


def test_ipv4_iter_bits():
    assert list(IPv4("0.0.0.0/8").iter_bits()) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert list(IPv4("10.0.0.0/8").iter_bits()) == [0, 0, 0, 0, 1, 0, 1, 0]
    assert list(IPv4("224.0.0.0/4").iter_bits()) == [1, 1, 1, 0]
    assert list(IPv4("255.255.255.255").iter_bits()) == [1] * 32


def test_ipv4_from_bits():
    assert repr(IPv4.from_bits([1, 1, 1, 1, 1, 1, 1, 1])) == "<IPv4 255.0.0.0/8>"
    assert repr(IPv4.from_bits([0, 0, 0, 0, 1, 0, 1, 0])) == "<IPv4 10.0.0.0/8>"


@pytest.fixture(params=["192.168.0.1", "224.0.0.0/4", "192.168.0.0/16", "255.255.255.255"])
def ipv4_bits(request):
    return request.param


def test_ipv4_from_to_bits(ipv4_bits):
    p = IPv4(ipv4_bits)
    assert IPv4.from_bits(p.iter_bits()) == p


def test_ipv4_iter_cover():
    assert [repr(x) for x in IPv4("192.168.0.0/24").iter_cover(23)] == []
    assert [repr(x) for x in IPv4("192.168.0.0/24").iter_cover(24)] == ["<IPv4 192.168.0.0/24>"]
    assert [repr(x) for x in IPv4("192.168.0.0/23").iter_cover(24)] == [
        "<IPv4 192.168.0.0/24>", "<IPv4 192.168.1.0/24>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.0/22").iter_cover(24)] == [
        "<IPv4 192.168.0.0/24>", "<IPv4 192.168.1.0/24>", "<IPv4 192.168.2.0/24>",
        "<IPv4 192.168.3.0/24>"
    ]


def test_ipv4_iter_free():
    assert [
        repr(x) for x in IPv4("192.168.0.0/22")
        .iter_free(["192.168.0.0/27", "192.168.1.0/24", "192.168.2.0/24"])
    ] == [
        "<IPv4 192.168.0.32/27>", "<IPv4 192.168.0.64/26>", "<IPv4 192.168.0.128/25>",
        "<IPv4 192.168.3.0/24>"
    ]
    assert [
        repr(x) for x in IPv4("192.168.0.0/24").iter_free(["192.168.0.0/25", "192.168.0.128/25"])
    ] == []
    assert [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.0.0/24"])] == [
        "<IPv4 192.168.1.0/24>", "<IPv4 192.168.2.0/23>", "<IPv4 192.168.4.0/22>",
        "<IPv4 192.168.8.0/21>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.15.0/24"])] == [
        "<IPv4 192.168.0.0/21>", "<IPv4 192.168.8.0/22>", "<IPv4 192.168.12.0/23>",
        "<IPv4 192.168.14.0/24>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.8.0/24"])] == [
        "<IPv4 192.168.0.0/21>", "<IPv4 192.168.9.0/24>", "<IPv4 192.168.10.0/23>",
        "<IPv4 192.168.12.0/22>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/23"])] == [
        "<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"
    ]
    assert [
        repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/24", "192.168.7.0/24"])
    ] == ["<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"]
    assert [
        repr(x) for x in IPv4("192.168.0.0/20")
        .iter_free(["192.168.0.0/24", "192.168.6.0/24", "192.168.7.0/24", "192.168.15.0/24"])
    ] == [
        "<IPv4 192.168.1.0/24>", "<IPv4 192.168.2.0/23>", "<IPv4 192.168.4.0/23>",
        "<IPv4 192.168.8.0/22>", "<IPv4 192.168.12.0/23>", "<IPv4 192.168.14.0/24>"
    ]
    assert [
        repr(x) for x in IPv4("192.168.0.0/22")
        .iter_free(["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"])
    ] == []
    assert [repr(x) for x in IPv4("192.168.0.0/24").iter_free([])] == ["<IPv4 192.168.0.0/24>"]


def test_ipv4_iter_address():
    assert [repr(x) for x in IPv4("192.168.0.0").iter_address(count=5)] == [
        "<IPv4 192.168.0.0/32>", "<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>",
        "<IPv4 192.168.0.3/32>", "<IPv4 192.168.0.4/32>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.255").iter_address(count=5)] == [
        "<IPv4 192.168.0.255/32>", "<IPv4 192.168.1.0/32>", "<IPv4 192.168.1.1/32>",
        "<IPv4 192.168.1.2/32>", "<IPv4 192.168.1.3/32>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.255").iter_address(until="192.168.1.3")] == [
        "<IPv4 192.168.0.255/32>", "<IPv4 192.168.1.0/32>", "<IPv4 192.168.1.1/32>",
        "<IPv4 192.168.1.2/32>", "<IPv4 192.168.1.3/32>"
    ]


def test_ipv4_size():
    assert IPv4("0.0.0.0/0").size == 4294967296
    assert IPv4("10.0.0.0/8").size == 16777216
    assert IPv4("192.168.0.0/16").size == 65536
    assert IPv4("0.0.0.0").size == 1


def test_ipv4_contains():
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/24")) is True
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/25")) is True
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0")) is True
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.127")) is True
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.255")) is True
    assert IPv4("192.168.0.0/24").contains(IPv4("192.167.255.255")) is False
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.1.0")) is False
    assert IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/16")) is False


def test_ipv4_first():
    assert repr(IPv4("192.168.0.5/24").first) == "<IPv4 192.168.0.0/24>"


def test_ipv4_last():
    assert repr(IPv4("192.168.0.5/24").last) == "<IPv4 192.168.0.255/24>"


def test_ipv4_area_spot():
    assert [repr(x) for x in IPv4("192.168.0.0/24").area_spot([], dist=2)] == []
    assert [repr(x) for x in IPv4("192.168.0.0/24").area_spot([], dist=2, sep=True)] == []
    assert [repr(x) for x in IPv4("192.168.0.0/30").area_spot(["192.168.0.1"], dist=16, sep=True)
            ] == ["<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>"]
    assert [
        repr(x) for x in IPv4("192.168.0.0/24")
        .area_spot(["192.168.0.1", "192.168.0.2", "192.168.0.128"], dist=2)
    ] == [
        "<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>", "<IPv4 192.168.0.3/32>",
        "<IPv4 192.168.0.4/32>", "<IPv4 192.168.0.126/32>", "<IPv4 192.168.0.127/32>",
        "<IPv4 192.168.0.128/32>", "<IPv4 192.168.0.129/32>", "<IPv4 192.168.0.130/32>"
    ]
    assert [
        repr(x) for x in IPv4("192.168.0.0/24")
        .area_spot(["192.168.0.1", "192.168.0.2", "192.168.0.128"], dist=2, sep=True)
    ] == [
        "<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>", "<IPv4 192.168.0.3/32>",
        "<IPv4 192.168.0.4/32>", "None", "<IPv4 192.168.0.126/32>", "<IPv4 192.168.0.127/32>",
        "<IPv4 192.168.0.128/32>", "<IPv4 192.168.0.129/32>", "<IPv4 192.168.0.130/32>"
    ]
    assert [
        repr(x) for x in IPv4("192.168.0.0/24")
        .area_spot(["192.168.0.1", "192.168.0.254"], dist=2, sep=True)
    ] == [
        "<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>", "<IPv4 192.168.0.3/32>", "None",
        "<IPv4 192.168.0.252/32>", "<IPv4 192.168.0.253/32>", "<IPv4 192.168.0.254/32>"
    ]
    assert [repr(x) for x in IPv4("192.168.0.0/31")
            .area_spot(["192.168.0.1"], dist=2, sep=True)] == ["<IPv4 192.168.0.1/32>"]


def test_ipv4_normalized():
    assert repr(IPv4("192.168.0.1/24").normalized) == "<IPv4 192.168.0.0/24>"
    assert repr(IPv4("239.12.5.15/4").normalized) == "<IPv4 224.0.0.0/4>"


def test_ipv4_set_mask():
    assert repr(IPv4("192.168.0.5/24").set_mask()) == "<IPv4 192.168.0.5/32>"
    assert repr(IPv4("192.168.0.5/24").set_mask(25)) == "<IPv4 192.168.0.5/25>"


def test_ipv4_netmask():
    assert repr(IPv4("192.168.0.0/24").netmask) == "<IPv4 255.255.255.0/32>"
    assert repr(IPv4("192.168.0.0/30").netmask) == "<IPv4 255.255.255.252/32>"


def test_ipv4_wildcard():
    assert repr(IPv4("192.168.0.0/24").wildcard) == "<IPv4 0.0.0.255/32>"
    assert repr(IPv4("192.168.0.0/30").wildcard) == "<IPv4 0.0.0.3/32>"


@pytest.fixture(
    params=[
        ("192.168.0.0/24", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.0/24"),
        ("192.168.0.0/25", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.0/25"),
        ("192.168.0.128/25", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.128/25"),
        ("192.168.0.130/32", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.130/32"),
        ("192.168.0.130/32", "192.168.0.128/25", "192.168.1.0/24", "192.168.1.2/32"),
    ]
)
def ipv4_rebase(request):
    return request.param


def test_ipv4_rebase(ipv4_rebase):
    # prefix, base, new base, result
    p, b, nb, r = ipv4_rebase
    assert IPv4(p).rebase(IPv4(b), IPv4(nb)) == IPv4(r)


@pytest.fixture(
    params=[("0.0.0.0", 0), ("255.0.0.0", 8), ("255.255.0.0", 16), ("255.255.255.0", 24),
            ("255.255.255.255", 32), ("128.0.0.0", 1), ("255.255.192.0", 18)]
)
def ipv4_netmask_len(request):
    return request.param


def test_ipv4_netmask_to_len(ipv4_netmask_len):
    m, b = ipv4_netmask_len
    assert IPv4.netmask_to_len(m) == b


def test_ipv6_str():
    # Fully qualified
    assert str(IPv6("::/0")), "::/0"
    assert str(IPv6("2001:db8::/32")) == "2001:db8::/32"
    assert str(IPv6("::ffff:192.168.0.1")) == "::ffff:192.168.0.1/128"
    # Address only
    assert str(IPv6("::")) == "::/128"


def test_ipv4_range_to_prefixes():
    assert [repr(x) for x in IPv4.range_to_prefixes('192.168.0.2', '192.168.0.2')] == [
        "<IPv4 192.168.0.2/32>"
    ]
    assert [repr(x) for x in IPv4.range_to_prefixes('192.168.0.2', '192.168.0.16')] == [
        "<IPv4 192.168.0.2/31>", "<IPv4 192.168.0.4/30>", "<IPv4 192.168.0.8/29>",
        "<IPv4 192.168.0.16/32>"
    ]
    assert [repr(x)
            for x in IPv4.range_to_prefixes('0.0.0.0', '255.255.255.255')] == ["<IPv4 0.0.0.0/0>"]


def test_ipv6_unicode():
    # Fully qualified
    assert unicode(IPv6("::/0")) == u"::/0"
    assert unicode(IPv6("2001:db8::/32")) == u"2001:db8::/32"
    assert unicode(IPv6("::ffff:192.168.0.1")) == u"::ffff:192.168.0.1/128"
    # Address only
    assert unicode(IPv6("::")) == u"::/128"


def test_ipv6_repr():
    assert repr(IPv6("::")) == "<IPv6 ::/128>"


def test_ipv6_len():
    assert len(IPv6("::/0")) == 0
    assert len(IPv6("::")) == 128
    assert len(IPv6("2001:db8::/32")) == 32
    assert len(IPv6("::ffff:19.168.0.1")) == 128


@pytest.fixture(
    params=[
        #    Prefix1     Prefix2 cmp    =     !=      <     <=     >     >=
        ("100::/16", "100::/16", 0, True, False, False, True, False, True),
        ("100::/16", "200::/16", -1, False, True, True, True, False, False),
        ("200::/16", "100::/16", 1, False, True, False, False, True, True),
        ("100::/16", "100::/32", -1, False, True, True, True, False, False),
        ("::/0", "100::/16", -1, False, True, True, True, False, False),
        ("::/0", "::/1", -1, False, True, True, True, False, False),
        ("100:200:300:400::/64", "100:200:300:200::/64", 1, False, True, False, False, True, True),
        ("100:200:300:200::/64", "100:200:300:400::/64", -1, False, True, True, True, False, False),
        ("::100:200:300:400/64", "::100:200:300:200/64", 1, False, True, False, False, True, True),
        ("::100:200:300:200/64", "::100:200:300:400/64", -1, False, True, True, True, False, False),
        ("::100:200:300:400/64", "::100:100:300:400/64", 1, False, True, False, False, True, True),
        ("::100:100:300:400/64", "::100:200:300:400/64", -1, False, True, True, True, False, False),
    ]
)
def ipv6_comparison(request):
    return request.param


def test_ipv6_comparison(ipv6_comparison):
    p1, p2, c, eq, ne, lt, le, gt, ge = ipv6_comparison
    p1 = IPv6(p1)
    p2 = IPv6(p2)
    assert cmp(p1, p2) is c
    assert (p1 == p2) is eq
    assert (p1 != p2) is ne
    assert (p1 < p2) is lt
    assert (p1 > p2) is gt
    assert (p1 <= p2) is le
    assert (p1 >= p2) is ge


def test_ipv6_hash():
    p0 = IPv6("::1")
    p1 = IPv6("::2")
    s = {p0}
    assert p0 in s
    assert p1 not in s
    ss = {p0: 1}
    assert ss[p0] == 1
    with pytest.raises(KeyError):
        ss[p1]


def test_ipv6_add():
    assert repr(IPv6("::/128") + 1) == "<IPv6 ::1/128>"
    assert repr(IPv6("::/128") + 0xffffffff) == "<IPv6 ::ffff:ffff/128>"
    assert repr(IPv6("::1/128") + 0xffffffff) == "<IPv6 ::1:0:0/128>"
    assert repr(IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff") + 2) == "<IPv6 ::1/128>"


def test_ipv6_sub():
    # prefix - number returns prefix
    assert repr(IPv6("100::5") - 3) == "<IPv6 100::2/128>"
    assert repr(IPv6("100::5") - 5) == "<IPv6 100::/128>"
    assert repr(IPv6("100::5") - 6) == "<IPv6 ff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128>"
    # prefix - prefix returns distance
    assert IPv6("100::7") - IPv6("100::5") == 2


def test_ipv6_iter_bits():
    assert list(IPv6("::/16").iter_bits()) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert list(IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff").iter_bits()) == [1] * 128
    assert list(IPv6("f000::/4").iter_bits()) == [1, 1, 1, 1]


def test_ipv6_from_bits():
    assert repr(IPv6.from_bits([1, 1, 1, 1, 1, 1, 1, 1])) == "<IPv6 ff00::/8>"
    assert repr(IPv6.from_bits([1, 1, 1, 1, 1, 1, 1, 1, 1])) == "<IPv6 ff80::/9>"


@pytest.fixture(params=["::", "::ffff:192.168.0.1", "2001:db8::/32", "100::1"])
def ipv6_bits(request):
    return request.param


def test_ipv6_from_to_bits(ipv6_bits):
    p = IPv6(ipv6_bits)
    assert IPv6.from_bits(p.iter_bits()) == p


def test_ipv6_iter_free():
    assert [repr(x) for x in IPv6("2001:db8::/32").iter_free([])] == ["<IPv6 2001:db8::/32>"]
    assert [repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8::/34"])] == [
        "<IPv6 2001:db8:4000::/34>", "<IPv6 2001:db8:8000::/33>"
    ]
    assert [repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8:4000::/34"])] == [
        "<IPv6 2001:db8::/34>", "<IPv6 2001:db8:8000::/33>"
    ]


def test_ipv6_iter_address():
    assert [repr(x) for x in IPv6("2001:db8::").iter_address(count=5)] == [
        "<IPv6 2001:db8::/128>", "<IPv6 2001:db8::1/128>", "<IPv6 2001:db8::2/128>",
        "<IPv6 2001:db8::3/128>", "<IPv6 2001:db8::4/128>"
    ]
    assert [repr(x) for x in IPv6("2001:db8::ffff").iter_address(count=5)] == [
        "<IPv6 2001:db8::ffff/128>", "<IPv6 2001:db8::1:0/128>", "<IPv6 2001:db8::1:1/128>",
        "<IPv6 2001:db8::1:2/128>", "<IPv6 2001:db8::1:3/128>"
    ]
    assert [repr(x) for x in IPv6("2001:db8::ffff").iter_address(until="2001:db8::1:3")] == [
        "<IPv6 2001:db8::ffff/128>", "<IPv6 2001:db8::1:0/128>", "<IPv6 2001:db8::1:1/128>",
        "<IPv6 2001:db8::1:2/128>", "<IPv6 2001:db8::1:3/128>"
    ]


def test_ipv6_contains():
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db8::/32")) is True
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db8::/64")) is True
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db8::")) is True
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db8:0:ffff:ffff:ffff:ffff:ffff")) is True
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db8:ffff:ffff:ffff:ffff:ffff:ffff")) is True
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db7:ffff:ffff:ffff:ffff:ffff:ffff")) is False
    assert IPv6("2001:db8::/32").contains(IPv6("2001:db9::")) is False


def test_ipv6_area_spot():
    assert [
        repr(x) for x in IPv6("2001:db8::/32").area_spot(["2001:db8::1", "2001:db8::a"], dist=2)
    ] == [
        "<IPv6 2001:db8::/128>", "<IPv6 2001:db8::1/128>", "<IPv6 2001:db8::2/128>",
        "<IPv6 2001:db8::3/128>", "<IPv6 2001:db8::8/128>", "<IPv6 2001:db8::9/128>",
        "<IPv6 2001:db8::a/128>", "<IPv6 2001:db8::b/128>", "<IPv6 2001:db8::c/128>"
    ]


def test_ipv6_first():
    assert repr(IPv6("2001:db8::10/32").first) == "<IPv6 2001:db8::/32>"


def test_ipv6_last():
    assert repr(IPv6("2001:db8::10/32").last) == "<IPv6 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff/32>"


def test_ipv6_normalized():
    assert repr(IPv6("0:00:0:0:0::1").normalized) == "<IPv6 ::1/128>"
    assert repr(IPv6("2001:db8:0:7:0:0:0:1").normalized) == "<IPv6 2001:db8:0:7::1/128>"
    assert repr(IPv6("::ffff:c0a8:1").normalized) == "<IPv6 ::ffff:192.168.0.1/128>"


def test_ipv6_set_mask():
    assert repr(IPv6("2001:db8::20/48").set_mask()) == "<IPv6 2001:db8::20/128>"
    assert repr(IPv6("2001:db8::20/48").set_mask(64)) == "<IPv6 2001:db8::20/64>"


def test_ipv6_ptr():
    assert IPv6("2001:db8::1"
                ).ptr(0) == "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2"
    assert IPv6("2001:db8::1").ptr(8) == "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"


def test_ipv6_digits():
    assert IPv6("2001:db8::1").digits == [
        "2", "0", "0", "1", "0", "d", "b", "8", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1"
    ]


@pytest.fixture(
    params=[
        # prefix, base, new base, result
        ("2001:db8::7/128", "2001:db8::/32", "2001:db9::/32", "2001:db9::7/128"),
    ]
)
def ipv6_rebase(request):
    return request.param


def test_ipv6_rebase(ipv6_rebase):
    p, b, nb, r = ipv6_rebase
    assert IPv6(p).rebase(IPv6(b), IPv6(nb)) == IPv6(r)


def test_prefixdb_ipv4():
    db = PrefixDB()
    db[IPv4("192.168.0.0/24")] = 1
    db[IPv4("192.168.1.0/24")] = 2
    db[IPv4("192.168.2.0/24")] = 3
    db[IPv4("10.0.0.0/8")] = 4
    assert db[IPv4("192.168.0.0/24")] == 1
    assert db[IPv4("192.168.1.0/24")] == 2
    assert db[IPv4("192.168.2.0/24")] == 3
    assert db[IPv4("10.0.0.0/8")] == 4
    with pytest.raises(KeyError):
        db[IPv4("172.16.0.0/12")]


def test_prefixdb_ipv6():
    db = PrefixDB()
    db[IPv6("2001:db8:100::/48")] = 1
    db[IPv6("2001:db8:200::/48")] = 2
    db[IPv6("2001:db8:300::/48")] = 3
    db[IPv6("2001:db8:400::/48")] = 4
    assert db[IPv6("2001:db8:100::/48")] == 1
    assert db[IPv6("2001:db8:200::/48")] == 2
    assert db[IPv6("2001:db8:300::/48")] == 3
    assert db[IPv6("2001:db8:400::/48")] == 4
    with pytest.raises(KeyError):
        db[IPv6("::/128")]
