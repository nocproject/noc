//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.view.Grid");

Ext.define("NOC.sa.discoveredobject.view.Grid", {
    extend: "Ext.grid.Panel",
    controller: "sa.discoveredobject.grid",
    alias: "widget.sa.discoveredobject.grid",
    requires: [
        "NOC.sa.discoveredobject.ApplicationController",
        "NOC.sa.discoveredobject.controller.Grid",
        "NOC.sa.discoveredobject.store.DiscoveredObject",
        // "Ext.ux.grid.column.GlyphAction"
    ],
    stateful: true,
    store: {
        type: "sa.discoveredobject"
    },
    selModel: {
        mode: "MULTI",
        type: "checkboxmodel"
    },
    columns: [
        {
            text: __("ID"),
            dataIndex: "id",
            hidden: true
        },
        {
            text: __("Address"),
            dataIndex: "address",
        },
        {
            text: __("Pool"),
            dataIndex: "pool",
            width: 100,
            renderer: NOC.render.Lookup("pool"),
        },
        {
            text: __("Hostname"),
            dataIndex: "hostname",
            renderer: function(v) {
                return v || "N/A";
            }
        },
        {
            text: __("State"),
            dataIndex: "state",
            width: 200,
            renderer: NOC.render.Lookup("state"),
        },
        {
            text: __("Rule"),
            dataIndex: "rule",
            width: 100,
            renderer: NOC.render.Lookup("rule"),
        },
        {
            text: __("Checks"),
            dataIndex: "checks",
            width: 250,
            renderer: "checksRenderer",
        },
        {
            text: __("Labels"),
            dataIndex: "effective_labels",
            editor: "labelfield",
            width: 200,
            renderer: NOC.render.LabelField,
        },
    ],
    listeners: {
        afterrender: "afterrenderHandler",
    },
    viewConfig: {
        enableTextSelection: true
    },
});
