//---------------------------------------------------------------------
// sa.managedobject AlarmPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.AlarmPanel");

Ext.define("NOC.sa.managedobject.AlarmPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        "NOC.fm.alarm.Model"
    ],
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.fm.alarm.Model",
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "sa.managedobject-alarm",
            columns: [
                {
                    text: "ID",
                    dataIndex: "id",
                    width: 150
                },
                {
                    text: "Time",
                    dataIndex: "timestamp",
                    width: 100,
                    renderer: NOC.render.DateTime
                },
                {
                    text: "Severity",
                    dataIndex: "severity",
                    width: 70,
                    renderer: NOC.render.Lookup("severity")
                },
                {
                    text: "Class",
                    dataIndex: "alarm_class",
                    width: 300,
                    renderer: NOC.render.Lookup("alarm_class")
                },
                {
                    text: "Subject",
                    dataIndex: "subject",
                    flex: 1
                },
                {
                    text: "Duration",
                    dataIndex: "duration",
                    width: 70,
                    align: "right",
                    renderer: NOC.render.Duration
                },
                {
                    text: "Events",
                    dataIndex: "events",
                    width: 30,
                    align: "right"
                }
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
            ],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
            }
        });
        Ext.apply(me, {
            items: [
                me.grid
            ]
        })
        me.callParent();
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        me.setTitle(record.get("name") + " alarms");
        Ext.Ajax.request({
            url: "/fm/alarm/?managed_object=" + me.currentRecord.get("id"),
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
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    },
    //
    getRowClass: function(record) {
        var me = this;
        return record.get("row_class");
    }
});
