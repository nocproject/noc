//---------------------------------------------------------------------
// sa.managedobject InterfacePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.InterfacePanel");

Ext.define("NOC.sa.managedobject.InterfacePanel", {
    extend: "NOC.core.ApplicationPanel",
    app: null,
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.currentObject = null;

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        // Create stores
        me.l1Store = Ext.create("NOC.sa.managedobject.L1Store");
        me.l3Store = Ext.create("NOC.sa.managedobject.L3Store");
        me.l2Store = Ext.create("NOC.sa.managedobject.L2Store");
        me.lagStore = Ext.create("NOC.sa.managedobject.LAGStore");
        // Create tabs
        me.l1Panel = Ext.create("NOC.sa.managedobject.L1Panel", {
            app: me,
            store: me.l1Store,
            disabled: true
        });
        me.lagPanel = Ext.create("NOC.sa.managedobject.LAGPanel", {
            app: me,
            store: me.lagStore,
            disabled: true
        });
        me.l2Panel = Ext.create("NOC.sa.managedobject.L2Panel", {
            app: me,
            store: me.l2Store,
            disabled: true
        });
        me.l3Panel = Ext.create("NOC.sa.managedobject.L3Panel", {
            app: me,
            store: me.l3Store,
            disabled: true
        });
        //
        me.tabPanel = Ext.create("Ext.tab.Panel", {
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
        });
        //
        Ext.apply(me, {
            items: [
                me.tabPanel
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.getCloseButton(),
                        me.refreshButton
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        me.setTitle(record.get("name") + " interfaces");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/interface/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
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
                me.tabPanel.setActiveTab(0);
            },
            failure: function() {
                NOC.error("Failed to load data");
            }
        });
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    }
});
