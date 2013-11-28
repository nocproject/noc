//---------------------------------------------------------------------
// inv.inv.plugins.inventory InventoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackPanel");

Ext.define("NOC.inv.inv.plugins.rack.RackPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        //"NOC.inv.inv.plugins.inventory.InventoryModel"
        "NOC.core.Rack"
    ],
    app: null,
    autoScroll: true,
    title: "Rack",
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.callParent();
    },
    //
    preview: function(data) {
        var me = this,
            r = NOC.core.Rack.getRack(5, 5, data.rack),
            dc = Ext.create("Ext.draw.Component", {
                viewBox: false,
                items: r
            });
        me.removeAll();
        me.add(dc);
    }
});
