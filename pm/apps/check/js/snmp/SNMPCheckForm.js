//---------------------------------------------------------------------
// SNMPCheckForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.snmp.SNMPCheckForm");

Ext.define("NOC.pm.check.snmp.SNMPCheckForm", {
    extend: "Ext.form.Panel",
    items: [
        {
            name: "address",
            fieldLabel: "Address",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "port",
            fieldLabel: "Port",
            xtype: "numberfield",
            allowBlank: false,
            value: 161
        },
        {
            name: "community",
            fieldLabel: "Community",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "oid",
            fieldLabel: "OID",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "timeout",
            fieldLabel: "Timeout",
            xtype: "numberfield",
            allowBlank: false,
            value: 10
        }
    ]
});
