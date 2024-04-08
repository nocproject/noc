//---------------------------------------------------------------------
// inv.inv Facade panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.facade.FacadePanel");

Ext.define("NOC.inv.inv.plugins.facade.FacadePanel", {
    extend: "Ext.panel.Panel",
    requires: [
    ],
    title: __("Facade"),
    closable: false,
    scrollable: true,

    initComponent: function () {
        var me = this;

        // Grids
        Ext.apply(me, {
            items: [
            ]
        });
        me.callParent();
    },
    //
    preview: function (data) {
        var me = this;
    }
});
