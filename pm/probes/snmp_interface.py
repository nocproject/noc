# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP IF-MIB probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.pm.probes.snmp import SNMPProbe

##
##
##
class SNMPInterfaceProbe(SNMPProbe):
    name="snmp-interface"
    parameters={
        "{{ifname}}_in_bandwidth" :    {
            "oid"   : "1.3.6.1.2.1.2.2.1.10.{{ifindex}}",
            "type"  : "counter",
            "scale" : 8,
        },
        "{{ifname}}_out_bandwidth" :   {
            "oid"   : "1.3.6.1.2.1.2.2.1.16.{{ifindex}}",
            "type"  : "counter",
            "scale" : 8,
        },
        "{{ifname}}_in_discards" :  {
            "oid"       : "1.3.6.1.2.1.2.2.1.13.{{ifindex}}",
            "type"      : "counter",
            "threshold" : {
                "warn"  : { "high" : 1},
                "fail"  : { "high" : 5}
            }
        },
        "{{ifname}}_out_discards" : {
            "oid"       : "1.3.6.1.2.1.2.2.1.19.{{ifindex}}",
            "type"      : "counter",
            "threshold" : {
                "warn"  : { "high" : 1},
                "fail"  : { "high" : 5}
            }
        },
        "{{ifname}}_in_errors" :  {
            "oid"       : "1.3.6.1.2.1.2.2.1.14.{{ifindex}}",
            "type"      : "counter",
            "threshold" : {
                "warn"  : { "high" : 1},
                "fail"  : { "high" : 5}
            }
        },
        "{{ifname}}_in_errors" :  {
            "oid"       : "1.3.6.1.2.1.2.2.1.20.{{ifindex}}",
            "type"      : "counter",
            "threshold" : {
                "warn"  : { "high" : 1},
                "fail"  : { "high" : 5}
            }
        },
        "{{ifname}}_admin_status" :  {
            "oid"  : "1.3.6.1.2.1.2.2.1.7.{{ifindex}}",
            "type" : "gauge",
        },
        "{{ifname}}_oper_status" :  {
            "oid"  : "1.3.6.1.2.1.2.2.1.8.{{ifindex}}",
            "type" : "gauge",
        },
    }
