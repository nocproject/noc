//---------------------------------------------------------------------
//.inv.monitor application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.monitor.Application");

Ext.define("NOC.inv.monitor.Application", {
    extend: "NOC.core.Application",
    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: null,
            fields: ["pool", "total_tasks", "running_tasks", "late_tasks", "lag"],
            data: []
        });

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: __("Refresh"),
            tooltip: __("Refresh data"),
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.loadData
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [me.refreshButton]
                }
            ],
            columns: [
                {
                    text: __("Pool"),
                    dataIndex: "pool",
                    width: 100
                },
                {
                    text: __("Tasks"),
                    dataIndex: "total_tasks",
                    width: 100,
                    align: "right"
                },
                {
                    text: __("Running"),
                    dataIndex: "running_tasks",
                    width: 100,
                    align: "right"
                },
                {
                    text: __("Late"),
                    dataIndex: "late_tasks",
                    width: 100,
                    align: "right"
                },
                {
                    text: __("Lag"),
                    dataIndex: "lag",
                    width: 100,
                    align: "right"
                }
            ]
        });
        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
        me.loadData();
    },
    //
    loadData: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/monitor/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText)
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    }
});
