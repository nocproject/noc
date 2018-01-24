//---------------------------------------------------------------------
// IPAM application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.Application");

Ext.define("NOC.ip.ipam.Application", {
    extend: "NOC.core.Application",
    layout: "card",

    initComponent: function() {
        var me = this;

        me.ITEM_LEGACY = me.registerItem(
            Ext.create("NOC.ip.ipam.LegacyPanel", {app: me})
        );

        Ext.apply(me, {
            items: me.getRegisteredItems(),
            activeItem: me.ITEM_LEGACY
        });
        me.callParent();
    },
    //
    showPrefix: function(vrf, afi, prefix) {
        var me = this;
        me.previewItem(
            me.ITEM_LEGACY,
            "/ip/ipam/" + vrf + "/" + afi + "/" + prefix + "/"
        );
    }
});
