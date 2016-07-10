//---------------------------------------------------------------------
// MAC Log window
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.macdb.MACLogForm");

Ext.define("NOC.inv.macdb.MACLogForm", {
    extend: "Ext.panel.Panel",
    autoScroll: true,
    layout: "fit",
    app: null,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("NOC.inv.macdb.MACLogStore");

        me.closeButton = Ext.create("Ext.button.Button", {
            itemId: "close",
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            autoScroll: true,
            layout: "fit",
            columns: [
                {
                    text: "Timestamp",
                    dataIndex: "timestamp",
                    width: 160
                },
                {
                    text: "Mac",
                    dataIndex: "mac",
                    width: 110
                },
                {
                    text: "VC Domain",
                    dataIndex: "vc_domain",
                    flex: 1
                },
                {
                    text: "Vlan",
                    dataIndex: "vlan",
                    width: 40
                },
                {
                    text: "Managed Object",
                    dataIndex: "managed_object_name",
                    flex: 2
                },
                {
                    text: "Interface",
                    dataIndex: "interface_name",
                    flex: 1
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.grid
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
        me.callParent();
    },

    preview: function(record) {
        var me = this;
        me.currentMAC = record.get("mac");
        Ext.Ajax.request({
            url: "/inv/macdb/" + record.get("mac") + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                //me.store.clear();
                if(!r || !r.length) {
                    NOC.info("No MAC history found");
                } else {
                    me.grid.setTitle(Ext.String.format(" MAC {0} history",
                        me.currentMAC));
                    me.store.loadData(r);
                }
            },
            failure: function() {
                NOC.error("Failed to get MAC history");
            }
        });
    },

    onClose: function() {
        var me = this;
        me.app.showGrid();
    }
});
