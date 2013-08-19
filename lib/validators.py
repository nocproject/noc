# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data type validators
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import re
try:
    from django.forms import ValidationError
except:  # pragma: no cover
    pass

##
## Regular expressions
##
rx_fqdn = re.compile(r"^([a-z0-9\-]+\.)+[a-z0-9\-]+$", re.IGNORECASE)
rx_asset = re.compile(r"^AS-[A-Z0-9\-]+$")
rx_extension = re.compile(r"^\.[a-zA-Z0-9]+$")
rx_mimetype = re.compile(r"^[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+$")
rx_email = re.compile(r"^[a-z0-9._\-]+@([a-z0-9\-]+\.)+[a-z0-9\-]+$",
                      re.IGNORECASE)
rx_oid = re.compile(r"^(\d+\.){5,}\d+$")
rx_objectid = re.compile(r"^[0-9a-f]{24}$")


##
## Validators returning boolean
##
def is_int(v):
    """
    Check for valid integer

    >>> is_int(10)
    True
    >>> is_int("10")
    True
    >>> is_int("Ten")
    False
    >>> is_int(None)
    False
    """
    try:
        v = int(v)
    except ValueError:
        return False
    except TypeError:
        return False
    return True


def is_asn(v):
    """
    Check value is valid 2-byte or 4-byte autonomous system number

    >>> is_asn(100)
    True
    >>> is_asn(100000)
    True
    >>> is_asn(-1)
    False
    """
    try:
        v = long(v)
        return v > 0
    except ValueError:
        return False


def is_ipv4(v):
    """
    Check value is valid IPv4 address

    >>> is_ipv4("192.168.0.1")
    True
    >>> is_ipv4("192.168.0")
    False
    >>> is_ipv4("192.168.0.1.1")
    False
    >>> is_ipv4("192.168.1.256")
    False
    >>> is_ipv4("192.168.a.250")
    False
    """
    X = v.split(".")
    if len(X) != 4:
        return False
    try:
        return len([x for x in X if 0 <= int(x) <= 255]) == 4
    except:
        return False


def is_ipv6(v):
    """
    Check value is valid IPv6 address

    >>> is_ipv6("::")
    True
    >>> is_ipv6("::1")
    True
    >>> is_ipv6("2001:db8::")
    True
    >>> is_ipv6("2001:db8:0000:0000:6232:6400::")
    True
    >>> is_ipv6("::ffff:192.168.0.1")
    True
    >>> is_ipv6("::ffff:192.168.0.256")
    False
    >>> is_ipv6("fe80::226:b0ff:fef7:c48c")
    True
    >>> is_ipv6("0:1:2:3:4:5:6:7:8")
    False
    >>> is_ipv6("0:1:2")
    False
    >>> is_ipv6("::g")
    False
    >>> is_ipv6("100:0:")
    False
    >>> is_ipv6("2a00:1118:f00f:fffe:c143:3284:1000::")
    True
    """
    if v == "::":
        return True
    parts = v.split(":")
    if len(parts) != 8 and "::" not in v:
        return False
    if len(parts) == 9 and not parts[-1] and not parts[-2]:
        parts = parts[:-1]
    # Process IPv4 at the end
    if parts and "." in parts[-1]:
        if not is_ipv4(parts[-1]):
            return False
        p = [int(x) for x in parts[-1].split(".")]
        parts = (parts[:-1] +
                 ["%02x%02x" % (p[0], p[1]), "%02x%02x" % (p[2], p[3])])
    if len(parts) > 8:
        return False
    if len(parts) == 8:
        # Replace empty parts with "0"
        parts = [p if p else "0" for p in parts]
    else:
        # Expand ::
        try:
            i = parts.index("")
        except ValueError:
            return False
        h = []
        if i > 0:
            h = parts[:i]
        if i + 1 < len(parts) and not parts[i + 1]:
            i += 1
        t = parts[i + 1:]
        parts = h + ["0"] * (8 - len(h) - len(t)) + t
    # Check all parts
    try:
        for p in parts:
            int(p, 16)
    except ValueError:
        return False
    return True


def is_ipv4_prefix(v):
    """
    Check value is valid IPv4 prefix

    >>> is_ipv4_prefix("192.168.0.0")
    False
    >>> is_ipv4_prefix("192.168.0.0/16")
    True
    >>> is_ipv4_prefix("192.168.256.0/24")
    False
    >>> is_ipv4_prefix("192.168.0.0/g")
    False
    >>> is_ipv4_prefix("192.168.0.0/-1")
    False
    >>> is_ipv4_prefix("192.168.0.0/33")
    False
    """
    x = v.split("/")
    if len(x) != 2:
        return False
    if not is_ipv4(x[0]):
        return False
    try:
        y = int(x[1])
    except:
        return False
    return 0 <= y <= 32


is_cidr = is_ipv4_prefix


def is_ipv6_prefix(v):
    """
    Check value is valid IPv6 prefix

    >>> is_ipv6_prefix("1::/32")
    True
    >>> is_ipv6_prefix("1::/-1")
    False
    >>> is_ipv6_prefix("1::/129")
    False
    >>> is_ipv6_prefix("1::/1/2")
    False
    >>> is_ipv6_prefix("1::/g")
    False
    >>> is_ipv6_prefix("192.168.0.0/32")
    False
    """
    x = v.split("/")
    if len(x) != 2:
        return False
    if not is_ipv6(x[0]):
        return False
    try:
        y = int(x[1])
    except:
        return False
    return 0 <= y <= 128


def is_prefix(v):
    """
    Check value is valid IPv4 or IPv6 prefix

    >>> is_prefix("192.168.0.0/16")
    True
    >>> is_prefix("1::/32")
    True
    """
    return is_ipv4_prefix(v) or is_ipv6_prefix(v)


def is_rd(v):
    """
    Check value is valid Route Distinguisher

    Special case RD: 0:0
    >>> is_rd("0:0")
    True

    Type 0 RD: <2byte ASN> : <ID>

    >>> is_rd("100:10")
    True
    >>> is_rd("100:0")
    True
    >>> is_rd("100:4294967295")
    True
    >>> is_rd("0:-10")
    False
    >>> is_rd("0:4294967296")
    False

    Type 1 RD: <IPv4> : <ID>

    >>> is_rd("10.10.10.10:0")
    True
    >>> is_rd("10.10.10.10:65535")
    True
    >>> is_rd("10.10.10.10:-1")
    False
    >>> is_rd("10.10.10.10:65536")
    False

    Type 2 RD: <4byte ASN> : <ID>

    >>> is_rd("100000:0")
    True
    >>> is_rd("100000:65535")
    True

    Error handling

    >>> is_rd("100000:-1")
    False
    >>> is_rd("100000:65536")
    False
    >>> is_rd("10:20:30")
    False
    >>> is_rd("100:b")
    False
    """
    if v == "0:0":
        return True
    x = v.split(":")
    if len(x) != 2:
        return False
    a, b = x
    try:
        b = int(b)
    except ValueError:
        return False
    if is_asn(a):
        a = int(a)
        if a <= 65535:
            # Type 0 RD: <2byte ASN>: <ID>
            return 0 <= b <= 4294967295L
        # Type 2 RD: <4 byte ASN>: <ID>
        return 0 <= b <= 65535
    if is_ipv4(a):
        # Type 1 RD: <ipv4>:<ID>
        return 0 <= b <= 65535
    return False


def is_as_set(v):
    """
    Check value is valuid AS-SET

    >>> is_as_set("AS-TEST")
    True
    >>> is_as_set("AS100")
    False
    """
    return rx_asset.match(v) is not None


def is_fqdn(v):
    """
    Check value is valid FQDN

    >>> is_fqdn("test.example.com")
    True
    >>> is_fqdn("test")
    False
    """
    return rx_fqdn.match(v) is not None


def is_re(v):
    """
    Check value is valid regular expression

    >>> is_re("1{1,2}")
    True
    >>> is_re("1[")
    False
    """
    try:
        re.compile(v)
        return True
    except:
        return False


def is_vlan(v):
    """
    Check value is valid VLAN ID

    >>> is_vlan(1)
    True
    >>> is_vlan(-1)
    False
    >>> is_vlan(4095)
    True
    >>> is_vlan(4096)
    False
    >>> is_vlan("g")
    False
    """
    try:
        v = int(v)
        return 1 <= v <= 4095
    except:
        return False


def is_email(v):
    """
    Check value is valid email

    >>> is_email("test@example.com")
    True
    >>> is_email("test")
    False
    """
    return rx_email.match(v) is not None


def is_oid(v):
    """
    Check OID

    >>> is_oid("1.3.6.1.6.3.1.1.4.1.0")
    True
    >>> is_oid("1.3.6.1.6.3.1.1.4.a.1.0")
    False
    """
    return rx_oid.match(v) is not None


def is_extension(v):
    """
    Check value is file extension starting with dot

    >>> is_extension(".txt")
    True
    >>> is_extension("txt")
    False
    """
    return rx_extension.match(v) is not None


def is_mimetype(v):
    """
    Check value is MIME Type

    >>> is_mimetype("application/octet-stream")
    True
    >>> is_mimetype("application")
    False
    """
    return rx_mimetype.match(v) is not None


def is_objectid(v):
    """
    Check value is mongodb's ObjectId

    :param v:
    :return:
    """
    return rx_objectid.match(v) is not None


def generic_validator(check, error_message):
    """
    Validator factory

    >>> v = generic_validator(is_int, "invalid int")
    >>> v(6)
    6
    >>> v("g")
    Traceback (most recent call last):
    ...
    ValidationError: [u'invalid int']
    """
    # Validator closure
    def inner_validator(value, *args, **kwargs):
        if not check(value):
            raise ValidationError(error_message)
        return value
    return inner_validator

##
## Validators
##
check_asn = generic_validator(is_asn, "Invalid ASN")
check_prefix = generic_validator(is_prefix, "Invalid prefix")
check_ipv4 = generic_validator(is_ipv4, "Invalid IPv4")
check_ipv6 = generic_validator(is_ipv6, "Invalid IPv6")
check_ipv4_prefix = generic_validator(is_ipv4_prefix, "Invalid IPv4 prefix")
check_ipv6_prefix = generic_validator(is_ipv6_prefix, "Invalid IPv6 prefix")
check_cidr = generic_validator(is_cidr, "Invalid CIDR")
check_rd = generic_validator(is_rd, "Invalid RD")
check_fqdn = generic_validator(is_fqdn, "Invalid FQDN")
check_re = generic_validator(is_re, "Invalid Regular Expression")
check_as_set = generic_validator(is_as_set, "Invalid AS-SET")
check_re = generic_validator(is_re, "Invalid Regular Expression")
check_vlan = generic_validator(is_vlan, "Invalid VLAN")
check_email = generic_validator(is_email, "Invalid EMail")
check_extension = generic_validator(is_extension, "Invalid extension")
check_mimetype = generic_validator(is_mimetype, "Invalid MIME type")
