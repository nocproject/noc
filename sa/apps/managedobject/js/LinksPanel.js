//---------------------------------------------------------------------
// sa.managed_object LinksPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LinksPanel");

Ext.define("NOC.sa.managedobject.LinksPanel", {
    extend: "Ext.panel.Panel",
    app: null,

    initComponent: function() {
        var me = this;

        me.closeButton = Ext.create("Ext.button.Button", {
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });
        me.store = Ext.create("NOC.sa.managedobject.LinksStore");
        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            columns: [
                {
                    text: "Local",
                    dataIndex: "local_interface",
                    renderer: NOC.render.Lookup("local_interface")
                },
                {
                    text: "Neighbor",
                    dataIndex: "remote_object",
                    renderer: NOC.render.Lookup("remote_object")
                },
                {
                    text: "Remote",
                    dataIndex: "remote_interface",
                    renderer: NOC.render.Lookup("remote_interface")
                },
                {
                    text: "Method",
                    dataIndex: "discovery_method"
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },

    preview: function(record) {
        var me = this;
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/links/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.grid.setTitle(record.get("name") + " links");
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    }
});
