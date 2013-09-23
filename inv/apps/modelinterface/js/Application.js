//---------------------------------------------------------------------
// inv.modelinterface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelinterface.Application");

Ext.define("NOC.inv.modelinterface.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.modelinterface.Model",
    search: true,
    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],
    //
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/inv/modelinterface/{{id}}/json/",
            previewName: "Model Interface: {{name}}"
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    width: 300,
                    dataIndex: "name"
                },
                {
                    text: "Builtin",
                    width: 50,
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool
                },
                {
                    text: "Description",
                    flex: 1,
                    dataIndex: "description"
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
                    name: "is_builtin",
                    xtype: "checkboxfield",
                    boxLabel: "Is Builtin"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "attrs",
                    xtype: "gridfield",
                    fieldLabel: "Attrs",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            editor: "textfield"
                        },
                        {
                            text: "Type",
                            dataIndex: "type",
                            editor: {
                                xtype: "combobox",
                                store: [
                                    "str", "int", "float", "bool",
                                    "objectid", "ref"
                                ],
                                autoSelect: true

                            }
                        },
                        {
                            text: "Description",
                            dataIndex: "description",
                            editor: "textfield",
                            flex: 1
                        },
                        {
                            text: "Req.",
                            dataIndex: "required",
                            editor: "checkboxfield",
                            width: 30,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: "Const.",
                            dataIndex: "is_const",
                            editor: "checkboxfield",
                            width: 30,
                            renderer: NOC.render.Bool
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
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
