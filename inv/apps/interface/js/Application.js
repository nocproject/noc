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
        me.l2Store = Ext.create("NOC.inv.interface.L2Store");
        me.lagStore = Ext.create("NOC.inv.interface.LAGStore");
        // Create tabs
        me.l1Panel = Ext.create("NOC.inv.interface.L1Panel", {
            app: me,
            store: me.l1Store,
            disabled: true
        });
        me.lagPanel = Ext.create("NOC.inv.interface.LAGPanel", {
            app: me,
            store: me.lagStore,
            disabled: true
        });
        me.l2Panel = Ext.create("NOC.inv.interface.L2Panel", {
            app: me,
            store: me.l2Store,
            disabled: true
        });
        me.l3Panel = Ext.create("NOC.inv.interface.L3Panel", {
            app: me,
            store: me.l3Store,
            disabled: true
        });
        //
        me.searchField = Ext.create({
            xtype: "searchfield",
            name: "search",
            disabled: true,
            emptyText: "Search ...",
            typeAhead: true,
            scope: me,
            handler: me.onSearch
        });
        //
        Ext.apply(me, {
            items: [
                Ext.create("Ext.tab.Panel", {
                    name: "tab",
                    itemId: "tab",
                    border: false,
                    activeTab: 0,
                    layout: "fit",
                    autoScroll: true,
                    defaults: {
                        autoScroll: true
                    },
                    items: [
                        me.l1Panel,
                        me.lagPanel,
                        me.l2Panel,
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
                },
                me.searchField
            ]
        });
        me.callParent();
        me.tabPanel = me.getComponent("tab");
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
            data = Ext.decode(response.responseText),
            adjust = function(panel, data) {
                var d = (data || []).length > 0;
                panel.setDisabled(!d);
            }
        // Set panel visibility
        adjust(me.l1Panel, data.l1);
        adjust(me.lagPanel, data.lag);
        adjust(me.l2Panel, data.l2);
        adjust(me.l3Panel, data.l3);
        // Load data
        me.l1Store.loadData(data.l1 || []);
        me.lagStore.loadData(data.lag || []);
        me.l2Store.loadData(data.l2 || []);
        me.l3Store.loadData(data.l3 || []);
        //
        me.searchField.setDisabled(false);
        me.tabPanel.setActiveTab(0);
        me.searchField.setValue("");
    },
    //
    onSearch: function(value) {
        var me = this,
            s = value.toLowerCase(),
            // Match substring
            smatch = function(record, field, s) {
                return record.get(field).toLowerCase().indexOf(s) != -1;
            };
        // Search L1
        me.l1Store.filterBy(function(r) {
            return (
                !s
                || smatch(r, "name", s)
                || smatch(r, "description", s)
                || smatch(r, "mac", s)
                || smatch(r, "lag"));
        });
        // Search LAG
        me.lagStore.filterBy(function(r) {
            return (
                !s
                || smatch(r, "name", s)
                || smatch(r, "description", s));
        });
        // Search L2
        me.l2Store.filterBy(function(r) {
            return (
                !s
                || smatch(r, "name", s)
                || smatch(r, "description", s));
        });
        // Search L3
        me.l3Store.filterBy(function(r) {
            return (
                !s
                || smatch(r, "name", s)
                || smatch(r, "description", s)
                || smatch(r, "vrf", s));
        });
    }
});
