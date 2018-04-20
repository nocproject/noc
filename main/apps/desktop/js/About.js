//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.About");

Ext.define("NOC.main.desktop.About", {
    extend: "Ext.Window",
    title: "About NOC",
    layout: "fit",
    autoShow: true,
    resizable: false,
    closable: true,
    modal: true,
    version: null,
    installation: null,
    width: 500,
    height: 132,
    app: null,
    aboutCfg: null,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "container",
                    html: me.app.templates.About(me.aboutCfg)
                }
            ]
        });
        me.callParent();
    }
});
