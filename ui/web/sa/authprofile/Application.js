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
                L: "LDAP",
                S: "Suggest"
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
                ["L", "LDAP"],
                ["S", "Suggest"]
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
    ],
    inlines: [
        {
            title: __("Suggest SNMP"),
            model: "NOC.sa.authprofile.SuggestSNMPModel",
            columns: [
                {
                    text: __("SNMP RO"),
                    dataIndex: "snmp_ro",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: __("SNMP RW"),
                    dataIndex: "snmp_rw",
                    editor: "textfield",
                    flex: 1
                }
            ]
        },
        {
            title: __("Suggest CLI"),
            model: "NOC.sa.authprofile.SuggestCLIModel",
            columns: [
                {
                    text: __("User"),
                    dataIndex: "user",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: __("Password"),
                    dataIndex: "password",
                    width: 200,
                    editor: "textfield"
                },
                {
                    text: __("Super Password"),
                    dataIndex: "super_password",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        }
    ]
});
