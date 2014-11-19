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
        '</div>',
        '<div id="{cmpId}_g_tooltip" class="noc-graph-tooltip"></div>'
    ],
    // Last point. null for now
    untilTime: null,
    // Available scales
    scales: [
        1, 5, 10, 60, 300, 900,
        3600, 4 * 3600, 12 * 3600,
        24 * 3600, 7 * 24 * 3600, 30 * 24 * 3600
    ],
    // Current scale index
    scale: 1,
    //
    STEP: 4,

    initComponent: function() {
        var me = this;
        //
        me.graph = null;
        me.tooltip = null;
        me.refreshTask = null;
        me.maxDataPoints = null;
        me.lastRequest = null;
        //
        me.updateTooltipTimeout = null;
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
                label: item.label || item.title || item.name,
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
    // Returns effective until time
    getUntilTime: function() {
        var me = this;
        if(me.untilTime === null) {
            return Math.floor(new Date().getTime() / 1000);
        } else {
            return me.untilTime;
        }
    },
    // Returns effective time range in seconds
    getTimeRange: function() {
        var me = this;
        return Math.round(me.getPlotSize().width * me.scales[me.scale] / me.STEP);
    },
    // Get data request parameters
    getDataParams: function() {
        var me = this,
            sf = me.scales[me.scale],
            w = me.getPlotSize().width,
            r = {
                format: me.format,
                target: me._series.map(function(item) {
                    return item.name;
                })
            };
        r.until = me.getUntilTime();
        r.from = Math.round(r.until - me.getTimeRange());
        if(me.maxDataPoints) {
            r.maxDataPoints = me.maxDataPoints;
        } else {
            r.maxDataPoints = w;
        }
        console.log(
            "Requesting from=", r.from, " until=", r.until, " delta=",
            r.until - r.from, " max_points=", r.maxDataPoints,
            "scale_factor=", sf
        );
        me.lastRequest = r;
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
        q.bind("plothover", Ext.bind(me.onPlotHover, me));
        me.graph = $.plot(
            q,
            me._series,
            {
                xaxis: {
                    mode: "time",
                    timezone: "browser",
                    min: me.lastRequest.from * 1000,
                    max: me.lastRequest.until * 1000
                },
                yaxis: {
                    tickFormatter: me.tickFormatter.suffixFormatter
                },
                selection: {
                    mode: "x"
                },
                crosshair: {
                    mode: "x"
                },
                grid: {
                    hoverable: true
                }
            }
        );
        //
        me.tooltip = $(me.el.getById(me.id + "_g_tooltip", false).dom);
        //
        me.backButton = $("<i class='fa fa-backward noc-graph-control' title='Backward'></i>");
        me.backButton
            .css({
                position: "absolute",
                left: "30px",
                top: "20px"
            })
            .appendTo(q)
            .mousemove(function(e) {
                e.stopPropagation();
                me.hideTooltip();
            })
            .click(Ext.bind(me.onBack, me));

        //
        me.forwardButton = $("<i class='fa fa-forward noc-graph-control' title='Forward'></i>");
        me.forwardButton
            .css({
                position: "absolute",
                left: "42px",
                top: "20px"
            })
            .appendTo(q)
            .mousemove(function(e) {
                e.stopPropagation();
                me.hideTooltip();
            })
            .click(Ext.bind(me.onForward, me));

        //
        me.refreshButton = $("<i class='fa fa-refresh fa-2x noc-graph-control' title='Reload'></i>");
        me.refreshButton
            .css({
                position: "absolute",
                left: "30px",
                top: "36px"
            })
            .appendTo(q)
            .mousemove(function(e) {
                e.stopPropagation();
                me.hideTooltip();
            })
            .click(Ext.bind(me.refreshGraph, me));
        //
        me.zoomOutButton = $("<i class='fa fa-search-minus fa-2x noc-graph-control' title='Zoom out'></i>");
        me.zoomOutButton
            .css({
                position: "absolute",
                left: "30px",
                top: "60px"
            })
            .appendTo(q)
            .mousemove(function(e) {
                e.stopPropagation();
                me.hideTooltip();
            })
            .click(Ext.bind(me.onZoomOut, me));
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
        var me = this,
            x0,
            opts = me.graph.getOptions();
        opts.xaxes[0].min = me.lastRequest.from * 1000;
        opts.xaxes[0].max = me.lastRequest.until * 1000;
        me.applyData(data);
        me.graph.setData(me._series);
        me.graph.setupGrid();
        me.graph.draw();
        x0 = Math.max(40, me.graph.getPlotOffset().left + 4);
        me.backButton.css({
            left: x0 + "px"
        });
        me.forwardButton.css({
            left: (x0 + 12) + "px"
        });
        me.refreshButton.css({
            left: x0 + "px"
        });
        me.zoomOutButton.css({
            left: x0 + "px"
        });
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
        var me = this,
            w = me.getPlotSize().width,
            now = Math.floor(new Date().getTime() / 1000),
            u, s, delta;
        $.each(me.graph.getXAxes(), function(_, axis) {
            // Snap to scale
            delta = Math.round((ranges.xaxis.to - ranges.xaxis.from) / 1000);
            for(s=0; s < me.scales.length - 1; s++) {
                if(me.scales[s] * w / me.STEP >= delta) {
                    break;
                }
            }
            me.scale = s;
            u = Math.round(ranges.xaxis.to / 1000);
            if((u > now) && (u - delta) < now) {
                // Align to current timestamp
                u = now;
            }
            me.untilTime = u;
        });
        me.graph.clearSelection();
        me.refreshGraph();
    },
    //
    onPlotHover: function(event, pos, item) {
        var me = this;
        me.latestPosition = pos;
        if(!me.updateTooltipTimeout) {
            // @todo: Use extjs timeouts
            me.updateTooltipTimeout = setTimeout(
                Ext.bind(me.updateTooltip, me),
                50
            );
        }
    },
    // Find leftmost nearest x
    nearestX: function(data, x) {
        var mi = 0,
            ml = data.length - 1,
            ma = ml,
            ci, cx;
        while(mi <= ma) {
            ci = (mi + ma) / 2 | 0;
            cx = data[ci][0];
            if(cx < x) {
                if((ci < ml) && (data[ci + 1][0] > x)) {
                    return ci;
                }
                mi = ci + 1;
            } else if (cx > x) {
                ma = ci - 1;
            } else {
                return ci;
            }
        }
        return -1;
    },
    //
    updateTooltip: function() {
        var me = this,
            pos = me.latestPosition,
            dataset = me.graph.getData(),
            x = pos.x,
            p0, p1, i,
            v = ["<span class='time'>" + NOC.render.Timestamp(x / 1000) + "</span>"];
        me.updateTooltipTimeout = null;
        for (i = 0; i < dataset.length; i++) {
            var series = dataset[i],
                data=series.data,
                nx = me.nearestX(data, x),
                y;
            if (nx === -1) {
                continue;
            }
            // Interpolate value
            if (data[nx][0] == x || nx == data.length - 1) {
                y = data[nx][1];
            } else {
                p0 = data[nx];
                p1 = data[nx + 1];
                y = p0[1] + (p1[1] - p0[1]) * (x - p0[0]) / (p1[0] - p0[0]);
            }
            v.push("<i class='fa fa-square' style='color: " + series.color + "'></i> " + series.label + ": " + me.tickFormatter.suffixFormatter(y, {tickDecimals: true}));
        }
        // Update tooltip
        var o = me.graph.pointOffset({
            x: x,
            y: pos.y
        });
        me.setTooltip(o.left, o.top - 14 * (v.length / 2), v.join("<br>"));
    },
    //
    setTooltip: function(x, y, contents) {
        var me = this;
        me.tooltip.html(contents).css({
            display: "block",
            top: y,
            left: x + 4
        });
    },
    //
    hideTooltip: function() {
        var me = this;
        me.tooltip.css({
            display: "none"
        });
    },
    //
    setSeries: function(series) {
        var me = this;
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
    },
    //
    onZoomOut: function() {
        var me = this;
        me.scale = Math.min(me.scale + 1, me.scales.length - 1);
        me.hideTooltip();
        me.refreshGraph();
    },
    //
    onBack: function() {
        var me = this;
        me.untilTime = Math.round(me.getUntilTime() - me.getTimeRange() / 1.62);
        me.hideTooltip();
        me.refreshGraph();
    },
    //
    onForward: function() {
        var me = this,
            now = Math.round(new Date().getTime() / 1000);
        me.untilTime = Math.round(me.getUntilTime() + me.getTimeRange() / 1.62);
        if(me.untilTime > now) {
            me.untilTime = now;
        }
        me.hideTooltip();
        me.refreshGraph();
    }
});
