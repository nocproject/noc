# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS DHCP rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.dhcp import *
##
## Cisco.IOS DHCPD Address Conflict SYSLOG
##
class Cisco_IOS_DHCPD_Address_Conflict_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS DHCPD Address Conflict SYSLOG"
    event_class=DHCPDAddressConflict
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^severity$",r"^4$"),
        (r"^source$",r"^syslog$"),
        (r"^message$",r"%DHCPD-4-PING_CONFLICT: DHCP address conflict:  server pinged (?P<ip>\S+)\.$"),
    ]
##
## Cisco.IOS DHCPD Address Conflict SYSLOG SNMP
##
class Cisco_IOS_DHCPD_Address_Conflict_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS DHCPD Address Conflict SYSLOG SNMP"
    event_class=DHCPDAddressConflict
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"(?P<ip>\S+)\.$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^PING_CONFLICT$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^DHCPD$"),
    ]
