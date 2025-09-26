# ----------------------------------------------------------------------
# Variable types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Optional, Any

# Third-party modules
from pydantic import BaseModel, HttpUrl, ValidationError

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
from noc.core.validators import is_fqdn

BOOL_VALUES = frozenset(("t", "true", "yes"))
REFERENCE_SCOPE_SPLITTER = "::"


class HTTPURLModel(BaseModel):
    url: HttpUrl

    @classmethod
    def normalize(cls, value) -> "HttpUrl":
        """https://xxxx"""
        return HTTPURLModel(url=value)


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
    HTTP_URL = "http_url"

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
    def decode_http_url(value):
        if is_fqdn(value):
            value = f"http://{value}"
        try:
            HTTPURLModel(url=value)
            return value
        except ValidationError as e:
            raise ValueError(str(e))

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

    def clean_reference(self, value: Any, scope: Optional[str] = None) -> Optional[str]:
        """Generate References string for instance"""
        match self:
            case ValueType.MAC_ADDRESS:
                scope = "mac"
            case ValueType.HTTP_URL:
                scope = "url"
                value = str(HTTPURLModel(url=value).url)
        if scope:
            return f"{scope}{REFERENCE_SCOPE_SPLITTER}{value}"
        return None

    @property
    def resource_model(self) -> Optional[str]:
        match self:
            case ValueType.IFACE_NAME:
                return "inv.Interface"
        return None
