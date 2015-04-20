//---------------------------------------------------------------------
// sa.action application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.action.Application");

Ext.define("NOC.sa.action.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.action.Model"
    ],
    model: "NOC.sa.action.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/sa/action/{{id}}/json/",
            previewName: "Action: {{name}}"
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
                    text: "Label",
                    dataIndex: "Label",
                    width: 200
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: "Lvl",
                    dataIndex: "access_level",
                    width: 50
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "medium",
                    regex: /^[a-zA-Z_][a-zA-Z_\-0-9]*$/
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: "UUID"
                },
                {
                    name: "label",
                    xtype: "textfield",
                    fieldLabel: "Label",
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    uiStyle: "extra"
                },
                {
                    name: "access_level",
                    xtype: "numberfield",
                    fieldLabel: "Access Level",
                    value: 15,
                    minValue: 0,
                    maxValue: 15,
                    uiStyle: "small"
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: "Handler",
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "params",
                    xtype: "gridfield",
                    fieldLabel: "Params",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            width: 150,
                            editor: {
                                xtype: "textfield",
                                regex: /^[a-zA-Z_][a-zA-Z_\-0-9]*$/
                            }
                        },
                        {
                            text: "Required",
                            dataIndex: "is_required",
                            width: 50,
                            editor: "checkbox",
                            renderer: NOC.render.Bool
                        },
                        {
                            text: "Type",
                            dataIndex: "type",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["str", "str"],
                                    ["float", "float"],
                                    ["int", "int"],
                                    ["interface", "interface"]
                                ]
                            }
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            flex: 1,
                            editor: "textfield"
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
