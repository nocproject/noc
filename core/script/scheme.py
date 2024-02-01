# ----------------------------------------------------------------------
# Access schemes constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Optional, List, Literal, Any

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
class ProtoConfig(object):
    alias: str
    check: Optional[str] = None
    snmp_version: Optional[int] = None
    is_http: bool = False
    is_cli: bool = False
    enable_suggest: bool = True
    credential: Optional[Any] = None


@dataclass(frozen=True)
class SNMPCredential(object):
    snmp_ro: str = None
    snmp_rw: Optional[str] = None
    oids: Optional[List[str]] = None


@dataclass(frozen=True)
class SNMPv3Credential(object):
    username: str
    context: Optional[str] = None
    auth_key: Optional[str] = None
    snmp_auth_proto: Literal["MD5", "SHA"] = "MD5"
    private_key: Optional[str] = None
    private_proto: Literal["DES", "AES"] = "DES"
    oids: Optional[List[str]] = None


@dataclass(frozen=True)
class CLICredential(object):
    username: str
    password: Optional[str] = None
    super_password: Optional[str] = None


@dataclass
class HTTPCredential(object):
    username: str
    password: Optional[str] = None


CONFIGS = {
    1: ProtoConfig("telnet", is_cli=True, check="TELNET", credential=CLICredential),
    2: ProtoConfig("ssh", is_cli=True, check="SSH", credential=CLICredential),
    3: ProtoConfig("http", is_http=True, check="HTTP", credential=HTTPCredential),
    4: ProtoConfig("https", is_http=True, check="HTTPS", credential=HTTPCredential),
    5: ProtoConfig("beef", is_cli=True, enable_suggest=False),
    6: ProtoConfig("snmp_v1", snmp_version=0, check="SNMPv1", credential=SNMPCredential),
    7: ProtoConfig("snmp_v2c", snmp_version=1, check="SNMPv2c", credential=SNMPCredential),
    8: ProtoConfig("snmp_v3", snmp_version=3, enable_suggest=False, credential=SNMPv3Credential),
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
