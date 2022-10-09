# ----------------------------------------------------------------------
# Access schemes constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Optional

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


CONFIGS = {
    1: ProtoConfig("telnet", is_cli=True, check="TELNET"),
    2: ProtoConfig("ssh", is_cli=True, check="SSH"),
    3: ProtoConfig("http", is_http=True, check="HTTP"),
    4: ProtoConfig("https", is_http=True, check="HTTPS"),
    5: ProtoConfig("beef", is_cli=True, enable_suggest=False),
    6: ProtoConfig("snmp_v1", snmp_version=0, check="SNMPv1"),
    7: ProtoConfig("snmp_v2c", snmp_version=1, check="SNMPv2c"),
    8: ProtoConfig("snmp_v3", snmp_version=3, enable_suggest=False),
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
