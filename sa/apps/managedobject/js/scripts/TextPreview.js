//---------------------------------------------------------------------
// TextPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.TextPreview");

Ext.define("NOC.sa.managedobject.scripts.TextPreview", {
    extend: "NOC.sa.managedobject.scripts.ResultPreview",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [{
                xtype: "container",
                autoScroll: true,
                bodyPadding: 4,
                html: "<pre>" + Ext.util.Format.htmlEncode(me.result) + "</pre>"
            }]
        });
        me.callParent();
    }
});
