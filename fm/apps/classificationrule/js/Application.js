//---------------------------------------------------------------------
// fm.classificationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.Application");

Ext.define("NOC.fm.classificationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.classificationrule.Model",
        "NOC.fm.eventclass.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.fm.classificationrule.Model",
    search: true,

    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 500
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Event Class",
            dataIndex: "event_class",
            flex: 1,
            renderer: NOC.render.Lookup("event_class")
        },
        {
            text: "Pref",
            dataIndex: "preference",
            width: 50
        }
    ],
    fields: [
        {
            xtype: "textfield",
            name: "name",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            xtype: "textarea",
            name: "description",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            xtype: "numberfield",
            name: "preference",
            fieldLabel: "Preference",
            allowBlank: false,
            defaultValue: 1000,
            minValue: 0,
            maxValue: 10000
        },
        {
            xtype: "fm.eventclass.LookupField",
            name: "event_class",
            fieldLabel: "Event Class",
            allowBlank: false
        },
        {
            xtype: "gridfield",
            name: "patterns",
            fieldLabel: "Patterns",
            allowBlank: false,
            columns: [
                {
                    text: "Key RE",
                    dataIndex: "key_re",
                    flex: 1,
                    editor: "textfield"
                },
                {
                    text: "Value RE",
                    dataIndex: "value_re",
                    flex: 1,
                    editor: "textfield"
                }
            ]
        }
    ],
    filters: [
        {
            title: "Builtin",
            name: "is_builtin",
            ftype: "boolean"
        },
        {
            title: "By Event Class",
            name: "event_class",
            ftype: "lookup",
            lookup: "fm.eventclass"
        }
    ],

    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: "/fm/classificationrule/{{id}}/json/",
            previewName: "Classification Rule: {{name}}"
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        //
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

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
