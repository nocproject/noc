//---------------------------------------------------------------------
// ip.ippool Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ippool.Model");

Ext.define("NOC.ip.ippool.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/ippool/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "termination_group",
            type: "int"
        },
        {
            name: "termination_group__label",
            type: "string",
            persist: false
        },
        {
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "afi",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "from_address",
            type: "string"
        },
        {
            name: "to_address",
            type: "string"
        }
    ]
});
