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
    app: null,
    autoScroll: true,
    title: "Inventory",

    initComponent: function() {
        var me = this;

        me.currentObject = null;

        //
        me.defaultRoot = {
            text: ".",
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
            stateId: "inv.inv.plugins.inventory-inventory",
            columns: [
                {
                    xtype: "treecolumn",
                    dataIndex: "name",
                    text: "Name",
                    width: 200
                },
                {
                    text: "Model",
                    dataIndex: "model"
                },
                {
                    text: "Description",
                    dataIndex: "description"
                },
                {
                    text: "Serial",
                    dataIndex: "serial"
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
