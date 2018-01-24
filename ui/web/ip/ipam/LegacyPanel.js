//---------------------------------------------------------------------
// ip.ipam Legacy application panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.LegacyPanel");

Ext.define("NOC.ip.ipam.LegacyPanel", {
    extend: "Ext.Container",
    layout: "fit",
    style: "border: none",
    app: undefined,
    iframe: undefined,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            autoEl: {
                tag: "iframe",
                src: "/ip/ipam/"
            }
        });
        me.callParent();
    },

    afterRender: function() {
        var me = this;
        me.callParent();
        me.iframe = window.frames[me.id];
        me.iframe.addEventListener(
            "load",
            Ext.bind(me.injectContext, me)
        );
        //me.injectContext();
    },

    preview: function(record, backItem) {
        var me = this;
        me.iframe.window.location = record;
    },
    //
    injectContext: function() {
        var me = this;
        console.log("inject", me);
        me.iframe.window.panel = me;
        me.iframe.window.app = me.app;
    }
});
