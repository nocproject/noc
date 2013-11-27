//---------------------------------------------------------------------
// inv.inv LAG Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.DataPanel");

Ext.define("NOC.inv.inv.DataPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.inv.inv.DataModel",
        "NOC.inv.inv.LogModel"
    ],
    title: "Data",
    closable: false,
    layout: "border",

    initComponent: function() {
        var me = this;

        // Data Store
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.DataModel",
            groupField: "interface"
        });
        // Log Store
        me.logStore = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.LogModel"
        });
        // Grids
        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.inv-data-grid",
                    store: me.store,
                    region: "center",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "Description",
                            dataIndex: "description"
                        },
                        {
                            text: "Type",
                            dataIndex: "type"
                        },
                        {
                            text: "Value",
                            dataIndex: "value",
                            flex: 1
                        }
                    ],
                    features: [{ftype:'grouping'}]
                },
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.inv-log-grid",
                    store: me.logStore,
                    region: "south",
                    height: 100,
                    columns: [
                        {
                            text: "Time",
                            dataIndex: "ts",
                            renderer: NOC.render.DateTime,
                            width: 100
                        },
                        {
                            text: "User",
                            dataIndex: "user",
                            width: 70
                        },
                        {
                            text: "System",
                            dataIndex: "system",
                            width: 70
                        },
                        {
                            text: "Operation",
                            dataIndex: "op",
                            width: 70
                        },
                        {
                            text: "Object",
                            dataIndex: "managed_object",
                            width: 100
                        },
                        {
                            text: "Message",
                            dataIndex: "message",
                            flex: 1
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        console.log("DATA", data);
        me.store.loadData(data.data);
        me.logStore.loadData(data.log);
    }
});
