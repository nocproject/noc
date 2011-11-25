//---------------------------------------------------------------------
// Resizable IFrame tab for legacy applications
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.IFramePanel");

Ext.define("NOC.main.desktop.IFramePanel", {
    extend: "Ext.Container",
    layout: 'fit',
    initComponent: function() {
        this.items = [{
            xtype : "component",
            style : 'border: none',
            autoEl : {
                tag : "iframe",
                src : this.noc.url
            }
        }];
        this.callParent(arguments);
    }
});
