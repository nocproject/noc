//---------------------------------------------------------------------
// ip.vrfgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrfgroup.Model");

Ext.define("NOC.ip.vrfgroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/vrfgroup/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "address_constraint",
            type: "string",
            defaultValue: "V"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "vrf_count",
            type: "int",
            persist: false
        }
    ]
});
