//---------------------------------------------------------------------
// sa.profilecheckrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.profilecheckrule.Application");

Ext.define("NOC.sa.profilecheckrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.profilecheckrule.Model",
        "NOC.main.ref.profile.LookupField"
    ],
    model: "NOC.sa.profilecheckrule.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/sa/profilecheckrule/{{id}}/json/",
            previewName: "Profile Check Rule: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Blt",
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Pref.",
                    dataIndex: "preference",
                    width: 50,
                    align: "right"
                },
                {
                    text: "Method",
                    dataIndex: "method",
                    width: 100
                },
                {
                    text: "Parameter",
                    dataIndex: "param",
                    width: 250
                },
                {
                    text: "Match",
                    dataIndex: "match_method",
                    width: 50
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    width: 250
                },
                {
                    text: "Action",
                    dataIndex: "action",
                    width: 50
                },
                {
                    text: "Profile",
                    dataIndex: "profile",
                    width: 150
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: "UUID"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "preference",
                    xtype: "numberfield",
                    fieldLabel: "Preference",
                    allowBlank: true,
                    uiStyle: "small"
                },
                {
                    xtype: "fieldset",
                    title: "Match",
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "method",
                            xtype: "combobox",
                            fieldLabel: "Method",
                            store: [
                                ["snmp_v2c_get", "snmp_v2c_get"],
                                ["http_get", "http_get"],
                                ["https_get", "https_get"]
                            ],
                            queryMode: "local",
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "param",
                            xtype: "textfield",
                            fieldLabel: "Parameter",
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "match_method",
                            xtype: "combobox",
                            fieldLabel: "Match",
                            store: [
                                ["eq", "equals"],
                                ["contains", "contains"],
                                ["re", "regexp"]
                            ],
                            queryMode: "local",
                            uiStyle: "small",
                            allowBlank: false
                        },
                        {
                            name: "value",
                            xtype: "textfield",
                            fieldLabel: "Value",
                            allowBlank: false,
                            uiStyle: "large"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: "Action",
                    layout: "hbox",
                    defaults: {
                        labelAlign: "top",
                        padding: 4
                    },
                    items: [
                        {
                            name: "action",
                            xtype: "combobox",
                            fieldLabel: "Action",
                            store: [
                                ["match", "Match"],
                                ["maybe", "Maybe"]
                            ],
                            queryMode: "local",
                            uiStyle: "medium",
                            allowBlank: false
                        },
                        {
                            name: "profile",
                            xtype: "main.ref.profile.LookupField",
                            fieldLabel: "Profile",
                            allowBlank: false
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: "JSON",
                    glyph: NOC.glyph.file,
                    tooltip: "Show JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
