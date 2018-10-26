//---------------------------------------------------------------------
// project.project application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Application");

Ext.define("NOC.project.project.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.project.project.Model"
    ],
    model: "NOC.project.project.Model",
    search: true,
    initComponent: function() {
        var me = this;
        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        Ext.apply(me, {
            formToolbar: [
                me.cardButton
            ],
            columns: [
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 150
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                }
            ]
        });
        me.callParent();
    },
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/project/" + me.currentRecord.get("id") + "/"
            );
        }
    },
    //
    onPreview: function(record) {
        var me = this;
        window.open(
            "/api/card/view/project/" + record.get("id") + "/"
        );
    }
});
