//---------------------------------------------------------------------
// JSONPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.JSONPreview");

Ext.define("NOC.sa.managedobject.scripts.JSONPreview", {
    extend: "NOC.sa.managedobject.scripts.ResultPreview",

    initComponent: function() {
        var me = this,
            text = JSON.stringify(me.result, undefined, 4);
        Ext.apply(me, {
            items: [{
                xtype: "container",
                autoScroll: true,
                bodyPadding: 4,
                html: "<pre>" + Ext.util.Format.htmlEncode(text) + "</pre>"
            }]
        });
        me.callParent();
    }
});
