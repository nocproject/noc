//---------------------------------------------------------------------
// bi.dashboardlayout application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.bi.dashboardlayout.Application");

Ext.define("NOC.bi.dashboardlayout.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.bi.dashboardlayout.Model"
    ],
    model: "NOC.bi.dashboardlayout.Model",
    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/bi/dashboardlayout/{id}/json/'),
            previewName: new Ext.XTemplate('Vendor: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name")
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description")
                },
                {
                    name: "cells",
                    xtype: "gridfield",
                    fieldLabel: __("Cells"),
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name",
                            editor: "textfield",
                            width: 150
                        },
                        {
                            text: __("Row"),
                            dataIndex: "row",
                            editor: "numberfield",
                            width: 50
                        },
                        {
                            text: __("Height"),
                            dataIndex: "height",
                            editor: "numberfield",
                            width: 50
                        },
                        {
                            text: __("Extra Small"),
                            dataIndex: "xs",
                            editor: "numberfield",
                            width: 50
                        },
                        {
                            text: __("Small"),
                            dataIndex: "sm",
                            editor: "numberfield",
                            width: 50
                        },
                        {
                            text: __("Medium"),
                            dataIndex: "md",
                            editor: "numberfield",
                            width: 50
                        },
                        {
                            text: __("Large"),
                            dataIndex: "lg",
                            editor: "numberfield",
                            width: 50
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
