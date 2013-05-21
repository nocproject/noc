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
    SPORT: 4,

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
        me.ignoreConnectionEvents = false;
        me.startNode = undefined;

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
        me.maximize();
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
        var pstyle = mxUtils.clone(style);
        pstyle[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_ELLIPSE;
        pstyle[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        delete style[mxConstants.STYLE_ROUNDED];
        me.graph.getStylesheet().putCellStyle('port', pstyle);
        // iport
        var npstyle = mxUtils.clone(pstyle);
        npstyle[mxConstants.STYLE_FILLCOLOR] = "black";
        npstyle[mxConstants.STYLE_PORT_CONSTRAINT] = "west";
        npstyle[mxConstants.STYLE_DIRECTION] = "west";
        me.graph.getStylesheet().putCellStyle('iport', npstyle);
        // oport
        npstyle = mxUtils.clone(pstyle);
        npstyle[mxConstants.STYLE_FILLCOLOR] = "black";
        npstyle[mxConstants.STYLE_PORT_CONSTRAINT] = "east";
        npstyle[mxConstants.STYLE_DIRECTION] = "east";
        me.graph.getStylesheet().putCellStyle('oport', npstyle);
        // tport
        npstyle = mxUtils.clone(pstyle);
        npstyle[mxConstants.STYLE_FILLCOLOR] = "green";
        npstyle[mxConstants.STYLE_PORT_CONSTRAINT] = "east";
        npstyle[mxConstants.STYLE_DIRECTION] = "east";
        me.graph.getStylesheet().putCellStyle('tport', npstyle);
        // fport
        npstyle = mxUtils.clone(pstyle);
        npstyle[mxConstants.STYLE_FILLCOLOR] = "red";
        npstyle[mxConstants.STYLE_PORT_CONSTRAINT] = "south";
        npstyle[mxConstants.STYLE_DIRECTION] = "south";
        me.graph.getStylesheet().putCellStyle('fport', npstyle);
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
        me.graph.addListener(
            mxEvent.CELL_CONNECTED,
            Ext.bind(me.onCellConnected, me)
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

        me.startNode = null;
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
    getStartNode: function() {
        var me = this;

        if(!me.startNode) {
            me.startNode = me.graph.insertVertex(
                me.graph.getDefaultParent(),
                null, null,
                me.STATE_WIDTH, me.STATE_HEIGHT,
                me.STATE_WIDTH, me.STATE_HEIGHT,
                "start"
            );
            me.startNode.ptype = me.SPORT;
        }
        return me.startNode;
    },
    //
    connectStartNode: function(node) {
        var me = this,
            sn = me.getStartNode();
            // Align start node
            sn.geometry.y = node.geometry.y + (node.geometry.height - sn.geometry.height) / 2;
            // Create Edge
            me.graph.insertEdge(me.graph.getDefaultParent(),
                null, null,
                sn, node.iport);
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
    // Adjust port according to the node
    adjustPort: function(port, ptype) {
        var me = this,
            node = port.parent,
            w = node.geometry.width,
            h = node.geometry.height,
            x, y;
        switch(ptype) {
            case me.IPORT:
                x = -me.PORT_RADIUS / 2;
                y = h / 2 - me.PORT_RADIUS / 2;
                port.setStyle("iport");
                break;
            case me.OPORT:
                x = w - me.PORT_RADIUS / 2;
                y = h / 2 - me.PORT_RADIUS / 2;
                port.setStyle("oport");
                break;
            case me.TPORT:
                x = w - me.PORT_RADIUS / 2;
                y = h / 2 - me.PORT_RADIUS / 2;
                port.setStyle("tport");
                break;
            case me.FPORT:
                x = w / 2 - me.PORT_RADIUS / 2;
                y = h - me.PORT_RADIUS / 2;
                port.setStyle("fport");
                break;
        }
        port.geometry.offset = new mxPoint(x, y);
        port.geometry.relative = true;
        port.ptype = ptype;
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
        v.iport = me.graph.insertVertex(v, null, null,
            0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "iport");
        me.adjustPort(v.iport, me.IPORT);
        // Output
        if(data.conditional) {
            v.tport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "tport");
            me.adjustPort(v.tport, me.TPORT);
            v.fport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "fport");
            me.adjustPort(v.fport, me.FPORT);
        } else {
            v.oport = me.graph.insertVertex(v, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "oport");
            me.adjustPort(v.oport, me.OPORT);
        }

        // Create start node
        if (data.start) {
            // Start node
            me.connectStartNode(v);
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
        me.ignoreConnectionEvents = true;
        model.beginUpdate();
        me.getStartNode();
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
            me.ignoreConnectionEvents = false;
        }
        me.inspector.showNode(null);
    },
    //
    onSave: function() {
        var me = this,
            cells = me.graph.getModel().cells,
            data = [],
            nextNodes = {},
            nextTrueNodes = {},
            nextFalseNodes = {},
            sid = null;
        // Apply inspector changes
        me.inspector.onApply();
        // Push deleted nodes
        for(var i in me.deletedNodes) {
            var c = me.deletedNodes[i];
            data.push({
                type: "node",
                deleted: true,
                id: c
            });
        }
        // Process edges
        for(var i in cells) {
            var c = cells[i],
                sn,
                tn;
            if(!c.isEdge() || !c.source || !c.target
                || c.source.ptype === undefined
                || c.target.ptype === undefined) {
                continue;
            }
            if(c.source.ptype != me.SPORT) {
                sn = c.source.parent.wfdata.id;
            }
            tn = c.target.parent.wfdata.id;
            switch(c.source.ptype) {
                case me.OPORT:
                    nextNodes[sn] = tn;
                    break
                case me.TPORT:
                    nextTrueNodes[sn] = tn;
                    break;
                case me.FPORT:
                    nextFalseNodes[sn] = tn;
                    break;
                case me.SPORT:
                    sid = tn;
                    break;
            }
        }
        // Prepare data
        for(var i in cells) {
            var c = cells[i],
                cid;
            if(!c.wfdata || !c.wfdata.changed) {
                continue;
            }
            cid = c.wfdata.id;
            var n = {
                type: "node",
                id: cid,
                name: c.wfdata.name,
                description: c.wfdata.description,
                handler: c.wfdata.handler,
                params: c.wfdata.params,
                x: c.geometry.x,
                y: c.geometry.y,
                next_node: nextNodes[cid],
                next_true_node: nextTrueNodes[cid],
                next_false_node: nextFalseNodes[cid],
                start: cid === sid
            };
            data.push(n);
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
        if(!cell || !cell.wfdata) {
            return;
        }
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
            // Push changes to previous nodes
            var cells = me.graph.getModel().cells,
                iport = me.currentNode.iport;
            for(var i in cells) {
                var c = cells[i];
                if(!c.isEdge() || !c.source || !c.target
                    || c.source.ptype === undefined
                    || c.target.ptype === undefined) {
                    continue;
                }
                if(c.source && c.target == iport
                    && c.source.parent.wfdata) {
                    me.registerChange(c.source.parent);
                }
            }
            // Delete node
            if(me.currentNode.wfdata.id.search(/^id:/) == -1) {
                // Push changes
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
        if((cell.ptype === me.OPORT) || (cell.ptype === me.TPORT) || (cell.ptype === me.FPORT) || cell.ptype === me.SPORT) {
            return cell.getEdgeCount() === 0;
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
    },
    //
    onCellConnected: function(graph, evt) {
        var me = this;
        if(me.ignoreConnectionEvents) {
            return;
        }
        var edge = evt.getProperty("edge");
        if(edge.source == me.startNode) {
            if(edge.target && edge.target.parent && edge.target.parent.wfdata) {
                me.registerChange(edge.target.parent);
            }
        } else {
            me.registerChange(edge.source.parent);
        }
        var p = evt.getProperty("previous");
        if(p && p.parent && p.parent.wfdata) {
            me.registerChange(p.parent);
        }
    },
    //
    changeShape: function(node) {
        var me = this;
        if(node.wfdata.conditional && node.style == "process") {
            // Process -> cond
            // Adjust node style
            node.setStyle("condition");
            node.geometry.y -= (me.CONDITION_HEIGHT - me.PROCESS_HEIGHT) / 2;
            node.geometry.width = me.CONDITION_WIDTH;
            node.geometry.height = me.CONDITION_HEIGHT;
            // Adjust iport
            me.adjustPort(node.iport, me.IPORT);
            // oport -> tport
            node.tport = node.oport;
            node.oport = undefined;
            me.adjustPort(node.tport, me.TPORT);
            // Create fport
            node.fport = me.graph.insertVertex(node, null, null,
                0, 0, me.PORT_RADIUS, me.PORT_RADIUS, "fport");
            me.adjustPort(node.fport, me.FPORT);
            // Show changes
            me.graph.refresh();
        } else if(!node.wfdata.conditional && node.style == "condition") {
            // Cond -> process
            // Adjust node style
            node.setStyle("process");
            node.geometry.y += (me.CONDITION_HEIGHT - me.PROCESS_HEIGHT) / 2;
            node.geometry.width = me.PROCESS_WIDTH;
            node.geometry.height = me.PROCESS_HEIGHT;
            // Adjust iport
            me.adjustPort(node.iport, me.IPORT);
            // tport -> oport
            node.oport = node.tport;
            node.tport = undefined;
            me.adjustPort(node.oport, me.OPORT);
            // Remove fport
            var f = node.fport;
            me.graph.removeCells([node.fport], true);
            node.fport = undefined;
            // Show changes
            me.graph.refresh();
        }
    }
});
