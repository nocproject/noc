//---------------------------------------------------------------------
// Validation plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.plugins.Validation");

Ext.define("NOC.fm.alarm.plugins.Validation", {
    extend: "Ext.panel.Panel",
    title: "Validation",
    app: null,
    autoScroll: true,
    bodyPadding: 4,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                "name", "interface", "value", "level"
            ],
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            autoScroll: true,
            store: me.store,
            columns: [
                {
                    dataIndex: "name",
                    text: "Metric",
                    width: 150
                },
                {
                    dataIndex: "interface",
                    text: "Interface",
                    width: 150
                },
                {
                    dataIndex: "level",
                    text: "level",
                    width: 50
                },
                {
                    dataIndex: "value",
                    text: "Value",
                    flex: 1
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });

        me.callParent();
    },

    updateData: function(data) {
        var me = this;
        me.store.loadData(data.thresholds);
    }
});
