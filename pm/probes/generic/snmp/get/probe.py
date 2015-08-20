## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic SNMP Get
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric


class SNMPGetProbe(Probe):
    TITLE = "SNMP Get"
    DESCRIPTION = "Generic SNMP Get"
    TAGS = ["snmp"]
    CONFIG_FORM = [
        {
            "xtype": "container",
            "layout": "hbox",
            "items": [
                {
                    "name": "address",
                    "xtype": "textfield",
                    "fieldLabel": "Address",
                    "allowBlank": False
                },
                {
                    "name": "snmp__ro",
                    "xtype": "textfield",
                    "fieldLabel": "SNMP Community",
                    "allowBlank": False
                }
            ]
        },
        {
            "name": "oid",
            "xtype": "textfield",
            "fieldLabel": "OID",
            "allowBlank": False
        },
        {
            "xtype": "container",
            "layout": "hbox",
            "items": [
                {
                    "name": "convert",
                    "xtype": "combobox",
                    "fieldLabel": "Convert",
                    "allowBlank": True,
                    "store": [
                        ["none", "none"],
                        ["counter", "counter"],
                        ["derive", "derive"]
                    ]
                },
                {
                    "name": "scale",
                    "xtype": "numberfield",
                    "fieldLabel": "Scale",
                    "allowBlank": True
                }
            ]
        }
    ]

    @metric(["Custom | SNMP | OID"],
            convert=metric.NONE,
            preference=metric.PREF_COMMON)
    def get_oid(self, address, snmp__ro, oid,
                convert=metric.NONE, scale=1.0):
        self.set_convert("Custom | SNMP | OID",
                         convert=convert, scale=float(scale))
        r = yield self.snmp_get(oid, address, community=snmp__ro)
        self.return_result(r)
