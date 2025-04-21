//---------------------------------------------------------------------
// main.jsonimport application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.jsonimport.Application");

Ext.define("NOC.main.jsonimport.Application", {
    extend: "NOC.core.Application",
    requires: [
        // "NOC.core.CMText"
    ],
    initComponent: function() {
        var me = this;

        me.saveButton = Ext.create("Ext.button.Button", {
            text: __("Save"),
            glyph: NOC.glyph.save,
            scope: me,
            handler: me.onSave,
            formBind: true,
            disabled: true
        });

        me.jsonField = Ext.create("NOC.core.CMText", {
            allowBlank: false,
            flex: 1
        });

        me.form = Ext.create("Ext.form.Panel", {
            layout: {
                type: "vbox",
                align: "stretch"
            },
            items: [
                me.jsonField
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.saveButton
                    ]
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.form
            ]
        });
        me.callParent();
    },
    //
    onSave: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/main/jsonimport/",
            method: "POST",
            scope: me,
            jsonData: {
                "json": me.jsonField.getValue()
            },
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    NOC.info(__("Object has been loaded"));
                    me.jsonField.setValue("");
                } else {
                    NOC.error("Error loading object: " + data.error);
                }
            },
            failure: function(response) {
                NOC.error("Error loading object");
            }
        });
    }
});
