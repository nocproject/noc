//---------------------------------------------------------------------
// Network Map Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapPanel");

Ext.define("NOC.inv.map.MapPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.inv.map.ShapeRegistry"
    ],
    layout: "fit",
    autoScroll: true,
    app: null,
    readOnly: false,
    pollingInterval: 20000,

    svgFilters: {
        // Asbestos, #7f8c8d
        osUnknown: [127, 140, 141],
        // Emerald, #23cc71
        osOk: [46, 204, 113],
        // Sunflower, #f1c40f
        osAlarm: [241, 196, 15],
        //
        osUnreach: [64, 64, 64],
        // Pomegranade, #c0392b
        osDown: [192, 57, 43]
    },

    svgDefaultFilters: [
        '<filter id="highlight">' +
            '<feGaussianBlur stdDeviation="4" result="coloredBlur"/>' +
            '<feMerge>' +
                '<feMergeNode in="coloredBlur"/>' +
                '<feMergeNode in="SourceGraphic"/>' +
            '</feMerge>' +
        '</filter>',

        '<filter id="glow">' +
            '<feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>' +
            '<feMerge>' +
                '<feMergeNode in="coloredBlur"/>' +
                '<feMergeNode in="SourceGraphic"/>' +
            '</feMerge>' +
        '</filter>'
    ],

    // Link bandwidth style
    bwStyle: [
        [10000000000, {"stroke-width": "4px"}],  // 10G
        [1000000000, {"stroke-width": "2px"}],  // 1G
        [100000000, {"stroke-width": "1px"}],  // 100M
        [0, {"stroke-width": "1px", "stroke-dasharray": "10 5"}]
    ],
    // Link utilization style
    luStyle: [
        [.95, {stroke: "#ff0000"}],
        [.80, {stroke: "#990000"}],
        [.50, {stroke: "#ff9933"}],
        [.0, {stroke: "#006600"}]
    ],
    adminDownStyle: {
        stroke: "#7f8c8d"
    },
    operDownStyle: {
        stroke: "#c0392b"
    },
    // Object status filter names
    statusFilter: {
        0: "osUnknown",
        1: "osOk",
        2: "osAlarm",
        3: "osUnreach",
        4: "osDown"
    },

    // Link overlay modes
    LO_NONE: 0,
    LO_LOAD: 1,

    initComponent: function () {
        var me = this;

        me.shapeRegistry = NOC.inv.map.ShapeRegistry;
        me.objectNodes = {};
        me.objectsList = [];
        me.portObjects = {};  // port id -> object id
        me.linkBw = {};  // Link id -> {in: ..., out: ...}
        me.isInteractive = false;  // Graph is editable
        me.isDirty = false;  // Graph is changed
        me.statusPollingTaskId = null;
        me.overlayPollingTaskId = null;
        me.currentHighlight = null;
        me.overlayMode = me.LO_NONE;
        me.interfaceMetrics = [];

        Ext.apply(me, {
            items: [
                {
                    xtype: "component",
                    autoScroll: true,
                    layout: "fit",
                    style: {
                        background: "#ecf0f1"
                    }
                }
            ]
        });
        me.callParent();
    },

    afterRender: function () {
        var me = this;
        me.callParent();
        new_load_scripts([
            "/ui/pkg/lodash/lodash.min.js",
            "/ui/pkg/backbone/backbone.min.js",
            "/ui/pkg/joint/joint.min.js"
        ], me, me.initMap);
    },

    // Initialize JointJS Map
    initMap: function () {
        var me = this,
            dom = me.items.first().el.dom;
        me.graph = new joint.dia.Graph;
        me.graph.on("change", Ext.bind(me.onChange, me));
        me.paper = new joint.dia.Paper({
            el: dom,
            model: me.graph,
            gridSize: 10,
            gridWidth: 10,
            gridHeight: 10,
            interactive: Ext.bind(me.onInteractive, me)
        });
        // Apply SVG filters
        Ext.Object.each(me.svgFilters, function(fn) {
            var ft = me.getFilter(fn, me.svgFilters[fn]),
                fd = V(ft);
            V(me.paper.svg).defs().append(fd);
        });
        Ext.each(me.svgDefaultFilters, function(f) {
            V(me.paper.svg).defs().append(V(f));
        });
        // Subscribe to events
        me.paper.on("cell:pointerdown", Ext.bind(me.onCellSelected, me));
        me.paper.on("blank:pointerdown", Ext.bind(me.onBlankSelected, me));
        me.paper.on("cell:highlight", Ext.bind(me.onCellHighlight));
        me.paper.on("cell:unhighlight", Ext.bind(me.onCellUnhighlight));
        //me.createContextMenus();
        me.fireEvent("mapready");
    },

    // Load segment data
    loadSegment: function(segmentId, forceSpring) {
        var me = this,
            url = "/inv/map/" + segmentId + "/data/";
        if(forceSpring) {
            url += "?force=spring"
        }
        me.segmentId = segmentId;
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderMap(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },

    //
    renderMap: function(data) {
        var me = this,
            cells = [];

        me.isInteractive = false;
        me.isDirty = false;
        me.currentHighlight = null;
        me.objectNodes = {};
        me.linkBw = {};
        me.objectsList = [];
        me.interfaceMetrics = [];
        me.graph.clear();
        // Create nodes
        Ext.each(data.nodes, function(node) {
            cells.push(me.createNode(node));
            Ext.each(node.ports, function(port) {
                me.portObjects[port.id] = node.id;
                Ext.each(port.ports, function(ifname) {
                    me.interfaceMetrics.push({
                        id: port.id,
                        tags: {
                            object: node.name,
                            interface: ifname
                        }
                    });
                });
            })
        });
        // Create links
        Ext.each(data.links, function(link) {
            cells.push(me.createLink(link));
        });
        me.graph.addCells(cells);
        me.paper.fitToContent();
        // Run status polling
        if(me.statusPollingTaskId) {
            me.getObjectStatus();
        } else {
            me.statusPollingTaskId = Ext.TaskManager.start({
                run: me.getObjectStatus,
                interval: me.pollingInterval,
                scope: me
            });
        }
    },

    //
    createNode: function(data) {
        var me = this,
            sclass, node;

        sclass = me.shapeRegistry.getShape(data.shape);
        node = new sclass({
            id: data.type + ":" + data.id,
            external: data.external,
            position: {
                x: data.x,
                y: data.y
            },
            attrs: {
                text: {
                    text: data.name
                },
                image: {
                    width: data.width,
                    height: data.height
                }
            },
            size: {
                width: data.width,
                height: data.height
            },
            data: {
                type: data.type,
                id: data.id
            }
        });
        me.objectNodes[data.id] = node;
        console.log("node>", node);
        me.objectsList.push(data.id);
        return node;
    },
    //
    createLink: function(data) {
        var me = this,
            cfg, src, dst, connector,
            getConnectionStyle=function(bw) {
                for(var i = 0; i < me.bwStyle.length; i++) {
                    var s = me.bwStyle[i];
                    if(s[0] <= bw) {
                        return s[1];
                    }
                }
            };

        src = me.objectNodes[me.portObjects[data.ports[0]]];
        dst = me.objectNodes[me.portObjects[data.ports[1]]];

        cfg = {
            id: data.type + ":" + data.id,
            source: {
                id: src
            },
            target: {
                id: dst
            },
            attrs: {
                ".tool-remove": {
                    display: "none"  // Disable "Remove" circle
                },
                ".marker-arrowheads": {
                    display: "none"  // Do not show hover arrowheads
                },
                ".connection": getConnectionStyle(data.bw)
            },
            data: {
                type: data.type,
                id: data.id,
                ports: data.ports
            },
            labels: [
                // Balance marker
                // @todo: Make hidden by default
                {
                    position: 0.5,
                    attrs: {
                        text: {
                            fill: "black",
                            text: "\uf111",
                            "font-family": "FontAwesome",
                            "font-size": 5,
                            visibility: "hidden"
                        },
                        rect: {
                            visibility: "hidden"
                        }
                    }
                }
            ]
        };
        //
        if(data.connector) {
            cfg.connector = {name: data.connector};
        } else {
            cfg.connector = {name: "normal"};
        }

        if(data.vertices && data.vertices.length > 0) {
            cfg.vertices = data.vertices;
        }
        //
        if(src.get("external")) {
            cfg["attrs"][".marker-source"] = {
                fill: "black",
                d: "M 10 0 L 0 5 L 10 10 z"
            };
        }
        if(dst.get("external")) {
            cfg["attrs"][".marker-target"] = {
                fill: "black",
                d: "M 10 0 L 0 5 L 10 10 z"
            };
        }
        //
        me.linkBw[data.id] = {
            in: data.in_bw,
            out: data.out_bw
        };
        //
        return new joint.dia.Link(cfg);
    },
    //
    unhighlight: function() {
        var me = this;
        if(me.currentHighlight) {
            me.currentHighlight.unhighlight();
            me.currentHighlight = null;
        }
    },
    //
    onCellSelected: function(view, evt, x, y) {
        var me = this,
            data = view.model.get("data");
        me.unhighlight();
        switch(data.type) {
            case "managedobject":
                view.highlight();
                me.currentHighlight = view;
                me.app.inspectManagedObject(data.id);
                break;
            case "link":
                me.app.inspectLink(data.id);
                break;
        }
    },
    onBlankSelected: function() {
        var me = this;
        me.unhighlight();
        me.app.inspectSegment();
    },
    // Change interactive flag
    setInteractive: function(interactive) {
        var me = this;
        me.isInteractive = interactive;
    },
    //
    onInteractive: function() {
        var me = this;
        return me.isInteractive;
    },
    //
    onChange: function() {
        var me = this;
        me.isDirty = true;
        me.fireEvent("changed");
    },

    save: function() {
        var me = this,
            bbox = me.paper.getContentBBox(),
            r = {
                nodes: [],
                links: [],
                width: bbox.width - bbox.x,
                height: bbox.height - bbox.y
            };
        // Get nodes position
        Ext.each(me.graph.getElements(), function(e) {
            var v = e.get("id").split(":");
            r.nodes.push({
                type: v[0],
                id: v[1],
                x: e.get("position").x,
                y: e.get("position").y
            });
        });
        // Get links position
        Ext.each(me.graph.getLinks(), function(e) {
            var vertices = e.get("vertices"),
                v = e.get("id").split(":"),
                lr = {
                    type: v[0],
                    id: v[1],
                    connector: e.get("connector").name
                };
            if(vertices) {
                lr.vertices = vertices.map(function(o) {
                    return {
                        x: o.x,
                        y: o.y
                    }
                });
            }
            r.links.push(lr);
        });
        Ext.Ajax.request({
            url: "/inv/map/" + me.segmentId + "/data/",
            method: "POST",
            jsonData: r,
            scope: me,
            success: function(response) {
                NOC.info("Map has been saved");
                me.isDirty = false;
                me.app.saveButton.setDisabled(true);
            },
            failure: function() {
                NOC.error("Failed to save data");
            }
     });
    },

    getObjectStatus: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/map/objects_statuses/",
            method: "POST",
            jsonData: {
                objects: me.objectsList
            },
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.applyObjectStatuses(data);
            },
            failure: function() {

            }
        });
    },

    resetOverlayData: function() {
        var me = this;
        Ext.each(me.graph.getLinks(), function(link) {
            link.attr({
                ".connection": {
                    filter: "none",
                    stroke: "black"
                }
            });

            link.label(0, {
                attrs: {
                    text: {
                        visibility: "hidden"
                    }
                }
            });
        });
    },

    getOverlayData: function() {
        var me = this;
        switch(me.overlayMode) {
            case me.LO_LOAD:
                var r = [];
                Ext.each(me.interfaceMetrics, function(m) {
                    r.push({
                        id: m.id,
                        metric: "Interface | Load | In",
                        tags: m.tags
                    });
                    r.push({
                        id: m.id,
                        metric: "Interface | Load | Out",
                        tags: m.tags
                    });
                });
                Ext.Ajax.request({
                    url: "/inv/map/metrics/",
                    method: "POST",
                    jsonData: {
                        metrics: r
                    },
                    scope: me,
                    success: function(response) {
                        me.setLoadOverlayData(
                            Ext.decode(response.responseText)
                        );
                    },
                    failure: function() {}
                });
                break;
        }
    },

    applyObjectStatuses: function(data) {
        var me = this;
        Ext.Object.each(data, function(s) {
            var node = me.objectNodes[s];
            if(!node) {
                return;
            }
            node.setFilter(me.statusFilter[data[s]]);
        });
    },
    //
    svgFilterTpl: new Ext.XTemplate(
        '<filter id="{id}">',
            '<feColorMatrix type="matrix" color-interpolation-filters="sRGB" ',
            'values="',
                '{r0} 0    0    0 {r1} ',
                '0    {g0} 0    0 {g1} ',
                '0    0    {b0} 0 {b1} ',
                '0    0    0    1 0    " />',
        '</filter>'
    ),
    //
    // Get SVG filter text
    //   c = [R, G, B]
    //
    getFilter: function(filterId, c) {
        var me = this,
            r1 = c[0] / 256.0,
            g1 = c[1] / 256.0,
            b1 = c[2] / 256.0,
            r0 = (256.0 - c[0]) / 256.0,
            g0 = (256.0 - c[1]) / 256.0,
            b0 = (256.0 - c[2]) / 256.0;
        return me.svgFilterTpl.apply({
            id: filterId,
            r0: r0,
            r1: r1,
            g0: g0,
            g1: g1,
            b0: b0,
            b1: b1
        });
    },

    stopPolling: function() {
        var me = this;
        if(me.statusPollingTaskId) {
            Ext.TaskManager.stop(me.statusPollingTaskId);
            me.statusPollingTaskId = null;
        }
        if(me.overlayPollingTaskId) {
            Ext.TaskManager.stop(me.overlayPollingTaskId);
            me.overlayPollingTaskId = null;
        }
    },

    setOverlayMode: function(mode) {
        var me = this;
        // Stop polling when necessary
        if(mode == me.LO_NONE && me.overlayPollingTaskId) {
            Ext.TaskManager.stop(me.overlayPollingTaskId);
            me.overlayPollingTaskId = null;
        }
        me.overlayMode = mode;
        // Start polling when necessary
        if(mode !== me.LO_NONE && !me.overlayPollingTaskId) {
            me.overlayPollingTaskId = Ext.TaskManager.start({
                run: me.getOverlayData,
                interval: me.pollingInterval,
                scope: me
            });
        }
        //
        if(mode === me.LO_NONE) {
            me.resetOverlayData();
        } else {
            me.getOverlayData();
        }
    },

    // Display links load
    // data is dict of
    // metric -> {ts: .., value: }
    setLoadOverlayData: function(data) {
        var me = this;
        console.log("setLoadOverlayData", data);
        Ext.each(me.graph.getLinks(), function(link) {
            var sIn, sOut, dIn, dOut, bw,
                td, dt, lu, cfg, tb, balance,
                ports = link.get("data").ports,
                linkId = link.get("data").id,
                luStyle = null,
                getTotal = function(port, metric) {
                    if(data[port] && data[port][metric]) {
                        return data[port][metric];
                    } else {
                        return 0.0;
                    }
                },
                getStatus = function(port, status) {
                    if(data[port] && data[port][status] !== undefined) {
                        return data[port][status];
                    } else {
                        return true;
                    }
                };
            //
            if(!getStatus(ports[0], "admin_status") || !getStatus(ports[1], "admin_status")) {
                // Administratively down
                link.attr({
                    ".connection": me.adminDownStyle
                });
                luStyle = Ext.apply({
                    attrs: {
                        text: me.adminDownStyle
                    },
                    visibility: "visible",
                    position: 0.5,
                    fill: me.adminDownStyle.stroke
                }, me.adminDownStyle);

                luStyle.fill = luStyle.stroke;
                luStyle.visibility = "visible";
                luStyle.text = "\uf00d";
                luStyle["font-size"] = 10;
                link.label(0, {attrs: {text: luStyle}});
                link.label(0, {position: 0.5});
            } else if(!getStatus(ports[0], "oper_status") || !getStatus(ports[1], "oper_status")) {
                // Administratively down
                link.attr({
                    ".connection": me.operDownStyle
                });
                luStyle = Ext.apply({
                    attrs: {
                        text: me.operDownStyle
                    },
                    visibility: "visible",
                    position: 0.5,
                    fill: me.operDownStyle.stroke
                }, me.operDownStyle);

                luStyle.fill = luStyle.stroke;
                luStyle.visibility = "visible";
                luStyle.text = "\uf0e7";
                luStyle["font-size"] = 10;
                link.label(0, {attrs: {text: luStyle}});
                link.label(0, {position: 0.5});
            } else {
                // Get bandwidth
                sIn = getTotal(ports[0], "Interface | Load | In");
                sOut = getTotal(ports[0], "Interface | Load | Out");
                dIn = getTotal(ports[1], "Interface | Load | In");
                dOut = getTotal(ports[1], "Interface | Load | Out");

                bw = me.linkBw[linkId];
                // Destination to target
                td = Math.max(sOut, dIn);
                // Target to destination
                dt = Math.max(sIn, dOut);
                if (bw) {
                    // Link utilization
                    lu = 0.0;
                    if (bw.in) {
                        lu = Math.max(lu, dt / bw.in);
                    }
                    if (bw.out) {
                        lu = Math.max(lu, td / bw.out);
                    }
                    // Apply proper style according to load
                    for (var i = 0; i < me.luStyle.length; i++) {
                        var t = me.luStyle[i][0],
                            style = me.luStyle[i][1];
                        if (lu >= t) {
                            cfg = {
                                filter: "url(#glow)"
                            };
                            cfg = Ext.apply(cfg, style);
                            luStyle = cfg;
                            link.attr({
                                ".connection": cfg
                            });
                            break;
                        }
                    }
                }
                // Show balance point
                tb = td + dt;
                if (tb > 0) {
                    balance = td / tb;
                    link.label(0, {position: balance});
                    if (luStyle) {
                        luStyle.fill = luStyle.stroke;
                        luStyle.visibility = "visible";
                        luStyle.text = "\uf111";
                        luStyle["font-size"] = 5;
                        link.label(0, {attrs: {text: luStyle}});
                    }
                }
            }
        });
    },

    onCellHighlight: function(view, el) {
        var me = this;
        V(el).attr("filter", "url(#highlight)");
    },

    onCellUnhighlight: function(view, el) {
        var me = this;
        V(el).attr("filter", "");
    },

    resetLayout: function(forceSpring) {
        var me = this;
        if(!me.segmentId) {
            return;
        }
        forceSpring = forceSpring || false;
        Ext.Ajax.request({
            url: "/inv/map/" + me.segmentId + "/data/",
            method: "DELETE",
            scope: me,
            success: function(response) {
                me.loadSegment(me.segmentId, forceSpring);
            },
            failure: function() {
                NOC.error("Failed to reset layout");
            }
        });
    }
});
