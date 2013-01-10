//---------------------------------------------------------------------
// inv.map application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.Application");

Ext.define("NOC.inv.map.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.inv.networkchart.LookupField"
    ],
    // Label position style
    labelPositionStyle: {
        "nw": "verticalLabelPosition=top;verticalAlign=bottom;labelPosition=left;align=right",
        "n": "verticalLabelPosition=top;verticalAlign=bottom",
        "ne": "verticalLabelPosition=top;verticalAlign=bottom;labelPosition=right;align=left",
        "e": "labelPosition=right;align=left",
        "se": "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=right;align=left",
        "s": "verticalLabelPosition=bottom;verticalAlign=top",
        sw: "verticalLabelPosition=bottom;verticalAlign=top;labelPosition=left;align=right",
        w: "labelPosition=left;align=right"
    },
    initComponent: function() {
        var me = this;
        me.chartCombo = Ext.create("NOC.inv.networkchart.LookupField", {
            fieldLabel: "Chart",
            labelWidth: 30,
            name: "chart",
            allowBlank: true,
            disabled: true,
            listeners: {
                scope: me,
                select: me.onSelectChart
            }
        });
        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.chartCombo
                ]
            }],
            items: [{
                xtype: "component",
                autoScroll: true,
                style: {
                    background: "url('/static/img/grid.gif')"
                }
            }]
        });
        me.graph = undefined;
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        // Load mxGraph JS library
        mxLanguage = "en";
        mxLoadStylesheets = false;  // window scope
        // mxImageBasePath = "";
        mxLoadResources = false;
        load_scripts(["/static/js/mxClient.min.js"], me,
            me.onLoadJS);
    },
    //
    onLoadJS: function() {
        var me = this;
        me.chartCombo.setDisabled(false);
    },
    //
    onSelectChart: function(combo, records, opts) {
        var me = this,
            mapId = records[0].get("id");
        Ext.Ajax.request({
            url: "/inv/map/chart/" + mapId + "/",
            method: "GET",
            scope: me,
            success: me.loadChart
        });
    },
    //
    loadChart: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        if(me.graph) {
            // @todo: clean graph
        } else {
            // Create Graph
            var c = me.items.first();
            me.graph = new mxGraph(c.el.dom);
            new mxRubberband(me.graph);
            me.graph.setPanning(true);
            me.graph.setTooltips(true);
            // Set styles
            var ss = me.graph.getStylesheet(),
                edgeStyle = ss.getDefaultEdgeStyle();
            edgeStyle[mxConstants.STYLE_EDGE] = mxEdgeStyle.ElbowConnector;
            delete edgeStyle.endArrow;
        }
        me.graph.getModel().beginUpdate();
        try {
            // Update data
            var parent = me.graph.getDefaultParent(),
                nodes = {},  // id -> node
                ports = {};  // id -> port
            for(var i in data) {
                var n = data[i];
                switch(n.type) {
                    // Insert node
                    case "node":
                        var style = [];
                        if(n.label) {
                            // Convert label position to style
                            var lp = n.label_position ? n.label_position : "s";
                            style.push(me.labelPositionStyle[lp]);
                        }
                        console.log(style.join(";"))
                        var v = me.graph.insertVertex(parent, null,
                            n.label ? n.label : null,
                            n.x, n.y, n.w, n.h,
                            style? style.join(";") : null
                        );
                        // Save id
                        if(n.id) {
                            nodes[n.id] = v;
                        };
                        // Create ports
                        for(var pi in n.ports) {
                            var pdata = n.ports[pi];
                            var pv = me.graph.insertVertex(v, null,
                                pdata.label, 1, 1, 5 * pdata.label.length, 12);
                            pv.geometry.offset = new mxPoint(3, 14 * pi - n.h);
                            pv.geometry.relative = true;
                            ports[pdata.id] = pv;
                        }
                        break;
                    // Insert link
                    case "link":
                        var v = me.graph.insertEdge(parent, null, "",
                            ports[n.ports[0]], ports[n.ports[1]]);
                        break;
                }
            }
        }
        finally {
            // Update display
            me.graph.getModel().endUpdate();
        }
    }
});
