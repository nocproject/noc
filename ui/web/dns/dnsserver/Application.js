//---------------------------------------------------------------------
// dns.dnsserver application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnsserver.Application");

Ext.define("NOC.dns.dnsserver.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.dns.dnsserver.Model",
        "NOC.main.sync.LookupField"
    ],
    model: "NOC.dns.dnsserver.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 100
        },
        {
            text: "IP",
            dataIndex: "ip",
            width: 100
        },
        {
            text: "Sync",
            dataIndex: "sync",
            renderer: NOC.render.Lookup("sync"),
            width: 150
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
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
            name: "sync",
            xtype: "main.sync.LookupField",
            fieldLabel: "Sync channel",
            allowBlank: true
        }
    ]
});
