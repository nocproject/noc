//---------------------------------------------------------------------
// sa.managed_object LinksPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LinksPanel");

Ext.define("NOC.sa.managedobject.LinksPanel", {
    extend: "NOC.core.ApplicationPanel",

    initComponent: function() {
        var me = this;

        me.currentLink = null;

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.approveButton = Ext.create("Ext.button.Button", {
            text: "Approve",
            glyph: NOC.glyph.ok_circle,
            disabled: true,
            scope: me,
            handler: me.onApproveLink
        });
        me.rejectButton = Ext.create("Ext.button.Button", {
            text: "Reject",
            glyph: NOC.glyph.remove_circle,
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
                        me.getCloseButton(),
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

    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
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
    onApproveLink: function() {
        var me = this,
            li = me.currentRecord.get("name") + ":" + me.currentLink.get("local_interface__label"),
            ri = me.currentLink.get("remote_object__label") + ":" + me.currentLink.get("remote_interface__label");
        Ext.Msg.show({
            title: "Approve link?",
            msg: "Would you like to approve link " + li + " -- " + ri + " manually?",
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            fn: function(btn) {
                if(btn == "yes") {
                    Ext.Ajax.request({
                        url: "/sa/managedobject/link/approve/",
                        method: "POST",
                        jsonData: {
                            link: me.currentLink.get("id")
                        },
                        scope: me,
                        success: function(response) {
                            var data = Ext.decode(response.responseText);
                            if(data.success) {
                                NOC.info("Link has been approved");
                            } else {
                                NOC.error("Failed to approve link: " + data.error);
                            }
                            me.onRefresh();
                        },
                        failure: function() {
                            NOC.error("Failed to approve link");
                        }
                    });
                }
            }
        });
    },
    //
    onRejectLink: function() {
        var me = this,
            li = me.currentRecord.get("name") + ":" + me.currentLink.get("local_interface__label"),
            ri = me.currentLink.get("remote_object__label") + ":" + me.currentLink.get("remote_interface__label");
        Ext.Msg.show({
            title: "Reject link?",
            msg: "Would you like to reject link " + li + " -- " + ri + "?",
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            fn: function(btn) {
                if(btn == "yes") {
                    Ext.Ajax.request({
                        url: "/sa/managedobject/link/reject/",
                        method: "POST",
                        jsonData: {
                            link: me.currentLink.get("id")
                        },
                        scope: me,
                        success: function(response) {
                            NOC.info("Link has been rejected");
                            me.onRefresh();
                        },
                        failure: function() {
                            NOC.error("Failed to reject link");
                        }
                    });
                }
            }
        });
    },
    //
    onGridSelect: function(grid, record, index, opt) {
        var me = this,
            commited = record.get("commited");
        me.currentLink = record;
        me.approveButton.setDisabled(commited);
        me.rejectButton.setDisabled(commited);
    },
    //
    onRefresh: function() {
        var me = this;
        me.approveButton.setDisabled(true);
        me.rejectButton.setDisabled(true);
        me.preview(me.currentRecord);
    }
});
