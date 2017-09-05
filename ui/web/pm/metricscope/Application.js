//---------------------------------------------------------------------
// pm.metricscope application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricscope.Application");

Ext.define("NOC.pm.metricscope.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricscope.Model"
    ],
    model: "NOC.pm.metricscope.Model",
    search: true,
    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/pm/metricscope/{id}/json/'),
            previewName: new Ext.XTemplate('Scope: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID"),
                    allowBlank: true
                },
                {
                    name: "table_name",
                    xtype: "textfield",
                    fieldLabel: __("Table"),
                    allowBlank: false,
                    uiStyle: "medium",
                    regex: /[a-zA-Z][0-9a-zA-Z_]*/
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "key_fields",
                    xtype: "gridfield",
                    fieldLabel: __("Key Fields"),
                    allowBlank: false,
                    columns: [
                        {
                            dataIndex: "field_name",
                            text: __("Field"),
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            dataIndex: "model",
                            text: __("Model"),
                            flex: 1,
                            editor: "textfield"
                        }
                    ]
                },
                {
                    name: "path",
                    xtype: "gridfield",
                    fieldLabel: __("Path"),
                    allowBlank: true,
                    columns: [
                        {
                            dataIndex: "name",
                            text: __("Name"),
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            dataIndex: "is_required",
                            text: __("Required"),
                            width: 50,
                            editor: "checkbox",
                            renderer: NOC.render.Bool
                        },
                        {
                            dataIndex: "default_value",
                            text: __("Default"),
                            flex: 1,
                            editor: "textfield"
                        }
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
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
