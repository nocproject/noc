//---------------------------------------------------------------------
// inv.interface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.Application");

Ext.define("NOC.inv.interface.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.sa.managedobject.LookupField"
    ],

    initComponent: function() {
        var me = this;

        me.currentObject = null;

        // Create stores
        me.l1Store = Ext.create("NOC.inv.interface.L1Store");
        me.l3Store = Ext.create("NOC.inv.interface.L3Store");
        me.lagStore = Ext.create("NOC.inv.interface.LAGStore");
        // Create tabs
        me.l1Panel = Ext.create("NOC.inv.interface.L1Panel", {
            app: me,
            store: me.l1Store
        });
        me.lagPanel = Ext.create("NOC.inv.interface.LAGPanel", {
            app: me,
            store: me.lagStore
        });
        me.l3Panel = Ext.create("NOC.inv.interface.L3Panel", {
            app: me,
            store: me.l3Store
        });
        //
        Ext.apply(me, {
            items: [
                Ext.create("Ext.tab.Panel", {
                    border: false,
                    activeTab: 0,
                    layout: "fit",
                    items: [
                        me.l1Panel,
                        me.lagPanel,
                        me.l3Panel
                    ]
                })
            ],
            tbar: [
                "Object:",
                {
                    xtype: "sa.managedobject.LookupField",
                    name: "managedobject",
                    itemId: "managedobject",
                    emptyText: "Select managed object ...",
                    listeners: {
                        select: {
                            scope: me,
                            fn: me.onObjectChange
                        }
                    }
                }
            ]
        });
        me.callParent();
    },
    // Called when managed object changed
    onObjectChange: function(combo, s) {
        var me = this;
        me.currentObject = s[0].get("id");
        me.loadInterfaces();
    },
    // Load object's interfaces
    loadInterfaces: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/interface/" + me.currentObject + "/",
            method: "GET",
            scope: me,
            success: me.onLoadInterfaces,
            failure: function() {
                NOC.error("Failed to get interfaces");
            }
        });
    },
    // Init stores
    onLoadInterfaces: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        // Set panel visibility
        if(data.l1) {
            me.l1Panel.show();
        } else {
            me.l1Panel.hide();
        }
        if(data.lag) {
            me.lagPanel.show();
        } else {
            me.lagPanel.hide();
        }
        if(data.l3) {
            me.l3Panel.show();
        } else {
            me.l3Panel.hide();
        }
        // Load data
        me.l1Store.loadData(data.l1 || []);
        me.lagStore.loadData(data.lag || []);
        me.l3Store.loadData(data.l3 || []);
    }
});
