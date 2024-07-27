# ----------------------------------------------------------------------
# noc.core.text tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.text import (
    parse_table,
    strip_html_tags,
    xml_to_table,
    list_to_ranges,
    ranges_to_list,
    replace_re_group,
    indent,
    split_alnum,
    alnum_key,
    find_indented,
    to_seconds,
    format_table,
    clean_number,
    safe_shadow,
    ch_escape,
    split_text,
    str_distance,
)


@pytest.mark.parametrize(
    "value,kwargs,expected",
    [
        (
            "First Second Third\n" "----- ------ -----\n" "a     b       c\n" "ddd   eee     fff\n",
            {},
            [["a", "b", "c"], ["ddd", "eee", "fff"]],
        ),
        (
            "First Second Third\n" "----- ------ -----\n" "a             c\n" "ddd   eee     fff\n",
            {},
            [["a", "", "c"], ["ddd", "eee", "fff"]],
        ),
        (
            "VLAN Status  Name                             Ports\n"
            "---- ------- -------------------------------- ---------------------------------\n"
            "4090 Static  VLAN4090                         f0/5, f0/6, f0/7, f0/8, g0/9\n"
            "                                              g0/10\n",
            {"allow_wrap": True, "n_row_delim": ", "},
            [["4090", "Static", "VLAN4090", "f0/5, f0/6, f0/7, f0/8, g0/9, g0/10"]],
        ),
        (
            " MSTI ID     Vid list\n"
            " -------     -------------------------------------------------------------\n"
            "    CIST     1-11,15-122,124-250,253,257-300,302-445,447-709\n"
            "             ,720-759,770-879,901-3859,3861-4094\n"
            "       1     12-14,123,251-252,254-256,301,446,710-719,760-769,\n"
            "             880-900,3860\n",
            {"allow_wrap": True, "n_row_delim": ","},
            [
                [
                    "CIST",
                    "1-11,15-122,124-250,253,257-300,302-445,447-709,720-759,770-879,901-3859,3861-4094",
                ],
                ["1", "12-14,123,251-252,254-256,301,446,710-719,760-769,880-900,3860"],
            ],
        ),
        (
            """Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator

        M - not in use, minimum links not met
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port


Number of channel-groups in use: 7
Number of aggregators:           7

Group  Port-channel  Protocol    Ports
------+-------------+-----------+-----------------------------------------------
11     Po11(SD)        LACP      Gi1/20(D)   Gi1/21(D)
12     Po12(SD)        LACP      Gi2/16(D)
13     Po13(SU)        LACP      Te3/2(P)
14     Po14(SU)        LACP      Te3/4(P)    Te4/4(P)
15     Po15(SU)        LACP      Gi2/6(P)    Gi2/14(P)
16     Po16(SU)        LACP      Te3/3(P)    Te4/3(P)
17     Po17(SU)        LACP      Gi2/3(P)    Gi2/19(P)   Gi2/20(P)
                                 Gi2/22(P)
""",
            {"allow_wrap": True, "max_width": 120},
            [
                ["11", "Po11(SD)", "LACP", "Gi1/20(D)   Gi1/21(D)"],
                ["12", "Po12(SD)", "LACP", "Gi2/16(D)"],
                ["13", "Po13(SU)", "LACP", "Te3/2(P)"],
                ["14", "Po14(SU)", "LACP", "Te3/4(P)    Te4/4(P)"],
                ["15", "Po15(SU)", "LACP", "Gi2/6(P)    Gi2/14(P)"],
                ["16", "Po16(SU)", "LACP", "Te3/3(P)    Te4/3(P)"],
                ["17", "Po17(SU)", "LACP", "Gi2/3(P)    Gi2/19(P)   Gi2/20(P)Gi2/22(P)"],
            ],
        ),
        (
            "Vlan    Mac Address       Type       Ports\n"
            "----    -----------       ----       -----\n"
            "All\t1111.2222.3333\t  STATIC     CPU\n"
            "611\t1111.2223.3efc\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.3cdc\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.4010\t  DYNAMIC    g0/2\n"
            "1\t1111.2224.1fd8\t  DYNAMIC    g0/1\n"
            "1\t1111.2225.0bb1\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.6bfc\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.42d8\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.6bf8\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.42dc\t  DYNAMIC    g0/2\n"
            "611\t1111.2226.0001\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.3cd8\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.3ef8\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.4014\t  DYNAMIC    g0/2\n"
            "611\t1111.2227.3480\t  DYNAMIC    g0/2\n"
            "1\t1111.2228.a16d\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.38e0\t  DYNAMIC    g0/2\n"
            "1\t1111.2229.a16c\t  DYNAMIC    g0/2\n"
            "611\t1111.2223.38e4\t  DYNAMIC    g0/2\n"
            "611\t1111.222a.2e1e\t  DYNAMIC    g0/2\n",
            {"expand_columns": True},
            [
                ["All", "1111.2222.3333", "STATIC", "CPU"],
                ["611", "1111.2223.3efc", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.3cdc", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.4010", "DYNAMIC", "g0/2"],
                ["1", "1111.2224.1fd8", "DYNAMIC", "g0/1"],
                ["1", "1111.2225.0bb1", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.6bfc", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.42d8", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.6bf8", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.42dc", "DYNAMIC", "g0/2"],
                ["611", "1111.2226.0001", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.3cd8", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.3ef8", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.4014", "DYNAMIC", "g0/2"],
                ["611", "1111.2227.3480", "DYNAMIC", "g0/2"],
                ["1", "1111.2228.a16d", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.38e0", "DYNAMIC", "g0/2"],
                ["1", "1111.2229.a16c", "DYNAMIC", "g0/2"],
                ["611", "1111.2223.38e4", "DYNAMIC", "g0/2"],
                ["611", "1111.222a.2e1e", "DYNAMIC", "g0/2"],
            ],
        ),
        (
            """ifIndex     ifDescr                                Interface
----------  -------------------------------------  ---------
         1  Switch  1 - Port  0                    GigabitEthernet 1/1
         2  Switch  1 - Port  1                    GigabitEthernet 1/2
         3  Switch  1 - Port  2                    GigabitEthernet 1/3
         4  Switch  1 - Port  3                    GigabitEthernet 1/4
         5  Switch  1 - Port  4                    GigabitEthernet 1/5
         6  Switch  1 - Port  5                    GigabitEthernet 1/6
         7  Switch  1 - Port  6                    GigabitEthernet 1/7
         8  Switch  1 - Port  7                    GigabitEthernet 1/8
         9  Switch  1 - Port  8                    GigabitEthernet 1/9
        10  Switch  1 - Port  9                    GigabitEthernet 1/10
        11  Switch  1 - Port 10                    GigabitEthernet 1/11
        12  Switch  1 - Port 11                    GigabitEthernet 1/12
        13  Switch  1 - Port 12                    2.5GigabitEthernet 1/1
""",
            {"allow_wrap": True, "max_width": 80},
            [
                ["1", "Switch  1 - Port  0", "GigabitEthernet 1/1"],
                ["2", "Switch  1 - Port  1", "GigabitEthernet 1/2"],
                ["3", "Switch  1 - Port  2", "GigabitEthernet 1/3"],
                ["4", "Switch  1 - Port  3", "GigabitEthernet 1/4"],
                ["5", "Switch  1 - Port  4", "GigabitEthernet 1/5"],
                ["6", "Switch  1 - Port  5", "GigabitEthernet 1/6"],
                ["7", "Switch  1 - Port  6", "GigabitEthernet 1/7"],
                ["8", "Switch  1 - Port  7", "GigabitEthernet 1/8"],
                ["9", "Switch  1 - Port  8", "GigabitEthernet 1/9"],
                ["10", "Switch  1 - Port  9", "GigabitEthernet 1/10"],
                ["11", "Switch  1 - Port 10", "GigabitEthernet 1/11"],
                ["12", "Switch  1 - Port 11", "GigabitEthernet 1/12"],
                ["13", "Switch  1 - Port 12", "2.5GigabitEthernet 1/1"],
            ],
        ),
        (
            """
LLDP Remote Device Summary

Local
Interface  RemID    Chassis ID            Port ID             System Name
---------  -------  --------------------  ------------------  ------------------
0/9        1        11:22:33:44:55:66     GigabitEthernet2/0/9  SS-MS-1
0/10

""",
            {"allow_extend": True},
            [
                ["0/9", "1", "11:22:33:44:55:66", "GigabitEthernet2/0/9", "SS-MS-1"],
                ["0/10", "", "", "", ""],
            ],
        ),
        (
            """
LLDP Remote Device Summary

Local
Interface  RemID    Chassis ID            Port ID             System Name
---------  -------  --------------------  ------------------  ------------------
0/9        3        11:22:33:44:55:66     GigabitEthernet0/0/8  qqq0-sasasasa-rr11
0/10       1        11:22:33:44:55:67     gi1/1/1             e22-a777-b774-1

""",
            {"allow_extend": True},
            [
                ["0/9", "3", "11:22:33:44:55:66", "GigabitEthernet0/0/8", "qqq0-sasasasa-rr11"],
                ["0/10", "1", "11:22:33:44:55:67", "gi1/1/1", "e22-a77"],
            ],
        ),
        (
            """

 Port       Device ID         Port ID        System Name    Capabilities  TTL
------- ----------------- --------------- ----------------- ------------ -----
g1      00:11:22:33:44:55 GigabitEthernet SS555_XXXX_Skeeee     B, R      109
                          0/0/3           x_333_Stack
g2      00:11:22:33:44:55 GigabitEthernet SS555_XXXX_Skeeee     B, R      109
                          1/0/3           x_333_Stack

""",
            {"allow_extend": True, "allow_wrap": True},
            [
                [
                    "g1",
                    "00:11:22:33:44:55",
                    "GigabitEthernet0/0/3",
                    "SS555_XXXX_Skeeeex_333_Stack",
                    "B, R",
                    "109",
                ],
                [
                    "g2",
                    "00:11:22:33:44:55",
                    "GigabitEthernet1/0/3",
                    "SS555_XXXX_Skeeeex_333_Stack",
                    "B, R",
                    "109",
                ],
            ],
        ),
        (
            """
  Port        Device ID          Port ID         System Name    Capabilities  TTL
--------- ----------------- ----------------- ----------------- ------------ -----
te1/0/3        (1RY\t#       GigabitEthernet1/  MBH_75_00020_1       B, R      106
                            3/0
""",
            {"allow_extend": True, "allow_wrap": True, "line_wrapper": None},
            [["te1/0/3", "(1RY\t#", "GigabitEthernet1/3/0", "MBH_75_00020_1", "B, R", "106"]],
        ),
        (
            """
  Port        Device ID        Port ID       System Name    Capabilities  TTL
--------- ----------------- ------------- ----------------- ------------ -----
gi1/0/1   00:11:22:33:44:55 gigaethernet1 Internacional'nyy     B, r      100
                                /1/28         -13_2pod
""",
            {"allow_wrap": True, "row_wrapper": lambda x: x.strip()},
            [
                [
                    "gi1/0/1",
                    "00:11:22:33:44:55",
                    "gigaethernet1/1/28",
                    "Internacional'nyy-13_2pod",
                    "B, r",
                    "100",
                ]
            ],
        ),
    ],
)
def test_parse_table(value, kwargs, expected):
    assert parse_table(value, **kwargs) == expected


@pytest.mark.parametrize("expected", ["Title            Body    Text"])
def test_strip_html_tags(expected):
    html = """
    <html>
    <head>
    <title>Title</title>
    </head>
    <body>
    <H1>Body</H1>
    <P>Text</P>
    </body>
    </html>
    """
    out = strip_html_tags(html)
    out = out.strip()
    out = out.replace("\n", "")
    assert out == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (
            [
                '<?xml version="1.0" encoding="UTF-8" ?><response><action><row><a>1</a><b>2</b></row><row><a>3</a><b>4</b></row></action></response>'  # noqa
            ],
            [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
        )
    ],
)
def test_xml_to_table(config, expected):
    assert xml_to_table(str(config), "action", "row") == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ([], ""),
        ([1], "1"),
        ([1, 2], "1-2"),
        ([1, 2, 3], "1-3"),
        ([1, 2, 3, 5], "1-3,5"),
        ([1, 2, 3, 5, 6, 7], "1-3,5-7"),
        (range(1, 4001), "1-4000"),
    ],
)
def test_list_to_ranges(config, expected):
    assert list_to_ranges(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ("1", [1]),
        ("1, 2", [1, 2]),
        ("1, 10-12", [1, 10, 11, 12]),
        ("1, 10-12, 15, 17-19", [1, 10, 11, 12, 15, 17, 18, 19]),
    ],
)
def test_ranges_to_list(config, expected):
    assert ranges_to_list(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ("nothing", "nothing"),
        ("the (?P<groupname>simple) test", "the groupvalue test"),
        ("the (?P<groupname> nested (test)>)", "the groupvalue"),
    ],
)
def test_replace_re_group_text(config, expected):
    assert replace_re_group(config, "(?P<groupname>", "groupvalue") == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (b"nothing", b"nothing"),
        (b"the (?P<groupname>simple) test", b"the groupvalue test"),
        (b"the (?P<groupname> nested (test)>)", b"the groupvalue"),
    ],
)
def test_replace_re_group_bytes(config, expected):
    assert replace_re_group(config, b"(?P<groupname>", b"groupvalue") == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ("", ""),
        (
            "the quick brown fox\\njumped over an lazy dog\\nend",
            " the quick brown fox\\njumped over an lazy dog\\nend",
        ),
    ],
)
def test_indent(config, expected):
    assert indent(config, n=1) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ("Fa 0/1", ["Fa ", 0, "/", 1]),
        ("Fa 0/1.15", ["Fa ", 0, "/", 1, ".", 15]),
        ("ge-1/0/1", ["ge-", 1, "/", 0, "/", 1]),
        ("ge-1/0/1.15", ["ge-", 1, "/", 0, "/", 1, ".", 15]),
    ],
)
def test_split_alnum(config, expected):
    assert split_alnum(config) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("auto", "auto"),
        ("0", "000000000000"),
        ("1", "000000000001"),
        ("Fa 0/1", "Fa 000000000000/000000000001"),
        ("ge-1/0/1.15", "ge-000000000001/000000000000/000000000001.000000000015"),
    ],
)
def test_alnum_key(input, expected):
    assert alnum_key(input) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (
            "section0\nsection 1\n  line 1-1\n  line 1-2\n\n section 2\n  line 2-1\n  line 2-2",
            ["section 1\n  line 1-1\n  line 1-2\n section 2\n  line 2-1\n  line 2-2"],
        )
    ],
)
def test_find_indented(config, expected):
    assert find_indented(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [("1h", 3600), ("1d", 86400), ("1w", 604800), ("1m", 2592000), ("1y", 31536000)],
)
def test_to_seconds(config, expected):
    assert to_seconds(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (
            [["H1", "H2", "H3"], ["s1", "s2", "s3"], ["s1.1", "s2.1", "s3.1"]],
            "H1   H2   H3  \n---- ---- ----\ns1   s2   s3  \ns1.1 s2.1 s3.1",
        )
    ],
)
def test_format_table(config, expected):
    assert format_table([0, 0, 0, 0, 0], config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [("12w34r5t6y7", "1234567"), ("   223ssSSSf*3", "2233"), ("(032HDWeg sda^@3f ", "0323")],
)
def test_clean_number(config, expected):
    assert clean_number(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [(None, "None"), ("s", "******"), ("sssssss", "s******s"), ("1", "******"), ([1, 2], "******")],
)
def test_safe_shadow(config, expected):
    assert safe_shadow(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        ("aaaa\nbbbb\nssssss\n", "aaaa\\\\nbbbb\\\\nssssss\\\\n"),
        ("aaaa\nbbbb\nsss sss\n", "aaaa\\\\nbbbb\\\\nsss sss\\\\n"),
    ],
)
def test_ch_escape(config, expected):
    assert ch_escape(config) == expected


@pytest.mark.parametrize(
    "config, max_chunk, expected",
    [
        (
            "sssssssssssssssssss\naaaaaaaaaaaaaaaaaaaaa\nsdasdasdasdsadasdasdsad",
            500,
            ["sssssssssssssssssss\naaaaaaaaaaaaaaaaaaaaa\nsdasdasdasdsadasdasdsad"],
        ),
        (
            "sssssssssssssssssss\naaaaaaaaaaaaaaaaaaaaa\nsdasdasdasdsadasdasdsad",
            50,
            ["sssssssssssssssssss\naaaaaaaaaaaaaaaaaaaaa", "sdasdasdasdsadasdasdsad"],
        ),
    ],
)
def test_split_text(config, max_chunk, expected):
    assert list(split_text(config, max_chunk=max_chunk)) == expected


@pytest.mark.parametrize(
    ["s1", "s2", "expected"],
    [
        # Empty
        ("", "", 0),
        # Same
        ("a", "a", 0),
        ("ab", "ab", 0),
        ("abc", "abc", 0),
        # Diference in case
        ("a", "A", 0),
        ("aB", "Ab", 0),
        ("aBc", "aBC", 0),
        # Difference in length
        ("ab", "abcd", 2),
        ("abcd", "ab", 2),
        # Difference in one char
        ("Gi X/1", "Gi 0/1", 1),
        # Difference in two chars
        ("Gi X/1", "Gi 0/2", 2),
    ],
)
def test_str_distance(s1: str, s2: str, expected: int) -> None:
    d = str_distance(s1, s2)
    assert d == expected
