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
    currentVRF: null,
    currentAFI: null,
    currentPrefix: null,

    initComponent: function() {
        var me = this;

        me.ITEM_LEGACY = me.registerItem(
            Ext.create("NOC.ip.ipam.LegacyPanel", {app: me})
        );

        me.ITEM_PREFIX_FORM = me.registerItem(
            Ext.create("NOC.ip.ipam.PrefixPanel", {app: me})
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
        me.currentVRF = vrf;
        me.currentAFI = afi;
        me.currentPrefix = prefix;
        me.previewItem(
            me.ITEM_LEGACY,
            "/ip/ipam/" + vrf + "/" + afi + "/" + prefix + "/"
        );
    },
    //
    showCurrentPrefix: function() {
        var me = this;
        me.showPrefix(me.currentVRF, me.currentAFI, me.currentPrefix)
    },
    //
    onAddPrefix: function(parentPrefixId) {
        var me = this;
        me.previewItem(
            me.ITEM_PREFIX_FORM,
            {
                parentId: parentPrefixId
            }
        );
    },
    //
    onChangePrefix: function(prefixId) {
        var me = this;
        me.previewItem(
            me.ITEM_PREFIX_FORM,
            {
                id: prefixId
            }
        )
    }
});
