//---------------------------------------------------------------------
// NOC.core.Application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.LogWindow");

Ext.define("NOC.core.LogWindow", {
    extend: "Ext.Window",
    autoShow: true,
    closable: true,
    maximizable: true,
    modal: true,
    msg: null,
    layout: "fit",
    padding: 4,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "panel",
                    html: "<pre>" + me.msg + "</pre>"
                }
            ]
        });
        me.callParent();
    }
});
