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

        me.ITEM_ADDRESS_FORM = me.registerItem(
            Ext.create("NOC.ip.ipam.AddressPanel", {app: me})
        );

        me.ITEM_REBASE_FORM = me.registerItem(
            Ext.create("NOC.ip.ipam.RebasePanel", {app: me})
        );

        Ext.apply(me, {
            items: me.getRegisteredItems(),
            activeItem: me.ITEM_LEGACY
        });
        me.callParent();
    },
    //
    setPrefix: function(vrf, afi, prefix) {
        var me = this;
        me.currentVRF = vrf;
        me.currentAFI = afi;
        me.currentPrefix = prefix;
    },
    //
    showPrefix: function(vrf, afi, prefix) {
        var me = this;
        me.setPrefix(vrf, afi, prefix);
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
    onAddPrefix: function(parentPrefixId, prefixHint) {
        var me = this;
        me.previewItem(
            me.ITEM_PREFIX_FORM,
            {
                parentId: parentPrefixId,
                prefix: prefixHint
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
    },
    //
    onAddAddress: function(prefixId, addressHint) {
        var me = this;
        me.previewItem(
            me.ITEM_ADDRESS_FORM,
            {
                prefixId: prefixId,
                address: addressHint
            }
        )
    },
    //
    onChangeAddress: function(addressId) {
        var me = this;
        me.previewItem(
            me.ITEM_ADDRESS_FORM,
            {
                id: addressId
            }
        )
    },
    getCommonPrefixPart: function(afi, prefix) {
        var parts = prefix.split("/"),
            net = parts[0],
            mask = parseInt(parts[1]);

        if(afi === "4") {
            // IPv4
            // Align to 8-bit border
            var v = net.split(".").slice(0, Math.floor(mask / 8)).join(".");
            if(v !== "") {
                v = v + "."
            }
            return v
        } else {
            // if p.mask < 16:
            //     return ""
            // # Align to 16-bit border
            // p.mask = (p.mask // 16) * 16
            // p = self.rx_ipv6_prefix_rest.sub("", p.normalized.prefix)
        }
    }
});
