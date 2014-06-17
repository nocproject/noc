//---------------------------------------------------------------------
// NOC.core.JSONPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.JSONPreview");

Ext.define("NOC.core.JSONPreview", {
    extend: "Ext.panel.Panel",
    msg: "",
    layout: "fit",
    app: null,
    restUrl: null,
    previewName: null,

    initComponent: function() {
        var me = this,
            tb = [],
            collection = me.app.noc.collection;

        // Close button
        tb.push(Ext.create("Ext.button.Button", {
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        }));
        //
        me.installButton = Ext.create("Ext.button.Button", {
            text: "Install",
            glyph: NOC.glyph.download,
            scope: me,
            handler: me.onInstallJSON
        });

        if(collection && NOC.settings.install_collection && NOC.hasPermission("create")) {
            tb.push("-");
            tb.push(me.installButton);
        }

        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: tb
            }],
            items: [{
                xtype: "container",
                autoScroll: true,
                bodyPadding: 4
            }]
        });
        me.callParent();
        //
        me.urlTemplate = Handlebars.compile(me.restUrl);
        me.titleTemplate = Handlebars.compile(me.previewName);
    },
    //
    preview: function(record) {
        var me = this;
        if(!record) {
            me.items.first().update("No data!!!");
            me.installButton.setDisabled(true);
            return;
        }
        var url = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        me.currentRecord = record;
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                var json = Ext.decode(response.responseText);
                me.items.first().update("<pre>" + Ext.util.Format.htmlEncode(json) + "</pre>");
                me.installButton.setDisabled(!record.get("uuid"));
            },
            failure: function() {
                NOC.error("Failed to get JSON")
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    onInstallJSON: function() {
        var me = this;
        Ext.Msg.show({
            title: "Add to collections?",
            msg: Ext.String.format("Would you like to add object to your local {0} collection?", me.app.noc.collection),
            buttons: Ext.Msg.YESNO,
            modal: true,
            fn: function(button) {
                if(button === "yes") {
                    Ext.Ajax.request({
                        url: me.urlTemplate(me.currentRecord.data),
                        method: "POST",
                        scope: me,
                        failure: function() {
                            NOC.error("Failed to save JSON");
                        }
                    });
                }
            }
        });
    }
});
