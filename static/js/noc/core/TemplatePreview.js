//---------------------------------------------------------------------
// NOC.core.TemplatePreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TemplatePreview");

Ext.define("NOC.core.TemplatePreview", {
    extend: "Ext.panel.Panel",
    layout: "fit",
    app: null,
    template: null,
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
                padding: 4
            }]
        });
        me.callParent();
        me.titleTemplate = Handlebars.compile(me.previewName);
    },
    //
    preview: function(record, extra) {
        var me = this,
            context = {};
        Ext.apply(context, record.data);
        if(extra) {
            Ext.apply(context, extra);
        }
        me.setTitle(me.titleTemplate(context));
        me.items.first().update("<div class='noc-tp'>" + me.template(context) + "</div>");
    },
    //
    onClose: function() {
        var me = this;
        me.app.showGrid();
    }
});
