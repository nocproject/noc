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

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.approveButton = Ext.create("Ext.button.Button", {
            text: "Approve",
            disabled: true,
            scope: me,
            handler: me.onApproveLink
        });
        me.rejectButton = Ext.create("Ext.button.Button", {
            text: "Reject",
            disabled: true,
            scope: me,
            handler: me.onRejectLink
        });

        me.store = Ext.create("NOC.sa.managedobject.LinksStore");
        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "sa.managedobject-links",
            columns: [
                {
                    text: "Local",
                    dataIndex: "local_interface",
                    renderer: NOC.render.Lookup("local_interface")
                },
                {
                    text: "Local Description",
                    dataIndex: "local_description"
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
                    text: "Remote Description",
                    dataIndex: "remote_description"
                },
                {
                    text: "Method",
                    dataIndex: "discovery_method"
                },
                {
                    text: "Commited",
                    dataIndex: "commited",
                    renderer: NOC.render.Bool
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton,
                        me.refreshButton,
                        "-",
                        me.approveButton,
                        me.rejectButton
                    ]
                }
            ],
            listeners: {
                scope: me,
                select: me.onGridSelect
            }
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
        me.currentRecord = record;
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
    },
    //
    onApproveLink: function() {

    },
    //
    onRejectLink: function() {

    },
    //
    onGridSelect: function(grid, record, index, opt) {
        var me = this,
            commited = record.get("commited");
        me.approveButton.setDisabled(commited);
        me.rejectButton.setDisabled(commited);
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    }
});
