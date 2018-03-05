//---------------------------------------------------------------------
// ip.ipam Legacy application panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
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
        me.iframe = document.getElementById(me.id);
        me.iframe.addEventListener(
            "load",
            Ext.bind(me.injectContext, me)
        );
    },

    preview: function(record, backItem) {
        var me = this;
        me.iframe.src = record;
    },
    //
    injectContext: function() {
        var me = this,
            idoc = me.iframe.contentWindow.document;
        me.iframe.contentWindow.panel = me;
        me.iframe.contentWindow.app = me.app;
        me.app.setPrefix(idoc.currentVRF, idoc.currentAFI, idoc.currentPrefix);
    }
});
