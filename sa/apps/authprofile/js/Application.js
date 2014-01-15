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
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Type",
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
            text: "User",
            dataIndex: "user",
            width: 100
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
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "type",
            xtype: "combobox",
            fieldLabel: "Type",
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
            fieldLabel: "User",
            allowBlank: true
        },
        {
            name: "password",
            xtype: "textfield",
            fieldLabel: "Password",
            allowBlank: true
        },
        {
            name: "super_password",
            xtype: "textfield",
            fieldLabel: "Super Password",
            allowBlank: true
        },
        {
            name: "snmp_ro",
            xtype: "textfield",
            fieldLabel: "RO Community",
            allowBlank: true
        },
        {
            name: "snmp_rw",
            xtype: "textfield",
            fieldLabel: "RW Community",
            allowBlank: true
        }
    ]
});
