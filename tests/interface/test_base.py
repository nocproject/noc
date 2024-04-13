# ----------------------------------------------------------------------
# noc.sa.interfaces test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest

# NOC modules
from noc.sa.interfaces.base import (
    NoneParameter,
    StringParameter,
    UnicodeParameter,
    REStringParameter,
    REParameter,
    PyExpParameter,
    BooleanParameter,
    IntParameter,
    FloatParameter,
    ListParameter,
    ListOfParameter,
    InstanceOfParameter,
    SubclassOfParameter,
    StringListParameter,
    DictParameter,
    DictListParameter,
    DateTimeParameter,
    IPv4Parameter,
    IPv4PrefixParameter,
    IPv6Parameter,
    IPv6PrefixParameter,
    IPParameter,
    PrefixParameter,
    VLANIDParameter,
    VLANStackParameter,
    VLANIDListParameter,
    VLANIDMapParameter,
    MACAddressParameter,
    OIDParameter,
    RDParameter,
    GeoPointParameter,
    TagsParameter,
    ColorParameter,
    ObjectIdParameter,
    InterfaceTypeError,
)


@pytest.mark.parametrize("raw,config", [(None, {})])
def test_none_parameter(raw, config):
    assert NoneParameter(**config).clean(raw) is None


@pytest.mark.parametrize("raw,config", [("None", {})])
def test_none_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert NoneParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("Test", {}, "Test"),
        (10, {}, "10"),
        (None, {}, "None"),
        ("no test", {"default": "test"}, "no test"),
        (None, {"default": "test"}, "test"),
        ("1", {"choices": ["1", "2"]}, "1"),
    ],
)
def test_string_parameter(raw, config, expected):
    assert StringParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("3", {"choices": ["1", "2"]})])
def test_string_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert StringParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("Test", {}, "Test"),
        (10, {}, "10"),
        (None, {}, "None"),
        ("no test", {"default": "test"}, "no test"),
        (None, {"default": "test"}, "test"),
        ("1", {"choices": ["1", "2"]}, "1"),
    ],
)
def test_unicode_parameter(raw, config, expected):
    assert UnicodeParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("3", {"choices": ["1", "2"]})])
def test_unicode_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert UnicodeParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("exp", {"regexp": "ex+p"}, "exp"),
        ("exxp", {"regexp": "ex+p"}, "exxp"),
        ("regexp 1", {"regexp": "ex+p"}, "regexp 1"),
        ("regexp 1", {"regexp": "ex+p", "default": "exxp"}, "regexp 1"),
        (None, {"regexp": "ex+p", "default": "exxp"}, "exxp"),
    ],
)
def test_re_string_parameter(raw, config, expected):
    assert REStringParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("ex", {"regexp": "ex+p"})])
def test_re_string_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert REStringParameter(**config).clean(raw)


@pytest.mark.parametrize("raw,config,expected", [(".+?", {}, ".+?")])
def test_re_parameter(raw, config, expected):
    assert REParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("+", {})])
def test_re_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert REParameter(**config).clean(raw)


@pytest.mark.parametrize("raw,config,expected", [("(a + 3) * 7", {}, "(a + 3) * 7")])
def test_pyexp_parameter(raw, config, expected):
    assert PyExpParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("a =!= b", {})])
def test_pyexp_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert PyExpParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (True, {}, True),
        (False, {}, False),
        ("True", {}, True),
        ("yes", {}, True),
        (1, {}, True),
        (0, {}, False),
        (None, {"default": False}, False),
        (None, {"default": True}, True),
    ],
)
def test_boolean_parameter(raw, config, expected):
    assert BooleanParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [([], {})])
def test_boolean_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert BooleanParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (1, {}, 1),
        ("1", {}, 1),
        (5, {"max_value": 10, "default": 7}, 5),
        (None, {"max_value": 10, "default": 7}, 7),
    ],
)
def test_int_parameter(raw, config, expected):
    assert IntParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config",
    [
        ("not a number", {}),
        (5, {"min_value": 10}),
        (10, {"max_value": 7}),
        (15, {"max_value": 10}),
        (None, {}),
    ],
)
def test_int_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert IntParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (1.2, {}, 1.2),
        ("1.2", {}, 1.2),
        (5.2, {"max_value": 10.2, "default": 7.2}, 5.2),
        (None, {"max_value": 10.2, "default": 7.2}, 7.2),
    ],
)
def test_float_parameter(raw, config, expected):
    assert FloatParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config",
    [
        ("not a number", {}),
        (5.2, {"min_value": 10.2}),
        (10.2, {"max_value": 7.2}),
        (15.2, {"max_value": 10.2}),
    ],
)
def test_float_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert FloatParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected", [("123", {}, ["1", "2", "3"]), (["1", "2", "3"], {}, ["1", "2", "3"])]
)
def test_list_parmeter(raw, config, expected):
    assert ListParameter(**config).clean(raw) == expected


class C(object):
    pass


class X(object):
    pass


class CC(C):
    pass


@pytest.mark.parametrize("raw,config", [(C(), {"cls": C}), (CC(), {"cls": C}), (C(), {"cls": "C"})])
def test_instanceof_parameter(raw, config):
    assert InstanceOfParameter(**config).clean(raw) == raw


@pytest.mark.parametrize("raw,config", [(X(), {"cls": C}), (1, {"cls": C}), (1, {"cls": "C"})])
def test_instanceof_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert InstanceOfParameter(**config).clean(raw) and "Ok"


class C(object):
    pass


class C1(C):
    pass


class C2(C1):
    pass


class C3(C1):
    pass


@pytest.mark.parametrize("raw,config", [(C2, {"cls": C}), (C2, {"cls": "C"})])
def test_subclassof_parameter(raw, config):
    assert SubclassOfParameter(**config).clean(raw)


@pytest.mark.parametrize("raw,config", [(1, {"cls": C}), (C3, {"cls": C2})])
def test_subclassof_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert SubclassOfParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ([1, 2, 3], {"element": IntParameter()}, [1, 2, 3]),
        ([1, 2, "3"], {"element": IntParameter()}, [1, 2, 3]),
        ([1, 2, 3, "x"], {"element": StringParameter()}, ["1", "2", "3", "x"]),
        (None, {"element": StringParameter(), "default": []}, []),
        (None, {"element": StringParameter(), "default": [1, 2, 3]}, ["1", "2", "3"]),
        (
            [("a", 1), ("b", "2")],
            {"element": [StringParameter(), IntParameter()]},
            [["a", 1], ["b", 2]],
        ),
    ],
)
def test_listof_parameter(raw, config, expected):
    assert ListOfParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config",
    [
        ([1, 2, "x"], {"element": IntParameter()}),
        ([("a", 1), ("b", "x")], {"element": [StringParameter(), IntParameter()]}),
    ],
)
def test_listof_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert ListOfParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [(["1", "2", "3"], {}, ["1", "2", "3"]), (["1", 2, "3"], {}, ["1", "2", "3"])],
)
def test_stringlist_parameter(raw, config, expected):
    assert StringListParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (
            {"i": 10, "s": "ten"},
            {"attrs": {"i": IntParameter(), "s": StringParameter()}},
            {"i": 10, "s": "ten"},
        )
    ],
)
def test_dict_parameter(raw, config, expected):
    assert DictParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config",
    [({"i": "10", "x": "ten"}, {"attrs": {"i": IntParameter(), "s": StringParameter()}})],
)
def test_dict_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert DictParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ([{"1": 2}, {"2": 3, "4": 1}], {}, [{"1": 2}, {"2": 3, "4": 1}]),
        (
            [{"i": 10, "s": "ten"}, {"i": "5", "s": "five"}],
            {"attrs": {"i": IntParameter(), "s": StringParameter()}},
            [{"i": 10, "s": "ten"}, {"i": 5, "s": "five"}],
        ),
        (
            {"i": "10", "s": "ten"},
            {"attrs": {"i": IntParameter(), "s": StringParameter()}, "convert": True},
            [{"i": 10, "s": "ten"}],
        ),
    ],
)
def test_dictlist_parameter(raw, config, expected):
    assert DictListParameter(**config).clean(raw) == expected


def test_datetime_parameter():
    now = datetime.datetime.now()
    assert DateTimeParameter().clean(now) == now.isoformat()


@pytest.mark.parametrize(
    "raw,config,expected",
    [("192.168.0.1", {}, "192.168.0.1"), (b"\xc0\xa8\x8f\x82", {}, "192.168.143.130")],
)
def test_ipv4_parameter(raw, config, expected):
    assert IPv4Parameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("192.168.0.256", {}), (b"\xc0\xa8\x8f\x82\x44", {})])
def test_ipv4_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert IPv4Parameter(**config).clean(raw)


@pytest.mark.parametrize("raw,config,expected", [("192.168.0.0/16", {}, "192.168.0.0/16")])
def test_ipv4prefix_parameter(raw, config, expected):
    assert IPv4PrefixParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config", [("192.168.0.256", {}), ("192.168.0.0/33", {}), ("192.168.0.0/-5", {})]
)
def test_ipv4prefix_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert IPv4PrefixParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("::", {}, "::"),
        ("::1", {}, "::1"),
        ("2001:db8::1", {}, "2001:db8::1"),
        ("2001:db8::", {}, "2001:db8::"),
        ("::ffff:192.168.0.1", {}, "::ffff:192.168.0.1"),
        ("0:00:0:0:0::1", {}, "::1"),
        ("::ffff:c0a8:1", {}, "::ffff:192.168.0.1"),
        ("2001:db8:0:7:0:0:0:1", {}, "2001:db8:0:7::1"),
    ],
)
def test_ipv6_parameter(raw, config, expected):
    assert IPv6Parameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("g::", {})])
def test_ipv6_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert IPv6Parameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected", [("::/128", {}, "::/128"), ("2001:db8::/32", {}, "2001:db8::/32")]
)
def test_ipv6prefix_parameter(raw, config, expected):
    assert IPv6PrefixParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config", [("2001:db8::/129", {}), ("2001:db8::/g", {}), ("2001:db8::", {})]
)
def test_ipv6prefix_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert IPv6PrefixParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("192.168.0.1", {}, "192.168.0.1"),
        ("2001:db8::", {}, "2001:db8::"),
        (b"\xc0\xa8\x8f\x82", {}, "192.168.143.130"),
    ],
)
def test_ip_parameter(raw, config, expected):
    assert IPParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [("192.168.0.0/24", {}, "192.168.0.0/24"), ("2001:db8::/32", {}, "2001:db8::/32")],
)
def test_prefix_parameter(raw, config, expected):
    assert PrefixParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config,expected", [(10, {}, 10)])
def test_vlanid_parameter(raw, config, expected):
    assert VLANIDParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [(5000, {}), (0, {})])
def test_vlanid_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert VLANIDParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [(10, {}, [10]), ([10], {}, [10]), ([10, "20"], {}, [10, 20]), ([10, 0], {}, [10, 0])],
)
def test_vlanstack_parameter(raw, config, expected):
    assert VLANStackParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config,expected", [(["1", "2", "3"], {}, [1, 2, 3]), ([1, 2, 3], {}, [1, 2, 3])]
)
def test_vlanidlist_parameter(raw, config, expected):
    assert VLANIDListParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config,expected", [("1,2,5-10", {}, "1-2,5-10"), ("", {}, "")])
def test_vlanidmap_parameter(raw, config, expected):
    assert VLANIDMapParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("1234.5678.9ABC", {}, "12:34:56:78:9A:BC"),
        ("1234.5678.9abc", {}, "12:34:56:78:9A:BC"),
        ("0112.3456.789a.bc", {}, "12:34:56:78:9A:BC"),
        ("12:34:56:78:9A:BC", {}, "12:34:56:78:9A:BC"),
        ("12-34-56-78-9A-BC", {}, "12:34:56:78:9A:BC"),
        ("0:13:46:50:87:5", {}, "00:13:46:50:87:05"),
        ("123456-789abc", {}, "12:34:56:78:9A:BC"),
        ("aabb-ccdd-eeff", {}, "AA:BB:CC:DD:EE:FF"),
        ("aabbccddeeff", {}, "AA:BB:CC:DD:EE:FF"),
        ("AA:BB:CC:DD:EE:FF", {}, "AA:BB:CC:DD:EE:FF"),
        ("\xa8\xf9K\x80\xb4\xc0", {}, "A8:F9:4B:80:B4:C0"),
    ],
)
def test_macaddress_parameter(raw, config, expected):
    assert MACAddressParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config",
    [
        ("1234.5678.9abc.def0", {}),
        ("12-34-56-78-9A-BC-DE", {}),
        ("AB-CD-EF-GH-HJ-KL", {}),
        ("\\xa8\\xf9K\\x80\\xb4\\xc0", {"accept_bin": False}),
    ],
)
def test_macaddress_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert MACAddressParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("1.3.6.1.2.1.1.1.0", {}, "1.3.6.1.2.1.1.1.0"),
        (None, {"default": "1.3.6.1.2.1.1.1.0"}, "1.3.6.1.2.1.1.1.0"),
    ],
)
def test_oid_parameter(raw, config, expected):
    assert OIDParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("1.3.6.1.2.1.1.X.0", {})])
def test_oid_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert OIDParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ("100:4294967295", {}, "100:4294967295"),
        ("10.10.10.10:10", {}, "10.10.10.10:10"),
        ("100000:500", {}, "100000:500"),
        ("100000L:100", {}, "100000:100"),
    ],
)
def test_rd_parameter(raw, config, expected):
    assert RDParameter(**config).clean(raw) == expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [([180, 90], {}, [180, 90]), ([75.5, "90"], {}, [75.5, 90]), ("[180, 85.5]", {}, [180, 85.5])],
)
def test_geopoint_parameter(raw, config, expected):
    assert GeoPointParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [([1], {})])
def test_geopoint_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert GeoPointParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ([1, 2, "tags"], {}, ["1", "2", "tags"]),
        ([1, 2, "tags "], {}, ["1", "2", "tags"]),
        ("1,2,tags", {}, ["1", "2", "tags"]),
        ("1 , 2,  tags", {}, ["1", "2", "tags"]),
    ],
)
def test_tags_parameter(raw, config, expected):
    assert TagsParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [(1, {})])
def test_tags_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert TagsParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected", [(None, {"default": 0xFF}, 0xFF), ("#ff0000", {}, 0xFF0000)]
)
def test_color_parameter(raw, config, expected):
    assert ColorParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("#ff00000", {}), ("#ff000x", {})])
def test_color_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert ColorParameter(**config).clean(raw)


@pytest.mark.parametrize(
    "raw,config,expected", [("5b2d0cba4575cf01ead6aa89", {}, "5b2d0cba4575cf01ead6aa89")]
)
def test_object_id_parameter(raw, config, expected):
    assert ObjectIdParameter(**config).clean(raw) == expected


@pytest.mark.parametrize("raw,config", [("5b2d0cba4575cf01ead6aa8x", {})])
def test_object_id_parameter_error(raw, config):
    with pytest.raises(InterfaceTypeError):
        assert ObjectIdParameter(**config).clean(raw)
