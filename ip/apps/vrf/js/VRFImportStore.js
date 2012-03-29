//---------------------------------------------------------------------
// VRF Import Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.VRFImportStore");

Ext.define("NOC.ip.vrf.VRFImportStore", {
    extend: "Ext.data.Store",
    fields: [
        "name",
        "rd",
        "vrf_group", "vrf_group__label",
        "afi_ipv4",
        "afi_ipv6",
        "description"
    ]
});
