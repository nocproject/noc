//---------------------------------------------------------------------
// NOC.core.Graph
// Graphite data renderer
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Graph");

Ext.define("NOC.core.Graph", {
    extend: "Ext.container.Container",

    // Refresh inverval in ms
    // null - fetch data and disable refresh
    refreshInterval: null,
    defaultInterpolation: "step-before",
    colorScheme: "classic9",
    defaultHoverRenderer: Ext.identityFn,
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
    //
    // List of time series
    // Available series options
    //    * name - target name
    //    * title - legend title
    //    * color - graph color (auto-assigned from pallete by default)
    //    * min
    //    * max
    //    * nullAs
    //    * interpolation
    //    * hoverRenderer ???
    series: [],
    width: 900,
    height: 500,
    legendWidth: 150,
    yAxisWidth: 40,

    tpl: [
        '<div id="{cmpId}_g_container" class="noc-graph-container">',
        '    <div id="{cmpId}_g_y_axis" class="noc-graph-y-axis" style="width: {yAxisWidth}px"></div>',
        '    <div id="{cmpId}_g_graph" class="noc-graph-graph" style="margin-left: {yAxisWidth}px"></div>',
        '    <div id="{cmpId}_g_legend" class="noc-graph-legend" style="width: {legendWidth}px"></div>',
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
        //
        me.parseGraphiteData = {
            "json": me.parseGraphiteJSONData,
            "raw": me.parseGraphiteRawData
        }[me.format];
        // Color palette for unassigned target colors
        me.palette = new Rickshaw.Color.Palette(me.colorScheme);
        // Prepare targets
        me._targets = {};
        me._series = [];
        Ext.each(me.series, function (item) {
            var t = {
                name: item.name,
                title: item.title || item.name,
                color: item.color || me.palette.color(),
                nullAs: item.nullAs || me.defaultNullAs
            };
            me._targets[item.name] = t;
            me._series.push(t);
        });

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
        r.until = me.untilTime !== null ? me.untilTime : Math.floor(new Date().getTime() / 1000);
        r.from = r.until - me.timeRange;
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
    createGraph: function (data) {
        var me = this;
        //
        me.applyData(data);
        // Create graph
        me.graph = new Rickshaw.Graph({
            element: me.getNamedDiv("graph"),
            width: me.width - me.legendWidth - me.yAxisWidth - 25,  // Legend padding 10 + 4
            height: me.height,
            stroke: true,
            renderer: me.renderer,
            series: me._series
        });
        // Create X-axis
        var xAxis = new Rickshaw.Graph.Axis.Time({
            graph: me.graph,
            ticksTreatment: "glow",
            timeFixture: new Rickshaw.Fixtures.Time.Local()
        });

        xAxis.render();
        // Create Y-axis
        var yAxis = new Rickshaw.Graph.Axis.Y({
            element: me.getNamedDiv("y_axis"),
            graph: me.graph,
            orientation: "left",
            tickFormat: Rickshaw.Fixtures.Number.formatKMBT
        });

        // Hover detail
        new Rickshaw.Graph.HoverDetail({
            graph: me.graph,
            xFormatter: function (x) {
                return new Date(x * 1000).toString();
            }
        });
        // Create legend
        new Rickshaw.Graph.Legend({
            graph: me.graph,
            element: me.getNamedDiv("legend")
        });
        //
        return me.graph;
    },
    //
    updateGraph: function(data) {
        var me = this;
        me.applyData(data);
        me.graph.render();
    },
    //
    startRefresh: function() {
        var me = this;
        me.refreshTask = Ext.TaskManager.start({
            scope: me,
            run: me.refreshGraph,
            interval: me.refreshInterval
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
        data = me.parseGraphiteData(response.responseText);
        data = me.formatData(data);
        // Rickshaw.Series.zeroFill(data);
        if(!me.graph) {
            me.createGraph(data);
            me.graph.render();
            if(me.refreshInterval) {
                var task = new Ext.util.DelayedTask(me.startRefresh, me);
                task.delay(me.refreshInterval);
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
                return {
                    x: v[1],
                    y: v[0] !== null && v[0] !== undefined ? v[0] : t.nullAs
                };
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
                            return +v;
                        }
                    })
                });
            }
            si = nli + 1;
        }
        return r;
    }
});
