//---------------------------------------------------------------------
// main.stompaccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.stompaccess.Application");

Ext.define("NOC.main.stompaccess.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.stompaccess.Model",
        "NOC.main.prefixtable.LookupField"
    ],
    model: "NOC.main.stompaccess.Model",
    columns: [
        {
            text: "User",
            dataIndex: "user",
            width: 100
        },
        {
            text: "Act.",
            dataIndex: "is_active",
            width: 25,
            renderer: NOC.render.Bool
        },
        {
            text: "Prefix Table",
            dataIndex: "prefix_table",
            flex: 1,
            renderer: NOC.render.Lookup("prefix_table")
        }
    ],
    fields: [
        {
            name: "user",
            fieldLabel: "STOMP User",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "password",
            fieldLabel: "STOMP Password",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "is_active",
            boxLabel: "Active",
            xtype: "checkboxfield"
        },
        {
            name: "prefix_table",
            fieldLabel: "Prefix Table",
            xtype: "main.prefixtable.LookupField"
        }
    ]
});
