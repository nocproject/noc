//---------------------------------------------------------------------
// inv.interface L2 Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.L2Store");

Ext.define("NOC.inv.interface.L2Store", {
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
            name: "untagged_vlan",
            type: "auto"
        },
        {
            name: "tagged_vlans",
            type: "auto"
        },
        {
            name: "tagged_range",
            type: "string",
            convert: function(value, record) {
                return NOC.listToRanges(record.get("tagged_vlans"));
            }
        }
    ],
    data: []
});
