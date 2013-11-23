//---------------------------------------------------------------------
// sa.managedobject InventoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.InventoryPanel");

Ext.define("NOC.sa.managedobject.InventoryPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        "NOC.sa.managedobject.InventoryModel"
    ],
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

        //
        me.defaultRoot = {
            text: ".",
            children: []
        };

        me.store = Ext.create("Ext.data.TreeStore", {
            model: "NOC.sa.managedobject.InventoryModel",
            root: me.defaultRoot
        });

        me.inventoryPanel = Ext.create("Ext.tree.Panel", {
            store: me.store,
            rootVisible: false,
            useArrows: true,
            stateful: true,
            stateId: "sa.managedobject-inventory",
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
        me.setTitle(record.get("name") + " inventory");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/inventory/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.setRootNode(data || me.defaultRoot)
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
