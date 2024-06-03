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
        "NOC.core.JSONPreview",
        "NOC.fm.alarmseverity.Model",
        "NOC.main.style.LookupField",
        "NOC.main.ref.sound.LookupField"
    ],
    model: "NOC.fm.alarmseverity.Model",
    rowClassField: "row_class",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Builtin"),
            dataIndex: "is_builtin",
            renderer: NOC.render.Bool,
            sortable: false,
            width: 50
        },
        {
            text: __("Severity"),
            dataIndex: "severity",
            width: 50,
            align: "right"
        },
        {
            text: __("Min. Weight"),
            dataIndex: "min_weight",
            width: 50,
            align: "right"
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "uuid",
            xtype: "displayfield",
            fieldLabel: __("UUID")
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "severity",
            xtype: "numberfield",
            fieldLabel: __("Severity"),
            allowBlank: false
        },
        {
            name: "min_weight",
            xtype: "numberfield",
            fieldLabel: __("Min. Weight"),
            allowBlank: false
        },
        {
            name: "code",
            xtype: "textfield",
            fieldLabel: __("Code"),
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: __("Style"),
            allowBlank: false
        },
        {
            name: "sound",
            xtype: "main.ref.sound.LookupField",
            fieldLabel: __("Sound"),
            allowBlank: false
        },
        {
            name: "volume",
            xtype: "numberfield",
            fieldLabel: __("Volume"),
            minValue: 0,
            maxValue: 100,
            allowBlank: true
        }
    ],

    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/fm/alarmseverity/{id}/json/'),
            previewName: new Ext.XTemplate('Alarm Severity: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        Ext.apply(me, {
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                },
                {
                    text: __("Test Sound"),
                    glyph: NOC.glyph.volume,
                    tooltip: __("Test Sound"),
                    scope: me,
                    handler: me.onTestSound
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
    },
    //
    onTestSound: function() {
        var me = this,
            snd;
        if(!me.currentRecord.get("sound")) {
            return;
        }
        snd = new Audio(Ext.String.format('/ui/pkg/nocsound/{0}.mp3', me.currentRecord.get("sound")));
        snd.volume = (me.currentRecord.get("volume") || 100) / 100;
        snd.play();
    }
});
