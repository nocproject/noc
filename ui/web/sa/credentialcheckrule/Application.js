//---------------------------------------------------------------------
// sa.credentialcheckrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.credentialcheckrule.Application");

Ext.define("NOC.sa.credentialcheckrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.PasswordField",
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "NOC.sa.credentialcheckrule.Model",
        "Ext.ux.form.GridField",
        "NOC.sa.authprofile.Model"
    ],
    model: "NOC.sa.credentialcheckrule.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 200
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 100,
            align: "left"
        },
        {
            text: __("Pref."),
            // tooltip: "Preference", - broken in ExtJS 5.1
            dataIndex: "preference",
            width: 40,
            align: "right"
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 200
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
            xtype: "displayfield",
            name: "uuid",
            fieldLabel: __("UUID")
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "preference",
            xtype: "numberfield",
            fieldLabel: __("Preference"),
            allowBlank: true,
            uiStyle: "small"
        },
        {
            name: "suggest_snmp",
            fieldLabel: __("Suggest SNMP"),
            xtype: "gridfield",
            allowBlank: true,
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
                    flex: 200
                }
            ]
        },
        {
            name: "suggest_credential",
            fieldLabel: __("Suggest CLI"),
            xtype: "gridfield",
            allowBlank: true,
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
                    flex: 200,
                    editor: "textfield"
                }
            ]
        },
        {
            name: "suggest_auth_profile",
            fieldLabel: __("Suggest Auth Profile"),
            xtype: "gridfield",
            allowBlank: true,
            columns: [
                {
                    text: __("Auth Profile"),
                    dataIndex: "auth_profile",
                    width: 200,
                    editor: {
                        xtype: "sa.authprofile.LookupField"
                    },
                    renderer: NOC.render.Lookup("auth_profile")
                },
            ]
        },
        {
            name: "match",
            xtype: "listform",
            fieldLabel: __("Match Rules"),
            rows: 2,
            items: [
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Match Labels"),
                    allowBlank: true,
                    isTree: true,
                    filterProtected: false,
                    pickerPosition: "down",
                    uiStyle: "extra",
                    query: {
                        "allow_matched": true
                    }
                },
                {
                    name: "exclude_labels",
                    xtype: "labelfield",
                    fieldLabel: __("Exclude Match Labels"),
                    allowBlank: true,
                    isTree: true,
                    filterProtected: false,
                    pickerPosition: "down",
                    uiStyle: "extra",
                    query: {
                        "allow_matched": true
                    }
                },
            ]
        }
    ]
});
