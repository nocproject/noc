# -*- coding: utf-8 -*-
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
    NoneParameter, StringParameter, UnicodeParameter, REStringParameter, REParameter,
    PyExpParameter, BooleanParameter, IntParameter, FloatParameter,
    ListParameter, ListOfParameter, InstanceOfParameter, SubclassOfParameter,
    StringListParameter, DictParameter, DictListParameter, DateTimeParameter,
    IPv4Parameter, IPv4PrefixParameter, IPv6Parameter, IPv6PrefixParameter,
    IPParameter, PrefixParameter,
    VLANIDParameter, VLANStackParameter, VLANIDListParameter, VLANIDMapParameter,
    MACAddressParameter, OIDParameter,
    RDParameter, GeoPointParameter, TagsParameter,
    ColorParameter, ObjectIdParameter,
    InterfaceTypeError
)


def test_none_parameter():
    assert NoneParameter().clean(None) is None
    with pytest.raises(InterfaceTypeError):
        NoneParameter().clean("None")


def test_string_parameter():
    assert StringParameter().clean("Test") == "Test"
    assert StringParameter().clean(10) == "10"
    assert StringParameter().clean(None) == "None"
    assert StringParameter(default="test").clean("no test") == "no test"
    assert StringParameter(default="test").clean(None) == "test"
    assert StringParameter(choices=["1", "2"]).clean("1") == "1"
    with pytest.raises(InterfaceTypeError):
        assert StringParameter(choices=["1", "2"]).clean("3")


def test_unicode_parameter():
    assert UnicodeParameter().clean(u"Test") == u"Test"
    assert UnicodeParameter().clean(10) == u"10"
    assert UnicodeParameter().clean(None) == u"None"
    assert UnicodeParameter(default=u"test").clean(u"no test") == u"no test"
    assert UnicodeParameter(default=u"test").clean(None) == u"test"
    assert UnicodeParameter(choices=[u"1", u"2"]).clean(u"1") == u"1"
    with pytest.raises(InterfaceTypeError):
        assert UnicodeParameter(choices=[u"1", u"2"]).clean(u"3")


def test_re_string_parameter():
    assert REStringParameter("ex+p").clean("exp") == "exp"
    assert REStringParameter("ex+p").clean("exxp") == "exxp"
    assert REStringParameter("ex+p").clean("regexp 1") == "regexp 1"
    with pytest.raises(InterfaceTypeError):
        assert REStringParameter("ex+p").clean("ex")
    assert REStringParameter("ex+p", default="exxp").clean("regexp 1") == "regexp 1"
    assert REStringParameter("ex+p", default="exxp").clean(None) == "exxp"


def test_re_parameter():
    assert REParameter().clean(".+?") == ".+?"
    with pytest.raises(InterfaceTypeError):
        assert REParameter().clean("+")


def test_pyexp_parameter():
    assert PyExpParameter().clean("(a + 3) * 7") == "(a + 3) * 7"
    with pytest.raises(InterfaceTypeError):
        assert PyExpParameter().clean("a =!= b")


def test_boolean_parameter():
    assert BooleanParameter().clean(True) is True
    assert BooleanParameter().clean(False) is False
    assert BooleanParameter().clean("True") is True
    assert BooleanParameter().clean("yes") is True
    assert BooleanParameter().clean(1) is True
    assert BooleanParameter().clean(0) is False
    with pytest.raises(InterfaceTypeError):
        assert BooleanParameter().clean([])
    assert BooleanParameter(default=False).clean(None) is False
    assert BooleanParameter(default=True).clean(None) is True


def test_int_parameter():
    assert IntParameter().clean(1) == 1
    assert IntParameter().clean("1") == 1
    with pytest.raises(InterfaceTypeError):
        IntParameter().clean("not a number")
    with pytest.raises(InterfaceTypeError):
        IntParameter(min_value=10).clean(5)
    with pytest.raises(InterfaceTypeError):
        IntParameter(max_value=7).clean(10)
    assert IntParameter(max_value=10, default=7).clean(5) == 5
    assert IntParameter(max_value=10, default=7).clean(None) == 7
    with pytest.raises(InterfaceTypeError):
        IntParameter(max_value=10, default=15)
    with pytest.raises(InterfaceTypeError):
        IntParameter().clean(None)


def test_float_parameter():
    assert FloatParameter().clean(1.2) == 1.2
    assert FloatParameter().clean("1.2") == 1.2
    with pytest.raises(InterfaceTypeError):
        FloatParameter().clean("not a number")
    with pytest.raises(InterfaceTypeError):
        FloatParameter(min_value=10).clean(5)
    with pytest.raises(InterfaceTypeError):
        FloatParameter(max_value=7).clean(10)
    assert FloatParameter(max_value=10, default=7).clean(5) == 5
    assert FloatParameter(max_value=10, default=7).clean(None) == 7
    with pytest.raises(InterfaceTypeError):
        assert FloatParameter(max_value=10, default=15)


def test_list_parmeter():
    assert ListParameter().clean("123") == ["1", "2", "3"]
    assert ListParameter().clean(["1", "2", "3"]) == ["1", "2", "3"]


def test_instanceof_parameter():
    class C(object):
        pass

    class X(object):
        pass

    class CC(C):
        pass

    c = C()
    cc = CC()
    x = X()
    assert InstanceOfParameter(cls=C).clean(c) == c
    assert InstanceOfParameter(cls=C).clean(cc) == cc
    with pytest.raises(InterfaceTypeError):
        InstanceOfParameter(cls=C).clean(x)
    with pytest.raises(InterfaceTypeError):
        InstanceOfParameter(cls=C).clean(1)

    assert InstanceOfParameter(cls="C").clean(c) == c
    with pytest.raises(InterfaceTypeError):
        InstanceOfParameter(cls="C").clean(1) and "Ok"


def subclass_of_parameter():
    class C(object):
        pass

    class C1(C):
        pass

    class C2(C1):
        pass

    class C3(C1):
        pass

    assert SubclassOfParameter(cls=C).clean(C2) is True
    with pytest.raises(InterfaceTypeError):
        SubclassOfParameter(cls=C).clean(1)
    assert SubclassOfParameter(cls="C").clean(C2) is True
    with pytest.raises(InterfaceTypeError):
        SubclassOfParameter(cls=C).clean(1)
    with pytest.raises(InterfaceTypeError):
        SubclassOfParameter(cls=C2).clean(C3)
    assert SubclassOfParameter(cls="C", required=False).clean(None)


def test_listof_parameter():
    assert ListOfParameter(element=IntParameter()).clean([1, 2, 3]) == [1, 2, 3]
    assert ListOfParameter(element=IntParameter()).clean([1, 2, "3"]) == [1, 2, 3]
    with pytest.raises(InterfaceTypeError):
        ListOfParameter(element=IntParameter()).clean([1, 2, "x"])
    assert ListOfParameter(element=StringParameter()).clean([1, 2, 3, "x"]) == ["1", "2", "3", "x"]
    assert ListOfParameter(element=StringParameter(), default=[]).clean(None) == []
    assert ListOfParameter(element=StringParameter(), default=[1, 2, 3]).clean(None) == ["1", "2",
                                                                                         "3"]
    assert ListOfParameter(element=[StringParameter(), IntParameter()]).clean(
        [("a", 1), ("b", "2")]) == [["a", 1], ["b", 2]]
    with pytest.raises(InterfaceTypeError):
        assert ListOfParameter(element=[StringParameter(), IntParameter()]).clean(
            [("a", 1), ("b", "x")])


def test_stringlist_parameter():
    assert StringListParameter().clean(["1", "2", "3"]) == ["1", "2", "3"]
    assert StringListParameter().clean(["1", 2, "3"]) == ["1", "2", "3"]


def test_dict_parameter():
    assert DictParameter(attrs={"i": IntParameter(), "s": StringParameter()}).clean(
        {"i": 10, "s": "ten"}) == {"i": 10, "s": "ten"}
    with pytest.raises(InterfaceTypeError):
        DictParameter(attrs={"i": IntParameter(), "s": StringParameter()}).clean(
            {"i": "10", "x": "ten"})


def test_dictlist_parameter():
    assert DictListParameter().clean([{"1": 2}, {"2": 3, "4": 1}]) == [{"1": 2}, {"2": 3, "4": 1}]
    assert DictListParameter(attrs={"i": IntParameter(), "s": StringParameter()}).clean(
        [{"i": 10, "s": "ten"}, {"i": "5", "s": "five"}]) == [{"i": 10, "s": "ten"},
                                                              {"i": 5, "s": "five"}]
    assert DictListParameter(attrs={"i": IntParameter(), "s": StringParameter()},
                             convert=True).clean({"i": "10", "s": "ten"}) == [{"i": 10, "s": "ten"}]


def test_datetime_parameter():
    now = datetime.datetime.now()
    assert DateTimeParameter().clean(now) == now.isoformat()


def test_ipv4_parameter():
    assert IPv4Parameter().clean("192.168.0.1") == "192.168.0.1"
    with pytest.raises(InterfaceTypeError):
        IPv4Parameter().clean("192.168.0.256")


def test_ipv4prefix_parameter():
    assert IPv4PrefixParameter().clean("192.168.0.0/16") == "192.168.0.0/16"
    with pytest.raises(InterfaceTypeError):
        IPv4PrefixParameter().clean("192.168.0.256")
    with pytest.raises(InterfaceTypeError):
        IPv4PrefixParameter().clean("192.168.0.0/33")
    with pytest.raises(InterfaceTypeError):
        IPv4PrefixParameter().clean("192.168.0.0/-5")


def test_ipv6_parameter():
    assert IPv6Parameter().clean("::") == "::"
    assert IPv6Parameter().clean("::1") == "::1"
    assert IPv6Parameter().clean("2001:db8::1") == "2001:db8::1"
    assert IPv6Parameter().clean("2001:db8::") == "2001:db8::"
    assert IPv6Parameter().clean("::ffff:192.168.0.1") == "::ffff:192.168.0.1"
    with pytest.raises(InterfaceTypeError):
        IPv6Parameter().clean("g::")
    assert IPv6Parameter().clean("0:00:0:0:0::1") == "::1"
    assert IPv6Parameter().clean("::ffff:c0a8:1") == "::ffff:192.168.0.1"
    assert IPv6Parameter().clean("2001:db8:0:7:0:0:0:1") == "2001:db8:0:7::1"


def test_ipv6prefix_parameter():
    assert IPv6PrefixParameter().clean("::/128") == "::/128"
    assert IPv6PrefixParameter().clean("2001:db8::/32") == "2001:db8::/32"
    with pytest.raises(InterfaceTypeError):
        IPv6PrefixParameter().clean("2001:db8::/129")
    with pytest.raises(InterfaceTypeError):
        IPv6PrefixParameter().clean("2001:db8::/g")
    with pytest.raises(InterfaceTypeError):
        IPv6PrefixParameter().clean("2001:db8::")


def test_ip_parameter():
    assert IPParameter().clean("192.168.0.1") == "192.168.0.1"
    assert IPParameter().clean("2001:db8::") == "2001:db8::"


def test_prefix_parameter():
    assert PrefixParameter().clean("192.168.0.0/24") == "192.168.0.0/24"
    assert PrefixParameter().clean("2001:db8::/32") == "2001:db8::/32"


def test_vlanid_parameter():
    assert VLANIDParameter().clean(10) == 10
    with pytest.raises(InterfaceTypeError):
        VLANIDParameter().clean(5000)
    with pytest.raises(InterfaceTypeError):
        VLANIDParameter().clean(0)


def test_vlanstack_parameter():
    assert VLANStackParameter().clean(10) == [10]
    assert VLANStackParameter().clean([10]) == [10]
    assert VLANStackParameter().clean([10, "20"]) == [10, 20]
    assert VLANStackParameter().clean([10, 0]) == [10, 0]


def test_vlanidlist_parameter():
    assert VLANIDListParameter().clean(["1", "2", "3"]) == [1, 2, 3]
    assert VLANIDListParameter().clean([1, 2, 3]) == [1, 2, 3]


def test_vlanidmap_parameter():
    assert VLANIDMapParameter().clean("1,2,5-10") == "1-2,5-10"
    assert VLANIDMapParameter().clean("") == ""


def test_macaddress_parameter():
    assert MACAddressParameter().clean("1234.5678.9ABC") == "12:34:56:78:9A:BC"
    assert MACAddressParameter().clean("1234.5678.9abc") == "12:34:56:78:9A:BC"
    assert MACAddressParameter().clean("0112.3456.789a.bc") == "12:34:56:78:9A:BC"
    with pytest.raises(InterfaceTypeError):
        MACAddressParameter().clean("1234.5678.9abc.def0")
    assert MACAddressParameter().clean("12:34:56:78:9A:BC") == "12:34:56:78:9A:BC"
    assert MACAddressParameter().clean("12-34-56-78-9A-BC") == "12:34:56:78:9A:BC"
    assert MACAddressParameter().clean("0:13:46:50:87:5") == "00:13:46:50:87:05"
    assert MACAddressParameter().clean("123456-789abc") == "12:34:56:78:9A:BC"
    with pytest.raises(InterfaceTypeError):
        MACAddressParameter().clean("12-34-56-78-9A-BC-DE")
    with pytest.raises(InterfaceTypeError):
        MACAddressParameter().clean("AB-CD-EF-GH-HJ-KL")
    assert MACAddressParameter().clean("aabb-ccdd-eeff") == "AA:BB:CC:DD:EE:FF"
    assert MACAddressParameter().clean("aabbccddeeff") == "AA:BB:CC:DD:EE:FF"
    assert MACAddressParameter().clean("AABBCCDDEEFF") == "AA:BB:CC:DD:EE:FF"
    assert MACAddressParameter().clean("\xa8\xf9K\x80\xb4\xc0") == "A8:F9:4B:80:B4:C0"
    with pytest.raises(InterfaceTypeError):
        MACAddressParameter(accept_bin=False).clean("\\xa8\\xf9K\\x80\\xb4\\xc0")


def test_oid_parameter():
    assert OIDParameter().clean("1.3.6.1.2.1.1.1.0") == "1.3.6.1.2.1.1.1.0"
    assert OIDParameter(default="1.3.6.1.2.1.1.1.0").clean(None) == "1.3.6.1.2.1.1.1.0"
    with pytest.raises(InterfaceTypeError):
        OIDParameter().clean("1.3.6.1.2.1.1.X.0")


def test_rd_parameter():
    assert RDParameter().clean("100:4294967295") == "100:4294967295"
    assert RDParameter().clean("10.10.10.10:10") == "10.10.10.10:10"
    assert RDParameter().clean("100000:500") == "100000:500"
    assert RDParameter().clean("100000L:100") == "100000:100"


def test_geopoint_parameter():
    assert GeoPointParameter().clean([180, 90]) == [180, 90]
    assert GeoPointParameter().clean([75.5, "90"]) == [75.5, 90]
    assert GeoPointParameter().clean("[180, 85.5]") == [180, 85.5]
    with pytest.raises(InterfaceTypeError):
        GeoPointParameter().clean([1])


def test_tags_parameter():
    assert TagsParameter().clean([1, 2, "tags"]) == [u"1", u"2", u"tags"]
    assert TagsParameter().clean([1, 2, "tags "]) == [u"1", u"2", u"tags"]
    assert TagsParameter().clean("1,2,tags") == [u"1", u"2", u"tags"]
    assert TagsParameter().clean("1 , 2,  tags") == [u"1", u"2", u"tags"]
    with pytest.raises(InterfaceTypeError):
        TagsParameter().clean(1)


def test_color_parameter():
    assert ColorParameter(default=0xff).clean(None) == 0xff
    assert ColorParameter().clean("#ff0000") == 0xff0000
    with pytest.raises(InterfaceTypeError):
        ColorParameter().clean("#ff00000")
    with pytest.raises(InterfaceTypeError):
        ColorParameter().clean("#ff000x")


def test_object_id_parameter():
    assert ObjectIdParameter().clean("5b2d0cba4575cf01ead6aa89") == "5b2d0cba4575cf01ead6aa89"
    with pytest.raises(InterfaceTypeError):
        ObjectIdParameter().clean("5b2d0cba4575cf01ead6aa8x")
