# ----------------------------------------------------------------------
# Access schemes constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass, field
from typing import Literal, Any

TELNET = 1
SSH = 2
HTTP = 3
HTTPS = 4
BEEF = 5

SCHEME_CHOICES = [
    (TELNET, "telnet"),
    (SSH, "ssh"),
    (HTTP, "http"),
    (HTTPS, "https"),
    (BEEF, "beef"),
]

PROTOCOLS = {TELNET: "telnet", SSH: "ssh", HTTP: "http", HTTPS: "https", BEEF: "beef"}

CLI_PROTOCOLS = {TELNET, SSH, BEEF}
HTTP_PROTOCOLS = {HTTP, HTTPS}


@dataclass(frozen=True)
class ProtoConfig:
    alias: str
    check: str | None = None
    snmp_version: int | None = None
    is_http: bool = False
    is_cli: bool = False
    enable_suggest: bool = True
    credential: Any | None = None


@dataclass(frozen=True)
class SNMPCredential:
    snmp_ro: str
    snmp_rw: str | None = field(default=None, hash=True)
    oids: list[str] | None = field(default=None, hash=False)
    snmp_v1_only: bool = field(default=False, hash=False)

    @property
    def protocol(self) -> "Protocol":
        if self.snmp_v1_only:
            return Protocol(6)
        return Protocol(7)

    @property
    def security_level(self):
        return "Community"


@dataclass(frozen=True)
class SNMPv3Credential:
    username: str
    context: str | None = None
    auth_key: str | None = None
    auth_proto: Literal["MD5", "SHA"] = "MD5"
    private_key: str | None = None
    private_proto: Literal["DES", "AES"] = "DES"
    oids: list[str] | None = field(default=None, hash=False)

    @property
    def protocol(self) -> "Protocol":
        return Protocol(8)

    @property
    def security_level(self):
        if self.auth_key and self.private_key:
            return "authPriv"
        if self.auth_key:
            return "authNoPriv"
        return "noAuthNoPriv"


@dataclass(frozen=True)
class CLICredential:
    username: str
    password: str | None = None
    super_password: str | None = None
    raise_privilege: bool = False
    enable_protocols: tuple[int, ...] = (1, 2)

    @property
    def protocol(self) -> "Protocol":
        return Protocol(self.enable_protocols[0])

    @property
    def user(self):
        return self.username


@dataclass
class HTTPCredential:
    username: str  # api_key, username
    password: str | None = None
    http_only: bool = True

    @property
    def protocol(self) -> "Protocol":
        if self.http_only:
            return Protocol(3)
        return Protocol(4)


CONFIGS = {
    1: ProtoConfig("telnet", is_cli=True, check="TELNET", credential=CLICredential),
    2: ProtoConfig("ssh", is_cli=True, check="SSH", credential=CLICredential),
    3: ProtoConfig("http", is_http=True, check="HTTP", credential=HTTPCredential),
    4: ProtoConfig("https", is_http=True, check="HTTPS", credential=HTTPCredential),
    5: ProtoConfig("beef", is_cli=True, enable_suggest=False),
    6: ProtoConfig("snmp_v1", snmp_version=0, check="SNMPv1", credential=SNMPCredential),
    7: ProtoConfig("snmp_v2c", snmp_version=1, check="SNMPv2c", credential=SNMPCredential),
    8: ProtoConfig("snmp_v3", snmp_version=3, check="SNMPv3", credential=SNMPv3Credential),
}


class Protocol(enum.Enum):
    @property
    def config(self):
        return CONFIGS[self.value]

    TELNET = 1
    SSH = 2
    HTTP = 3
    HTTPS = 4
    BEEF = 5
    SNMPv1 = 6
    SNMPv2c = 7
    SNMPv3 = 8
