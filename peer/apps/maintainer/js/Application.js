//---------------------------------------------------------------------
// peer.maintainer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.maintainer.Application");

Ext.define("NOC.peer.maintainer.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.maintainer.Model",
        "NOC.peer.person.LookupField",
        "NOC.peer.person.M2MField",
        "NOC.peer.rir.LookupField"
    ],
    model: "NOC.peer.maintainer.Model",
    search: true,
    columns: [
        {
            text: "Maintainer",
            dataIndex: "maintainer",
            flex: 1
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "RIR",
            dataIndex: "rir",
            renderer: NOC.render.Lookup("rir"),
            flex: 1
        }
    ],
    fields: [
        {
            name: "maintainer",
            xtype: "textfield",
            fieldLabel: "Maintainer",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: false
        },
        {
            name: "password",
            xtype: "textfield",
            fieldLabel: "Password",
            allowBlank: true
        },
        {
            name: "rir",
            xtype: "peer.rir.LookupField",
            fieldLabel: "RIR",
            allowBlank: false
        },
        {
            xtype: "peer.person.M2MField",
            name: "admins",
            height: 220,
            width: 600,
            fieldLabel: "Admin-c",
            buttons: ['add', 'remove'],
            allowBlank: false
        },
        {
            name: "extra",
            xtype: "textareafield",
            fieldLabel: "Extra",
            allowBlank: true,
            width: 600, 
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        }
    ]
});
