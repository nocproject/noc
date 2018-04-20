//---------------------------------------------------------------------
// support.account application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.account.Application");

Ext.define("NOC.support.account.Application", {
    extend: "NOC.core.Application",
    //requires: [],
    items: [],
    initComponent: function() {
        var me = this;

        me.accountTab = Ext.create("NOC.support.account.AccountPanel", {
            app: me});
        me.systemTab = Ext.create("NOC.support.account.SystemPanel", {
            app: me});
        Ext.apply(me, {
            items: [{
                xtype: "tabpanel",
                layout: "fit",
                autoScroll: true,
                tabPosition: "left",
                items: [
                    me.accountTab,
                    me.systemTab
                ]
            }]
        });
        me.callParent();
        me.getInfo();
    },
    //
    getInfo: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/support/account/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.account) {
                    me.accountTab.setRegistered(data.account);
                    me.systemTab.setDisabled(false);
                } else {
                    me.accountTab.setNotRegistered();
                    me.systemTab.setDisabled(true);
                }
                if(data.system) {
                    me.systemTab.setRegistered(data.system);
                    me.items.first().setActiveItem(1);
                } else {
                    me.systemTab.setNotRegistered();
                }
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    }
});
