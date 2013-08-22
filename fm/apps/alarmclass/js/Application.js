//---------------------------------------------------------------------
// fm.alarmclass application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclass.Application");

Ext.define("NOC.fm.alarmclass.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.fm.alarmclass.Model",
        "NOC.fm.alarmseverity.LookupField"
    ],
    model: "NOC.fm.alarmclass.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 250
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            renderer: NOC.render.Bool,
            width: 30
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
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Builtin"
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description"
        },
        {
            name: "is_unique",
            xtype: "checkboxfield",
            boxLabel: "Unique"
        },
        {
            name: "user_clearable",
            xtype: "checkboxfield",
            boxLabel: "User Clearable"
        },
        {
            name: "default_severity",
            xtype: "fm.alarmseverity.LookupField",
            fieldLabel: "Default Severity"
        },
        {
            name: "flap_window",
            xtype: "numberfield",
            fieldLabel: "Flap Window",
            allowBlank: true
        },
        {
            name: "flap_threshold",
            xtype: "numberfield",
            fieldLabel: "Flap Threshold",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ],
    //
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            formToolbar: [
                {
                    text: "JSON",
                    glyph: NOC.glyph.file,
                    tooltip: "View as JSON",
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/alarmclass/{{id}}/json/",
            previewName: "Alarm Class: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        me.callParent();
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
