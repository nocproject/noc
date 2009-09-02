# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS IPsec classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,DROP_EVENT,Expression
from noc.fm.rules.classes.ipsec import *
from noc.fm.rules.classes.default import DROP

##
## Cisco.IOS IPsec Phase1 Tunnel Start SNMP
##
class Cisco_IOS_IPsec_Phase1_Tunnel_Start_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Phase1 Tunnel Start SNMP"
    event_class=IPsecPhase1TunnelStart
    preference=1000
    required_mibs=["CISCO-IPSEC-FLOW-MONITOR-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.2\.0\.1$"),   # cikeTunnelStart
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.2\.2\.1\.6\..*",r"^(?P<bin_local_ip>....)"),  # cikePeerLocalAddr
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.2\.2\.1\.7\..*",r"^(?P<bin_remote_ip>....)"), # cikePeerRemoteAddr
        Expression("local_ip","decode_ipv4(bin_local_ip)"),
        Expression("remote_ip","decode_ipv4(bin_remote_ip)"),
    ]
##
## Cisco.IOS IPsec Phase1 Tunnel Stop SNMP
##
class Cisco_IOS_IPsec_Phase1_Tunnel_Stop_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Phase1 Tunnel Stop SNMP"
    event_class=IPsecPhase1TunnelStop
    preference=1000
    required_mibs=["CISCO-IPSEC-FLOW-MONITOR-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.2\.0\.2$"),   # cikeTunnelStop
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.2\.2\.1\.6\..*",r"^(?P<bin_local_ip>....)"),  # cikePeerLocalAddr
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.2\.2\.1\.7\..*",r"^(?P<bin_remote_ip>....)"), # cikePeerRemoteAddr
        Expression("local_ip","decode_ipv4(bin_local_ip)"),
        Expression("remote_ip","decode_ipv4(bin_remote_ip)"),
    ]
##
## Cisco.IOS IPsec Phase2 Tunnel Start SNMP
##
class Cisco_IOS_IPsec_Phase2_Tunnel_Start_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Phase2 Tunnel Start SNMP"
    event_class=IPsecPhase2TunnelStart
    preference=1000
    required_mibs=["CISCO-IPSEC-FLOW-MONITOR-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.2\.0\.7$"),      # cipSecTunnelStart
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.3\.3\.1\.10\.",r"(?P<bin_remote_ip>....)"),      # cipSecEndPtRemoteAddr1
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.3\.3\.1\.4\.",r"(?P<bin_local_ip>....)"),        # cipSecEndPtLocalAddr1
        Expression("local_ip","decode_ipv4(bin_local_ip)"),
        Expression("remote_ip","decode_ipv4(bin_remote_ip)"),
    ]
##
## Cisco.IOS IPsec Phase2 Tunnel Stop SNMP
##
class Cisco_IOS_IPsec_Phase2_Tunnel_Stop_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Phase2 Tunnel Stop SNMP"
    event_class=IPsecPhase2TunnelStop
    preference=1000
    required_mibs=["CISCO-IPSEC-FLOW-MONITOR-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.2\.0\.8$"),      # cipSecTunnelStop
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.4\.3\.2\.1\.12\.\d+",r"(?P<bin_remote_ip>....)"),# cipSecEndPtHistRemoteAddr1
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.171\.1\.4\.3\.2\.1\.6\.\d+",r"(?P<bin_local_ip>....)"),  # cipSecEndPtHistLocalAddr1
        Expression("local_ip","decode_ipv4(bin_local_ip)"),
        Expression("remote_ip","decode_ipv4(bin_remote_ip)"),
    ]
##
## Cisco.IOS IPsec Crypto Map Added SNMP
##
class Cisco_IOS_IPsec_Crypto_Map_Added_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Crypto Map Added SNMP"
    event_class=DROP
    preference=1000
    action=DROP_EVENT
    required_mibs=["CISCO-IPSEC-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.10\.62\.2\.0\.3$"), # cipsCryptomapAdded
        (r"^profile$",r"^Cisco\.IOS$"),
    ]

##
## Cisco.IOS IPsec Crypto Map Deleted SNMP
##
class Cisco_IOS_IPsec_Crypto_Map_Deleted_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Crypto Map Deleted SNMP"
    event_class=DROP
    preference=1000
    action=DROP_EVENT
    required_mibs=["CISCO-IPSEC-MIB"]
    patterns=[
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.10\.62\.2\.0\.4$"), # cipsCryptomapDeleted
        (r"^profile$",r"^Cisco\.IOS$"),
    ]
##
## Cisco.IOS IPsec Invalid SPI SYSLOG
##
class Cisco_IOS_IPsec_Invalid_SPI_SYSLOG_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Invalid SPI SYSLOG"
    event_class=IPsecInvalidSPI
    preference=1000
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^syslog$"),
        (r"^severity$",r"^4$"),
        (r"^message$",r"%CRYPTO-4-RECVD_PKT_INV_SPI: decaps: rec'd IPSEC packet has invalid spi for destaddr=(?P<dst_ip>.+), prot=50, spi=.*, srcaddr=(?P<src_ip>\S+)$"),
    ]
##
## Cisco.IOS IPsec Invalid SPI SYSLOG SNMP
##
class Cisco_IOS_IPsec_Invalid_SPI_SYSLOG_SNMP_Rule(ClassificationRule):
    name="Cisco.IOS IPsec Invalid SPI SYSLOG SNMP"
    event_class=IPsecInvalidSPI
    preference=1000
    required_mibs=["CISCO-SYSLOG-MIB"]
    patterns=[
        (r"^profile$",r"^Cisco\.IOS$"),
        (r"^source$",r"^SNMP Trap$"),
        (r"^1\.3\.6\.1\.6\.3\.1\.1\.4\.1\.0$",r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.2\.0\.1$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.2\.\d+$",r"^CRYPTO$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.4\.\d+$",r"^RECVD_PKT_INV_SPI$"),
        (r"^1\.3\.6\.1\.4\.1\.9\.9\.41\.1\.2\.3\.1\.5\.\d+$",r"^decaps: rec'd IPSEC packet has invalid spi for destaddr=(?P<dst_ip>\S+), prot=50, spi=.+, srcaddr=(?P<src_ip>\S+)$"),
    ]
