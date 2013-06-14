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
        var me = this,
            storeFields = ["timestamp"],
            axisFields = [],
            series = [];
        // Determine store fields
        me.tsList = [];
        for(var i in me.ts) {
            me.tsList.push(i);
            storeFields.push("v" + i);
            axisFields.push("v" + i);
            series.push(
                {
                    type: "line",
                    axis: ["bottom", "right"],
                    xField: "timestamp",
                    yField: "v" + i,
                    title: me.ts[i],
                    tips: {
                        trackMouse: true,
                        width: 200,
                        height: 40,
                        renderer: (function(n) {
                            return function(storeItem, item) {
                                this.setTitle(
                                    Ext.String.format("Time: {0}<br/>Value: {1}",
                                        Ext.Date.format(storeItem.get("timestamp"), "Y-m-d H:i:s"),
                                        storeItem.get(n)
                                    )
                                );
                            }
                        })("v" + i)
                    }
                }
            );
        }

        me.store = Ext.create("Ext.data.Store", {
            fields: storeFields,
            data: []
        });

        me.scaleStore = Ext.create("Ext.data.Store", {
            fields: ["scale", "label", "step", "dateFormat"],
            data: [
                {scale: 3600, label: "1h", step: [Ext.Date.MINUTE, 5], dateFormat: "H:i"},
                {scale: 3600 * 3, label: "3h", step: [Ext.Date.MINUTE, 10], dateFormat: "H:i"},
                {scale: 3600 * 12, label: "12h", step: [Ext.Date.MINUTE, 15], dateFormat: "H:i"},
                {scale: 3600 * 24, label: "1d", step: [Ext.Date.MINUTE, 30], dateFormat: "H:i"},
                {scale: 3600 * 24 * 7, label: "7d", step: [Ext.Date.HOUR, 1], dateFormat: "H:i"},
                {scale: 3600 * 24 * 30, label: "30d", step: [Ext.Date.HOUR, 3], dateFormat: "H:i"},
            ]
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
                            fields: axisFields,
                            position: "right",
                            grid: true
                        },
                        {
                            type: "Time",
                            fields: ["timestamp"],
                            position: "bottom",
                            dateFormat: "H:i",
                            grid: true,
                            step: [Ext.Date.MINUTE, 5]
                        }
                    ],
                    series: series
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "bottom",
                    items: [
                        {
                            xtype: "button",
                            width: 20,
                            text: "&#9664;"
                        },
                        {
                            xtype: "slider",
                            minValue: 0,
                            maxValue: 100,
                            increment: 10,
                            flex: 1
                        },
                        {
                            xtype: "button",
                            width: 20,
                            text: "&#9654;"
                        },
                        {
                            xtype: "combobox",
                            width: 50,
                            queryMode: "local",
                            displayField: "label",
                            valueField: "scale",
                            store: me.scaleStore,
                            allowBlank: false,
                            value: 3600,
                            listeners: {
                                select: {
                                    scope: me,
                                    fn: me.onScale
                                }
                            }
                        }
                    ]
                }
            ]
        });
        //
        me.callParent();
        //
        me.chart = me.items.get(0);
        me.timeAxis = me.chart.axes.get(1);
        me.loadData(3600);
    },
    //
    loadData: function(scale, end) {
        var me = this,
            e = ((end || new Date()).getTime() / 1000) >> 0,
            b = e - scale;

        Ext.Ajax.request({
            url: "/pm/ts/data/",
            params: {
                ts: me.tsList,
                begin: b,
                end: e
            },
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    r = [];
                for(var ts in data.data) {
                    var tsdata = data.data[ts];
                    for(var i in tsdata) {
                        var v = tsdata[i],
                            x = {timestamp: new Date(v[0] * 1000)};
                        x["v" + ts] = v[1];
                        r.push(x);
                    }
                }
                // Switch interval
                me.timeAxis.fromDate = new Date(b * 1000);
                me.timeAxis.toDate = new Date(e * 1000);
                // Submit data to chart
                me.store.loadRawData(r);
            },
            failure: function(response) {
                NOC.error("Failed to get data");
            }
        });
    },
    //
    onScale: function(combo, records, opts) {
        var me = this,
            r = records[0];
        me.timeAxis.step = r.get("step");
        me.loadData(r.get("scale"));
    }
});
