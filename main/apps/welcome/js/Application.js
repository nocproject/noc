//---------------------------------------------------------------------
// main.welcome application
//---------------------------------------------------------------------
// Copyright (C) 2007-{{year}} The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.welcome.Application");

Ext.define("NOC.main.welcome.Application", {
    extend: "NOC.core.Application",
    items: [
        {
            xtype: "container",
            html: "Welcome",
            bodyPadding: 4
        }
    ],
    initComponent: function() {
        this.callParent();
        Ext.Ajax.request({
            method: "GET",
            url: "/main/welcome/",
            scope: this,
            success: function(response) {
                this.removeAll();
                this.add({
                    xtype: "component",
                    html: Ext.decode(response.responseText)
                });
            }
        });
    }
});
