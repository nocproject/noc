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
        osUnknown: [128, 128, 128],
        osOk: [0, 0, 255],
        osAlarm: [255, 255, 0],
        osUnreach: [64, 64, 64],
        osDown: [255, 0, 0]
    },

    svgDefaultFilters: [
        '<filter id="highlight">' +
            '<feGaussianBlur stdDeviation="4" result="coloredBlur"/>' +
            '<feMerge>' +
                '<feMergeNode in="coloredBlur"/>' +
                '<feMergeNode in="SourceGraphic"/>' +
            '</feMerge>' +
        '</filter>'
    ],

    statusFilter: {
        0: "osUnknown",
        1: "osOk",
        2: "osAlarm",
        3: "osUnreach",
        4: "osDown"
    },

    initComponent: function () {
        var me = this;

        me.shapeRegistry = NOC.inv.map.ShapeRegistry;
        me.objectNodes = {};
        me.objectsList = [];
        me.portObjects = {};  // port id -> object id
        me.isInteractive = false;  // Graph is editable
        me.isDirty = false;  // Graph is changed
        me.pollingTaskId = null;
        me.currentHighlight = null;

        Ext.apply(me, {
            items: [
                {
                    xtype: "component",
                    autoScroll: true,
                    layout: "fit",
                    style: {
                        background: "#e0e0e0"
                    }
                }
            ]
        });
        me.callParent();
    },

    afterRender: function () {
        var me = this;
        me.callParent();
        load_scripts([
            "/static/pkg/jquery/jquery.js",
            "/static/pkg/jointjs/jointjs.js"
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
        //me.createContextMenus();
        me.fireEvent("mapready");
    },

    // Load segment data
    loadSegment: function(segmentId) {
        var me = this;
        me.segmentId = segmentId;
        Ext.Ajax.request({
            url: "/inv/map/" + segmentId + "/data/",
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
        me.objectsList = [];
        me.graph.clear();
        // Create nodes
        Ext.each(data.nodes, function(node) {
            cells.push(me.createNode(node));
            Ext.each(node.ports, function(port) {
                me.portObjects[port.id] = node.id;
            })
        });
        // Create links
        Ext.each(data.links, function(link) {
            cells.push(me.createLink(link));
        });
        me.graph.addCells(cells);
        me.paper.fitToContent();
        if(me.pollingTaskId) {
            me.getObjectStatus();
        } else {
            me.pollingTaskId = Ext.TaskManager.start({
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
        me.objectsList.push(data.id);
        return node;
    },
    //
    createLink: function(data) {
        var me = this,
            cfg, src, dst;

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
                }
            },
            data: {
                type: data.type,
                id: data.id
            }
        };
        //
        if(data.smooth) {
            cfg.smooth = true;
        }
        if(data.vertices) {
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
            data = view.model.get("data")
        switch(data.type) {
            case "managedobject":
                me.unhighlight();
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
                lr = {
                    id: e.get("id")
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
            '<feColorMatrix type="matrix" ',
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
            r1 = c[0] / 255.0,
            g1 = c[1] / 255.0,
            b1 = c[2] / 255.0,
            r0 = 1.0 - r1,
            g0 = 1.0 - g1,
            b0 = 1.0 - b1;
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
        if(me.pollingTaskId) {
            Ext.TaskManager.stop(me.pollingTaskId);
            me.pollingTaskId = null;
        }
    }
});
