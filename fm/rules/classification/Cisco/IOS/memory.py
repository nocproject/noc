# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco IOS specific memory-related rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule
from noc.fm.rules.classes.memory import *
##
## Cisco.IOS Memory Allocation Failed SYSLOG
##
class Cisco_IOS_Memory_Allocation_Failed_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS Memory Allocation Failed SYSLOG"
    event_class=MemoryAllocationError
    preference=1000
    patterns=[
        (r"^source$",r"^syslog$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^message$",r"%SYS-2-(?:MALLOCFAIL|CHUNKEXPANDFAIL)"),
    ]
##
## Cisco.IOS Memory Allocation Failed SYSLOG SNMP
##
class Cisco_IOS_Memory_Allocation_Failed_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS Memory Allocation Failed SYSLOG SNMP"
    event_class=MemoryAllocationError
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^SYS$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^(?:CHUNKEXPANDFAIL|MALLOCFAIL)$"),
    ]
