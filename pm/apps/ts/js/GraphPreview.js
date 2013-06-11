//---------------------------------------------------------------------
// GraphPreview model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.GraphPreview");

Ext.define("NOC.pm.ts.GraphPreview", {
    extend: "Ext.Window",
    ts: undefined,
    app: undefined,
    width: 600,
    height: 400,
    autoShow: true,
    layout: "fit",

    initComponent: function() {
        var me = this;
        me.store = Ext.create("Ext.data.Store", {
            fields: ["timestamp", "value"],
            data: []
        });
        Ext.apply(me, {
            items: [
                {
                    xtype: "chart",
                    store: me.store,
                    axes: [
                        {
                            type: "Numeric",
                            fields: ["value"],
                            position: "right",
                            title: "Value",
                            minimum: 0
                        },
                        {
                            type: "Time",
                            position: "bottom",
                            dateFormat: "ga",
                            title: "Time"
                        }
                    ],
                    series: [
                        {
                            type: "area",
                            xField: "timestamp",
                            yField: "value"
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.loadData();
    },
    //
    loadData: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/pm/ts/data/",
            params: {
                ts: me.ts
            },
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    r = data.data[me.ts].map(function(v) {
                        return {
                            timestamp: new Date(v[0] * 1000),
                            value: v[1]
                        }
                    });
                console.log(r);
                me.store.loadRawData(r);
            }
        });
    }
});
