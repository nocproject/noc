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

        me.stopSelectedButton = Ext.create("Ext.button.Button", {
             text: "Disable",
             glyph: NOC.glyph.minus_sign,
             scope: me,
             disabled: true,
             handler: me.onStopSelected
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
                },
                {
                    name: "link_count",
                    type: "integer"
                }
            ]
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            width: 550,
            store: me.store,
            stateful: true,
            stateId: "sa.managedobject-discovery",
            region: "west",
            split: true,
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
                        F: "Fail",
                        true: "OK",
                        false: "Fail"
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
                },
                {
                    text: "Links Found",
                    dataIndex: "link_count",
                    width: 50,
                    align: "right",
                    renderer: function(v) {
                        if(v) {
                            return v;
                        } else {
                            return "";
                        }
                    }
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
                        me.runSelectedButton,
                        me.stopSelectedButton
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

        me.logPanel = Ext.create("Ext.panel.Panel", {
            layout: "fit",
            region: "center",
            autoScroll: true,
            flex: 1,
            items: [{
                xtype: "container",
                autoScroll: true,
                padding: 4
            }]
        });

        Ext.apply(me, {
            items: [
                {
                    xtype: "container",
                    layout: "border",
                    items: [
                        me.grid,
                        me.logPanel
                    ]
                }
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
        var me = this,
            records = me.grid.getSelectionModel().getSelection(),
            names = records.map(function(r) {
                return r.get("name");
            });
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.currentRecord.get("id") + "/discovery/run/",
            method: "POST",
            scope: me,
            jsonData: {
                "names": names
            },
            success: function() {
                me.onRefresh();
            },
            failure: function() {
                NOC.error("Failed to run tasks");
            }
        });
    },
    //
    onStopSelected: function() {
        var me = this,
            records = me.grid.getSelectionModel().getSelection(),
            names = records.map(function(r) {
                return r.get("name");
            });
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.currentRecord.get("id") + "/discovery/stop/",
            method: "POST",
            scope: me,
            jsonData: {
                "names": names
            },
            success: function() {
                me.onRefresh();
            },
            failure: function() {
                NOC.error("Failed to disable tasks");
            }
        });
    },
    //
    onGridSelection: function(selection, records) {
        var me = this,
            canRun, canStop;
        canRun = records.filter(function(v) {
            var status = v.get("status");
            return v.get("enable_profile") === true && (status === "W" || status === "S");
        }).length > 0;
        canStop = records.filter(function(v) {
            var status = v.get("status");
            return v.get("enable_profile") === true && status === "W";
        }).length > 0;
        me.runSelectedButton.setDisabled(!canRun);
        me.stopSelectedButton.setDisabled(!canStop);
        if(records.length === 1) {
            me.showLog(records[0].get("name"));
        }
    },
    //
    setLog: function(text) {
        var me = this;
        me.logPanel.items.first().update("<pre>" + text + "<pre>");
    },
    //
    showLog: function(name) {
        var me = this,
            url = "/sa/managedobject/" + me.currentRecord.get("id") + "/job_log/" + name + "/";
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                me.setLog(response.responseText);
            },
            failure: function() {
                me.setLog("Failed to get job log");
            }
        });
    }
});
