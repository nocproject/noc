//---------------------------------------------------------------------
// Workflow editor
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.WFEditor");

Ext.define("NOC.wf.workflow.WFEditor", {
    extend: "Ext.Window",
    requires: [
        "NOC.wf.workflow.WFInspector"
    ],
    width: 800,
    height: 600,
    maximizable: true,
    autoShow: true,
    closeable: true,
    modal: true,
    app: undefined,
    wf: undefined,

    PROCESS_WIDTH: 100,
    PROCESS_HEIGHT: 50,
    CONDITION_WIDTH: 100,
    CONDITION_HEIGHT: 100,
    PORT_RADIUS: 8,
    STATE_WIDTH: 30,
    STATE_HEIGHT: 30,

    IPORT: 0,
    OPORT: 1,
    TPORT: 2,
    FPORT: 3,

    items: [{
        xtype: "component",
        autoScroll: true,
        style: {
            background: "url('/static/img/grid.gif')"
        }
    }],
    //
    initComponent: function() {
        var me = this;

        me.handlers = {};
        me.nodeN = 1;
        me.currentNode = undefined;
        me.deletedNodes = [];

        Ext.Ajax.request({
            url: "/wf/workflow/handlers/",
            method: "GET",
            scope: me,
            success: me.onLoadHandlers
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            iconCls: "icon_disk",
            text: "Save",
            tooltip: "Save changes",
            disabled: true,
            scope: me,
            handler: me.onSave
        });
        // Zoom buttons
        me.zoomInButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom In",
            iconCls: "icon_magnifier_zoom_in",
            scope: me,
            handler: me.onZoomIn,
        });
        me.zoomOutButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom Out",
            iconCls: "icon_magifier_zoom_out",
            scope: me,
            handler: me.onZoomOut,
        });
        me.zoomActualButton = Ext.create("Ext.button.Button", {
            tooltip: "Zoom Actual",
            iconCls: "icon_magnifier",
            scope: me,
            handler: me.onZoomActual,
        });

        me.inspector = Ext.create("NOC.wf.workflow.WFInspector", {
            dock: "right",
            editor: me
        });

        me.addButton = Ext.create("Ext.button.Button", {
            tooltip: "Add",
            iconCls: "icon_add",
            scope: me,
            handler: me.onAddNode
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            tooltip: "Delete",
            iconCls: "icon_delete",
            scope: me,
            handler: me.onDeleteNode,
            disabled: true
        });

        Ext.apply(me, {
            title: Ext.String.format(
                "Workflow Editor: {0}",
                me.wf.get("name")
            ),
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.saveButton,
                        "-",
                        // Zoom
                        me.zoomInButton,
                        me.zoomOutButton,
                        me.zoomActualButton,
                        "-",
                        me.addButton,
                        me.deleteButton
                    ]
                },
                me.inspector
            ]
        });
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        // Load mxGraph JS library
        mxLanguage = "en";
        mxLoadStylesheets = false;  // window scope
        mxImageBasePath = "/static/img/mxgraph/";
        mxLoadResources = false;
        load_scripts(["/static/js/mxClient.min.js"], me,
            me.onLoadJS);
    },
    //
    onLoadJS: function() {
        var me = this;
        // mxClient has been loaded
        me.initGraph();
    },
    //
    initGraph: function() {
        var me = this,
            c = me.items.first().el.dom;
        mxEvent.disableContextMenu(c); // Disable default context menu
        // Enables guides
        mxGraphHandler.prototype.guidesEnabled = true;
        // Create graph
        me.graph = new mxGraph(c);
        me.graph.setDisconnectOnMove(false);
        me.graph.setConnectable(true);
        me.graph.cellsResizable = false;
        new mxRubberband(me.graph);
        me.graph.setPanning(true);
        me.graph.setTooltips(true);
        me.graph.foldingEnabled = false;
        // Set styles
        var style = me.graph.getStylesheet().getDefaultVertexStyle();
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_SWIMLANE;
        style[mxConstants.STYLE_VERTICAL_ALIGN] = 'middle';
        style[mxConstants.STYLE_LABEL_BACKGROUNDCOLOR] = 'white';
        style[mxConstants.STYLE_FONTSIZE] = 11;
        style[mxConstants.STYLE_STARTSIZE] = 22;
        style[mxConstants.STYLE_HORIZONTAL] = false;
        style[mxConstants.STYLE_FONTCOLOR] = 'black';
        style[mxConstants.STYLE_STROKECOLOR] = 'black';
        style[mxConstants.STYLE_STROKEWIDTH] = 2;
        delete style[mxConstants.STYLE_FILLCOLOR];
        // Process style
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_RECTANGLE;
        style[mxConstants.STYLE_FONTSIZE] = 10;
        style[mxConstants.STYLE_ROUNDED] = true;
        style[mxConstants.STYLE_HORIZONTAL] = true;
        style[mxConstants.STYLE_VERTICAL_ALIGN] = 'middle';
        delete style[mxConstants.STYLE_STARTSIZE];
        style[mxConstants.STYLE_LABEL_BACKGROUNDCOLOR] = 'none';
        me.graph.getStylesheet().putCellStyle('process', style);
        // Start style
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_ELLIPSE;
        style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        delete style[mxConstants.STYLE_ROUNDED];
        me.graph.getStylesheet().putCellStyle('start', style);
        // End style
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_DOUBLE_ELLIPSE;
        style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        delete style[mxConstants.STYLE_ROUNDED];
        me.graph.getStylesheet().putCellStyle('end', style);
        // Port style
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_ELLIPSE;
        style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        delete style[mxConstants.STYLE_ROUNDED];
        me.graph.getStylesheet().putCellStyle('port', style);
        // Condition style
        style = mxUtils.clone(style);
		style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_RHOMBUS;
		style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RhombusPerimeter;
        style[mxConstants.STYLE_VERTICAL_ALIGN] = 'middle';
		//style[mxConstants.STYLE_SPACING_TOP] = 40;
		//style[mxConstants.STYLE_SPACING_RIGHT] = 64;
		me.graph.getStylesheet().putCellStyle('condition', style);
        // Edge style
        style = me.graph.getStylesheet().getDefaultEdgeStyle();
        style[mxConstants.STYLE_EDGE] = mxEdgeStyle.OrthConnector;
        style[mxConstants.STYLE_ENDARROW] = mxConstants.ARROW_BLOCK;
        style[mxConstants.STYLE_ROUNDED] = true;
        style[mxConstants.STYLE_FONTCOLOR] = 'black';
        style[mxConstants.STYLE_STROKECOLOR] = 'black';
        //
        me.graph.setConnectable(true);
		me.graph.setAllowDanglingEdges(false);
        // Inititalize tooltips
        me.graph.getTooltipForCell = me.getTooltipForCell;
        // Event listeners
        me.graph.addListener(
            mxEvent.CLICK,
            Ext.bind(me.onClickNode, me)
        );
        me.graph.addListener(
            mxEvent.MOVE_CELLS,
            Ext.bind(me.onNodeMove, me)
        );
        //
        me.graph.connectionHandler.isValidSource = Ext.bind(me.isValidSource, me);
        me.graph.connectionHandler.isValidTarget = Ext.bind(me.isValidTarget, me);
        //
        me.loadNodes();
    },
    //
    loadNodes: function() {
        var me = this;

        me.graph.removeCells(me.graph.getChildVertices(me.graph.getDefaultParent()), true);
        me.deletedNodes = [];
        Ext.Ajax.request({
            url: "/wf/workflow/" + me.wf.get("id") + "/nodes/",
            method: "GET",
            scope: me,
            success: function(response) {
                var me = this,
                    data = Ext.decode(response.responseText);
                me.onLoadNodes(data);
            },
            failure: function() {
                NOC.error("Failed to get nodes");
            }
        });
    },
    //
    addEndNode: function(port) {
        var me = this,
            parent = port.parent.parent,
            x, y, e;
        x = port.geometry.x + port.geometry.offset.x + port.parent.geometry.x;
        y = port.geometry.y + port.geometry.offset.y + port.parent.geometry.y;
        if(port.ptype == me.FPORT) {
            y += 50;
        } else {
            x += 50;
            y -= me.STATE_HEIGHT / 2 - me.PORT_RADIUS / 2;
        }
        e = me.graph.insertVertex(parent, null, null,
            x, y, me.STATE_WIDTH, me.STATE_HEIGHT, "end");
        me.graph.insertEdge(parent, null, null, port, e);
    },
    //
    addNode: function(data) {
        var me = this,
            parent = me.graph.getDefaultParent(),
            w, h, style, v;
        if(data.conditional) {
            w = me.CONDITION_WIDTH;
            h = me.CONDITION_HEIGHT;
            style = "condition";
        } else {
            w = me.PROCESS_WIDTH;
            h = me.PROCESS_HEIGHT;
            style = "process";
        }
        // Create node
        v = me.graph.insertVertex(parent, null,
            data.name,
            data.x, data.y, w, h,
            style
        );
        v.wfdata = data;
        v.nocTooltipTemplate = me.app.templates.NodeTooltip;
        v.setConnectable(false);
        // Create ports
        // Input
        var iport = me.graph.insertVertex(v, null, null,
            0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "port;portConstraint=west;direction=west;fillColor=black");
        iport.geometry.offset = new mxPoint(
            -me.PORT_RADIUS / 2, h / 2 - me.PORT_RADIUS / 2);
        iport.geometry.relative = true;
        iport.ptype = me.IPORT;
        v.iport = iport;
        // Output
        if(data.conditional) {
            var tport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "port;fillColor=green;portConstraint=east;direction=east");
            tport.geometry.offset = new mxPoint(
                w - me.PORT_RADIUS / 2, h / 2 - me.PORT_RADIUS / 2);
            tport.geometry.relative = true;
            tport.ptype = me.TPORT;
            v.tport = tport;
            var fport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "port;fillColor=red;portConstraint=south;direction=south");
            fport.geometry.offset = new mxPoint(
                w / 2 - me.PORT_RADIUS / 2, h - me.PORT_RADIUS / 2);
            fport.geometry.relative = true;
            fport.ptype = me.FPORT;
            v.fport = fport;
        } else {
            var oport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "port;fillColor=black;portConstraint=east;direction=east");
            oport.geometry.offset = new mxPoint(
                w - me.PORT_RADIUS / 2, h / 2 - me.PORT_RADIUS / 2);
            oport.geometry.relative = true;
            oport.ptype = me.OPORT;
            v.oport = oport;
        }

        // Create start node
        if (data.start) {
            // Start node
            var s = me.graph.insertVertex(parent,
                null, null,
                20, data.y + h / 2 - me.STATE_HEIGHT / 2,
                me.STATE_WIDTH, me.STATE_HEIGHT,
                "start"
            );
            me.graph.insertEdge(parent, null, null,
                s, v.iport);
        }
        return v;
    },
    //
    onLoadNodes: function(data) {
        var me = this,
            parent = me.graph.getDefaultParent(),
            model = me.graph.getModel(),
            nodes = {};

        me.saveButton.setDisabled(true);
        model.beginUpdate();
        try {
            // Create nodes
            Ext.each(data, function(value) {
                switch(value.type) {
                    case 'node':
                        nodes[value.id] = me.addNode(value);
                        break;
                }
            });
            // Create edges
            Ext.each(data, function(value) {
                switch(value.type) {
                    case 'node':
                        if(value.conditional) {
                            if(value.next_true_node) {
                                me.graph.insertEdge(
                                    parent,
                                    null, "Yes",
                                    nodes[value.id].tport,
                                    nodes[value.next_true_node].iport,
                                    null
                                );
                            }
                            if(value.next_false_node) {
                                me.graph.insertEdge(
                                    parent,
                                    null, "No",
                                    nodes[value.id].fport,
                                    nodes[value.next_false_node].iport
                                );
                            }
                        } else {
                            if(value.next_node) {
                                me.graph.insertEdge(
                                    parent,
                                    null, null,
                                    nodes[value.id].oport,
                                    nodes[value.next_node].iport,
                                    null
                                );
                            } else {
                                me.addEndNode(nodes[value.id].oport);
                            }
                        }
                        break;
                }
            });
        }
        finally {
            model.endUpdate();
        }
    },
    //
    onSave: function() {
        var me = this,
            cells = me.graph.getModel().cells,
            data = [];
        // Push deleted nodes
        for(var i in me.deletedNodes) {
            var c = me.deletedNodes[i];
            data.push({
                type: "node",
                deleted: true,
                id: c
            });
        }
        // Prepare data
        for(var i in cells) {
            var c = cells[i];
            if(!c.wfdata || !c.wfdata.changed) {
                continue;
            }
            data.push({
                type: "node",
                id: c.wfdata.id,
                name: c.wfdata.name,
                description: c.wfdata.description,
                handler: c.wfdata.handler,
                params: c.wfdata.params,
                x: c.geometry.x,
                y: c.geometry.y
            });
        }
        //
        Ext.Ajax.request({
            url: "/wf/workflow/" + me.wf.get("id") + "/nodes/",
            method: "POST",
            scope: me,
            jsonData: data,
            success: function(response) {
                var me = this;
                me.loadNodes();
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    },
    //
    getTooltipForCell: function(cell) {
        if(!cell.wfdata) {
            return "";
        }
        return cell.nocTooltipTemplate(cell.wfdata);
    },
    //
    onClickNode: function(sender, evt) {
        var me = this;

        me.currentNode = evt.properties.cell;
        if(me.currentNode && !me.currentNode.wfdata) {
            me.currentNode = null;
        }
        me.inspector.showNode(me.currentNode);
        me.deleteButton.setDisabled(!me.currentNode);
    },
    //
    onLoadHandlers: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        me.handlers = data;
        me.inspector.setHandlers(data);
    },
    //
    onNodeMove: function(graph, event) {
        var me = this,
            cells = event.properties.cells;
        for(var i in cells) {
            var c = cells[i];
            if(c.wfdata) {
                me.registerChange(c);
            }
        }
    },
    //
    registerChange: function(cell) {
        var me = this;
        me.saveButton.setDisabled(false);
        cell.wfdata.changed = true;
    },
    // Zoom In
    onZoomIn: function() {
        var me = this;
        me.graph.zoomIn();
    },
    // Zoom Out
    onZoomOut: function() {
        var me = this;
        me.graph.zoomOut();
    },
    // Zoom Actual
    onZoomActual: function() {
        var me = this;
        me.graph.zoomActual();
    },
    //
    onAddNode: function() {
        var me = this,
            model = me.graph.getModel(),
            v;
        model.beginUpdate();
        try {
            var n = me.nodeN;
            me.nodeN += 1;
            v = me.addNode({
                id: "id:" + n,
                name: "Node #" + n,
                conditional: false,
                start: false
            });
        } finally {
            model.endUpdate();
        }
        me.inspector.showNode(v);
    },
    //
    onDeleteNode: function() {
        var me = this;
        if(me.currentNode) {
            if(me.currentNode.wfdata.id.search(/^id:/) == -1) {
                me.deletedNodes.push(me.currentNode.wfdata.id);
                me.saveButton.setDisabled(false);
            }
            me.graph.removeCells([me.currentNode], true);
            me.currentNode = undefined;
            me.inspector.showNode(me.currentNode);
        }
    },
    //
    isValidSource: function(cell) {
        var me = this,
            vs = me.graph.isValidSource(cell);
        if(!vs) {
            return false;
        }
        if(cell.ptype === undefined) {
            return true;
        }
        if((cell.ptype === me.OPORT) || (cell.ptype === me.TPORT) || (cell.ptype === me.FPORT)) {
            return !cell.edges;
        }
        return false;
    },
    //
    isValidTarget: function(cell) {
        var me = this,
            vt = me.graph.isValidTarget(cell);
        if(!vt) {
            return false;
        }
        if(cell.ptype === undefined) {
            return true;
        }
        return cell.ptype === me.IPORT;
    }
});
