//---------------------------------------------------------------------
// sa.managed_object DiscoveryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.DiscoveryPanel");

Ext.define("NOC.sa.managedobject.DiscoveryPanel", {
    extend: "Ext.panel.Panel",
    app: null,
    layout: "fit",
    autoScroll: true,

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

         me.runSelectedButton = Ext.create("Ext.button.Button", {
             text: "Run",
             glyph: NOC.glyph.play,
             scope: me,
             disabled: true,
             handler: me.onRunSelected
        });

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                {
                    name: "name",
                    type: "string"
                },
                {
                    name: "enable_profile",
                    type: "boolean"
                },
                {
                    name: "status",
                    type: "string"
                },
                {
                    name: "last_run",
                    type: "date"
                },
                {
                    name: "last_status",
                    type: "string"
                },
                {
                    name: "next_run",
                    type: "date"
                }
            ]
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 120
                },
                {
                    text: "Profile",
                    dataIndex: "enable_profile",
                    renderer: NOC.render.Bool,
                    width: 40
                },
                {
                    text: "Status",
                    dataIndex: "status",
                    width: 40,
                    renderer: NOC.render.Choices({
                        W: "Wait",
                        R: "Run",
                        S: "Stop",
                        F: "Fail"
                    })
                },
                {
                    text: "Last Run",
                    dataIndex: "last_run",
                    width: 120,
                    renderer: NOC.render.DateTime
                },
                {
                    text: "Last Status",
                    dataIndex: "last_status",
                    width: 40,
                    renderer: NOC.render.Choices({
                        W: "Wait",
                        R: "Run",
                        S: "Stop",
                        F: "Fail"
                    })
                },
                {
                    text: "Next Run",
                    dataIndex: "next_run",
                    width: 120,
                    renderer: NOC.render.DateTime
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
                        me.runSelectedButton
                    ]
                }
            ],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
            },
            selModel: Ext.create("Ext.selection.RowModel", {
                mode: "MULTI"
            }),
            listeners: {
                scope: me,
                selectionchange: me.onGridSelection
            }
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setTitle(record.get("name") + " discovery");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/discovery/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to load data");
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    getRowClass: function(record) {
        var me = this;
        console.log(record.get("name"), record.get("enable_profile"));
        if(!record.get("enable_profile")) {
            return "noc-inactive";
        } else if(record.get("last_status") === "F") {
            return "noc-fail";
        }
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    },
    //
    onRunSelected: function() {
        var me = this;
        NOC.error("Not implemented");
    },
    //
    onGridSelection: function(selection, records) {
        var me = this;
        me.runSelectedButton.setDisabled(records.length === 0);
    }
});
