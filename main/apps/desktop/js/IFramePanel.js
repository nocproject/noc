//---------------------------------------------------------------------
// Resizable IFrame tab for legacy applications
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.IFramePanel");

Ext.define("NOC.main.desktop.IFramePanel", {
    extend: "Ext.Container",
    layout: "fit",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            style : "border: none",
            autoEl: {
                tag: "iframe",
                src: me.noc.url
            }
        });
        me.callParent();
    },
    getHistoryHash: function() {
        var me = this;
        return me.noc.app_id;
    }
});
