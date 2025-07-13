# ----------------------------------------------------------------------
# Variable types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Optional, Any

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

BOOL_VALUES = frozenset(("t", "true", "yes"))


class ValueType(enum.Enum):
    """
    Source for setting data item
    """

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOL = "bool"
    IPV4_ADDR = "ipv4_address"
    IPV6_ADDR = "ipv6_address"
    IP_ADDR = "ip_address"
    IPV4_PREFIX = "ipv4_prefix"
    IPV6_PREFIX = "ipv6_prefix"
    IP_PREFIX = "ip_prefix"
    MAC_ADDRESS = "mac"
    IFACE_NAME = "interface_name"
    SNMP_OID = "oid"

    def get_default(self, value):
        match self.value:
            case "str":
                return ""
            case "int":
                return 0
            case "float":
                return 0.0
        return None

    @staticmethod
    def decode_str(value):
        return value

    @staticmethod
    def decode_int(value):
        if value is not None:
            try:
                return int(value)
            except ValueError:
                pass
        return 0

    @staticmethod
    def decode_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in BOOL_VALUES
        return bool(value)

    @staticmethod
    def decode_float(value):
        if value is not None:
            try:
                return float(value)
            except ValueError:
                pass
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

    @staticmethod
    def decode_interface_name(value):
        return value

    def clean_value(self, value, errors: str = "strict"):
        decoder = getattr(self, f"decode_{self.value}")
        try:
            return decoder(value)
        except ValueError as e:
            if errors != "strict":
                return self.get_default(value)
            raise e

    def clean_reference(self, value: Any) -> Optional[str]:
        """Generate References string for instance"""
        match self:
            case ValueType.MAC_ADDRESS:
                return f"mac:{value}"
        return None
