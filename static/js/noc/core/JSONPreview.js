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
        var me = this;

        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        itemId: "close",
                        text: "Close",
                        glyph: NOC.glyph.arrow_left,
                        scope: me,
                        handler: me.onClose
                    }
                ]
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
        var me = this,
            url = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                var json = Ext.decode(response.responseText);
                me.items.first().update("<pre>" + json + "</pre>");
                //NOC.SyntaxHighlight.highlight(me.items.first(),
                //    json, "json");
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
    }
});
