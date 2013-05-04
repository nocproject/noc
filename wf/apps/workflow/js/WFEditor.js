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

        me.inspector = Ext.create("NOC.wf.workflow.WFInspector", {
            dock: "right",
            editor: me
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
                        me.saveButton
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
        me.graph = new mxGraph(c);
        me.graph.disconnectOnMove = false;
        // me.graph.foldingEnabled = false;
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
        //
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_ELLIPSE;
        style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        delete style[mxConstants.STYLE_ROUNDED];
        me.graph.getStylesheet().putCellStyle('start', style);
        //
        style = mxUtils.clone(style);
        style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_DOUBLE_ELLIPSE;
        style[mxConstants.STYLE_PERIMETER] = mxPerimeter.EllipsePerimeter;
        style[mxConstants.STYLE_SPACING_TOP] = 28;
        style[mxConstants.STYLE_FONTSIZE] = 14;
        style[mxConstants.STYLE_FONTSTYLE] = 1;
        delete style[mxConstants.STYLE_SPACING_RIGHT];
        me.graph.getStylesheet().putCellStyle('end', style);
        // Condition style
        style = mxUtils.clone(style);
		style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_RHOMBUS;
		style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RhombusPerimeter;
		style[mxConstants.STYLE_VERTICAL_ALIGN] = 'top';
		style[mxConstants.STYLE_SPACING_TOP] = 40;
		style[mxConstants.STYLE_SPACING_RIGHT] = 64;
		me.graph.getStylesheet().putCellStyle('condition', style);
        // Edge style
        style = me.graph.getStylesheet().getDefaultEdgeStyle();
        style[mxConstants.STYLE_EDGE] = mxEdgeStyle.ElbowConnector;
        style[mxConstants.STYLE_ENDARROW] = mxConstants.ARROW_BLOCK;
        style[mxConstants.STYLE_ROUNDED] = true;
        style[mxConstants.STYLE_FONTCOLOR] = 'black';
        style[mxConstants.STYLE_STROKECOLOR] = 'black';
        //
        me.graph.setConnectable(true);
		me.graph.setAllowDanglingEdges(false);
        me.graph.cellsResizable = false;
        // Inititalize tooltips
        me.graph.getTooltipForCell = me.getTooltipForCell;
        me.graph.addListener(mxEvent.CLICK, Ext.bind(me.onClickNode, me));
        me.loadNodes();
    },
    //
    loadNodes: function() {
        var me = this;
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
    onLoadNodes: function(data) {
        var me = this,
            parent = me.graph.getDefaultParent(),
            model = me.graph.getModel(),
            nodes = {};

        model.beginUpdate();
        try {
            // Create nodes
            Ext.each(data, function(value) {
                switch(value.type) {
                    case 'node':
                        // Parse node
                        var w, h, style;
                        if(value.conditional) {
                            w = 100;
                            h = 100;
                            style = "condition";
                        } else {
                            w = 100;
                            h = 50;
                            style = "process";
                        }
                        var v = me.graph.insertVertex(parent, null,
                            value.name,
                            value.x, value.y, w, h,
                            style
                        );
                        v.wfdata = value;
                        v.nocTooltipTemplate = me.app.templates.NodeTooltip;
                        nodes[value.name] = v;
                        if (value.start) {
                            // Start node
                            var s = me.graph.insertVertex(parent,
                                null, null,
                                20, value.y + h / 2 - 15,
                                30, 30,
                                "start"
                            );
                            me.graph.insertEdge(parent, null, null,
                                s, v);
                        }
                        break;
                }
                // Create edges
                Ext.each(data, function(value) {
                    switch(value.type) {
                        case 'node':
                            if(value.conditional) {
                                if(value.next_true_node) {
                                    me.graph.insertEdge(
                                        parent,
                                        null, "Yes",
                                        nodes[value.name],
                                        nodes[value.next_true_node],
                                        null
                                    );
                                }
                                if(value.next_false_node) {
                                    me.graph.insertEdge(
                                        parent,
                                        null, "No",
                                        nodes[value.name],
                                        nodes[value.next_false_node],
                                        null
                                    );
                                }
                            } else {
                                if(value.next_node) {
                                    me.graph.insertEdge(
                                        parent,
                                        null, null,
                                        nodes[value.name],
                                        nodes[value.next_node],
                                        null
                                    );
                                }
                            }
                            break;
                    }
                });
            });
        }
        finally {
            model.endUpdate();
        }
    },
    //
    onSave: function() {
        var me = this;
        NOC.error("Not implemented");
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

        me.inspector.showNode(evt.properties.cell);
    },
    //
    onLoadHandlers: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        me.handlers = data;
        me.inspector.setHandlers(data);
    }
});
