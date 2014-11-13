//---------------------------------------------------------------------
// NOC.core.Graph
// Graphite data renderer
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Graph");
console.debug("Using Flot " + $.plot.version);

Ext.define("NOC.core.Graph", {
    extend: "Ext.container.Container",

    // Refresh inverval in ms
    // null - fetch data and disable refresh
    refreshInterval: null,
    defaultNullAs: null,
    // Graphite data URL root
    dataURL: "/pm/render/",
    // Graphite data format
    format: "json",
    // Graph renderer, one of
    // * line
    // * area
    // * bar
    // * scatterplot
    renderer: "line",
    // List of time series
    // Available series options
    //    * name - target name
    //    * title - legend title
    //    * nullAs
    series: [],
    width: 900,
    height: 500,
    tpl: [
        '<div id="{cmpId}_g_container" class="noc-graph-container">',
        '</div>'
    ],
    // Graph time range
    timeRange: 24 * 3600,
    // Last point. null for now
    untilTime: null,

    initComponent: function () {
        var me = this;
        //
        me.graph = null;
        me.refreshTask = null;
        me.maxDataPoints = null;
        //
        me.parseData = {
            json: me.parseGraphiteJSONData,
            raw: me.parseGraphiteRawData
        }[me.format];
        me.prepareSeries();
        Ext.apply(me, {
            data: {
                cmpId: me.id,
                yAxisWidth: me.yAxisWidth,
                legendWidth: me.legendWidth
            }
        });
        me.callParent();
    },
    //
    prepareSeries: function() {
        var me = this;
        // Prepare targets
        me._targets = {};
        me._series = [];
        Ext.each(me.series, function (item) {
            var t = {
                name: item.name,
                label: item.title || item.name,
                nullAs: item.nullAs || me.defaultNullAs,
                data: []
            };
            me._targets[item.name] = t;
            me._series.push(t);
        });
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        me.refreshGraph();
    },
    //
    getTarget: function(target) {
        var me = this;
        return me._targets[target];
    },

    // Get data request URL
    getDataUrl: function() {
        var me = this;
        return me.dataURL
    },
    // Get data request parameters
    getDataParams: function() {
        var me = this,
            r = {
                format: me.format,
                target: me._series.map(function(item) {
                    return item.name;
                })
            };
        r.until = Math.round(me.untilTime !== null ? me.untilTime : Math.floor(new Date().getTime() / 1000));
        r.from = Math.round(r.until - me.timeRange);
        if(me.maxDataPoints) {
            r.maxDataPoints = me.maxDataPoints;
        } else {
            r.maxDataPoints = me.getPlotSize().width;
        }
        return r;
    },
    // Apply data to series
    applyData: function(data) {
        var me = this;
        Ext.each(data, function(item) {
            var t = me.getTarget(item.target);
            t.data = item.datapoints;
        });
    },
    // Get named div
    getNamedDiv: function(name) {
        var me = this;
        return me.el.getById(me.id + "_g_" + name, true)
    },
    //
    applyGraphSize: function() {
        var me = this,
            el, size;
        el = me.el.getById(me.id + "_g_container", false);
        size = me.getPlotSize();
        el.setSize(size.width, size.height);
        me.maxDataPoints = size.width;
        return el;
    },
    //
    createGraph: function (data) {
        var me = this,
            el, size, q;
        //
        me.applyData(data);
        // Create graph
        el = me.applyGraphSize();
        q = $(el.dom);
        q.bind("plotselected", Ext.bind(me.onPlotSelected, me));
        me.graph = $.plot(
            q,
            me._series,
            {
                xaxis: {
                    mode: "time",
                    timezone: "browser"
                },
                yaxis: {
                    tickFormatter: me.tickFormatter.suffixFormatter
                },
                selection: {
                    mode: "x"
                }
            }
        );
        //
        return me.graph;
    },
    //
    onResize: function() {
        var me = this;
        me.callParent();
        me.applyGraphSize();
    },

    getPlotSize: function() {
        var me = this;
        return me.getSize();
    },

    getAsImage: function(mimeType) {
        var me = this;
        mimeType = mimeType || "image/png";
        return me.graph.getCanvas().toDataURL(mimeType);
    },
    //
    updateGraph: function(data) {
        var me = this;
        me.applyData(data);
        me.graph.setData(me._series);
        me.graph.setupGrid();
        me.graph.draw();
    },
    //
    startRefresh: function() {
        var me = this;
        me.refreshTask = Ext.TaskManager.start({
            scope: me,
            run: me.refreshGraph,
            interval: me.refreshInterval * 1000
        });
    },
    // Request graphite data and update chart
    refreshGraph: function () {
        var me = this;
        Ext.Ajax.request({
            url: me.getDataUrl(),
            method: "GET",
            params: me.getDataParams(),
            scope: me,
            success: me.onSuccess,
            failure: me.onFailure
        });
    },
    // Called on successful AJAX response
    onSuccess: function (response) {
        var me = this,
            data;
        data = me.parseData(response.responseText);
        data = me.formatData(data);
        // Rickshaw.Series.zeroFill(data);
        if(!me.graph) {
            me.createGraph(data);
            if(me.refreshInterval) {
                var task = new Ext.util.DelayedTask(me.startRefresh, me);
                task.delay(me.refreshInterval * 1000);
            }
        } else {
            me.updateGraph(data);
        }
    },
    //
    onFailure: function(response) {
        throw "onFailure is not implemented yet";
    },
    // format received data
    formatData: function (data) {
        var me = this;
        // Add extra point when single point returned
        Ext.each(data, function (item) {
            if (item.datapoints.length === 1) {
                item.datapoints.push([item.datapoints[0][0], 1]);
            }
        });
        return data;
    },
    // Parse JSON format
    parseGraphiteJSONData: function (text) {
        var me = this,
            data = Ext.decode(text);
        Ext.each(data, function (item) {
            var t = me.getTarget(item.target);
            item.datapoints = item.datapoints.map(function (v) {
                return [
                    v[1] * 1000,
                    v[0] !== null && v[0] !== undefined ? v[0] : t.nullAs
                ];
            });
        });
        return data;
    },

    // @todo: Complete and test
    parseGraphiteRawData: function (text) {
        var r = [],  // {metric: , start: , step: , data:}
            nli, si, slice, match,
            rxMeta = /^([^,]+),(\d+),(\d+),(\d+)\|/;
        for (si = 0; si < text.length;) {
            nli = text.indexOf("\n", si);
            if (nli === -1) {
                nli = text.length;
            }
            slice = text.substring(si, nli);
            match = slice.match(rxMeta);
            if (match !== null) {
                r.push({
                    target: match[1],
                    start: +match[2] * 1000,
                    stop: +match[3] * 1000,
                    step: +match[4],
                    // @todo: Convert to datapoints
                    data: slice.substring(match[0].length).split(",").map(function (v) {
                        if (v === "None") {
                            return null;
                        } else {
                            return +v * 1000;
                        }
                    })
                });
            }
            si = nli + 1;
        }
        return r;
    },
    //
    onPlotSelected: function(event, ranges) {
        var me = this;
        $.each(me.graph.getXAxes(), function(_, axis) {
            me.untilTime = Math.round(ranges.xaxis.to / 1000);
            me.timeRange = Math.round((ranges.xaxis.to - ranges.xaxis.from) / 1000);
        });
        me.graph.clearSelection();
        me.refreshGraph();
    },
    //
    setSeries: function(series) {
        var me = this;
        console.log("setSeries", series);
        me.series = series;
        me.prepareSeries();
        if(me.graph) {
            me.graph = null;
        }
        me.refreshGraph();
    },
    // Formatters
    tickFormatter: {
        suffixFormatter: function(val, axis) {
            if(val > 1000000000000) {
                return (val / 1000000000000).toFixed(axis.tickDecimals) + "T"
            }
            if(val > 1000000000) {
                return (val / 1000000000).toFixed(axis.tickDecimals) + "G"
            }
            if(val > 1000000) {
                return (val / 1000000).toFixed(axis.tickDecimals) + "M"
            }
            if(val > 1000) {
                return (val / 1000).toFixed(axis.tickDecimals) + "K"
            }
            return val.toFixed(axis.tickDecimals) + "";
        }
    }
});
