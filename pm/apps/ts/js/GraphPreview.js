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
    maximizable: true,

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
                    animate: true,
                    store: me.store,
                    legend: {
                        position: "bottom"
                    },
                    axes: [
                        {
                            type: "Numeric",
                            fields: ["value"],
                            position: "right",
                            minimum: 0,
                            grid: true
                        },
                        {
                            type: "Time",
                            fields: ["timestamp"],
                            position: "bottom",
                            dateFormat: "H:i",
                            grid: true
                        }
                    ],
                    series: [
                        {
                            type: "line",
                            axis: ["bottom", "right"],
                            xField: "timestamp",
                            yField: "value",
                            tips: {
                                trackMouse: true,
                                width: 200,
                                height: 40,
                                renderer: function(storeItem, item) {
                                    console.log(arguments);
                                    this.setTitle(
                                        Ext.String.format("Time: {0}<br/>Value: {1}",
                                            Ext.Date.format(storeItem.get("timestamp"), "Y-m-d H:i:s"),
                                            storeItem.get("value")
                                        )
                                    );
                                }
                            }
                        }
                    ]
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "bottom",
                    items: [
                        {
                            text: "Time machine here!"
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
                ts: me.ts,
                begin: 1371074031,
                end: 1371125036
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
                me.store.loadRawData(r);
            }
        });
    }
});
