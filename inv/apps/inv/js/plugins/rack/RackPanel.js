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

    initComponent: function() {
        var me = this;

        me.reloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            scope: me,
            tooltip: "Reload"
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.reloadButton,
                        "-"
                    ]
                }
            ]
        });

        me.callParent();
    },
    //
    preview: function(data) {
        var me = this,
            r = NOC.core.Rack.getRack(5, 5, data.rack, data.content),
            dc = Ext.create("Ext.draw.Component", {
                viewBox: false,
                items: r,
                autoScroll: true
            });
        me.removeAll();
        me.add(dc);
    }
});
