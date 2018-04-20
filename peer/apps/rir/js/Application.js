//---------------------------------------------------------------------
// peer.rir application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.rir.Application");

Ext.define("NOC.peer.rir.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.peer.rir.Model"],
    model: "NOC.peer.rir.Model",
    columns: [
        {
            text: "RIR",
            dataIndex: "name"
        },
        
        {
            text: "whois",
            dataIndex: "whois"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "name",
            allowBlank: false
        },
        {
            name: "whois",
            xtype: "textfield",
            fieldLabel: "whois",
            allowBlank: true
        }
    ]
});
