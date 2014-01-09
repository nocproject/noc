//---------------------------------------------------------------------
// sa.managedobject L3 Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.L3Store");

Ext.define("NOC.sa.managedobject.L3Store", {
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
            name: "mac",
            type: "string"
        },
        {
            name: "vrf",
            type: "string"
        }
    ],
    data: []
});
