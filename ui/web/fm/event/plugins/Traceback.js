//---------------------------------------------------------------------
// Traceback plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.plugins.Traceback");

Ext.define("NOC.fm.event.plugins.Traceback", {
    extend: "Ext.panel.Panel",
    title: __("Traceback"),
    app: null,
    autoScroll: true,
    bodyPadding: 4,

    updateData: function(data) {
        var me = this;
        me.update("<PRE>" + Ext.util.Format.htmlEncode(data.traceback) + "</PRE>");
    }
});


