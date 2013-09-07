//---------------------------------------------------------------------
// NOC.core.Preview
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Preview");

Ext.define("NOC.core.Preview", {
    extend: "Ext.panel.Panel",
    msg: "",
    layout: "fit",
    syntax: null,
    app: null,
    restUrl: null,

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
                    },
                    me.revCombo,
                    me.diffCombo
                ]
            }],
            items: [{
                xtype: "container",
                autoScroll: true,
                padding: 4
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
        me.currentRecord = record;
        me.rootUrl = Ext.String.format(me.restUrl, record.get("id"));
        me.rootUrl = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        me.requestText();
    },
    //
    requestText: function() {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl,
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get text");
            }
        });
    },
    //
    renderText: function(text) {
        var me = this;
        me.items.first().update("<pre>" + text + "<pre>");
    },
    //
    onClose: function() {
        var me = this;
        me.app.showGrid();
    }
});
