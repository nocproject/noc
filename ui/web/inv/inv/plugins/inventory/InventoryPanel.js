//---------------------------------------------------------------------
// inv.inv.plugins.inventory InventoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.inventory.InventoryPanel");

Ext.define("NOC.inv.inv.plugins.inventory.InventoryPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        "NOC.inv.inv.plugins.inventory.InventoryModel"
    ],
    layout: "fit",
    app: null,
    scrollable: true,
    title: __("Inventory"),

    initComponent: function() {
        var me = this;

        me.currentObject = null;

        //
        me.defaultRoot = {
            text: __("."),
            children: []
        };

        me.store = Ext.create("Ext.data.TreeStore", {
            model: "NOC.inv.inv.plugins.inventory.InventoryModel",
            root: me.defaultRoot
        });

        me.inventoryPanel = Ext.create("Ext.tree.Panel", {
            store: me.store,
            rootVisible: false,
            useArrows: true,
            stateful: true,
            stateId: "inv.inv-inventory-inventory",
            columns: [
                {
                    xtype: "treecolumn",
                    dataIndex: "name",
                    text: __("Name"),
                    width: 200
                },
                {
                    text: __("Model"),
                    dataIndex: "model",
                    width: 300
                },
                {
                    text: __("Revision"),
                    dataIndex: "revision",
                    width: 100
                },
                {
                    text: __("Serial"),
                    dataIndex: "serial",
                    width: 150
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ]
        });
        //
        Ext.apply(me, {
            items: [
                me.inventoryPanel
            ]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.store.setRootNode(data || me.defaultRoot)
    }
});
