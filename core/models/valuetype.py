# ----------------------------------------------------------------------
# Variable types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Optional, Any, List, Annotated

# Third-party modules
from pydantic import BaseModel, HttpUrl, ValidationError, StringConstraints, field_validator

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
    VLANIDParameter,
)
from noc.core.validators import is_fqdn
from noc.models import get_model, is_document

BOOL_VALUES = frozenset(("t", "true", "yes", "on"))
REFERENCE_SCOPE_SPLITTER = "::"
ARRAY_ANNEX = "**"
ARRAY_DELIMITER = " | "
DomainName = Annotated[
    str,
    StringConstraints(
        pattern=r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9].?$"
    ),
]
# HOSTNAME = Annotated[
#     str,
#     StringConstraints(
#         pattern=r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63}(?<!-))*$"
#     ),
# ]


class HTTPURLModel(BaseModel):
    url: HttpUrl

    @classmethod
    def normalize(cls, value) -> "HttpUrl":
        """https://xxxx"""
        return HTTPURLModel(url=value)


class HostNameModel(BaseModel):
    hostname: str

    @field_validator("hostname")
    def validate_hostname(cls, v):
        if not all(c.isalnum() or c in {"-", "."} for c in v):
            raise ValueError("Hostname contains invalid characters.")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Hostname cannot start or end with a hyphen.")
        # Add more complex validation rules as needed
        return v

    @classmethod
    def normalize(cls, value) -> "HttpUrl":
        """https://xxxx"""
        return HostNameModel(hostname=value)


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
    SERIAL_NUM = "serial_num"
    VLAN = "vlan"
    IP_VRF = "vrf"
    HOSTNAME = "hostname"

    @property
    def is_logical(self):
        """Check type is boolean"""
        return self == ValueType.BOOL

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
            HTTPURLModel.normalize(value)
            return value
        except ValidationError as e:
            raise ValueError(str(e))

    @staticmethod
    def decode_interface_name(value):
        return value

    @staticmethod
    def decode_vlan(value):
        return VLANIDParameter().clean(value)

    @staticmethod
    def decode_vrf(value):
        if hasattr(value, "name"):
            return str(value.name)
        return str(value)

    @staticmethod
    def decode_serial_num(value):
        """Check"""
        return str(value.strip())

    @staticmethod
    def decode_hostname(value):
        try:
            HostNameModel.normalize(value)
            return value
        except ValidationError as e:
            raise ValueError(str(e))
        except ValueError as e:
            raise e

    @staticmethod
    def convert_from_array(value: Any) -> str:
        """Convert from strint to array"""
        return f"{ARRAY_ANNEX}{ARRAY_DELIMITER.join([str(v) for v in value])}"

    @staticmethod
    def convert_to_array(value: str) -> List[str]:
        """Convert array to string"""
        return [v.strip() for v in value.split(ARRAY_DELIMITER)]

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
            case ValueType.SERIAL_NUM:
                scope = "sn"
            case ValueType.HOSTNAME:
                scope = "hostname"
                value = value.lower()
        if scope:
            return f"{scope}{REFERENCE_SCOPE_SPLITTER}{value}"
        return None

    @property
    def resource_model(self) -> Optional[str]:
        match self:
            case ValueType.IFACE_NAME:
                return "inv.Interface"
            case ValueType.VLAN:
                return "vc.VLAN"
            case ValueType.IP_VRF:
                return "ip.VRF"
            case ValueType.IPV4_ADDR:
                return "ip.Address"
        return None

    def get_resource_instance(self) -> Optional[Any]:
        """Getting resource instance"""
        m = self.resource_model
        if not m:
            raise AttributeError("Not resource model")
        m = get_model(m)
        # Get component?
        if is_document(m) or isinstance(self.value, int):
            return m.get_by_id(self.value)
        if isinstance(self.value, str) and self.value.isdigit():
            return m.get_by_id(int(self.value))
        return m.get_by_name(self.value)
