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

    initComponent: function () {
        var me = this;

        me.shapeRegistry = NOC.inv.map.ShapeRegistry;
        me.objectNodes = {};
        me.portObjects = {};  // port id -> object id

        Ext.apply(me, {
            items: [
                {
                    xtype: "component",
                    autoScroll: true,
                    layout: "fit",
                    padding: 4,
                    style: {
                        background: "url('/static/img/grid.gif')"
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
        me.paper = new joint.dia.Paper({
            el: dom,
            model: me.graph,
            gridSize: 10,
            interactive: false
        });
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
            }
        });
    },

    //
    renderMap: function(data) {
        var me = this,
            cells = [];

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
    onCellSelected: function(view, evt, x, y) {
        var me = this,
            data = view.model.get("data")
        switch(data.type) {
            case "managedobject":
                view.highlight();
                me.app.inspectManagedObject(data.id);
                break;
            case "link":
                me.app.inspectLink(data.id);
                break;
        }
    },
    onBlankSelected: function() {
        var me = this;
        me.app.inspectSegment();
    }
});