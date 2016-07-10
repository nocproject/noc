//---------------------------------------------------------------------
// fm.reportalarmdetail application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.reportalarmdetail.Application");

Ext.define("NOC.fm.reportalarmdetail.Application", {
    extend: "NOC.core.Application",
    initComponent: function() {
        var me = this;

        me.formatButton = Ext.create("Ext.button.Segmented", {
            items: [
                {
                    text: "CSV",
                    pressed: true
                },
                {
                    text: "Excel"
                }
            ],
            anchor: null
        });
        
        me.formPanel = Ext.create("Ext.form.Panel", {
            defaults: {
                labelWidth: 40
            },
            items: [
                {
                    name: "from_date",
                    xtype: "datefield",
                    fieldLabel: __("From"),
                    allowBlank: false,
                    format: "d.m.Y",
                    width: 135
                },
                {
                    name: "to_date",
                    xtype: "datefield",
                    fieldLabel: __("To"),
                    allowBlank: false,
                    format: "d.m.Y",
                    width: 135
                },
                me.formatButton
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Download"),
                            glyph: NOC.glyph.download,
                            scope: me,
                            handler: me.onDownload,
                            formBind: true
                        }
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.formPanel]
        });
        me.callParent();
    },

    onDownload: function() {
        var me = this,
            v = me.formPanel.getValues(),
            format = "csv";

        if(me.formatButton.items.items[1].pressed) {
            format = "xlsx"
        }

        window.open(
            "/fm/reportalarmdetail/download/?from_date=" + v.from_date + "&to_date=" + v.to_date + "&format=" + format
        );
    }
});
