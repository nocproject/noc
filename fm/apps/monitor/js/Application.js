//---------------------------------------------------------------------
// fm.monitor application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.monitor.Application");

Ext.define("NOC.fm.monitor.Application", {
    extend: "NOC.core.Application",
    //requires: [],
    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: null,
            fields: ["id", "group", "key", "value"],
            groupField: "group",
            data: []
        });

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            tooltip: "Refresh data",
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
                    text: "Key",
                    dataIndex: "key",
                    width: 100
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    flex: 1
                }
            ],
            features: [{
                ftype: "groupingsummary",
                groupHeaderTpl: "{name}"
            }]
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
            url: "/fm/monitor/data/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText)
                console.log(data);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    }
});
