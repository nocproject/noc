//---------------------------------------------------------------------
// fm.outage.application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.outage.Application");

Ext.define("NOC.fm.outage.Application", {
    extend: "NOC.core.Application",
    pollingInterval: 60000,
    //requires: [],
    initComponent: function() {
        var me = this;

        me.pollingTaskId = null;

        me.store = Ext.create("Ext.data.TreeStore", {
            root: {
                expanded: true,
                children: []
            }
        });

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            tooltip: "Refresh data",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.loadData
        });

        me.tree = Ext.create("Ext.tree.Panel", {
            store: me.store,
            rootVisible: false,
            columns: [
                {
                    xtype: "treecolumn",
                    dataIndex: "text",
                    width: 500
                },
                {
                    text: "Objects",
                    dataIndex: "n_objects",
                    width: 50,
                    align: "right"
                },
                {
                    text: "Clients",
                    dataIndex: "affected_clients",
                    width: 50,
                    align: "right"
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.refreshButton
                    ]
                }
            ],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
            }
        });
        Ext.apply(me, {
            items: [
                me.tree
            ]
        });
        me.callParent();
        me.loadData();
        me.startPolling();
    },
    //
    loadData: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/fm/outage/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.setRootNode(data.root);
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    getRowClass: function(record) {
        if(record.get("leaf")) {

        } else {
            return "noc-alert-warning noc-bold";
        }
    },
    onCloseApp: function() {
        var me = this;
        me.stopPolling();
    },

    //
    pollingTask: function () {
        var me = this;
        // Poll only application tab is visible
        if (!me.isActiveApp()) {
            return;
        }
        me.loadData();
    },
    //
    startPolling: function() {
        var me = this;
        if(me.pollingTaskId) {
            me.pollingTask();
        } else {
            me.pollingTaskId = Ext.TaskManager.start({
                run: me.pollingTask,
                interval: me.pollingInterval,
                scope: me
            });
        }
    },
    //
    stopPolling: function() {
        var me = this;
        if(me.pollingTaskId) {
            Ext.TaskManager.stop(me.pollingTaskId);
            me.pollingTaskId = null;
        }
    },

});

