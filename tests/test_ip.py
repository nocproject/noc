# ---------------------------------------------------------------------
# noc.core.ip tests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.ip import IP, IPv4, IPv6, PrefixDB
from noc.core.comp import smart_text


@pytest.mark.parametrize(
    "prefix,result",
    [
        ("192.168.0.1", "<IPv4 192.168.0.1/32>"),
        ("::/0", "<IPv6 ::/0>"),
        ("2001:db8::/32", "<IPv6 2001:db8::/32>"),
        ("::ffff:192.168.0.1", "<IPv6 ::ffff:192.168.0.1/128>"),
    ],
)
def test_ip_prefix(prefix, result):
    assert repr(IP.prefix(prefix)) == result


@pytest.mark.parametrize("prefix,afi", [("192.168.0.0/24", "4"), ("::1/128", "6")])
def test_ip_afi(prefix, afi):
    assert IP.get_afi(prefix) == afi


@pytest.mark.parametrize(
    "p1,p2,result",
    [
        ("192.168.0.0/24", IPv4("192.168.0.0/24"), True),
        (IPv4("192.168.0.0/24"), IPv4("192.168.0.0/24"), True),
        ("192.168.1.1", IPv4("192.168.0.0/24"), False),
        (IPv4("192.168.1.1"), IPv4("192.168.0.0/24"), False),
    ],
)
def test_ipv4_in(p1, p2, result):
    assert (p1 in p2) is result


@pytest.mark.parametrize("p1,p2", [("::1", "192.168.0.0/24")])
def test_ipv4_in_value_error(p1, p2):
    with pytest.raises(ValueError):
        p1 in IPv4(p2)


@pytest.mark.parametrize(
    "p1,p2", [(IPv4("192.168.0.0/24"), "192.168.0.0/24"), (IPv4("192.168.0.0"), "192.168.0.0/32")]
)
def test_ipv4_str(p1, p2):
    assert str(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.0/24"), "192.168.0.0/24"),
        (IPv4("192.168.0.0"), "192.168.0.0/32"),
        (IPv4("192.168.0.0", netmask="255.255.255.0"), "192.168.0.0/24"),
    ],
)
def test_ipv4_unicode(p1, p2):
    assert smart_text(p1) == p2


@pytest.mark.parametrize("p1,p2", [(IPv4("192.168.0.0/24"), "<IPv4 192.168.0.0/24>")])
def test_ipv4_repr(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2", [(IPv4("192.168.0.0/24"), 24), (IPv4("192.168.0.0"), 32), (IPv4("0.0.0.0/0"), 0)]
)
def test_ipv4_len(p1, p2):
    assert len(p1) == p2


@pytest.mark.parametrize(
    "p1, p2, c, eq, ne, lt, le, gt, ge",
    [
        #    Prefix1          Prefix2      cmp    =     !=      <     <=     >     >=
        ("192.168.0.0/24", "192.168.0.0/24", 0, True, False, False, True, False, True),
        ("192.168.0.0/24", "192.168.1.0/24", -1, False, True, True, True, False, False),
        ("192.168.1.0/24", "192.168.0.0/24", 1, False, True, False, False, True, True),
        ("192.168.0.0/24", "192.168.0.0/25", -1, False, True, True, True, False, False),
        ("0.0.0.0/0", "192.168.0.0/24", -1, False, True, True, True, False, False),
        ("0.0.0.0/0", "0.0.0.0/1", -1, False, True, True, True, False, False),
    ],
)
def test_ipv4_comparison(p1, p2, c, eq, ne, lt, le, gt, ge):
    p1 = IPv4(p1)
    p2 = IPv4(p2)
    assert ((p1 > p2) - (p1 < p2)) == c
    assert (p1 == p2) is eq
    assert (p1 != p2) is ne
    assert (p1 < p2) is lt
    assert (p1 > p2) is gt
    assert (p1 <= p2) is le
    assert (p1 >= p2) is ge


@pytest.mark.parametrize("p1,p2", [("192.168.0.1", "192.168.0.2")])
def test_ipv4_hash(p1, p2):
    p1 = IPv4(p1)
    p2 = IPv4(p2)
    s = {p1}
    assert p1 in s
    assert p2 not in s
    ss = {p1: 1}
    assert ss[p1] == 1
    with pytest.raises(KeyError):
        ss[p2]  # pylint: disable=pointless-statement


@pytest.mark.parametrize(
    "p1,p2",
    [
        ((IPv4("0.0.0.0/32") + 1), "<IPv4 0.0.0.1/32>"),
        ((IPv4("192.168.0.0/32") + 257), "<IPv4 192.168.1.1/32>"),
        ((IPv4("255.255.255.255/32") + 2), "<IPv4 0.0.0.1/32>"),
    ],
)
def test_ipv4_add(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (repr(IPv4("192.168.0.10/32") - 9), "<IPv4 192.168.0.1/32>"),
        (repr(IPv4("192.168.1.10/32") - 265), "<IPv4 192.168.0.1/32>"),
        (repr(IPv4("0.0.0.0/32") - 1), "<IPv4 255.255.255.255/32>"),
        (IPv4("192.168.0.10/32") - IPv4("192.168.0.1/32"), 9),
    ],
)
def test_ipv4_sub(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("0.0.0.0/8").iter_bits(), [0, 0, 0, 0, 0, 0, 0, 0]),
        (IPv4("10.0.0.0/8").iter_bits(), [0, 0, 0, 0, 1, 0, 1, 0]),
        (IPv4("224.0.0.0/4").iter_bits(), [1, 1, 1, 0]),
        (IPv4("255.255.255.255").iter_bits(), [1] * 32),
    ],
)
def test_ipv4_iter_bits(p1, p2):
    assert list(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4.from_bits([1, 1, 1, 1, 1, 1, 1, 1]), "<IPv4 255.0.0.0/8>"),
        (IPv4.from_bits([0, 0, 0, 0, 1, 0, 1, 0]), "<IPv4 10.0.0.0/8>"),
    ],
)
def test_ipv4_from_bits(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "prefix", ["192.168.0.1", "224.0.0.0/4", "192.168.0.0/16", "255.255.255.255"]
)
def test_ipv4_from_to_bits(prefix):
    p = IPv4(prefix)
    assert IPv4.from_bits(p.iter_bits()) == p


@pytest.mark.parametrize(
    "p1,p2",
    [
        ([repr(x) for x in IPv4("192.168.0.0/24").iter_cover(23)], []),
        ([repr(x) for x in IPv4("192.168.0.0/24").iter_cover(24)], ["<IPv4 192.168.0.0/24>"]),
        (
            [repr(x) for x in IPv4("192.168.0.0/23").iter_cover(24)],
            ["<IPv4 192.168.0.0/24>", "<IPv4 192.168.1.0/24>"],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.0/22").iter_cover(24)],
            [
                "<IPv4 192.168.0.0/24>",
                "<IPv4 192.168.1.0/24>",
                "<IPv4 192.168.2.0/24>",
                "<IPv4 192.168.3.0/24>",
            ],
        ),
    ],
)
def test_ipv4_iter_cover(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            [
                repr(x)
                for x in IPv4("192.168.0.0/22").iter_free(
                    ["192.168.0.0/27", "192.168.1.0/24", "192.168.2.0/24"]
                )
            ],
            [
                "<IPv4 192.168.0.32/27>",
                "<IPv4 192.168.0.64/26>",
                "<IPv4 192.168.0.128/25>",
                "<IPv4 192.168.3.0/24>",
            ],
        ),
        (
            [
                repr(x)
                for x in IPv4("192.168.0.0/24").iter_free(["192.168.0.0/25", "192.168.0.128/25"])
            ],
            [],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.0.0/24"])],
            [
                "<IPv4 192.168.1.0/24>",
                "<IPv4 192.168.2.0/23>",
                "<IPv4 192.168.4.0/22>",
                "<IPv4 192.168.8.0/21>",
            ],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.15.0/24"])],
            [
                "<IPv4 192.168.0.0/21>",
                "<IPv4 192.168.8.0/22>",
                "<IPv4 192.168.12.0/23>",
                "<IPv4 192.168.14.0/24>",
            ],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.8.0/24"])],
            [
                "<IPv4 192.168.0.0/21>",
                "<IPv4 192.168.9.0/24>",
                "<IPv4 192.168.10.0/23>",
                "<IPv4 192.168.12.0/22>",
            ],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/23"])],
            ["<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"],
        ),
        (
            [
                repr(x)
                for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/24", "192.168.7.0/24"])
            ],
            ["<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"],
        ),
        (
            [
                repr(x)
                for x in IPv4("192.168.0.0/20").iter_free(
                    ["192.168.0.0/24", "192.168.6.0/24", "192.168.7.0/24", "192.168.15.0/24"]
                )
            ],
            [
                "<IPv4 192.168.1.0/24>",
                "<IPv4 192.168.2.0/23>",
                "<IPv4 192.168.4.0/23>",
                "<IPv4 192.168.8.0/22>",
                "<IPv4 192.168.12.0/23>",
                "<IPv4 192.168.14.0/24>",
            ],
        ),
        (
            [
                repr(x)
                for x in IPv4("192.168.0.0/22").iter_free(
                    ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"]
                )
            ],
            [],
        ),
        ([repr(x) for x in IPv4("192.168.0.0/24").iter_free([])], ["<IPv4 192.168.0.0/24>"]),
    ],
)
def test_ipv4_iter_free(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            [repr(x) for x in IPv4("192.168.0.0").iter_address(count=5)],
            [
                "<IPv4 192.168.0.0/32>",
                "<IPv4 192.168.0.1/32>",
                "<IPv4 192.168.0.2/32>",
                "<IPv4 192.168.0.3/32>",
                "<IPv4 192.168.0.4/32>",
            ],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.255").iter_address(count=5)],
            [
                "<IPv4 192.168.0.255/32>",
                "<IPv4 192.168.1.0/32>",
                "<IPv4 192.168.1.1/32>",
                "<IPv4 192.168.1.2/32>",
                "<IPv4 192.168.1.3/32>",
            ],
        ),
        (
            [repr(x) for x in IPv4("192.168.0.255").iter_address(until="192.168.1.3")],
            [
                "<IPv4 192.168.0.255/32>",
                "<IPv4 192.168.1.0/32>",
                "<IPv4 192.168.1.1/32>",
                "<IPv4 192.168.1.2/32>",
                "<IPv4 192.168.1.3/32>",
            ],
        ),
    ],
)
def test_ipv4_iter_address(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        ("0.0.0.0/0", 4294967296),
        ("10.0.0.0/8", 16777216),
        ("192.168.0.0/16", 65536),
        ("0.0.0.0", 1),
    ],
)
def test_ipv4_size(p1, p2):
    assert IPv4(p1).size == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/24")), True),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/25")), True),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0")), True),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.127")), True),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.255")), True),
        (IPv4("192.168.0.0/24").contains(IPv4("192.167.255.255")), False),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.1.0")), False),
        (IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/16")), False),
    ],
)
def test_ipv4_contains(p1, p2):
    assert p1 is p2


@pytest.mark.parametrize("p1,p2", [(IPv4("192.168.0.5/24").first, "<IPv4 192.168.0.0/24>")])
def test_ipv4_first(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize("p1,p2", [(IPv4("192.168.0.5/24").last, "<IPv4 192.168.0.255/24>")])
def test_ipv4_last(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "prefix,addresses,cfg,result",
    [
        ("192.168.0.0/24", [], {"dist": 2}, []),
        ("192.168.0.0/24", [], {"dist": 2, "sep": True}, []),
        (
            "192.168.0.0/30",
            ["192.168.0.1"],
            {"dist": 16, "sep": True},
            ["<IPv4 192.168.0.1/32>", "<IPv4 192.168.0.2/32>"],
        ),
        (
            "192.168.0.0/30",
            ["192.168.0.1"],
            {"dist": 16, "sep": True, "exclude_special": False},
            [
                "<IPv4 192.168.0.0/32>",
                "<IPv4 192.168.0.1/32>",
                "<IPv4 192.168.0.2/32>",
                "<IPv4 192.168.0.3/32>",
            ],
        ),
        (
            "192.168.0.0/24",
            ["192.168.0.1", "192.168.0.2", "192.168.0.128"],
            {"dist": 2},
            [
                "<IPv4 192.168.0.1/32>",
                "<IPv4 192.168.0.2/32>",
                "<IPv4 192.168.0.3/32>",
                "<IPv4 192.168.0.4/32>",
                "<IPv4 192.168.0.126/32>",
                "<IPv4 192.168.0.127/32>",
                "<IPv4 192.168.0.128/32>",
                "<IPv4 192.168.0.129/32>",
                "<IPv4 192.168.0.130/32>",
            ],
        ),
        (
            "192.168.0.0/24",
            ["192.168.0.1", "192.168.0.2", "192.168.0.128"],
            {"dist": 2, "sep": True},
            [
                "<IPv4 192.168.0.1/32>",
                "<IPv4 192.168.0.2/32>",
                "<IPv4 192.168.0.3/32>",
                "<IPv4 192.168.0.4/32>",
                "None",
                "<IPv4 192.168.0.126/32>",
                "<IPv4 192.168.0.127/32>",
                "<IPv4 192.168.0.128/32>",
                "<IPv4 192.168.0.129/32>",
                "<IPv4 192.168.0.130/32>",
            ],
        ),
        (
            "192.168.0.0/24",
            ["192.168.0.1", "192.168.0.254"],
            {"dist": 2, "sep": True},
            [
                "<IPv4 192.168.0.1/32>",
                "<IPv4 192.168.0.2/32>",
                "<IPv4 192.168.0.3/32>",
                "None",
                "<IPv4 192.168.0.252/32>",
                "<IPv4 192.168.0.253/32>",
                "<IPv4 192.168.0.254/32>",
            ],
        ),
        (
            "192.168.0.0/31",
            ["192.168.0.1"],
            {"dist": 2, "sep": True},
            ["<IPv4 192.168.0.0/32>", "<IPv4 192.168.0.1/32>"],
        ),
    ],
)
def test_ipv4_area_spot(prefix, addresses, cfg, result):
    assert [repr(x) for x in IPv4(prefix).area_spot(addresses, **cfg)] == result


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.1/24").normalized, "<IPv4 192.168.0.0/24>"),
        (IPv4("239.12.5.15/4").normalized, "<IPv4 224.0.0.0/4>"),
    ],
)
def test_ipv4_normalized(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.5/24").set_mask(), "<IPv4 192.168.0.5/32>"),
        (IPv4("192.168.0.5/24").set_mask(25), "<IPv4 192.168.0.5/25>"),
    ],
)
def test_ipv4_set_mask(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.0/24").netmask, "<IPv4 255.255.255.0/32>"),
        (IPv4("192.168.0.0/30").netmask, "<IPv4 255.255.255.252/32>"),
    ],
)
def test_ipv4_netmask(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv4("192.168.0.0/24").wildcard, "<IPv4 0.0.0.255/32>"),
        (IPv4("192.168.0.0/30").wildcard, "<IPv4 0.0.0.3/32>"),
    ],
)
def test_ipv4_wildcard(p1, p2):
    assert repr(p1) == p2


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
    params=[
        ("0.0.0.0", 0),
        ("255.0.0.0", 8),
        ("255.255.0.0", 16),
        ("255.255.255.0", 24),
        ("255.255.255.255", 32),
        ("128.0.0.0", 1),
        ("255.255.192.0", 18),
    ]
)
def ipv4_netmask_len(request):
    return request.param


def test_ipv4_netmask_to_len(ipv4_netmask_len):
    m, b = ipv4_netmask_len
    assert IPv4.netmask_to_len(m) == b


@pytest.mark.parametrize(
    "addr,result", [("192.168.0.1", "192.168.0.1"), ("127.0.0.1", "127.0.0.1")]
)
def test_ipv4_expand(addr, result):
    assert IPv4.expand(addr) == result


@pytest.mark.parametrize(
    "p1,p2",
    [
        ("::/0", "::/0"),
        ("2001:db8::/32", "2001:db8::/32"),
        ("::ffff:192.168.0.1", "::ffff:192.168.0.1/128"),
        ("::", "::/128"),
    ],
)
def test_ipv6_str(p1, p2):
    assert str(IPv6(p1)) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            [repr(x) for x in IPv4.range_to_prefixes("192.168.0.2", "192.168.0.2")],
            ["<IPv4 192.168.0.2/32>"],
        ),
        (
            [repr(x) for x in IPv4.range_to_prefixes("192.168.0.2", "192.168.0.16")],
            [
                "<IPv4 192.168.0.2/31>",
                "<IPv4 192.168.0.4/30>",
                "<IPv4 192.168.0.8/29>",
                "<IPv4 192.168.0.16/32>",
            ],
        ),
        (
            [repr(x) for x in IPv4.range_to_prefixes("0.0.0.0", "255.255.255.255")],
            ["<IPv4 0.0.0.0/0>"],
        ),
    ],
)
def test_ipv4_range_to_prefixes(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "prefix,special",
    [
        ("192.168.0.0/24", {"192.168.0.0", "192.168.0.255"}),
        ("192.168.0.0/16", {"192.168.0.0", "192.168.255.255"}),
        ("192.168.0.0/32", set()),
        ("192.168.0.0/31", set()),
        ("192.168.0.0/30", {"192.168.0.0", "192.168.0.3"}),
    ],
)
def test_ipv4_special_addresses(prefix, special):
    assert IPv4.prefix(prefix).special_addresses == set(IPv4(a) for a in special)


@pytest.mark.parametrize(
    "p1,p2",
    [
        ("::/0", "::/0"),
        ("2001:db8::/32", "2001:db8::/32"),
        ("::ffff:192.168.0.1", "::ffff:192.168.0.1/128"),
        ("::", "::/128"),
    ],
)
def test_ipv6_unicode(p1, p2):
    assert smart_text(IPv6(p1)) == p2


@pytest.mark.parametrize("p1,p2", [("::", "<IPv6 ::/128>")])
def test_ipv6_repr(p1, p2):
    assert repr(IPv6(p1)) == p2


@pytest.mark.parametrize(
    "p1,p2", [("::/0", 0), ("::", 128), ("2001:db8::/32", 32), ("::ffff:19.168.0.1", 128)]
)
def test_ipv6_len(p1, p2):
    assert len(IPv6(p1)) == p2


@pytest.mark.parametrize(
    "p1, p2, c, eq, ne, lt, le, gt, ge",
    [
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
    ],
)
def test_ipv6_comparison(p1, p2, c, eq, ne, lt, le, gt, ge):
    p1 = IPv6(p1)
    p2 = IPv6(p2)
    assert ((p1 > p2) - (p1 < p2)) == c
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
        ss[p1]  # pylint: disable=pointless-statement


@pytest.mark.parametrize(
    "p1,p2",
    [
        ((IPv6("::/128") + 1), "<IPv6 ::1/128>"),
        ((IPv6("::/128") + 0xFFFFFFFF), "<IPv6 ::ffff:ffff/128>"),
        ((IPv6("::1/128") + 0xFFFFFFFF), "<IPv6 ::1:0:0/128>"),
        ((IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff") + 2), "<IPv6 ::1/128>"),
    ],
)
def test_ipv6_add(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        ((IPv6("100::5") - 3), "<IPv6 100::2/128>"),
        ((IPv6("100::5") - 5), "<IPv6 100::/128>"),
        ((IPv6("100::5") - 6), "<IPv6 ff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128>"),
        ((IPv6("100::7") - IPv6("100::5")), "2"),
    ],
)
def test_ipv6_sub(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        ((IPv6("::/16").iter_bits()), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ((IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff").iter_bits()), [1] * 128),
        ((IPv6("f000::/4").iter_bits()), [1, 1, 1, 1]),
    ],
)
def test_ipv6_iter_bits(p1, p2):
    assert list(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        ((IPv6.from_bits([1, 1, 1, 1, 1, 1, 1, 1])), "<IPv6 ff00::/8>"),
        ((IPv6.from_bits([1, 1, 1, 1, 1, 1, 1, 1, 1])), "<IPv6 ff80::/9>"),
    ],
)
def test_ipv6_from_bits(p1, p2):
    assert repr(p1) == p2


@pytest.fixture(params=["::", "::ffff:192.168.0.1", "2001:db8::/32", "100::1"])
def ipv6_bits(request):
    return request.param


def test_ipv6_from_to_bits(ipv6_bits):
    p = IPv6(ipv6_bits)
    assert IPv6.from_bits(p.iter_bits()) == p


@pytest.mark.parametrize(
    "p1,p2",
    [
        ([repr(x) for x in IPv6("2001:db8::/32").iter_free([])], ["<IPv6 2001:db8::/32>"]),
        (
            [repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8::/34"])],
            ["<IPv6 2001:db8:4000::/34>", "<IPv6 2001:db8:8000::/33>"],
        ),
        (
            [repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8:4000::/34"])],
            ["<IPv6 2001:db8::/34>", "<IPv6 2001:db8:8000::/33>"],
        ),
    ],
)
def test_ipv6_iter_free(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            [repr(x) for x in IPv6("2001:db8::").iter_address(count=5)],
            [
                "<IPv6 2001:db8::/128>",
                "<IPv6 2001:db8::1/128>",
                "<IPv6 2001:db8::2/128>",
                "<IPv6 2001:db8::3/128>",
                "<IPv6 2001:db8::4/128>",
            ],
        ),
        (
            [repr(x) for x in IPv6("2001:db8::ffff").iter_address(count=5)],
            [
                "<IPv6 2001:db8::ffff/128>",
                "<IPv6 2001:db8::1:0/128>",
                "<IPv6 2001:db8::1:1/128>",
                "<IPv6 2001:db8::1:2/128>",
                "<IPv6 2001:db8::1:3/128>",
            ],
        ),
        (
            [repr(x) for x in IPv6("2001:db8::ffff").iter_address(until="2001:db8::1:3")],
            [
                "<IPv6 2001:db8::ffff/128>",
                "<IPv6 2001:db8::1:0/128>",
                "<IPv6 2001:db8::1:1/128>",
                "<IPv6 2001:db8::1:2/128>",
                "<IPv6 2001:db8::1:3/128>",
            ],
        ),
    ],
)
def test_ipv6_iter_address(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv6("2001:db8::/32").contains(IPv6("2001:db8::/32")), True),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db8::/64")), True),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db8::")), True),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db8:0:ffff:ffff:ffff:ffff:ffff")), True),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db8:ffff:ffff:ffff:ffff:ffff:ffff")), True),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db7:ffff:ffff:ffff:ffff:ffff:ffff")), False),
        (IPv6("2001:db8::/32").contains(IPv6("2001:db9::")), False),
    ],
)
def test_ipv6_contains(p1, p2):
    assert p1 is p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            [
                repr(x)
                for x in IPv6("2001:db8::/32").area_spot(["2001:db8::1", "2001:db8::a"], dist=2)
            ],
            [
                "<IPv6 2001:db8::/128>",
                "<IPv6 2001:db8::1/128>",
                "<IPv6 2001:db8::2/128>",
                "<IPv6 2001:db8::3/128>",
                "<IPv6 2001:db8::8/128>",
                "<IPv6 2001:db8::9/128>",
                "<IPv6 2001:db8::a/128>",
                "<IPv6 2001:db8::b/128>",
                "<IPv6 2001:db8::c/128>",
            ],
        )
    ],
)
def test_ipv6_area_spot(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize("p1,p2", [(IPv6("2001:db8::10/32").first, "<IPv6 2001:db8::/32>")])
def test_ipv6_first(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2", [(IPv6("2001:db8::10/32").last, "<IPv6 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff/32>")]
)
def test_ipv6_last(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv6("0:00:0:0:0::1").normalized, "<IPv6 ::1/128>"),
        (IPv6("2001:db8:0:7:0:0:0:1").normalized, "<IPv6 2001:db8:0:7::1/128>"),
        (IPv6("::ffff:c0a8:1").normalized, "<IPv6 ::ffff:192.168.0.1/128>"),
    ],
)
def test_ipv6_normalized(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (IPv6("2001:db8::20/48").set_mask(), "<IPv6 2001:db8::20/128>"),
        (IPv6("2001:db8::20/48").set_mask(64), "<IPv6 2001:db8::20/64>"),
    ],
)
def test_ipv6_set_mask(p1, p2):
    assert repr(p1) == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            IPv6("2001:db8::1").ptr(0),
            "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2",
        ),
        (IPv6("2001:db8::1").ptr(8), "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"),
    ],
)
def test_ipv6_ptr(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "p1,p2",
    [
        (
            IPv6("2001:db8::1").digits,
            [
                "2",
                "0",
                "0",
                "1",
                "0",
                "d",
                "b",
                "8",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "1",
            ],
        )
    ],
)
def test_ipv6_digits(p1, p2):
    assert p1 == p2


@pytest.mark.parametrize(
    "prefix,base,new_base,result",
    [("2001:db8::7/128", "2001:db8::/32", "2001:db9::/32", "2001:db9::7/128")],
)
def test_ipv6_rebase(prefix, base, new_base, result):
    assert IPv6(prefix).rebase(IPv6(base), IPv6(new_base)) == IPv6(result)


@pytest.mark.parametrize(
    "prefix", ["2001:db8::7/128", "2001:db8::/32", "2001:db9::/32", "2001:db9::7/128"]
)
def test_ipv6_special_addresses(prefix):
    assert IPv6.prefix(prefix).special_addresses == set()


@pytest.mark.parametrize(
    "addr,result",
    [
        ("2001:db8::7/128", "2001:db8:0:0:0:0:0:7/128"),
        ("2001:db8:1:2:3:4:5:7/128", "2001:db8:1:2:3:4:5:7/128"),
    ],
)
def test_ipv6_expand(addr, result):
    assert IPv6.expand(addr) == result


@pytest.mark.parametrize(
    "p1,p2,p3,p4,p5,p6,p7,p8,p9",
    [
        (
            "192.168.0.0/24",
            1,
            "192.168.1.0/24",
            2,
            "192.168.2.0/24",
            3,
            "10.0.0.0/8",
            4,
            "172.16.0.0/12",
        )
    ],
)
def test_prefixdb_ipv4(p1, p2, p3, p4, p5, p6, p7, p8, p9):
    db = PrefixDB()
    db[IPv4(p1)] = p2
    db[IPv4(p3)] = p4
    db[IPv4(p5)] = p6
    db[IPv4(p7)] = p8
    assert db[IPv4(p1)] == p2
    assert db[IPv4(p3)] == p4
    assert db[IPv4(p5)] == p6
    assert db[IPv4(p7)] == p8
    with pytest.raises(KeyError):
        db[IPv4(p9)]


@pytest.mark.parametrize(
    "p1,p2,p3,p4,p5,p6,p7,p8,p9",
    [
        (
            "2001:db8:100::/48",
            1,
            "2001:db8:200::/48",
            2,
            "2001:db8:300::/48",
            3,
            "2001:db8:400::/48",
            4,
            "::/128",
        )
    ],
)
def test_prefixdb_ipv6(p1, p2, p3, p4, p5, p6, p7, p8, p9):
    db = PrefixDB()
    db[IPv6(p1)] = p2
    db[IPv6(p3)] = p4
    db[IPv6(p5)] = p6
    db[IPv6(p7)] = p8
    assert db[IPv6(p1)] == p2
    assert db[IPv6(p3)] == p4
    assert db[IPv6(p5)] == p6
    assert db[IPv6(p7)] == p8
    with pytest.raises(KeyError):
        db[IPv6(p9)]


@pytest.mark.parametrize(
    "p,result",
    [
        ("192.168.0.1", True),
        ("59.19.38.22", False),
        ("10.10.0.22", True),
        ("172.16.0.0/12", True),
        ("3.3.4.5", False),
    ],
)
def test_is_private(p, result):
    assert IP.prefix(p).is_private is result


@pytest.mark.parametrize(
    "p,result",
    [
        ("127.0.0.1", True),
        ("59.19.38.22", False),
        ("127.0.0.1", True),
        ("172.16.0.0/12", False),
        ("127.20.0.1", True),
    ],
)
def test_is_loopback(p, result):
    assert IP.prefix(p).is_loopback is result
