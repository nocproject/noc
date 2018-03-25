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
    pollingInterval: 180000,

    svgFilters: {
        // Asbestos, #7f8c8d
        osUnknown: [127, 140, 141],
        // Emerald, #23cc71
        osOk: [46, 204, 113],
        // Sunflower, #f1c40f
        osAlarm: [241, 196, 15],
        // #404040
        osUnreach: [64, 64, 64],
        // Pomegranade, #c0392b
        osDown: [192, 57, 43]
    },

    CAP_STP: "Network | STP",

    svgDefaultFilters: [
        '<filter id="highlight">' +
        '<feGaussianBlur stdDeviation="4" result="coloredBlur"/>' +
        '<feMerge>' +
        '<feMergeNode in="coloredBlur"/>' +
        '<feMergeNode in="SourceGraphic"/>' +
        '</feMerge>' +
        '</filter>',

        '<filter id="glow" filterUnits="userSpaceOnUse">' +
        '<feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>' +
        '<feMerge>' +
        '<feMergeNode in="coloredBlur"/>' +
        '<feMergeNode in="SourceGraphic"/>' +
        '</feMerge>' +
        '</filter>',

        '<filter x="0" y="0" width="1" height="1" id="solid">' +
        '<feFlood flood-color="rgb(236,240,241)"/>' +
        '<feComposite in="SourceGraphic"/>' +
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
    stpBlockedStyle: {
        stroke: "#8e44ad"
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
    // Link status
    LINK_OK: 0,
    LINK_ADMIN_DOWN: 1,
    LINK_OPER_DOWN: 2,
    LINK_STP_BLOCKED: 3,

    resizeHandles: 'onResize',

    initComponent: function() {
        var me = this;

        me.shapeRegistry = NOC.inv.map.ShapeRegistry;
        me.hasStp = false;
        me.objectNodes = {};
        me.objectsList = [];
        me.portObjects = {};  // port id -> object id
        me.currentStpRoots = {};
        me.currentStpBlocked = {};
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
        //
        me.nodeMenu = Ext.create("Ext.menu.Menu", {
            items: [
                {
                    text: __("View Card"),
                    glyph: NOC.glyph.eye,
                    scope: me,
                    handler: me.onNodeMenuViewCard,
                    menuOn: ['managedobject', 'link']
                },
                {
                    text: __("Edit"),
                    glyph: NOC.glyph.pencil,
                    scope: me,
                    handler: me.onNodeMenuEdit,
                    menuOn: ['managedobject', 'link']
                },
                {
                    text: __("Show dashboard"),
                    glyph: NOC.glyph.line_chart,
                    scope: me,
                    handler: me.onNodeMenuDashboard,
                    menuOn: ['managedobject', 'link']
                },
                {
                    text: __("To maintaince mode"),
                    glyph: NOC.glyph.plus,
                    scope: me,
                    handler: me.onNodeMenuMaintainceMode,
                    menuOn: 'managedobject'
                },
                {
                    text: __("Create new maintaince"),
                    glyph: NOC.glyph.wrench,
                    scope: me,
                    handler: me.onNodeMenuNewMaintaince,
                    menuOn: 'managedobject'
                },
                {
                    text: __("Add to group"),
                    glyph: NOC.glyph.shopping_basket,
                    scope: me,
                    handler: me.onNodeMenuAddToBasket,
                    menuOn: 'managedobject'
                }
            ]
        });
        me.segmentMenu = Ext.create("Ext.menu.Menu", {
            items: [
                {
                    text: __("Add all objects to group"),
                    glyph: NOC.glyph.shopping_basket,
                    scope: me,
                    handler: me.onSegmentMenuAddToBasket,
                    menuOn: ['managedobject', 'link']
                }
            ]
        });
        me.nodeMenuObject = null;
        me.nodeMenuObjectType = null;
        //
        me.callParent();
    },

    afterRender: function() {
        var me = this;
        me.callParent();
        new_load_scripts([
            "/ui/pkg/lodash/lodash.min.js",
            "/ui/pkg/backbone/backbone.min.js",
            "/ui/pkg/joint/joint.min.js"
        ], me, me.initMap);
    },

    // Initialize JointJS Map
    initMap: function() {
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
        me.paper.on("cell:pointerdblclick", Ext.bind(me.onCellDoubleClick, me));
        me.paper.on("blank:pointerdown", Ext.bind(me.onBlankSelected, me));
        me.paper.on("cell:highlight", Ext.bind(me.onCellHighlight));
        me.paper.on("cell:unhighlight", Ext.bind(me.onCellUnhighlight));
        me.paper.on("cell:contextmenu", Ext.bind(me.onContextMenu, me));
        me.paper.on("blank:contextmenu", Ext.bind(me.onSegmentContextMenu, me));
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
                var data = Ext.decode(response.responseText);
                if(data.error) {
                    NOC.error(data.error);
                } else {
                    me.renderMap(data);
                }
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    },

    //
    renderMap: function(data) {
        var me = this,
            nodes = [],
            links = [];

        me.isInteractive = false;
        me.isDirty = false;
        me.currentHighlight = null;
        me.objectNodes = {};
        me.linkBw = {};
        me.objectsList = [];
        me.interfaceMetrics = [];
        me.currentStpRoots = {};
        me.graph.clear();
        // Create nodes
        Ext.each(data.nodes, function(node) {
            if(!me.app.viewAllNodeButton.pressed && data.links.length > data.max_links && node.external === true) {
                // skip create
                return;
            }
            nodes.push(me.createNode(node));
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
            });
        });
        // Create links
        Ext.each(data.links, function(link) {
            if(me.objectNodes[me.portObjects[link.ports[0]]] &&
                me.objectNodes[me.portObjects[link.ports[1]]])
                links.push(me.createLink(link));
        });
        me.graph.addCells(nodes);
        me.graph.addCells(links);

        nodes.forEach(function(node) {
            node.toFront();
        });
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
        me.hasStp = data.caps.indexOf("Network | STP") !== -1;
        me.app.viewStpButton.setDisabled(!me.hasStp);
        me.setPaperDimension();
        me.fireEvent("renderdone");
    },

    //
    createNode: function(data) {
        var me = this,
            sclass, node;
        var dataName = data.name;
        if(dataName.indexOf('#') > 0) {
            var tokens = data.name.split("#");
            tokens.pop();
            dataName = tokens.join('#');
        }
        var name = me.breakText(dataName, {width: data.shape_width * 2});
        sclass = me.shapeRegistry.getShape(data.shape);
        node = new sclass({
            id: data.type + ":" + data.id,
            external: data.external,
            name: name,
            address: data.address,
            position: {
                x: data.x,
                y: data.y
            },
            attrs: {
                text: {
                    text: name
                },
                image: {
                    width: data.shape_width,
                    height: data.shape_height
                }
            },
            size: {
                width: data.shape_width,
                height: data.shape_height
            },
            data: {
                type: data.type,
                id: data.id,
                caps: data.caps
            }
        });
        me.objectNodes[data.id] = node;
        if(data.type === "managedobject") {
            me.objectsList.push(data.id)
        }
        return node;
    },
    //
    createLink: function(data) {
        var me = this,
            cfg, src, dst, connector,
            getConnectionStyle = function(bw) {
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
                            text: __("\uf111"),
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
        me.nodeMenu.hide();
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
            case "cloud":
                view.highlight();
                me.currentHighlight = view;
                me.app.inspectCloud(data.id);
                break
        }
    },

    onSegmentContextMenu: function(evt) {
        var me = this;

        evt.preventDefault();
        me.segmentMenu.showAt(evt.clientX, evt.clientY);
    },

    onContextMenu: function(view, evt, x, y) {
        var me = this;

        evt.preventDefault();
        me.nodeMenuObject = view.model.get("id").split(":")[1];
        me.nodeMenuObjectType = view.model.get('data').type;
        if('wrench' !== me.nodeMenuObjectType) {
            me.nodeMenu.items.items.map(function(item) {
                item.setVisible(item.menuOn.indexOf(me.nodeMenuObjectType) !== -1)
            });
            me.nodeMenu.showAt(evt.clientX, evt.clientY);
        }
    },
    onCellDoubleClick: function(view, evt, x, y) {
        var me = this,
            data = view.model.get("data");
        if(data.type === "managedobject") {
            window.open(
                "/api/card/view/managedobject/" + data.id + "/"
            );
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
    //
    onRotate: function() {
        var me = this,
            bbox = me.paper.getContentBBox();
        Ext.each(me.graph.getElements(), function(e) {
            var pos = e.get("position");
            e.set("position", {
                x: -pos.y + bbox.height,
                y: pos.x
            })
        });
        me.setPaperDimension();
    },
    //
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
            if('wrench' !== e.get('data').type) {
                var v = e.get("id").split(":");
                r.nodes.push({
                    type: v[0],
                    id: v[1],
                    x: e.get("position").x,
                    y: e.get("position").y
                });
            }
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
                NOC.info(__("Map has been saved"));
                me.isDirty = false;
                me.app.saveButton.setDisabled(true);
            },
            failure: function() {
                NOC.error(__("Failed to save data"));
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
                    stroke: "black"
                },
                '.': {filter: 'none'}
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
                    failure: Ext.emptyFn
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
            node.setFilter(me.statusFilter[data[s] & 0x1f]); // Remove maintenance bit
            var embeddedCells = node.getEmbeddedCells();
            if(data[s] & 0x20) {
                if(embeddedCells.length === 0) {
                    var nodeSize = node.get('size');
                    var size = nodeSize.width / 3;
                    var wrench = new joint.shapes.basic.Circle({
                        position: {
                            x: node.get('position').x + nodeSize.width - size,
                            y: node.get('position').y - size / 2
                        },
                        size: {width: size, height: size},
                        attrs: {
                            circle: {fill: '#FFFFFF', stoke: '#FFFFFF'},
                            text: {text: '\uf0ad', 'font-family': 'FontAwesome', 'font-size': size / 1.7}
                        }
                    });
                    wrench.set('data', {type: 'wrench'});
                    node.embed(wrench);
                    me.graph.addCell(wrench);
                    me.paper.findViewByModel(wrench).options.interactive = false;
                }
            } else {
                if(embeddedCells.length !== 0) {
                    Ext.each(embeddedCells, function(cell) {
                        node.unembed(cell);
                        cell.remove();
                    });
                }
            }
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
                me.setLinkStyle(link, me.LINK_ADMIN_DOWN);
            } else if(!getStatus(ports[0], "oper_status") || !getStatus(ports[1], "oper_status")) {
                me.setLinkStyle(link, me.LINK_OPER_DOWN);
            } else if(!me.currentStpBlocked[linkId]) {
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
                if(bw) {
                    // Link utilization
                    lu = 0.0;
                    if(bw.in) {
                        lu = Math.max(lu, dt / bw.in);
                    }
                    if(bw.out) {
                        lu = Math.max(lu, td / bw.out);
                    }
                    // Apply proper style according to load
                    for(var i = 0; i < me.luStyle.length; i++) {
                        var t = me.luStyle[i][0],
                            style = me.luStyle[i][1];
                        if(lu >= t) {
                            cfg = {};
                            cfg = Ext.apply(cfg, style);
                            luStyle = cfg;
                            link.attr({
                                ".connection": cfg,
                                '.': {filter: {name: 'dropShadow', args: {dx: 1, dy: 1, blur: 2}}}
                            });
                            break;
                        }
                    }
                }
                // Show balance point
                tb = td + dt;
                if(tb > 0) {
                    balance = td / tb;
                    link.label(0, {position: balance});
                    if(luStyle) {
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
                NOC.error(__("Failed to reset layout"));
            }
        });
    },

    setZoom: function(zoom) {
        var me = this;
        me.paper.scale(zoom, zoom);
        me.setPaperDimension();
    },

    onNodeMenuViewCard: function() {
        var me = this;
        window.open(
            "/api/card/view/managedobject/" + me.nodeMenuObject + "/"
        );
    },

    onNodeMenuEdit: function() {
        var me = this;
        NOC.launch("sa.managedobject", "history", {args: [me.nodeMenuObject]});
    },

    onNodeMenuDashboard: function() {
        var me = this,
            objectType = me.nodeMenuObjectType;

        if('managedobject' == me.nodeMenuObjectType) objectType = 'mo';
        window.open(
            '/ui/grafana/dashboard/script/noc.js?dashboard=' + objectType + '&id=' + me.nodeMenuObject
        );
    },

    onNodeMenuMaintainceMode: function() {
        var me = this,
            objectId = Number(me.nodeMenuObject);

        NOC.run(
            'NOC.inv.map.Maintenance',
            __('Add To Maintenance'),
            {
                args: [
                    {mode: 'Object'},
                    [{object: objectId, object__label: me.objectNodes[objectId].attributes.attrs.text.text}]
                ]
            }
        );
    },

    addToMaintaince: function(objects) {
        var elements = [];
        Ext.Array.forEach(objects, function(item) {
            elements.push({object: item.get('object'), object__label: item.get('object__label')});
        });
        NOC.run(
            'NOC.inv.map.Maintenance',
            __('Add To Maintenance'),
            {
                args: [
                    {mode: 'Object'},
                    elements
                ]
            }
        );
    },

    newMaintaince: function(objects) {
        var args = {
            direct_objects: objects,
            subject: __('created from map at ') + Ext.Date.format(new Date(), 'd.m.Y H:i P'),
            contacts: NOC.email ? NOC.email : NOC.username,
            start_date: Ext.Date.format(new Date(), 'd.m.Y'),
            start_time: Ext.Date.format(new Date(), 'H:i'),
            stop_time: '12:00',
            suppress_alarms: true
        };

        Ext.create('NOC.maintenance.maintenancetype.LookupField')
            .getStore()
            .load({
                params: {__query: 'РНР'},
                callback: function(records) {
                    if(records.length > 0) {
                        Ext.apply(args, {
                            type: records[0].id
                        })
                    }
                    NOC.launch("maintenance.maintenance", "new", {
                        args: args
                    });
                }
            });
    },

    onNodeMenuNewMaintaince: function() {
        var me = this,
            objectId = Number(me.nodeMenuObject);
        me.newMaintaince([{
            object: objectId,
            object__label: me.objectNodes[objectId].attributes.attrs.text.text
        }]);
    },

    onNodeMenuAddToBasket: function() {
        var me = this,
            objectId = Number(me.nodeMenuObject);
        var store = Ext.data.StoreManager.lookup('basketStore');

        if(store.getCount() === 0) {
            me.fireEvent("openbasket");
        }
        me.addObjectToBasket(objectId, store);
    },

    onSegmentMenuAddToBasket: function() {
        var me = this;
        var store = Ext.data.StoreManager.lookup('basketStore');

        if(store.getCount() === 0) {
            me.fireEvent("openbasket");
        }
        Ext.each(this.graph.getElements(), function(e) {
            if('managedobject' === e.get('id').split(':')[0]) {
                var objectId = Number(e.get('id').split(':')[1]);
                me.addObjectToBasket(objectId, store);
            }
        });
    },

    addObjectToBasket: function(id, store) {
        Ext.Ajax.request({
            url: "/sa/managedobject/" + id + "/",
            method: "GET",
            success: function(response) {
                var data = Ext.decode(response.responseText);
                var object = {
                    id: id,
                    object: id,
                    object__label: data.name,
                    address: data.address,
                    platform: data.platform__label,
                    time: data.time_pattern
                };
                store.add(object);
            },
            failure: function() {
                NOC.msg.failed(__("Failed to get object data"));
            }
        });
    },

    setStp: function(status) {
        var me = this;
        if(status) {
            me.pollStp();
        }
    },

    pollStp: function() {
        var me = this,
            stpNodes = [];
        // Get STP nodes
        Ext.Object.each(me.objectNodes, function(k, v) {
            if(v.attributes.data.caps.indexOf(me.CAP_STP) !== -1) {
                stpNodes.push(k);
            }
        });
        // Get STP status
        Ext.Ajax.request({
            url: "/inv/map/stp/status/",
            method: "POST",
            jsonData: {
                objects: stpNodes
            },
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.setStpBlocked(data.blocked);
                me.setStpRoots(data.roots);
            },
            failure: function() {
                NOC.msg.failed(__("Failed to get STP status"));
            }
        });
    },

    setStpRoots: function(roots) {
        var me = this,
            newStpRoots = {};
        // Set new STP roots
        Ext.each(roots, function(rootId) {
            var root = me.objectNodes[rootId];
            if(root) {
                if(!me.currentStpRoots[rootId]) {
                    me.objectNodes[rootId].attr("text/class", "stp-root");
                }
                newStpRoots[rootId] = true;
            }
        });
        // Remove previous STP roots
        Ext.Object.each(me.currentStpRoots, function(k) {
            if(!newStpRoots[k]) {
                // Remove node style
                me.objectNodes[k].attr("text/class", "");
            }
        });
        me.currentStpRoots = newStpRoots;
    },

    setStpBlocked: function(blocked) {
        var me = this,
            newStpBlocked = {};
        Ext.each(me.graph.getLinks(), function(link) {
            var linkId = link.get("data").id;
            if(blocked.indexOf(linkId) !== -1) {
                newStpBlocked[linkId] = true;
                me.setLinkStyle(link, me.LINK_STP_BLOCKED);
            }
        });
        // @todo: Remove changed styles
        me.currentStpBlocked = newStpBlocked;
        console.log("blocked", me.currentStpBlocked);
    },

    setLinkStyle: function(link, status) {
        var me = this,
            style, glyph,
            fontSize = 10,
            luStyle;

        switch(status) {
            case me.LINK_OK:
                break;
            case me.LINK_ADMIN_DOWN:
                style = me.adminDownStyle;
                glyph = "\uf00d";
                break;
            case me.LINK_OPER_DOWN:
                style = me.operDownStyle;
                glyph = "\uf071";
                break;
            case me.LINK_STP_BLOCKED:
                style = me.stpBlockedStyle;
                glyph = "\uf05e";
                fontSize = 12;
                break;
        }
        //
        link.attr({
            ".connection": style
        });
        luStyle = Ext.apply({
            attrs: {
                text: style
            },
            visibility: "visible",
            position: 0.5,
            fill: style.stroke
        }, style);
        // @todo: Remove?
        luStyle.fill = luStyle.stroke;
        luStyle.visibility = "visible";
        luStyle.text = glyph;
        luStyle["font-size"] = fontSize;
        link.label(0, {attrs: {text: luStyle}});
        link.label(0, {position: 0.5});
    },

    onResize: function(width, height) {
        var me = this;
        if('paper' in me) {
            me.setPaperDimension();
        }
    },

    setPaperDimension: function() {
        var me = this,
            w = me.getWidth(),
            h = me.getHeight();

        if(me.paper) {
            me.paper.fitToContent();
            var contentBB = me.paper.getContentBBox();
            if(contentBB && contentBB.width && contentBB.height) {
                w = Ext.Array.max([contentBB.width, me.getWidth()]);
                h = Ext.Array.max([contentBB.height, me.getHeight()]);
                // ToDo may by use paper padding?
                var padding = 15;
                me.paper.setOrigin((-1) * contentBB.x + padding, (-1) * contentBB.y + padding);
                me.paper.setDimensions(w + padding * 2, h + padding * 2);
            }
        }
    },

    changeLabelText: function(showIPAddress) {
        if(showIPAddress) {
            Ext.each(this.graph.getElements(), function(e) {
                e.attr('text/text', e.get('address'));
            });
        } else {
            Ext.each(this.graph.getElements(), function(e) {
                e.attr('text/text', e.get('name'));
            });
        }
    },

    breakText: function(text, size, styles, opt) {
        opt = opt || {};
        var width = size.width;
        var height = size.height;
        var svgDocument = opt.svgDocument || V('svg').node;
        var textElement = V('<text><tspan></tspan></text>').attr(styles || {}).node;
        var textSpan = textElement.firstChild;
        var textNode = document.createTextNode('');

        // Prevent flickering
        textElement.style.opacity = 0;
        // Prevent FF from throwing an uncaught exception when `getBBox()`
        // called on element that is not in the render tree (is not measurable).
        // <tspan>.getComputedTextLength() returns always 0 in this case.
        // Note that the `textElement` resp. `textSpan` can become hidden
        // when it's appended to the DOM and a `display: none` CSS stylesheet
        // rule gets applied.
        textElement.style.display = 'block';
        textSpan.style.display = 'block';
        textSpan.appendChild(textNode);
        svgDocument.appendChild(textElement);
        if (!opt.svgDocument) {
            document.body.appendChild(svgDocument);
        }

        var words = text.split(/(\W+)/);
        var full = [];
        var lines = [];
        var p;
        var lineHeight;

        for (var i = 0, l = 0, len = words.length; i < len; i++) {
            var word = words[i];

            textNode.data = lines[l] ? lines[l] + word : word;
            if (textSpan.getComputedTextLength() <= width) {
                // the current line fits
                lines[l] = textNode.data;
                if (p) {
                    // We were partitioning. Put rest of the word onto next line
                    full[l++] = true;
                    // cancel partitioning
                    p = 0;
                }
            } else {
                if (!lines[l] || p) {
                    var partition = !!p;
                    p = word.length - 1;
                    if (partition || !p) {
                        // word has only one character.
                        if (!p) {
                            if (!lines[l]) {
                                // we won't fit this text within our rect
                                lines = [];
                                break;
                            }
                            // partitioning didn't help on the non-empty line
                            // try again, but this time start with a new line
                            // cancel partitions created
                            words.splice(i, 2, word + words[i + 1]);
                            // adjust word length
                            len--;
                            full[l++] = true;
                            i--;
                            continue;
                        }
                        // move last letter to the beginning of the next word
                        words[i] = word.substring(0, p);
                        words[i + 1] = word.substring(p) + words[i + 1];
                    } else {
                        // We initiate partitioning
                        // split the long word into two words
                        words.splice(i, 1, word.substring(0, p), word.substring(p));
                        // adjust words length
                        len++;
                        if (l && !full[l - 1]) {
                            // if the previous line is not full, try to fit max part of
                            // the current word there
                            l--;
                        }
                    }
                    i--;
                    continue;
                }
                l++;
                i--;
            }
            // if size.height is defined we have to check whether the height of the entire
            // text exceeds the rect height
            if (height !== undefined) {
                if (lineHeight === undefined) {
                    var heightValue;
                    // use the same defaults as in V.prototype.text
                    if (styles.lineHeight === 'auto') {
                        heightValue = { value: 1.5, unit: 'em' };
                    } else {
                        heightValue = joint.util.parseCssNumeric(styles.lineHeight, ['em']) || { value: 1, unit: 'em' };
                    }
                    lineHeight = heightValue.value;
                    if (heightValue.unit === 'em' ) {
                        lineHeight *= textElement.getBBox().height;
                    }
                }
                if (lineHeight * lines.length > height) {
                    // remove overflowing lines
                    lines.splice(Math.floor(height / lineHeight));
                    break;
                }
            }
        }
        if (opt.svgDocument) {
            // svg document was provided, remove the text element only
            svgDocument.removeChild(textElement);
        } else {
            // clean svg document
            document.body.removeChild(svgDocument);
        }
        return lines.join('\n');
    }
});
