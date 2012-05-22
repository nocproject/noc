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
        // Create tabs
        Ext.apply(me, {
            items: [
                Ext.create("Ext.tab.Panel", {
                    border: false,
                    activeTab: 0,
                    layout: "fit",
                    items: [
                        Ext.create("NOC.inv.interface.L1Panel", {
                            app: me,
                            store: me.l1Store
                        }),
                        Ext.create("NOC.inv.interface.L3Panel", {
                            app: me,
                            store: me.l3Store
                        })
                    ]
                })
            ],
            tbar: [
                "Object:",
                {
                    xtype: "sa.managedobject.LookupField",
                    name: "managedobject",
                    itemId: "managedobject",
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
        me.l1Store.loadData(data.l1 || []);
        me.l3Store.loadData(data.l3 || []);
    }
});
