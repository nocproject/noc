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
            text: __("Refresh"),
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
                    text: __("ID"),
                    dataIndex: "id",
                    width: 150
                },
                {
                    text: __("Time"),
                    dataIndex: "timestamp",
                    width: 100,
                    renderer: NOC.render.DateTime
                },
                {
                    text: __("Severity"),
                    dataIndex: "severity",
                    width: 70,
                    renderer: NOC.render.Lookup("severity")
                },
                {
                    text: __("Class"),
                    dataIndex: "alarm_class",
                    width: 300,
                    renderer: NOC.render.Lookup("alarm_class")
                },
                {
                    text: __("Subject"),
                    dataIndex: "subject",
                    flex: 1
                },
                {
                    text: __("Duration"),
                    dataIndex: "duration",
                    width: 70,
                    align: "right",
                    renderer: NOC.render.Duration
                },
                {
                    text: __("Events"),
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
            },
            listeners: {
                scope: me,
                itemdblclick: function(grid, record) {
                    me.onOpenAlarm(record.get("id"));
                }
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
    },
    //
    onOpenAlarm: function(alarmId) {
        var me = this;
        NOC.launch(
            "fm.alarm", "history", {args: [alarmId]}
        );
    }
});
