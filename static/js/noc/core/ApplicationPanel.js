//---------------------------------------------------------------------
// NOC.core.ApplicationPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ApplicationPanel");

Ext.define("NOC.core.ApplicationPanel", {
    extend: "Ext.panel.Panel",
    app: undefined,
    backItem: undefined,
    currentRecord: undefined,
    autoScroll: true,
    historyHashPrefix: null,

    preview: function(record, backItem) {
        var me = this,
            bi = backItem === undefined? me.backItem : backItem;
        me.currentRecord = record;
        me.backItem = bi;
        if(me.historyHashPrefix) {
            me.app.setHistoryHash(
                me.currentRecord.get("id"),
                me.historyHashPrefix
            );
        }
    },
    //
    onClose: function() {
        var me = this;
        me.app.showItem(me.backItem);
    },
    //
    getCloseButton: function(cfg) {
        var me = this,
            opts = {
                text: "Close",
                glyph: NOC.glyph.arrow_left,
                scope: me,
                handler: me.onClose
            };
        Ext.apply(opts, cfg || {});
        return Ext.create("Ext.button.Button", opts);
    }
});
