# ----------------------------------------------------------------------
# Variable types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum

# NOC modules
from noc.sa.interfaces.base import (
    IPv4Parameter,
    IPv6Parameter,
    IPParameter,
    PrefixParameter,
    IPv4PrefixParameter,
    IPv6PrefixParameter,
    MACAddressParameter,
    OIDParameter,
)


class ValueType(enum.Enum):
    """
    Source for setting data item
    """

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    IPV4_ADDR = "ipv4_address"
    IPV6_ADDR = "ipv6_address"
    IP_ADDR = "ip_address"
    IPV4_PREFIX = "ipv4_prefix"
    IPV6_PREFIX = "ipv6_prefix"
    IP_PREFIX = "ip_prefix"
    MAC_ADDRESS = "mac"
    IFACE_NAME = "interface_name"
    SNMP_OID = "oid"

    @staticmethod
    def decode_str(value):
        return value

    @staticmethod
    def decode_int(value):
        if value is not None and value.isdigit():
            return int(value)
        return 0

    @staticmethod
    def decode_ipv4_address(value):
        return IPv4Parameter().clean(value)

    @staticmethod
    def decode_ipv6_address(value):
        return IPv6Parameter().clean(value)

    @staticmethod
    def decode_ip_address(value):
        return IPParameter().clean(value)

    @staticmethod
    def decode_ipv4_prefix(value):
        return IPv4PrefixParameter().clean(value)

    @staticmethod
    def decode_ipv6_prefix(value):
        return IPv6PrefixParameter().clean(value)

    @staticmethod
    def decode_ip_prefix(value):
        return PrefixParameter().clean(value)

    @staticmethod
    def decode_mac(value):
        return MACAddressParameter().clean(value)

    @staticmethod
    def decode_oid(value):
        return OIDParameter().clean(value)

    def clean_value(self, value):
        decoder = getattr(self, f"decode_{self.value}")
        return decoder(value)
