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
                    text: "Profile Check Rule Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Blt",
                    // tooltip: "Built-in", - broken in ExtJS 5.1
                    dataIndex: "is_builtin",
                    width: 40,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    text: "Pref.",
                    // tooltip: "Preference", - broken in ExtJS 5.1
                    dataIndex: "preference",
                    width: 40,
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
                    width: 180
                },
                {
                    text: "Match",
                    dataIndex: "match_method",
                    width: 50,
                    align: "center"
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    width: 200
                },
                {
                    text: "Action",
                    dataIndex: "action",
                    width: 50
                },
                {
                    text: "Profile",
                    dataIndex: "profile",
                    flex: 1,
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
                    fieldLabel: "UUID",
                    disabled: true
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
                            uiStyle: "large"
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
                            allowBlank: false,
                            uiStyle: "medium"
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
