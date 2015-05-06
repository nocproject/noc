//---------------------------------------------------------------------
// fm.alarmseverity application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmseverity.Application");

Ext.define("NOC.fm.alarmseverity.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmseverity.Model",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.fm.alarmseverity.Model",
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            renderer: NOC.render.Bool,
            sortable: false,
            width: 50
        },
        {
            text: "Severity",
            dataIndex: "severity",
            width: 50,
            align: "right"
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
            xtype: "textfield",
            fieldLabel: "Name",
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
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "severity",
            xtype: "numberfield",
            fieldLabel: "Severity",
            allowBlank: false
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: false
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/alarmseverity/{{id}}/json/",
            previewName: "Alarm Severity: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        Ext.apply(me, {
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
        //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
