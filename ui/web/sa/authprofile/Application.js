//---------------------------------------------------------------------
// sa.authprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.Application");

Ext.define("NOC.sa.authprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.authprofile.Model",
        "NOC.main.remotesystem.LookupField",
        "NOC.core.PasswordField"
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
            xtype: "password",
            fieldLabel: __("Password"),
            uiStyle: "large",
            allowBlank: true
        },
        {
            name: "super_password",
            xtype: "password",
            fieldLabel: __("Super Password"),
            uiStyle: "large",
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
        },
        {
            xtype: "fieldset",
            layout: "hbox",
            title: __("Integration"),
            defaults: {
                padding: 4,
                labelAlign: "right"
            },
            items: [
                {
                    name: "remote_system",
                    xtype: "main.remotesystem.LookupField",
                    fieldLabel: __("Remote System"),
                    allowBlank: true
                },
                {
                    name: "remote_id",
                    xtype: "textfield",
                    fieldLabel: __("Remote ID"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "bi_id",
                    xtype: "displayfield",
                    fieldLabel: __("BI ID"),
                    allowBlank: true,
                    uiStyle: "medium"
                }
            ]
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: __("Tags"),
            allowBlank: true,
            uiStyle: "extra"
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
