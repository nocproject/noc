//---------------------------------------------------------------------
// inv.connectionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.connectionrule.Application");

Ext.define("NOC.inv.connectionrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.connectionrule.Model",
        "NOC.core.StringListField"
    ],
    model: "NOC.inv.connectionrule.Model",
    search: true,

    actions: [
        {
            title: "Get JSON",
            action: "json",
            glyph: NOC.glyph.file,
            resultTemplate: "JSON"
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/inv/connectionrule/{{id}}/json/",
            previewName: "Connection Rule: {{name}}"
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
                    text: "Builtin",
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool,
                    sortable: false
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
                    fieldLabel: "Name",
                    xtype: "textfield",
                    allowBlank: false
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: "UUID"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "context",
                    xtype: "gridfield",
                    fieldLabel: "Context",
                    columns: [
                        {
                            text: "Type",
                            dataIndex: "type",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Scope",
                            dataIndex: "scope",
                            width: 70,
                            editor: "textfield"
                        },
                        {
                            text: "Reset Scopes",
                            dataIndex: "reset_scopes",
                            flex: 1,
                            editor: "stringlistfield"
                        }
                    ]
                },
                {
                    name: "rules",
                    xtype: "gridfield",
                    fieldLabel: "Rules",
                    columns: [
                        {
                            text: "Match Type",
                            dataIndex: "match_type",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Match Connection",
                            dataIndex: "match_connection",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Scope",
                            dataIndex: "scope",
                            width: 50,
                            editor: "textfield"
                        },
                        {
                            text: "Target Type",
                            dataIndex: "target_type",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Target Number",
                            dataIndex: "target_number",
                            width: 100,
                            editor: "textfield"
                        },
                        {
                            text: "Target Connection",
                            dataIndex: "target_connection",
                            width: 100,
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

    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],

    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
