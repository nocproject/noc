//---------------------------------------------------------------------
// pm.probe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.probe.Application");

Ext.define("NOC.pm.probe.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.probe.Model",
        "NOC.main.user.LookupField"
    ],
    model: "NOC.pm.probe.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Credentials",
            dataIndex: "user",
            flex: 1,
            renderer: NOC.render.Lookup("user")
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            allowBlank: false,
            fieldLabel: "Name",
            regex: /^[0-9a-zA-Z\-_\.]+$/
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "user",
            xtype: "main.user.LookupField",
            fieldLabel: "Credentials"
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
