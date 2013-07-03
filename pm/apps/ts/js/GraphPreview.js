//---------------------------------------------------------------------
// GraphPreview model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.GraphPreview");

Ext.define("NOC.pm.ts.GraphPreview", {
    extend: "Ext.panel.Panel",
    layout: "fit",
    app: null,
    items: [
        {
            xtype: "container"
        }
    ],
    autoScroll: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            iconCls: "icon_arrow_undo",
                            scope: me,
                            handler: me.onClose
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },

    setTS: function(tses) {
        var me = this,
            cId = "#" + me.items.first().id,  // Container id
            dataGetters;
        me.tses = tses;
        // Cubism context
        me.context = cubism.context().step(5000).size(600);
        // Build data getters closure
        dataGetters = Ext.Object.getKeys(tses)
            .map(Ext.bind(me.getRequest, me));

        d3.select(cId).selectAll(".horizon").call(function(div) {
            // Horizon bar
            div.data(dataGetters)
            .enter()
            .insert("div", ".bottom-horizon")
            .attr("class", "horizon")
            .call(
                me.context.horizon() //.extent([-10, 10])
                .height(120)
            );

            // Axis
            div.data(["bottom-horizon"]).enter()
            .append("div")
            .attr("class", function(d) {
                return d + " axis";
            })
            .each(function(d) {
                d3.select(this).call(
                    me.context.axis()
                        .ticks(12)
                        .orient(d)
                );
            });

            // Axis
            div.data(dataGetters)
            .append("div")
            .attr("class", "rule")
            .call(me.context.rule());
        });
        //
        me.context.on("focus", function(i) {
            d3.selectAll(".value")
                .style("left",
                    i === null ? null : Math.min(i + 4, me.context.size() - 48) + "px"
                );
        });
    },

    getRequest: function(ts) {
        var me = this;
        return me.context.metric(function(start, stop, step, callback) {
            // Convert start/stop to ms
            start = +start;
            stop = +stop;
            Ext.Ajax.request({
                url: "/pm/ts/step/" + ts + "/",
                method: "GET",
                params: {
                    start: start / 1000,
                    stop: stop / 1000,
                    step: step / 1000
                },
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    callback(null, data.map(function(v) {
                        return v === null ? NaN : v;
                    }));
                },
                failure: function() {}
            });
        }, me.tses[ts]);
    },
    //
    onClose: function() {
        var me = this;
        me.context.stop();
        me.app.showGrid();
    }
});
