//---------------------------------------------------------------------
// main.welcome application
//---------------------------------------------------------------------
// Copyright (C) 2007-{{year}} The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.welcome.Application");

Ext.define("NOC.main.welcome.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.main.welcome.templates.Welcome"
    ],
    appId: "main.welcome",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            html: me.templates.Welcome({})
        });
        me.callParent();
    }
});
