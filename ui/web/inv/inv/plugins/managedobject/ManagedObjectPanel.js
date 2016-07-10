//---------------------------------------------------------------------
// inv.inv ManagedObjectPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.managedobject.ManagedObjectPanel");

Ext.define("NOC.inv.inv.plugins.managedobject.ManagedObjectPanel", {
    extend: "Ext.panel.Panel",
    requires: [],
    title: "Managed Object",
    closable: false,
    layout: "fit",

    initComponent: function() {
        var me = this;

        // Grids
        Ext.apply(me, {
            items: [
            ]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        console.log(me.items, me.items.length);
        if(!me.items.length) {
            me.app.addAppForm(me, "sa.managedobject", data.managed_object_id);
        }
    }
});
