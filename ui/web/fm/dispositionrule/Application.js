//---------------------------------------------------------------------
// fm.dispositionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.dispositionrule.Application");

Ext.define("NOC.fm.dispositionrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.core.TemplatePreview",
        "NOC.core.StringListField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.ListFormField",
        "NOC.fm.eventclass.LookupField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.main.label.LookupField",
        'Ext.ux.form.JSONField',
        "Ext.ux.form.GridField",
        "Ext.form.field.Tag"
    ],
    model: "NOC.fm.dispositionrule.Model",
    search: true,
    treeFilter: "category",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 500
        },
        {
            text: __("Builtin"),
            dataIndex: "is_builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: __("Alarm Disposition"),
            dataIndex: "alarm_disposition",
            flex: 1,
            renderer: NOC.render.Lookup("alarm_disposition")
        },
        {
            text: __("Pref"),
            dataIndex: "preference",
            width: 50
        }
    ],
    filters: [
        {
            title: __("By Event Class"),
            name: "event_class",
            ftype: "lookup",
            lookup: "fm.eventclass"
        },
        {
            title: __("By Alarm Class"),
            name: "alarm_disposition",
            ftype: "lookup",
            lookup: "fm.alarmclass"
        }
    ],

    initComponent: function() {
        var me = this;
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/fm/dispositionrule/{id}/json/'),
            previewName: new Ext.XTemplate('Disposition Rule: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        //
        Ext.apply(me, {
            fields: [
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: __("UUID")
                },
                {
                    xtype: "textarea",
                    name: "description",
                    fieldLabel: __("Description"),
                    allowBlank: true
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

    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
});
