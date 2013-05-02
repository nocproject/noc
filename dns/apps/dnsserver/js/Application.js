//---------------------------------------------------------------------
// dns.dnsserver application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnsserver.Application");

Ext.define("NOC.dns.dnsserver.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.dns.dnsserver.Model"
    ],
    model: "NOC.dns.dnsserver.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "IP",
            dataIndex: "ip"
        },
        {
            text: "Channel",
            dataIndex: "sync_channel"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "ip",
            xtype: "textfield",
            fieldLabel: "IP",
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "sync_channel",
            xtype: "textfield",
            fieldLabel: "Sync channel",
            allowBlank: true,
            regex: /^[a-zA-Z0-9]+$/
        }
    ]
});
