//---------------------------------------------------------------------
// sa.authprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.Application");

Ext.define("NOC.sa.authprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.authprofile.Model"
    ],
    model: "NOC.sa.authprofile.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 200
        },
        {
            text: __("Type"),
            dataIndex: "type",
            width: 100,
            renderer: NOC.render.Choices({
                G: "Local Group",
                R: "RADIUS",
                T: "TACACS+",
                L: "LDAP"
            })
        },
        {
            text: __("User"),
            dataIndex: "user",
            width: 100
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "type",
            xtype: "combobox",
            fieldLabel: __("Type"),
            allowBlank: false,
            store: [
                ["G", "Local Group"],
                ["R", "RADIUS"],
                ["T", "TACACS+"],
                ["L", "LDAP"]
            ]
        },
        {
            name: "user",
            xtype: "textfield",
            fieldLabel: __("User"),
            allowBlank: true
        },
        {
            name: "password",
            xtype: "textfield",
            inputType: "password",
            fieldLabel: __("Password"),
            allowBlank: true
        },
        {
            name: "super_password",
            xtype: "textfield",
            inputType: "password",
            fieldLabel: __("Super Password"),
            allowBlank: true
        },
        {
            name: "snmp_ro",
            xtype: "textfield",
            fieldLabel: __("RO Community"),
            allowBlank: true
        },
        {
            name: "snmp_rw",
            xtype: "textfield",
            fieldLabel: __("RW Community"),
            allowBlank: true
        }
    ]
});
