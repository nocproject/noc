//---------------------------------------------------------------------
// inv.interface L3 Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L3Store");

Ext.define("NOC.inv.interface.L3Store", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "ipv4_addresses",
            type: "auto"
        },
        {
            name: "ipv6_addresses",
            type: "auto"
        },
        {
            name: "ip",
            convert: function(value, record) {
                var ipv4 = record.get("ipv4_addresses") || [],
                    ipv6 = record.get("ipv6_addresses") || [];
                return ipv4.concat(ipv6);
            }
        },
        {
            name: "enabled_protocols",
            type: "auto"
        },
        {
            name: "vlan",
            type: "auto"
        },
        {
            name: "vrf",
            type: "string"
        }
    ],
    data: []
});
