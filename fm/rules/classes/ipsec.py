# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IPsec Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## IPsec Phase1 Tunnel Start
##
class IPsecPhase1TunnelStart(EventClass):
    name     = "IPsec Phase1 Tunnel Start"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="IPsec Phase1 Tunnel Start: {{local_ip}} - {{remote_ip}}"
    body_template="""IPsec Phase1 Tunnel Start:
{{local_ip}} - {{remote_ip}}"""
    class Vars:
        local_ip=Var(required=True)
        remote_ip=Var(required=True)
##
## IPsec Phase1 Tunnel Stop
##
class IPsecPhase1TunnelStop(EventClass):
    name     = "IPsec Phase1 Tunnel Stop"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="IPsec Phase1 Tunnel Stop: {{local_ip}} - {{remote_ip}}"
    body_template="""IPsec Phase1 Tunnel Stop:
{{local_ip}} - {{remote_ip}}"""
    class Vars:
        local_ip=Var(required=True)
        remote_ip=Var(required=True)
#
#class IPsecPhase1NoSA(EventClass):
#    pass
##
## IPsec Phase2 Tunnel Start
##
class IPsecPhase2TunnelStart(EventClass):
    name     = "IPsec Phase2 Tunnel Start"
    category = "NETWORK"
    priority = "NORMAL"
    subject_template="IPsec Phase2 Tunnel Start: {{local_ip}} - {{remote_ip}}"
    body_template="""IPsec Phase2 Tunnel Start:
{{local_ip}} - {{remote_ip}}"""
    class Vars:
        local_ip=Var(required=True)
        remote_ip=Var(required=True)
##
## IPsec Phase2 Tunnel Stop
##
class IPsecPhase2TunnelStop(EventClass):
    name     = "IPsec Phase2 Tunnel Stop"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="IPsec Phase2 Tunnel Stop: {{local_ip}} - {{remote_ip}}"
    body_template="""IPsec Phase2 Tunnel Stop:
{{local_ip}} - {{remote_ip}}"""
    class Vars:
        local_ip=Var(required=True)
        remote_ip=Var(required=True)
#
#class IPsecPhase2NoSA(EventClass):
#    pass
#
##
## IPsec Invalid SPI
##
class IPsecInvalidSPI(EventClass):
    name     = "IPsec Invalid SPI"
    category = "NETWORK"
    priority = "MAJOR"
    subject_template="IPsec Invalid packet SPI: {{src_ip}} - {{dst_ip}}"
    body_template="""IPsec Invalid packet SPI:
{{src_ip}} - {{dst_ip}}"""
    class Vars:
        src_ip=Var(required=True)
        dst_ip=Var(required=True)
