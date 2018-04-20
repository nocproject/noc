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
    //    * fill - filled area
    //    * steps - staircase
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
        5 * 60, 15 * 60,
        3600, 6 * 3600, 12 * 3600,
        86400, 2 * 86400, 7 * 86400, 30 * 86400,
        365 * 86400
    ],

    scaleTitles: [
        "5 min", "15 min",
        "1h", "6h", "12h",
        "1 day", "2 days", "Week", "Month",
        "Year"
    ],

    // Current scale index
    scale: 0,
    //
    initComponent: function() {
        var me = this;
        //
        me.graph = null;
        me.tooltip = null;
        me.refreshTask = null;
        me.maxDataPoints = null;
        me.lastMin = null;
        me.lastMax = null;
        me.controls = {};
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
                data: [],
                lines: {
                    fill: item.fill || false,
                    steps: item.steps || false
                }
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
        return me.scales[me.scale];
    },
    // Get data request parameters
    getDataParams: function() {
        var me = this,
            ofactor = 1.2,
            w = me.getPlotSize().width,
            r = {
                format: me.format,
                target: me._series.map(function(item) {
                    return item.name;
                })
            };
        me.lastMax = me.getUntilTime();
        me.lastMin = Math.round(me.lastMax - me.getTimeRange());
        r.until = me.lastMax;
        r.from = Math.round(me.lastMax - me.getTimeRange() * ofactor);
        if(me.maxDataPoints) {
            r.maxDataPoints = me.maxDataPoints;
        } else {
            r.maxDataPoints = w;
        }
        r.maxDataPoints = Math.round(r.maxDataPoints * ofactor);
        console.log(
            "Requesting from=", r.from, " until=", r.until, " delta=",
            r.until - r.from, " max_points=", r.maxDataPoints,
            "scale_factor=", me.scales[me.scale]
        );
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
                    min: me.lastMin * 1000,
                    max: me.lastMax * 1000
                },
                yaxis: {
                    // tickFormatter: me.tickFormatter.suffixFormatter
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
        opts.xaxes[0].min = me.lastMin * 1000;
        opts.xaxes[0].max = me.lastMax * 1000;
        me.applyData(data);
        me.graph.setData(me._series);
        me.graph.setupGrid();
        me.graph.draw();
        x0 = Math.max(40, me.graph.getPlotOffset().left + 4);
        me.applyControls(x0);
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
    //
    applyControls: function(left) {
        var me = this,
            gs = 24,
            gss = 12,
            y = 12,
            x = left,
            disableMouseMove = function(e) {
                e.stopPropagation();
                me.hideTooltip();
            },
            i, ctl, cls, t,
            applyControl = function(name, style, left, title, handler) {
                ctl = me.controls[name];
                if(ctl) {
                    ctl.css({
                        left: left + "px"
                    });
                } else {
                    ctl = $("<i class=\"fa " + style + " fa-2x fa-fw noc-graph-control\" title=\"" + title + "\"></i>");
                    ctl
                        .css({
                            position: "absolute",
                            left: left + "px",
                            top: y + "px"
                        })
                        .appendTo(me.graph.getPlaceholder())
                        .mousemove(disableMouseMove)
                        .click(Ext.bind(handler, me));
                    me.controls[name] = ctl;
                }
            };
        // Update controls
        applyControl("back", "fa-caret-square-o-left", x, "Move backward", me.onBack);
        x += gs;
        applyControl("forward", "fa-caret-square-o-right", x, "Move forward", me.onForward);
        x += gs;
        applyControl("now", "fa-clock-o", x, "Move to current time", me.onNow);
        x += gs;
        y += gs;
        // Update zoom bar
        if(!me.controls.zoom) {
            me.controls.zoom = [];
            for(i = me.scales.length - 1; i >= 0; i--) {
                cls = i === me.scale ? "fa-square" : "fa-square-o";
                t = me.scaleTitles[i];
                ctl = $("<i class=\"fa " + cls + " fa-1x fa-fw noc-graph-control\" title=\"" + t + "\"></i>");
                ctl
                    .css({
                        position: "absolute",
                        left: left + "px",
                        top: y + "px"
                    })
                    .appendTo(me.graph.getPlaceholder())
                    .mousemove(disableMouseMove)
                    .click(Ext.bind(me.zoomTo, me, [i]));
                y += gss;
                me.controls.zoom.push(ctl);
            }
        } else {
            for(i = 0; i < me.scales.length; i ++) {
                if(me.scales.length - 1 - i === me.scale) {
                    me.controls.zoom[i].removeClass("fa-square-o").addClass("fa-square");
                } else {
                    me.controls.zoom[i].removeClass("fa-square").addClass("fa-square-o");
                }
            }
        }
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
                if(me.scales[s] >= delta) {
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
        var me = this,
            tw;
        me.tooltip.html(contents).css({
            display: "block",
            top: y
        });
        tw = me.tooltip.width();
        if(tw + x > me.graph.getPlaceholder().width()) {
            me.tooltip.css({
                left: x - 4 - tw
            });
        } else {
            me.tooltip.css({
                left: x + 4
            });
        }
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
    zoomTo: function(level) {
        var me = this;
        me.scale = Math.max(
            Math.min(level, me.scales.length - 1),
            0
        );
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
            me.untilTime = null;
        }
        me.hideTooltip();
        me.refreshGraph();
    },
    onNow: function() {
        var me = this;
        me.untilTime = null;
        me.hideTooltip();
        me.refreshGraph();
    }
});
