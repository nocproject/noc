//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.view.Sidebar");

Ext.define("NOC.sa.discoveredobject.view.Sidebar", {
    extend: "Ext.form.Panel",
    alias: "widget.sa.discoveredobject.sidebar",
    controller: "sa.discoveredobject.sidebar",
    viewModel: {
        type: "sa.discoveredobject.sidebar"
    },
    requires: [
        "NOC.sa.discoveredobject.controller.Sidebar",
        "NOC.sa.discoveredobject.model.Sidebar",
    ],
    reference: "sa-discoveredobject-filter",
    title: __("Filter"),
    titleAlign: "center",
    minWidth: 350,
    scrollable: {
        indicators: false,
        x: false,
        y: true
    },
    suspendLayout: true,
    defaults: {
        xtype: "fieldset",
        margin: 5,
        collapsible: true
    },
    items: [
    ],
    initComponent: function() {
        this.callParent();
    },
});
