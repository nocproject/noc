//---------------------------------------------------------------------
// sa.credentialcheckrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
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
        "NOC.sa.authprofile.LookupField"
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
            width: 40,
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
            text: __("Match Expression"),
            dataIndex: "match_expression",
            width: 400,
            renderer: function(v, _x) {
                var labels = [], text;
                Ext.each(v, function(label) {
                    labels.push(NOC.render.Label({
                        badges: label.badges,
                        name: label.name,
                        description: label.description || "",
                        bg_color1: label.bg_color1 || 0,
                        fg_color1: label.fg_color1 || 0,
                        bg_color2: label.bg_color2 || 0,
                        fg_color2: label.fg_color2 || 0
                    }));
                });
                text = labels.join("");
                return '<span data-qtitle="Match Expression" ' +
                    'data-qtip="' + text + '">' + text + '</span>';
            }
        },
        {
            text: __("Description"),
            dataIndex: "description",
            width: 200,
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
            name: "is_active",
            xtype: "checkbox",
            boxLabel: __("Active")
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
            name: "suggest_protocols",
            xtype: "gridfield",
            fieldLabel: __("Topology methods"),
            columns: [
                {
                    text: __("Protocol"),
                    dataIndex: "protocol",
                    width: 100,
                    sortable: false,
                    editor: {
                        xtype: "combobox",
                        store: [
                            ["TELNET", "TELNET"],
                            ["SSH", "SSH"],
                            ["HTTP", "HTTP"],
                            ["HTTPS", "HTTPS"],
                            ["SNMPv1", "SNMPv1"],
                            ["SNMPv2c", "SNMPv2c"]

                        ]
                    }
                }
            ]
        },
        {
            name: "suggest_snmp_oids",
            xtype: "gridfield",
            fieldLabel: __("Suggest SNMP OIDs"),
            columns: [
                {
                    text: __("Oid"),
                    dataIndex: "oid",
                    width: 300,
                    sortable: false,
                    editor: {
                        xtype: "textfield",
                    }
                }
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
    ],
    filters: [
        {
            title: __("By Match Rules Labels"),
            name: "match",
            ftype: "label",
            lookup: "main.handler.LookupField",
            pickerPosition: "left",
            isTree: true,
            filterProtected: false,
            treePickerWidth: 400,
            query_filter: {
                "allow_matched": true
            }
        },
        {
            title: __("By Object"),
            name: "managed_object",
            ftype: "lookup",
            lookup: "sa.managedobject"
        }
    ]
});
